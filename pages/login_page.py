"""
Page Object: Login Page
URL: /web/index.php/auth/login
"""

from playwright.sync_api import Page, expect


class LoginPage:
    URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"

    def __init__(self, page: Page):
        self.page = page
        # Locators
        self.username_input   = page.get_by_placeholder("Username")
        self.password_input   = page.get_by_placeholder("Password")
        self.login_button     = page.get_by_role("button", name="Login")
        self.error_message    = page.locator(".oxd-alert-content-text")

    def navigate(self):
        """Open the login page."""
        self.page.goto(self.URL)
        expect(self.login_button).to_be_visible()

    def login(self, username: str, password: str):
        """Fill credentials and submit the login form."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        # Wait until the dashboard or an error appears
        self.page.wait_for_load_state("networkidle")

    def get_error_text(self) -> str:
        """Return the login error message text."""
        return self.error_message.inner_text()
