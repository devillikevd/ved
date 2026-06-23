import requests
import json
import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def get_disease(code):
    url = "https://connect.medlineplus.gov/service"
    params = {
        "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.90",
        "mainSearchCriteria.v.c": code,
        "knowledgeResponseType": "application/json"
    }
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    # Load disease codes
    file_path = "disease_codes.json"
    if not os.path.exists(file_path):
        file_path = "../disease_codes.json"
        
    try:
        with open(file_path, "r") as f:
            codes = json.load(f)
    except FileNotFoundError:
        print("Error: Could not find disease_codes.json")
        codes = []

    # Connect to MongoDB
    mongo_connected = False
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Verify connection
        client.server_info()
        db = client.health_library
        collection = db.diseases
        mongo_connected = True
        print("Connected to MongoDB successfully.")
    except ServerSelectionTimeoutError:
        print("MongoDB is not running locally on port 27017.")
        print("Data will be fetched but NOT saved to the database.")
    except Exception as e:
        print(f"MongoDB connection error: {e}")

    # Fetch and Process Data
    for code in codes:
        print(f"\nFetching data for code: {code}")
        data = get_disease(code)
        
        # Extract disease name from MedlinePlus response
        # The structure is usually data['feed']['entry'][0]['title']['_value']
        name = "Unknown Disease"
        try:
            entries = data.get("feed", {}).get("entry", [])
            if entries:
                name = entries[0].get("title", {}).get("_value", "Unknown Disease")
        except Exception as e:
            print(f"Error parsing name for {code}: {e}")

        # Construct our schema
        disease = {
            "name": name,
            "code": code,
            "category": "",
            "source": "MedlinePlus",
            "symptoms": [],
            "overview": "",
            "references": []
        }
        
        print(f"Parsed Schema:\n{json.dumps(disease, indent=2)}")
        
        # Save to DB or MD File
        if mongo_connected:
            # Check if it already exists to avoid duplicates
            if not collection.find_one({"code": code}):
                collection.insert_one(disease)
                print(f"Saved {code} ({name}) to MongoDB 'health_library.diseases'")
            else:
                print(f"{code} already exists in database. Skipping insertion.")
        else:
            # Save to Markdown database as a fallback
            md_path = "database.md"
            if not os.path.exists(md_path):
                md_path = "../database.md"
                
            with open(md_path, "a", encoding="utf-8") as f:
                f.write(f"\n## {name}\n")
                f.write(f"- **Code:** {code}\n")
                f.write(f"- **Source:** MedlinePlus\n")
                f.write(f"- **Category:** {disease['category']}\n")
                f.write(f"- **Symptoms:** None listed yet\n")
                f.write(f"- **Overview:** {disease['overview']}\n")
                f.write(f"- **References:** []\n\n")
                f.write("---\n")
            print(f"Saved {code} ({name}) to fallback Markdown file 'database.md'")

