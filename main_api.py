"""
Health Library - Advanced FastAPI Backend
Serves the premium frontend and provides rich API endpoints for disease search,
category browsing, and statistics.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import sqlite3
import os
import json
import asyncio

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = FastAPI(title="Health Library API", version="2.0")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_PATH = "database/health_library.db"


def get_db():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database not found.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
async def index():
    return FileResponse("static/index.html")


# ── CATEGORIES ──────────────────────────────────────────────────
@app.get("/api/categories")
async def get_categories():
    """Get all disease categories with counts."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM categories ORDER BY disease_count DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── ALPHABET ────────────────────────────────────────────────────
@app.get("/api/diseases/alphabet/{letter}")
async def get_by_alphabet(letter: str, page: int = 1, limit: int = 50):
    """Get diseases by starting letter with pagination."""
    if len(letter) != 1 or not letter.isalpha():
        raise HTTPException(status_code=400, detail="Invalid letter.")
    offset = (page - 1) * limit
    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM diseases WHERE first_letter = ?",
        (letter.upper(),)
    ).fetchone()["cnt"]

    rows = conn.execute(
        "SELECT * FROM diseases WHERE first_letter = ? ORDER BY name LIMIT ? OFFSET ?",
        (letter.upper(), limit, offset)
    ).fetchall()
    conn.close()
    return {"total": total, "page": page, "limit": limit, "results": [dict(r) for r in rows]}


# ── SEARCH ──────────────────────────────────────────────────────
@app.get("/api/diseases/search")
async def search_diseases(q: str = Query(..., min_length=2), page: int = 1, limit: int = 50):
    """Full-text search across name, code, keywords, chapter."""
    offset = (page - 1) * limit
    pattern = f"%{q}%"
    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM diseases WHERE name LIKE ? OR code LIKE ? OR keywords LIKE ? OR chapter LIKE ?",
        (pattern, pattern, pattern, pattern)
    ).fetchone()["cnt"]

    rows = conn.execute(
        "SELECT * FROM diseases WHERE name LIKE ? OR code LIKE ? OR keywords LIKE ? OR chapter LIKE ? ORDER BY name LIMIT ? OFFSET ?",
        (pattern, pattern, pattern, pattern, limit, offset)
    ).fetchall()

    # Log search (safely ignore read-only errors on Vercel)
    try:
        conn.execute("INSERT INTO search_stats (query, result_count) VALUES (?, ?)", (q, total))
        conn.commit()
    except sqlite3.OperationalError:
        pass # Ignored on read-only environments like Vercel
    finally:
        conn.close()
    return {"total": total, "page": page, "limit": limit, "results": [dict(r) for r in rows]}


# ── CATEGORY FILTER ─────────────────────────────────────────────
@app.get("/api/diseases/category/{chapter}")
async def get_by_category(chapter: str, page: int = 1, limit: int = 50):
    """Get diseases by ICD-10 chapter/category."""
    offset = (page - 1) * limit
    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM diseases WHERE chapter = ?", (chapter,)
    ).fetchone()["cnt"]

    rows = conn.execute(
        "SELECT * FROM diseases WHERE chapter = ? ORDER BY name LIMIT ? OFFSET ?",
        (chapter, limit, offset)
    ).fetchall()
    conn.close()
    return {"total": total, "page": page, "limit": limit, "results": [dict(r) for r in rows]}


# ── SEVERITY FILTER ─────────────────────────────────────────────
@app.get("/api/diseases/severity/{level}")
async def get_by_severity(level: str, page: int = 1, limit: int = 50):
    """Get diseases by severity: Critical, Severe, Moderate, General."""
    offset = (page - 1) * limit
    conn = get_db()

    total = conn.execute(
        "SELECT COUNT(*) as cnt FROM diseases WHERE severity = ?", (level,)
    ).fetchone()["cnt"]

    rows = conn.execute(
        "SELECT * FROM diseases WHERE severity = ? ORDER BY name LIMIT ? OFFSET ?",
        (level, limit, offset)
    ).fetchall()
    conn.close()
    return {"total": total, "page": page, "limit": limit, "results": [dict(r) for r in rows]}


# ── SINGLE DISEASE ──────────────────────────────────────────────
@app.get("/api/disease/{code}")
async def get_disease_detail(code: str):
    """Get a single disease by its ICD-10 code."""
    conn = get_db()
    row = conn.execute("SELECT * FROM diseases WHERE code = ?", (code,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Disease not found.")
    return dict(row)

# ── SINGLE DISEASE DETAILS (AI GENERATED) ───────────────────────
@app.get("/api/disease/{code}/details")
async def get_disease_ai_details(code: str):
    """Get rich medical details (overview, symptoms, medicines) powered by AI."""
    conn = get_db()
    row = conn.execute("SELECT * FROM diseases WHERE code = ?", (code,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Disease not found.")
        
    disease_dict = dict(row)
    
    # If already generated and cached, return immediately
    if disease_dict.get("overview") and disease_dict.get("symptoms"):
        conn.close()
        return disease_dict

    name = disease_dict["name"]
    chapter = disease_dict["chapter"]
    
    # Try to generate using Gemini if API key is present
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if GEMINI_AVAILABLE and api_key:
        try:
            client = genai.Client()
            prompt = f"""
            You are a highly advanced medical expert assistant. Provide comprehensive, structured, and accurate medical information about the following disease/condition:
            Name: {name}
            ICD-10 Code: {code}
            Category: {chapter}
            
            Please provide the response in valid JSON format with exactly these keys:
            - "overview": Detailed paragraph explaining the condition.
            - "symptoms": Bulleted list of common symptoms (as a single string with HTML <li> tags).
            - "causes": Bulleted list of primary causes and risk factors (as a single string with HTML <li> tags).
            - "medicines": Bulleted list of medical treatments and medicines (as a single string with HTML <li> tags).
            - "home_remedies": Bulleted list of home remedies and lifestyle changes (as a single string with HTML <li> tags).
            - "prevention": Bulleted list of preventive measures (as a single string with HTML <li> tags).
            - "when_to_see_doctor": A short paragraph explaining when to seek emergency or medical care.
            
            Do not include any markdown formatting like ```json. Just raw JSON.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            
            # Clean response text and parse JSON
            res_text = response.text.strip()
            if res_text.startswith("```json"):
                res_text = res_text[7:-3].strip()
            if res_text.startswith("```"):
                res_text = res_text[3:-3].strip()
                
            parsed = json.loads(res_text)
            overview = parsed.get("overview", "Information not available.")
            symptoms = parsed.get("symptoms", "<li>Information not available</li>")
            causes = parsed.get("causes", "<li>Information not available</li>")
            medicines = parsed.get("medicines", "<li>Information not available</li>")
            home_remedies = parsed.get("home_remedies", "<li>Information not available</li>")
            prevention = parsed.get("prevention", "<li>Information not available</li>")
            when_to_see_doctor = parsed.get("when_to_see_doctor", "Consult a doctor for more information.")
            
        except Exception as e:
            print(f"Gemini generation error: {e}")
            overview, symptoms, causes, medicines, home_remedies, prevention, when_to_see_doctor = generate_mock_details(name, chapter)
    else:
        # Simulate delay to mimic AI generation
        await asyncio.sleep(1.5)
        overview, symptoms, causes, medicines, home_remedies, prevention, when_to_see_doctor = generate_mock_details(name, chapter)
        
    # Cache the results in the database (safely ignore read-only errors on Vercel)
    try:
        conn.execute(
            """UPDATE diseases SET 
               overview = ?, symptoms = ?, causes = ?, medicines = ?, home_remedies = ?, prevention = ?, when_to_see_doctor = ?
               WHERE code = ?""",
            (overview, symptoms, causes, medicines, home_remedies, prevention, when_to_see_doctor, code)
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass # Ignored on read-only environments like Vercel
    finally:
        conn.close()
    
    disease_dict["overview"] = overview
    disease_dict["symptoms"] = symptoms
    disease_dict["causes"] = causes
    disease_dict["medicines"] = medicines
    disease_dict["home_remedies"] = home_remedies
    disease_dict["prevention"] = prevention
    disease_dict["when_to_see_doctor"] = when_to_see_doctor
    
    return disease_dict

def generate_mock_details(name, chapter):
    """Fallback generator when Gemini is not configured."""
    overview = f"<strong>{name}</strong> is a medical condition classified under {chapter}. This condition requires proper medical evaluation for accurate diagnosis and management. It may affect various body systems depending on the severity and patient history. Please consult a healthcare professional for specific clinical advice."
    
    symptoms = f"<li>General discomfort or pain related to {name.lower()}</li><li>Specific localized symptoms depending on severity</li><li>Possible systemic reactions if untreated</li>"
    
    causes = f"<li>Genetic predisposition or family history</li><li>Environmental factors and lifestyle choices</li><li>Underlying physiological imbalances related to {chapter}</li>"
    
    medicines = f"<li>Medical evaluation and diagnosis by a specialist</li><li>Symptomatic relief medications (e.g., analgesics if applicable)</li><li>Targeted therapy based on clinical guidelines for {chapter}</li>"
    
    home_remedies = f"<li>Adequate rest and hydration</li><li>Maintaining a balanced, nutritious diet</li><li>Stress management techniques</li>"
    
    prevention = f"<li>Regular health screenings and check-ups</li><li>Avoiding known risk factors and triggers</li><li>Adopting a healthy lifestyle and exercise routine</li>"
    
    when_to_see_doctor = f"You should see a doctor immediately if you experience severe symptoms, sudden worsening of your condition, or if {name.lower()} starts interfering with your daily activities. Do not delay seeking medical help for acute episodes."
    
    return overview, symptoms, causes, medicines, home_remedies, prevention, when_to_see_doctor



# ── STATS ───────────────────────────────────────────────────────
@app.get("/api/stats")
async def get_stats():
    """Dashboard statistics."""
    conn = get_db()
    total_diseases = conn.execute("SELECT COUNT(*) as cnt FROM diseases").fetchone()["cnt"]
    total_categories = conn.execute("SELECT COUNT(*) as cnt FROM categories").fetchone()["cnt"]
    severity_breakdown = conn.execute(
        "SELECT severity, COUNT(*) as cnt FROM diseases GROUP BY severity ORDER BY cnt DESC"
    ).fetchall()
    letter_breakdown = conn.execute(
        "SELECT first_letter, COUNT(*) as cnt FROM diseases GROUP BY first_letter ORDER BY first_letter"
    ).fetchall()
    conn.close()
    return {
        "total_diseases": total_diseases,
        "total_categories": total_categories,
        "severity": [dict(r) for r in severity_breakdown],
        "by_letter": [dict(r) for r in letter_breakdown],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_api:app", host="0.0.0.0", port=8000, reload=True)
