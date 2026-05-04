# src/utils.py
# ─────────────────────────────────────────────────────────────

# This file:
#     1. Contails all the program logic for the app.
#     2. Only functions that are being used across the app, taking inputs and returns outputs without any external interference

# INPUTS:
#     1. Text string, Job descriptions and Date Strings

# OUTPUT:
#     1. Processed values - labels, extracted dates, urgency texts

# ─────────────────────────────────────────────────────────────


import re
from datetime import datetime


def days_until(date_str: str) -> int| None:
    
    # Claculates number of days remaining till a job closing date
    # Returns a negative number if date has already passed
    # For error's regarding missing date or unreadable dates- None returned
    # Input: date string - Eg: "2025-06-01" or "2025-06-01 00:00:00"
    # Output: days left integer / or None for no valid date

    # Handle missing, nan, or balnk values from Excel
    if not date_str or str(date_str).lower() in ["nan", "none", ""]:
        return None
    try:
        #[:10] takes only "YYYY-MM-DD" format ignoring suffix added by excel
        closing = datetime.strptime(str(date_str)[:10], "%Y-%m-%d").date()
        today = datetime.today().date()
        return (closing - today).days #date subtraction like integer
    except ValueError:
        return None #If format is unexpected - fail safetly
    

def urgency_label(days: int | None) -> str:
    
    # Convert number of days to readable format
    # Used in dashboard "Closing Soon" table
    # Input: integer / None
    # Output: readable text like "Urgent - 2 Days Left"

    if days is None     : return "No Closing Date"
    if days < 0         : return "Closed"
    if days == 0        : return "Closes Today"
    if days <= 2        : return f"Urgent - {days} days left"
    if days <= 7        : return f"This week - {days} days remaining"
    return f"{days} days remaining"


def sponsorship_label(job_description: str) -> str:

    # Scans job description and classifies visa sponsorship status
    # Checks EXCLUSION language first - hard no is more important to catch than a maybe. 
    # Then checks for positive signals with regards to visa sponsorship
    # Inputs: Job description text
    # Output: One of the below
    #         1. "No Sponsorship"     - Job explicitly excludes visa holders
    #         2. "Likely Sponsorship" - Job mentions visa support
    #         3. "Not Mentioned"      - No visa information in job description
    #         4. "Unknown"            - No job description provided

    if not job_description:
        return "Unknown"
    

    # Convert job description to lower case, for NLP progression of visa sponsorship details
    text = job_description.lower()


    # ── Exclusion signals — checked FIRST ────────────────────
    # if any of the below words appear - clear that there is no sponsorship
    no_sponsorship_phrases = [
        "must have full working rights",
        "full working rights in australia",
        "right to work in australia",
        "australian citizens only",
        "australian citizen or permanent resident",
        "permanent residents only",
        "no sponsorship",
        "cannot sponsor",
        "not able to sponsor",
        "sponsorship is not available"
    ]


    # ── Positive signals — checked SECOND ────────────────────
    likely_sponsorship_phrases = [
        "visa sponsorship",
        "sponsorship available",
        "482 visa",
        "tss visa",
        "employer sponsored",
        "work visa support",
        "willing to sponsor",
        "sponsorship provided"
    ]


    # Loop through Exclusions - return if match found
    for phrase in no_sponsorship_phrases:
        if phrase in text:
            return "No Sponsorship"
        

    # Loop through to check if sponsorship is likely
    for phrase in likely_sponsorship_phrases:
        if phrase in text:
            return "Likely Sponsorship"
        
    
    # For No visa information in job description
    return "Not Mentioned"


def extract_closing_date(job_description: str) -> str:
    # Looks for a closing date within Job description
    # Only recogonised when preceeded by for suffixed by phrases like "applications close" or "apply by"
    # This prevents errors related to extracting start dates or any other dates
    # Input: raw job description text
    # Output: YYYY_MM_DD if closing date found / "" if not found

    
    # Checking for job description - return "" if not found
    if not job_description:
        return ""
    

    # # ── Anchor phrases ────────────────────────────────────────
    # We only looking for dates following one of these phrases
    # re.IGNORECASE makes it case insensitive so "Apply By" also matches
    anchor_patterns = [
    r"applications?\s+close[sd]?\s*[:\-]?\s*(?:on\s+)?(.+)",
    r"closing\s+date\s*[:\-]?\s*(.+)",
    r"apply\s+by\s*[:\-]?\s*(.+)",
    r"closes\s*[:\-]?\s*(.+)",
    r"application\s+deadline\s*[:\-]?\s*(.+)",
    r"deadline\s*[:\-]?\s*(.+)",
    r"apply\s+before\s*[:\-]?\s*(.+)",
]


    # Month name to number lookup

    month_map = {
        "january"   :   "01"  ,
        "february"  :   "02"  ,
        "march"     :   "03"  ,
        "april"     :   "04"  ,   
        "may"       :   "05"  ,
        "june"      :   "06"  ,
        "july"      :   "07"  ,
        "august"    :   "08"  ,
        "september" :   "09"  ,
        "october"   :   "10"  ,
        "november"  :   "11"  ,
        "december"  :   "12"  ,
    }


    def try_parse(raw :str) -> str:
        # Takes raw text after anchor words to extract a date
        # Input: raw text from job description following an anchor phrase
        # Output: YYYY_MM_DD if date found / "" if no date found


        # Stripping Punctuations and spaces 
        raw = raw.strip(".,: ")


        # Handles different newline types -> \n, \r\n, \r
        # [0] - takes only the first line - so that unrelated text not parsed
        # raw = raw.splitlines()[0].strip()
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        raw = lines[0] if lines else ""
        if not raw:
            return ""
        
        # Keep only the likely date section, so extra description text does not confuse parsing
        raw = raw[:40]


        # PATTERN 1:  DD Month YYYY - eg: 20 May 2025
        m = re.search(
            r'(\d{1,2})\s+(january|february|march|april|may|june|july|august'
            r'|september|october|november|december)\s+(\d{4})',
            raw.lower()
        )
        if m:
            day = m.group(1).zfill(2) # zfill() - pads a string with leading zero till it reaches spicified length
            month = month_map[m.group(2)]
            year = m.group(3)
            return f"{year}-{month}-{day}"
        

        # PATTERN 2:  DD/MM/YYYY or DD-MM-YYYY - eg: 20/05/2025
        m = re.search(
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})', raw
        )
        if m:
            day = m.group(1).zfill(2)
            month = m.group(2).zfill(2)
            year = m.group(3)
            return f"{year}-{month}-{day}"
        

        # PATTERN 3:  DD.MM.YYYY - eg: 20.05.2025
        m = re.search(
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})', raw
        )
        if m:
            day = m.group(1).zfill(2)
            month = m.group(2).zfill(2)
            year = m.group(3)
            return f"{year}-{month}-{day}"
        

        # PATTERN 4:  Month DD YYYY - eg: May 20, 2025
        m = re.search(
            r'(january|february|march|april|may|june|july|august'
            '|september|october|november|december)\s+(\d{1,2})[,\s]+(\d{4})', raw.lower()
        )
        if m:
            day = m.group(2).zfill(2)
            month = month_map[m.group(1)]
            year = m.group(3)
            return f"{year}-{month}-{day}"
        

        # No date pattern recogonised
        return ""
    


    # Try each anchor phrase against job description
    for pattern in anchor_patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)  #re.IGNORECASE makes it case insensitive so "Apply By" also matches
        if match:
            result = try_parse(match.group(1))
            if result:
                return result
            

    return ""        
            










    

