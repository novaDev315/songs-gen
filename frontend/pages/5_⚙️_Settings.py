"""Settings page."""

import streamlit as st
from auth import require_auth

st.set_page_config(page_title="Settings", page_icon="⚙️", layout="wide")
api = require_auth()

st.title("⚙️ Settings")

# System status
st.subheader("System Status")
try:
    status = api.get_system_status()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("File Watcher", status['workers']['file_watcher'].upper())
    with col2:
        st.metric("Workers", status['workers']['background_workers'].upper())
    with col3:
        st.metric("Backup Scheduler", status['workers']['backup_scheduler'].upper())

except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")

# User info
st.subheader("User Information")
try:
    user = api.get_me()
    st.write(f"**Username:** {user['username']}")
    st.write(f"**Role:** {user['role']}")
    st.write(f"**Created:** {user['created_at'][:19]}")
except Exception as e:
    st.error(f"Error: {e}")

st.markdown("---")

# About
st.subheader("About")
st.markdown("""
**Song Automation Pipeline v1.0.0**

Complete automation system for AI-generated music:
- Automatic song detection
- Suno.com integration
- Quality evaluation
- YouTube upload automation

Built with FastAPI, Streamlit, and Docker.
""")
