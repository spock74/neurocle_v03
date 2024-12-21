import sqlite3

def create_tables():
    # Conectar ao banco de dados SQLite (ou criar se não existir)
    conn = sqlite3.connect('neurocle_v03.db')
    cursor = conn.cursor()

    # Criação da tabela users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        hashed_password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    # Criação da tabela assistants
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assistants_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_asst TEXT NOT NULL, 
        object TEXT NOT NULL,
        created_at TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        model TEXT DEFAULT 'gpt-4o-mini',
        instructions TEXT NOT NULL,
        tools TEXT,  -- Armazenar como JSON (pode ser armazenado como TEXT)
        metadata TEXT,  -- Armazenar como JSON (pode ser armazenado como TEXT,
        temperature REAL NOT NULL,
        top_p REAL
    );
    ''')

    # Criação da tabela threads
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        assistant_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (assistant_id) REFERENCES assistants(id) ON DELETE CASCADE
    );
    ''')
    
    
    
    
    # Criar tabela para vector stores
    cursor.execute('''    
    -- Criar tabela para vector stores
    CREATE TABLE IF NOT EXISTS vector_stores (
        id_vector VARCHAR(255) PRIMARY KEY,
        name VARCHAR(255),
        created_at BIGINT,
        status VARCHAR(50),
        file_counts_total INT,
        file_counts_completed INT,
        file_counts_in_progress INT,
        file_counts_failed INT,
        file_counts_cancelled INT,
        assistant_id VARCHAR(255),  -- Referência ao assistente associado
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')



    # Criação da tabela messages
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        thread_id INTEGER NOT NULL,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
    );
    ''')

    # Salvar (commit) as mudanças e fechar a conexão
    conn.commit()
    conn.close()
    print("Tabelas criadas com sucesso!")
    
    
    
### ================================================
def create_questions_tables():
    conn = sqlite3.connect('neurocle_v03.db')
    cursor = conn.cursor()
    
    try:
        # Tabela de questões
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            subject TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            created_by TEXT NOT NULL,
            FOREIGN KEY (created_by) REFERENCES users(email)
        )
        ''')
        
        # Tabela de tags
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Tabela de relação questões-tags
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_tags (
            question_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (question_id, tag_id),
            FOREIGN KEY (question_id) REFERENCES questions(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        )
        ''')
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



# Executar a função para criar as tabelas
if __name__ == "__main__":
    create_tables()
    create_questions_tables()