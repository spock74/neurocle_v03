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
        hashed_password TEXT NOT NULL
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

# def drop_vector_stores_table():
#     # Conectar ao banco de dados SQLite (ou criar se não existir)
#     conn = sqlite3.connect('neurocle_v03.db')
#     cursor = conn.cursor()

#     try:
#         # Drop da tabela vector_stores
#         cursor.execute('DROP TABLE IF EXISTS vector_stores;')
        
#         # Commit das mudanças
#         conn.commit()
#         print("Tabela vector_stores removida com sucesso!")
#     except Exception as e:
#         print(f"Erro ao remover tabela: {e}")
#     finally:
#         # Fechar a conexão
#         conn.close()

# drop_vector_stores_table()


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

# Executar a função para criar as tabelas
if __name__ == "__main__":
    create_tables()