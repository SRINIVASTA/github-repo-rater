import streamlit as st
import requests
import pandas as pd
from scorer import calculate_user_rating  # <-- Correct clean local import

st.set_page_config(page_title="GitHub User Auditor", page_icon="👤", layout="centered")
st.title("👤 GitHub User Profile Auditor")
st.write("Analyze and grade a developer's public GitHub footprint instantly from your browser.")

# Force Streamlit layer UI gap hiding fixes
st.markdown(""" 
 <style> 
 header[data-testid="stHeader"] { visibility: hidden !important; display: none !important; } 
 div[data-testid="stToolbar"] { visibility: hidden !important; display: none !important; } 
 footer { visibility: hidden !important; } 
 [data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }
 </style> 
 """, unsafe_allow_html=True) 

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
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "Streamlit-User-Auditor-v1"}
        if has_token:
            headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
            
        with st.spinner(f"Fetching real-time data for @{username}..."):
            try:
                response = requests.get(api_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    results = calculate_user_rating(user_data)
                    
                    st.success(f"🎯 Audit Complete for @{user_data.get('login')}!")
                    col1, col2 = st.columns()
                    with col1:
                        if user_data.get("avatar_url"):
                            st.image(user_data.get("avatar_url"), width=150)
                    with col2:
                        st.subheader(user_data.get("name") or username)
                        st.caption(f"📍 Location: {user_data.get('location') or 'Not Specified'}")
                        st.write(user_data.get("bio") or "*No profile bio provided.*")
                    
                    st.divider()
                    c1, c2 = st.columns(2)
                    with c1: st.metric(label="Profile Grade Score", value=f"{results['total_score']} / 100")
                    with c2: st.metric(label="Calculated Tier Grade", value=results['grade'])
                    
                    # Renders bar chart using your custom exact dictionary keys
                    chart_df = pd.DataFrame({
                        "Evaluation Module": list(results["breakdown"].keys()),
                        "Score Segment": list(results["breakdown"].values())
                    })
                    st.bar_chart(data=chart_df, x="Evaluation Module", y="Score Segment", use_container_width=True)
                else:
                    st.error(f"❌ GitHub API Error Code: {response.status_code}")
                    if response.status_code == 404: st.info("💡 Username does not match an active user account.")
                    elif response.status_code == 403: st.warning("💡 API Rate Limit Reached.")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                st.error("🌐 Connection Failure: Unable to reach the GitHub API endpoints.")
