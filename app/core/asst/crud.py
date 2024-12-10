from openai import OpenAIError, OpenAI
import time
from datetime import datetime
import requests
from fastapi import HTTPException
from app.api.api_v1.assistants_schema import QuestionRequest, QuestionResponse, AssistantCreate, AssistantResponse
from app.core.settings.conf import logger
from app.core.asst.prompt_cefaleias_v02 import formatted_optimized_instructions, formatted_instructions_1
from app.core.openai_utils.create_client import create_client

API_BASE_URL = "http://localhost:8000/api/v1"

def __create_assistant(name: str=None, instructions: str=formatted_instructions_1, model: str="gpt-4o-mini"):
    TD = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    client = create_client()
    try:
        assistant = client.beta.assistants.create(
            name=f"asst_{TD}",
            instructions=instructions,
            model=model,
            tools=[{"type": "file_search"}, {"type": "code_interpreter"}],
        )
        logger.info(f"::ZEHN:: Assistant created successfully with ID {assistant.id}")
        # return assistant
        return assistant.json()
    except Exception as e:
        logger.error(f"Failed to create assistant: {e}")
        raise
   

def get_assistant(assistant_id: str):
    client = create_client()
    try:
        assistant = client.beta.assistants.retrieve(assistant_id)
        return assistant
    except Exception as e:
        logger.error(f"Failed to retrieve assistant: {e}")
        raise

def update_assistant(assistant_id: str, **kwargs):
    client = create_client()
    try:
        assistant = client.beta.assistants.update(assistant_id, **kwargs)
        return assistant
    except Exception as e:
        logger.error(f"Failed to update assistant: {e}")
        raise

def delete_assistant(assistant_id: str):
    client = create_client()
    try:
        response = client.beta.assistants.delete(assistant_id)
        return response
    except Exception as e:
        logger.error(f"Failed to delete assistant: {e}")
        raise


def list_assistants(limit: int = 20, after: str = None):
    client = create_client()
    try:
        assistants = client.beta.assistants.list(limit=limit, after=after)
        logger.info(f"::ZEHN:: Retrieved {len(assistants.data)} assistants")
        return [
            AssistantResponse(
                id_asst=assistant.id,
                object=assistant.to_json(),
                created_at=assistant.created_at,
                name=assistant.name,
                description=assistant.description,
                model=assistant.model,
                instructions=assistant.instructions,
                tools=assistant.tools,
                metadata=assistant.metadata,
                temperature=assistant.temperature,
                top_p=assistant.top_p
            ) for assistant in assistants.data
        ]
    except Exception as e:
        logger.error(f"Failed to list assistants: {e}")
        raise



def send_question_to_assistant(question: QuestionRequest):
    response = requests.post(f"{API_BASE_URL}/question/{question.assistant_id}", json=question.dict())
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: {response.status_code} - {response.text}"


