# app.py
# ─────────────────────────────────────────────────────────────
# CareerMatch AI — Main Application Entry Point
# 
# This is the top-level Streamlit app. It imports logic from
# src/tracker.py and src/utils.py, and renders the UI across
# three tabs: Add Job, Tracker, and Dashboard.
# ─────────────────────────────────────────────────────────────
import streamlit as st 
import pandas as pd

#import modules from src/ folder
from src.tracker import load_tracker, save_tracker, add_job, update_status, STATUSES, COLUMNS
from src.utils import days_until, urgency_label, sponsorship_label

# ── Page Configuration ────────────────────────────────────────
# # First streamlit call in scrit 
#  sets browser tab title, icon, and layout width

st.set_page_config(
    page_title = "CareerMatch AI",
    page_icon = "🎯",
    layout = "wide"             #"wide" -> uses full browser width - better for tables
)

# App header - visible at top of every tab
st.title("🎯 CareerMatch AI")
st.caption("Job tracking, ATS Matching and Sponsorship Detection - For Australian Market")

#  ── Tab Layout ────────────────────────────────────────────────
#  st.tabs() -> returns list of tab context managers
#  Each "with tabs[n]:" block renders contents inside that tab
tabs = st.tabs([
    "➕ Add Job",
    "📋 Tracker",
    "📊 Dashboard"
])

# ═════════════════════════════════════════════════════════════
# TAB 1 -> ADD JOB
# Renders a form for the user to manually enter a new job
# on "SAVE" runs sponsorship detection and writes to excel
# ═════════════════════════════════════════════════════════════

with tabs[0]:
    st.header("Add a New Job")

    # st.columns(2) -> splits layout into two equal side-by-side COLUMNS
    # this keeps the form compact rather than a vertical list

    col1, col2 = st.columns(2)

    with col1:
        job_title = st.text_input("Job Title *")
        company = st.text_input("Company *")
        location = st.text_input("Location  *")
        job_link = st.text_input("Job Link")
        source = st.selectbox("Source", [
            "SEEK", "LinkedIn", "Indeed",
            "Company Website", "Referral", "Other"
        ])
    

    with col2:
        employment_type = st.selectbox("Empolyment Type:", [
            "Full-time", "Part-time", "Casual", "Contract", "Internship"
        ])
        salary = st.text_input("Salary / Rate(optional)")
        closing_date = st.date_input("Closing Date")

        # the job description is used ONLY for sponsorship detection at this stage
        # in phase 2-> will be used for ATS keyword matching
        job_description = st.text_area(
            "Paste Job Description - Sponsorship Detection Purpose",
            height = 150
        )
    notes = st.text_area("Notes")

    # ── Save Button ───────────────────────────────────────────
    # use container with=True makes button stretch full width
    if st.button("💾 Save Job", use_container_width=True):
        
        # Basic validation - job title and company are minimum required fields
        if not job_title or not company:
            st.error("Job Title and Company Required")
        else:

            # run sponsorship detection before saving
            # sponsorship_label() -> scans job description for for keywords related to sponsorship_label
            # returns results with oprions - "No Sponsorship", "Not Mentioned", "Unknown", "Likely Sponsorship"
            detected_sponsorship = sponsorship_label(job_description)


            add_job(
                job_title = job_title,
                company = company,
                location = location,
                job_link = job_link,
                source = source,
                closing_date = str(closing_date), #convert date object to string for Excel
                employment_type = employment_type,
                salary = salary,
                sponsorship = detected_sponsorship,
                notes = notes

            )

            st.success(f"✅ Job saved! Sponsorship detected: **{detected_sponsorship}**")
            st.balloons() #UX feedback - celebration



# ═════════════════════════════════════════════════════════════
# TAB - 2 load_tracker
# loads all saved jobs and displays them in filterable table
# allows in line status updates and csv export
# ═════════════════════════════════════════════════════════════

with tabs[1]:
    st.header("Application Tracker")

    #load the current state of tracker from excel
    df = load_tracker()

    if df.empty:
        st.info("No jobs saved yet. Add your first one in the ➕ tab!")
    else:
        # ── Filters ───────────────────────────────────────────
        # Multiselect lets the user show/hide rows by status and sponsorship
        # default = show all rows
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect("Filter by Status",
                                           options = STATUSES,
                                           default = STATUSES)
        
        with col2:
            sponsorship_filter = st.multiselect(
                "Filter By Sponsorship",
                options = ["No Sponsorship", "Not Mentioned", "Unknown", "Likely Sponsorship"],
                default = ["No Sponsorship", "Not Mentioned", "Unknown", "Likely Sponsorship"]
            )

        # Apply both filters using boolean indexing
        # .isin() check if row value in selected list
        filtered = df[
            df["Status"].isin(status_filter)
            &
            df["Sponsorship"].isin(sponsorship_filter)
        ]

        # render the filtered dataframe as interactive table
        st.dataframe(filtered, use_container_width = True, height = 400)

        # ── Inline Status Update ──────────────────────────────
        # Allows user to update Job Status directly from tracker tab
        # without reopening or re-entering job details
        st.subheader("Update Job Status")
        if not filtered.empty:
            row_index = st.number_input(
                "Row Number to Update(0 = first row)",
                min_value = 0,
                max_value = len(df)-1,
                step = 1
            )
            new_status = st.selectbox("New Status", STATUSES)


            if st.button("Update Status"):
                update_status(int(row_index), new_status)
                st.success("Status Updated")
                st.rerun() #refresh page to update table dynamically
            

            # ── Inline Status Update ──────────────────────────────
            # Converts filtered dataframe to CSV and gives download option
            # only current filtered view is exported - not full excel dataframe
            st.download_button(
                label = "⬇️ Download as CSV",
                data = filtered.to_csv(index=False),
                file_name = "careermatch_tracker.csv",
                mime = "text/csv"
            )


# ═════════════════════════════════════════════════════════════
# TAB 3 - DASHBOARD
# Provides high level summary of job search progress
# Shows Key Metrics, status breakdown, sponsorship breakdown, 
# and list of jobs closing in next 5 days
# ═════════════════════════════════════════════════════════════



with tabs[2]:
    st.header("Dashboard")

    df = load_tracker()

    if df.empty:
        st.info("Add Jobs to view bashboard")
    else:
        # - Top Metrics Row ───────────────────────────────────────────
        # st.metric() -> renders a large number with a label
        # four columns = four KPI in single row
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Jobs:",
                    len(df))
        col2.metric("Applied Jobs:",
                    len(df[df["Status"]== "Applied"]))
        col3.metric("Interviews:",
                    len(df[df["Status"] == "Interview"]))
        col4.metric("Sponsorship Friendly:",
                    len(df[df["Sponsorship"] == "Likely Sponsorship"]))
        
        st.divider()

        # - Graphs ───────────────────────────────────────────
        # st.bar_chart() is a quick built-in chart — no matplotlib needed.
        # value_counts() counts how many rows have each unique value.

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("By Status")
            st.bar_chart(df["Status"].value_counts())

        with col2:
            st.subheader("By Sponsorship")
            st.bar_chart(df["Sponsorship"].value_counts())

        st.divider()

        # - Graphs ───────────────────────────────────────────
        # for graph, calculate days remaining until closing closing_date      
        # days_until() -> retuns integer or none if no closing_date
        # urgency_label() -> counts how many rows have unique value
        st.subheader("⏰ Closing Soon")

        df["_days_left"] = df["Closing Date"].apply(
            lambda x: days_until(str(x))    #lambda applies function to every row
        )
        df["_urgency"] = df["_days_left"].apply(urgency_label)

        # filter the jobs that are closing only within 7 days that hasn't closed yet
        urgent = df[
            df["_days_left"].notna() 
            &
            (df["_days_left"] >= 0)
            &
            (df["_days_left"] <= 5)
        ][["Job Title", "Company", "Closing Date", "_urgency", "Status"]]

        if urgent.empty:
            st.success("No Jobs Closing Within 5 Days")
        else: 
            st.dataframe(urgent, use_container_width = True)



        





