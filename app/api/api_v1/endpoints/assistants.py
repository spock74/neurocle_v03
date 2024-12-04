# from fastapi import APIRouter, Depends, HTTPException
# from openai import OpenAI
# from app.api.dependencies import get_openai_client
from app.services.assistant_service import (create_assistant, 
                                            get_assistant, 
                                            send_question, 
                                            delete_assistant, 
                                            update_assistant, 
                                            QuestionRequest, 
                                            QuestionResponse)
from fastapi import APIRouter, Depends, HTTPException, Query
from openai import OpenAI, OpenAIError
from app.api.dependencies import get_openai_client
from app.services import assistant_service
from app.api.api_v1.assistants_schema import (
    AssistantCreate, AssistantResponse, AssistantUpdate, 
    VectorStoreCreate, VectorStoreResponse, QuestionRequest, QuestionResponse)
from app.core.settings.conf import logger
from typing import List, Dict
from app.core.asst.crud import list_assistants

router = APIRouter()

#******************************
# app/services/database_service.py

import sqlite3
DATABASE_URL = "user_assistants.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_highlighted_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS highlighted
                    (user_id TEXT, metadata TEXT, assistant_id TEXT)''')
    conn.commit()
    conn.close()

def insert_highlighted_data(user_id, metadata, assistant_id):
    conn = get_db_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS highlighted (id INTEGER PRIMARY KEY, user_id TEXT, metadata TEXT, assistant_id TEXT)")

    conn.execute("INSERT INTO highlighted (user_id, metadata, assistant_id) VALUES (?, ?, ?)",
                 (user_id, str(metadata), assistant_id))
    conn.commit()
    conn.close()
#******************************

@router.post("/assistant", response_model=AssistantResponse)
async def create_assistant_route(
    assistant_create: AssistantCreate,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        response = await create_assistant(client, assistant_create)
        insert_highlighted_data(assistant_create.user_id, assistant_create.metadata, response.id)
        return response
    except Exception as e:
        logger.error(f"Error creating assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating assistant: {str(e)}")


@router.get("/assistant/{assistant_id}", response_model=AssistantResponse)
async def get_assistant_route_(
    assistant_id: str,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        return await get_assistant(client, assistant_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

###*******
#

@router.get("/assistants", response_model=List[AssistantResponse])
async def list_assistants_route(
    limit: int = Query(default=20, ge=1, le=99),
    after: str = Query(default=None),
    client: OpenAI = Depends(get_openai_client)
):
    try:
        logger.info(f"Attempting to list assistants with limit: {limit}, after: {after}")
        assistants = list_assistants(limit=limit, after=after)
        logger.info(f"Successfully retrieved {len(assistants)} assistants")
        return assistants
    except Exception as e:
        logger.error(f"Error listing assistants: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing assistants: {str(e)}")
# @router.get("/assistants", response_model=List[AssistantResponse])
# async def list_assistants_route(
#     limit: int = Query(default=99, ge=1, le=100),
#     after: str = Query(default=None),
#     client: OpenAI = Depends(get_openai_client)
# ):
#     try:
#         logger.info(f"Attempting to list assistants with limit: {limit}, after: {after}")
#         assistants = list_assistants()
#         logger.info(f"Successfully retrieved {len(assistants)} assistants")
#         return assistants
#     except Exception as e:
#         logger.error(f"Error listing assistants: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error listing assistants: {str(e)}")
# @router.get("/assistants", response_model=List[Dict[str, str]])
# async def list_assistants_route(
#     limit: int = Query(default=20, ge=1, le=100),
#     after: str = Query(default=None),
#     client: OpenAI = Depends(get_openai_client)
# ):
#     try:
#         logger.info(f"Attempting to list assistants with limit: {limit}, after: {after}")
#         assistants_info = await assistant_service.list_assistant_info(client, limit, after)
#         logger.info(f"Successfully retrieved {len(assistants_info)} assistant info")
#         return assistants_info
#     except Exception as e:
#         logger.error(f"Error listing assistant info: {str(e)}")
#         logger.error(f"Error type: {type(e).__name__}")
#         logger.error(f"Error details: {e.__dict__}")
#         raise HTTPException(status_code=500, detail=f"Error listing assistant info: {str(e)}")
###*******

@router.post("/filter", response_model=List[AssistantResponse])
def filter_assistants(
    metadata: Dict[str, Dict[str, str]],
    client: OpenAI = Depends(get_openai_client)
):
    try:
        assistants = assistant_service.filter_assistants_by_metadata(client, metadata["metadata"])
        return assistants
    except Exception as e:
        logger.error(f"Error in filter_assistants: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.put("/assistant/{assistant_id}", response_model=AssistantResponse)
async def update_assistant_route(
    assistant_id: str,
    assistant_update: AssistantUpdate,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        response = await update_assistant(client, assistant_id, assistant_update)
        return response
    except Exception as e:
        logger.error(f"Error updating assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating assistant: {str(e)}")
    
    
    
@router.delete("/assistant/{assistant_id}", response_model=dict)
async def delete_assistant_route(
    assistant_id: str,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        await delete_assistant(client, assistant_id)
        return {"message": f"Assistant {assistant_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting assistant: {str(e)}")