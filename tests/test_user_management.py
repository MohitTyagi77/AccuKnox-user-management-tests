"""
test_user_management.py
========================
End-to-end test suite for the OrangeHRM User Management module.

Test Cases
----------
TC-01  Verify successful login with valid credentials
TC-02  Verify navigation to Admin > User Management
TC-03  Add a new user with all required fields
TC-04  Search for the newly created user by username
TC-05  Edit all possible user details (role + status)
TC-06  Validate that the updated details are saved correctly
TC-07  Delete the user and verify removal from the list
TC-08  Verify login fails with invalid credentials

Run:
    pytest tests/test_user_management.py -v
    # Or from project root (pytest.ini configures testpaths = tests):
    pytest -v
"""

import pytest
from playwright.sync_api import Page, expect

from pages import LoginPage, AdminPage, UserFormPage
from conftest import ADMIN_USERNAME, ADMIN_PASSWORD, TEST_USER_DATA


# ─────────────────────────────────────────────────────────────────────────────
# TC-01  Login with valid credentials
# ─────────────────────────────────────────────────────────────────────────────

def test_tc01_login_with_valid_credentials(page: Page):
    """
    TC-01: Verify that a user can log in with valid credentials
    and is redirected to the dashboard.
    """
    login = LoginPage(page)
    login.navigate()
    login.login(ADMIN_USERNAME, ADMIN_PASSWORD)

    # Assert the URL contains 'dashboard'
    expect(page).to_have_url(
        "https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index"
    )
    # Assert the OrangeHRM logo / dashboard header is visible
    expect(page.locator(".oxd-topbar-header-breadcrumb")).to_be_visible()


# ─────────────────────────────────────────────────────────────────────────────
# TC-02  Navigate to Admin > User Management
# ─────────────────────────────────────────────────────────────────────────────

def test_tc02_navigate_to_user_management(logged_in_page: Page):
    """
    TC-02: Verify that the Admin module's User Management page
    loads correctly and displays the Add button.
    """
    admin = AdminPage(logged_in_page)
    admin.navigate()

    expect(admin.add_button).to_be_visible()
    expect(admin.search_button).to_be_visible()
    expect(logged_in_page).to_have_url(
        "https://opensource-demo.orangehrmlive.com/web/index.php/admin/viewSystemUsers"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC-03  Add a new user
# ─────────────────────────────────────────────────────────────────────────────

def test_tc03_add_new_user(logged_in_page: Page):
    """
    TC-03: Verify that a new user can be added with all required
    fields filled in and that a success toast appears.
    """
    admin = AdminPage(logged_in_page)
    admin.navigate()
    admin.click_add()

    form = UserFormPage(logged_in_page)
    form.fill_add_user_form(
        role=          TEST_USER_DATA["role"],
        status=        TEST_USER_DATA["status"],
        employee_name= TEST_USER_DATA["employee_name"],
        username=      TEST_USER_DATA["username"] + "_tc03",
        password=      TEST_USER_DATA["password"],
    )
    form.submit()

    # A success toast must be visible after saving
    expect(form.success_toast).to_be_visible(timeout=8_000)

    # Clean up: delete the tc03-specific user
    admin.navigate()
    admin.search_by_username(TEST_USER_DATA["username"] + "_tc03")
    if admin.get_result_count() > 0:
        admin.select_user_checkbox(TEST_USER_DATA["username"] + "_tc03")
        admin.click_delete_selected()
        admin.confirm_delete()


# ─────────────────────────────────────────────────────────────────────────────
# TC-04  Search for the created user
# ─────────────────────────────────────────────────────────────────────────────

def test_tc04_search_created_user(logged_in_page: Page, created_user: dict):
    """
    TC-04: Verify that searching by the created username returns
    exactly one matching record.
    """
    admin = AdminPage(logged_in_page)
    admin.navigate()
    admin.search_by_username(created_user["username"])

    # Exactly one result row
    expect(admin.result_rows).to_have_count(1, timeout=8_000)

    # The result row must display the username
    expect(
        logged_in_page.locator(
            f".oxd-table-row:has-text('{created_user['username']}')"
        ).first
    ).to_be_visible()


# ─────────────────────────────────────────────────────────────────────────────
# TC-05  Edit ALL possible user details (role + status)
# ─────────────────────────────────────────────────────────────────────────────

def test_tc05_edit_user_details(logged_in_page: Page, created_user: dict):
    """
    TC-05: Verify that the edit form opens pre-populated and that
    ALL editable fields (User Role and Status) can be changed and saved.

    Changes made:
      - User Role: ESS → Admin
      - Status:    Enabled → Disabled
    """
    admin = AdminPage(logged_in_page)
    admin.navigate()
    admin.search_by_username(created_user["username"])
    admin.click_edit_for_user(created_user["username"])

    form = UserFormPage(logged_in_page)

    # Username field should be pre-populated
    expect(form.username_input).to_have_value(created_user["username"])

    # Change the User Role from ESS to Admin
    form.set_user_role("Admin")

    # Change the Status from Enabled to Disabled
    form.set_status("Disabled")

    form.submit()

    expect(form.success_toast).to_be_visible(timeout=8_000)


# ─────────────────────────────────────────────────────────────────────────────
# TC-06  Validate updated details are persisted
# ─────────────────────────────────────────────────────────────────────────────

def test_tc06_validate_updated_details(logged_in_page: Page, created_user: dict):
    """
    TC-06: After editing, re-open the user record and verify that
    both the updated User Role (Admin) and Status (Disabled) are
    reflected in the form.
    """
    admin = AdminPage(logged_in_page)
    admin.navigate()
    admin.search_by_username(created_user["username"])
    admin.click_edit_for_user(created_user["username"])

    # The status dropdown should now read "Disabled"
    status_text = logged_in_page.locator(
        "//label[text()='Status']/../..//div[@class='oxd-select-text-input']"
    ).inner_text()
    assert "Disabled" in status_text, (
        f"Expected 'Disabled' status but got: '{status_text}'"
    )

    # The user role dropdown should now read "Admin"
    role_text = logged_in_page.locator(
        "//label[text()='User Role']/../..//div[@class='oxd-select-text-input']"
    ).inner_text()
    assert "Admin" in role_text, (
        f"Expected 'Admin' user role but got: '{role_text}'"
    )


# ─────────────────────────────────────────────────────────────────────────────
# TC-07  Delete the user
# ─────────────────────────────────────────────────────────────────────────────

def test_tc07_delete_user(logged_in_page: Page, created_user: dict):
    """
    TC-07: Verify that the user can be deleted and that a subsequent
    search for the same username returns no results.

    NOTE: This test deletes the shared created_user.  The conftest
    teardown will also attempt a delete but will gracefully skip
    if 0 records are found — which is safe.
    """
    admin = AdminPage(logged_in_page)
    admin.navigate()
    admin.search_by_username(created_user["username"])
    admin.select_user_checkbox(created_user["username"])
    admin.click_delete_selected()
    admin.confirm_delete()

    # Re-search — should find no records
    admin.search_by_username(created_user["username"])
    expect(admin.result_rows).to_have_count(0, timeout=8_000)


# ─────────────────────────────────────────────────────────────────────────────
# TC-08  Login fails with invalid credentials
# ─────────────────────────────────────────────────────────────────────────────

def test_tc08_login_with_invalid_credentials(page: Page):
    """
    TC-08: Verify that logging in with wrong credentials shows an
    error message and does NOT redirect to the dashboard.
    """
    login = LoginPage(page)
    login.navigate()
    login.login("invalid_user", "wrong_password")

    # Error alert must be visible
    expect(login.error_message).to_be_visible(timeout=5_000)

    # Must NOT be on the dashboard
    assert "dashboard" not in page.url, (
        "Expected to stay on login page but was redirected to dashboard."
    )
