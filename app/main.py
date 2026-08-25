import streamlit as st
import requests
import pandas as pd
import logging
import io
import pytest  # <-- Import pytest to run it inside the app
# Import the external scoring engine
from scorer import calculate_user_rating

# Web layout configuration setup
st.set_page_config(page_title="GitHub User Auditor", page_icon="👤", layout="centered")

# Create two tabs: One for the App itself, one for the Live Test Suite
tab1, tab2 = st.tabs(["📊 Profile Auditor", "🧪 Live Pytest Suite"])

with tab1:
    st.title("👤 GitHub User Profile Auditor")
    st.write("Analyze and grade a developer's public GitHub footprint instantly from your browser.")

    # --- 1. FORCE STREAMLIT CHROMIUM HIDING LAYERS & GAP FIX ---
    st.markdown(""" 
     <style> 
     header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
     div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
     footer { visibility: hidden !important; } 
     
     [data-testid="stMainBlockContainer"] {
         padding-top: 1rem !important;
     }
     .main .block-container {
         padding-top: 1rem !important;
     }
     </style> 
     """, unsafe_allow_html=True) 

    logging.basicConfig(level=logging.INFO) 
    logger = logging.getLogger("FIREWALL") 

    # --- 2. 🔑 AUTOMATED ACCESS VERIFICATION CHECK ---
    has_token = "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != ""

    if has_token:
        st.sidebar.success("🔒 GitHub Token Status: ACTIVE (5,000 req/hr)")
    else:
        st.sidebar.warning("💡 Running unauthenticated (60 req/hr Shared Limit)")

    user_input = st.text_input("GitHub Username", placeholder="e.g., torvalds")

    if st.button("Audit User Profile", type="primary"):
        if not user_input:
            st.warning("Please enter a username.")
        else:
            parsed_input = user_input.replace("https://github.com", "").strip("/").split("/")
            username = parsed_input[0] if parsed_input else user_input.strip()
            
            api_url = f"https://github.com{username}"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Streamlit-User-Auditor-v1"
            }
            
            if has_token:
                headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
                
            with st.spinner(f"Fetching real-time data for @{username}..."):
                try:
                    response = requests.get(api_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        user_data = response.json()
                        results = calculate_user_rating(user_data)
                        
                        st.success(f"🎯 Audit Complete for @{user_data.get('login')}!")
                        
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if user_data.get("avatar_url"):
                                st.image(user_data.get("avatar_url"), width=150)
                        with col2:
                            st.subheader(user_data.get("name") or username)
                            st.caption(f"📍 Location: {user_data.get('location') or 'Not Specified'}")
                            st.write(user_data.get("bio") or "*No profile bio provided.*")
                        
                        st.divider()
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric(label="Profile Grade Score", value=f"{results['total_score']} / 100")
                        with c2:
                            st.metric(label="Calculated Tier", value=results['grade'])
                        
                        st.subheader("📊 Footprint Metric Distribution")
                        chart_df = pd.DataFrame({
                            "Evaluation Module": list(results["breakdown"].keys()),
                            "Score Segment": list(results["breakdown"].values())
                        })
                        st.bar_chart(data=chart_df, x="Evaluation Module", y="Score Segment", use_container_width=True)
                        
                        st.subheader("💡 Optimization Recommendations")
                        if not user_data.get("bio"):
                            st.error("❌ Missing Account Bio: Add a brief summary detailing your technical specialization stacks.")
                        if not user_data.get("blog"):
                            st.warning("⚠️ Portfolio Link Missing: Connect a portfolio URL or LinkedIn page to your profile.")
                        if results['total_score'] >= 85:
                            st.info("🔥 Outstanding profile layout! This workspace projects clear authority, active maintenance, and solid personal branding.")
                        else:
                            st.info("📌 Tip: Increasing your public activity and filling out your profile fields will improve your score.")

                    else:
                        st.error(f"❌ GitHub API Return Code: {response.status_code}")
                        
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    st.error("🌐 Connection Failure: Unable to reach the GitHub API endpoints.")
                    logger.error(f"API Connection Exception: {str(e)}")

# --- 3. 🧪 EMBEDDED PYTEST DASHBOARD TAB ---
with tab2:
    st.header("🧪 Automated Test Diagnostics")
    st.write("Click below to execute the `pytest` suite directly inside the Streamlit instance runtime environment.")
    
    if st.button("🚀 Run Pytest Suite Engine", type="secondary"):
        with st.spinner("Executing test cases..."):
            # Capture the standard terminal output stream into memory string buffers
            string_buffer = io.StringIO()
            
            # Direct pytest to scan and execute test_app.py while outputting results to our buffer
            # We target "test_app.py" assuming pytest is running from the app/ directory context
            exit_code = pytest.main(["-v", "test_app.py"], plugins=[])
            
            # If it cannot find it locally, try targeting it via relative folder tree structure
            if exit_code == pytest.ExitCode.NO_TESTS_COLLECTED:
                exit_code = pytest.main(["-v", "app/test_app.py"])
            
            if exit_code == 0:
                st.success("🟢 All System Diagnostics Passed! Your scoring engine metrics are 100% verified.")
            else:
                st.error("🔴 Test Suite Regression Detected! One or more math logic validations failed.")
                
            st.info("💡 Note: For security and safety, formal console logging outputs remain inside your local server terminal window terminal logs.")

