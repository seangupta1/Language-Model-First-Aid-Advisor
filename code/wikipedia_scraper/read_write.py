import os
import json
import wikipediaapi
from pathlib import Path

def read_list_from_file(filepath: str) -> list[str]:
    print(f"Reading list from {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_title(filepath: str, page_title: str):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Writing page title '{page_title}' to {filepath}")
    
    file_exists = os.path.exists(filepath) and os.path.getsize(filepath) > 0
    
    with open(filepath, "a", encoding="utf-8") as f:
        if file_exists:
            f.write("\n" + page_title)
        else:
            f.write(page_title)
        
def save_json_data_to_file(filepath: str, json_data: dict):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    page_id = json_data["id"] 
    title = json_data["title"]
    print(f"Saving article {page_id} - '{title}' to {filepath}")
    
    with open(filepath, "a", encoding="utf-8") as out:
        out.write(json.dumps(json_data, ensure_ascii=False) + "\n")