import os
import json
def noop_add_json_data(data: dict, folder1_name: str, folder2_name_part: list, folder3_name_part: str):
    pass
    
def add_json_data(data: dict, folder1_name: str, folder2_name_part: list, folder3_name_part: str):
    """
    Finds all subfolders in folder1_name whose names contain any element of folder2_name_part.
    Inside each of those, finds a folder named folder3_name_part.
    In each such folder, updates (or creates) a details.json file by merging the given data.
    """
    count = 0
    for f2 in os.listdir(folder1_name):
        full_f2_path = os.path.join(folder1_name, f2)
        if not os.path.isdir(full_f2_path):
            continue

        # Folder2 name must contain ANY of the given substrings
        if not any(part in f2 for part in folder2_name_part):
            continue

        # Verify folder3 exists
        f3_path = os.path.join(full_f2_path, folder3_name_part)
        if not os.path.isdir(f3_path):
            continue

        # Path to details.json
        json_path = os.path.join(f3_path, "details.json")

        # Load existing JSON object if present
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                if not isinstance(existing, dict):
                    existing = {}  # Force to dict if wrong type
            except json.JSONDecodeError:
                existing = {}
        else:
            existing = {}

        # Merge new data (new values override old ones)
        existing.update(data)

        # Save result
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)
        count += 1
    print("updated",count,"files")
    
add_json_data(	
    data={"משקל": "4 גרם","קוטר": "18 מ\"מ", "חומר": "סגסוגת של 75% נחושת ו-25% ניקל."},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,1994)],
    folder3_name_part="שקל"
)  


add_json_data(	
    data={"משקל": "3.5 גרם","קוטר": "18 מ\"מ", "חומר": "פלדה מצופה ניקל."},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1994,2025)],
    folder3_name_part="שקל"
)  


noop_add_json_data(	
    data={"משקל": "5.7 גרם","קוטר": "21.6 מ\"מ", "חומר": "פלדה מצופה ניקל."},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,2025)],
    folder3_name_part="2 שקלים"
)  
noop_add_json_data(	
    data={"משקל": "7 גרם","קוטר": "23 מ\"מ", "חומר": "טבעתו החיצונית עשויה מפלדה מצופה בניקל. מרכזו עשוי ארד מצופה באורייט"},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,2025)],
    folder3_name_part="10 שקלים"
)  
noop_add_json_data(	
    data={"משקל": "8.18 גרם","קוטר": "24 מ\"מ", "חומר": "סגסוגת שתרכובתה 75% נחושת ו-25% ניקל"},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,2025)],
    folder3_name_part="5 שקלים"
)
noop_add_json_data(
    data={"משקל": "3 גרם","קוטר": "19.5 מ\"מ", "חומר": "סגסוגת שתרכובתה 92% נחושת, 6% אלומיניום ו-2% ניקל"},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,2025)],
    folder3_name_part="5 אגורות"
)
noop_add_json_data(
    data={"משקל": "2 גרם","קוטר": "17 מ\"מ", "חומר": "סגסוגת שתרכובתה 92% נחושת, 6% אלומיניום ו-2% ניקל"},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,2025)],
    folder3_name_part="אגורה"
)
noop_add_json_data(
    data={"משקל": "6.5 גרם","קוטר": "26 מ\"מ", "חומר": "סגסוגת שתרכובתה 92% נחושת, 6% אלומיניום ו-2% ניקל"},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,2025)],
    folder3_name_part="חצי שקל"
)
noop_add_json_data(
    data={"משקל": "4 גרם","קוטר": "22 מ\"מ", "חומר": "סגסוגת שתרכובתה 92% נחושת, 6% אלומיניום ו-2% ניקל"},
    folder1_name="images/שקל חדש",
    folder2_name_part=[str(i) for i in range(1980,2025)],
    folder3_name_part="10 אגורות"
)
