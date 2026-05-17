# Init wikipedia API
import wikipediaapi

user_agent = 'YOUR_PROJECT_NAME/VERSION (YOUR_EMAIL)'

wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent=user_agent
)

headers = {
    "User-Agent": user_agent
}

folder_path = "data/"
article_list_file_path = f"{folder_path}wikipedia_pages.txt"
article_data_file_path = f"{folder_path}data.jsonl"

unneeded_sections = ["See also", "References", "External links", "Further reading", "Notes", "Sources"]

delay = 0.2

article_conversion_update_interval = 100

whitelist_keywords = {
    # General treatment
    "therapy", "treatment", "intervention", "procedure",
    "management", "rehabilitation", "care",

    # Emergency care
    "emergency", "trauma", "resuscitation",
    "first aid", "critical care", "intensive care",
    "life support", "advanced life support",
    "basic life support", "cpr",
    "defibrillation", "stabilization",

    # Acute conditions management
    "cardiac", "arrest", "stroke", "treatment",
    "seizure", "shock", "management"

    # Surgical
    "surgery", "surgical", "operation",
    "transplant", "resection", "bypass",

    # Medications
    "drug", "medication", "vaccine",
    "antibiotic", "antiviral", "insulin",
    "chemotherapy", "immunotherapy",
    "blood"

    # Procedures / devices
    "intubation", "ventilation", "ventilator",
    "pacemaker", "stent", "catheter",
    "angioplasty", "dialysis", "infusion",
    "transfusion", "anesthesia", "lens"
    
    # Other
    "team", "protocol", "guideline", "algorithm",
    "prehospital", "emergency", "medical", "services", "ems",
    "global", "response", "disaster", "mass casualty",
    "triage", "transport", "evacuation", "emt", "health",
    "associalted", "associated", "complication", "outcome",
    "prognosis", "basics", "reliefe", "medical", "relief",
    "plane", "products", "product", "medic", "therapeutics",
    "bioscience", "biosciences", "pharmaceutical",
    "pharmacology", "pharmacotherapy",
}

whitelist_suffixes = (
    "ectomy", "otomy", "plasty",
    "scopy", "stomy", "therapy"
)

blocked_categories_endings = [
    "by country",
    "by continent",
    "by nationality"
]
blocked_categories_beginings = [
    "People",
]
blocked_categories = [
    "",
]

max_search_depth = 4

# category_name = "Category:Emergency medical services"
# category_name = "Category:Emergency medicine"
category_name = "Category:Medical treatments"
