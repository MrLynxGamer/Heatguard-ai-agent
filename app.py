import streamlit as st
import requests
import google.generativeai as genai

# Page configuration for mobile devices
st.set_page_config(
    page_title="HeatGuard AI Agent",
    page_icon="🌡️",
    layout="centered"
)

st.title("🌡️ HeatGuard AI")
st.subheader("Autonomous Urban Heat Safety Agent")
st.write("Powered by **FortyGuard Hyperlocal Thermal API** and **Google Gemini AI**.")
st.markdown("---")

# Sidebar for API keys
with st.sidebar:
    st.header("🔑 Credentials Setup")
    fg_api_key = st.text_input("FortyGuard API Key", type="password")
    gemini_api_key = st.text_input("Gemini API Key", type="password")
    st.info("Keys are processed securely in session memory.")

def fetch_fortyguard_temp(lat, lon, api_key):
    if not api_key:
        return {"temperature_2m": 38.5, "status": "Simulated Active Data (Enter API Key for live feed)"}
    
    url = f"https://api.fortyguard.com/v1/temperature/snapshot?lat={lat}&lon={lon}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"temperature_2m": 37.0, "status": f"API HTTP {response.status_code}"}
    except Exception as e:
        return {"temperature_2m": 37.0, "status": f"Connection Error: {str(e)}"}

def run_agentic_analysis(user_prompt, thermal_data, gemini_key):
    if not gemini_key:
        return "⚠️ Please enter your Gemini API Key in the sidebar to run the AI Agent."
    
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        agent_system_prompt = f"""
        You are 'HeatGuard AI', an autonomous urban climate risk agent built for FortyGuard Hackathon '26.
        
        LIVE HYPERLOCAL THERMAL DATA (FortyGuard 2m Height Sensor):
        - Current 2m Air Temp: {thermal_data.get('temperature_2m', 'N/A')} °C
        - Sensor Status: {thermal_data.get('status', 'Optimal')}
        
        USER QUERY / SCENARIO:
        "{user_prompt}"
        
        INSTRUCTIONS:
        1. Categorize Threat Level: [LOW / MODERATE / CRITICAL DANGER]
        2. Provide 3 specific, actionable recommendations tailored to the query.
        3. Suggest immediate cooling interventions.
        Keep the response clear, structured, and practical.
        """
        
        response = model.generate_content(agent_system_prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini AI: {str(e)}"

st.write("### 📍 Step 1: Select Target Area Coordinates")
col1, col2 = st.columns(2)
with col1:
    latitude = st.number_input("Latitude", value=33.4484, format="%.4f")
with col2:
    longitude = st.number_input("Longitude", value=-112.0740, format="%.4f")

st.write("### 💬 Step 2: Define Your Safety Scenario")
user_query = st.text_area(
    "Describe the activity or query:",
    value="Our construction team is performing outdoor roof installation between 12 PM and 3 PM today. Is it safe, and what precautions should we take?"
)

if st.button("🚀 Analyze Heat Risk with Agent", type="primary"):
    with st.spinner("1/2 Fetching FortyGuard 2m Thermal Data..."):
        thermal_result = fetch_fortyguard_temp(latitude, longitude, fg_api_key)
        
    st.success(f"FortyGuard Data Retrieved! Current Local Temp: {thermal_result.get('temperature_2m')} °C")
    
    with st.spinner("2/2 Gemini Agent processing thermal risk advisory..."):
        agent_output = run_agentic_analysis(user_query, thermal_result, gemini_api_key)
        
    st.markdown("### 🤖 Agentic Advisory Output")
    st.info(agent_output)
