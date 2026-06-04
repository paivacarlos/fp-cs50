# GitHub Projects Tasks - Epic 2: User Authentication System

This document contains the detailed task definitions for **Epic 2** based on the [engineering_spec.md](file:///c:/Users/carlo/cs50/chapter_10/project/fp-cs50/docs%20of%20project/engineering_spec.md). You can copy and paste the titles and descriptions directly to create "Draft Issues" or "Issues" in your GitHub Project.

---

## 1. Implement password hashing utilities
* **Title:** `[Epic 2 - Task 1] Implement password hashing and validation`
* **Description:**
  Set up utilities to securely hash user passwords during registration and verify them during login using `werkzeug.security`.
* **Acceptance Criteria:**
  - [ ] Helper functions or logic defined using `generate_password_hash` to store passwords securely.
  - [ ] Helper functions or logic defined using `check_password_hash` to validate passwords during login.

---

## 2. Implement registration UI and controller (with auto-login)
* **Title:** `[Epic 2 - Task 2] Implement registration UI and route controller`
* **Description:**
  Create the registration form template (`register.html`) and backend route controller (`routes/auth.py`). 
* **Acceptance Criteria:**
  - [ ] HTML registration form created with fields for username, password, and password confirmation.
  - [ ] Route handler (`POST /register`) that validates inputs (e.g., checks if username already exists, matches password confirmation).
  - [ ] Inserts the new user into the SQLite database.
  - [ ] **Auto-login behavior:** Instantly populates the Flask session cookie with the new user's ID upon successful registration, directing them to the dashboard/setup page without requiring a manual login.
  - [ ] Navigation link added to redirect users who already have an account to the login page.

---

## 3. Configure Flask session security
* **Title:** `[Epic 2 - Task 3] Configure Flask session cookie security`
* **Description:**
  Initialize and configure Flask sessions to keep users logged in securely.
* **Acceptance Criteria:**
  - [ ] Flask app configured to load `FLASK_SECRET_KEY` from the environment.
  - [ ] Sessions configured with secure cookie parameters (e.g., HTTPOnly, SameSite='Lax').

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
  - [ ] Decorator checks if user ID exists in the active Flask session.
  - [ ] Redirects anonymous users to the login screen.
  - [ ] Applied to protected routes (e.g., setup panel, history page, Q&A game loop endpoints).

---

## 6. Implement logout route
* **Title:** `[Epic 2 - Task 6] Implement logout endpoint`
* **Description:**
  Create a route to securely terminate the user's session.
* **Acceptance Criteria:**
  - [ ] Route handler (`/logout`) that clears user data from the Flask session.
  - [ ] Redirects the user to the landing page or login screen with a success message.
