

import os
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from openai import OpenAI
from pydantic import BaseModel

# from app.api.api_v1.assistants_schema import create_client
# from app.api.openai_utils_schemas import OpenAIClientSchema

from app.core.settings.conf import logger

# Autor: Jose E Moraes



def get_db_session():
    """
    Cria uma nova sessão de banco de dados.

    Yields:
        Session: A sessão do banco de dados.

    Raises:
        Exception: Se ocorrer um erro ao obter a sessão do banco de dados.
    """
    logger.debug("Iniciando a sessão do banco de dados.")
    db = next(get_db())
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro ao obter a sessão do banco de dados: {e}")
        raise
    finally:
        logger.debug("Fechando a sessão do banco de dados.")
        db.close()

# Use esta função como uma dependência
db_dependency = Depends(get_db_session)

# *********************************************************************
class OpenAIClientSchema(BaseModel):
    api_key: str = os.getenv("OPENAI_NEUROCURSO_API_KEY")
    organization: str = os.getenv("OPENAI_NEUROCURSO_ORGANIZATION_ID")

client_schema_ = OpenAIClientSchema(api_key=os.getenv("OPENAI_NEUROCURSO_API_KEY"), organization=os.getenv("OPENAI_NEUROCURSO_ORGANIZATION_ID"))
def create_client(client_: OpenAIClientSchema=client_schema_):
    """
    Create an OpenAI client instance with the provided assistant configuration.

    Args:
        assistant (OpenAIAssistantSchema): A schema containing OpenAI configuration details.

    Returns:
        OpenAI: An instance of the OpenAI client.

    Raises:
        ValueError: If the API key or organization ID is missing.
        OpenAIError: If there's an error initializing the OpenAI client.
    """
    
    try:
        if not client_.api_key:
            raise ValueError("API key is required")
        
        
        if not client_.organization:
            raise ValueError("Organization ID is required")

        client = OpenAI(
            api_key=client_.api_key, 
            organization=client_.organization,
        )

        
        # Test the connection
        client.models.list()
        
        logger.info("OpenAI client created successfully")
        return client

    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise

    except OpenAIError as oe:
        logger.error(f"OpenAI error: {str(oe)}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise


def get_openai_client():
    return OpenAI(
        api_key=os.getenv("OPENAI_NEUROCURSO_API_KEY"),
        organization=os.getenv("OPENAI_NEUROCURSO_ORGANIZATION_ID")
    )