# PressConference EA

<p align="center">
  <img src="static/images/harvard_shield.jpg" alt="Harvard Shield" width="130" height="85">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="static/images/cs50_logo.png" alt="CS50 Logo" width="85" height="85">
</p>

<h3 align="center">CS50's Introduction to Computer Science</h3>
<h4 align="center">Harvard University - Final Project</h4>

---

### 📺 Video Walkthrough
> [!IMPORTANT]
> **Video Link:** [Watch the Final Project Video Walkthrough on YouTube](https://youtu.be/xxxxxx) *(Placeholder - please paste your recorded YouTube video URL here before submitting)*

---

## ⚽ Project Overview

**PressConference EA** is an interactive web companion application designed for players of **EA Sports FC (formerly FIFA)**. It bridges gameplay screenshots, direct user commentary, and state-of-the-art Generative AI to simulate a realistic, dynamic, and dramatic post-match sports press conference. 

The game loop works as follows:
1. **Match Upload:** The user uploads a gameplay or post-match statistics screenshot of their game and provides a brief initial comment (up to 200 characters) about the match context from the coach's perspective.
2. **Interactive Q&A Session:** The AI acts as a sharp, critical sports reporter, initiating a 3-round sequential press conference. The AI reporter tailors its questions based on the visual data extracted from the screenshot, the coach's initial notes, and the coach's replies in previous rounds.
3. **Sports Chronicle Generation:** Once the three rounds are finished, the app synthesizes the entire session into a stylized sports article (chronicle) with a punchy headline, displayed in a classic retro-styled printed newspaper page layout.

---

## 🌟 Distinctiveness and Complexity

To satisfy the CS50x final project criteria, this project has been built to exceed standard web application expectations in both **distinctiveness** and **architectural complexity**.

### 1. Distinctiveness
Most typical CS50 final projects fall into standard categories like to-do list managers, recipe websites, generic e-commerce mockups, or financial portfolio trackers (similar to CS50 Finance). **PressConference EA** is highly distinctive as it functions as a visual-gaming companion that merges **multimodal computer vision input** (analyzing match scoreboards/screenshots) with a **conversational state machine** and **automated sports journalism simulation**. 

Key elements of distinctiveness include:
* **Interactive Sports Roleplay:** It puts the user in the shoes of a manager interacting with persistent reporter personalities.
* **Multimodal Validation:** The AI validates the visual input. If a user uploads an unrelated image (e.g., a landscape, a cat, or an icon), the application detects the anomaly, rejects the upload, and stops the API loop to prevent resource waste.
* **Custom Vintage Newspaper Styling:** The output isn't just text; it renders a beautifully formatted, print-ready, dynamic glassmorphic-styled sports chronicle.

### 2. Technical Complexity
* **Conversational State Machine:** Rather than simple one-off API endpoints, the application implements a strict 3-round Q&A game cycle. The AI questions are generated sequentially, where Round 2 depends on Round 1's response, and Round 3 wraps up based on the accumulated transcript of all previous exchanges.
* **Multilayer Upload Security:** Security is handled robustly on the backend:
  1. *Extension Validation:* Rejects disallowed extensions.
  2. *MIME-Type Verification:* Checks the header of the uploaded payload.
  3. *Magic Bytes Binary Signature Analysis:* Reads the first 12 bytes of the file stream to verify it matches genuine PNG, JPEG, or GIF headers, preventing double-extension shell injection attacks.
  4. *Name Hashing:* Cryptographically renames all files to UUIDs to prevent directory traversal and overwrite attacks.
* **Database Design & Indexing:** A SQLite schema with strict `FOREIGN KEY` constraints, cascade deletion rules (`ON DELETE CASCADE`), and optimized database indexes (`idx_conferences_user_id` and `idx_rounds_conference_id`) for high-performance retrieval.
* **State & Transaction Integrity:** The backend implements cleanup wrappers: if a Generative AI query times out or fails, any newly uploaded files are automatically deleted, and database entries are reverted (`NULL` rollbacks), ensuring the user's session remains uncorrupted.
* **Post/Redirect/Get (PRG) Pattern:** Adheres strictly to the PRG pattern for authentication and setup routes to prevent duplicate form submissions and browser warning messages on F5 refreshes.
* **Comprehensive Testing Suite:** The workspace features **63 automated test assertions** including unit, integration, mock-based API tests, and browser-driven end-to-end (E2E) tests written with **Playwright**, validating interactive states (like dynamic character counters, drag-and-drop elements, and error alerts).

---

## 📂 File-by-File Directory Structure

Here is a detailed breakdown of the files created and their specific responsibilities in the project:

### Root Directory
* [app.py](app.py): The entrypoint of the application. It initializes the Flask instance, applies cookie-level security configurations (`HTTPOnly`, `SameSite="Lax"`, `MAX_CONTENT_LENGTH=5MB`), and registers all application blueprints (blueprints partition routes into clean modules).
* [schema.sql](schema.sql): Defines the relational schema. It creates tables for `users` (credentials), `conferences` (press room sessions, uploaded stats, and finalized chronicles), and `rounds` (the conversational dialogue history). Enforces cascading deletion and performance indexes.
* [requirements.txt](requirements.txt): Lists all Python dependencies, including Flask, Pytest, Playwright, dotenv, and the official Google Generative AI SDK.

### 🌐 Blueprints & Routing (`routes/`)
* [routes/auth.py](routes/auth.py): Blueprint managing secure user account creation, session verification, login validation (using password hashes), and session tear-down (logout).
* [routes/main.py](routes/main.py): Renders standard frontend pages such as the login/register views, the dashboard where press conferences are configured, the historical archives, and the retro newspaper display.
* [routes/api.py](routes/api.py): The core backend controller. Manages AJAX endpoints for uploading stats, updating the active conversational round, querying Gemini to generate questions/chronicles, saving answers, and managing transactional integrity (reverting states on errors).

### 🛠️ Services (`services/`)
* [services/db.py](services/db.py): Implements a context manager (`with get_db()`) to handle database connections. Ensures all query connections are cleanly closed after execution, preventing locked files or resource exhaustion.
* [services/gemini.py](services/gemini.py): Integrates the new `google-genai` SDK using structured Pydantic schemas (`ChronicleResponse`) for predictable JSON generation. It defines the multimodal AI prompts, forces image classification validation (detecting invalid non-game uploads), and handles the switch to Mock Mode.

### 🛡️ Utilities (`utils/`)
* [utils/security.py](utils/security.py): Hosts security helpers, wrapping password hashing processes and exporting route protectors (`@login_required` and `@api_login_required`).
* [utils/upload.py](utils/upload.py): Implements secure file upload logic, validating extensions, validating binary headers (magic bytes), checking file limits, and cryptographically naming upload payloads.

### 🎨 Templates & Interface (`templates/` & `static/`)
* [templates/base.html](templates/base.html): The base template containing shared UI shell configurations, glassmorphic CSS stylings, custom alert components, and navigation structures.
* [templates/login.html](templates/login.html) / [templates/register.html](templates/register.html): Custom user authentication screens.
* [templates/setup.html](templates/setup.html): The setup dashboard interface, containing drag-and-drop file regions, real-time image preview cards, and character countdown monitors.
* [templates/history.html](templates/history.html): Renders a card grid outlining the user's past conferences, including stats screenshots, matching dates, headlines, and links to reload records.
* [templates/newspaper.html](templates/newspaper.html): Interactive Q&A chat and article generator, built with CSS animations to simulate live typing, ending in a vintage paper layout.
* `static/`: Contains assets such as CSS styling rules, images, and Javascript handlers controlling the dynamic gameplay screens.

### 🧪 Automated Tests (`tests/`)
* [tests/conftest.py](tests/conftest.py): Supplies Pytest configurations, maintaining isolated test database fixtures to prevent testing artifacts from dirtying local files.
* [tests/test_auth.py](tests/test_auth.py): Verifies registration security, password constraints, and login session controls.
* [tests/test_security.py](tests/test_security.py): Asserts security decorator actions.
* [tests/test_upload.py](tests/test_upload.py): Asserts binary image verification, rejecting mock text payloads disguised as `.png`.
* [tests/test_api.py](tests/test_api.py): Thoroughly tests backend game loops, mock AI integrations, state machines, and rollback cleanups.
* [tests/test_gemini.py](tests/test_gemini.py): Tests the LLM prompt construction logic and Mock mode outputs.
* [tests/test_ui.py](tests/test_ui.py): Uses Playwright to simulate user interactions on actual Chrome/Chromium page sessions, testing features like character limiters, multiple file rejection alerts, and image previews.

---

## 🛠️ Installation & Setup

Follow these steps to deploy and run the project locally.

### 1. Prerequisites
Make sure you have Python 3.10+ installed:
```bash
python --version
```

### 2. Clone and Setup Environment
Navigate to your workspace directory and create a Python virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (CMD):**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
* **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
1. Copy the provided `.env.example` file to create a `.env` file:
   ```bash
   cp .env.example .env
   ```
2. Open the `.env` file and insert your keys:
   * `FLASK_SECRET_KEY`: A cryptographically secure random secret key.
   * `GEMINI_API_KEY`: Your official Gemini API Key from Google AI Studio.
   * `MOCK_GEMINI`: Set this to `false` to query the live Gemini model, or `true` for Mock Mode (see below).

---

## 💡 Quick Evaluation Tip (Mock Mode)

To make evaluation simple and avoid requiring a live Google Gemini API key:
1. Open your `.env` file.
2. Set `MOCK_GEMINI=true`.
3. Start the application normally.

With this flag set to `true`, the application operates in **Mock Mode**, providing pre-configured questions and sports articles instantaneously without making any external network requests or requiring a valid `GEMINI_API_KEY`. This ensures the evaluation team can review all UI screens and features instantly!

---

## 🗄️ Database Initialization

Before launching the server for the first time, generate the database file:
```bash
python -m services.db
```
This script will read `schema.sql` and output `conference_data.db` with all tables, constraints, indices, and relationships.

---

## 🚀 Running the Application

To start the Flask development server, execute:
```bash
python -m flask run
```
By default, the server is exposed at `http://127.0.0.1:5000/`.

---

## 🧪 Running the Test Suite

We have written a comprehensive, automated test suite that runs on isolated temporary databases so as not to pollute your main development database.

### 1. Playwright Setup (First Time Only)
Before executing the UI/browser automation tests, install Playwright's Chromium binary:
```bash
playwright install chromium
```

### 2. Run All Tests
```bash
pytest
```
*Tip: You can target specific files, like `pytest tests/test_api.py` or run browser-only tests with `pytest tests/test_ui.py`.*
