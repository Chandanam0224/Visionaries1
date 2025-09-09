# db_init.py
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'tickets.db'

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT,
        raw_text TEXT,
        priority TEXT,
        intent TEXT,
        sentiment TEXT,
        compliance_flag INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS ai_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        step TEXT,
        detail TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("DB initialized at", DB)
