"""
Page Object: User Form (Add / Edit)
Covers both the Add User and Save (Edit) User forms.
"""

from playwright.sync_api import Page, expect


class UserFormPage:

    def __init__(self, page: Page):
        self.page = page
        # Form fields  (OrangeHRM uses custom .oxd-select-text for dropdowns)
        self.user_role_dropdown   = page.locator(
            "//label[text()='User Role']/../..//div[@class='oxd-select-text-input']"
        )
        self.status_dropdown      = page.locator(
            "//label[text()='Status']/../..//div[@class='oxd-select-text-input']"
        )
        self.employee_name_input  = page.locator(
            "//label[text()='Employee Name']/../..//input"
        )
        self.username_input       = page.locator(
            "//label[text()='Username']/../..//input"
        )
        self.password_input       = page.locator(
            "//label[text()='Password']/../..//input"
        ).first
        self.confirm_password_input = page.locator(
            "//label[text()='Confirm Password']/../..//input"
        )
        # Buttons
        self.save_button   = page.get_by_role("button", name="Save")
        self.cancel_button = page.get_by_role("button", name="Cancel")
        # Toast / success banner
        self.success_toast = page.locator(".oxd-toast--success")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _select_dropdown_option(self, dropdown_locator, option_text: str):
        """Click a custom OrangeHRM dropdown and pick the matching option."""
        dropdown_locator.click()
        self.page.get_by_role("option", name=option_text).click()

    # ── Form fill ─────────────────────────────────────────────────────────────

    def set_user_role(self, role: str):
        """Choose a User Role from the dropdown (e.g. 'Admin', 'ESS')."""
        self._select_dropdown_option(self.user_role_dropdown, role)

    def set_status(self, status: str):
        """Choose a Status from the dropdown (e.g. 'Enabled', 'Disabled')."""
        self._select_dropdown_option(self.status_dropdown, status)

    def set_employee_name(self, name: str):
        """
        Type into the Employee Name autocomplete and select the first suggestion.
        """
        self.employee_name_input.fill(name)
        # Wait for autocomplete dropdown to appear and pick first option
        autocomplete_option = self.page.locator(".oxd-autocomplete-option").first
        autocomplete_option.wait_for(state="visible", timeout=5000)
        autocomplete_option.click()

    def set_username(self, username: str):
        """Fill in the Username field."""
        self.username_input.fill(username)

    def set_password(self, password: str, confirm: str = None):
        """Fill in Password and Confirm Password fields."""
        self.password_input.fill(password)
        self.confirm_password_input.fill(confirm if confirm else password)

    # ── Full form actions ─────────────────────────────────────────────────────

    def fill_add_user_form(
        self,
        role: str,
        status: str,
        employee_name: str,
        username: str,
        password: str,
    ):
        """Fill every field on the Add User form."""
        self.set_user_role(role)
        self.set_status(status)
        self.set_employee_name(employee_name)
        self.set_username(username)
        self.set_password(password)

    def submit(self):
        """Click Save and wait for navigation."""
        self.save_button.click()
        self.page.wait_for_load_state("networkidle")

    def cancel(self):
        """Click Cancel and wait for navigation."""
        self.cancel_button.click()
        self.page.wait_for_load_state("networkidle")

    def is_success_toast_visible(self) -> bool:
        """Return True if the green success toast is displayed."""
        return self.success_toast.is_visible()

    # ── Validation helpers ────────────────────────────────────────────────────

    def get_username_value(self) -> str:
        """Read back the current value of the Username input (for edit validation)."""
        return self.username_input.input_value()
