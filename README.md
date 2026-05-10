# AccuKnox – OrangeHRM User Management Tests

End-to-end automation for the **User Management** module of
[OrangeHRM](https://opensource-demo.orangehrmlive.com), built with
**Playwright + Python** and structured using the **Page Object Model (POM)**.

---

## Project Structure

```
AccuKnox-user-management-tests/
├── pages/
│   ├── __init__.py              # Exports LoginPage, AdminPage, UserFormPage
│   ├── login_page.py            # Login page POM
│   ├── admin_page.py            # Admin → User Management list POM
│   └── user_form_page.py        # Add / Edit user form POM
├── tests/
│   ├── __init__.py
│   └── test_user_management.py  # All 8 test cases
├── test_cases/
│   └── UserManagement_TestCases.xlsx  # Manual test case document
├── conftest.py                  # Shared fixtures (auth, created_user)
├── pytest.ini                   # testpaths = tests, default -v flag
├── requirements.txt
└── README.md
```

---

## Test Cases Covered

| TC ID  | Scenario                                              |
|--------|-------------------------------------------------------|
| TC-01  | Login with valid credentials                          |
| TC-02  | Navigate to Admin > User Management                   |
| TC-03  | Add a new user with all required fields               |
| TC-04  | Search for the newly created user by username         |
| TC-05  | Edit all possible user details (Role + Status)        |
| TC-06  | Validate that all updated details are persisted       |
| TC-07  | Delete the user and verify removal from the list      |
| TC-08  | Login fails with invalid credentials (negative test)  |

---

## Prerequisites

- **Python 3.9+**
- **pip**
- Internet access to reach `opensource-demo.orangehrmlive.com`

---

## Setup

### 1 — Clone the repository

```bash
git clone https://github.com/mohitsingh4716/AccuKnox-user-management-tests.git
cd AccuKnox-user-management-tests
```

### 2 — Create and activate a virtual environment (recommended)

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4 — Install Playwright browsers

```bash
playwright install chromium
```

> Install all browsers with `playwright install` if you want to run on Firefox or WebKit too.

---

## Running the Tests

### Run all tests (headless, default)

```bash
pytest
```

### Run all tests in headed mode (see the browser)

```bash
pytest --headed
```

### Run a single test case

```bash
pytest tests/test_user_management.py::test_tc01_login_with_valid_credentials -v
```

### Run on a specific browser

```bash
pytest --browser firefox
pytest --browser webkit
```

### Generate an HTML report

```bash
pip install pytest-html
pytest --html=report.html --self-contained-html
```

---

## Configuration

Key settings are at the top of **`conftest.py`**:

| Variable          | Default         | Description                        |
|-------------------|-----------------|------------------------------------|
| `ADMIN_USERNAME`  | `Admin`         | Login username                     |
| `ADMIN_PASSWORD`  | `admin123`      | Login password                     |
| `TEST_USER_DATA`  | see conftest.py | Data used to create the test user  |
| `slow_mo`         | `500` ms        | Slow-motion delay (browser-level)  |

---

## Playwright Version

```
playwright==1.50.0
pytest-playwright==0.6.2
```

Verify after install:

```bash
playwright --version
```

---

## Application Under Test

| Property | Value                                                                              |
|----------|------------------------------------------------------------------------------------|
| URL      | https://opensource-demo.orangehrmlive.com/web/index.php/auth/login                |
| Username | Admin                                                                              |
| Password | admin123                                                                           |

> ⚠️ This is a shared public demo instance. Test data (usernames) are randomised
> per run to avoid conflicts with other users.

---

## Notes / Known Issues

- The demo site is occasionally reset by the OrangeHRM team, which may clear
  test users created by previous runs.
- Employee names used in the Add User form must already exist in the system.
  The default test data uses `"Lisa"` as a partial match — adjust in
  `conftest.py` → `TEST_USER_DATA["employee_name"]` if needed.
- TC-07 deletes the shared `created_user`. The `conftest.py` teardown safely
  skips deletion if the user is already gone.
