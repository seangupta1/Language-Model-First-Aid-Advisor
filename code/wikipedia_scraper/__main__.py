from read_write import read_list_from_file
from wikipedia_crawler import *
from config import *
from colors import Colors
from pathlib import Path
import os
import json

# Saves all articles in the specified category and its subcategories
def save_articles_from_category():
    # Save all pages in category
    pages = save_wikipedia_pages_in_category(
        category_name=category_name, 
        max_depth=max_search_depth
    )

    # Print all pages
    print(f"\n{Colors.GREEN}Collected Wikipedia Pages: {len(pages)}{Colors.RESET}")
    
# Get list of all articles in the specified category and its subcategories
def get_articles_list():
    # Save all pages in category
    pages = get_list_of_pages_in_category(
        category_name=category_name, 
        max_depth=max_search_depth
    )

    # Print all pages
    print(f"\n{Colors.GREEN}Collected Wikipedia Pages: {len(pages)}{Colors.RESET}")    

# Saves article data from a list of article titles
def save_articles_data_from_list():
    articles_to_fetch = read_list_from_file(article_list_file_path)

    save_wikipedia_articles_data(articles_to_fetch, start_index=34821)
    
# Converts article data from JSONL file
def convert_articles_data(output_file_path: str):
    # Read data from JSONL file and do some operation
    with open(article_data_file_path, "r", encoding="utf-8") as f:
        
        for index, line in enumerate(f, start=1):
            article_data_in = json.loads(line)
            
            # Print update
            if index % article_conversion_update_interval == 0:
                print(f"{Colors.YELLOW}{index} articles converted.{Colors.RESET}")       

            # Operation
            all_text = {}
            
            for key in article_data_in["text"]:        
                # path = Path(output_file_path)
                # path.parent.mkdir(parents=True, exist_ok=True)
                
                all_text[key] = remove_unwanted_text(article_data_in["text"][key])
                
            json_article = {
                'id': article_data_in['id'],
                "title": article_data_in['title'],
                'url': article_data_in['url'],
                "text": all_text
            }
            
            # Save article data to file
            save_json_data_to_file(output_file_path, json_article)
                    
    print(f"{Colors.GREEN}Data write completed!{Colors.RESET}")    

if __name__ == "__main__":
    # Step 1. Make list
    # get_articles_list()
    
    # Step 2. Get articles from list
    save_articles_data_from_list()
    
    # Step 3. Clean articles data (should not need to run because this step automaticcaly happend in step 2)
    # convert_articles_data('data/cleaned_data.jsonl')
