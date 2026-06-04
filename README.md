# PressConference EA

PressConference EA is a web application focused on engagement and sports storytelling for **EA FC 26** players. The system transforms the stats from a post-match screenshot and a brief player comment into an interactive, immersive 3-round press conference, where the AI acts as the reporter and the user as the coach. At the end, the app generates a stylized sports article covering the conference.

## Project Structure

* `docs of project/`: Contains project specification files and task definitions.
* `requirements.txt`: List of Python dependencies for the project.

## Installation & Setup

Follow these steps to set up and run the project locally.

### 1. Prerequisites

Make sure you have Python 3.10+ installed on your machine. You can check your version by running:
```bash
python --version
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to isolate the project dependencies. Create one by running:
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

Activate the virtual environment depending on your operating system and shell:

* **Windows PowerShell:**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Windows CMD:**
  ```cmd
  .\venv\Scripts\activate.bat
  ```
* **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```

Once activated, you will see `(venv)` at the beginning of your terminal prompt.

### 4. Install Dependencies

Install all required Python packages defined in `requirements.txt`:
```bash
pip install -r requirements.txt
```

This will install the following main packages:
* **Flask:** Backend web framework.
* **google-generativeai:** SDK to interact with Gemini API.
* **python-dotenv:** To manage environment variables.
* **werkzeug:** Helper library for password hashing.

## Database Usage & Helpers

To simplify database operations and avoid repeating connection boilerplate, you can use the database service located in [services/db.py](file:///c:/Users/carlo/cs50/chapter_10/project/fp-cs50/services/db.py).

### Importing the Service

Import the helpers into your routes or scripts:
```python
from services.db import query_db, execute_db, get_db
```

### 1. Fetching Data (`query_db`)

Use `query_db` to run `SELECT` queries. 

* **To fetch multiple records:**
  ```python
  users = query_db("SELECT * FROM users")
  for user in users:
      print(user["username"]) # Access columns by name thanks to sqlite3.Row
  ```

* **To fetch a single record:**
  Set `one=True` to return only the first row (or `None` if no record is found):
  ```python
  user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
  if user:
      print(user["username"])
  ```

### 2. Modifying Data (`execute_db`)

Use `execute_db` to run `INSERT`, `UPDATE`, or `DELETE` queries. It automatically commits changes to the database.

* **Inserting a record:**
  ```python
  execute_db("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_password))
  ```

* **Updating a record:**
  ```python
  execute_db("UPDATE conferences SET headline = ? WHERE id = ?", (new_headline, conf_id))
  ```

### 3. Direct Connection Control (`get_db`)

If you need full control over the database connection (e.g. managing transactions manually), use the connection context manager:
```python
with get_db() as conn:
    # Run operations directly on the connection 'conn'
    cursor = conn.cursor()
    cursor.execute("...")
    # Connection is automatically closed at the end of the block
```
