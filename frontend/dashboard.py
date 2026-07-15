import os
import sys
import json
import streamlit as st
from datetime import datetime

# Ensure the backend can be imported cleanly
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.agent_orchestrator import route_stadium_query

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Stadium Sentinel Command Grid",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Custom CSS for Premium Cyberpunk/Glassmorphic Aesthetic
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #050510; color: #e0e6ed; }
    .main-header {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 800; font-size: 2.2rem; color: #00f2fe;
        text-transform: uppercase; letter-spacing: 2px;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.8);
        border-bottom: 2px solid #00f2fe; padding-bottom: 10px; margin-bottom: 30px;
    }
    .col-header { font-size: 1.4rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
    .text-cyan { color: #00f2fe; }
    .text-emerald { color: #00ff87; }
    .text-warning { color: #ff3366; }
    .text-orange { color: #ff9900; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(10, 15, 25, 0.6) !important; color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State
# ---------------------------------------------------------
if "staff_logs" not in st.session_state: st.session_state.staff_logs = []
if "fan_chat" not in st.session_state: st.session_state.fan_chat = []

# ---------------------------------------------------------
# Layout
# ---------------------------------------------------------
st.markdown('<div class="main-header">STADIUM SENTINEL COMMAND GRID — FIFA WORLD CUP 2026</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

# =========================================================
# COLUMN 1: Operations Control Center (SOC)
# =========================================================
with col1:
    with st.container(border=True): # EXECUTIVE BORDERED CONTAINER
        st.markdown('<div class="col-header"><span class="text-cyan">⚙️ Operations Control Center (SOC)</span></div>', unsafe_allow_html=True)
        st.metric(label="System Integrity", value="ONLINE", delta="100% Operational")
        
        st.subheader("Live Telemetry Injection")
        telemetry_input = st.text_area("JSON Telemetry Payload", value='''{"gate_alpha_density": "85%", "active_incidents": 1}''', height=100)
        
        st.subheader("SOC Incident Query")
        staff_query = st.text_input("Enter ground report:", placeholder="e.g., Gate A is overcrowded.")
        
        if st.button("Execute SOC Analysis ⚡", type="primary", use_container_width=True):
            if staff_query:
                with st.spinner("Analyzing operational parameters..."):
                    # Parse telemetry safely
                    try:
                        telemetry_dict = json.loads(telemetry_input)
                    except:
                        telemetry_dict = {}
                    
                    response = route_stadium_query(user_query=staff_query, user_role="staff", telemetry=telemetry_dict)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    st.session_state.staff_logs.insert(0, {"time": timestamp, "query": staff_query, "response": response})

        st.subheader("Terminal Logs")
        for log in st.session_state.staff_logs:
            with st.expander(f"[{log['time']}] >> {log['query']}", expanded=True):
                resp = log['response']
                
                # Check if the response contains structured keys
                if isinstance(resp, dict) and "action_protocol" in resp:
                    # Risk Level Styling
                    risk = resp.get("risk_level", "Unknown")
                    # Assign color based on risk
                    color_class = "text-warning" if risk.lower() == "high" else "text-orange" if risk.lower() == "medium" else "text-emerald"
                    
                    st.markdown(f"**Risk Level:** <span class='{color_class}'>[{risk.upper()}]</span>", unsafe_allow_html=True)
                    st.markdown(f"**Affected Zones:** `{', '.join(resp.get('affected_zones', []))}`")
                    st.markdown("**Action Protocol:**")
                    st.info(resp.get("action_protocol", "No protocol provided."))
                else:
                    # Fallback for raw text
                    st.write(str(resp))

# =========================================================
# COLUMN 2: Inclusive Fan Experience & Mobility Hub
# =========================================================
with col2:
    with st.container(border=True): # EXECUTIVE BORDERED CONTAINER
        st.markdown('<div class="col-header"><span class="text-emerald">♿ Inclusive Fan Experience & Mobility Hub</span></div>', unsafe_allow_html=True)
        st.metric(label="Agent Mode", value="ACTIVE", delta="Ready for Requests")
        
        language = st.selectbox("Preferred Response Locale / Language", ["English", "Spanish", "German", "French"])
        
        chat_container = st.container(height=450)
        with chat_container:
            if not st.session_state.fan_chat: st.info("[SYSTEM] Agent standing by for fan requests...")
            for msg in st.session_state.fan_chat:
                if msg["role"] == "user": st.markdown(f"👤 **Fan:** {msg['content']}")
                else: st.markdown(f"🤖 **Accessibility Agent:** {msg['content']}")
        
        fan_query = st.chat_input("Enter fan navigation or assistance request...")
        if fan_query:
            st.session_state.fan_chat.append({"role": "user", "content": fan_query})
            with st.spinner("Routing intent via accessibility sub-graph..."):
                response = route_stadium_query(user_query=fan_query, user_role="fan", language=language)
                st.session_state.fan_chat.append({"role": "assistant", "content": response})
                st.rerun()
