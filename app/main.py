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
        api_url = f"https://api.github.com/repos/{repo_path}"
        
        with st.spinner("Processing API data metrics..."):
            response = requests.get(api_url)
            
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
            else:
                st.error("Could not fetch data. Check your connection or repository name spelling.")
