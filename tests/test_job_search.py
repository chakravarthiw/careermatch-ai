# tests/test_job_search.py
# ---------------------------------------------------------
# Tests Adzuna API job search functionality
# ---------------------------------------------------------

from src.job_search import search_jobs

def test_search_jobs():

    # Run job search 
    jobs = search_jobs(
        keyword = "Data Analyst",
        location = "Melbourne",
        sponsorship_priority = True
    )

    # Basic Assertsions
    assert isinstance(jobs, list)

    # Ensure at lease one is returned
    assert len(jobs) > 0

    # print first few jobs for inspections
    for job in jobs[0:3]:
        print("\n-------------")
        print("TITLE:", job["title"])
        print("COMPANY:", job["company"])
        print("LOCATION:", job["location"])
        print("SPONSORSHIP:", job["sponsorship"])
        print("LINK:", job["link"])
        print("DESC LENGTH :", len(job["description"]))
        print("DESCRIPTION:", job["description"])

    # Don't assert specific sponsorship values — API results change
    # Just assert the structure is correct
    assert all("title" in job for job in jobs)
    assert all("sponsorship" in job for job in jobs)