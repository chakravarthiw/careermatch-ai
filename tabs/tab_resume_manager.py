# tabs/tab_resume_manager.py
# ─────────────────────────────────────────────────────────────
# Resume Manager Tab - CareerMatch AI
# ─────────────────────────────────────────────────────────────

# Pupose:
# Manages the user's' MASTER resume

# Why this exists:
#     1. Instead of repeatedly pasting the resume into ATS tools,
#        the user saves it once and the app reuses it in the UI

# Features that depend on this:
#     1. ATS matching
#     2. Resume Optimisation
#     3. Resume tailoring
#     4. AI Powered resume suggestions

# Workflow:
# User pastes resume
# → Clicks Save Resume
# → Resume saved to disk
# → Other tabs can load it automatically
# ─────────────────────────────────────────────────────────────

import streamlit as st
from src.resume_store import(
    save_resume, load_resume, resume_exists, delete_resume
)

# ═════════════════════════════════════════════════════════════
# MAIN TAB FUNCTION
# ═════════════════════════════════════════════════════════════
# app.py will call this function when the user switches to the resume Manager tab

def render():
    def clear_resume():
        delete_resume()
        st.session_state["resume_text_area"] = ""
    
    # ═════════════════════════════════════════════════════════════
    # TAB HEADER
    # ═════════════════════════════════════════════════════════════
    # Main title and helper text shown at top of tab
    # ═════════════════════════════════════════════════════════════
    st.header("📄 Resume Manager")

    st.caption("Save your Resume")

    # ═════════════════════════════════════════════════════════════
    # LOAD EXISTING RESUME
    # ═════════════════════════════════════════════════════════════
    # load_resume() reads saved resume from disk
    # if resume exists: 
    #     1. loads into text area
    #     2. user can edit/update at any time
    # ═════════════════════════════════════════════════════════════

    saved_resume = load_resume()

    # ═════════════════════════════════════════════════════════════
    # RESUME STATUS MESSAGE
    # ═════════════════════════════════════════════════════════════
    # Shows whether app currently has a saved resume
    # resume_exists() checks:
    #     1. file exists
    #     2. resume is not emply
    # ═════════════════════════════════════════════════════════════

    if resume_exists():
        word_count = len(saved_resume.split())
        st.success(f"Current Resume Saved - {word_count} words")
    else:
        st.warning("Please save a resume")
        
    # ─────────────────────────────────────────────────────────
    # RESUME METRICS
    # ─────────────────────────────────────────────────────────
    # Shows quick statistics about the saved resume.
    # Helps users understand resume size and completeness.
    # ─────────────────────────────────────────────────────────

    word_count = len(saved_resume.split()) if saved_resume else 0

    char_count = len(saved_resume) if saved_resume else 0

    line_count = (
        len(saved_resume.splitlines())
        if saved_resume
        else 0
    )

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    metric_col1.metric(
        "Words",
        word_count
    )

    metric_col2.metric(
        "Characters",
        char_count
    )

    metric_col3.metric(
        "Lines",
        line_count
    )

    st.divider()
            

    # ═════════════════════════════════════════════════════════════
    # RESUME TEXT AREA
    # ═════════════════════════════════════════════════════════════
    # Main input area where user pasts their resume 
    # value=saved_resume
    # automatically loads previously saved resume
    # ═════════════════════════════════════════════════════════════

    resume_text = st.text_area(
        "Paste Current Resume",
        value = saved_resume,
        height = 400,
        key = "resume_text_area",
        help = (
            "Pase resume into this text area please"
        )
    )

    st.divider()

    # ═════════════════════════════════════════════════════════════
    # ACTION BUTTONS
    # ═════════════════════════════════════════════════════════════
    # SAVE BUTTON       - saves resume to disk using save_resume
    # CLEAR RESUME      - removes saved file
    # ═════════════════════════════════════════════════════════════
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "💾 Save Resume",
            width = "stretch",
            type = "primary"
        ):
            # ═════════════════════════════════════════════════════════════
            # VALIDATION
            # ═════════════════════════════════════════════════════════════
            # Prevents empty resumes from being saved 
            # .strip() removes empty spaces
            # ═════════════════════════════════════════════════════════════
            if resume_text.strip():
                
                # Save resume to disk
                save_resume(resume_text)
                
                # Show success message
                st.success(
                    "✅ Resume saved successfully."
                )

                # Rerun to refresh UI
                st.rerun()
            else:

                # Error if user tries to save empty resume 
                st.error(
                    "Please paste your resume before saving."
                )
    with col2:
        # The button is displayed only if a resume exists
        if resume_exists():
            st.button(
                "🗑️ Clear Resume",
                width="stretch",
                on_click = clear_resume
            )
               

            
