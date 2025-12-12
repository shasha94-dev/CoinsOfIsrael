import os
import json

# --- CONFIGURATION ---
IMAGE_FOLDER = 'images'
FOLDER_MAP_FILE = 'folder_map.json'

# EXACT Hebrew strings used in index.html
UI_TERMS = [
    "ארכיון המטבעות הישראלי",
    "לפי שנה",
    "לפי סוג",
    "אודות ותודות",
    "הצהרת נגישות",
    "חפש שנה, שם או סדרה...",
    "אין נתונים נוספים",
    "ללא תיוג",
    "שנה",
    "סדרה"
]

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return {}
    return {}

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

folder_map = load_json(FOLDER_MAP_FILE)

def ask_translation(text, context=""):
    if not isinstance(text, str): return
    text = text.strip()
    if not text: return

    # Check cache
    if text in folder_map:
        return

    print(f"\n------------------------------------------------")
    print(f"Context: {context}")
    print(f"Hebrew Source: [{text}]")
    english = input("English Translation: ").strip()

    if not english:
        english = text

    folder_map[text] = english
    save_json(FOLDER_MAP_FILE, folder_map)

def scan_all():
    print("🚀 Starting Complete Scan...")
    
    # 1. SCAN UI TERMS (Fixes your headlines/buttons)
    print("\n--- Checking Interface Terms ---")
    for term in UI_TERMS:
        ask_translation(term, "Website Interface")

    # 2. SCAN FOLDERS
    print("\n--- Checking Folders ---")
    if os.path.exists(IMAGE_FOLDER):
        for series in os.listdir(IMAGE_FOLDER):
            path = os.path.join(IMAGE_FOLDER, series)
            if not os.path.isdir(path): continue
            ask_translation(series, "Series Name")
            
            for year in os.listdir(path):
                y_path = os.path.join(path, year)
                if not os.path.isdir(y_path): continue
                
                for coin in os.listdir(y_path):
                    c_path = os.path.join(y_path, coin)
                    if not os.path.isdir(c_path): continue
                    
                    ask_translation(coin, "Coin Name")
                    
                    # 3. SCAN DETAILS.JSON
                    d_path = os.path.join(c_path, 'details.json')
                    if os.path.exists(d_path):
                        data = load_json(d_path)
                        for k, v in data.items():
                            ask_translation(k, f"Key in {coin}")
                            if isinstance(v, str):
                                ask_translation(v, f"Value in {coin}")
                            elif isinstance(v, dict) and 'he' in v:
                                ask_translation(v['he'], f"Value in {coin}")

                    # Subtypes
                    for sub in os.listdir(c_path):
                        if os.path.isdir(os.path.join(c_path, sub)):
                            ask_translation(sub, "Subtype")

    print("\n✨ Done! Refresh your website now.")

if __name__ == "__main__":
    scan_all()
