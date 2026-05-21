# src/resume_store.py
# ─────────────────────────────────────────────────────────────
# Resume Store - CareerMatch AI

# What this file does:
#     1.Provides simple persistant store for user's master resume
#     2. Saved Once - used everywhere - no repeated pasting

# Storage:
#     1. Plain Text file at data/master_resume.txt
#     2. Gitignored - personal data never commited to github

# INPUTS:
#     1. resume text as string
# OUTPUTS:
#     1. resume text as a string, or "" if not saved 
# ─────────────────────────────────────────────────────────────

import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_PATH = BASE_DIR / "data" / "master_resume.txt"
TIMESTAMP_PATH = "data/resume_last_updated.txt"

def save_resume(text: str) -> None:
    # Saves resume text to disk
    # Overwrites any perviously saved resume 
    # Input: Resume Text as string 
    # Output: Writes file to disk
    os.makedirs("data", exist_ok = True)
    with open(RESUME_PATH, "w", encoding ="utf-8") as f:
        f.write(text.strip())
        # Save timestamp
        updated_at = datetime.now().strftime(
            "%d %b %Y %I:%M %p"
        )
        with open(TIMESTAMP_PATH, "w", encoding = "utf-8") as f:
            f.write(updated_at)


def load_resume() -> str:
    # Loads saved resume text from disk
    # Returns empty string if no resume saved yet
    # Input: No inputs to this function
    # Output: resume as text or "" if not found
    try:
        if os.path.exists(RESUME_PATH):
            with open(RESUME_PATH, "r", encoding = "utf-8") as f:
                return f.read()
        return ""
    except Exception as e:
         print(f"Resume save error: {e}")


def resume_exists() -> bool:
    # Checks if the resume has been saved
    # Used to show/hide ATS buttons through the app
    # Input: No inputs to this function
    # Output: True if resume exists and not empty
    text = load_resume()
    return bool(text.strip())


def delete_resume() -> None:
    if os.path.exists(RESUME_PATH):
        os.remove(RESUME_PATH)


def get_resume_last_updated() -> str:
    # Returns last updated timestamp for the resume 
    # returns "Unknown" if timestamp missing
    if os.path.exists(TIMESTAMP_PATH):
        with open(TIMESTAMP_PATH, "r", encoding = "utf-8") as f:
            return f.read().strip()
    return "Unknown"