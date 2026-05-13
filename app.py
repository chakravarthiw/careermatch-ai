# app.py
# ─────────────────────────────────────────────────────────────
# CareerMatch AI — Main Application Entry Point
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd
from datetime import datetime, date

from src.tracker import load_tracker, add_job, update_status, STATUSES
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

# ── Page Configuration ────────────────────────────────────────
st.set_page_config(
    page_title="CareerMatch AI",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 CareerMatch AI")
st.caption("Job tracking, ATS Matching and Sponsorship Detection - For Australian Market")

tabs = st.tabs([
    "➕ Add Job",
    "📋 Tracker",
    "📊 Dashboard",
])

# ═════════════════════════════════════════════════════════════
# TAB 1 — ADD JOB
# ═════════════════════════════════════════════════════════════

with tabs[0]:
    st.header("Add a New Job")

    st.subheader("Step 1 - Paste Job Description")
    st.caption("Sponsorship and Closing Date Auto Generated")

    job_description = st.text_area(
        "PASTE JOB DESCRIPTION HERE",
        height=400,
    )

    known_companies = get_known_companies()

    # Run detection as soon as text is pasted
    detected_sponsorship = sponsorship_label(job_description)
    detected_closing_date = extract_closing_date(job_description)
    detected_job_title = extract_job_title(job_description)
    detected_salary = extract_salary(job_description)
    detected_location = extract_location(job_description)
    detected_employment = extract_employment_type(job_description)
    detected_company = extract_company(job_description, known_companies)

    if job_description:
        col_a, col_b = st.columns(2)

        with col_a:
            if detected_closing_date:
                st.success(f"📅 Closing date detected: **{detected_closing_date}**")
            else:
                st.warning("📅 No closing date found — enter manually below.")

        with col_b:
            if detected_sponsorship == "Likely Sponsorship":
                st.success(f"🛂 Sponsorship: **{detected_sponsorship}**")
            elif detected_sponsorship == "No Sponsorship":
                st.error(f"🛂 Sponsorship: **{detected_sponsorship}**")
            else:
                st.warning(f"🛂 Sponsorship: **{detected_sponsorship}**")

    st.divider()
    st.subheader("Step 2 - Fill Job Details Manually")

    col1, col2 = st.columns(2)

    with col1:
        job_title = st.text_input("Job Title *", value=detected_job_title)
        company = st.text_input("Company *", value=detected_company)
        location = st.text_input("Location *", value=detected_location)
        job_link = st.text_input("Job Link")

        source = st.selectbox(
            "Source",
            ["SEEK", "LinkedIn", "Indeed", "Company Website", "Referral", "Other"],
        )

    with col2:
        employment_options = ["Full-time", "Part-time", "Casual", "Contract", "Internship"]

        default_emp_index = (
            employment_options.index(detected_employment)
            if detected_employment in employment_options
            else 0
        )

        employment_type = st.selectbox(
            "Employment Type:",
            employment_options,
            index=default_emp_index,
        )

        salary = st.text_input("Salary / Rate (optional)", value=detected_salary)

        if detected_closing_date:
            try:
                default_date = datetime.strptime(detected_closing_date, "%Y-%m-%d").date()
            except ValueError:
                default_date = date.today()
        else:
            default_date = date.today()

        closing_date = st.date_input("Closing Date", value=default_date)

    notes = st.text_area("Notes")

    if st.button("💾 Save Job", use_container_width=True):
        if not job_title or not company:
            st.error("Job Title and Company Required")
        else:
            detected_sponsorship = sponsorship_label(job_description)

            add_job(
                job_title=job_title,
                company=company,
                location=location,
                job_link=job_link,
                source=source,
                closing_date=str(closing_date),
                employment_type=employment_type,
                salary=salary,
                sponsorship=detected_sponsorship,
                notes=notes,
            )

            lines = job_description.splitlines() if job_description else []

            record_correction(
                confirmed_title=job_title,
                detected_title=detected_job_title,
                first_line=lines[0].strip() if len(lines) > 0 else "",
                second_line=lines[1].strip() if len(lines) > 1 else "",
            )

            record_company(
                confirmed_company=company,
                detected_company=detected_company,
            )

            st.success(f"✅ Job saved! Sponsorship detected: **{detected_sponsorship}**")
            st.balloons()

# ═════════════════════════════════════════════════════════════
# TAB 2 — TRACKER
# ═════════════════════════════════════════════════════════════

with tabs[1]:
    st.header("Application Tracker")

    df = load_tracker()

    if df.empty:
        st.info("No jobs saved yet. Add your first one in the ➕ tab!")
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
                options=["No Sponsorship", "Not Mentioned", "Unknown", "Likely Sponsorship"],
                default=["No Sponsorship", "Not Mentioned", "Unknown", "Likely Sponsorship"],
            )

        with col3:
            search_text = st.text_input("🔍 Search Job / Company")

        filtered = df[
            df["Status"].isin(status_filter)
            & df["Sponsorship"].isin(sponsorship_filter)
        ]

        if search_text:
            search_lower = search_text.lower()
            filtered = filtered[
                filtered["Job Title"].astype(str).str.lower().str.contains(search_lower)
                | filtered["Company"].astype(str).str.lower().str.contains(search_lower)
            ]

        st.caption(f"Showing **{len(filtered)}** of **{len(df)}** jobs")
        st.dataframe(filtered, use_container_width=True, height=400)

        st.subheader("Update Job Status")

        if not filtered.empty:
            row_index = st.number_input(
                "Row Number to Update (0 = first row)",
                min_value=0,
                max_value=len(df) - 1,
                step=1,
            )

            new_status = st.selectbox("New Status", STATUSES)

            if st.button("Update Status"):
                update_status(int(row_index), new_status)
                st.success("Status Updated")
                st.rerun()

        st.divider()

        st.download_button(
            label="⬇️ Download as CSV",
            data=filtered.to_csv(index=False),
            file_name="careermatch_tracker.csv",
            mime="text/csv",
        )

# ═════════════════════════════════════════════════════════════
# TAB 3 — DASHBOARD
# ═════════════════════════════════════════════════════════════

with tabs[2]:
    st.header("Dashboard")

    df = load_tracker()

    if df.empty:
        st.info("Add jobs to view dashboard")
    else:
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Jobs:", len(df))
        col2.metric("Applied Jobs:", len(df[df["Status"] == "Applied"]))
        col3.metric("Interviews:", len(df[df["Status"] == "Interview"]))
        col4.metric(
            "Sponsorship Friendly:",
            len(df[df["Sponsorship"] == "Likely Sponsorship"]),
        )

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("By Status")
            st.bar_chart(df["Status"].value_counts())

        with col2:
            st.subheader("By Sponsorship")
            st.bar_chart(df["Sponsorship"].value_counts())

        st.divider()

        st.subheader("⏰ Closing Soon")

        df["_days_left"] = df["Closing Date"].apply(lambda x: days_until(str(x)))
        df["_urgency"] = df["_days_left"].apply(urgency_label)

        urgent = df[
            df["_days_left"].notna()
            & (df["_days_left"] >= 0)
            & (df["_days_left"] <= 5)
        ][["Job Title", "Company", "Closing Date", "_urgency", "Status"]]

        if urgent.empty:
            st.success("No Jobs Closing Within 5 Days")
        else:
            st.dataframe(urgent, use_container_width=True)