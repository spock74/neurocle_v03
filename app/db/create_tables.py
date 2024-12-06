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
        name TEXT NOT NULL,
        model TEXT DEFAULT 'gpt-4o-mini',
        instructions TEXT,
        description TEXT,
        tools TEXT,  -- Armazenar como JSON (pode ser armazenado como TEXT)
        metadata TEXT,  -- Armazenar como JSON (pode ser armazenado como TEXT)
        temperature REAL,
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