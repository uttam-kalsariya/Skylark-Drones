"""
Streamlit Web Application & Interactive Chat Interface for Skylark Drones BI Agent.

Responsible for:
- Streamlit chat UI using st.chat_message and st.chat_input.
- Managing session state for multi-turn conversation history.
- Displaying monday.com board connection status & item metrics in the sidebar.
"""

import os
import streamlit as st
from dotenv import load_dotenv

import agent
import monday_client

load_dotenv()

# Page Setup
st.set_page_config(
    page_title="Skylark Drones BI Agent",
    page_icon="🚁",
    layout="wide",
)


@st.cache_data(ttl=300)
def get_board_connection_status():
    """Fetch board metadata and item counts for the sidebar status view."""
    status = {"connected": False, "error": None, "boards": {}}
    try:
        token = os.getenv("MONDAY_API_TOKEN")
        if not token:
            status["error"] = "MONDAY_API_TOKEN missing in .env"
            return status

        boards = monday_client.list_boards()
        status["connected"] = True

        work_orders_id = os.getenv("WORK_ORDERS_BOARD_ID")
        deals_id = os.getenv("DEALS_BOARD_ID")

        for b in boards:
            b_id = str(b["id"])
            if work_orders_id and b_id == str(work_orders_id):
                items = monday_client.get_board_items(b_id)
                status["boards"]["Work Orders"] = {"id": b_id, "name": b["name"], "count": len(items)}
            elif deals_id and b_id == str(deals_id):
                items = monday_client.get_board_items(b_id)
                status["boards"]["Deals"] = {"id": b_id, "name": b["name"], "count": len(items)}

        # Fallback if board IDs are not set explicitly
        if not status["boards"] and boards:
            for b in boards[:2]:
                items = monday_client.get_board_items(b["id"])
                status["boards"][b["name"]] = {"id": b["id"], "name": b["name"], "count": len(items)}

    except Exception as err:
        status["connected"] = False
        status["error"] = str(err)

    return status


# Sidebar Configuration
with st.sidebar:
    st.title("🚁 Skylark Drones")
    st.caption("Business Intelligence Assistant")
    st.divider()

    st.subheader("monday.com Connection")
    conn_info = get_board_connection_status()

    if conn_info["connected"]:
        st.success("Connected to monday.com API v2")
        if conn_info["boards"]:
            for board_label, details in conn_info["boards"].items():
                st.metric(
                    label=f"📋 {board_label} ({details['name']})",
                    value=f"{details['count']} records",
                )
        else:
            st.info("No specific board IDs configured in .env")
    else:
        st.error("Connection Offline")
        if conn_info["error"]:
            st.caption(f"Error: {conn_info['error']}")

    st.divider()
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main Interface Title
st.title("Business Intelligence Agent")
st.markdown(
    "Ask questions about pipeline health, overdue work orders, sector performance, or request a **leadership update**."
)

# Session State for Conversation History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Existing Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input Box
if prompt := st.chat_input("Ask a BI question (e.g. 'Which work orders are overdue?')..."):
    # Render user prompt
    with st.chat_message("user"):
        st.markdown(prompt)

    # Store user prompt in history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare assistant response container
    with st.chat_message("assistant"):
        with st.spinner("Analyzing live monday.com data..."):
            try:
                # Call agent orchestrator passing full conversation history
                history_for_agent = st.session_state.messages[:-1]
                response_text = agent.run_agent(
                    user_message=prompt,
                    conversation_history=history_for_agent,
                )
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                error_msg = f"⚠️ **Error executing query**: {e}"
                st.error(error_msg)
