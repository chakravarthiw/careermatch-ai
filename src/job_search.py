# src/job_search.py
# ─────────────────────────────────────────────────────────────
# Job Search Logic - CareerMatch AI
# ─────────────────────────────────────────────────────────────
# Handles all job search functionality using Adzuna API
# Talks to the Adzuna API
# Streamlit UI asks: "Find me Data Analyst jobs in Melbourne"

# This file:
#     1. Sends Streamlit Search request to Adzuna.
#     2. Receives Raw job results back.
#     3. Cleans messy API data to simple disctionaries
#     4. Adds Sponsorship detection
#     5. Adds Employment type detection
#     6. Sends clean jobs back to Streamlit UI

# INPUT       : Keyword + Location + Optional advanced features

# OUTPUT      : Clean List of jobs with Sponsorship Analysis 
# ---------------------------------------------------------

import os
import requests
from dotenv import load_dotenv
from src.utils import sponsorship_label, extract_employment_type

# Load environment variable 
load_dotenv()

# Read API Credentials 
APP_ID  = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


def search_jobs(
        keyword                 : str,
        location                : str,
        sponsorship_priority    : bool = False,
        jobs_to_fetch           : int  = 10,
        sort_by                 : str = "Relevance",
        max_age_days            : int | None = None
) -> list:
    
    '''
    Search for jobs using Adzuna API

    Parameters:
        keyword                 : Job title. Example: "Data Analyst"
        location                : City/State/Country. Example: "Melbourne"
        sponsorship_priority    : If True, sponsorship friendly jobs at top of page
        results_per_page        : Number of jobs to request from Adzuna. Example: 10,25,50
        sort_by                 : How results are to be sorted
        max_age_days            : Only show jobs posted within the mentioned number of days. Example: 7 days, 12 days 

        Returns:
            List of cleaned job disctionaries
    '''

    # Prevent empty searches
    if not keyword:
        return []
    
    # If API keys are missing, stop early.
    # Prevents from confusing crashes
    if not APP_ID or not APP_KEY:
        print("Not able to connect to Adzuna API. Check connections please.")
        return []

    # Adzuna Australia API endpoint
    url =   "https://api.adzuna.com/v1/api/jobs/au/search/1"


    # Parameters sent to API
    # This is the search form we send to the API
    params = {
        "app_id"            : APP_ID,
        "app_key"           : APP_KEY,
        "what"              : keyword,
        "where"             : location,
        "results_per_page"  : jobs_to_fetch,
        "content-type"      : "application/json"
    }

    # Add date filter only when user selects one
    if max_age_days is not None:
        params["max_days_old"] = max_age_days

    # Convert UI labels to Adzuna sort values
    if sort_by == 'Date':
        params["sort_by"] = "date"

    elif sort_by == "Salary":
        params["sort_by"] = "salary"

    try:
        # send request to Adzuna
        response = requests.get(url, params=params, timeout = 10)
        # Raise exception if status code is 4xx or 5xx
        response.raise_for_status()

        # Converst JSON response to python dictionary
        data = response.json()

        # Store clean jobs 
        jobs = []

        # Loop through returned jobs
        for job in data.get("results", []):

            # Extract job description
            description = job.get("description", "")

            # Run sponsorship detection
            sponsorship = sponsorship_label(description)

            # Run employment type dectector
            employment_type = extract_employment_type(description) 

            # Create a dictionary for clean jobs
            cleaned_jobs = {
                "title"             : job.get("title", "N/A"),
                "company"           : (job.get("company", {})
                                   .get("display_name", "N/A")),
                "location"          : (job.get("location", {})
                                   .get("display_name", "N/A")),
                "salary_min"        : job.get("salary_min"),
                "salary_max"        : job.get("salary_max"),
                "contract_type"     : job.get("contract_type"),
                "link"              : job.get("redirect_url", ""),
                "created"           : job.get("created"),
                "description"       : description,
                "sponsorship"       : sponsorship,
                "employment_type"   : employment_type 
            }

            # Append details to JSON cleaned job list
            jobs.append(cleaned_jobs)

        # Sponsorship Aware results list
        # Sort sponsorship-friendly jobs to top if requested
        if sponsorship_priority:
            priority_order = {
                "Likely Sponsorship" : 0,
                "Unknown"            : 1,
                "Not Mentioned"      : 2,
                "No Sponsorship"     : 3
            }
            jobs.sort(
                key=lambda x: priority_order.get(x["sponsorship"], 99)
            )

        return jobs

    except requests.exceptions.RequestException as e:
        print(f"API ERROR: {e}")
        return []
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return []


