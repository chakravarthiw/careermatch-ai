# src/learner.py
# ─────────────────────────────────────────────────────────────
# This file:
#     1. Records job title corrections as Naive Bayes training data
#     2. Maintains a growing list of known companies
#     3. both data sets grow as more jobs are saved

# Inputs:
#     1. confirmed_title      - what user types in Job Title field
#     2. dectedted_title      - what extract_job_title() guessed
#     3. confirmed_company    - what user typed in Company field
#     4. detected_company     - what extract_company() guessed
#     5. first_line           - line 1 of job description


# Outputs:
#     1. data/title_memory.json   - labelled training data for Naive Bayes
#     2. ata/company_memory.json - known company names for lookup

# ─────────────────────────────────────────────────────────────

import json
import os
from datetime import date


# ── File Paths ────────────────────────────────────────────────
# Both memory files live in data/ folder
# data/ -> is git-ignored so personal data is always safe
TITLE_MEMORY_PATH = "data/title_memory.json"
COMPANY_MEMORY_PATH = "data/company_memory.json"


# Minimum entries before Naibe Bayes training begins
# Below this - rule based extractor handles everything
MIN_SAMPLES = 15

# ══════════════════════════════════════════════════════════════
# TITLE MEMORY
# Stores every save event as training example
# was_corrected = True    -> user changed what extractor guessed
# was_corrected = False   -> extractor was right
# ══════════════════════════════════════════════════════════════


def load_title_memory() -> list:

    # Loads all saved title correction entries
    # Input: None - reads from TITLE_MEMORY_PATH
    # Output: list of entry dicts/ empty list if file not found

    if os.path.exists(TITLE_MEMORY_PATH):
        with open(TITLE_MEMORY_PATH, "r") as f:
            return json.load(f)
    return []


def record_correction(
        confirmed_title : str,
        detected_title  : str,
        first_line      : str,
        second_line     : str = ""  
)-> None:
    # Saves one title save event to training data 
    # Called on every Save Job action - corrections and correct predictions saved
    # Input:  1. confirmed_title  : what user typed
    #         2. detected_title   : what extract_job_title() predicted
    #         3. first_line       : raw line 1 of job description
    #         4. second_line      : raw line 2 of job description
    # Output: writes to data/title_memory.json

    memory = load_title_memory()

    entry = {
        "date"              : date.today().strftime("%Y-%m-%d"),
        "confirmed_title"   : confirmed_title.strip(),
        "detected_title"    : detected_title.strip(),
        "first_line"        : first_line.strip(),
        "second_line"       : second_line.strip(),
        # Key Training label -> was extractor correct
        "was_corrected"     : confirmed_title.strip() != detected_title.strip()
    }
    memory.append(entry)
    os.makedirs("data",exist_ok=True)

    with open(TITLE_MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)


# ══════════════════════════════════════════════════════════════
# COMPANY MEMORY
# Stores every confirmed company name as lookup entry
# Used by extract_company() as seach before regex runs
# Grows automatically - no manual maintainance needed
# ══════════════════════════════════════════════════════════════


def load_company_memory() -> list:
   
    # Loads list of known company entries
    # Input: reads from data/company_memory.json
    # Output: list of companies in dictionary format / empty list if not found

    if os.path.exists(COMPANY_MEMORY_PATH):
        with open(COMPANY_MEMORY_PATH, "r") as f:
            return json.load(f)
    return []


def record_company(
        confirmed_company   : str,
        detected_company    : str
) -> None:
    
    # Saves Company name after every job save
    # Only adds if already not in memory - not storing duplicates
    # Input: 1. confirmed_company     : what is typed in Company field
    #        2. detected_company      : what extract_company() guessed
    # Output: writes to data/company_memory.json

    if not confirmed_company.strip():
        return
    
    memory = load_company_memory()

    # Duplicate check - case insensitive
    # "AO" and "ao" are the same
    known = {e['company'].lower() for e in memory}

    if confirmed_company.strip().lower() not in known:
        memory.append({
            "date"              : date.today().strftime("%Y-%m-%d"),
            "company"           : confirmed_company.strip(),
            "was_corrected"     : confirmed_company.strip().lower() != detected_company.strip().lower()
        })

        os.makedirs("data", exist_ok=True)

        with open(COMPANY_MEMORY_PATH, "w") as f:
            json.dump(memory, f, indent=2)


def get_known_companies() -> list:

    # Returns list of company names
    # called by app.py to pass to extract_company()
    # Input: None
    # Output: List of strings
    memory = load_company_memory()
    return [e["company"] for e in memory]   


# ══════════════════════════════════════════════════════════════
# STATS
# Summary of collected training data
# Used by dashboard to show learning process 
# ══════════════════════════════════════════════════════════════


def correction_status() -> dict:
    # Returns summary of the title and company memory
    # Input: None
    # Output: Dict with counts and current learning phase

    title_memory    = load_title_memory()
    company_memory  = load_company_memory()
    total           = len(title_memory)
    corrections     = sum(1 for e in title_memory if e.get("was_corrected"))

    return {
        "title_entries"           : total,
        "title_corrections"       : corrections,
        "correct_predictions"     : total - corrections,
        "known_companies"         : len(company_memory),
        "phase"                   : (
            "Alpha - Collecting Data" if total < MIN_SAMPLES else
            "Beta - Ready to Train"
        ),
        "entries_until_beta"      : max(0, MIN_SAMPLES - total)
    }