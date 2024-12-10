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
from typing import List, Dict, Any
from app.core.asst.crud import list_assistants

import json
import sqlite3

from app.core.security import get_current_user  # 


router = APIRouter()



from app.db.cruds_operations import insert_assistant_in_db
@router.post("/assistant", response_model=AssistantResponse)
async def create_assistant_route(
    assistant_create: AssistantCreate,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        response = await create_assistant(client, assistant_create)
        
        # Insert the assistant data into the database
        insert_assistant_in_db(
            id_asst=response.id_asst,
            object=response.object,
            created_at=response.created_at,
            name=response.name,
            description=response.description,
            model=response.model,
            instructions=response.instructions,
            tools=json.dumps(response.tools),  # Convert tools to JSON string if necessary
            metadata=json.dumps(response.metadata),  # Convert metadata to JSON string if necessary
            temperature=response.temperature,
            top_p=response.top_p,
        )
        
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
    
    
@router.delete("/assistants/{assistant_id}")
async def delete_assistant(
    assistant_id: str,
    current_user: str = Depends(get_current_user),  # Adicionar dependência de autenticação
    client: OpenAI = Depends(get_openai_client)
):
    """
    Delete an assistant. Requires authentication.
    """
    try:
        logger.info(f"User {current_user} attempting to delete assistant {assistant_id}")
        
        # Verificar se o assistant existe
        try:
            assistant = client.beta.assistants.retrieve(assistant_id)
        except Exception as e:
            logger.error(f"Assistant {assistant_id} not found: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Assistant not found: {assistant_id}")

        # Deletar o assistant
        deleted_assistant = client.beta.assistants.delete(assistant_id)
        
        if deleted_assistant.deleted:
            logger.info(f"Assistant {assistant_id} successfully deleted by user {current_user}")
            return {"message": f"Assistant {assistant_id} deleted successfully"}
        else:
            logger.error(f"Failed to delete assistant {assistant_id}")
            raise HTTPException(status_code=500, detail="Failed to delete assistant")
            
    except Exception as e:
        logger.error(f"Error deleting assistant {assistant_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting assistant: {str(e)}")    
# @router.delete("/assistant/{assistant_id}", response_model=dict)
# async def delete_assistant_route(
#     assistant_id: str,
#     client: OpenAI = Depends(get_openai_client)
# ):
#     try:
#         await delete_assistant(client, assistant_id)
#         return {"message": f"Assistant {assistant_id} deleted successfully"}
#     except Exception as e:
#         logger.error(f"Error deleting assistant: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error deleting assistant: {str(e)}")
    
    
##############################################################    
############################################################## 
################## Para o cliente dashBoard ##################  
##############################################################
##############################################################    


from app.db.cruds_operations import read_assistants
@router.get("/assistants_all", response_model=List[Dict[str, Any]])
async def get_all_assistants():
    try:
        # Fetch all assistants from the database
        assistants = read_assistants()

        return assistants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving assistants: {str(e)}")
    
    
    
            