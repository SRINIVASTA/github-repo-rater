import pytest
import subprocess
import time
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module", autouse=True)
def streamlit_server():
    """Starts the Streamlit application interface in the background for testing."""
    process = subprocess.Popen(
        ["streamlit", "run", "app/main.py", "--server.port=8502", "--server.headless=true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    yield
    process.terminate()

def test_user_profile_audit_workflow():
    """Simulates an automated execution loop hitting the main entry viewport."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8502")
        
        assert page.is_visible("text=GitHub User Profile Auditor")
        
        username_input = page.get_by_role("textbox", name="GitHub Username")
        assert username_input.is_visible()
        username_input.fill("test-profile-handle")
        
        audit_button = page.get_by_role("button", name="Audit User Profile")
        assert audit_button.is_visible()
        audit_button.click()
        
        time.sleep(2)
        assert page.get_by_text("GitHub API Return Code").is_visible() or page.get_by_text("Connection Failure").is_visible()
        browser.close()
