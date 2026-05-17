import wikipediaapi
import time
import requests
from config import *
from read_write import save_json_data_to_file, save_title
from colors import Colors
from utils import is_blocked_category, is_persons_name, remove_unwanted_text

def save_wikipedia_pages_in_category(
    category_name: str, 
    max_depth: int = 1,
    depth: int = 0, 
    visited_categories: set[str] | None = None, 
    pages: set[str] | None = None
    ):
    
    # Init sets on first run
    if visited_categories is None:
        visited_categories = set()
    if pages is None:
        pages = set()
        
    # Check if category
    if not category_name.startswith("Category:"):
        raise ValueError("category_name must start with 'Category:'")
    
    # Check if already visited of max depth reached
    if category_name in visited_categories:
        return pages
    if depth >= max_depth:
        print(f"{Colors.RED}Max depth {max_depth} reached at category {category_name}.{Colors.RESET}")
        return pages
    
    # Add category to visited
    visited_categories.add(category_name)
    
    # Delay to not spam API
    time.sleep(delay)
    
    # Get current page from API
    current_page = wiki.page(category_name)
    
    # Check if page exists
    if not current_page.exists():
        raise ValueError(f"{category_name} does not exist.")
    
    # Print update
    print(f"\nProcessing current page: {category_name} at depth {depth} (after {delay:.2f}s delay)")
    
    # Loop through each member in category
    for member in current_page.categorymembers.values():
        # Delay to not spam API
        time.sleep(delay)

        # Print update
        print(f"\nAccessing member: {member.title} (after {delay:.2f}s delay)")
        
        # Check if page elif category
        if member.ns == wikipediaapi.Namespace.MAIN:
            
            if member.title not in pages:
                
                # Add page id to pages set
                pages.add(member.title)
                
                # Save page title to file
                save_title(article_list_file_path, member.title)
                
                # Save article text to file
                save_wikipedia_article_data(member)
            
        elif member.ns == wikipediaapi.Namespace.CATEGORY:
            # Recurse into the sub category
            save_wikipedia_pages_in_category(
                member.title, 
                max_depth, 
                depth + 1, 
                visited_categories, 
                pages
            )
    
    # Return all pages
    return pages

def get_wikipedia_article(article_title: str):
    # Checck article title
    if article_title is None:
        raise ValueError("article_title can't be None")
    
    # Delay to not spam API
    time.sleep(delay)
    
    # Get current page from API
    current_page = wiki.page(article_title)
    
    # Check if page exists
    if not current_page.exists():
        raise ValueError(f"{article_title} does not exist.")
    
    # Print update
    print(f'Retrieved article: {article_title} after {delay:.2f}s delay')
    
    # Return page
    return current_page

def save_wikipedia_articles_data(article_titles: list[str], start_index=0):
    # Check article titles
    if article_titles is None:
        raise ValueError("article_titles can't be None")
    
    # Remove duplocates
    article_titles = list(set(article_titles))
    
    # Sort
    article_titles.sort()
    
    # Set start index
    article_titles = article_titles[start_index:]
    
    # Loop through each article
    for index, title in enumerate(article_titles, start=1):
        print(f"Processing article: {title}")
        
        total = len(article_titles)
        remaining = total - index
        seconds_remaining = remaining * (delay + 0.55)
        time_to_complete_seconds = (int)(seconds_remaining % 60)
        time_to_complete_minutes = (int)(seconds_remaining // 60)
        time_to_complete_minutes_displayed = (int)(time_to_complete_minutes % 60)
        time_to_complete_hours= (int)(time_to_complete_minutes // 60)
        
        print(f"{Colors.YELLOW}Progress: {index}/{len(article_titles)} | {index / len(article_titles) * 100:.2f}% | Estimated time remaining: {time_to_complete_hours} hours, {time_to_complete_minutes_displayed} minutes, {time_to_complete_seconds} seconds{Colors.RESET}")
        
        # Retrieve article
        article = get_wikipedia_article(title)
        
        all_text = {}
        for section in article.sections:
            all_text.update(extract_relevant_text(section))
        
        json_article = {
            'id': article.pageid,
            "title": article.title,
            'url': article.fullurl,
            "text": all_text
        }
        
        # Save article data to file
        save_json_data_to_file(article_data_file_path, json_article)
        
def save_wikipedia_article_data(article: wikipediaapi.WikipediaPage):
    if article is None:
        raise ValueError("article can't be None")
    
    all_text = {}
    for section in article.sections:
        all_text.update(extract_relevant_text(section))
    
    json_article = {
        'id': article.pageid,
        "title": article.title,
        'url': article.fullurl,
        "text": all_text
    }
    
    # Save article data to file
    save_json_data_to_file(article_data_file_path, json_article)

def extract_relevant_text(section: wikipediaapi.WikipediaPageSection, all_section_text: dict | None = None):
        if all_section_text is None:
            all_section_text = {}
            
        if section.title not in unneeded_sections:
            all_section_text[section.title] = remove_unwanted_text(section.text.strip())
        
        for subsection in section.sections:
            extract_relevant_text(subsection, all_section_text)
        
        return all_section_text

def get_list_of_pages_in_category(
    category_name: str, 
    max_depth: int = 1,
    depth: int = 0, 
    visited_categories: set[str] | None = None, 
    pages: set[str] | None = None
    ):
    
    # Init sets on first run
    if visited_categories is None:
        visited_categories = set()
    if pages is None:
        pages = set()
        
    # Check if category
    if not category_name.startswith("Category:"):
        raise ValueError("category_name must start with 'Category:'")
    
    # Check if already visited of max depth reached
    if category_name in visited_categories or category_name in blocked_categories or is_blocked_category(category_name) or is_persons_name(category_name):
        # Print update
        print(f"{Colors.RED}Skipping category: {category_name} (already visited or blocked){Colors.RESET}")
        return pages
    if depth >= max_depth:
        print(f"{Colors.RED}Max depth {max_depth} reached at category {category_name}.{Colors.RESET}")
        return pages

    # Print update
    print(f"{Colors.YELLOW}{len(pages)} pages collected | {len(visited_categories)} categories collected{Colors.RESET}")
    
    # Add category to visited
    visited_categories.add(category_name)
    
    # Delay to not spam API
    time.sleep(delay)
    
    # Print update
    print(f"\nAccessing category: {category_name} (after {delay:.2f}s delay)")
    
    # Get current page from API
    current_page = wiki.page(category_name)
    
    # Check if page exists
    if not current_page.exists():
        raise ValueError(f"{category_name} does not exist.")
    
    # Print update
    print(f"\nProcessing current page: {category_name} at depth {depth} (after {delay:.2f}s delay)")
    
    # Loop through each member in category
    for member in current_page.categorymembers.values():
        
        # Check if page elif category
        if member.ns == wikipediaapi.Namespace.MAIN:
            
            if member.title not in pages:
                
                # Skip if possible person's name
                if is_persons_name(member.title):
                    print(f"{Colors.RED}Skipping page: {member.title} (possible person's name){Colors.RESET}")
                    continue
                
                # Add page title to pages set
                pages.add(member.title)
                
                # Save page title to file
                save_title(article_list_file_path, member.title)
            
        elif member.ns == wikipediaapi.Namespace.CATEGORY:
            # Delay to not spam API
            time.sleep(delay)
            
            # Recurse into the sub category
            get_list_of_pages_in_category(
                member.title, 
                max_depth, 
                depth + 1, 
                visited_categories, 
                pages
            )
    
    # Return all pages
    return pages