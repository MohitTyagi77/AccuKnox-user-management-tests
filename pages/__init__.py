"""
pages/__init__.py
=================
Expose all Page Object Model classes from a single import point.

Usage:
    from pages import LoginPage, AdminPage, UserFormPage
"""

from .login_page import LoginPage
from .admin_page import AdminPage
from .user_form_page import UserFormPage

__all__ = ["LoginPage", "AdminPage", "UserFormPage"]
