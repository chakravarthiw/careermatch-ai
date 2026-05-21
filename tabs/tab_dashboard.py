# tabs/tab_dashboard.py
# ─────────────────────────────────────────────────────────────
# Dashboard Tab — CareerMatch AI
#
# What this file does:
#   Renders the Dashboard tab which gives the user a high-level
#   overview of their entire job search at a glance.
#
# Responsibilities:
#   - Show 4 key metrics: Total Jobs, Applied, Interviews,
#     Sponsorship Friendly
#   - Show status breakdown bar chart
#   - Show sponsorship breakdown bar chart
#   - Show jobs closing within the next 5 days with urgency labels
#
# Inputs:
#   tabs — the list of Streamlit tab objects created in app.py
#
# Outputs:
#   Rendered Streamlit UI inside tabs[3]
#
# Dependencies:
#   src/tracker.py  — load_tracker()
#   src/utils.py    — days_until(), urgency_label()
# ─────────────────────────────────────────────────────────────

import streamlit as st

from src.tracker import load_tracker
from src.utils import days_until, urgency_label


def render():
    # Input : tabs — list of Streamlit tab objects from st.tabs()
    # Output: rendered Streamlit UI inside tabs[3]

    

    st.header("Dashboard")

    # ── Load Tracker Data ─────────────────────────────────
    # Load the current state of the Excel tracker.
    # If no jobs have been saved yet, show a prompt instead.
    df = load_tracker()

    if df.empty:
        st.info("Add jobs to view dashboard.")
        return

    # ── KPI Metrics Row ───────────────────────────────────
    # Four key stats displayed as large numbers in one row.
    # Each metric gives the user an instant read on where
    # their job search stands right now.
    #
    # len(df[df["Status"] == "Applied"]) counts rows where
    # the Status column equals "Applied".
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Jobs",
        len(df),
        help="Total number of jobs saved in your tracker"
    )

    col2.metric(
        "Applied",
        len(df[df["Status"] == "Applied"]),
        help="Jobs where status has been updated to Applied"
    )

    col3.metric(
        "Interviews",
        len(df[df["Status"] == "Interview"]),
        help="Jobs where you have an interview scheduled"
    )

    col4.metric(
        "Sponsorship Friendly",
        len(df[df["Sponsorship"] == "Likely Sponsorship"]),
        help="Jobs where sponsorship language was detected"
    )

    st.divider()

    # ── Pipeline Charts ───────────────────────────────────
    # Two side-by-side bar charts showing the breakdown of
    # applications by status and by sponsorship classification.
    #
    # value_counts() counts how many rows have each unique value.
    # e.g. {"Applied": 5, "Saved": 3, "Interview": 1}
    # st.bar_chart() renders it instantly — no matplotlib needed.
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Applications by Status")
        # value_counts() returns a Series sorted by frequency
        status_counts = df["Status"].value_counts()

        if status_counts.empty:
            st.info("No status data yet.")
        else:
            st.bar_chart(status_counts)

    with col2:
        st.subheader("Applications by Sponsorship")
        sponsorship_counts = df["Sponsorship"].value_counts()

        if sponsorship_counts.empty:
            st.info("No sponsorship data yet.")
        else:
            st.bar_chart(sponsorship_counts)

    st.divider()

    # ── Closing Soon Table ────────────────────────────────
    # Calculates days remaining for every saved job and
    # filters to only show jobs closing within 5 days.
    #
    # lambda x: ... applies days_until() to every row.
    # urgency_label() converts the integer to readable text.
    # Job Link is included so the user can click straight
    # to the application without searching for it.
    st.subheader("⏰ Closing Soon — Next 5 Days")
    st.caption("Jobs with a closing date within the next 5 days.")

    # Calculate days remaining for every job
    df["_days_left"] = df["Closing Date"].apply(
        lambda x: days_until(str(x))
    )

    # Convert days to human-readable urgency label
    df["_urgency"] = df["_days_left"].apply(urgency_label)

    # Filter to jobs closing within 5 days that are still open
    # notna() excludes rows where days_left could not be calculated
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
        "Job Link"
    ]]

    if urgent.empty:
        st.success("✅ No jobs closing within the next 5 days.")
    else:
        # Rename _urgency for cleaner display in the table
        urgent = urgent.rename(columns={"_urgency": "Urgency"})
        st.dataframe(urgent, width="stretch")

    st.divider()

    # ── Application Source Breakdown ──────────────────────
    # Shows which platforms your applications are coming from.
    # Helps identify if you're over-relying on one source.
    st.subheader("Applications by Source")
    source_counts = df["Source"].value_counts()

    if source_counts.empty:
        st.info("No source data yet.")
    else:
        st.bar_chart(source_counts)

    st.divider()

    # ── Learner Memory Status ─────────────────────────────
    # Shows how many title corrections and company names
    # have been collected by the learner module.
    # This section grows more useful as more jobs are saved.
    st.subheader("🧠 Learner Memory")
    st.caption("Tracks how the app is learning from your corrections over time.")

    try:
        from src.learner import correction_status
        stats = correction_status()

        mem_col1, mem_col2, mem_col3 = st.columns(3)

        mem_col1.metric(
            "Title Entries",
            stats.get("title_entries", 0),
            help="Total job saves recorded for title learning"
        )

        mem_col2.metric(
            "Known Companies",
            stats.get("known_companies", 0),
            help="Company names the app recognises automatically"
        )

        mem_col3.metric(
            "Correct Predictions",
            stats.get("correct_predictions", 0),
            help="Times the app correctly predicted the job title"
        )

        # Show current learning phase
        phase = stats.get("phase", "Unknown")
        entries_until_beta = stats.get("entries_until_beta", 0)

        if entries_until_beta > 0:
            st.info(
                f"📊 Learning phase: **{phase}** — "
                f"save **{entries_until_beta}** more jobs to reach Beta."
            )
        else:
            st.success(
                f"🎓 Learning phase: **{phase}** — "
                f"enough data collected to begin training."
            )

    except Exception as e:
        # Learner module may not exist in all deployments
        st.caption("Learner memory not available.")