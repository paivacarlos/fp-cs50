import sqlite3
import os
from contextlib import contextmanager
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Define the database path (defaults to conference_data.db in the root)
DATABASE_PATH = os.getenv("DATABASE_PATH", "conference_data.db")

@contextmanager
def get_db():
    """
    Context manager for database connections.
    
    Ensures that the connection is opened, configured, and automatically
    closed when the block is exited, even if errors occur.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Configure row_factory to return sqlite3.Row objects (access columns by name)
    conn.row_factory = sqlite3.Row
    
    # Enable Foreign Key constraints check
    conn.execute("PRAGMA foreign_keys = ON;")
    
    try:
        yield conn
    finally:
        conn.close()

def query_db(query, args=(), one=False):
    """
    Helper function to query the database and fetch results.
    
    Usage:
        users = query_db("SELECT * FROM users")
        user = query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    """
    with get_db() as conn:
        cursor = conn.execute(query, args)
        results = cursor.fetchall()
        return (results[0] if results else None) if one else results

def execute_db(query, args=()):
    """
    Helper function to execute database modifications (INSERT, UPDATE, DELETE).
    Automatically commits changes.
    
    Usage:
        execute_db("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hashed_pw))
    """
    with get_db() as conn:
        conn.execute(query, args)
        conn.commit()

def init_db():
    """
    Initializes the database by executing the schema.sql script.
    
    Reads the schema definition and creates all required tables and indexes.
    """
    # Locate schema.sql in the project root relative to this file
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(project_root, "schema.sql")
    
    with get_db() as conn:
        with open(schema_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
            
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
