# src/resume_matcher.py
# ─────────────────────────────────────────────────────────────
# Resume Matcher - CareerMatch AI Phase 3

# What this file does:
#     1. Compares a resume against job description and returns:
#         a. An ATS match score(0-100%)
#         b. List of matched keywords
#         c. List of missing words

# Approach:
#     1. Uses TF-IDF vectorization from scikit-learn to extract
#         a. most important keywords from job description 
#         b. comapres those to keywords on resume 

# TF-IDF (Term Frequency - Inverse Document Frequency) weighs:
#     1. words by how important they are to this specific document comapred to 
#        general english - so words like "the" scores lower than words like "Python"

# INPUT: 
#         1. resume_text      - full resume as a string
#         2. job_description  - full job description as string
#         3. top_n            - how many keywords to extract (default 20)

# OUTPUTS:
#         1. dict with keys:
#             a. score            - float 0.0 to 100.0
#             b. matched          - list of keywords found in resume
#             c. missing          - list of keywords not found in reusme 
#             d. label            - readable score band
# ─────────────────────────────────────────────────────────────


import re 
from sklearn.feature_extraction.text import TfidfVectorizer

# ── Score Band Labels ─────────────────────────────────────────
# Maps score ranges to human readable labels shown in the UI
# These are based on typical ATS screening cutoffs
SCORE_BANDS = [
    (90, "Excellent match - apply immediately"),
    (75, "Strong Match - minor tailoring recommended"),
    (60, "Possible match - resume needs work"),
    (0, "Weak match - Significant keyword gap"),
]