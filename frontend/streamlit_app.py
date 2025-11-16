"""Song Automation Pipeline - Streamlit Frontend"""

import streamlit as st
from auth import require_auth

st.set_page_config(
    page_title="Song Automation Pipeline",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Require authentication
api = require_auth()

# Main dashboard content
st.title("🎵 Song Automation Pipeline")
st.markdown("""
Welcome to the Song Automation Pipeline!

Use the sidebar to navigate to different sections:
- 📊 **Dashboard**: Overview and statistics
- 📋 **Queue**: Task queue status
- ⭐ **Review**: Manual song review
- 🎬 **YouTube**: Uploaded videos
- ⚙️ **Settings**: Configuration

Current user: **{username}**
""".format(username=st.session_state.get('username', 'Unknown')))

st.markdown("---")

# Feature overview
st.subheader("System Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📁 File Monitoring**

    Automatically detects new song files in the generated/ folder
    """)

with col2:
    st.markdown("""
    **☁️ Suno Integration**

    Uploads song prompts to Suno.com for generation
    """)

with col3:
    st.markdown("""
    **⬇️ Download Management**

    Downloads generated audio from Suno automatically
    """)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **⭐ Quality Evaluation**

    Automated quality checks and manual review interface
    """)

with col2:
    st.markdown("""
    **🎬 YouTube Upload**

    Publishes approved songs to YouTube with metadata
    """)

with col3:
    st.markdown("""
    **📊 Progress Tracking**

    Real-time status updates for all songs in pipeline
    """)

# Sidebar logout button
st.markdown("---")
if st.sidebar.button("Logout"):
    for key in ['token', 'refresh_token', 'authenticated', 'username']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()
