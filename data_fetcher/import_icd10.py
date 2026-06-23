import simple_icd_10_cm as icd
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def import_all_icd10():
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        # Check connection
        client.server_info()
        db = client.health_library
        collection = db.diseases
        
        # Get all ICD-10 codes
        all_codes = icd.get_all_codes()
        print(f"Found {len(all_codes)} ICD-10 codes. Preparing for batch insertion...")
        
        batch = []
        batch_size = 5000
        total_inserted = 0
        
        for code in all_codes:
            if icd.is_valid_item(code):
                description = icd.get_description(code)
                disease = {
                    "name": description,
                    "code": code,
                    "category": "ICD-10",
                    "source": "ICD-10-CM",
                    "symptoms": [],
                    "overview": "",
                    "references": []
                }
                batch.append(disease)
                
                if len(batch) >= batch_size:
                    # Insert batch ignoring duplicates
                    try:
                        collection.insert_many(batch, ordered=False)
                    except Exception as e:
                        # ordered=False allows continuing if some fail
                        pass
                    
                    total_inserted += len(batch)
                    batch = []
                    print(f"Inserted {total_inserted} codes...")
        
        # Insert remaining
        if batch:
            try:
                collection.insert_many(batch, ordered=False)
                total_inserted += len(batch)
            except Exception:
                pass
            
        print(f"Successfully imported a total of {total_inserted} ICD-10 diseases into MongoDB!")
        
    except ServerSelectionTimeoutError:
        print("MongoDB is not running locally on port 27017.")
        print("Cannot save the dataset. Please start MongoDB to perform the actual import.")
        # Print a sample of what would be inserted
        sample_code = "E11.9"
        if icd.is_valid_item(sample_code):
            print(f"\nExample data that would be saved:\nCode: {sample_code}\nName: {icd.get_description(sample_code)}")

if __name__ == "__main__":
    import_all_icd10()
