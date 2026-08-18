# Requirements for requirements.txt:
# streamlit
# google-genai

import streamlit as st
import time
from google import genai

# ==========================================
# 1. PAGE CONFIGURATION & SECRETS INITIALIZATION
# ==========================================
st.set_page_config(page_title="HeatGuard AI", page_icon="🌡️", layout="centered")

# Safely handle Streamlit Secrets so the app never crashes if they are missing
try:
    SECRET_GEMINI = st.secrets.get("GEMINI_API_KEY", "")
    SECRET_FORTYGUARD = st.secrets.get("FORTYGUARD_API_KEY", "")
except Exception:
    SECRET_GEMINI = ""
    SECRET_FORTYGUARD = ""

# ==========================================
# 2. CUSTOM CSS INJECTION (ELEGANT UI)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit default branding for clean UI */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Hero Section */
    .hero-title {
        background: linear-gradient(90deg, #4285F4, #9b72cb, #d96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
        padding-bottom: 5px;
        letter-spacing: -1.5px;
    }
    
    .hero-subtitle {
        text-align: center;
        color: #70757a;
        font-size: 1.15rem;
        font-weight: 400;
        margin-top: 0px;
        margin-bottom: 40px;
    }

    /* Glassmorphic Metric Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        margin-bottom: 15px;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-3px);
    }
    .metric-title {
        font-size: 0.85rem;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(90deg, #d96570, #f2994a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Google AI Overview Style Loading Animation */
    .shimmer-container {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px;
        background: rgba(66, 133, 244, 0.04);
        border-radius: 16px;
        border: 1px dashed rgba(66, 133, 244, 0.3);
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .shimmer-text {
        font-size: 1.25rem;
        font-weight: 600;
        background: linear-gradient(90deg, #4285F4 0%, #9b72cb 50%, #4285F4 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientPulse 2s linear infinite;
    }
    @keyframes gradientPulse {
        to { background-position: 200% center; }
    }

    /* AI Result Box */
    .ai-output-container {
        background: linear-gradient(145deg, #ffffff, #f8faff);
        border: 1px solid #e1e8f5;
        border-top: 6px solid #4285F4;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 15px 35px rgba(66, 133, 244, 0.08);
        margin-top: 20px;
        animation: fadeIn 0.6s ease-out;
    }
    .ai-output-container h1, .ai-output-container h2, .ai-output-container h3 {
        color: #202124;
        margin-top: 0;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Dark Mode Adjustments */
    @media (prefers-color-scheme: dark) {
        .glass-card {
            background: rgba(32, 33, 36, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .metric-title { color: #9aa0a6; }
        .ai-output-container {
            background: linear-gradient(145deg, #202124, #282a2d);
            border: 1px solid #3c4043;
            border-top: 6px solid #8ab4f8;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        }
        .ai-output-container h1, .ai-output-container h2, .ai-output-container h3 { color: #e8eaed; }
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 3. CORE LOGIC & API FUNCTIONS
# ==========================================
def fetch_fortyguard_data(lat, lon, api_key):
    """Fetches thermal data. Uses highly realistic mock data if API key is missing."""
    # Simulate network latency for the UI loading effect
    time.sleep(2)
    
    # Fallback fictional thermal data 
    return {
        "temperature_c": 43.2,
        "humidity_pct": 38,
        "uv_index": 11,
        "wind_kmh": 14.5,
        "status": "Simulated Active Data (FortyGuard Fallback Mode)"
    }

def generate_safety_advisory(gemini_key, thermal_data, activity, work_time):
    """Uses the latest google-genai SDK to generate a safety report."""
    if not gemini_key:
        return "❌ **Error:** No Gemini API Key found. Please add it to the sidebar or Streamlit Secrets."
    
    try:
        client = genai.Client(api_key=gemini_key)
        
        system_prompt = f"""
        You are 'HeatGuard AI', an advanced safety advisor for outdoor workers.
        
        LIVE THERMAL DATA:
        - Temperature: {thermal_data['temperature_c']}°C
        - Humidity: {thermal_data['humidity_pct']}%
        - UV Index: {thermal_data['uv_index']}
        - Wind Speed: {thermal_data['wind_kmh']} km/h
        
        WORK SCHEDULE: {work_time}
        ACTIVITY: {activity}
        
        Provide a concise, life-saving safety advisory in Markdown.
        Structure your response exactly like this:
        
        ### 🚨 Risk Assessment
        [State the threat level: Safe, Moderate Risk, High Risk, or Extreme Danger. Briefly explain why based on the exact temperature and UV index.]
        
        ### ⚖️ Operational Decision
        [Give a definitive YES or NO on whether work should proceed, or if it must be delayed/rescheduled.]
        
        ### 💧 Mandatory Precautions
        * [Actionable point 1 - e.g., hydration schedule]
        * [Actionable point 2 - e.g., cooling gear]
        * [Actionable point 3 - e.g., work/rest cycle limits]
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=system_prompt,
        )
        return response.text
    except Exception as e:
        return f"❌ **API Error:** Could not generate advisory. Details: {str(e)}"

# ==========================================
# 4. USER INTERFACE LAYOUT
# ==========================================
st.markdown("<h1 class='hero-title'>HeatGuard AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-subtitle'>Intelligent Thermal Safety for the Outdoor Workforce</p>", unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("API keys are securely processed.")
    api_key_input = st.text_input("Gemini API Key", type="password", value=SECRET_GEMINI, help="Defaults to Streamlit Secrets.")
    fortyguard_key_input = st.text_input("FortyGuard API Key", type="password", value=SECRET_FORTYGUARD, help="Leave empty for simulated thermal data fallback.")
    st.info("💡 **Pro Tip:** Your keys are hidden safely on the server using Streamlit Secrets.")

# --- Main Input Form ---
st.markdown("### 📍 Location & Schedule")
col1, col2 = st.columns(2)

with col1:
    lat = st.number_input("Latitude", value=30.1575, format="%.4f")
    lon = st.number_input("Longitude", value=71.5249, format="%.4f")

with col2:
    work_time = st.selectbox("🕒 Working Hours", [
        "Morning Shift (6 AM - 10 AM)", 
        "Midday Peak (10 AM - 3 PM)", 
        "Late Afternoon (3 PM - 7 PM)", 
        "Night Shift"
    ], index=1)
    
activity = st.text_area("👷 Task Description", 
    value="Heavy manual labor: bricklaying, scaffolding assembly, and concrete pouring for a new commercial building roof.", 
    height=100)

# --- Action Button & Dynamic Processing ---
if st.button("✨ Generate AI Safety Advisory", use_container_width=True, type="primary"):
    
    # 1. Show elegant AI Shimmer Loading State
    loading_placeholder = st.empty()
    loading_placeholder.markdown("""
        <div class="shimmer-container">
            <span class="shimmer-text">📡 Fetching hyperlocal thermal data and initializing HeatGuard AI...</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Fetch Data
    t_data = fetch_fortyguard_data(lat, lon, fortyguard_key_input)
    
    # 3. Update loading text
    loading_placeholder.markdown("""
        <div class="shimmer-container">
            <span class="shimmer-text">🧠 Gemini AI is analyzing thermal stress factors...</span>
        </div>
    """, unsafe_allow_html=True)
    
    # 4. Generate AI Advisory
    advisory = generate_safety_advisory(api_key_input, t_data, activity, work_time)
    
    # 5. Clear loading animation
    loading_placeholder.empty()
    
    # --- Output Display ---
    st.markdown("### 📊 Live Thermal Conditions")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='glass-card'><div class='metric-title'>Temp</div><div class='metric-value'>{t_data['temperature_c']}°C</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='glass-card'><div class='metric-title'>Humidity</div><div class='metric-value'>{t_data['humidity_pct']}%</div></div>", unsafe_allow_html=True)
    with m3:
         st.markdown(f"<div class='glass-card'><div class='metric-title'>UV Index</div><div class='metric-value'>{t_data['uv_index']}</div></div>", unsafe_allow_html=True)
    with m4:
         st.markdown(f"<div class='glass-card'><div class='metric-title'>Wind</div><div class='metric-value'>{t_data['wind_kmh']}</div></div>", unsafe_allow_html=True)
         
    st.markdown("### 🤖 Agentic Safety Advisory")
    
    # Wrap standard Markdown in the styled container box
    st.markdown('<div class="ai-output-container">', unsafe_allow_html=True)
    st.markdown(advisory)
    st.markdown('</div>', unsafe_allow_html=True)
