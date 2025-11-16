"""Queue management page."""

import streamlit as st
from auth import require_auth
import pandas as pd

st.set_page_config(page_title="Queue", page_icon="📋", layout="wide")
api = require_auth()

st.title("📋 Task Queue")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    status_filter = st.selectbox(
        "Status",
        ['All', 'pending', 'running', 'completed', 'failed']
    )

with col2:
    task_type_filter = st.selectbox(
        "Task Type",
        ['All', 'suno_upload', 'suno_download', 'evaluate', 'youtube_upload']
    )

with col3:
    limit = st.number_input("Results", min_value=10, max_value=200, value=50)

# Fetch tasks
try:
    tasks = api.list_tasks(
        status=None if status_filter == 'All' else status_filter,
        task_type=None if task_type_filter == 'All' else task_type_filter,
        limit=limit
    )

    if tasks:
        st.write(f"**Found {len(tasks)} tasks**")

        # Create DataFrame
        df = pd.DataFrame(tasks)

        # Display table
        st.dataframe(
            df[['id', 'task_type', 'song_id', 'status', 'priority', 'retry_count', 'created_at']],
            use_container_width=True
        )

        # Failed task actions
        failed_tasks = [t for t in tasks if t['status'] == 'failed']
        if failed_tasks:
            st.markdown("---")
            st.subheader(f"⚠️ Failed Tasks ({len(failed_tasks)})")

            for task in failed_tasks:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Task {task['id']}**: {task['task_type']} - Song: {task['song_id']}")
                    if task.get('error_message'):
                        st.caption(f"Error: {task['error_message'][:100]}")
                with col2:
                    if st.button(f"Retry", key=f"retry_{task['id']}"):
                        try:
                            api.retry_task(task['id'])
                            st.success("Task re-queued!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Retry failed: {e}")
    else:
        st.info("No tasks found.")

except Exception as e:
    st.error(f"Error loading queue: {e}")
