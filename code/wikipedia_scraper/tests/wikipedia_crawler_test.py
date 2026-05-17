import wikipediaapi
import time
import random

def collect_wikipedia_pages_in_category(
    category_name: str, 
    max_depth: int = 1,
    depth: int = 0, 
    visited_categories: set[str] | None = None, 
    pages: set[str] | None = None
    ):
    
    if visited_categories is None:
        visited_categories = set()
    if pages is None:
        pages = set()
        
    if not category_name.startswith("Category:"):
        raise ValueError("category_name must start with 'Category:'")
    
    if category_name in visited_categories or depth >= max_depth:
        return pages
    
    visited_categories.add(category_name)
    
    delay = random.uniform(1, 5)
    time.sleep(delay)
    # current_page = wiki.page(category_name)
    current_page = get_mock_page(category_name)
    
    if not current_page.exists():
        raise ValueError(f"{category_name} does not exist.")
    
    print(f"Processing current page: {category_name} at depth {depth} (after {delay:.2f}s delay)")
    
    for member in current_page.categorymembers.values():
        delay = random.uniform(1, 5)
        time.sleep(delay)

        print(f"  Accessing member: {member.title} (after {delay:.2f}s delay)")
        
        if member.ns == wikipediaapi.Namespace.MAIN:
            pages.add(member.title)
        elif member.ns == wikipediaapi.Namespace.CATEGORY:
            collect_wikipedia_pages_in_category(
                member.title, 
                max_depth, 
                depth + 1, 
                visited_categories, 
                pages
            )
            
    return pages

# pages = collect_wikipedia_pages_in_category(category_name="Category:Machine learning algorithms", max_depth=20)
# print(pages)

# -----------------------------
# MockPage class
# -----------------------------
class MockPage:
    def __init__(self, title, ns=None, exists=True, members=None):
        self.title = title
        # Determine namespace automatically
        if ns is None:
            self.ns = wikipediaapi.Namespace.CATEGORY if title.startswith("Category:") else wikipediaapi.Namespace.MAIN
        else:
            self.ns = ns
        self._exists = exists
        self.categorymembers = members or {}

    def exists(self):
        return self._exists

# -----------------------------
# Mock category tree
# -----------------------------

mock_category_members = {
    "Page A": MockPage("Page A"),
    "Category:Subcategory B": MockPage(
        "Category:Subcategory B",
        members={
            "Page B1": MockPage("Page B1"),
            "Page B2": MockPage("Page B2"),
            "Category:Subcategory B1": MockPage(
                "Category:Subcategory B1",
                members={
                    "Page B1-1": MockPage("Page B1-1"),
                    "Category:Subcategory B1a": MockPage(
                        "Category:Subcategory B1a",
                        members={
                            "Page B1a-1": MockPage("Page B1a-1"),
                            "Page B1a-2": MockPage("Page B1a-2"),
                        }
                    )
                }
            ),
        }
    ),
    "Category:Subcategory C": MockPage(
        "Category:Subcategory C",
        members={
            "Page C1": MockPage("Page C1"),
            "Category:Subcategory C1": MockPage(
                "Category:Subcategory C1",
                members={
                    "Page C1-1": MockPage("Page C1-1"),
                    "Page C1-2": MockPage("Page C1-2"),
                }
            ),
        }
    )
}


# -----------------------------
# Function to get the correct mock page
# -----------------------------
def find_subcategory(title, category_members):
    """Recursively search for a subcategory by title in the mock tree."""
    if title in category_members:
        return category_members[title]
    for member in category_members.values():
        if member.ns == wikipediaapi.Namespace.CATEGORY:
            found = find_subcategory(title, member.categorymembers)
            if found:
                return found
    return None

def get_mock_page(title):
    if title == "Category:Root":
        return MockPage("Category:Root", members=mock_category_members)
    elif title.startswith("Category:"):
        found = find_subcategory(title, mock_category_members)
        if found:
            return found
        # If not found, return empty category
        return MockPage(title)
    else:
        # Individual pages
        return MockPage(title)


    



all_pages = collect_wikipedia_pages_in_category(
    "Category:Root",
    max_depth=5
)

print("Pages found in dry-run:")
for p in sorted(all_pages):
    print(p)
    
with open("wikipedia_pages.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(all_pages)))