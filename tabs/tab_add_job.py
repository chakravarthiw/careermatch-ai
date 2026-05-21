# tabs/tab_add_job.py
# ─────────────────────────────────────────────────────────────
# Add Job Tab — CareerMatch AI
#
# What this file does:
#   Renders the Add Job tab which is the main data entry
#   workflow for saving a new job application to the tracker.
#
# Responsibilities:
#   - Accept a pasted job description
#   - Run auto-extraction pipeline on the description
#   - Show colour-coded feedback for sponsorship and closing date
#   - Pre-fill Step 2 form fields with detected values
#   - Allow user to review and correct any field
#   - Save confirmed job to Excel tracker
#   - Record corrections and company names to learner memory
#   - Reset form cleanly after saving
#
# Inputs:
#   tabs — the list of Streamlit tab objects created in app.py
#
# Outputs:
#   Rendered Streamlit UI inside tabs[1]
#   Saved job row in data/applications.xlsx
#   Updated learner memory in data/title_memory.json
#   Updated company memory in data/company_memory.json
#
# Dependencies:
#   src/tracker.py  — add_job()
#   src/utils.py    — sponsorship_label(), extract_closing_date(),
#                     extract_job_title(), extract_location(),
#                     extract_employment_type(), extract_salary(),
#                     extract_company()
#   src/learner.py  — record_correction(), record_company(),
#                     get_known_companies()
#
# Important Streamlit note:
#   Streamlit reruns the entire script on every user interaction.
#   To avoid losing form values during reruns, this tab snapshots
#   all widget values into st.session_state before saving and
#   resetting. See save_and_reset() for details.
# ─────────────────────────────────────────────────────────────

import streamlit as st
from datetime import date

from src.tracker import add_job
from src.utils import (
    sponsorship_label,
    extract_closing_date,
    extract_job_title,
    extract_location,
    extract_employment_type,
    extract_salary,
    extract_company,
)
from src.learner import (
    record_correction,
    record_company,
    get_known_companies,
)


# ── Constants ─────────────────────────────────────────────────
# Employment type options used in the selectbox.
# Defined here so they can be referenced in both the
# session state initialisation and the selectbox widget.
EMPLOYMENT_OPTIONS = [
    "Full-time",
    "Part-time",
    "Casual",
    "Contract",
    "Internship",
]

# Default session state values for all form fields.
# Used to initialise missing keys on first load and
# to reset the form after a successful save.
FORM_DEFAULTS = {
    "_title_input"      : "",
    "_company_input"    : "",
    "_location_input"   : "",
    "_salary_input"     : "",
    "_job_link_input"   : "",
    "_notes_input"      : "",
    "_source_input"     : "SEEK",
    "_employment_input" : "Full-time",
    "_closing_input"    : date.today(),
}


def _initialise_session_state():
    # Sets default values for all form widget keys on first load.
    # Uses setdefault pattern — only fills keys that don't exist yet.
    # This prevents overwriting values the user has already typed.
    for key, value in FORM_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _save_and_reset():
    # ─────────────────────────────────────────────────────────
    # SAVE + RESET CALLBACK
    # ─────────────────────────────────────────────────────────
    # This function is passed as on_click= to the Save Job button.
    # Streamlit calls it BEFORE the page rerenders, which means
    # we can safely read and clear widget values here.
    #
    # Why this pattern is necessary:
    # Once a Streamlit widget is rendered, its value cannot be
    # changed directly in the same script run. The only safe way
    # to reset a widget is through its session_state key, and
    # that must happen before the widget renders — i.e. in a
    # callback.
    #
    # Flow:
    # 1. User clicks Save Job
    # 2. This callback runs first — snapshots all values
    # 3. Clears all visible form widget keys
    # 4. Sets _pending_save = True as a flag for the save block
    # 5. Page rerenders with cleared form
    # 6. Save block detects _pending_save and writes to Excel
    # ─────────────────────────────────────────────────────────

    jd = st.session_state.get("job_description_input", "")

    # Allow save if title is filled even without a description.
    # This handles the case where fields were pre-filled from
    # the Job Search tab and no description was pasted manually.
    if not st.session_state.get("_title_input") and not jd:
        return

    # Snapshot all current form values before clearing.
    # These _snap_* keys are read by the save block below.
    st.session_state["_snap_jd"]         = jd
    st.session_state["_snap_title"]      = st.session_state.get("_title_input", "")
    st.session_state["_snap_company"]    = st.session_state.get("_company_input", "")
    st.session_state["_snap_location"]   = st.session_state.get("_location_input", "")
    st.session_state["_snap_job_link"]   = st.session_state.get("_job_link_input", "")
    st.session_state["_snap_source"]     = st.session_state.get("_source_input", "SEEK")
    st.session_state["_snap_employment"] = st.session_state.get("_employment_input", "Full-time")
    st.session_state["_snap_salary"]     = st.session_state.get("_salary_input", "")
    st.session_state["_snap_closing"]    = st.session_state.get("_closing_input", date.today())
    st.session_state["_snap_notes"]      = st.session_state.get("_notes_input", "")

    # Signal to the save block that a valid save is pending
    st.session_state["_pending_save"] = True

    # Clear all visible form fields so the form resets cleanly.
    # This supports rapid entry of multiple jobs in a row.
    st.session_state["job_description_input"] = ""
    st.session_state["_title_input"]          = ""
    st.session_state["_company_input"]        = ""
    st.session_state["_location_input"]       = ""
    st.session_state["_job_link_input"]       = ""
    st.session_state["_salary_input"]         = ""
    st.session_state["_notes_input"]          = ""
    st.session_state["_source_input"]         = "SEEK"
    st.session_state["_employment_input"]     = "Full-time"
    st.session_state["_closing_input"]        = date.today()


def _run_extraction_pipeline(job_description: str) -> dict:
    # ─────────────────────────────────────────────────────────
    # EXTRACTION PIPELINE
    # ─────────────────────────────────────────────────────────
    # Runs all auto-extraction functions on the pasted job
    # description and returns results as a single dictionary.
    #
    # Centralising the pipeline here means:
    # 1. All detections happen in one place — easy to maintain
    # 2. The render function stays readable
    # 3. Each function can be tested independently
    #
    # Input : raw job description text
    # Output: dict with all detected field values
    # ─────────────────────────────────────────────────────────

    known_companies = get_known_companies()

    return {
        "sponsorship"     : sponsorship_label(job_description),
        "closing_date"    : extract_closing_date(job_description),
        "job_title"       : extract_job_title(job_description),
        "salary"          : extract_salary(job_description),
        "location"        : extract_location(job_description),
        "employment_type" : extract_employment_type(job_description),
        "company"         : extract_company(job_description, known_companies),
    }


def _autofill_empty_fields(detected: dict):
    # ─────────────────────────────────────────────────────────
    # AUTO-FILL LOGIC
    # ─────────────────────────────────────────────────────────
    # Only fills session state fields that are currently empty.
    # This prevents the app from overwriting manual user edits.
    #
    # Example: if the user corrects the company name from
    # "Kinexus" to "Kinexus Group", pasting the same description
    # again will NOT revert their correction.
    #
    # Input : detected — dict from _run_extraction_pipeline()
    # Output: updates session_state keys in place
    # ─────────────────────────────────────────────────────────

    field_map = {
        "_title_input"    : detected["job_title"],
        "_company_input"  : detected["company"],
        "_location_input" : detected["location"],
        "_salary_input"   : detected["salary"],
    }

    for key, value in field_map.items():
        if not st.session_state.get(key):
            st.session_state[key] = value


def _show_detection_feedback(detected: dict):
    # ─────────────────────────────────────────────────────────
    # DETECTION FEEDBACK BANNERS
    # ─────────────────────────────────────────────────────────
    # Shows colour-coded banners immediately after the user
    # pastes a job description so they get instant feedback
    # on what the app detected before scrolling to the form.
    #
    # Green  = good news (date found / likely sponsorship)
    # Red    = hard no (no sponsorship)
    # Yellow = unclear (no date / not mentioned)
    #
    # Input : detected — dict from _run_extraction_pipeline()
    # Output: renders st.success / st.warning / st.error banners
    # ─────────────────────────────────────────────────────────

    col_a, col_b = st.columns(2)

    with col_a:
        if detected["closing_date"]:
            st.success(f"📅 Closing date detected: **{detected['closing_date']}**")
        else:
            st.warning("📅 No closing date found — enter manually below.")

    with col_b:
        if detected["sponsorship"] == "Likely Sponsorship":
            st.success(f"🛂 Sponsorship: **{detected['sponsorship']}**")
        elif detected["sponsorship"] == "No Sponsorship":
            st.error(f"🛂 Sponsorship: **{detected['sponsorship']}**")
        else:
            st.warning(f"🛂 Sponsorship: **{detected['sponsorship']}**")


def render():

    st.header("➕ Add a New Job")

    # Initialise session state defaults on first load
    _initialise_session_state()

    st.header("Add a New Job")

    # ── Success Message ───────────────────────────────────
    # After saving, the app calls st.rerun() which clears
    # all local variables. We use session_state flags to
    # persist the success message across the rerun so it
    # appears after the form has reset — not before.
    if st.session_state.get("just_saved"):
        st.success(
            f"✅ Job saved! Sponsorship: "
            f"**{st.session_state.get('saved_sponsorship', 'Unknown')}**"
        )
        st.balloons()
        # Reset flag so message only shows once
        st.session_state["just_saved"] = False

    # ── Step 1: Job Description ───────────────────────────
    # The description box appears first so auto-detections
    # run before the user scrolls to the form fields below.
    # This means the form is already pre-filled by the time
    # the user reaches Step 2.
    st.subheader("Step 1 — Paste Job Description")
    st.caption(
        "Job title, company, location, salary, employment type, "
        "closing date and sponsorship will be auto-detected."
    )

    job_description = st.text_area(
        "Paste Job Description Here",
        height=400,
        key="job_description_input",
        help="Paste the full job ad here. The more complete the description, the more accurate the auto-detection."
    )

    # Run extraction pipeline and auto-fill only when
    # description text is present
    if job_description:
        detected = _run_extraction_pipeline(job_description)
        _autofill_empty_fields(detected)
        _show_detection_feedback(detected)
    else:
        # Empty detected dict — used as safe default below
        detected = {
            "sponsorship"     : "Unknown",
            "closing_date"    : "",
            "job_title"       : "",
            "salary"          : "",
            "location"        : "",
            "employment_type" : "Full-time",
            "company"         : "",
        }

    st.divider()

    # ── Step 2: Job Details Form ──────────────────────────
    # Fields are pre-filled from auto-detection where possible.
    # The user reviews, corrects if needed, then saves.
    # All corrections are recorded to learner memory on save.
    st.subheader("Step 2 — Confirm or Edit Job Details")
    st.caption(
        "Auto-detected fields are pre-filled. "
        "Check and correct anything before saving."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.text_input("Job Title *", key="_title_input")

        # Hint shown only if description was pasted but
        # title could not be detected — prompts manual entry
        if job_description and not detected["job_title"]:
            st.caption("⚠️ Could not detect title — please enter manually.")

        st.text_input("Company *", key="_company_input")
        st.text_input("Location", key="_location_input")
        st.text_input(
            "Job Link (full URL)",
            key="_job_link_input",
            placeholder="https://www.seek.com.au/job/12345678"
        )
        st.selectbox(
            "Source",
            ["SEEK", "LinkedIn", "Indeed", "Company Website", "Referral", "Other"],
            key="_source_input",
        )

    with col2:

        st.selectbox(
            "Employment Type",
            EMPLOYMENT_OPTIONS,
            key="_employment_input",
        )

        st.text_input(
            "Salary / Rate (optional)",
            key="_salary_input",
        )

        # ── Closing Date ──────────────────────────────────
        # If a closing date was auto-detected, convert the
        # "YYYY-MM-DD" string back to a date object so the
        # calendar picker can use it as the default value.
        # User can always click a different date to override.
        if detected["closing_date"]:
            try:
                from datetime import datetime
                default_date = datetime.strptime(
                    detected["closing_date"], "%Y-%m-%d"
                ).date()
                # Only set if not already manually overridden
                if st.session_state.get("_closing_input") == date.today():
                    st.session_state["_closing_input"] = default_date
            except ValueError:
                pass

        st.date_input("Closing Date", key="_closing_input")

    st.text_area("Notes", key="_notes_input")

    # ── Save Job Button ───────────────────────────────────
    # on_click= runs _save_and_reset() before the page rerenders.
    # The save logic below then reads from the _snap_* keys
    # that the callback wrote, not from the cleared form fields.
    if st.button(
        "💾 Save Job",
        width="stretch",
        on_click=_save_and_reset,
    ):
        if st.session_state.get("_pending_save"):

            # Read all snapshotted values
            snap_jd         = st.session_state.get("_snap_jd", "")
            snap_title      = st.session_state.get("_snap_title", "")
            snap_company    = st.session_state.get("_snap_company", "")
            snap_location   = st.session_state.get("_snap_location", "")
            snap_link       = st.session_state.get("_snap_job_link", "")
            snap_source     = st.session_state.get("_snap_source", "SEEK")
            snap_emp        = st.session_state.get("_snap_employment", "Full-time")
            snap_salary     = st.session_state.get("_snap_salary", "")
            snap_closing    = st.session_state.get("_snap_closing", date.today())
            snap_notes      = st.session_state.get("_snap_notes", "")

            # Validate required fields before writing to Excel
            if not snap_title or not snap_company:
                st.error("Job Title and Company are required.")
                st.session_state["_pending_save"] = False

            else:
                # Run sponsorship detection on the snapshotted
                # description — not the cleared form field
                snap_sponsorship = sponsorship_label(snap_jd)

                # Write new job row to Excel via tracker.py
                add_job(
                    job_title=snap_title,
                    company=snap_company,
                    location=snap_location,
                    job_link=snap_link,
                    source=snap_source,
                    closing_date=str(snap_closing),
                    employment_type=snap_emp,
                    salary=snap_salary,
                    sponsorship=snap_sponsorship,
                    notes=snap_notes,
                )

                # ── Learner Memory Update ─────────────────
                # Record confirmed values for future learning.
                # record_correction() stores whether the app
                # correctly predicted the job title.
                # record_company() stores the confirmed company
                # name for future description matching.
                lines = snap_jd.splitlines() if snap_jd else []

                record_correction(
                    confirmed_title=snap_title,
                    detected_title=detected["job_title"],
                    first_line=lines[0].strip() if lines else "",
                    second_line=lines[1].strip() if len(lines) > 1 else "",
                )

                record_company(
                    confirmed_company=snap_company,
                    detected_company=detected["company"],
                )

                # Store sponsorship result so success message
                # can display it after st.rerun()
                st.session_state["saved_sponsorship"] = snap_sponsorship
                st.session_state["just_saved"]        = True
                st.session_state["_pending_save"]     = False

                # Rerun refreshes the UI with cleared form
                # and shows the success message at the top
                st.rerun()