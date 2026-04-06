"""
E2E smoke tests – browser interaction via Playwright.
"""
import re

from playwright.sync_api import Page, expect


def test_root_redirects_to_login(page: Page, app_server: str):
    """Visiting / without a session should land on the login page."""
    page.goto(f"{app_server}/")
    # After redirect, URL must contain /login
    expect(page).to_have_url(re.compile(r".*/login"))


def test_login_page_shows_form(page: Page, app_server: str):
    """The login page must show the username/password form, not an error page."""
    page.goto(f"{app_server}/login")

    expect(page).to_have_title(re.compile(r"MEDIBOT.*Login", re.IGNORECASE))
    expect(page.locator("input#username")).to_be_visible()
    expect(page.locator("input#password")).to_be_visible()
    expect(page.locator("button[type=submit]")).to_be_visible()
