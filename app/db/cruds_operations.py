import sqlite3
from datetime import datetime

# Função para conectar ao banco de dados
def connect_db():
    return sqlite3.connect('neurocle_v03.db')

# Função para criar um novo usuário
def create_user(username, email, hashed_password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, hashed_password)
        VALUES (?, ?, ?)
    ''', (username, email, hashed_password))
    conn.commit()
    conn.close()

# Função para ler todos os usuários
def read_users():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

# Função para atualizar um usuário
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

# Função para criar um novo assistente
def insert_assistant_in_db(id_asst:str, 
                           name:str, 
                           model:str, 
                           instructions:str, 
                           description:str, 
                           tools:str, 
                           metadata:str, 
                           temperature:float, 
                           top_p:float):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO assistants_table (id_asst, name, model, instructions, description, tools, metadata, temperature, top_p)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (id_asst, name, model, instructions, description, tools, metadata, temperature, top_p))
    conn.commit()
    conn.close()

# Função para ler todos os assistentes
def read_assistants():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assistants')
    assistants = cursor.fetchall()
    conn.close()
    return assistants

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

# Função para deletar um assistente
def delete_assistant(assistant_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM assistants WHERE id = ?', (assistant_id,))
    conn.commit()
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