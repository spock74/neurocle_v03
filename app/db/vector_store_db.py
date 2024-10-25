import sqlite3
from app.core.settings.conf import logger

DB_PATH = "vector_stores.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assistant_vector_stores (
            assistant_id TEXT PRIMARY KEY,
            vector_store_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_vector_store_id(assistant_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT vector_store_id FROM assistant_vector_stores WHERE assistant_id = ?", (assistant_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_vector_store_id(assistant_id, vector_store_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO assistant_vector_stores (assistant_id, vector_store_id)
        VALUES (?, ?)
    ''', (assistant_id, vector_store_id))
    conn.commit()
    conn.close()

# ---)))(((((******)))))
def init_question_log_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assistant_id TEXT NOT NULL,
            thread_id TEXT NOT NULL,
            question_text TEXT NOT NULL,
            user_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            response_json TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
# ---    
# ---    
def insert_question_log(assistant_id: str, thread_id: str, question_text: str, user_id: str, response_json: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO question_log (assistant_id, thread_id, question_text, user_id, response_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (assistant_id, thread_id, question_text, user_id, response_json))
    conn.commit()
    conn.close()
# ---)))(((((******)))))

# "assistant_id"
# :
# "asst_CBuAZ5PoR8mnn8APqOKh79E9"
# ,
# "user_id"
# :
# "user1234"
# ,
# "thread_id"
# :
# "thread_jApx1j4HMZbgVePQnLXtfmri"