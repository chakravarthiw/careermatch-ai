# tabs/tab_tracker.py
# ─────────────────────────────────────────────────────────────
# Tracker Tab — CareerMatch AI
#
# What this file does:
#   Renders the Application Tracker tab which gives the user
#   a full view of all saved job applications with filtering,
#   search, status updates, and export functionality.
#
# Responsibilities:
#   - Load and display saved jobs from Excel
#   - Filter by status and sponsorship
#   - Search by job title or company name
#   - Show focused 6-column table view
#   - Allow inline status updates with job detail expander
#   - Export filtered view as CSV
#   - Danger zone — delete all jobs with confirmation
#
# Inputs:
#   tabs — the list of Streamlit tab objects created in app.py
#
# Outputs:
#   Rendered Streamlit UI inside tabs[2]
#
# Dependencies:
#   src/tracker.py — load_tracker(), save_tracker(),
#                    update_status(), STATUSES, COLUMNS
# ─────────────────────────────────────────────────────────────

import streamlit as st
import pandas as pd

from src.tracker import (
    load_tracker,
    save_tracker,
    update_status,
    STATUSES,
    COLUMNS,
)


def render(tabs):
    # render() is called from app.py and draws the entire Tracker tab.
    # Input : tabs — list of Streamlit tab objects from st.tabs()
    # Output: rendered Streamlit UI inside tabs[2]

    with tabs[2]:

        st.header("Application Tracker")

        # ── Load Tracker Data ─────────────────────────────────
        # Load the current state of the Excel tracker.
        # If no jobs saved yet — show a prompt and stop rendering.
        df = load_tracker()

        if df.empty:
            st.info("No jobs saved yet. Add your first one in the ➕ tab!")

        else:

            # ── Filters ───────────────────────────────────────
            # Three controls side by side:
            # 1. Status multiselect — show/hide by pipeline stage
            # 2. Sponsorship multiselect — show/hide by visa status
            # 3. Text search — filter by job title or company name
            #
            # All three apply simultaneously to the filtered table.
            col1, col2, col3 = st.columns(3)

            with col1:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=STATUSES,
                    default=STATUSES,
                    help="Show only jobs at selected pipeline stages"
                )

            with col2:
                sponsorship_filter = st.multiselect(
                    "Filter by Sponsorship",
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
                    help="Show only jobs matching selected sponsorship status"
                )

            with col3:
                search_text = st.text_input(
                    "🔍 Search Job Title / Company",
                    placeholder="e.g. Data Analyst, ANZ"
                )

            # ── Apply Filters ─────────────────────────────────
            # .isin() checks if each row's value is in the
            # selected list. & means both conditions must match.
            filtered = df[
                df["Status"].isin(status_filter)
                & df["Sponsorship"].isin(sponsorship_filter)
            ]

            # Apply text search across Job Title and Company.
            # .str.contains() checks if the search text appears
            # anywhere in the column value — case insensitive.
            if search_text:
                search_lower = search_text.lower()
                filtered = filtered[
                    filtered["Job Title"].astype(str).str.lower().str.contains(search_lower)
                    |
                    filtered["Company"].astype(str).str.lower().str.contains(search_lower)
                ]

            # ── Focused Table View ────────────────────────────
            # Only show the 6 most important columns in the UI.
            # Full data with all 20 columns is still saved in
            # Excel and available via the CSV export below.
            display_columns = [
                "Job Title",
                "Company",
                "Status",
                "Sponsorship",
                "Closing Date",
                "Job Link",
            ]

            # Safety check — only include columns that exist.
            # Prevents crashes if a column is missing for any reason.
            safe_display = [
                col for col in display_columns
                if col in filtered.columns
            ]

            # Show result count so user knows how many rows match
            st.caption(
                f"Showing **{len(filtered)}** of **{len(df)}** jobs"
            )

            st.dataframe(
                filtered[safe_display],
                width="stretch",
                height=400,
            )

            st.divider()

            # ── Status Update ─────────────────────────────────
            # Lets the user move an application through the pipeline
            # e.g. Saved → Tailoring → Applied → Interview.
            #
            # When status is set to "Applied", tracker.py
            # automatically fills today's date in Date Applied.
            st.subheader("Update Job Status")

            if not filtered.empty:

                row_index = st.number_input(
                    "Row number to update (0 = first row)",
                    min_value=0,
                    max_value=len(df) - 1,
                    step=1,
                    help="Row number matches the leftmost number in the table above"
                )

                # ── Job Detail Expander ───────────────────────
                # When a row number is entered, show the full
                # details of that job including hidden fields
                # like location, salary, employment type, notes.
                # Collapsed by default to keep the UI clean.
                if row_index < len(df):
                    selected_row = df.iloc[int(row_index)]

                    with st.expander(
                        f"📋 {selected_row.get('Job Title', 'Unknown')} "
                        f"at {selected_row.get('Company', 'Unknown')}",
                        expanded=False
                    ):
                        # to_frame() converts the single row into
                        # a vertical key-value table — cleaner than
                        # listing each field with st.markdown()
                        st.dataframe(
                            selected_row.to_frame(name="Details"),
                            width="stretch",
                        )

                new_status = st.selectbox(
                    "New Status",
                    STATUSES,
                    help="Select the new pipeline stage for this application"
                )

                if st.button(
                    "✅ Update Status",
                    width="stretch"
                ):
                    # update_status() in tracker.py handles the
                    # Excel write and auto-fills Date Applied
                    # if the new status is "Applied"
                    update_status(int(row_index), new_status)
                    st.success(f"Status updated to **{new_status}**")
                    # Rerun refreshes the table immediately
                    st.rerun()

            st.divider()

            # ── CSV Export ────────────────────────────────────
            # Exports only the currently filtered view — not
            # the full tracker. This means the user can filter
            # to e.g. "Applied" jobs and export just those.
            st.download_button(
                label="⬇️ Download Filtered View as CSV",
                data=filtered.to_csv(index=False),
                file_name="careermatch_tracker.csv",
                mime="text/csv",
                help="Downloads the currently filtered view as a CSV file"
            )

        # ── Danger Zone ───────────────────────────────────────
        # Placed outside the else block so it's always visible —
        # even when the tracker is empty, the user can still
        # trigger a reset if the file is in a bad state.
        #
        # Hidden inside an expander and requires typing DELETE
        # exactly to confirm — prevents accidental deletion.
        st.divider()
        st.subheader("⚠️ Danger Zone")

        with st.expander("🗑️ Delete All Saved Jobs"):

            st.warning(
                "This will permanently delete ALL saved jobs "
                "from the tracker. This action CANNOT be undone."
            )

            confirm_text = st.text_input(
                "Type DELETE to confirm",
                key="delete_confirm",
                placeholder="DELETE"
            )

            if st.button(
                "🗑️ Delete All Jobs",
                type="primary",
                width="stretch"
            ):
                if confirm_text == "DELETE":
                    # Replace tracker with empty DataFrame
                    # keeping the correct column structure
                    save_tracker(pd.DataFrame(columns=COLUMNS))
                    st.success("✅ All jobs deleted.")
                    st.rerun()
                else:
                    st.error(
                        "Type DELETE exactly to confirm. "
                        "This cannot be undone."
                    )