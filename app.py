# app.py
# ─────────────────────────────────────────────────────────────
# CareerMatch AI — Main Application Entry Point
# FULL VERSION WITH:
# ✅ Auto Detection
# ✅ Excel Save
# ✅ Full Form Reset
# ✅ Tracker
# ✅ Dashboard
# ✅ Delete All Jobs
# ✅ Learning Memory
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
    COLUMNS
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

# ── PAGE CONFIG ──────────────────────────────────────────────

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

with tabs[0]:

    # ── SAVE + RESET FUNCTION ────────────────────────────────

    def save_and_reset():

        jd = st.session_state.get("job_description_input", "")

        if not jd:
            return

        # ── SNAPSHOT VALUES ──────────────────────────────────

        st.session_state["_snap_jd"] = jd
        st.session_state["_snap_title"] = st.session_state.get("_title_input", "")
        st.session_state["_snap_company"] = st.session_state.get("_company_input", "")
        st.session_state["_snap_location"] = st.session_state.get("_location_input", "")
        st.session_state["_snap_job_link"] = st.session_state.get("_job_link_input", "")
        st.session_state["_snap_source"] = st.session_state.get("_source_input", "SEEK")

        st.session_state["_snap_employment"] = st.session_state.get(
            "_employment_input",
            "Full-time"
        )

        st.session_state["_snap_salary"] = st.session_state.get("_salary_input", "")

        st.session_state["_snap_closing"] = st.session_state.get(
            "_closing_input",
            date.today()
        )

        st.session_state["_snap_notes"] = st.session_state.get("_notes_input", "")

        st.session_state["_pending_save"] = True

        # ── CLEAR FORM ───────────────────────────────────────

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

    # ── INITIALISE SESSION STATE ─────────────────────────────

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

    # ── SUCCESS MESSAGE ──────────────────────────────────────

    if st.session_state.get("just_saved"):

        st.success(
            f"✅ Job saved! Sponsorship status: "
            f"{st.session_state.get('saved_sponsorship', 'Unknown')}"
        )

        st.balloons()

        st.session_state["just_saved"] = False

    # ── JOB DESCRIPTION ──────────────────────────────────────

    job_description = st.text_area(
        "PASTE JOB DESCRIPTION HERE",
        height=400,
        key="job_description_input",
    )

    # ── DETECTIONS ───────────────────────────────────────────

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
        known_companies
    )

    # ── AUTO FILL EMPTY FIELDS ──────────────────────────────

    if job_description:

        if not st.session_state.get("_title_input"):
            st.session_state["_title_input"] = detected_job_title

        if not st.session_state.get("_company_input"):
            st.session_state["_company_input"] = detected_company

        if not st.session_state.get("_location_input"):
            st.session_state["_location_input"] = detected_location

        if not st.session_state.get("_salary_input"):
            st.session_state["_salary_input"] = detected_salary

    # ── FEEDBACK BANNERS ────────────────────────────────────

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

    st.subheader("Step 2 - Fill Job Details Manually")

    employment_options = [
        "Full-time",
        "Part-time",
        "Casual",
        "Contract",
        "Internship"
    ]

    col1, col2 = st.columns(2)

    with col1:

        st.text_input(
            "Job Title *",
            key="_title_input"
        )

        st.text_input(
            "Company *",
            key="_company_input"
        )

        st.text_input(
            "Location *",
            key="_location_input"
        )

        st.text_input(
            "Job Link",
            key="_job_link_input"
        )

        st.selectbox(
            "Source",
            [
                "SEEK",
                "LinkedIn",
                "Indeed",
                "Company Website",
                "Referral",
                "Other"
            ],
            key="_source_input"
        )

    with col2:

        st.selectbox(
            "Employment Type",
            employment_options,
            key="_employment_input"
        )

        st.text_input(
            "Salary / Rate (optional)",
            key="_salary_input"
        )

        st.date_input(
            "Closing Date",
            key="_closing_input"
        )

    st.text_area(
        "Notes",
        key="_notes_input"
    )

    # ── SAVE BUTTON ──────────────────────────────────────────

    if st.button(
        "💾 Save Job",
        use_container_width=True,
        on_click=save_and_reset
    ):

        if st.session_state.get("_pending_save"):

            snap_jd = st.session_state.get("_snap_jd", "")

            snap_title = st.session_state.get("_snap_title", "")

            snap_company = st.session_state.get(
                "_snap_company",
                ""
            )

            snap_location = st.session_state.get(
                "_snap_location",
                ""
            )

            snap_link = st.session_state.get(
                "_snap_job_link",
                ""
            )

            snap_source = st.session_state.get(
                "_snap_source",
                "SEEK"
            )

            snap_emp = st.session_state.get(
                "_snap_employment",
                "Full-time"
            )

            snap_salary = st.session_state.get(
                "_snap_salary",
                ""
            )

            snap_closing = st.session_state.get(
                "_snap_closing",
                date.today()
            )

            snap_notes = st.session_state.get(
                "_snap_notes",
                ""
            )

            # ── VALIDATION ───────────────────────────────────

            if not snap_title or not snap_company:

                st.error(
                    "Job Title and Company are required."
                )

                st.session_state["_pending_save"] = False

            else:

                snap_sponsorship = sponsorship_label(
                    snap_jd
                )

                # ── SAVE JOB ─────────────────────────────────

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

                # ── LEARNING MEMORY ─────────────────────────

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

                st.session_state["saved_sponsorship"] = (
                    snap_sponsorship
                )

                st.session_state["just_saved"] = True

                st.session_state["_pending_save"] = False

                st.rerun()

# ═════════════════════════════════════════════════════════════
# TAB 2 — TRACKER
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
                    "Likely Sponsorship"
                ],
                default=[
                    "No Sponsorship",
                    "Not Mentioned",
                    "Unknown",
                    "Likely Sponsorship"
                ],
            )

        with col3:

            search_text = st.text_input(
                "🔍 Search Job / Company"
            )

        filtered = df[
            df["Status"].isin(status_filter)
            & df["Sponsorship"].isin(sponsorship_filter)
        ]

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
            height=400
        )

        # ── UPDATE STATUS ────────────────────────────────────

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
                STATUSES
            )

            if st.button("Update Status"):

                update_status(
                    int(row_index),
                    new_status
                )

                st.success("Status Updated")

                st.rerun()

        st.divider()

        # ── DOWNLOAD CSV ─────────────────────────────────────

        st.download_button(
            label="⬇️ Download as CSV",
            data=filtered.to_csv(index=False),
            file_name="careermatch_tracker.csv",
            mime="text/csv",
        )

    # ── DANGER ZONE ──────────────────────────────────────────

    st.divider()

    st.subheader("⚠️ Danger Zone")

    with st.expander("DELETE ALL SAVED JOBS"):

        st.warning(
            "This will permanently delete all saved jobs "
            "from the tracker. CANNOT BE UNDONE!"
        )

        confirm_text = st.text_input(
            "Type DELETE to confirm",
            key="delete_confirm"
        )

        if st.button(
            "🗑️ Delete All Jobs",
            type="primary"
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

with tabs[2]:

    st.header("Dashboard")

    df = load_tracker()

    if df.empty:

        st.info(
            "Add jobs to view dashboard."
        )

    else:

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Jobs",
            len(df)
        )

        col2.metric(
            "Applied",
            len(df[df["Status"] == "Applied"])
        )

        col3.metric(
            "Interviews",
            len(df[df["Status"] == "Interview"])
        )

        col4.metric(
            "Sponsorship Friendly",
            len(df[
                df["Sponsorship"] == "Likely Sponsorship"
            ])
        )

        st.divider()

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
            "Status"
        ]]

        if urgent.empty:

            st.success(
                "No jobs closing within 5 days."
            )

        else:

            st.dataframe(
                urgent,
                use_container_width=True
            )