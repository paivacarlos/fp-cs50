# GitHub Projects Tasks - Epic 1: Base Environment & DB Setup

This document contains the detailed task definitions for **Epic 1** based on the [engineering_spec.md](file:///c:/Users/carlo/cs50/chapter_10/project/fp-cs50/engineering_spec.md). You can copy and paste the titles and descriptions directly to create "Draft Issues" or "Issues" in your GitHub Project.

---

## 1. Create `requirements.txt` with project dependencies
* **Title:** `[Epic 1] Configure requirements.txt and dependencies`
* **Description:**
  Configure the `requirements.txt` file containing all the necessary dependencies to initialize the Flask project and integrate it with the database and the Gemini API.
* **Acceptance Criteria:**
  - [ ] `requirements.txt` file created in the project root.
  - [ ] Dependencies listed with stable or pinned versions: `Flask`, `werkzeug`, `google-generativeai`, `python-dotenv`, etc.
  - [ ] Basic installation instructions in a virtual environment documented.

---

## 2. Create database schema script `schema.sql`
* **Title:** `[Epic 1] Create schema.sql for database definition`
* **Description:**
  Write the SQL script to create the initial structure of the SQLite database (`conference_data.db`).
* **Acceptance Criteria:**
  - [ ] `users` table created with fields: `id` (PK, auto-increment), `username` (UNIQUE, NOT NULL), `hash` (TEXT, NOT NULL).
  - [ ] `conferences` table created with fields: `id` (PK), `user_id` (FK to `users.id`), `screenshot_path` (TEXT), `initial_context` (TEXT), `headline` (TEXT), `chronicle` (TEXT), `created_at` (DATETIME).
  - [ ] `rounds` table created with fields: `id` (PK), `conference_id` (FK to `conferences.id`), `round_number` (INTEGER), `question` (TEXT), `answer` (TEXT).
  - [ ] Foreign key constraints configured with referential integrity.

---

## 3. Implement `services/db.py` for SQLite management
* **Title:** `[Epic 1] Implement database connection and manipulation service (services/db.py)`
* **Description:**
  Develop the service layer responsible for opening/closing connections to SQLite, returning rows mapped as dictionaries (row factory), and managing safe transactions/queries.
* **Acceptance Criteria:**
  - [ ] `services/db.py` file created.
  - [ ] Connection context manager (class or function) implemented.
  - [ ] SQLite configured to enable foreign key support.
  - [ ] `sqlite3.Row` configured for easy column attribute access.

---

## 4. Create CLI helper/command for database initialization (`init_db`)
* **Title:** `[Epic 1] Implement CLI helper for database initialization (init_db)`
* **Description:**
  Develop a CLI command or helper script to read `schema.sql` and generate a clean SQLite database file.
* **Acceptance Criteria:**
  - [ ] Function or script callable via terminal (e.g., `python -m services.db` or `flask init-db`).
  - [ ] Creation of the `conference_data.db` file if it does not exist.
  - [ ] Clean execution of `schema.sql` without errors.

---

## 5. Create environment variables template `.env.example`
* **Title:** `[Epic 1] Create .env.example environment template`
* **Description:**
  Create a `.env.example` template file to document the required environment variables (such as API keys and Flask session secrets) without exposing real credentials.
* **Acceptance Criteria:**
  - [ ] `.env.example` file created in the project root.
  - [ ] `FLASK_SECRET_KEY` variable placeholder defined for Flask sessions.
  - [ ] `GEMINI_API_KEY` variable placeholder defined for the artificial intelligence integration.
  - [ ] `.gitignore` updated to ensure the real `.env` file is not tracked by Git.
