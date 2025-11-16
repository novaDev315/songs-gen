"""Dashboard page with statistics and overview."""

import streamlit as st
from auth import require_auth
import pandas as pd

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
api = require_auth()

st.title("📊 Dashboard")

# Get system status
try:
    status = api.get_system_status()

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Songs",
            status['songs']['total'],
            delta=None
        )

    with col2:
        st.metric(
            "Pending Tasks",
            status['tasks']['by_status'].get('pending', 0)
        )

    with col3:
        st.metric(
            "Running Tasks",
            status['tasks']['by_status'].get('running', 0)
        )

    with col4:
        st.metric(
            "Uploaded to YouTube",
            status['songs']['by_status'].get('uploaded', 0)
        )

    st.markdown("---")

    # Song status breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Songs by Status")
        song_status_df = pd.DataFrame([
            {'Status': k.capitalize(), 'Count': v}
            for k, v in status['songs']['by_status'].items()
        ])
        st.bar_chart(song_status_df.set_index('Status'))

    with col2:
        st.subheader("Tasks by Status")
        task_status_df = pd.DataFrame([
            {'Status': k.capitalize(), 'Count': v}
            for k, v in status['tasks']['by_status'].items()
        ])
        st.bar_chart(task_status_df.set_index('Status'))

    # Recent songs
    st.markdown("---")
    st.subheader("Recent Songs")

    songs = api.list_songs(limit=10)
    if songs:
        for song in songs:
            with st.expander(f"{song['title']} - {song['status'].upper()}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {song['id']}")
                    st.write(f"**Genre:** {song.get('genre', 'N/A')}")
                with col2:
                    st.write(f"**Status:** {song['status']}")
                    st.write(f"**Created:** {song['created_at'][:19]}")
    else:
        st.info("No songs yet. Create a song file in generated/songs/ to get started!")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
