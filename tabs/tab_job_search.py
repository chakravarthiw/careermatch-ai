# tabs/tab_job_search.py
# ─────────────────────────────────────────────────────────────
# Job Search Tab — CareerMatch AI
#
# What this file does:
#   Renders the Job Search tab which allows the user to search
#   for Australian jobs via the Adzuna API. Results are shown
#   as expandable cards with sponsorship badges, salary info,
#   and a description preview. Jobs can be sent directly to
#   the Add Job tab with one click.
#
# Responsibilities:
#   - Accept keyword and location inputs
#   - Toggle sponsorship-priority sorting
#   - Call Adzuna API via src/job_search.py
#   - Display results as collapsible job cards
#   - Colour-code cards by sponsorship status
#   - Show salary range where available
#   - Allow one-click pre-fill of Add Job tab
#   - Track which cards have been added this session
#   - Persist search results across Streamlit reruns
#
# Inputs:
#   tabs — the list of Streamlit tab objects created in app.py
#
# Outputs:
#   Rendered Streamlit UI inside tabs[0]
#   Updates to st.session_state for Add Job tab pre-fill
#
# Dependencies:
#   src/job_search.py — search_jobs()
#
# Note on Adzuna descriptions:
#   Adzuna caps job descriptions at 500 characters.
#   This is enough for a preview but not for reliable
#   sponsorship detection or closing date extraction.
#   Users should click "View Job" to read the full listing
#   and paste the full description into the Add Job tab.
# ─────────────────────────────────────────────────────────────

import streamlit as st

from src.job_search import search_jobs


def _get_sponsorship_badge(sponsorship: str) -> str:
    # Converts a sponsorship label into a colour-coded emoji badge.
    # Used in both the expander title and the card body.
    # Input : sponsorship string from sponsorship_label()
    # Output: formatted badge string with emoji

    if sponsorship == "Likely Sponsorship":
        return "🟢 Likely Sponsorship"
    elif sponsorship == "No Sponsorship":
        return "🔴 No Sponsorship"
    else:
        return "🟡 Not Mentioned"


def _get_salary_display(sal_min, sal_max) -> str:
    # Formats Adzuna's separate min/max salary fields into
    # a single readable string.
    # Adzuna returns None for both fields if salary not listed.
    # Input : sal_min, sal_max — numeric or None
    # Output: formatted salary string or "Salary not listed"

    if sal_min and sal_max:
        return f"${sal_min:,.0f} – ${sal_max:,.0f}"
    elif sal_min:
        return f"From ${sal_min:,.0f}"
    elif sal_max:
        return f"Up to ${sal_max:,.0f}"
    else:
        return "Salary not listed"


def _render_job_card(i: int, job: dict):
    # ─────────────────────────────────────────────────────────
    # JOB CARD
    # ─────────────────────────────────────────────────────────
    # Renders one job result as a collapsible expander card.
    # Each card shows:
    #   - Sponsorship badge in the title (colour coded)
    #   - Job title and company in the title
    #   - Location in the title
    #   - Full company, location, salary, sponsorship in body
    #   - First 300 chars of description as a preview
    #   - View Job button — opens full listing in new tab
    #   - Add to Tracker button — pre-fills Add Job tab
    #
    # Cards that have already been added show a checkmark
    # and a disabled button to prevent duplicate adds.
    #
    # Input : i   — index of this job in the results list
    #         job — dict with title, company, location etc.
    # Output: rendered Streamlit expander with card content
    # ─────────────────────────────────────────────────────────

    sponsorship     = job.get("sponsorship", "Unknown")
    badge           = _get_sponsorship_badge(sponsorship)
    salary_display  = _get_salary_display(
        job.get("salary_min"),
        job.get("salary_max")
    )

    # Check if this card was already added this session
    already_added   = i in st.session_state.get("added_jobs", set())

    # Show checkmark in title if already added
    title_badge     = "✅ Added" if already_added else badge

    # ── Expander Title ────────────────────────────────────────
    # Title format: [badge] | [Job Title] — [Company] | [Location]
    # Kept on one line so cards are easy to scan quickly.
    with st.expander(
        f"{title_badge}   |   {job.get('title', 'Unknown')} — "
        f"{job.get('company', 'Unknown')}   |   "
        f"{job.get('location', '')}",
        expanded=False
    ):
        col_j1, col_j2 = st.columns([3, 1])

        with col_j1:

            # ── Job Details ───────────────────────────────────
            st.markdown(f"**Company:** {job.get('company', '—')}")
            st.markdown(f"**Location:** {job.get('location', '—')}")
            st.markdown(f"**Salary:** {salary_display}")
            st.markdown(f"**Sponsorship:** {badge}")

            # ── Description Preview ───────────────────────────
            # Adzuna caps at 500 chars so we show up to 300.
            # A "..." suffix signals the description is truncated.
            # User should click View Job to read the full listing.
            description = job.get("description", "")
            if description:
                st.markdown("**Preview:**")
                preview = (
                    description[:300] + "..."
                    if len(description) > 300
                    else description
                )
                st.caption(preview)

            # ── Sponsorship Note ──────────────────────────────
            # Remind the user that sponsorship detection on the
            # truncated Adzuna description is unreliable.
            # Full detection runs when they paste the complete
            # description in the Add Job tab.
            st.caption(
                "ℹ️ Sponsorship detection on previews is limited. "
                "Paste the full description in ➕ Add Job for accurate results."
            )

        with col_j2:

            # ── View Job Button ───────────────────────────────
            # Opens the full Adzuna listing in a new browser tab.
            # This is where the user reads the full description
            # before deciding whether to apply.
            st.link_button(
                "🔗 View Job",
                url=job.get("link", "#"),
                width="stretch",
            )

            # ── Add to Tracker Button ─────────────────────────
            # Pre-fills the Add Job tab session state with this
            # job's details so the user doesn't have to manually
            # copy anything. Button is disabled after first click
            # to prevent duplicate adds in the same session.
            if st.button(
                "✅ Already Added" if already_added else "➕ Add to Tracker",
                key=f"add_job_{i}",
                width="stretch",
                disabled=already_added,
            ):
                # Pre-fill Add Job tab form fields via session state
                st.session_state["_title_input"]          = job.get("title", "")
                st.session_state["_company_input"]        = job.get("company", "")
                st.session_state["_location_input"]       = job.get("location", "")
                st.session_state["_salary_input"]         = (
                    salary_display
                    if salary_display != "Salary not listed"
                    else ""
                )
                st.session_state["_job_link_input"]       = job.get("link", "")

                # Pass truncated description as a starting point.
                # User should replace with the full description.
                st.session_state["job_description_input"] = job.get("description", "")

                # Mark this card as added for this session
                st.session_state["added_jobs"].add(i)

                st.success(
                    "✅ Details sent to **➕ Add Job** tab — "
                    "switch tabs to review and save."
                )


def render(tabs):
    # render() is called from app.py and draws the entire Job Search tab.
    # Input : tabs — list of Streamlit tab objects from st.tabs()
    # Output: rendered Streamlit UI inside tabs[0]

    with tabs[0]:

        st.header("🔍 Find Jobs")
        st.caption(
            "Search Australian jobs via Adzuna. "
            "Enable sponsorship sorting to rank visa-friendly roles to the top."
        )

        # ── Initialise Session State ──────────────────────────
        # Persist search results and added-cards tracking across
        # Streamlit reruns. Without this, results disappear every
        # time the user interacts with any widget on the page.
        if "search_results" not in st.session_state:
            st.session_state["search_results"] = []

        if "search_keyword_used" not in st.session_state:
            st.session_state["search_keyword_used"] = ""

        if "search_location_used" not in st.session_state:
            st.session_state["search_location_used"] = ""

        if "added_jobs" not in st.session_state:
            st.session_state["added_jobs"] = set()

        # ── Search Controls ───────────────────────────────────
        # Three controls in a row:
        # 1. Keyword input — job title or skills
        # 2. Location input — city or state
        # 3. Sponsorship toggle — sorts results by visa friendliness
        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])

        with col_s1:
            search_keyword = st.text_input(
                "Job Title / Keywords",
                placeholder="e.g. Data Analyst, Event Coordinator",
                key="search_keyword",
            )

        with col_s2:
            search_location = st.text_input(
                "Location",
                placeholder="e.g. Melbourne, Sydney, Australia",
                value="Melbourne",
                key="search_location",
            )

        with col_s3:
            # st.write("") adds vertical space to align the
            # toggle with the text inputs above it
            st.write("")
            sponsorship_priority = st.toggle(
                "🛂 Sponsorship first",
                value=True,
                help=(
                    "Sorts results so sponsorship-friendly jobs "
                    "appear at the top of the list"
                ),
            )

        search_clicked = st.button(
            "🔍 Search Jobs",
            width="stretch",
        )

        # ── Execute Search ────────────────────────────────────
        # Only runs when Search button is clicked.
        # Results stored in session_state so they persist across
        # reruns triggered by other widget interactions.
        if search_clicked:
            if not search_keyword:
                st.warning("Please enter a job title or keyword.")
            else:
                with st.spinner(
                    f"Searching for **{search_keyword}** "
                    f"jobs in **{search_location}**..."
                ):
                    results = search_jobs(
                        keyword=search_keyword,
                        location=search_location,
                        sponsorship_priority=sponsorship_priority,
                    )

                # Store results and search terms for display
                st.session_state["search_results"]       = results
                st.session_state["search_keyword_used"]  = search_keyword
                st.session_state["search_location_used"] = search_location

                # Reset added cards tracking for new search
                # User starts fresh — no cards marked as added
                st.session_state["added_jobs"] = set()

                if not results:
                    st.warning(
                        "No jobs found. Try different keywords or location."
                    )

        # ── Display Results ───────────────────────────────────
        # Read from session_state — not from the search call above.
        # This means results stay visible even after the user
        # interacts with filters or other widgets on the page.
        results = st.session_state.get("search_results", [])

        if results:
            st.divider()

            # Show result count and search terms as context
            st.caption(
                f"Found **{len(results)}** jobs for "
                f"**{st.session_state.get('search_keyword_used', '')}** "
                f"in **{st.session_state.get('search_location_used', '')}**"
            )

            # Render each job as a collapsible card
            for i, job in enumerate(results):
                _render_job_card(i, job)