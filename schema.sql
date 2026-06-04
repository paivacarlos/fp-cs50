-- Enable foreign key support in SQLite
PRAGMA foreign_keys = ON;

-- 1. Users Table (Authentication)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL
);

-- 2. Conferences Table (Press Conferences Metadata and Outputs)
CREATE TABLE IF NOT EXISTS conferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    screenshot_path TEXT NOT NULL,
    initial_context TEXT NOT NULL, -- User's match notes (up to 200 chars)
    headline TEXT,                 -- AI generated headline (NULL until final round completes)
    chronicle TEXT,                -- AI generated article text (NULL until final round completes)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Rounds Table (Dialog logs for the 3 Q&A rounds)
CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conference_id INTEGER NOT NULL,
    round_number INTEGER NOT NULL, -- Values: 1, 2, or 3
    question TEXT NOT NULL,        -- AI generated reporter question
    answer TEXT,                   -- User's answer (NULL until submitted)
    FOREIGN KEY (conference_id) REFERENCES conferences(id) ON DELETE CASCADE
);

-- Indices for performance optimization on foreign keys
CREATE INDEX IF NOT EXISTS idx_conferences_user_id ON conferences(user_id);
CREATE INDEX IF NOT EXISTS idx_rounds_conference_id ON rounds(conference_id);
