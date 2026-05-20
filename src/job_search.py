# src/job_search.py
# ---------------------------------------------------------
# Handles all job search functionality using Adzuna API

# INPUT       : Keyword + Location

# OUTPUT      : Clean List of jobs with Sponsorship Analysis 
# ---------------------------------------------------------

import os
import requests
from dotenv import load_dotenv

from src.utils import sponsorship_label

# Load environment variable 
load_dotenv()

# Read API Credentials 
APP_ID  = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


def search_jobs(
        keyword                 : str,
        location                : str,
        sponsorship_priority    : bool = False
) -> list:
    # This function searches for jobs, enriches them and returms clean data 
    # INPUTS : 
    #         1. keyword
    #         2. location 
    #         3. sponsorship_priority
    # OUTPUTS: List of jobs with keyword, location and sponsorship status

    # Prevent empty searches
    if not keyword:
        return []

    # Adzuna Australia API endpoint
    url =   "https://api.adzuna.com/v1/api/jobs/au/search/1"


    # Parameters sent to API
    params = {
        "app_id"            : APP_ID,
        "app_key"           : APP_KEY,
        "what"              : keyword,
        "where"             : location,
        "results_per_page"  : 10
    }

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
            sponsorship = sponsorship_label(description) if len(description) > 100 else "See full listing"

            # Create a dictionary for clean jobs
            cleaned_jobs = {
                "title"         : job.get("title", "N/A"),
                "company"       : (job.get("company", {})
                                   .get("display_name", "N/A")),
                "location"      : (job.get("location", {})
                                   .get("display_name", "N/A")),
                "salary_min"    : job.get("salary_min"),
                "salary_max"    : job.get("salary_max"),
                "link"          : job.get("redirect_url", ""),
                "description"   : description,
                "sponsorship"   : sponsorship
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


# if __name__ == "__main__":

#     jobs = search_jobs(
#         keyword="Data Analyst",
#         location="Melbourne",
#         sponsorship_priority=True
#     )

#     print("\nTOTAL JOBS FOUND:", len(jobs))

#     for job in jobs[:3]:

#         print("\n------------------------")
#         print("TITLE:", job["title"])
#         print("COMPANY:", job["company"])
#         print("LOCATION:", job["location"])
#         print("SPONSORSHIP:", job["sponsorship"])
#         print("LINK:", job["link"])
