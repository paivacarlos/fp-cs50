# Epic 5: Chronicle Generation & Newspaper Styling
Transforming the transcript into a stylized sports article.

This document breaks down the tasks of Epic 5 into atomized steps to track implementation progress, commits, and Pull Requests.

---

## Technical Tasks

### Phase 1: Backend & Gemini Integration (Services Layer)
- [x] **Task 5.1.1:** Create the Pydantic schema/model `ChronicleResponse` with `headline: str` and `chronicle: str` fields in [services/gemini.py](../services/gemini.py).
- [x] **Task 5.1.2:** Implement the `generate_chronicle(image_path: str, context: str, history: list) -> dict` function in [services/gemini.py](../services/gemini.py), using `response_mime_type="application/json"` and passing the `ChronicleResponse` schema in the `response_schema` of the Gemini SDK.
- [x] **Task 5.1.3:** Write unit tests in [tests/test_gemini.py](../tests/test_gemini.py) to mock the Gemini API and ensure that `generate_chronicle` processes and returns the correct JSON structure.

### Phase 2: Persistence & Endpoint Flow (Database & Routes Layer)
- [x] **Task 5.2.1:** Update the `POST /api/conference/answer` endpoint in [routes/api.py](../routes/api.py) to detect when the completed round is **Round 3**.
- [x] **Task 5.2.2:** Integrate the call to `generate_chronicle` when Round 3 is answered, passing the accumulated question/answer history from the database, the screenshot, and the initial context.
- [x] **Task 5.2.3:** Create a SQL transaction/query to update the `headline` and `chronicle` fields in the `conferences` table for the current conference.
- [x] **Task 5.2.4:** Create a new route `GET /conference/<int:conference_id>/newspaper` in [routes/main.py](../routes/main.py) protected by `@login_required` that validates if the conference belongs to the logged-in user, retrieves the database data, and renders the newspaper template.
- [x] **Task 5.2.5:** Add integration tests in [tests/test_api.py](../tests/test_api.py) covering:
  - The successful saving of the headline and chronicle upon completing Round 3.
  - Unauthorized access protection and correct authorization verification when viewing the `/conference/<id>/newspaper` route.
  - The database rollback in case the chronicle generation by Gemini fails in Round 3.

### Phase 3: Newspaper Interface & Styling (Frontend Layer)
- [x] **Task 5.3.1:** Create the new template `templates/newspaper.html` inheriting from [templates/base.html](../templates/base.html).
- [x] **Task 5.3.2:** Design the semantic HTML markup in `newspaper.html` containing:
  - A classic newspaper header (e.g., "THE DAILY PRESS" with a gothic/serif font, date, and authorship).
  - The main headline (`headline`) with visual emphasis.
  - The screenshot image (stylized with a vintage filter, such as grayscale or sepia).
  - The chronicle text (`chronicle`).
- [x] **Task 5.3.3:** Create the stylesheet [static/css/newspaper.css](../static/css/newspaper.css) applying parchment/aged paper style background colors (`#f4ebd0` or similar) and classic typography with serif fonts.
- [x] **Task 5.3.4:** Implement column layout for the chronicle body using CSS Columns (`column-count`, `column-gap`, and `column-rule`).
- [x] **Task 5.3.5:** Apply micro-animation effects (e.g., subtle paper texture) and a Drop Cap style (first letter of the chronicle text classically stylized).
- [x] **Task 5.3.6:** Update the frontend JavaScript logic (which handles Q&A requests) to redirect the user to the `/conference/<id>/newspaper` route as soon as the Round 3 completion status is received.

### Phase 4: E2E Interface Tests (UI Quality Assurance)
- [ ] **Task 5.4.1:** Write an E2E test with Playwright in [tests/test_ui.py](../tests/test_ui.py) simulating a manager's flow submitting answers until completing Round 3 and verifying the redirect.
- [ ] **Task 5.4.2:** Add assertions in the E2E test to verify that the headline, chronicle text, and stylized screenshot are visible on the newspaper page.
