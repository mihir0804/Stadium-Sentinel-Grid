import os
import sys
import json
import streamlit as st
from datetime import datetime

# Ensure the backend can be imported cleanly regardless of execution directory
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
    /* Global App Background */
    .stApp {
        background-color: #050510;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,0.2) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,0.2) 0, transparent 50%);
        color: #e0e6ed;
    }

    /* Glassmorphic Containers */
    .glass-container {
        background: rgba(20, 25, 35, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 242, 254, 0.2);
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 242, 254, 0.05);
        min-height: 80vh;
    }

    /* High-contrast Structural Header */
    .main-header {
        font-family: 'Courier New', Courier, monospace;
        font-weight: 800;
        font-size: 2.2rem;
        color: #00f2fe;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 0 0 12px rgba(0, 242, 254, 0.8);
        border-bottom: 2px solid #00f2fe;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }

    /* Column Titles */
    .col-header {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 25px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Colors and Indicators */
    .text-cyan { color: #00f2fe; text-shadow: 0 0 8px rgba(0,242,254,0.6); }
    .text-emerald { color: #00ff87; text-shadow: 0 0 8px rgba(0,255,135,0.6); }
    .text-warning { color: #ff3366; text-shadow: 0 0 8px rgba(255,51,102,0.6); }
    .text-orange { color: #ff9900; text-shadow: 0 0 8px rgba(255,153,0,0.6); }
    
    /* Text Inputs and Text Areas Styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(10, 15, 25, 0.6) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #00f2fe !important;
        box-shadow: 0 0 8px rgba(0,242,254,0.4) !important;
    }

    /* Hide Streamlit default components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "staff_logs" not in st.session_state:
    st.session_state.staff_logs = []

if "fan_chat" not in st.session_state:
    st.session_state.fan_chat = []

# ---------------------------------------------------------
# App Header Layout
# ---------------------------------------------------------
st.markdown('<div class="main-header">STADIUM SENTINEL COMMAND GRID — FIFA WORLD CUP 2026</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Dual Column Grid Layout
# ---------------------------------------------------------
col1, col2 = st.columns(2, gap="large")

# =========================================================
# COLUMN 1: Operations Control Center (SOC)
# =========================================================
with col1:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.markdown('<div class="col-header"><span class="text-cyan">⚙️ Operations Control Center (SOC)</span></div>', unsafe_allow_html=True)
    
    # Live Telemetry Block
    st.subheader("Live Telemetry Injection")
    default_telemetry = '''{
  "gate_alpha_density": "85%",
  "transit_line_status": "delayed",
  "temperature": "32C",
  "active_incidents": 1
}'''
    telemetry_input = st.text_area("JSON Telemetry Payload", value=default_telemetry, height=140)
    
    # SOC Query
    st.subheader("SOC Incident Query")
    staff_query = st.text_input("Enter operational scenario or ground report:", placeholder="e.g., Gate A is overcrowded and medical is delayed.")
    
    if st.button("Execute SOC Analysis ⚡", type="primary", use_container_width=True):
        if staff_query:
            try:
                telemetry_dict = json.loads(telemetry_input)
            except json.JSONDecodeError:
                st.error("Invalid JSON telemetry payload. Proceeding without telemetry...")
                telemetry_dict = None
                
            with st.spinner("Analyzing operational parameters and telemetry matrices..."):
                response = route_stadium_query(
                    user_query=staff_query, 
                    user_role="staff", 
                    telemetry=telemetry_dict
                )
                
                # Append to session logs
                timestamp = datetime.now().strftime("%H:%M:%S")
                st.session_state.staff_logs.insert(0, {"time": timestamp, "query": staff_query, "response": response})
                
    st.markdown("---")
    st.subheader("Terminal Logs (Recent First)")
    
    # Render Staff Terminal Logs
    for log in st.session_state.staff_logs:
        with st.expander(f"[{log['time']}] >> {log['query']}", expanded=True):
            resp = log['response']
            if isinstance(resp, dict) and "risk_level" in resp:
                # Dynamic Risk Level formatting
                risk = resp.get("risk_level", "Unknown")
                color_class = "text-warning" if risk == "High" else "text-orange" if risk == "Medium" else "text-emerald"
                
                st.markdown(f"**Risk Level:** <span class='{color_class}'>[{risk.upper()}]</span>", unsafe_allow_html=True)
                
                # Zonal Impact
                zones = resp.get("affected_zones", [])
                st.markdown(f"**Affected Zones:** `{', '.join(zones)}`")
                
                # Action Protocol
                st.markdown("**Action Protocol:**")
                st.info(resp.get("action_protocol", "No protocol provided."))
            else:
                # Fallback for raw string or error outputs
                st.code(json.dumps(resp, indent=2) if isinstance(resp, dict) else resp, language="json")
                
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# COLUMN 2: Inclusive Fan Experience & Mobility Hub
# =========================================================
with col2:
    st.markdown('<div class="glass-container">', unsafe_allow_html=True)
    st.markdown('<div class="col-header"><span class="text-emerald">♿ Inclusive Fan Experience & Mobility Hub</span></div>', unsafe_allow_html=True)
    
    # Fan Locale / Language Context
    language = st.selectbox(
        "Preferred Response Locale / Language",
        ["English", "Spanish", "French", "German", "Arabic", "Mandarin", "Portuguese"]
    )
    
    st.markdown("---")
    
    # Chat UI Container mapping to st.session_state for persistence
    chat_container = st.container(height=450)
    
    with chat_container:
        if not st.session_state.fan_chat:
            st.markdown("*<span class='text-cyan'>[SYSTEM] Awaiting incoming fan network requests...</span>*", unsafe_allow_html=True)
        
        for msg in st.session_state.fan_chat:
            if msg["role"] == "user":
                st.markdown(f"👤 **Fan Request:** {msg['content']}")
            else:
                st.markdown(f"🤖 **<span class='text-emerald'>Accessibility Agent:</span>** {msg['content']}", unsafe_allow_html=True)
                st.markdown("---")
                
    # Incoming Fan Query Trigger
    fan_query = st.chat_input("Enter fan navigation, assistance, or routing request...")
    if fan_query:
        # Append User Message and Re-render immediately
        st.session_state.fan_chat.append({"role": "user", "content": fan_query})
        
        with st.spinner("Routing intent via accessibility sub-graph..."):
            response = route_stadium_query(
                user_query=fan_query,
                user_role="fan",
                language=language
            )
            
            # Append Agent Response
            st.session_state.fan_chat.append({"role": "assistant", "content": response})
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
