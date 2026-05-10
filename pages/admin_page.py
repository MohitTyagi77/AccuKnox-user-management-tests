"""
Page Object: Admin – User Management List
URL: /web/index.php/admin/viewSystemUsers
"""

from playwright.sync_api import Page, expect


class AdminPage:
    URL = "https://opensource-demo.orangehrmlive.com/web/index.php/admin/viewSystemUsers"

    def __init__(self, page: Page):
        self.page = page
        # Search form
        self.search_username_input = page.locator(
            "//label[text()='Username']/../..//input"
        )
        self.search_button  = page.get_by_role("button", name="Search")
        self.reset_button   = page.get_by_role("button", name="Reset")
        # Table / records
        self.result_rows    = page.locator(".oxd-table-body .oxd-table-row")
        self.record_count   = page.locator("span.oxd-text--span", has_text="Record")
        # Toolbar
        self.add_button     = page.get_by_role("button", name="Add")

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self):
        """Go to the User Management list page."""
        self.page.goto(self.URL)
        expect(self.add_button).to_be_visible()

    # ── Search ────────────────────────────────────────────────────────────────

    def search_by_username(self, username: str):
        """Fill username in search form and click Search."""
        self.search_username_input.fill(username)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")

    def get_result_count(self) -> int:
        """Return number of rows in the search results table."""
        return self.result_rows.count()

    def get_record_label(self) -> str:
        """Return the '(1) Record Found' label text."""
        return self.record_count.inner_text()

    # ── Add ───────────────────────────────────────────────────────────────────

    def click_add(self):
        """Click the Add button to open the Add User form."""
        self.add_button.click()
        self.page.wait_for_load_state("networkidle")

    # ── Row actions ───────────────────────────────────────────────────────────

    def click_edit_for_user(self, username: str):
        """
        Find the row containing *username* and click its edit (pencil) icon.
        """
        row = self.page.locator(
            f".oxd-table-row:has-text('{username}')"
        ).first
        row.locator("button i.bi-pencil").click()
        self.page.wait_for_load_state("networkidle")

    def select_user_checkbox(self, username: str):
        """Tick the checkbox on the row that contains *username*."""
        row = self.page.locator(
            f".oxd-table-row:has-text('{username}')"
        ).first
        row.locator(".oxd-checkbox-input").click()

    def click_delete_selected(self):
        """Click the top-level 'Delete Selected' button."""
        self.page.get_by_role("button", name="Delete Selected").click()

    def confirm_delete(self):
        """Confirm the deletion in the confirmation dialog."""
        self.page.get_by_role("button", name="Yes, Delete").click()
        self.page.wait_for_load_state("networkidle")
