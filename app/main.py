import streamlit as st
import requests
import pandas as pd
from scorer import calculate_rating

# Web configuration properties
st.set_page_config(page_title="GitHub Repo Rater", page_icon="📊", layout="centered")

st.title("📊 GitHub Repository Rater")
st.write("Analyze and evaluate repository health instantly from your browser.")

# Interactive text box
repo_input = st.text_input("Repository Path", placeholder="e.g., srinivasta/ai-portfolio-engine")

if st.button("Run Analytics Engine", type="primary"):
    if not repo_input:
        st.warning("Please enter a valid path.")
    else:
        # Format strings to extract exact repo addresses
        repo_path = repo_input.replace("https://github.com", "").strip("/")
        
        if "/" not in repo_path:
            st.error("⚠️ Invalid format! Please enter the path as 'username/repository-name'.")
        else:
            api_url = f"https://github.com{repo_path}"
            
            headers = {}
            if "GITHUB_TOKEN" in st.secrets:
                headers["Authorization"] = f"token {st.secrets['GITHUB_TOKEN']}"
            
            with st.spinner("Processing API data metrics..."):
                try:
                    response = requests.get(api_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        repo_data = response.json()
                        results = calculate_rating(repo_data)
                        
                        st.success(f"Analysis Complete for {repo_data.get('full_name')}!")
                        
                        # Big Grade Badges
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric(label="Overall Score", value=f"{results['total_score']} / 100")
                        with c2:
                            st.metric(label="Calculated Grade", value=results['grade'])
                        
                        # Visual Chart
                        st.subheader("📊 Metric Score Breakdown")
                        chart_df = pd.DataFrame({
                            "Metric Section": list(results["breakdown"].keys()),
                            "Assigned Weight": list(results["breakdown"].values())
                        })
                        st.bar_chart(data=chart_df, x="Metric Section", y="Assigned Weight", use_container_width=True)
                        
                        # 📝 Smart Automated Recommendations based on Grade
                        st.subheader("💡 Rater Audit Insights")
                        if results['grade'] in ["A+", "A"]:
                            st.info("🔥 This repository is highly optimized, active, and exhibits phenomenal open-source health standards.")
                        elif results['grade'] == "B":
                            st.warning("⚠️ Good project framework, but could use more community activity or an updated description.")
                        else:
                            st.error("🚨 Critical maintenance needed. Check if this repository has open issues running wild or missing core README files.")
                        
                    elif response.status_code == 403:
                        st.error("🚫 GitHub API Rate limit completely exhausted. Please add a GITHUB_TOKEN inside Streamlit Cloud Secrets.")
                    elif response.status_code == 404:
                        st.error("🔍 Repository not found. Please double-check the spelling layout.")
                    else:
                        st.error(f"GitHub API returned unexpected status code: {response.status_code}.")
                        
                except requests.exceptions.Timeout:
                    st.error("⏳ Connection timed out! Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("🌐 Shared IP block detected. Please use a Personal Access Token to secure your connection.")
                except Exception as e:
                    st.error("An unexpected app tracking exception occurred.")
