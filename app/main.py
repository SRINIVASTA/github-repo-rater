import streamlit as st
import requests
import pandas as pd
from scorer import calculate_rating

# Web configuration properties
st.set_page_config(page_title="GitHub Repo Rater", page_icon="📊", layout="centered")

st.title("📊 GitHub Repository Rater")
st.write("Analyze and evaluate repository health instantly from your browser.")

# --- 🔑 SECRET TOKEN DIAGNOSTIC CHECK ---
if "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != "":
    st.sidebar.success("🔒 GitHub Authentication Token: ACTIVE")
    raw_token = st.secrets["GITHUB_TOKEN"].strip()
    masked_token = raw_token[:4] + "..." + raw_token[-4:] if len(raw_token) > 8 else "INVALID"
    st.sidebar.caption(f"Loaded Token structure: `{masked_token}`")
else:
    st.sidebar.error("⚠️ GitHub Authentication Token: MISSING")
    st.sidebar.info("Add: `GITHUB_TOKEN = \"your_token\"` to Streamlit Cloud Secrets.")

# Interactive text box
repo_input = st.text_input("Repository Path", placeholder="e.g., srinivasta/vizag-smart-health-app")

if st.button("Run Analytics Engine", type="primary"):
    if not repo_input:
        st.warning("Please enter a valid path.")
    else:
        # Standardize, lower-case, and cleanup user string input fields
        repo_path = repo_input.replace("https://github.com/", "").strip("/").lower()
        
        if "/" not in repo_path:
            st.error("⚠️ Invalid format! Use 'username/repository-name'.")
        else:
            api_url = f"https://github.com{repo_path}"
            
            # Setup modern enterprise headers
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Streamlit-Repo-Rater-App-v2"
            }
            
            # MODERN AUTH CORRECTION: Swapped 'token' prefix with 'Bearer' 
            if "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"].strip() != "":
                headers["Authorization"] = f"Bearer {st.secrets['GITHUB_TOKEN'].strip()}"
            
            with st.spinner("Processing API data metrics..."):
                try:
                    response = requests.get(api_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        repo_data = response.json()
                        results = calculate_rating(repo_data)
                        
                        st.success(f"Analysis Complete for {repo_data.get('full_name')}!")
                        
                        # Render Numeric Metrics
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric(label="Overall Score", value=f"{results['total_score']} / 100")
                        with c2:
                            st.metric(label="Calculated Grade", value=results['grade'])
                        
                        # Graph Display
                        chart_df = pd.DataFrame({
                            "Metric Section": list(results["breakdown"].keys()),
                            "Assigned Weight": list(results["breakdown"].values())
                        })
                        st.bar_chart(data=chart_df, x="Metric Section", y="Assigned Weight", use_container_width=True)
                        
                        # Audit insights
                        st.subheader("💡 Rater Audit Insights")
                        if results['grade'] in ["A+", "A"]:
                            st.info("🔥 This repository is highly optimized, active, and exhibits phenomenal open-source health standards.")
                        elif results['grade'] == "B":
                            st.warning("⚠️ Good project framework, but could use more community activity or an updated description.")
                        else:
                            st.error("🚨 Critical maintenance needed. Check if this repository has open issues running wild or missing core README files.")
                        
                    else:
                        # 🔍 CLEAR DEBUG ERROR PANEL
                        st.error(f"❌ GitHub API Error! Server Response Code: {response.status_code}")
                        if response.status_code == 401:
                            st.info("💡 **Reason (Bad Credentials):** The token you pasted inside Streamlit Secrets is invalid, has a typo, or was revoked. Generate a fresh token on GitHub.")
                        elif response.status_code == 403:
                            st.info("💡 **Reason (Rate Limited/Forbidden):** If your token is loaded, this means it lacks the `public_repo` scope checkbox. Edit your token on GitHub and check that box.")
                        elif response.status_code == 404:
                            st.info(f"💡 **Reason (Not Found):** The repository path `{repo_path}` doesn't match a public project. Check for trailing typos.")
                        
                except requests.exceptions.Timeout:
                    st.error("⏳ Connection timed out!")
                except requests.exceptions.ConnectionError:
                    st.error("🌐 Hard infrastructure network block encountered between server nodes.")
                except Exception as e:
                    st.error(f"Unexpected operational loop failure: {str(e)}")
