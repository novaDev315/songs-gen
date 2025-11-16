"""Authentication helpers for Streamlit."""

import streamlit as st
from api_client import APIClient


def require_auth() -> APIClient:
    """Require authentication and return API client."""
    if 'api_client' not in st.session_state:
        st.session_state.api_client = APIClient()

    if 'token' not in st.session_state or not st.session_state.get('authenticated'):
        show_login_page()
        st.stop()

    # Set token on client
    st.session_state.api_client.set_token(st.session_state.token)
    return st.session_state.api_client


def show_login_page() -> None:
    """Show login page."""
    st.title("🎵 Song Automation Pipeline")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.subheader("Login")

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                try:
                    client = APIClient()
                    response = client.login(username, password)

                    st.session_state.token = response['access_token']
                    st.session_state.refresh_token = response['refresh_token']
                    st.session_state.authenticated = True
                    st.session_state.username = username

                    st.success("Login successful!")
                    st.rerun()

                except Exception as e:
                    st.error(f"Login failed: {str(e)}")
            else:
                st.warning("Please enter username and password")
