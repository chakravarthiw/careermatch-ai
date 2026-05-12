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
    r"end\s+date\s*[:\-]?\s*(.+)",
    r"applications?\s+close\s+the\s+(.+)"
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
        raw = raw[:60]
        raw = re.sub(r'\(.*?\)', '', raw).strip()


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
            day = m.group(1).zfill(2)      # group 1 = day number e.g. "12"
            month = month_map[m.group(2)]  # group 2 = month name e.g. "may"
            year = m.group(3) if m.group(3) else str(datetime.today().year)
            return f"{year}-{month}-{day}"
        

        # PATTERN 5:  Optional day name) DDth Month (Optional YYYY) - eg: "Tuesday 12th May", "12th May 2026", "Tuesday, 19th May"
        m = re.search(
            r'(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)?'
            r',?\s*(\d{1,2})(?:st|nd|rd|th)\s+'
            r'(january|february|march|april|may|june|july|august'
            r'|september|october|november|december)'
            r'(?:\s+(\d{4}))?', raw.lower()
        )
        if m:
            day = m.group(2).zfill(2)
            month = month_map[m.group(2)]
            # If year is missing - assume current year
            year = m.group(3) if m.group(3) else str(datetime.today().year)
            return f"{year}-{month}-{day}"
        

        # PATTERN 6:  DDth of Month (Optional YYYY)
        # Handles: "24th of May", "24th of May 2026", "the 24th of May"
        m = re.search(
            r'(\d{1,2})(?:st|nd|rd|th)\s+of\s+'
            r'(january|february|march|april|may|june|july|august'
            r'|september|october|november|december)'
            r'(?:\s+(\d{4}))?',
            raw.lower()
        )
        if m:
            day   = m.group(1).zfill(2)
            month = month_map[m.group(2)]
            year  = m.group(3) if m.group(3) else str(datetime.today().year)
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


def extract_employment_type(job_description: str) -> str:

    # Scans for employment type keywords
    # Checks most specific phrases first to avoid false matches
    # Defaults to Full Time if nothing found - most common
    # Input: raw job description type
    # Output: Employment type string matching selectbox options / "" returned if not able to find the contract type



    if not job_description:
        return "Full Time"
    
    # Convert Job Description to lewer case for NLP mechanisms
    text = job_description.lower()


    # Order matters - check specific phrases before generic ones
    # "fixed term" must come before "full time" to avoid errors and wrong match
    if any(p in text for p in ["full-time", "full time"]):
        return "Full Time"
    if any(p in text for p in ["fixed-term", "fixed term"]):
        return "Contract"
    if any(p in text for p in ["part-time", "part time"]):
        return "Part Time"
    if any(p in text for p in ["internship", "intern ", "graduate program"]):
        return "Internship"
    if "casual" in text:
        return "Casual"
    if any(p in text for p in [
        "contract role",
        "contract position",
        "contract employment",
        "fixed-term",
        "fixed term",
        "12 month contract",
        "6 month contract"    
    ]):
        return "Contract"
    
    
    # Default value if not any of the above
    return ""


def extract_salary(job_description: str) -> str:

    # Scans for salary or rate information using regex
    # Handles ranges, hourly rates, annual salary and k notifications
    # Patters are tired in a specific order
    # Input: Raw Job Description String
    # Output: Salary string as found in text, or "" if not found

    # Basic Test for salary check
    if not job_description:
        return ""
    
    patterns = [
        # Annual range: $60,000 - $69,000 / $60,000 to $69,000
        r"\$\s?\d{1,3}(?:,\d{3})+(?:\.\d{2})?\s*(?:-|to|-)\s*\$?\s?\d{1,3}(?:,\d{3})+(?:\.\d{2})?\s*(?:per year|pa|p\.a\.|annualy|year)?",
        # Hourly range:  $38.50 - $45.00 per hour
        r"\$\s?\d{1,3}(?:\.\d{2})?\s*(?:-|to|-)\s*\$?\s?\d{1,3}(?:\.\d{2})?\s*(?:per hour|/hr|hr|hour)",
        # k-notation range: $60k - $80k
        r"\$\s?\d{1,3}k\s*(?:-|to)\s*\$?\s?\d{2,3}k",
        # Single annual with comma: $75,000 per year
        r"\$\s?\d{1,3}(?:,\d{3})+(?:\.\d{2})\s*(?:per year| pa| p\.a\.|annually)?",
        # Single hourly: $45.50 per hour
        r"\$\s?\d{1,3}(?:\.\d{2})?\s*(?:per hour| /hr | /hour|ph|p/h)",
        # Single k notations: $75k
        r"\$\s?\d{2,3}k",
        # Award/above award: award rate, above award
        r"(?:above\s+)?award\s+rate",
    ]

    for pattern in patterns:
        m = re.search(pattern, job_description, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return ""



def extract_location(job_description: str) -> str:

    # Scans for location using anchor phrases, then falls back to city name list
    # Anchor phrases checked first - more reliable than city scanning alone
    # Input: raw job job_description
    # Output: Location String/ "" if not found

    if not job_description:
        return ""
    
    # Anchor phrase approach - look for location after known labels
    anchor_patterns = [
        r"location\s*[:\-]\s*(.+)",
        r"work\s+location\s*[:\-]\s*(.+)",
        r"based\s+in\s+(.+)",
        r"office\s+location\s*[:\-]\s*(.+)"
    ]


    for pattern in anchor_patterns:
        m = re.search(pattern, job_description, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # Take first line only - avoid pulling full sentences
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            candidate = lines[0][:60] if lines else ""
            if candidate:
                return candidate.strip(".,:-")
            

    australian_cities = [
        "Melbourne", "Sydney", "Brisbane", "Perth", "Adelaide",
        "Canberra", "Hobart", "Darwin", "Gold Coast", "Newcastle",
        "Geelong", "Wollongong", "Townsville", "Cairns", "Bendigo"
    ]

    for city in australian_cities:
        if re.search(rf'\b{city}\b', job_description, re.IGNORECASE):
            return city
    return ""


def extract_job_title(job_description: str) -> str:

    # Extracts likely job title from non meta data lines of job job_description
    # Observation from Seek/Linkdin ads: title seems to be mostly in line 1
    # Uses positive validation - checks if line looks like a "Title" rather than trying to rule out bad lines with skip test
    # Input: Job description
    # Output: Job title string / "" if not confident

    if not job_description:
        return ""


    # ── Helpers ───────────────────────────────────────────────    
    # Words that only appear in metadata lines, never in real title
    # Kept intentionally small - positive validation does the heavy lifting
    METADATA_WORDS = {
        "apply", "posted", "full time", "part time", "casual", "contract",
        "worldwide", "locations", "time type", "requisition", "days ago",
        "days left", "remote", "hybrid", "salary", "closing", "deadline"        
    }

    
    # Role type words that commonly appear in job titles
    # If line contains these words - huge probability its a title
    TITLE_SIGNALS = [
        "manager", "coordinator", "officer", "analyst", "engineer",
        "director", "supervisor", "assistant", "associate", "specialist",
        "consultant", "advisor", "lead", "planner", "operator", "executive",
        "administrator", "developer", "designer", "technician", "support"
    ]

    def looks_like_title(line: str) -> bool:
        # Returns True if line might be a job title
        # checks length, metadata words and tital signal words


        # too short or too long to be title
        if len(line) < 4 or len(line) > 80:
            return False
        

        line_lower = line.lower()

        # Contains a known metadata word - not a title
        if any (word in line_lower for word in METADATA_WORDS):
            return False
        

        # All CAPS - usually a section header like "About the role"
        if line.isupper() and len(line.split()) > 1:
            return False
        

        # If line contains a title word- strong positive signal
        if any(signal in line_lower for signal in TITLE_SIGNALS):
            return True
        

        # Short title cased or mixed case line with no meta data- likely a title 
        # Eg: "General Operator", "Data Scientist"
        words = line.split()
        if 1 <= len(words) <= 8:
            return True
        return False
    

    # ── Tier 1: Anchor Phrase ───────────────────────────────────────────────    
    # Some job boards include an explicit label - reliable signal
    anchor_patterns = [
        r"(?:job title|position title|role title|position)\s*[:\-]\s*(.+)",
    ]
    for pattern in anchor_patterns:
        m = re.search(pattern, job_description, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip().splitlines()[0].strip(".,:-")
            if candidate:
                return candidate
            
    
    # ── Tier 2: First Two Non Empty Lines ───────────────────────────────────────────────    
    # Real World pattern confirmed across Seek and Linkdin - Title is always almost Line 1 or line 2
    lines = [line.strip() for line in job_description.splitlines() if line.strip()]

    for line in lines[:2]:
        if looks_like_title(line):
            # Strip or show name suffix - handles "Guest Experience Supervisor – KURIOS
            # re.split on em-dash, en-dash or pipe - keeps only the title part
            line = re.split(r'\s*[–—|]\s*', line)[0] # [0] goes AFTER the split, on the result list
            return line.strip(".,:-")                # now stripping a string not a list
        

    # ── Tier 3: give up ─────────────────────────────────────────────── 
    # Blank is better than wrong guess - user to fill in manually
    # the manual entry becomes correction -> training data for learner.property   
    return ""



