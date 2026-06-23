import sqlite3
import sys

def search_by_alphabet(letter):
    conn = sqlite3.connect("database/health_library.db")
    cursor = conn.cursor()
    
    letter = letter.upper()
    print(f"\n--- Searching for diseases starting with '{letter}' ---")
    
    # We use LIMIT 20 so we don't flood the console
    cursor.execute("SELECT code, name FROM diseases WHERE first_letter = ? LIMIT 20", (letter,))
    results = cursor.fetchall()
    
    if not results:
        print("No diseases found starting with this letter.")
    else:
        for code, name in results:
            print(f"[{code}] {name}")
        if len(results) == 20:
            print("... (Showing first 20 results)")
            
    conn.close()

def search_by_symptom(keyword):
    conn = sqlite3.connect("database/health_library.db")
    cursor = conn.cursor()
    
    print(f"\n--- Searching for diseases related to '{keyword}' ---")
    
    # Use LIKE for symptom/keyword searching within the disease name
    query = f"%{keyword}%"
    cursor.execute("SELECT code, name FROM diseases WHERE name LIKE ? LIMIT 20", (query,))
    results = cursor.fetchall()
    
    if not results:
        print("No matches found for this keyword.")
    else:
        for code, name in results:
            print(f"[{code}] {name}")
        if len(results) == 20:
            print("... (Showing first 20 results)")
            
    conn.close()

def main():
    print("==============================================")
    print("HEALTH LIBRARY - SEARCH ENGINE")
    print("==============================================")
    
    while True:
        print("\nChoose an option:")
        print("1. Search by Starting Alphabet (A-Z)")
        print("2. Search by Symptom / Keyword (e.g. 'fever', 'diabetes', 'pain')")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == '1':
            letter = input("Enter a starting letter (A-Z): ").strip()
            if len(letter) == 1 and letter.isalpha():
                search_by_alphabet(letter)
            else:
                print("Invalid input. Please enter a single letter.")
                
        elif choice == '2':
            keyword = input("Enter symptom or keyword: ").strip()
            if keyword:
                search_by_symptom(keyword)
            else:
                print("Invalid input. Keyword cannot be empty.")
                
        elif choice == '3':
            print("Exiting search engine. Stay healthy!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    import os
    if not os.path.exists("database/health_library.db"):
        print("Error: Database not found! Please run 'python database/setup_sqlite.py' first.")
    else:
        main()
