import os
import time
import requests
import logging
import argparse  # Importa o módulo argparse
from typing import List
from app.core.asst.prompt_cefaleias_v02 import formatted_instructions_1

# Configurações
API_BASE_URL = "http://localhost:8000/api/v1"
API_KEY = os.getenv("OPENAI_NEUROCURSO_API_KEY")

# Configuração do logging
logging.basicConfig(filename='assistants_creation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para validar e-mail
def is_valid_email(email: str) -> bool:
    return not email.startswith('_')

# Função para criar a vector store
def create_vector_store(file_paths: List[str]) -> str:
    url = f"{API_BASE_URL}/vectorstores"
    payload = {
        "file_paths": file_paths  # Certifique-se de que o payload está estruturado corretamente
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx e 5xx
        return response.json()['vector_store_id']  # Retorna o ID da vector store criada
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating vector store: {e}")
        return None

# Função para criar assistente
# Função para criar assistente
def create_assistant(email: str, model: str, instructions: str, description: str, temperature: float, vector_store_id: str) -> str:
    url = f"{API_BASE_URL}/assistant"
    timestamp = int(time.time())
    assistant_name = f'assst_{email}_{timestamp}_{vector_store_id}'  # Nome do assistente com o padrão especificado
    payload = {
        "name": assistant_name,
        "model": model,
        "instructions": instructions,
        "description": description,
        "user_id": email,
        "temperature": temperature,
        "metadata": {
            "vectorstore_id": vector_store_id  # Adiciona o ID da vector store nos metadados
        }
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx e 5xx
        if 'id_asst' in response.json():  # Verifica se a chave 'id_asst' existe
            return response.json()['id_asst']  # Retorna o ID do assistente criado
        else:
            logging.error(f"Response does not contain 'id_asst': {response.json()}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error creating assistant for {email}: {e}")
        return None

# Função para listar arquivos PDF
def list_pdf_files(directory: str) -> List[str]:
    if not os.path.exists(directory):
        logging.error(f"The directory {directory} does not exist.")
        return []

    pdf_files = [os.path.abspath(os.path.join(directory, f)) for f in os.listdir(directory) if f.endswith('.pdf')]
    print("PDF files found:", pdf_files)  # Adiciona depuração para verificar os arquivos encontrados
    return pdf_files

# Função principal
def main(vector_store_id: str = None, pdf_directory: str = None):
    # Lista os arquivos PDF
    pdf_files = list_pdf_files(pdf_directory)

    # Verifica se há arquivos PDF válidos
    if not pdf_files:
        logging.error("No valid PDF files found in the specified directory.")
        return

    # Se vector_store_id não for fornecido, cria a vector store
    if not vector_store_id:
        logging.info("Creating vector store with the found PDF files...")
        vector_store_id = create_vector_store(pdf_files)
        if not vector_store_id:
            logging.error("Failed to create vector store. Exiting.")
            return
        logging.info(f'Vector store global criada: {vector_store_id}')
    else:
        logging.info(f'Usando vector store fornecida: {vector_store_id}')

    # Lê os e-mails do arquivo
    with open('emails.txt', 'r') as f:
        emails = [line.strip() for line in f.readlines()]

    # Cria um assistente para cada e-mail
    for email in emails:
        if is_valid_email(email):
            logging.info(f"Creating assistant for email: {email}")
            assistant_id = create_assistant(email, model="gpt-4o-mini", instructions=formatted_instructions_1, description="", temperature=0.2, vector_store_id=vector_store_id)
            if assistant_id:
                logging.info(f'Assistente criado: {assistant_id} para o email: {email}')
            else:
                logging.warning(f'Assistente não criado para o email: {email}')
        else:
            logging.warning(f'E-mail inválido: {email}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assistente de criação com vector store e diretório de PDFs.")
    parser.add_argument("--vector_store_id", type=str, help="ID da vector store a ser usada.")
    parser.add_argument("--pdf_directory", type=str, required=True, help="Caminho absoluto para a pasta que contém os PDFs.")
    args = parser.parse_args()

    main(vector_store_id=args.vector_store_id, pdf_directory=args.pdf_directory)