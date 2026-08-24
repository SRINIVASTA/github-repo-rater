import streamlit as st
import requests
import pandas as pd
from scorer import calculate_rating

# Web configuration properties
st.set_page_config(page_title="GitHub Repo Rater", page_icon="📊", layout="centered")

st.title("📊 GitHub Repository Rater")
st.write("Analyze and evaluate repository health instantly from your browser.")

# Interactive text box
repo_input = st.text_input("Repository Path", placeholder="e.g., streamlit/streamlit")

if st.button("Run Analytics Engine", type="primary"):
    if not repo_input:
        st.warning("Please enter a valid path.")
    else:
        # Format strings to extract exact repo addresses
        repo_path = repo_input.replace("https://github.com/", "").strip("/")
        
        # Validation: Check if the input contains the required slash '/'
        if "/" not in repo_path:
            st.error("⚠️ Invalid format! Please enter the path as 'username/repository-name'.")
        else:
            api_url = f"https://github.com{repo_path}"
            
            with st.spinner("Processing API data metrics..."):
                try:
                    # Added a 10-second timeout so the app doesn't hang forever
                    response = requests.get(api_url, timeout=10)
                    
                    if response.status_code == 200:
                        repo_data = response.json()
                        results = calculate_rating(repo_data)
                        
                        st.success("Analysis Complete!")
                        
                        # Render Metric Blocks
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric(label="Overall Score", value=f"{results['total_score']} / 100")
                        with c2:
                            st.metric(label="Calculated Grade", value=results['grade'])
                        
                        # Visual Chart
                        chart_df = pd.DataFrame({
                            "Metric Section": list(results["breakdown"].keys()),
                            "Assigned Weight": list(results["breakdown"].values())
                        })
                        st.bar_chart(data=chart_df, x="Metric Section", y="Assigned Weight", use_container_width=True)
                    elif response.status_code == 404:
                        st.error("🔍 Repository not found. Please double-check the spelling.")
                    else:
                        st.error(f"GitHub API returned an error code: {response.status_code}. Rate limit might be reached.")
                        
                except requests.exceptions.Timeout:
                    st.error("⏳ Connection timed out! GitHub's servers took too long to respond. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("🌐 Network Connection Error! Streamlit Cloud is having trouble reaching GitHub. Please click 'Run Analytics Engine' again.")
                except Exception as e:
                    st.error("An unexpected error occurred. Please try again.")
