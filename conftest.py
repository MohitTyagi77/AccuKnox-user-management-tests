"""
conftest.py – Shared pytest-playwright fixtures
================================================
Provides:
  - browser_type_launch_args : slow-mo for readability (browser-level setting)
  - browser_context_args     : viewport size
  - logged_in_page           : a Page that is already authenticated
  - created_user             : session-scoped fixture that creates a user once
                               and exposes its data for search / edit / delete tests
"""

import uuid
import pytest
from playwright.sync_api import Page

from pages import LoginPage, AdminPage, UserFormPage

# ── Credentials & test data ───────────────────────────────────────────────────

ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "admin123"

# A unique username per test-run so parallel runs don't collide
TEST_USER_DATA = {
    "role":          "ESS",
    "status":        "Enabled",
    "employee_name": "Lisa",          # partial name; autocomplete picks first match
    "username":      f"accuknox_{uuid.uuid4().hex[:6]}",
    "password":      "Admin@12345",
}

# ── Browser launch settings ───────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Override browser launch args: 500 ms slow-mo for demo / CI video."""
    return {
        **browser_type_launch_args,
        "slow_mo": 500,
    }


# ── Browser context settings ──────────────────────────────────────────────────

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Override default context: 1280×800 viewport."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 800},
    }


# ── Authenticated page ────────────────────────────────────────────────────────

@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """
    Return a page that has already completed the login flow.
    Each test that uses this fixture gets a fresh browser page.
    """
    login = LoginPage(page)
    login.navigate()
    login.login(ADMIN_USERNAME, ADMIN_PASSWORD)
    # Verify we landed on the dashboard
    page.wait_for_url("**/dashboard/**", timeout=10_000)
    return page


# ── Pre-created user (session-scoped) ─────────────────────────────────────────

@pytest.fixture(scope="session")
def created_user(browser, browser_context_args):
    """
    Session-scoped fixture: creates one test user before the test session
    and yields TEST_USER_DATA.  Runs cleanup (delete) after all tests finish.
    """
    context = browser.new_context(**browser_context_args)
    page    = context.new_page()

    # --- Setup: log in and create the user ---
    login = LoginPage(page)
    login.navigate()
    login.login(ADMIN_USERNAME, ADMIN_PASSWORD)
    page.wait_for_url("**/dashboard/**", timeout=10_000)

    admin = AdminPage(page)
    admin.navigate()
    admin.click_add()

    form = UserFormPage(page)
    form.fill_add_user_form(
        role=          TEST_USER_DATA["role"],
        status=        TEST_USER_DATA["status"],
        employee_name= TEST_USER_DATA["employee_name"],
        username=      TEST_USER_DATA["username"],
        password=      TEST_USER_DATA["password"],
    )
    form.submit()

    yield TEST_USER_DATA          # tests run here

    # --- Teardown: delete the user if it still exists ---
    try:
        admin.navigate()
        admin.search_by_username(TEST_USER_DATA["username"])
        # Only delete if the user still exists (TC-07 may have already deleted it)
        if admin.get_result_count() > 0:
            admin.select_user_checkbox(TEST_USER_DATA["username"])
            admin.click_delete_selected()
            admin.confirm_delete()
    except Exception as e:
        print(f"[conftest teardown] Could not delete test user (may already be deleted): {e}")
    finally:
        page.close()
        context.close()
