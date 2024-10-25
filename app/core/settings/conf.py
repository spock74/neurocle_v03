# 
# deepeval login --confident-api-key f9b7mfTSy51yfxBMxleUqQIKO39w3CHibVoyEaI8aXU=
# 


# ----------------------------------------------------------------
import os, sys
import coloredlogs
import yaml
import logging  
import unittest
from pydantic import BaseModel
from pydantic_settings import BaseSettings
# ----------------------------------------------------------------


# ----------------------------------------------------------------
#! TODO: Adicionar os modelos de LLM que serão utilizados
#! Como VISAO, TTS, STT, embeddings, etc.
#! Passar esse valores para o arquivo de configuração yaml
#! bem como os valores ENVIRONMENT de API_KEY, etc.

API_BASE_URL = "http://localhost:8000/api/v1"

UI_LANGUAGE = "ui_config_pt_br.yaml"

LLM_MODEL_NAME_GPT_3_5_TURBO = "gpt-3.5-turbo"
LLM_MODEL_NAME_GPT_4_TURBO = "gpt-4-Turbo"
LLM_MODEL_NAME_GPT_4_o = "gpt-4o"
# ----------------------------------------------------------------
LLM_MODEL_NAME_GPT_4_o_MINI = "gpt-4o-mini"
# ----------------------------------------------------------------
URL_LLM_OPENAI = "https://api.openai.com/v1"
# ----------------------------------------------------------------
LLM_CLAUDE_API_KEY = ""
                                    
# ----------------------------------------------------------------
LLM_MODEL_NAME_OLLAMA_LLAMA_3_1_8b = "llama3.1:8b"  
LLM_MODEL_NAME_OLLAMA_MISTRAL = "mistral"
# ----------------------------------------------------------------

# ----------------------------------------------------------------
URL_LLM_LOCAL = "http://localhost:11434/api/generate"
# ----------------------------------------------------------------

# class Settings(BaseSettings):
#     # ... other settings ...
#     REDIS_HOST: str = "localhost"
#     REDIS_PORT: int = 6379
# # ----------------------------------------------------------------
# ENV_NAME_NEUROCURSO_API_KEY_CHATBOT = "OPENAI_NEUROCURSO_API_KEY"
# ENV_NAME_NEUROCURSO_ORG_CHATBOT  = "OPENAI_NEUROCURSO_ORGANIZATION_ID"
# ----------------------------------------------------------------


# Configuração do logging
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# Autor: Jose E Moraes

def setup_logger():
    logger = logging.getLogger()
    logger.disabled = False

    # Definir o nível de log para DEBUG
    logger.setLevel(logging.DEBUG)

    # Definir o formato do log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Criar um manipulador de log que escreve para um arquivo
    file_handler = logging.FileHandler('logs/file.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Criar um manipulador de log que escreve para o console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Adicionar cores aos logs no console
    coloredlogs.install(level='DEBUG', logger=logger)

    return logger

logger = setup_logger()


class Settings:
    """
    Classe para armazenar as configurações do projeto.

    Atributos:
        PROJECT_NAME (str): Nome do projeto.
        DATABASE_URL (str): URL do banco de dados.
        ENVIRONMENT (str): Ambiente de execução (desenvolvimento, produção, etc.).
    """
    PROJECT_NAME: str = "My Project"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/neurocurso")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    def __init__(self):
        logger.debug("Configurações carregadas: %s", self.__dict__)

settings = Settings()
logger.debug("Instância de Settings criada: %s", settings)
    

# -------------------------------------------------------------    
    
    
# # -------------------------------------------------------------
# class DatabaseConfig:
#     def __init__(self, host, user, password, port, database):
#         self.host = host
#         self.user = user
#         self.port = port
#         self.password = password
#         self.database = database
# # -------------------------------------------------------------

# # - Zehn Moraes
# # - Contains the configurations for the application.

# from pydantic_settings import BaseSettings
# from typing import List
# import logging
# import os


# class Configs(BaseSettings):
#     """
#     Configuration class for the application.
#     """
#     log_file: str
#     DEBUG: bool
#     ABSOL_PATH_NEURO_PDF_DOCS: str
#     IDIO_VERSION: str
#     UUID_VERSION: str
#     RUNING_NAME: str
#     OPENAI_NEUROCURSO_API_KEY: str
#     OPENAI_NEUROCURSO_ORGANIZATION: str
#     POPPLER_PATH: str
#     MODEL_GPT_4_0125: str
#     MODEL_GPT_35_0125: str
#     MODEL_GPT_VISION: str
#     MODEL_TTS_HD: str
#     MODEL_WHISPER: str
#     MODEL_TEXT_EMBEDDING_3_LARGE: str
#     MODEL_TEXT_EMBEDDING_3_SMALL: str
#     MODEL_TEXT_EMBEDDING_ADA_002: str
#     ASST_TOOLS_CODE_INTERPRETER: List[dict]
#     ASST_TOOLS_RETRIEVAL: List[dict]
#     ASST_TOOLS_CODE_INTERPRETER_AND_RETRIEVAL: List[dict]
#     PROMPT_EDIT_IN_USE: str


# configuracao = Configs(
#     log_file="./logs/file.log",
#     DEBUG=True,
#     ABSOL_PATH_NEURO_PDF_DOCS="/Users/moraes/Documents/projetos/continuum/",
#     IDIO_VERSION="1.0",
#     UUID_VERSION="1.0",
#     RUNING_NAME="MyApp",
#     OPENAI_NEUROCURSO_API_KEY=os.getenv("OPENAI_NEUROCURSO_API_KEY"),
#     OPENAI_NEUROCURSO_ORGANIZATION=os.getenv("OPENAI_NEUROCURSO_ORGANIZATION"),
#     MODEL_GPT_4_0125="gpt-4-0125-preview",
#     MODEL_GPT_35_0125="gpt-3.5-turbo-0125",
#     MODEL_GPT_VISION="gpt-4-vision-preview",
#     MODEL_TTS_HD="tts-1-hd",
#     MODEL_WHISPER="whisper-1",
#     MODEL_TEXT_EMBEDDING_3_LARGE="text-embedding-3-large",
#     MODEL_TEXT_EMBEDDING_3_SMALL="text-embedding-3-small",
#     MODEL_TEXT_EMBEDDING_ADA_002="text-embedding-ada-002",
#     ASST_TOOLS_CODE_INTERPRETER=[{"type": "code_interpreter"}],
#     ASST_TOOLS_RETRIEVAL=[{"type": "retrieval"}],
#     ASST_TOOLS_CODE_INTERPRETER_AND_RETRIEVAL=[{"type": "code_interpreter"}, {"type": "retrieval"}],
#     PROMPT_EDIT_IN_USE="prompt.edit_text_from_pdf.prompt_edit_01v02_optimized",
#     POPPLER_PATH=r"/opt/homebrew/Cellar/poppler/24.02.0/bin",
# )

# # Configure logging
# logging.basicConfig(
#     filename=configuracao.log_file,
#     level=logging.DEBUG if configuracao.DEBUG else logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )