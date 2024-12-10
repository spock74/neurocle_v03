import sqlite3
from app.core.settings.conf import logger

def init_db():
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect('neurocle_v03.db')
        cursor = conn.cursor()
        
        # Criar tabela users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()