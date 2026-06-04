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
