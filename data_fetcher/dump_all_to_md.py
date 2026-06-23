import simple_icd_10_cm as icd
import time

def dump_all():
    print("Fetching all ICD-10 codes. This might take a few seconds...")
    start_time = time.time()
    
    all_codes = icd.get_all_codes()
    print(f"Found {len(all_codes)} total codes. Extracting valid diseases...")
    
    with open("database_all.md", "w", encoding="utf-8") as f:
        f.write("# Complete ICD-10 Medical Database\n\n")
        f.write("This file contains the complete list of 98,000+ ICD-10 medical conditions.\n\n")
        
        count = 0
        for code in all_codes:
            if icd.is_valid_item(code):
                desc = icd.get_description(code)
                f.write(f"## {desc}\n")
                f.write(f"- **Code:** {code}\n")
                f.write(f"- **Category:** ICD-10-CM\n")
                f.write(f"- **Source:** simple_icd_10_cm\n\n")
                count += 1
                
                if count % 20000 == 0:
                    print(f"Written {count} records to MD file...")
                    
    elapsed = round(time.time() - start_time, 2)
    print(f"Successfully dumped {count} records to database_all.md in {elapsed} seconds!")

if __name__ == "__main__":
    dump_all()
