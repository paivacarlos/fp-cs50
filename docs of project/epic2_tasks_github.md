# GitHub Projects Tasks - Epic 2: User Authentication System

This document contains the detailed task definitions for **Epic 2** based on the [engineering_spec.md](engineering_spec.md). You can copy and paste the titles and descriptions directly to create "Draft Issues" or "Issues" in your GitHub Project.

---

## 1. Implement password hashing utilities
* **Title:** `[Epic 2 - Task 1] Implement password hashing and validation`
* **Description:**
  Set up stateless helper functions to securely hash user passwords and verify them using `werkzeug.security` inside a dedicated utility module, along with unit tests using `pytest`.
* **Acceptance Criteria:**
  - [x] Create `utils/security.py` containing:
    - `hash_password(password)`: returns the hashed password string.
    - `check_password(password_hash, password)`: returns boolean indicating if password is valid.
  - [x] Create `tests/test_security.py` with pytest test cases validating:
    - Hashing produces a non-plain-text string.
    - Hashing the same password twice produces different hashes (salts are working).
    - `check_password` returns `True` for matching password and `False` for matching check, and `False` for incorrect passwords.
  - [x] Run and pass tests using command `pytest tests/test_security.py`.

---

## 2. Implement registration UI and controller (with auto-login)
* **Title:** `[Epic 2 - Task 2] Implement registration UI and route controller`
* **Description:**
  Create the registration form template (`register.html`) and backend route controller (`routes/auth.py`), covered by tests at all levels (unit, API, and frontend structure).
* **Acceptance Criteria:**
  - [x] HTML registration form (`templates/register.html`) created with fields for username, password, and password confirmation.
  - [x] Route handler (`POST /register`) that validates inputs (e.g., checks if username already exists, matches password confirmation).
  - [x] Inserts the new user into the SQLite database.
  - [x] **Auto-login behavior:** Instantly populates the Flask session cookie with the new user's ID upon successful registration, directing them to the dashboard/setup page.
  - [x] Navigation link added to redirect users who already have an account to the login page.
  - [x] **Unit & API Tests (`tests/test_auth.py`):**
    - Verify GET `/register` returns `200` status and includes the registration form elements.
    - Verify successful POST `/register` registers the user, performs auto-login (session cookie updated), and redirects correctly.
    - Verify POST `/register` validation errors (duplicate username, password mismatch) prevent database insert and return descriptive warnings.
  - [x] **Frontend Structure Tests (`tests/test_auth.py`):**
    - Assert HTML form contains inputs for `username`, `password`, and `confirm_password` with appropriate form submission attributes.

---

## 3. Configure Flask session security
* **Title:** `[Epic 2 - Task 3] Configure Flask session cookie security`
* **Description:**
  Initialize and configure Flask sessions to keep users logged in securely.
* **Acceptance Criteria:**
  - [x] Flask app configured to load `FLASK_SECRET_KEY` from the environment.
  - [x] Sessions configured with secure cookie parameters (e.g., HTTPOnly, SameSite='Lax').

---

## 4. Implement login UI and controller
* **Title:** `[Epic 2 - Task 4] Implement login UI and route controller`
* **Description:**
  Create the login form template (`login.html`) and backend route controller.
* **Acceptance Criteria:**
  - [ ] HTML login form created with fields for username and password.
  - [ ] Route handler (`POST /login`) that retrieves user from database, verifies the password hash, and stores their user ID in the session.
  - [ ] Proper error messages displayed for invalid credentials.
  - [ ] Navigation link added to redirect users who do not have an account to the registration page.

---

## 5. Implement `@login_required` decorator
* **Title:** `[Epic 2 - Task 5] Implement login_required decorator for protected routes`
* **Description:**
  Create a custom Python decorator (`@login_required`) to secure views and API endpoints, ensuring only authenticated users can access them.
* **Acceptance Criteria:**
  - [x] Decorator checks if user ID exists in the active Flask session.
  - [x] Redirects anonymous users to the login screen.
  - [x] Applied to protected routes (e.g., setup panel, history page, Q&A game loop endpoints).

---

## 6. Implement logout route
* **Title:** `[Epic 2 - Task 6] Implement logout endpoint`
* **Description:**
  Create a route to securely terminate the user's session.
* **Acceptance Criteria:**
  - [x] Route handler (`/logout`) that clears user data from the Flask session.
  - [x] Redirects the user to the landing page or login screen with a success message.
