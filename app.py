# app.py
# ─────────────────────────────────────────────────────────────
# CareerMatch AI — Main Entry Point
#
# This file is intentionally minimal.
# All tab logic lives in the tabs/ folder.
# This file only handles page config and tab orchestration.
# ─────────────────────────────────────────────────────────────

import streamlit as st

from tabs.tab_job_search import render as render_job_search
from tabs.tab_add_job    import render as render_add_job
from tabs.tab_tracker    import render as render_tracker
from tabs.tab_dashboard  import render as render_dashboard

# ── Page Configuration ────────────────────────────────────────
# Must be the first Streamlit call in the entire app.
st.set_page_config(
    page_title="CareerMatch AI",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 CareerMatch AI")
st.caption(
    "Job tracking, ATS matching, and sponsorship detection "
    "— built for the Australian job market."
)

# ── Tab Layout ────────────────────────────────────────────────
# Each tab is rendered by its own module in the tabs/ folder.
# To add a new tab: create tabs/tab_name.py with a render()
# function, import it here, add it to st.tabs(), and call it.
tabs = st.tabs([
    "🔍 Job Search",
    "➕ Add Job",
    "📋 Tracker",
    "📊 Dashboard",
])

render_job_search(tabs)
render_add_job(tabs)
render_tracker(tabs)
render_dashboard(tabs)