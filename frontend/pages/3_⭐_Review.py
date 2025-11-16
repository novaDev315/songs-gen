"""Song review page for manual evaluation."""

import streamlit as st
from auth import require_auth

st.set_page_config(page_title="Review", page_icon="⭐", layout="wide")
api = require_auth()

st.title("⭐ Song Review")

# Filter
review_filter = st.radio(
    "Show",
    ['Pending Review', 'Approved', 'Rejected', 'All'],
    horizontal=True
)

# Fetch evaluations
try:
    if review_filter == 'Pending Review':
        evaluations = api.list_evaluations(approved=None)
        evaluations = [e for e in evaluations if e.get('manual_rating') is None]
    elif review_filter == 'Approved':
        evaluations = api.list_evaluations(approved=True)
    elif review_filter == 'Rejected':
        evaluations = api.list_evaluations(approved=False)
    else:
        evaluations = api.list_evaluations()

    if evaluations:
        st.write(f"**{len(evaluations)} songs to review**")

        for eval in evaluations:
            song = api.get_song(eval['song_id'])

            with st.expander(f"{song['title']} - Quality Score: {eval.get('audio_quality_score', 'N/A')}", expanded=eval.get('manual_rating') is None):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("Song Details")
                    st.write(f"**ID:** {song['id']}")
                    st.write(f"**Genre:** {song.get('genre', 'N/A')}")
                    st.write(f"**Style Prompt:** {song.get('style_prompt', 'N/A')[:100]}")

                    st.subheader("Quality Metrics")
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    with metrics_col1:
                        st.metric("Quality Score", f"{eval.get('audio_quality_score', 0):.1f}/100")
                    with metrics_col2:
                        st.metric("Duration", f"{eval.get('duration_seconds', 0):.1f}s")
                    with metrics_col3:
                        st.metric("File Size", f"{eval.get('file_size_mb', 0):.2f} MB")

                    # Audio player (if downloaded)
                    audio_path = f"/app/downloads/{song['id']}.mp3"
                    try:
                        st.audio(audio_path)
                    except:
                        st.info("Audio file not available for preview")

                with col2:
                    st.subheader("Manual Review")

                    if eval.get('approved') is not None:
                        st.success("✅ Approved" if eval['approved'] else "❌ Rejected")
                        if eval.get('notes'):
                            st.caption(f"Notes: {eval['notes']}")
                    else:
                        rating = st.slider(
                            "Your Rating",
                            min_value=1,
                            max_value=5,
                            value=3,
                            key=f"rating_{eval['id']}"
                        )

                        notes = st.text_area(
                            "Notes",
                            key=f"notes_{eval['id']}",
                            height=100
                        )

                        col_approve, col_reject = st.columns(2)

                        with col_approve:
                            if st.button("✅ Approve", key=f"approve_{eval['id']}", use_container_width=True):
                                try:
                                    api.approve_song(eval['id'])
                                    st.success("Song approved!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

                        with col_reject:
                            if st.button("❌ Reject", key=f"reject_{eval['id']}", use_container_width=True):
                                try:
                                    api.reject_song(eval['id'], notes)
                                    st.warning("Song rejected")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    else:
        st.info("No songs to review.")

except Exception as e:
    st.error(f"Error loading reviews: {e}")
