"""
Streamlit Web Application & Interactive Chat Interface for Skylark Drones BI Agent.

Light Theme & Sticky Header Implementation:
- Pure light slate background (#f8fafc) and pure white cards (#ffffff).
- High contrast dark navy text (#0f172a / #1e293b).
- Sticky top header (z-index 9999) using CSS :has(.hdr-anchor) selector.
- Zero top gap: padding-top: 0 on main block container.
"""

import os
import time
import streamlit as st
from dotenv import load_dotenv

import agent
import monday_client

load_dotenv()

# Page Setup
st.set_page_config(
    page_title="Skylark Drones · BI Agent",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Light Theme & Sticky Header CSS ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ══ Hide Default Streamlit Top Header Bar ══ */
[data-testid="stHeader"] {
    display: none !important;
}

/* ══ Global Reset & Light Theme Override ══ */
html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

/* ══ Main Block Container: Remove Top Blank Space ══ */
.main .block-container, [data-testid="stMainBlockContainer"] {
    padding-top: 0rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* ══ Sticky Top Header Component via :has(.hdr-anchor) ══ */
[data-testid="stVerticalBlock"] > div:has(.hdr-anchor) {
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;
    background-color: #ffffff !important;
    border-bottom: 1px solid #e2e8f0 !important;
    padding: 10px 2rem !important;
    margin-left: -2rem !important;
    margin-right: -2rem !important;
    margin-top: 0 !important;
    margin-bottom: 1rem !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05) !important;
}

/* Align columns vertically inside Sticky Header */
[data-testid="stVerticalBlock"] > div:has(.hdr-anchor) [data-testid="stHorizontalBlock"] {
    align-items: center !important;
}

[data-testid="stVerticalBlock"] > div:has(.hdr-anchor) [data-testid="stColumn"] {
    display: flex !important;
    align-items: center !important;
}

/* Uniform Height & Alignment for Header Buttons & Popovers */
[data-testid="stVerticalBlock"] > div:has(.hdr-anchor) button {
    height: 36px !important;
    min-height: 36px !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0 12px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #1e293b !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    margin: 0 !important;
    width: 100% !important;
    transition: all 0.18s ease-in-out !important;
}

[data-testid="stVerticalBlock"] > div:has(.hdr-anchor) button:hover {
    background-color: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
}

/* ══ Sidebar Styling ══ */
[data-testid="stSidebar"], [data-testid="stSidebarContent"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.02) !important;
}

[data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
    color: #475569 !important;
}

/* ══ Sidebar Metric Cards ══ */
[data-testid="stMetric"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    margin-bottom: 12px !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03) !important;
    transition: all 0.2s ease-in-out !important;
}
[data-testid="stMetric"]:hover {
    border-color: #cbd5e1 !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stMetricLabel"] {
    color: #64748b !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] {
    color: #1e3a8a !important;
    font-size: 1.6rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}

/* ══ Sidebar Buttons ══ */
[data-testid="stSidebar"] .stButton > button {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #334155 !important;
    border-radius: 10px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    padding: 9px 14px !important;
    text-align: left !important;
    transition: all 0.18s ease-in-out !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #f1f5f9 !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    transform: translateX(2px) !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.06) !important;
}

/* ══ Suggestion Chips ══ */
.chip-btn > button {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #1e293b !important;
    border-radius: 9999px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
    transition: all 0.2s ease-in-out !important;
}
.chip-btn > button:hover {
    background-color: #eff6ff !important;
    border-color: #3b82f6 !important;
    color: #1d4ed8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 10px rgba(59, 130, 246, 0.12) !important;
}

/* ══ Hero Section ══ */
.hero-title {
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    letter-spacing: -0.03em !important;
    line-height: 1.2 !important;
    margin-bottom: 6px !important;
    margin-top: 0.4rem !important;
}
.hero-subtitle {
    font-size: 0.94rem !important;
    color: #64748b !important;
    margin-bottom: 20px !important;
}

/* ══ Chat Message Cards (Light Theme Enforced) ══ */
[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin-bottom: 14px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
    animation: fadeIn 0.25s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* User Message */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background-color: #f0f7ff !important;
    border: 1px solid #dbeafe !important;
    box-shadow: 0 2px 8px rgba(37, 99, 235, 0.05) !important;
}

/* Assistant Message */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05) !important;
}

/* Avatars */
[data-testid="stChatMessageAvatarUser"] {
    background-color: #3b82f6 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background-color: #2563eb !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}

/* Response Text Styling */
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {
    color: #1e293b !important;
    font-size: 0.94rem !important;
    line-height: 1.65 !important;
}
[data-testid="stChatMessage"] h1, [data-testid="stChatMessage"] h2, [data-testid="stChatMessage"] h3 {
    color: #0f172a !important;
    font-weight: 700 !important;
    margin-top: 14px !important;
    margin-bottom: 8px !important;
}
[data-testid="stChatMessage"] strong {
    color: #0f172a !important;
    font-weight: 700 !important;
    background-color: rgba(59, 130, 246, 0.08);
    padding: 1px 4px;
    border-radius: 4px;
}
[data-testid="stChatMessage"] blockquote {
    border-left: 3px solid #3b82f6 !important;
    background: #f8fafc !important;
    color: #334155 !important;
    padding: 10px 14px !important;
    border-radius: 0 8px 8px 0 !important;
    margin: 10px 0 !important;
}

/* Status Badge */
.resp-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: #3b82f6;
    background-color: #eff6ff;
    border: 1px solid #dbeafe;
    border-radius: 8px;
    padding: 4px 10px;
    margin-bottom: 12px;
    text-transform: uppercase;
}

.live-indicator {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #15803d;
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    padding: 6px 12px;
    border-radius: 9999px;
    margin-bottom: 12px;
}
.live-dot {
    width: 7px;
    height: 7px;
    background-color: #16a34a;
    border-radius: 50%;
    display: inline-block;
}

/* Input Area (Crisp Premium Border & Shadow) */
[data-testid="stChatInputContainer"] {
    background-color: #ffffff !important;
    border: 1.5px solid #94a3b8 !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08) !important;
    transition: all 0.2s ease-in-out !important;
}
[data-testid="stChatInputContainer"]:hover {
    border-color: #64748b !important;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.12) !important;
}
[data-testid="stChatInputContainer"]:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3.5px rgba(37, 99, 235, 0.18), 0 6px 20px rgba(37, 99, 235, 0.10) !important;
}
[data-testid="stChatInput"] textarea {
    color: #0f172a !important;
    font-size: 0.93rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
}

/* Submit Button Icon in Input Box */
[data-testid="stChatInputSubmitButton"] button {
    background-color: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    color: #2563eb !important;
    border-radius: 8px !important;
    transition: all 0.18s ease-in-out !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border-color: #2563eb !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)


# ─── Session State Initialization ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "session_id" not in st.session_state:
    st.session_state.session_id = 1


# ─── Top Header / Sticky Toolbar Component ─────────────────────────────────────
hdr_col1, hdr_col2, hdr_col3, hdr_col4 = st.columns([6, 2.2, 2.2, 1.2])

with hdr_col1:
    st.markdown(
        f"""
        <div class="hdr-anchor" style="display: flex; align-items: center; gap: 8px; height: 36px;">
            <span style="font-weight: 700; color: #0f172a; font-size: 1.05rem; line-height: 1;">Business Intelligence Agent</span>
            <span style="color: #cbd5e1; font-size: 0.9rem; line-height: 1;">/</span>
            <span style="font-weight: 500; color: #64748b; font-size: 0.85rem; line-height: 1;">Session #{st.session_state.session_id}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hdr_col2:
    if st.button("➕ New Chat", use_container_width=True, key="hdr_new_chat"):
        st.session_state.messages = []
        st.session_state.session_id += 1
        st.rerun()

with hdr_col3:
    with st.popover("🗑️ Clear Chat", use_container_width=True):
        st.markdown("<div style='font-size:0.85rem; font-weight:600; color:#0f172a; margin-bottom:6px;'>Clear conversation history?</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.78rem; color:#64748b; margin-bottom:12px;'>This will clear all messages in the current view.</div>", unsafe_allow_html=True)
        if st.button("Confirm Clear", type="primary", use_container_width=True, key="confirm_clear_btn"):
            st.session_state.messages = []
            st.rerun()

with hdr_col4:
    with st.popover("•••", use_container_width=True):
        st.markdown("<div style='font-size:0.82rem; font-weight:700; color:#0f172a; margin-bottom:10px;'>Options</div>", unsafe_allow_html=True)

        if st.session_state.messages:
            chat_text = "# Skylark Drones BI Agent - Conversation Export\n\n"
            for m in st.session_state.messages:
                role = "USER" if m["role"] == "user" else "ASSISTANT"
                chat_text += f"### [{role}]\n{m['content']}\n\n---\n\n"

            st.download_button(
                label="📥 Export Chat (.md)",
                data=chat_text,
                file_name=f"skylark_bi_chat_session_{st.session_state.session_id}.md",
                mime="text/markdown",
                use_container_width=True,
                key="dl_chat_md",
            )
        else:
            st.caption("No chat history to export.")

        st.markdown("<hr style='margin:10px 0;'>", unsafe_allow_html=True)

        with st.expander("ℹ️ About this agent"):
            st.markdown("""
            **Skylark Drones BI Assistant**
            
            Queries live business metrics dynamically from monday.com API v2:
            - **Deals Board**: Revenue, pipeline health, stage breakdown, sectoral values.
            - **Work Orders Board**: Active operations, completed orders, overdue deliverables.
            
            Powered by Google Gemini 3.5 Flash with function calling & data cleaning resilience.

            ---
            **Developer**: Uttam Kalsariya  
            - 🌐 [Portfolio](https://uttam-kalsariya.github.io/uttamkalsariya.github.io/)  
            - 🐙 [GitHub](https://github.com/uttam-kalsariya/)  
            - 💼 [LinkedIn](https://www.linkedin.com/in/uttam-kalsariya/)  
            - 📞 +91 8000651264
            """)


# ─── Board connection status (cached 5 min) ───────────────────────────────────
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

        if not status["boards"] and boards:
            for b in boards:
                b_name_lower = b.get("name", "").lower()
                b_id = str(b["id"])
                if "work" in b_name_lower or "order" in b_name_lower:
                    items = monday_client.get_board_items(b_id)
                    status["boards"]["Work Orders"] = {"id": b_id, "name": b["name"], "count": len(items)}
                elif "deal" in b_name_lower or "funnel" in b_name_lower or "pipe" in b_name_lower:
                    items = monday_client.get_board_items(b_id)
                    status["boards"]["Deals"] = {"id": b_id, "name": b["name"], "count": len(items)}

    except Exception as err:
        status["connected"] = False
        status["error"] = str(err)

    return status


# ─── Sidebar Configuration ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; padding: 6px 0 10px 0;">
        <div style="width: 38px; height: 38px; background-color: #1e3a8a; border-radius: 10px;
                    display: flex; align-items: center; justify-content: center;
                    color: #ffffff; font-weight: 800; font-size: 0.95rem; letter-spacing: 0.05em;
                    box-shadow: 0 2px 8px rgba(30, 58, 138, 0.25);">
            SD
        </div>
        <div>
            <div style="font-size: 1rem; font-weight: 700; color: #0f172a; line-height: 1.15;">Skylark Drones</div>
            <div style="font-size: 0.68rem; font-weight: 600; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2px;">Business Intelligence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 10px 0 18px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size: 0.68rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">
        DATA CONNECTIONS
    </div>
    """, unsafe_allow_html=True)

    conn_info = get_board_connection_status()

    if conn_info["connected"]:
        st.markdown("""
        <div class="live-indicator">
            <span class="live-dot"></span>
            <span>Live — monday.com API v2</span>
        </div>
        """, unsafe_allow_html=True)

        if conn_info["boards"]:
            for board_label, details in conn_info["boards"].items():
                st.metric(
                    label=board_label,
                    value=f"{details['count']} records",
                    help=f"Board: {details['name']} · ID {details['id']}",
                )
        else:
            st.info("No active boards mapped.")
    else:
        st.markdown("""
        <div style="display: inline-flex; align-items: center; gap: 7px; font-size: 0.78rem; font-weight: 600; color: #b91c1c; background: #fef2f2; border: 1px solid #fecaca; padding: 6px 12px; border-radius: 9999px; margin-bottom: 12px;">
            <span style="width: 7px; height: 7px; background-color: #dc2626; border-radius: 50%;"></span>
            <span>Offline — Connection Error</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size: 0.68rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;">
        QUICK PROMPTS
    </div>
    """, unsafe_allow_html=True)

    quick_prompts = [
        "Leadership update",
        "Pipeline by sector",
        "Overdue work orders",
        "Total deal value",
        "Top deals this month",
        "Data quality audit",
    ]

    for label in quick_prompts:
        if st.button(label, use_container_width=True, key=f"qp_{label}"):
            st.session_state["_inject_prompt"] = label
            st.rerun()

    st.markdown("<hr style='margin: 16px 0;'>", unsafe_allow_html=True)

    col_clr, col_ref = st.columns([3, 1])
    with col_clr:
        if st.button("Clear chat", use_container_width=True, key="clear_btn"):
            st.session_state.messages = []
            st.rerun()
    with col_ref:
        if st.button("↻", use_container_width=True, key="refresh_btn", help="Refresh board cache"):
            st.cache_data.clear()
            st.rerun()

    st.markdown("""
    <div style="margin-top: 24px; padding: 12px; background: #f1f5f9; border-radius: 10px; border: 1px solid #e2e8f0; text-align: center;">
        <div style="font-size: 0.65rem; color: #64748b; line-height: 1.6; font-weight: 500;">
            SKYLARK DRONES BI PLATFORM<br/>
            <span style="color: #1e3a8a; font-weight: 600;">monday.com API</span> × <span style="color: #2563eb; font-weight: 600;">Gemini AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─── Main Interface Title Section ──────────────────────────────────────────────
st.markdown("""
<div>
    <div class="hero-title">Business Intelligence Agent</div>
    <div class="hero-subtitle">Query live pipeline metrics, work order statuses, sector performance, or request an executive summary.</div>
</div>
""", unsafe_allow_html=True)

injected = st.session_state.pop("_inject_prompt", None)

# Empty Chat Welcome Screen
if not st.session_state.messages:
    st.markdown("""
    <div style="background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 2rem; box-shadow: 0 2px 10px rgba(0,0,0,0.02); text-align: center;">
        <div style="width: 48px; height: 48px; background-color: #eff6ff; border: 1px solid #dbeafe; border-radius: 12px; margin: 0 auto 16px auto; display: flex; align-items: center; justify-content: center; color: #2563eb; font-weight: 700; font-size: 1.1rem;">
            SD
        </div>
        <div style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 8px;">
            Welcome to Skylark Drones BI Assistant
        </div>
        <div style="font-size: 0.88rem; color: #64748b; max-width: 460px; margin: 0 auto 20px auto; line-height: 1.6;">
            Ask questions in plain English to dynamically retrieve real-time analytics from your monday.com Work Orders and Deals boards.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.78rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;'>Suggested Queries</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='chip-btn'>", unsafe_allow_html=True)
        if st.button("Give me a leadership update", key="chip1", use_container_width=True):
            st.session_state["_inject_prompt"] = "Give me a leadership update"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='chip-btn'>", unsafe_allow_html=True)
        if st.button("Which work orders are overdue?", key="chip2", use_container_width=True):
            st.session_state["_inject_prompt"] = "Which work orders are overdue?"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='chip-btn'>", unsafe_allow_html=True)
        if st.button("What is our total deal value by sector?", key="chip3", use_container_width=True):
            st.session_state["_inject_prompt"] = "What is our total deal value by sector?"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ─── Render Conversation History ──────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and message.get("badge"):
            st.markdown(f'<div class="resp-badge">⚡ LIVE DATA · {message["badge"]}</div>', unsafe_allow_html=True)
        st.markdown(message["content"])

prompt = st.chat_input("Ask a BI question...") or injected

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(
            '<div style="color: #64748b; font-size: 0.85rem; padding: 6px 0; font-weight: 500;">Retrieving and processing live monday.com metrics...</div>',
            unsafe_allow_html=True,
        )

        try:
            t0 = time.time()
            history_for_agent = st.session_state.messages[:-1]
            response_text = agent.run_agent(
                user_message=prompt,
                conversation_history=history_for_agent,
            )
            elapsed = round(time.time() - t0, 1)
            st.session_state.query_count += 1

            thinking_placeholder.empty()

            badge = f"{elapsed}s · Query #{st.session_state.query_count}"
            st.markdown(f'<div class="resp-badge">⚡ LIVE DATA · {badge}</div>', unsafe_allow_html=True)
            st.markdown(response_text)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "badge": badge,
            })

        except Exception as e:
            thinking_placeholder.empty()
            st.error(f"Execution Error: {e}")
