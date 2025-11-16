"""Song Automation Pipeline - Streamlit Frontend"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Song Automation Pipeline",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for mobile-friendly design
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .feature-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Main header
st.markdown('<div class="main-header">🎵 Song Automation Pipeline</div>', unsafe_allow_html=True)

# Introduction
st.markdown(
    """
    Welcome to the **Song Automation Pipeline**!

    This system automates the entire workflow from song creation to YouTube upload:
    """
)

# Feature overview
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="feature-box">
        <h3>📁 File Monitoring</h3>
        Automatically detects new song files in the generated/ folder
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-box">
        <h3>⬇️ Download Management</h3>
        Downloads generated audio from Suno automatically
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-box">
        <h3>🎬 YouTube Upload</h3>
        Publishes approved songs to YouTube with metadata
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-box">
        <h3>☁️ Suno Integration</h3>
        Uploads song prompts to Suno.com for generation
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-box">
        <h3>⭐ Quality Evaluation</h3>
        Automated quality checks and manual review interface
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="feature-box">
        <h3>📊 Progress Tracking</h3>
        Real-time status updates for all songs in pipeline
        </div>
        """,
        unsafe_allow_html=True,
    )

# Status section
st.markdown("---")
st.subheader("System Status")

col1, col2, col3 = st.columns(3)

# Get backend URL from environment
backend_url = os.getenv("BACKEND_URL", "http://backend:8000")

with col1:
    st.metric("Phase", "1: Core Infrastructure")

with col2:
    st.metric("Status", "✅ Complete")

with col3:
    st.markdown(f'<p class="status-success">Backend: {backend_url}</p>', unsafe_allow_html=True)

# Phase information
st.markdown("---")
st.subheader("Implementation Roadmap")

phases = [
    ("Phase 1", "Core Infrastructure", "✅ Complete", True),
    ("Phase 2", "Backend Core Services", "⏳ Upcoming", False),
    ("Phase 3", "Suno Integration", "⏳ Planned", False),
    ("Phase 4", "Evaluation System", "⏳ Planned", False),
    ("Phase 5", "YouTube Integration", "⏳ Planned", False),
    ("Phase 6", "Web UI Features", "⏳ Planned", False),
    ("Phase 7", "Testing & Validation", "⏳ Planned", False),
]

for phase_name, phase_desc, phase_status, is_complete in phases:
    with st.expander(f"{phase_name}: {phase_desc} - {phase_status}", expanded=is_complete):
        if phase_name == "Phase 1":
            st.markdown(
                """
                **Completed:**
                - ✅ Docker Compose setup (backend + frontend)
                - ✅ SQLite database with WAL mode
                - ✅ JWT authentication with refresh tokens
                - ✅ Database models (users, songs, suno_jobs, evaluations, youtube_uploads, task_queue)
                - ✅ Automated daily backups (3 AM, 30-day retention)
                - ✅ Health check endpoints
                - ✅ CORS configuration
                """
            )
        else:
            st.info(f"{phase_name} features will be available in upcoming releases.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6c757d; font-size: 0.9rem;">
    Song Automation Pipeline v1.0.0 | Phase 1 Complete<br>
    Built with FastAPI + Streamlit + Docker
    </div>
    """,
    unsafe_allow_html=True,
)
