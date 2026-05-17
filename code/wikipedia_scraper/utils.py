import re
from config import blocked_categories_endings, blocked_categories_beginings, whitelist_suffixes, whitelist_keywords

# Removes any junk text that may be in the article text collected
def remove_unwanted_text(text):
    # Remove headers
    final_text = re.sub(r"\n*==+.*?==+\n*", "\n", text)
    
    # Remove templates
    final_text = re.sub(r"\{\{.*?\}\}", "", final_text, flags=re.DOTALL)
    
    # Remove links
    final_text = re.sub(r"\[\[(File|Image):.*?\]\]", "", final_text)
    final_text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", final_text)
    final_text = re.sub(r"\[https?:\/\/[^\s\]]+ ?([^\]]*)\]", r"\1", final_text)

    # Remove refences
    final_text = re.sub(r"<ref.*?>.*?</ref>", "", final_text, flags=re.DOTALL)
    final_text = re.sub(r"<ref.*?/>", "", final_text)

    # Remove HTML tags
    final_text = re.sub(r"<.*?>", "", final_text)
    
    # Remove tables
    final_text = re.sub(r"\{\|.*?\|\}", "", final_text, flags=re.DOTALL)

    # Remove citation needed
    final_text = re.sub(r"\[\s*citation needed\s*\]", "", final_text, flags=re.IGNORECASE)

    # Remove category
    final_text = re.sub(r"\[\s*category:.*?\]", "", final_text, flags=re.IGNORECASE)

    # Remove new lines
    final_text = final_text.replace("\n", " ")

    # Remove extra whitespace
    final_text = re.sub(r"\s+", " ", final_text).strip()
    
    return final_text

def is_blocked_category(category_name: str):
    for category_ending in blocked_categories_endings:
        if category_name.endswith(category_ending):
            return True
    for category_begining in blocked_categories_beginings:
        if category_name.startswith(category_begining):
            return True
    return False

def is_persons_name(title):
    # Skip articles that are possibly about people
    words = title.split()
    if len(words) in [2, 3] and all(w[0].isupper() for w in words) and not any(w.endswith(whitelist_suffixes) for w in words) and not any(keyword in title.lower() for keyword in whitelist_keywords):
        return True
    return False