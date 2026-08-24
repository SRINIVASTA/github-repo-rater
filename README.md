# GitHub User Profile Auditor 👤🔒

An automated profile auditing engine that securely parses a developer's public footprint via the GitHub REST API to calculate a weighted profile score, footprint distribution, and structural optimization grade.

🌐 **Live Interactive Web App:** [Launch Live Streamlit Dashboard](https://git-repo-rater-vrjefshmuuzegrpdzjphka.streamlit.app/)


## 🌟 Features

- **Instant Browser Auditing:** Fetch and grade any developer's public footprint by username.
- **Dynamic Tiering System:** Automatically categorizes profiles into Tiers (e.g., **Tier A**) based on a weighted 0-100 score.
- **Footprint Metric Distribution:** Evaluates engineering presence across major performance segments:
  - **Codebase Portfolio:** Scoring project quality, architectures, and repository depth.
  - **Network Influence:** Tracking engagement metrics, contributions, and social visibility.
  - **Profile Optimization:** Assessing biography, layout completeness, and personal branding.
  - **Evaluation Module:** Comprehensive overview scoring of general engineering habits.
- **Token Integration:** Built-in validation checking for active `GITHUB_TOKEN` statuses to prevent API rate-limiting during deep audits.

## 📊 Evaluation Metrics

The algorithm scans your public footprint and computes scores across three principal vectors:
1. **Profile Optimization** (Bio, Location, Layout completeness, Custom Branding)
2. **Codebase Portfolio** (Active repositories, codebase health, language distributions)
3. **Network Influence** (Followers, open-source interactions, external contributions)

## 🛠️ Tech Stack

- **Backend Logic:** Python 3.x (Structured natively within the `/app` folder)
- **Data Source:** [GitHub REST API](https://github.com)

## 🚀 Getting Started

### Prerequisites

Ensure you have Python 3.x installed. Download it directly from the [Official Python Website](https://python.org).

### Installation

1. **Clone the application:**
   ```bash
   git clone https://github.com
   cd github-repo-rater
   ```

2. **Establish a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install application dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Authentication Setup

To execute full audits without rate limits, generate a Personal Access Token (PAT) from your [GitHub Developer Settings](https://github.com/settings/tokens). 

Create a `.env` file in the root directory and append your token:
```env
GITHUB_TOKEN=your_personal_access_token_here
```

## 💻 Usage

To launch the script and generate a profile audit report directly from your command line or web dashboard, execute:

```bash
python -m app.main
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
