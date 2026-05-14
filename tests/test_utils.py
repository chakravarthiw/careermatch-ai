# tests/test_utils.py
# ─────────────────────────────────────────────────────────────
# Tests for src/utils.py
#
# These tests check the rule-based extraction functions used by
# CareerMatch AI:
# - sponsorship detection
# - closing date extraction
# - employment type extraction
# - salary extraction
# - location extraction
# - job title extraction
# - company extraction
# ─────────────────────────────────────────────────────────────

from src.utils import (
    sponsorship_label,
    extract_closing_date,
    extract_employment_type,
    extract_salary,
    extract_location,
    extract_job_title,
    extract_company,
)

import src.learner as learner

# ═════════════════════════════════════════════════════════════
# SPONSORSHIP TESTS
# ═════════════════════════════════════════════════════════════

def test_sponsorship_no_sponsorship():
    text = "Applicants must have full working rights in Australia."
    assert sponsorship_label(text) == "No Sponsorship"


def test_sponsorship_likely_sponsorship():
    text = "Visa sponsorship available for the right candidate."
    assert sponsorship_label(text) == "Likely Sponsorship"


def test_sponsorship_not_mentioned():
    text = "We are looking for a data analyst with strong Python skills."
    assert sponsorship_label(text) == "Not Mentioned"


def test_sponsorship_empty_text():
    assert sponsorship_label("") == "Unknown"


# ═════════════════════════════════════════════════════════════
# CLOSING DATE TESTS
# ═════════════════════════════════════════════════════════════

def test_extract_closing_date_dd_month_year():
    text = "Applications close on 20 May 2026"
    assert extract_closing_date(text) == "2026-05-20"


def test_extract_closing_date_slash_format():
    text = "Closing date: 20/05/2026"
    assert extract_closing_date(text) == "2026-05-20"


def test_extract_closing_date_month_day_year():
    text = "Deadline: May 20, 2026"
    assert extract_closing_date(text) == "2026-05-20"


def test_extract_closing_date_ordinal():
    text = "Applications close Tuesday 12th May 2026"
    assert extract_closing_date(text) == "2026-05-12"


def test_extract_closing_date_not_found():
    text = "This role is open until the position is filled."
    assert extract_closing_date(text) == ""


# ═════════════════════════════════════════════════════════════
# EMPLOYMENT TYPE TESTS
# ═════════════════════════════════════════════════════════════

def test_extract_employment_type_full_time():
    text = "This is a full-time position based in Melbourne."
    assert extract_employment_type(text) in ["Full-time", "Full Time"]


def test_extract_employment_type_part_time():
    text = "We are hiring for a part-time customer service role."
    assert extract_employment_type(text) in ["Part-time", "Part Time"]


def test_extract_employment_type_casual():
    text = "This is a casual event operations role."
    assert extract_employment_type(text) == "Casual"


def test_extract_employment_type_contract():
    text = "This is a 12 month contract role."
    assert extract_employment_type(text) == "Contract"


def test_extract_employment_type_internship():
    text = "Graduate program and internship opportunities available."
    assert extract_employment_type(text) == "Internship"


# ═════════════════════════════════════════════════════════════
# SALARY TESTS
# ═════════════════════════════════════════════════════════════

def test_extract_salary_annual_range():
    text = "Salary range is $70,000 - $85,000 per year."
    assert extract_salary(text) != ""


def test_extract_salary_hourly_rate():
    text = "Pay rate: $38.50 per hour."
    assert "$38.50" in extract_salary(text)


def test_extract_salary_k_range():
    text = "Package: $80k - $100k."
    assert extract_salary(text) != ""


def test_extract_salary_not_found():
    text = "Competitive salary package available."
    assert extract_salary(text) == ""


# ═════════════════════════════════════════════════════════════
# LOCATION TESTS
# ═════════════════════════════════════════════════════════════

def test_extract_location_from_label():
    text = "Location: Melbourne, VIC"
    assert extract_location(text) == "Melbourne, VIC"


def test_extract_location_city_fallback():
    text = "This role is based in Brisbane with hybrid work options."
    assert extract_location(text) in ["Brisbane", "Brisbane with hybrid work options"]


def test_extract_location_not_found():
    text = "This role offers flexible working arrangements."
    assert extract_location(text) == ""


# ═════════════════════════════════════════════════════════════
# JOB TITLE TESTS
# ═════════════════════════════════════════════════════════════

def test_extract_job_title_first_line():
    text = """
General Operator
Casual
Melbourne, VIC
"""
    assert extract_job_title(text) == "General Operator"


def test_extract_job_title_anchor():
    text = "Job Title: Data Analyst\nCompany: Example Co"
    assert extract_job_title(text) == "Data Analyst"


def test_extract_job_title_not_found():
    text = """
Apply now
Posted 2 days ago
Full time
"""
    assert extract_job_title(text) == ""


# ═════════════════════════════════════════════════════════════
# COMPANY TESTS
# ═════════════════════════════════════════════════════════════

def test_extract_company_from_known_companies():
    text = "Join Tennis Australia and help deliver world-class events."
    known_companies = ["Tennis Australia", "RMIT University"]
    assert extract_company(text, known_companies) == "Tennis Australia"


def test_extract_company_from_label():
    text = "Company: Monash University\nRole: Event Assistant"
    known_companies = []
    assert extract_company(text, known_companies) == "Monash University"


def test_extract_company_not_found():
    text = "We are looking for an enthusiastic operations assistant."
    known_companies = []
    assert extract_company(text, known_companies) == ""

def test_extract_employment_type_returns_dropdown_label_full_time():
    assert extract_employment_type("This is a full-time role.") == "Full-time"

def test_extract_employment_type_returns_dropdown_label_part_time():
    assert extract_employment_type("This is a part-time role.") == "Part-time"

