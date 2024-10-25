# from fastapi import APIRouter, Depends, HTTPException
# from openai import OpenAI
# from app.api.dependencies import get_openai_client
# from app.services.assistant_service import (create_assistant, 
#                                             get_assistant, 
#                                             send_question, 
#                                             delete_assistant, 
#                                             update_assistant, 
#                                             QuestionRequest, 
#                                             QuestionResponse)
# from app.api.api_v1.assistants_schema import AssistantCreate, AssistantResponse, AssistantUpdate, VectorStoreCreate, VectorStoreResponse, VectorStoreResponse
# from app.core.settings.conf import logger
# from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from app.api.dependencies import get_openai_client
from app.services import assistant_service
from app.api.api_v1.assistants_schema import (
    ThreadCreate, VectorStoreCreate, ThreadResponse
)
from app.core.settings.conf import logger
from typing import List, Dict


router = APIRouter()



@router.post("/thread", response_model=ThreadResponse)
async def create_assistant_route(
    thread_create: ThreadCreate,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        response = await create_thread(client, thread_create)
        return response
    except Exception as e:
        logger.error(f"Error creating assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating assistant: {str(e)}")