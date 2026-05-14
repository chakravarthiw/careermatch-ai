# app.py
# ─────────────────────────────────────────────────────────────
# CareerMatch AI — Main Streamlit Application
# ─────────────────────────────────────────────────────────────
#
# Purpose:
# This file controls the user interface and main workflow for
# CareerMatch AI.
#
# Responsibilities:
# - Display the Streamlit UI
# - Accept pasted job descriptions
# - Run extraction functions from src/utils.py
# - Save job applications using src/tracker.py
# - Record corrections and company memory using src/learner.py
# - Display tracker and dashboard views
#
# Project architecture:
# app.py      -> UI + workflow orchestration
# tracker.py  -> Excel persistence layer
# utils.py    -> rule-based extraction and text processing
# learner.py  -> correction memory and known company storage
#
# Important Streamlit note:
# Streamlit reruns the whole script after most user interactions.
# To avoid losing form values during reruns, this app snapshots
# widget values into st.session_state before saving and resetting.
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
from datetime import datetime, date

from src.tracker import (
    load_tracker,
    add_job,
    update_status,
    STATUSES,
    save_tracker,
    COLUMNS,
)

from src.utils import (
    days_until,
    urgency_label,
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
    correction_status,
)

# ═════════════════════════════════════════════════════════════
# PAGE SETUP
# ═════════════════════════════════════════════════════════════
# This section configures the browser tab, page layout and main
# navigation tabs. The app currently has three main screens:
# 1. Add Job
# 2. Tracker
# 3. Dashboard
# ═════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="CareerMatch AI",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 CareerMatch AI")

st.caption(
    "Job tracking, ATS Matching and Sponsorship Detection - For Australian Market"
)

tabs = st.tabs([
    "➕ Add Job",
    "📋 Tracker",
    "📊 Dashboard",
])

# ═════════════════════════════════════════════════════════════
# TAB 1 — ADD JOB
# ═════════════════════════════════════════════════════════════
# This tab is the main data-entry workflow.
#
# User flow:
# 1. Paste job description
# 2. App extracts key fields automatically
# 3. User reviews/edits fields
# 4. User saves job
# 5. App records job + learner memory
# 6. Form resets for the next job
# ═════════════════════════════════════════════════════════════

with tabs[0]:

    # ─────────────────────────────────────────────────────────
    # SAVE + RESET CALLBACK
    # ─────────────────────────────────────────────────────────
    # Streamlit widgets are tied to session_state keys.
    #
    # Important:
    # Once a widget is rendered, Streamlit does not allow us to
    # directly change that widget's value later in the same run.
    #
    # To safely reset the form:
    # 1. This callback runs before the page rerenders.
    # 2. It snapshots all current widget values into "_snap_*" keys.
    # 3. It clears visible form widget values.
    # 4. The save block later reads from the snapshots, not the cleared fields.
    #
    # This gives the user a smooth workflow:
    # paste JD -> autofill -> save -> form clears automatically.
    # ─────────────────────────────────────────────────────────

    def save_and_reset():

        jd = st.session_state.get("job_description_input", "")

        # If no job description has been pasted, there is nothing to save.
        if not jd:
            return

        # Snapshot the job description and all Step 2 form values.
        # These snapshot values are temporary and are only used during
        # the save operation after the button click.
        st.session_state["_snap_jd"] = jd
        st.session_state["_snap_title"] = st.session_state.get("_title_input", "")
        st.session_state["_snap_company"] = st.session_state.get("_company_input", "")
        st.session_state["_snap_location"] = st.session_state.get("_location_input", "")
        st.session_state["_snap_job_link"] = st.session_state.get("_job_link_input", "")
        st.session_state["_snap_source"] = st.session_state.get("_source_input", "SEEK")

        st.session_state["_snap_employment"] = st.session_state.get(
            "_employment_input",
            "Full-time",
        )

        st.session_state["_snap_salary"] = st.session_state.get("_salary_input", "")

        st.session_state["_snap_closing"] = st.session_state.get(
            "_closing_input",
            date.today(),
        )

        st.session_state["_snap_notes"] = st.session_state.get("_notes_input", "")

        # This flag tells the save block that a valid save attempt is waiting.
        st.session_state["_pending_save"] = True

        # Clear visible form fields after snapshotting.
        # This supports rapid entry of multiple job descriptions.
        st.session_state["job_description_input"] = ""

        st.session_state["_title_input"] = ""
        st.session_state["_company_input"] = ""
        st.session_state["_location_input"] = ""
        st.session_state["_job_link_input"] = ""
        st.session_state["_salary_input"] = ""
        st.session_state["_notes_input"] = ""

        st.session_state["_source_input"] = "SEEK"
        st.session_state["_employment_input"] = "Full-time"
        st.session_state["_closing_input"] = date.today()

    # ─────────────────────────────────────────────────────────
    # INITIALISE SESSION STATE
    # ─────────────────────────────────────────────────────────
    # Streamlit widgets need default values the first time the app loads.
    # We only initialise missing keys so we do not overwrite anything the
    # user has typed during normal interaction.
    # ─────────────────────────────────────────────────────────

    defaults = {
        "_title_input": "",
        "_company_input": "",
        "_location_input": "",
        "_salary_input": "",
        "_job_link_input": "",
        "_notes_input": "",
        "_source_input": "SEEK",
        "_employment_input": "Full-time",
        "_closing_input": date.today(),
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.header("Add a New Job")

    st.subheader("Step 1 - Paste Job Description")

    st.caption(
        "Sponsorship and Closing Date Auto Generated"
    )

    # ─────────────────────────────────────────────────────────
    # SUCCESS MESSAGE
    # ─────────────────────────────────────────────────────────
    # After saving a job, the app reruns. This flag allows the
    # success message to appear after the rerun instead of disappearing
    # immediately during the save operation.
    # ─────────────────────────────────────────────────────────

    if st.session_state.get("just_saved"):

        st.success(
            f"✅ Job saved! Sponsorship status: "
            f"{st.session_state.get('saved_sponsorship', 'Unknown')}"
        )

        st.balloons()

        # Reset the flag so the message only shows once.
        st.session_state["just_saved"] = False

    # ─────────────────────────────────────────────────────────
    # STEP 1 — JOB DESCRIPTION INPUT
    # ─────────────────────────────────────────────────────────
    # The user pastes a full job advertisement here.
    # The extraction pipeline below reads from this text area.
    # ─────────────────────────────────────────────────────────

    job_description = st.text_area(
        "PASTE JOB DESCRIPTION HERE",
        height=400,
        key="job_description_input",
    )

    # ─────────────────────────────────────────────────────────
    # EXTRACTION PIPELINE
    # ─────────────────────────────────────────────────────────
    # The pasted job description is processed through rule-based
    # extraction functions from src/utils.py.
    #
    # Current extraction approach:
    # - regex patterns
    # - line-based heuristics
    # - sponsorship keyword matching
    # - known company memory lookup
    #
    # These detected values are used to pre-fill the form below.
    # The user can still manually correct anything before saving.
    # ─────────────────────────────────────────────────────────

    detected_sponsorship = sponsorship_label(job_description)

    detected_closing_date = extract_closing_date(
        job_description
    )

    detected_job_title = extract_job_title(
        job_description
    )

    detected_salary = extract_salary(
        job_description
    )

    detected_location = extract_location(
        job_description
    )

    detected_employment = extract_employment_type(
        job_description
    )

    known_companies = get_known_companies()

    detected_company = extract_company(
        job_description,
        known_companies,
    )

    # ─────────────────────────────────────────────────────────
    # AUTO-FILL STEP 2 FIELDS
    # ─────────────────────────────────────────────────────────
    # Only empty fields are auto-filled.
    # This prevents the app from overwriting manual user edits.
    # Example:
    # If the app detects the wrong company and the user corrects it,
    # the correction will not be replaced on the next rerun.
    # ─────────────────────────────────────────────────────────

    if job_description:

        if not st.session_state.get("_title_input"):
            st.session_state["_title_input"] = detected_job_title

        if not st.session_state.get("_company_input"):
            st.session_state["_company_input"] = detected_company

        if not st.session_state.get("_location_input"):
            st.session_state["_location_input"] = detected_location

        if not st.session_state.get("_salary_input"):
            st.session_state["_salary_input"] = detected_salary

    # ─────────────────────────────────────────────────────────
    # EXTRACTION FEEDBACK BANNERS
    # ─────────────────────────────────────────────────────────
    # These banners give the user quick feedback on what the app
    # detected from the pasted job description.
    # ─────────────────────────────────────────────────────────

    if job_description:

        col_a, col_b = st.columns(2)

        with col_a:

            if detected_closing_date:

                st.success(
                    f"📅 Closing date detected: "
                    f"**{detected_closing_date}**"
                )

            else:

                st.warning(
                    "📅 No closing date found — enter manually below."
                )

        with col_b:

            if detected_sponsorship == "Likely Sponsorship":

                st.success(
                    f"🛂 Sponsorship: **{detected_sponsorship}**"
                )

            elif detected_sponsorship == "No Sponsorship":

                st.error(
                    f"🛂 Sponsorship: **{detected_sponsorship}**"
                )

            else:

                st.warning(
                    f"🛂 Sponsorship: **{detected_sponsorship}**"
                )

    st.divider()

    # ─────────────────────────────────────────────────────────
    # STEP 2 — REVIEW AND EDIT EXTRACTED DETAILS
    # ─────────────────────────────────────────────────────────
    # The app auto-fills these fields, but the user remains in control.
    # Corrected values become part of learner memory after saving.
    # ─────────────────────────────────────────────────────────

    st.subheader("Step 2 - Fill Job Details Manually")

    employment_options = [
        "Full-time",
        "Part-time",
        "Casual",
        "Contract",
        "Internship",
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Job Title *",
            key="_title_input",
        )

        st.text_input(
            "Company *",
            key="_company_input",
        )

        st.text_input(
            "Location *",
            key="_location_input",
        )

        st.text_input(
            "Job Link",
            key="_job_link_input",
        )

        st.selectbox(
            "Source",
            [
                "SEEK",
                "LinkedIn",
                "Indeed",
                "Company Website",
                "Referral",
                "Other",
            ],
            key="_source_input",
        )

    with col2:

        st.selectbox(
            "Employment Type",
            employment_options,
            key="_employment_input",
        )

        st.text_input(
            "Salary / Rate (optional)",
            key="_salary_input",
        )

        st.date_input(
            "Closing Date",
            key="_closing_input",
        )

    st.text_area(
        "Notes",
        key="_notes_input",
    )

    # ─────────────────────────────────────────────────────────
    # SAVE JOB
    # ─────────────────────────────────────────────────────────
    # The button uses save_and_reset() as a callback.
    # That callback snapshots the form values before clearing fields.
    #
    # This block then:
    # 1. Reads the snapshot values
    # 2. Validates required fields
    # 3. Saves the job to Excel
    # 4. Records learner memory
    # 5. Triggers a clean rerun
    # ─────────────────────────────────────────────────────────

    if st.button(
        "💾 Save Job",
        use_container_width=True,
        on_click=save_and_reset,
    ):

        if st.session_state.get("_pending_save"):

            snap_jd = st.session_state.get("_snap_jd", "")

            snap_title = st.session_state.get("_snap_title", "")

            snap_company = st.session_state.get(
                "_snap_company",
                "",
            )

            snap_location = st.session_state.get(
                "_snap_location",
                "",
            )

            snap_link = st.session_state.get(
                "_snap_job_link",
                "",
            )

            snap_source = st.session_state.get(
                "_snap_source",
                "SEEK",
            )

            snap_emp = st.session_state.get(
                "_snap_employment",
                "Full-time",
            )

            snap_salary = st.session_state.get(
                "_snap_salary",
                "",
            )

            snap_closing = st.session_state.get(
                "_snap_closing",
                date.today(),
            )

            snap_notes = st.session_state.get(
                "_snap_notes",
                "",
            )

            # Required fields are checked before writing to Excel.
            if not snap_title or not snap_company:

                st.error(
                    "Job Title and Company are required."
                )

                st.session_state["_pending_save"] = False

            else:

                snap_sponsorship = sponsorship_label(
                    snap_jd
                )

                # Save the final reviewed application row.
                # add_job() is defined in tracker.py and handles
                # loading the current tracker, appending the row,
                # and writing the Excel file.
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

                # ─────────────────────────────────────────────
                # LEARNER MEMORY UPDATE
                # ─────────────────────────────────────────────
                # Store confirmed user inputs for future learning.
                #
                # record_correction():
                #   Saves detected title vs confirmed title.
                #
                # record_company():
                #   Saves confirmed company names so future job ads
                #   can match known companies more reliably.
                # ─────────────────────────────────────────────

                lines = snap_jd.splitlines() if snap_jd else []

                record_correction(
                    confirmed_title=snap_title,
                    detected_title=detected_job_title,
                    first_line=lines[0].strip() if lines else "",
                    second_line=lines[1].strip() if len(lines) > 1 else "",
                )

                record_company(
                    confirmed_company=snap_company,
                    detected_company=detected_company,
                )

                # Store save feedback so it appears after st.rerun().
                st.session_state["saved_sponsorship"] = (
                    snap_sponsorship
                )

                st.session_state["just_saved"] = True

                st.session_state["_pending_save"] = False

                # Rerun refreshes the UI after saving and resetting.
                st.rerun()

# ═════════════════════════════════════════════════════════════
# TAB 2 — TRACKER
# ═════════════════════════════════════════════════════════════
# Tracker tab responsibilities:
# - Load saved jobs from Excel
# - Display all applications
# - Filter by status and sponsorship
# - Search by job title/company
# - Update application status
# - Export filtered results as CSV
# - Delete all saved jobs when explicitly confirmed
# ═════════════════════════════════════════════════════════════

with tabs[1]:

    st.header("Application Tracker")

    df = load_tracker()

    if df.empty:

        st.info(
            "No jobs saved yet. Add your first one in the ➕ tab!"
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            status_filter = st.multiselect(
                "Filter by Status",
                options=STATUSES,
                default=STATUSES,
            )

        with col2:

            sponsorship_filter = st.multiselect(
                "Filter By Sponsorship",
                options=[
                    "No Sponsorship",
                    "Not Mentioned",
                    "Unknown",
                    "Likely Sponsorship",
                ],
                default=[
                    "No Sponsorship",
                    "Not Mentioned",
                    "Unknown",
                    "Likely Sponsorship",
                ],
            )

        with col3:

            search_text = st.text_input(
                "🔍 Search Job / Company"
            )

        # Apply filters to the tracker dataframe.
        filtered = df[
            df["Status"].isin(status_filter)
            & df["Sponsorship"].isin(sponsorship_filter)
        ]

        # Optional text search across job title and company.
        if search_text:

            search_lower = search_text.lower()

            filtered = filtered[
                filtered["Job Title"]
                .astype(str)
                .str.lower()
                .str.contains(search_lower)

                |

                filtered["Company"]
                .astype(str)
                .str.lower()
                .str.contains(search_lower)
            ]

        st.caption(
            f"Showing **{len(filtered)}** of **{len(df)}** jobs"
        )

        st.dataframe(
            filtered,
            use_container_width=True,
            height=400,
        )

        # ─────────────────────────────────────────────────────
        # UPDATE APPLICATION STATUS
        # ─────────────────────────────────────────────────────
        # Lets the user move an application through the pipeline
        # e.g. Saved -> Tailoring -> Applied -> Interview.
        # ─────────────────────────────────────────────────────

        st.subheader("Update Job Status")

        if not filtered.empty:

            row_index = st.number_input(
                "Row Number to Update (0 = first row)",
                min_value=0,
                max_value=len(df) - 1,
                step=1,
            )

            new_status = st.selectbox(
                "New Status",
                STATUSES,
            )

            if st.button("Update Status"):

                update_status(
                    int(row_index),
                    new_status,
                )

                st.success("Status Updated")

                st.rerun()

        st.divider()

        # Export current filtered table for external use.
        st.download_button(
            label="⬇️ Download as CSV",
            data=filtered.to_csv(index=False),
            file_name="careermatch_tracker.csv",
            mime="text/csv",
        )

    # ─────────────────────────────────────────────────────────
    # DANGER ZONE
    # ─────────────────────────────────────────────────────────
    # This destructive action is intentionally hidden inside an
    # expander and requires exact text confirmation.
    # ─────────────────────────────────────────────────────────

    st.divider()

    st.subheader("⚠️ Danger Zone")

    with st.expander("DELETE ALL SAVED JOBS"):

        st.warning(
            "This will permanently delete all saved jobs "
            "from the tracker. CANNOT BE UNDONE!"
        )

        confirm_text = st.text_input(
            "Type DELETE to confirm",
            key="delete_confirm",
        )

        if st.button(
            "🗑️ Delete All Jobs",
            type="primary",
        ):

            if confirm_text == "DELETE":

                save_tracker(
                    pd.DataFrame(columns=COLUMNS)
                )

                st.success(
                    "✅ All jobs deleted."
                )

                st.rerun()

            else:

                st.error(
                    "Type DELETE exactly to confirm."
                )

# ═════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD
# ═════════════════════════════════════════════════════════════
# Dashboard tab responsibilities:
# - Show application counts
# - Show pipeline status breakdown
# - Show sponsorship breakdown
# - Highlight roles closing soon
# ═════════════════════════════════════════════════════════════

with tabs[2]:

    st.header("Dashboard")

    df = load_tracker()

    if df.empty:

        st.info(
            "Add jobs to view dashboard."
        )

    else:

        # High-level application metrics.
        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Jobs",
            len(df),
        )

        col2.metric(
            "Applied",
            len(df[df["Status"] == "Applied"]),
        )

        col3.metric(
            "Interviews",
            len(df[df["Status"] == "Interview"]),
        )

        col4.metric(
            "Sponsorship Friendly",
            len(df[
                df["Sponsorship"] == "Likely Sponsorship"
            ]),
        )

        st.divider()

        # Simple visual summaries of application pipeline and sponsorship.
        col1, col2 = st.columns(2)

        with col1:

            st.subheader("By Status")

            st.bar_chart(
                df["Status"].value_counts()
            )

        with col2:

            st.subheader("By Sponsorship")

            st.bar_chart(
                df["Sponsorship"].value_counts()
            )

        st.divider()

        # Closing Soon table helps prioritise applications.
        st.subheader("⏰ Closing Soon")

        df["_days_left"] = df["Closing Date"].apply(
            lambda x: days_until(str(x))
        )

        df["_urgency"] = df["_days_left"].apply(
            urgency_label
        )

        urgent = df[
            df["_days_left"].notna()
            & (df["_days_left"] >= 0)
            & (df["_days_left"] <= 5)
        ][[
            "Job Title",
            "Company",
            "Closing Date",
            "_urgency",
            "Status",
        ]]

        if urgent.empty:

            st.success(
                "No jobs closing within 5 days."
            )

        else:

            st.dataframe(
                urgent,
                use_container_width=True,
            )