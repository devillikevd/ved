"""
Advanced Database Setup Script
Creates a properly structured, categorized SQLite database with 98,000+ ICD-10 diseases.
Each disease is mapped to its official ICD-10 Chapter, Body System, and has searchable keywords.
"""

import sqlite3
import simple_icd_10_cm as icd
import time
import os
import re

# Official ICD-10-CM Chapter Mapping
ICD10_CHAPTERS = {
    "A": ("Infectious & Parasitic Diseases", "Immune System"),
    "B": ("Infectious & Parasitic Diseases", "Immune System"),
    "C": ("Neoplasms (Cancer)", "Oncology"),
    "D0": ("Neoplasms (Cancer)", "Oncology"),
    "D1": ("Neoplasms (Cancer)", "Oncology"),
    "D2": ("Neoplasms (Cancer)", "Oncology"),
    "D3": ("Neoplasms (Cancer)", "Oncology"),
    "D4": ("Neoplasms (Cancer)", "Oncology"),
    "D5": ("Blood & Immune Disorders", "Hematology"),
    "D6": ("Blood & Immune Disorders", "Hematology"),
    "D7": ("Blood & Immune Disorders", "Hematology"),
    "D8": ("Blood & Immune Disorders", "Hematology"),
    "E": ("Endocrine, Nutritional & Metabolic", "Endocrinology"),
    "F": ("Mental & Behavioral Disorders", "Psychiatry"),
    "G": ("Nervous System Diseases", "Neurology"),
    "H0": ("Eye & Adnexa Diseases", "Ophthalmology"),
    "H1": ("Eye & Adnexa Diseases", "Ophthalmology"),
    "H2": ("Eye & Adnexa Diseases", "Ophthalmology"),
    "H3": ("Eye & Adnexa Diseases", "Ophthalmology"),
    "H4": ("Eye & Adnexa Diseases", "Ophthalmology"),
    "H5": ("Eye & Adnexa Diseases", "Ophthalmology"),
    "H6": ("Ear & Mastoid Diseases", "Otolaryngology"),
    "H7": ("Ear & Mastoid Diseases", "Otolaryngology"),
    "H8": ("Ear & Mastoid Diseases", "Otolaryngology"),
    "H9": ("Ear & Mastoid Diseases", "Otolaryngology"),
    "I": ("Circulatory System Diseases", "Cardiology"),
    "J": ("Respiratory System Diseases", "Pulmonology"),
    "K": ("Digestive System Diseases", "Gastroenterology"),
    "L": ("Skin & Subcutaneous Diseases", "Dermatology"),
    "M": ("Musculoskeletal & Connective Tissue", "Orthopedics"),
    "N": ("Genitourinary System Diseases", "Urology"),
    "O": ("Pregnancy & Childbirth", "Obstetrics"),
    "P": ("Perinatal Conditions", "Neonatology"),
    "Q": ("Congenital Malformations", "Genetics"),
    "R": ("Symptoms, Signs & Abnormal Findings", "General Medicine"),
    "S": ("Injury & Poisoning", "Emergency Medicine"),
    "T": ("Injury & Poisoning", "Emergency Medicine"),
    "U": ("Special Purpose Codes", "Other"),
    "V": ("External Causes of Morbidity", "Emergency Medicine"),
    "W": ("External Causes of Morbidity", "Emergency Medicine"),
    "X": ("External Causes of Morbidity", "Emergency Medicine"),
    "Y": ("External Causes of Morbidity", "Emergency Medicine"),
    "Z": ("Health Status & Services", "Preventive Medicine"),
}

# Common symptom keywords to extract from disease names
SYMPTOM_KEYWORDS = [
    "pain", "fever", "cough", "bleeding", "swelling", "inflammation",
    "infection", "fracture", "burn", "wound", "ulcer", "tumor",
    "cancer", "diabetes", "hypertension", "anemia", "asthma",
    "pneumonia", "arthritis", "allergy", "nausea", "vomiting",
    "diarrhea", "headache", "fatigue", "weakness", "paralysis",
    "seizure", "edema", "abscess", "hernia", "obstruction",
    "perforation", "hemorrhage", "thrombosis", "embolism",
    "stenosis", "insufficiency", "failure", "disorder", "syndrome",
    "dystrophy", "atrophy", "necrosis", "fibrosis", "sclerosis",
    "ischemia", "infarction", "rupture", "sprain", "strain",
    "dislocation", "contusion", "laceration", "abrasion",
    "poisoning", "toxicity", "deficiency", "excess", "obesity",
    "malnutrition", "dehydration", "sepsis", "shock",
    "respiratory", "cardiac", "renal", "hepatic", "cerebral",
    "chronic", "acute", "malignant", "benign", "congenital",
]


def get_chapter_info(code):
    """Map an ICD-10 code to its chapter category and body system."""
    if not code:
        return ("Uncategorized", "General")
    
    # Try 2-char prefix first (for D0-D4 vs D5-D8 split, H0-H5 vs H6-H9)
    prefix2 = code[:2].upper()
    if prefix2 in ICD10_CHAPTERS:
        return ICD10_CHAPTERS[prefix2]
    
    # Fallback to 1-char prefix
    prefix1 = code[0].upper()
    if prefix1 in ICD10_CHAPTERS:
        return ICD10_CHAPTERS[prefix1]
    
    return ("Uncategorized", "General")


def extract_keywords(name):
    """Extract searchable symptom keywords from a disease name."""
    name_lower = name.lower()
    found = []
    for kw in SYMPTOM_KEYWORDS:
        if kw in name_lower:
            found.append(kw)
    return ",".join(found) if found else ""


def get_severity(code, name):
    """Estimate a basic severity tag from the disease name/code."""
    name_lower = name.lower()
    if any(w in name_lower for w in ["malignant", "cancer", "carcinoma", "sarcoma", "leukemia", "lymphoma", "melanoma"]):
        return "Critical"
    if any(w in name_lower for w in ["acute", "hemorrhage", "infarction", "sepsis", "shock", "failure", "embolism", "rupture"]):
        return "Severe"
    if any(w in name_lower for w in ["chronic", "recurrent", "progressive"]):
        return "Moderate"
    return "General"


def setup_advanced_database():
    print("=" * 70)
    print("  HEALTH LIBRARY - ADVANCED DATABASE BUILDER")
    print("=" * 70)
    start = time.time()

    os.makedirs("database", exist_ok=True)
    db_path = "database/health_library.db"

    # Remove old DB for fresh build
    if os.path.exists(db_path):
        os.remove(db_path)
        print("[1/5] Removed old database.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── SCHEMA ──────────────────────────────────────────────────
    print("[2/5] Creating advanced schema...")

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS diseases (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            code          TEXT UNIQUE NOT NULL,
            name          TEXT NOT NULL,
            first_letter  TEXT NOT NULL,
            chapter       TEXT NOT NULL,
            body_system   TEXT NOT NULL,
            severity      TEXT DEFAULT 'General',
            keywords      TEXT DEFAULT '',
            source        TEXT DEFAULT 'ICD-10-CM',
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS categories (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter       TEXT UNIQUE NOT NULL,
            body_system   TEXT NOT NULL,
            disease_count INTEGER DEFAULT 0,
            icon          TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS search_stats (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            query         TEXT NOT NULL,
            result_count  INTEGER DEFAULT 0,
            searched_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # ── DATA EXTRACTION ─────────────────────────────────────────
    print("[3/5] Extracting 98,000+ ICD-10 codes with rich metadata...")
    all_codes = icd.get_all_codes()

    records = []
    category_counts = {}

    for code in all_codes:
        if icd.is_valid_item(code):
            name = icd.get_description(code)
            first_letter = name[0].upper() if name else "?"
            chapter, body_system = get_chapter_info(code)
            severity = get_severity(code, name)
            keywords = extract_keywords(name)

            records.append((code, name, first_letter, chapter, body_system, severity, keywords, "ICD-10-CM"))

            if chapter not in category_counts:
                category_counts[chapter] = {"body_system": body_system, "count": 0}
            category_counts[chapter]["count"] += 1

    print(f"    Extracted {len(records)} diseases across {len(category_counts)} categories.")

    # ── BATCH INSERT ────────────────────────────────────────────
    print("[4/5] Inserting into database (batch mode)...")
    cursor.executemany('''
        INSERT OR IGNORE INTO diseases (code, name, first_letter, chapter, body_system, severity, keywords, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)

    # Insert category summaries
    CATEGORY_ICONS = {
        "Infectious & Parasitic Diseases": "virus",
        "Neoplasms (Cancer)": "cancer",
        "Blood & Immune Disorders": "blood",
        "Endocrine, Nutritional & Metabolic": "metabolism",
        "Mental & Behavioral Disorders": "brain",
        "Nervous System Diseases": "neurology",
        "Eye & Adnexa Diseases": "eye",
        "Ear & Mastoid Diseases": "ear",
        "Circulatory System Diseases": "heart",
        "Respiratory System Diseases": "lungs",
        "Digestive System Diseases": "stomach",
        "Skin & Subcutaneous Diseases": "skin",
        "Musculoskeletal & Connective Tissue": "bone",
        "Genitourinary System Diseases": "kidney",
        "Pregnancy & Childbirth": "pregnancy",
        "Perinatal Conditions": "baby",
        "Congenital Malformations": "dna",
        "Symptoms, Signs & Abnormal Findings": "stethoscope",
        "Injury & Poisoning": "injury",
        "External Causes of Morbidity": "emergency",
        "Health Status & Services": "checkup",
        "Special Purpose Codes": "code",
    }

    for chapter, info in category_counts.items():
        icon = CATEGORY_ICONS.get(chapter, "medical")
        cursor.execute('''
            INSERT OR IGNORE INTO categories (chapter, body_system, disease_count, icon)
            VALUES (?, ?, ?, ?)
        ''', (chapter, info["body_system"], info["count"], icon))

    # ── INDEXES ─────────────────────────────────────────────────
    print("[5/5] Building search indexes for fast lookups...")
    cursor.executescript('''
        CREATE INDEX IF NOT EXISTS idx_first_letter ON diseases(first_letter);
        CREATE INDEX IF NOT EXISTS idx_name ON diseases(name);
        CREATE INDEX IF NOT EXISTS idx_chapter ON diseases(chapter);
        CREATE INDEX IF NOT EXISTS idx_body_system ON diseases(body_system);
        CREATE INDEX IF NOT EXISTS idx_severity ON diseases(severity);
        CREATE INDEX IF NOT EXISTS idx_keywords ON diseases(keywords);
        CREATE INDEX IF NOT EXISTS idx_code ON diseases(code);
    ''')

    conn.commit()
    conn.close()

    elapsed = round(time.time() - start, 2)
    print("")
    print("=" * 70)
    print(f"  DATABASE READY!")
    print(f"  Records  : {len(records)}")
    print(f"  Categories: {len(category_counts)}")
    print(f"  Time     : {elapsed}s")
    print(f"  Location : {os.path.abspath(db_path)}")
    print("=" * 70)


if __name__ == "__main__":
    setup_advanced_database()
