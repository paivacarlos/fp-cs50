# Product Specification: PressConference EA

## 1. Product Overview
The **PressConference EA** is a web application focused on engagement and sports storytelling for **EA FC 26** players. The system transforms the cold metrics from a post-match screenshot and a brief player comment into an interactive, immersive 3-round press conference, where the AI acts as the reporter and the user as the coach. At the end, the app generates journalistic coverage based on the provided answers.

---

## 2. Feature Scope

### Feature 1: Press Conference Setup Panel
* **Media Upload:** A file input field for the user to upload an image (a screenshot of the post-match game statistics).
* **Additional Context:** A text area of up to 200 characters for the user to insert match nuances not visible in the screenshot (e.g., *"The opposing goalkeeper saved everything, and my striker missed an open goal"*).
* **Start Conference:** An action button that:
  1. Validates inputs (verifies if the image exists and if the comment is within the 200-character limit).
  2. Submits the data to trigger the first round of the press conference.

### Feature 2: Interactive Press Conference Engine (3-Round Loop)
This is the core dynamic of the application. The system maintains session/conversation state and manages a closed loop of **Question (AI) ➔ Answer (User)** for exactly 3 rounds:
* **Round 1:** The AI analyzes the screenshot (OCR/Vision) + the user's initial context, then generates **Question 1** in a sports reporter tone. The user types their answer and submits.
* **Round 2:** The AI evaluates the user's previous answer within the original match context and asks **Question 2** (either a follow-up or a transition to a new topic). The user types their answer and submits.
* **Round 3:** The AI asks **Question 3** (the final question of the press conference). The user types their final answer and submits.

### Feature 3: Wrap-up and "The Headline of the Day"
* **Sports Chronicle Generation:** After the user submits the third answer, the question-and-answer interface closes.
* **Content Delivery:** The AI compiles the initial screenshot, context, and all 3 answers to generate:
  * **Newspaper Headline:** An eye-catching, stylized sports headline.
  * **Article/Summary:** A chronicle of the conference in the style of a printed newspaper or sports portal, summarizing the coach's stance and match narrative.

### Feature 4: Persistence and History
* **Auto-Save:** Once the headline and chronicle are generated, all data from that press conference (image metadata/path, context, Q&A rounds, and final output) is automatically saved to the database, linked to the active user's account.
* **History Page:** A separate section on the site where the logged-in user can browse their own past press conferences in a timeline or grid/card format.
* **Retrospective Viewing:** Clicking a history entry allows the user to review the uploaded screenshot, initial comment, and the final headline/summary generated.

### Feature 5: User Authentication (Login & Register)
* **Registration:** A sign-up form allowing users to create an account with a unique username and password.
* **Login:** A secure sign-in form for users to access their accounts.
* **Session Management:** Once logged in, a session cookie keeps the user authenticated. Only authenticated users can access the Setup Panel, the Interactive Press Conference, and the History Page. Anonymous users will be redirected to the login/register screen.
* **Log Out:** An option to terminate the current session securely.

---

## 3. Business Rules and Constraints
1. **Text Limitation:** The user's initial comment cannot exceed 200 characters.
2. **Session State / Sequencing:** The user must answer questions sequentially (e.g., cannot skip to Question 2 without answering Question 1).
3. **Mandatory Completion:** The newspaper chronicle is only generated if the user completes all 3 rounds of the press conference.
4. **Key Protection:** The system must handle AI API keys centrally on the server (never exposed to the client/browser).
5. **Access Control:** All core features (Setup, Press Conference, History) require user authentication. User data is isolated, meaning a user can only view their own history.
