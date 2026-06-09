# GitHub Projects Tasks - Epic 4: AI Engine Integration & Q&A loop

This document contains the detailed task definitions for **Epic 4** based on the [engineering_spec.md](engineering_spec.md). You can copy and paste the titles and descriptions directly to create "Draft Issues" or "Issues" in your GitHub Project.

---

## 1. Implement Gemini AI service wrapper
* **Title:** `[Epic 4 - Task 1] Implement Gemini AI service wrapper`
* **Description:**
  Create a backend service module in `services/gemini.py` that wraps the Google GenAI SDK. This module will expose functions to configure the Gemini model, load the API key from environment variables, and request reporter questions from the Gemini API using multimodal inputs (match statistics screenshot + text context).
* **Acceptance Criteria:**
  - [ ] Initialize the Gemini client using the `google-generativeai` SDK.
  - [ ] Retrieve the Gemini API key from environment variables (`GEMINI_API_KEY`) and raise a clean configuration error if it is missing.
  - [ ] Use `gemini-1.5-flash` or `gemini-2.0-flash` (or equivalent current model) as the default model.
  - [ ] Implement `generate_first_question(image_path: str, context: str) -> str`:
    - Reads the image file from the path.
    - Sends the image and initial coach comment to the model.
    - Instructs the model using a system prompt to assume the persona of a realistic sports reporter asking an engaging first question about the match.
  - [ ] Implement `generate_next_question(image_path: str, context: str, history: list) -> str`:
    - Takes the image, original context, and a list of previous rounds (questions and answers).
    - Submits the dialogue history to the model to generate a relevant follow-up question.
  - [ ] Write unit/integration tests for `services/gemini.py` using mock/stub requests or a test API key to verify behavior.

---

## 2. Create conference start API endpoint
* **Title:** `[Epic 4 - Task 2] Create API endpoint to initiate press conferences`
* **Description:**
  Implement the backend route handler `POST /api/conference/start` in a new blueprint `routes/api.py`. This endpoint will validate the incoming request parameters (match screenshot and initial text context), save the uploaded file, insert a new record in the `conferences` database table, request the first question from the Gemini service, record that question as Round 1, and return it.
* **Acceptance Criteria:**
  - [ ] Create `routes/api.py` and register the `api_bp` blueprint inside `app.py`.
  - [ ] Protect `POST /api/conference/start` using the `@login_required` decorator.
  - [ ] Validate that a file is uploaded under the key `screenshot` and that its extension is valid using `utils.upload`.
  - [ ] Validate that the `initial_context` text is present and between 1 and 200 characters.
  - [ ] Save the screenshot to the filesystem using `save_upload_file` and obtain its relative path (e.g. `/static/uploads/...`).
  - [ ] Insert a new record in the `conferences` table containing the `user_id` (from session), `screenshot_path`, and `initial_context`.
  - [ ] Invoke `generate_first_question` from `services/gemini.py`.
  - [ ] Insert the generated question into the `rounds` table as `round_number = 1`.
  - [ ] Return a JSON response with status `201 Created` containing:
    - `conference_id`: The ID of the newly created conference.
    - `round_number`: `1`
    - `question`: The generated question text.
  - [ ] Write tests simulating successful initiation and validation failures (missing file, too long context).

---

## 3. Create conference answer and loop API endpoint
* **Title:** `[Epic 4 - Task 3] Create API endpoint to submit answers and advance Q&A rounds`
* **Description:**
  Implement the backend route handler `POST /api/conference/answer` (within `routes/api.py`) which processes the coach's response to the active question. It will update the database with the answer, check if there are subsequent rounds (1 and 2), query Gemini for the next follow-up question, or transition the conference state to completion (Round 3).
* **Acceptance Criteria:**
  - [ ] Protect `POST /api/conference/answer` using the `@login_required` decorator.
  - [ ] Expect `conference_id` and `answer` (non-empty string) in the POST request body.
  - [ ] Fetch the current round from the database and verify that the user owns the conference.
  - [ ] Save the coach's `answer` to the active round in the `rounds` table.
  - [ ] If the active round number is `1` or `2`:
    - Retrieve the screenshot, context, and entire previous dialogue history (Rounds 1 to current).
    - Call `generate_next_question` passing the history, screenshot, and context.
    - Save the next question to the database under a new round (`round_number = active_round_number + 1`).
    - Return a JSON response with status `200 OK` containing:
      - `round_number`: The new round number (e.g. `2` or `3`).
      - `question`: The new question text.
  - [ ] If the active round number is `3`:
    - Return a JSON response with status `200 OK` signaling completion (e.g. `{"status": "complete", "message": "All rounds finished, ready for chronicle generation"}`).
  - [ ] Implement checks to prevent answering out of order or re-submitting answers to already answered rounds.
  - [ ] Write tests verifying the state progression through rounds 1, 2, and 3, and the blocking of double answers.
