import os
import sys

def main():
    print("="*60)
    print("HEALTH LIBRARY BACKEND - MASTER PIPELINE")
    print("="*60)
    print("\nWelcome! This pipeline implements all 3 steps of the tutorial:\n")
    print("STEP 1: MedlinePlus API Fetcher (data_fetcher/medlineplus.py)")
    print("STEP 2: Bulk ICD-10 Dataset Import (data_fetcher/import_icd10.py)")
    print("STEP 3: RAG Pipeline with Gemini AI (models/rag_pipeline.py)")
    
    print("\nTo run the individual steps, use the following commands from the terminal:\n")
    
    print("1. Run MedlinePlus Fetcher (Step 1):")
    print("   python data_fetcher/medlineplus.py\n")
    
    print("2. Import 98,000+ ICD-10 Codes into MongoDB (Step 2):")
    print("   python data_fetcher/import_icd10.py\n")
    
    print("3. Run RAG Pipeline to generate patient-friendly explanation (Step 3):")
    print("   set GEMINI_API_KEY=your_actual_api_key")
    print("   python models/rag_pipeline.py\n")
    
    print("Note: Ensure MongoDB is running locally on port 27017 for Database operations to succeed.")
    print("If MongoDB is not running, the scripts will run in 'simulation mode' where they only fetch/print data.")

if __name__ == "__main__":
    main()
