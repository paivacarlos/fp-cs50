# Epic 6: History Dashboard & Retro Modal
Viewing past conferences securely.

This document breaks down the tasks of Epic 6 into atomized steps to track implementation progress, commits, and Pull Requests. It also includes the postponed E2E Playwright UI tests at the end.

---

## Technical Tasks

### Phase 1: Backend & API (Database & Routes Layer)
- [x] **Task 6.1.1:** Create the `GET /history` route in [routes/main.py](../routes/main.py) protected by `@login_required` that renders the `templates/history.html` template.
- [x] **Task 6.1.2:** Implement the database query in the `GET /history` route to retrieve only the completed conferences (`headline IS NOT NULL AND chronicle IS NOT NULL`) associated with the session's `user_id`, ordered by `created_at DESC`, and pass them to the template.
- [x] **Task 6.1.3:** Write integration tests in [tests/test_api.py](../tests/test_api.py) to ensure that accessing the `/history` route redirects unauthorized users to `/login` and returns `200 OK` for logged-in users.
- [x] **Task 6.1.4:** Create the new endpoint `GET /api/conference/<int:conference_id>/details` in [routes/api.py](../routes/api.py) protected by `@login_required` that validates conference ownership, fetches the conference data and all associated `rounds`, and returns them in JSON format.
- [x] **Task 6.1.5:** Write integration tests in [tests/test_api.py](../tests/test_api.py) covering the details endpoint: success (correct return of structured JSON), 404 error (non-existent conference), and 403 error (unauthorized access to other users' conferences).

### Phase 2: History Interface & Navigation (Frontend Layer)
- [x] **Task 6.2.1:** Create the new template `templates/history.html` inheriting from [templates/base.html](../templates/base.html).
- [x] **Task 6.2.2:** Design the HTML markup in `history.html` containing a grid or timeline displaying cards (`.history-card`) for each conference (with formatted date, headline, and screenshot thumbnail).
- [x] **Task 6.2.3:** Create the stylesheet [static/css/history.css](../static/css/history.css) (or update the existing one) applying modern design to the history cards (glassmorphism, gradient borders, and scale micro-animations on hover).
- [x] **Task 6.2.4:** Update global navigation by adding cross-links:
  - A quick access link to history (e.g., "View History") in the header or footer of [templates/setup.html](../templates/setup.html).
  - A return link (e.g., "← Back to Setup") in the header or footer of [templates/history.html](../templates/history.html).

### Phase 3: Retrospective Modal & Interactivity (JS Layer)
- [x] **Task 6.3.1:** Design the HTML markup of the Retrospective Modal (`#retro-modal`) in `history.html` (containing a close button, area for Q&A transcript, and area to render the newspaper).
- [x] **Task 6.3.2:** Style the modal (`.modal-overlay`, `.modal-content`, Q&A chat bubbles) in [static/css/history.css](../static/css/history.css), configuring a translucent overlay and smooth entrance animations (fade-in / scale).
- [x] **Task 6.3.3:** Implement JavaScript logic in `history.html` to:
  - Add click event listeners to each `.history-card`.
  - Send a request via `fetch()` to the `/api/conference/<id>/details` endpoint.
  - Dynamically populate the chat structure (questions/answers) and the newspaper layout inside the modal.
  - Display the modal and handle close actions (clicking the "X" button, the external area, or pressing the Esc key).

### Phase 4: Project E2E Interface Tests (UI Quality Assurance)
- [ ] **Task 6.4.1:** Write the E2E test of **Epic 5** with Playwright in [tests/test_ui.py](../tests/test_ui.py) simulating a manager's flow submitting answers until completing Round 3 and verifying the redirect to the newspaper, validating visible elements on the final page.
- [ ] **Task 6.4.2:** Write the E2E test of **Epic 6** with Playwright in [tests/test_ui.py](../tests/test_ui.py) simulating the navigation flow:
  - Login and navigate to the `/history` route.
  - Click on a history card and validate that the Retrospective Modal opens correctly.
  - Verify that the conference transcript (questions and answers) and the headline are readable inside the modal.
