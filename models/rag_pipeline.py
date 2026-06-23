import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from google import genai

def generate_patient_explanation(disease_code):
    print("="*60)
    print(f"STEP 3: RAG PIPELINE (Generating Patient-Friendly Explanation)")
    print("="*60)

    # 1. Retrieve Data from Database
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        client.server_info()
        db = client.health_library
        disease = db.diseases.find_one({"code": disease_code})
    except ServerSelectionTimeoutError:
        print("WARNING: MongoDB not running. Simulating database retrieval...")
        disease = {
            "name": "Type 2 diabetes mellitus without complications", 
            "code": "E11.9", 
            "source": "ICD-10-CM / MedlinePlus"
        }
        
    if not disease:
        print(f"ERROR: Disease with code {disease_code} not found in database.")
        return

    print(f"Retrieved Medical Data: {disease['name']} (Code: {disease['code']})")
    
    # 2. Setup LLM (Google GenAI API)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\nWARNING: GEMINI_API_KEY environment variable is not set.")
        print("To generate real explanations using Gemini AI, set it via terminal:")
        print("Windows: set GEMINI_API_KEY=your_key_here")
        print("Mac/Linux: export GEMINI_API_KEY=your_key_here\n")
        print("Simulating RAG pipeline output for now...\n")
        
        print("="*50)
        print(f"Patient-Friendly Explanation for: {disease['name']}")
        print("="*50)
        print("This is a simulated explanation. In a real scenario, the AI would generate a customized explanation based on the medical data.")
        return

    # Initialize GenAI Client
    client_genai = genai.Client()
    
    # Construct Context and Prompt
    prompt = f"""
    You are an empathetic, expert doctor explaining medical conditions to a patient in simple, non-medical terms.
    
    Medical Condition: {disease['name']}
    ICD-10 Code: {disease['code']}
    Source Info: {disease.get('source', 'Unknown')}
    
    Please provide a patient-friendly overview of this condition, common symptoms to look out for, and basic lifestyle advice. 
    Keep it encouraging, easy to understand, and structured with bullet points.
    """
    
    print("Sending medical data to Gemini AI for patient-friendly conversion...")
    try:
        response = client_genai.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # 3. Print the Result
        print("\n" + "="*60)
        print(f"Patient-Friendly Explanation")
        print("="*60)
        print(response.text)
        print("="*60)
    except Exception as e:
        print(f"Error during AI generation: {e}")

if __name__ == "__main__":
    # Test with a common disease code
    generate_patient_explanation("E11.9")
