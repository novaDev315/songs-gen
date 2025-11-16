"""YouTube uploads page."""

import streamlit as st
from auth import require_auth

st.set_page_config(page_title="YouTube", page_icon="🎬", layout="wide")
api = require_auth()

st.title("🎬 YouTube Uploads")

# OAuth status
try:
    # Try to get uploads (will fail if not authenticated)
    uploads = api.list_uploads(limit=1)
    st.success("✅ YouTube authenticated")
except:
    st.warning("⚠️ YouTube not authenticated")
    if st.button("Authenticate with YouTube"):
        try:
            auth_url = api.get_oauth_url()
            st.markdown(f"[Click here to authenticate]({auth_url})")
            st.info("After authenticating, return to this page.")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")

# List uploads
try:
    uploads = api.list_uploads(limit=50)

    if uploads:
        st.write(f"**{len(uploads)} videos uploaded**")

        for upload in uploads:
            with st.expander(f"{upload['title']}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Video ID:** {upload['video_id']}")
                    st.write(f"**URL:** {upload['video_url']}")
                    st.write(f"**Privacy:** {upload['privacy']}")
                    st.write(f"**Uploaded:** {upload['uploaded_at'][:19]}")

                    if upload['description']:
                        st.caption(upload['description'][:200])

                with col2:
                    st.link_button("View on YouTube", upload['video_url'])
    else:
        st.info("No videos uploaded yet.")

except Exception as e:
    st.error(f"Error loading uploads: {e}")
