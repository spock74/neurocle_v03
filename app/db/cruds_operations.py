import sqlite3
from datetime import datetime
from app.core.settings.conf import logger
from typing import Dict, List, Optional

# Função para conectar ao banco de dados
def connect_db():
    return sqlite3.connect('neurocle_v03.db')
# ----------------------------------------------------------------------------



# Função para criar um novo usuário
# ----------------------------------------------------------------------------
def get_user_by_email(email: str):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, email, username, hashed_password FROM users WHERE email = ?",
            (email,)
        )
        user = cursor.fetchone()
        if user:
            return {
                "id": user[0],
                "email": user[1],
                "username": user[2],
                "hashed_password": user[3]
            }
        return None
    finally:
        conn.close()

def create_user(username: str, email: str, hashed_password: str):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (username, email, hashed_password)
            VALUES (?, ?, ?)
            """,
            (username, email, hashed_password)
        )
        conn.commit()
        return {"username": username, "email": email}
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating user: {str(e)}")
    finally:
        conn.close()
# ----------------------------------------------------------------------------        

# Função para ler todos os usuários
def read_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users
# ----------------------------------------------------------------------------
def check_users_table():
    conn = sqlite3.connect('neurocle_v03.db')
    cursor = conn.cursor()
    
    # Verificar se a tabela existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='users'
    """)
    
    if not cursor.fetchone():
        # Criar tabela se não existir
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        print("Table 'users' created")
    
    # Mostrar estrutura da tabela
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("\nTable structure:")
    for col in columns:
        print(col)
    
    # Mostrar todos os usuários
    cursor.execute("SELECT id, username, email FROM users")
    users = cursor.fetchall()
    print("\nExisting users:")
    for user in users:
        print(user)
    
    conn.close()

# Execute a verificação
check_users_table()




# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
def get_user_by_email(email: str):
    """
    Get user from database by email
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        logger.info(f"Searching for user with email: {email}")  # Debug log
        cursor.execute(
            "SELECT id, email, username, hashed_password FROM users WHERE email = ?", 
            (email,)
        )
        user = cursor.fetchone()
        if user:
            logger.info("User found in database")  # Debug log
            return {
                "id": user[0],
                "email": user[1],
                "username": user[2],
                "hashed_password": user[3]
            }
        logger.warning("User not found in database")  # Debug log
        return None
    except Exception as e:
        logger.error(f"Database error: {str(e)}")  # Debug log
        raise
    finally:
        conn.close()
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
        



# Função para atualizar um usuário
# ----------------------------------------------------------------------------
def update_user(user_id, username=None, email=None, hashed_password=None):
    conn = connect_db()
    cursor = conn.cursor()
    if username:
        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
    if email:
        cursor.execute('UPDATE users SET email = ? WHERE id = ?', (email, user_id))
    if hashed_password:
        cursor.execute('UPDATE users SET hashed_password = ? WHERE id = ?', (hashed_password, user_id))
    conn.commit()
    conn.close()

# Função para deletar um usuário
def delete_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
# ------------------ CRUD USERS -----------------------------------------
# ----------------------------------------------------------------------------




# Função para criar um novo assistente
# ----------------------------------------------------------------------------
def insert_assistant_in_db(id_asst:str,
                        object: str,
                        created_at: str,
                        name: str,
                        description: str,
                        model: str,
                        instructions: str,
                        tools: str,
                        metadata: str,
                        temperature: str,
                        top_p: str
                    ):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO assistants_table (id_asst, object, created_at, name, description, model, instructions,tools, metadata, temperature, top_p)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_asst, object, created_at, name, description, model, instructions,tools, metadata, temperature, top_p))
    conn.commit()
    logger.debug(f"::Zenh:: Assistant ID {id_asst} inserida no DB sqlite")
    conn.close()
# ----------------------------------------------------------------------------



# Função para ler todos os assistentes
# ----------------------------------------------------------------------------
def read_assistants():
    try:
        conn = connect_db()  # Establish a connection to the database
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        cursor.execute('SELECT * FROM assistants_table')  # Execute a SQL query to select all records
        rows = cursor.fetchall()  # Fetch all rows returned by the query

        # Convert the list of tuples to a list of dictionaries
        assistants = []
        for row in rows:
            assistants.append({
                "id_asst": row[1],
                "object": row[2],
                "created_at": row[3],
                "name": row[4],
                "description": row[5],
                "model": row[6],
                "instructions": row[7],
                "tools": row[8],
                "metadata": row[9],
                "temperature": row[10],
                "top_p": row[11]
            })

        return assistants  # Return the list of dictionaries
    except Exception as e:
        print(f"Error reading assistants: {str(e)}")  # Log the error
        return []  # Return an empty list or handle the error as needed
    finally:
        conn.close()  # Ensure the connection is 
# ----------------------------------------------------------------------------
        
        

# Função para atualizar um assistente
def update_assistant(assistant_id, name=None, model=None, instructions=None, description=None, tools=None, metadata=None, temperature=None, top_p=None):
    conn = connect_db()
    cursor = conn.cursor()
    if name:
        cursor.execute('UPDATE assistants SET name = ? WHERE id = ?', (name, assistant_id))
    if model:
        cursor.execute('UPDATE assistants SET model = ? WHERE id = ?', (model, assistant_id))
    if instructions:
        cursor.execute('UPDATE assistants SET instructions = ? WHERE id = ?', (instructions, assistant_id))
    if description:
        cursor.execute('UPDATE assistants SET description = ? WHERE id = ?', (description, assistant_id))
    if tools:
        cursor.execute('UPDATE assistants SET tools = ? WHERE id = ?', (tools, assistant_id))
    if metadata:
        cursor.execute('UPDATE assistants SET metadata = ? WHERE id = ?', (metadata, assistant_id))
    if temperature is not None:
        cursor.execute('UPDATE assistants SET temperature = ? WHERE id = ?', (temperature, assistant_id))
    if top_p is not None:
        cursor.execute('UPDATE assistants SET top_p = ? WHERE id = ?', (top_p, assistant_id))
    conn.commit()
    conn.close()
# ----------------------------------------------------------------------------


# Função para deletar um assistente
def delete_assistant(assistant_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM assistants WHERE id = ?', (assistant_id,))
    conn.commit()
    conn.close()
# ------------------ CRUD ASSISTANTS -----------------------------------------
# ----------------------------------------------------------------------------




# ----------------------------------------------------------------------------
# ------------------ CRUD VECTOR STORES --------------------------------------
def insert_vector_store(
    id_vector: str,
    name: str,
    created_at: int,
    status: str,
    file_counts_total: int,
    file_counts_completed: int,
    file_counts_in_progress: int,
    file_counts_failed: int,
    file_counts_cancelled: int,
    assistant_id: str
):
    """
    Insert a new vector store into the database.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        logger.info("Executing SQL insert for vector store")
        cursor.execute('''
            INSERT INTO vector_stores (
                id_vector,
                name,
                created_at,
                status,
                file_counts_total,
                file_counts_completed,
                file_counts_in_progress,
                file_counts_failed,
                file_counts_cancelled,
                assistant_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            id_vector,
            name,
            created_at,
            status,
            file_counts_total,
            file_counts_completed,
            file_counts_in_progress,
            file_counts_failed,
            file_counts_cancelled,
            assistant_id
        ))
        conn.commit()
        logger.info(f"Vector store {id_vector} inserted successfully")
    except Exception as e:
        logger.error(f"Database error during insert: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()




# Função para ler todos os vector stores
# -------------------------------------------------------------------
def read_vector_stores():
    """
    Read all vector stores from the database.
    """
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT 
                id_vector,
                name,
                created_at,
                status,
                file_counts_total,
                file_counts_completed,
                file_counts_in_progress,
                file_counts_failed,
                file_counts_cancelled
            FROM vector_stores
        ''')
        vector_stores = cursor.fetchall()
        logger.info(f"Retrieved {len(vector_stores)} vector stores from database")
        return vector_stores
    except Exception as e:
        logger.error(f"Error reading vector stores: {str(e)}")
        raise
    finally:
        conn.close()


# Função para atualizar um vector store
# -------------------------------------------------------------------
def update_vector_store(
    id_vector: str,
    name: str = None,
    status: str = None,
    file_counts_total: int = None,
    file_counts_completed: int = None,
    file_counts_in_progress: int = None,
    file_counts_failed: int = None,
    file_counts_cancelled: int = None
):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        if name:
            cursor.execute('UPDATE vector_stores SET name = ? WHERE id_vector = ?', (name, id_vector))
        if status:
            cursor.execute('UPDATE vector_stores SET status = ? WHERE id_vector = ?', (status, id_vector))
        if file_counts_total is not None:
            cursor.execute('UPDATE vector_stores SET file_counts_total = ? WHERE id_vector = ?', (file_counts_total, id_vector))
        if file_counts_completed is not None:
            cursor.execute('UPDATE vector_stores SET file_counts_completed = ? WHERE id_vector = ?', (file_counts_completed, id_vector))
        if file_counts_in_progress is not None:
            cursor.execute('UPDATE vector_stores SET file_counts_in_progress = ? WHERE id_vector = ?', (file_counts_in_progress, id_vector))
        if file_counts_failed is not None:
            cursor.execute('UPDATE vector_stores SET file_counts_failed = ? WHERE id_vector = ?', (file_counts_failed, id_vector))
        if file_counts_cancelled is not None:
            cursor.execute('UPDATE vector_stores SET file_counts_cancelled = ? WHERE id_vector = ?', (file_counts_cancelled, id_vector))
        conn.commit()
    finally:
        conn.close()
# -------------------------------------------------------------------



# Função para deletar um vector store
# -------------------------------------------------------------------
def delete_vector_store(id_vector: str):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM vector_stores WHERE id_vector = ?', (id_vector,))
        conn.commit()
    finally:
        conn.close()
# --------------------------------------------------------------------
# ------------------ FIM CRUD VECTOR STORES --------------------------
   
# para endpoint de listar todas questoes
## -------------------------------------------------------------------------    
## -------------------------------------------------------------------------    
def get_questions(
    skip: int = 0,
    limit: int = 10,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    tag: Optional[str] = None
):
    """
    Get questions from database with optional filtering
    """
    try:
        conn = sqlite3.connect('neurocle_v03.db')
        cursor = conn.cursor()
        
        # Construir query base
        query = """
            SELECT 
                q.id,
                q.title,
                q.content,
                q.answer,
                q.subject,
                q.difficulty,
                q.created_at,
                q.updated_at,
                q.created_by,
                GROUP_CONCAT(t.name) as tags
            FROM questions q
            LEFT JOIN question_tags qt ON q.id = qt.question_id
            LEFT JOIN tags t ON qt.tag_id = t.id
        """
        
        # Adicionar condições WHERE
        conditions = []
        params = []
        
        if subject:
            conditions.append("q.subject = ?")
            params.append(subject)
            
        if difficulty:
            conditions.append("q.difficulty = ?")
            params.append(difficulty)
            
        if tag:
            conditions.append("t.name = ?")
            params.append(tag)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        # Adicionar GROUP BY, ORDER BY e LIMIT
        query += """
            GROUP BY q.id
            ORDER BY q.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, skip])
        
        # Executar query
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Formatar resultados
        questions = []
        for row in rows:
            question = {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "answer": row[3],
                "subject": row[4],
                "difficulty": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "created_by": row[8],
                "tags": row[9].split(',') if row[9] else []
            }
            questions.append(question)
            
        return questions
        
    except Exception as e:
        logger.error(f"Database error in get_questions: {str(e)}")
        raise
    finally:
        conn.close()

# ===========

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




# Exemplo de uso
if __name__ == "__main__":
    # Criar um novo usuário
    create_user("john_doe", "john@example.com", "hashed_password123")
    
    # Ler todos os usuários
    users = read_users()
    print("Users:", users)

    # Atualizar um usuário (supondo que o ID do usuário seja 1)
    update_user(1, username="john_updated")

    # Deletar um usuário (supondo que o ID do usuário seja 1)
    delete_user(1)

    # Criar um novo assistente
    create_assistant("Assistant 1", "gpt-4o-mini", "Some instructions", "Some description", '{"tool1": "value1"}', '{"meta": "data"}', 0.5, 1.0, "user_code_1")

    # Ler todos os assistentes
    assistants = read_assistants()
    print("Assistants:", assistants)

    # Atualizar um assistente (supondo que o ID do assistente seja 1)
    update_assistant(1, name="Assistant 1 Updated")

    # Deletar um assistente (supondo que o ID do assistente seja 1)
    delete_assistant(1)
    
 