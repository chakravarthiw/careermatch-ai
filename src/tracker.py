# src/tracker.py
# ─────────────────────────────────────────────────────────────
# This file:
#     1. Manages ALL reading and writing of Job Application data
#     2. Acts as a database layer - nothing else writes to Excel sheet directly other than this file

# INPUTS:
#     1. Job Details: title, company, link etc - as function arguments

# OUTPUT:
#     1. PANDAS Dataframe and saved excel file
# ─────────────────────────────────────────────────────────────

import os
from datetime import date
import pandas as pd

# Path to excel tracker file
# Changes to excel filename can be made in one place only
TRACKER_PATH = "data/applications.xlsx"


# ── COLUMNS ───────────────────────────────────────────────────
# Defines all columns that the tracker sheet will have.
# Every saved job will have all fields even if empty.
# Add new columns here to reflect changes across the platform.
COLUMNS = [
    "Job Title", "Company", "Location", "Job Link", "Source", "Closing Date", "Date Found",
    "Date Applied", "Status", "Match Score", "Sponsorship", "Employment Type", "Salary / Rate",
    "Resume Version", "Cover Letter Version", "Contact Person", "Contact Email", "Follow-up Date",
    "Interview Date", "Notes"
]


# ── STATUSES ──────────────────────────────────────────────────
# Every valid stage the application can be at.
# Used in dropdowns throughout the UI.
# Change here makes changes across the platform.
STATUSES = [
    "Saved", "Tailoring", "Applied", "Follow-up Sent", "Interview", "Final Stage", "Offer",
    "Rejected", "Closed"
]


def load_tracker() -> pd.DataFrame:
    # Loads saved jobs from Excel - returns them in table format.
    # If file doesn't exist - returns an empty table with correct columns.
    # Input : No explicit inputs - knows file location via TRACKER_PATH
    # Output: DataFrame of all saved jobs

    if os.path.exists(TRACKER_PATH):
        return pd.read_excel(TRACKER_PATH)
    return pd.DataFrame(columns=COLUMNS)


def save_tracker(df: pd.DataFrame) -> None:
    # Writes job data to Excel file.
    # Creates data/ folder first if it doesn't already exist.
    # Input : DataFrame containing all job rows
    # Output: Nothing returned - saves Excel file to disk

    # exist_ok=True handles the case where folder already exists - no crash
    os.makedirs("data", exist_ok=True)
    # index=False stops an extra row-number column appearing in the spreadsheet
    df.to_excel(TRACKER_PATH, index=False)


def add_job(
        job_title: str,
        company: str,
        location: str,
        job_link: str,
        source: str,
        closing_date: str,
        employment_type: str,
        salary: str,
        sponsorship: str,
        notes: str
) -> pd.DataFrame:
    # Takes all details of one job and adds it as a new row in the tracker.
    # Called when the "Save Job" button is clicked in app.py.
    # Input : All job fields as string arguments
    # Output: Updated DataFrame after new row is added and saved

    # Always load existing data first - never overwrite existing jobs
    df = load_tracker()

    # Extra security check for required fields
    # Second layer of protection beyond the UI validation in app.py
    if not job_title or not company:
        return df

    # Create a blank "form" with every column as a key and "" as default.
    # Guarantees every row always has every column - no missing fields.
    new_entry = {col: "" for col in COLUMNS}

    # Fill in the actual values.
    # date.today().strftime("%Y-%m-%d") gives today's date as "2025-05-01" - clean for Excel
    new_entry.update(
        {
            "Job Title"       : job_title,
            "Company"         : company,
            "Location"        : location,
            "Job Link"        : job_link,
            "Source"          : source,
            "Closing Date"    : closing_date,
            # Auto-filled fields - user never needs to enter these manually
            "Date Found"      : date.today().strftime("%Y-%m-%d"),
            "Status"          : "Saved",
            "Sponsorship"     : sponsorship,
            "Employment Type" : employment_type,
            "Salary / Rate"   : salary,
            "Notes"           : notes,
        }
    )

    # pd.concat() appends the new row to the existing table.
    # ignore_index=True resets row numbers to stay clean: 0, 1, 2, 3...
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    save_tracker(df)
    return df


def update_status(row_index: int, new_status: str) -> pd.DataFrame:
    # Finds a row by its index number and updates the Status column.
    # If new status is "Applied", also auto-fills today's date in Date Applied.
    # Input : row_index — which row to update, new_status — what to change it to
    # Output: Updated DataFrame after the change is saved

    df = load_tracker()

    # Safety check - only proceed if the row number actually exists
    if 0 <= row_index < len(df):
        # df.at[row, column] = go to this exact cell and change the value
        df.at[row_index, "Status"] = new_status

        # If marked as Applied, auto-fill today's date in Date Applied column
        if new_status == "Applied":
            df.at[row_index, "Date Applied"] = date.today().strftime("%Y-%m-%d")

        save_tracker(df)

    return df