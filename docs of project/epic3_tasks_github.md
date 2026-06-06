# GitHub Projects Tasks - Epic 3: Press Conference Setup (Inputs & Media)

This document contains the detailed task definitions for **Epic 3** based on the [engineering_spec.md](engineering_spec.md). You can copy and paste the titles and descriptions directly to create "Draft Issues" or "Issues" in your GitHub Project.

---

## 1. Create setup/dashboard UI and route
* **Title:** `[Epic 3 - Task 1] Create dashboard/setup UI and view route`
* **Description:**
  Build the user interface for the press conference configuration (`templates/setup.html`), extending from `base.html` and providing a modern, responsive page layout to collect starting game parameters.
* **Acceptance Criteria:**
  - [ ] Replace the existing placeholder in `templates/setup.html` with a complete setup page layout.
  - [ ] Integrate a form pointing to the conference initiation endpoint (to be built in Epic 4).
  - [ ] The form must include:
    - A file input field for uploading the match screenshot.
    - A textarea for typing the initial match context.
    - A stylized submit button (e.g., "Start Press Conference").
  - [ ] Ensure full responsiveness and look-and-feel alignment with the project's styling and theme setup.

---

## 2. Implement drag-and-drop and instantaneous image preview
* **Title:** `[Epic 3 - Task 2] Implement drag-and-drop upload and instant image preview`
* **Description:**
  Add frontend JavaScript interactivity to improve user experience, allowing users to drag and drop image files directly onto the target zone and preview them immediately before submitting.
* **Acceptance Criteria:**
  - [ ] Create a visually distinct upload zone/drop-zone in `setup.html`.
  - [ ] Implement JS event listeners for `dragover`, `dragleave`, and `drop` events to change styling when dragging files over the area.
  - [ ] Read the dragged or selected file via JavaScript's `FileReader` API and render a preview thumbnail image immediately on-screen.
  - [ ] Restrict drop-zone selection on the client-side to standard image formats (PNG, JPG, JPEG, GIF).

---

## 3. Reactive character counter and strict length checks
* **Title:** `[Epic 3 - Task 3] Implement reactive text counter and character limit validations`
* **Description:**
  Add a client-side reactive counter showing remaining characters allowed in the context textarea, combined with a strict backend length validation to enforce the 200-character cap.
* **Acceptance Criteria:**
  - [ ] Add a real-time reactive character counter next to the textarea that ticks down from 200.
  - [ ] Enforce `maxlength="200"` directly on the textarea element in the HTML.
  - [ ] In the backend handler processing the request, add validation to check that the context length is between 1 and 200 characters inclusive.
  - [ ] Implement unit or API tests validating success and failure conditions (empty context, context size within limit, context size exceeding limit).

---

## 4. Secure file upload service with collision avoidance
* **Title:** `[Epic 3 - Task 4] Implement secure file saving and collision avoidance`
* **Description:**
  Develop backend utility functions to securely process and store uploaded screenshots in `static/uploads/`, validating file type safety and renaming files using secure hashes to avoid collisions.
* **Acceptance Criteria:**
  - [ ] Verify the upload directory `static/uploads/` exists (or create it programmatically if missing).
  - [ ] Implement backend checks to ensure only valid image extensions are accepted (e.g., `png`, `jpg`, `jpeg`, `gif`).
  - [ ] Generate secure, unique filenames using cryptographic hashing (e.g., MD5/SHA-256 of contents, or using UUID + timestamp) to prevent duplicate name conflicts or directory traversal exploits.
  - [ ] Save the file physically to the filesystem and return its relative path for database recording.
  - [ ] Create tests simulating successful and blocked uploads (unsupported file extensions, invalid payloads).
