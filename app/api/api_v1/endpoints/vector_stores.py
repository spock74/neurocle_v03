import os
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI, OpenAIError
from app.api.dependencies import get_openai_client
from app.core.settings.conf import logger
from typing import List, Dict
from app.services import assistant_service
from app.api.api_v1.assistants_schema import VectorStoreCreate, VectorStoreResponse
from app.db.vector_store_db import get_vector_store_id, set_vector_store_id
    
from app.api.api_v1.assistants_schema import VectorStoreListResponse

from app.db.cruds_operations import (
    insert_vector_store,  # Adicionando esta importação
    read_vector_stores,
    update_vector_store,
    delete_vector_store
)

from pydantic import BaseModel

router = APIRouter()




#@@@ ----------------------------------------------------------------------    
#@@@ ----------------------------------------------------------------------    
@router.post("/vectorstores", response_model=VectorStoreResponse)
async def create_and_populate_vector_store(
    vector_store: VectorStoreCreate,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        logger.info(f"Processing vector store for assistant: {vector_store.assistant_id}")
        
        # Check if the assistant exists
        try:
            client.beta.assistants.retrieve(vector_store.assistant_id)
        except OpenAIError as oe:
            if oe.status_code == 404:
                logger.error(f"Assistant not found: {vector_store.assistant_id}")
                raise HTTPException(status_code=404, detail=f"Assistant not found: {vector_store.assistant_id}")
            raise

        # Try to get existing vector store from the database
        vector_store_id = get_vector_store_id(vector_store.assistant_id)
        
        if vector_store_id:
            # Use the existing vector store
            vector_store_obj = client.beta.vector_stores.retrieve(vector_store_id)
            logger.info(f"Using existing vector store: {vector_store_obj.id}")
        else:
            # If no existing vector store, create a new one
            logger.info(f"Creating new vector store for assistant: {vector_store.assistant_id}")
            vector_store_obj = await assistant_service.create_vector_store(client, vector_store.assistant_id)
            logger.info(f"Vector store created: {vector_store_obj.id}")
            # Store the new vector store id in the database
            set_vector_store_id(vector_store.assistant_id, vector_store_obj.id)

        # Validate file paths
        valid_file_paths = []
        for path in vector_store.file_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                valid_file_paths.append(full_path)
            else:
                logger.warning(f"File not found: {full_path}")

        if not valid_file_paths:
            raise FileNotFoundError("No valid files found to upload")

        # Send files to vector store
        logger.info(f"Sending files to vector store: {vector_store_obj.id}")
        file_batch = await assistant_service.send_files_to_vector_store(client, vector_store_obj.id, valid_file_paths)
        logger.info(f"Files sent to vector store. Status: {file_batch.status}")

        # Save to SQLite database
        try:
            insert_vector_store(
                id_vector=vector_store_obj.id,
                name=vector_store_obj.name,
                created_at=vector_store_obj.created_at,
                status=file_batch.status,
                file_counts_total=file_batch.file_counts.total,
                file_counts_completed=file_batch.file_counts.completed,
                file_counts_in_progress=file_batch.file_counts.in_progress,
                file_counts_failed=file_batch.file_counts.failed,
                file_counts_cancelled=file_batch.file_counts.cancelled,
                assistant_id=vector_store.assistant_id
            )
            logger.info(f"Vector store {vector_store_obj.id} saved to database")
        except Exception as db_error:
            logger.error(f"Error saving to database: {str(db_error)}")
            # Continue execution even if database save fails
            pass

        # Update assistant with vector store (only if it's a new vector store)
        if not vector_store_id:
            logger.info(f"Updating assistant with vector store: {vector_store.assistant_id}")
            updated_assistant = await assistant_service.update_assistant_with_vector_store(
                client, 
                vector_store.assistant_id, 
                vector_store_obj.id
            )
            logger.info(f"Assistant updated successfully: {updated_assistant.id}")

        response = VectorStoreResponse(
            vector_store_id=vector_store_obj.id,
            file_batch_status=file_batch.status,
            file_counts=file_batch.file_counts.__dict__
        )
                
        return response
    except OpenAIError as oe:
        logger.error(f"OpenAI API error in create_and_populate_vector_store: {str(oe)}")
        raise HTTPException(status_code=oe.status_code, detail=str(oe))
    except FileNotFoundError as fnf:
        logger.error(f"File not found error: {str(fnf)}")
        raise HTTPException(status_code=400, detail=str(fnf))
    except Exception as e:
        logger.error(f"Unexpected error in create_and_populate_vector_store: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {e.__dict__}")
        raise HTTPException(status_code=500, detail=f"Error creating and populating vector store: {str(e)}")
# @router.post("/vectorstores", response_model=VectorStoreResponse)
# async def create_and_populate_vector_store(
#     vector_store: VectorStoreCreate,
#     client: OpenAI = Depends(get_openai_client)
# ):
#     try:
#         logger.info(f"Processing vector store for assistant: {vector_store.assistant_id}")
        
#         # Check if the assistant exists
#         try:
#             client.beta.assistants.retrieve(vector_store.assistant_id)
#         except OpenAIError as oe:
#             if oe.status_code == 404:
#                 logger.error(f"Assistant not found: {vector_store.assistant_id}")
#                 raise HTTPException(status_code=404, detail=f"Assistant not found: {vector_store.assistant_id}")
#             raise

#         # Try to get existing vector store from the database
#         vector_store_id = get_vector_store_id(vector_store.assistant_id)
        
#         if vector_store_id:
#             # Use the existing vector store
#             vector_store_obj = client.beta.vector_stores.retrieve(vector_store_id)
#             logger.info(f"Using existing vector store: {vector_store_obj.id}")
#         else:
#             # If no existing vector store, create a new one
#             logger.info(f"Creating new vector store for assistant: {vector_store.assistant_id}")
#             vector_store_obj = await assistant_service.create_vector_store(client, vector_store.assistant_id)
#             logger.info(f"Vector store created: {vector_store_obj.id}")
#             # Store the new vector store id in the database
#             set_vector_store_id(vector_store.assistant_id, vector_store_obj.id)

#         # Validate file paths
#         valid_file_paths = []
#         for path in vector_store.file_paths:
#             full_path = os.path.abspath(path)
#             if os.path.exists(full_path):
#                 valid_file_paths.append(full_path)
#             else:
#                 logger.warning(f"File not found: {full_path}")

#         if not valid_file_paths:
#             raise FileNotFoundError("No valid files found to upload")

#         # Send files to vector store
#         logger.info(f"Sending files to vector store: {vector_store_obj.id}")
#         file_batch = await assistant_service.send_files_to_vector_store(client, vector_store_obj.id, valid_file_paths)
#         logger.info(f"Files sent to vector store. Status: {file_batch.status}")

#         # Update assistant with vector store (only if it's a new vector store)
#         if not vector_store_id:
#             logger.info(f"Updating assistant with vector store: {vector_store.assistant_id}")
#             updated_assistant = await assistant_service.update_assistant_with_vector_store(client, vector_store.assistant_id, vector_store_obj.id)
#             logger.info(f"Assistant updated successfully: {updated_assistant.id}")

#         response = VectorStoreResponse(
#             vector_store_id=vector_store_obj.id,
#             file_batch_status=file_batch.status,
#             file_counts=file_batch.file_counts.__dict__  # Convert FileCounts to a dictionary
#         )
                
#         return response
#     except OpenAIError as oe:
#         logger.error(f"OpenAI API error in create_and_populate_vector_store: {str(oe)}")
#         raise HTTPException(status_code=oe.status_code, detail=str(oe))
#     except FileNotFoundError as fnf:
#         logger.error(f"File not found error: {str(fnf)}")
#         raise HTTPException(status_code=400, detail=str(fnf))
#     except Exception as e:
#         logger.error(f"Unexpected error in create_and_populate_vector_store: {str(e)}")
#         logger.error(f"Error type: {type(e).__name__}")
#         logger.error(f"Error details: {e.__dict__}")
#         raise HTTPException(status_code=500, detail=f"Error creating and populating vector store: {str(e)}")
#@@@ ----------------------------------------------------------------------    
#@@@ ----------------------------------------------------------------------    
    
    
    
    
    

#@@@ ----------------------------------------------------------------------    
#@@@ ----------------------------------------------------------------------    
# def list_vector_stores(client: OpenAI):
#     """
#     List all vector stores.
    
#     Args:
#         client (OpenAI): The OpenAI client instance.
        
#     Returns:
#         list: A list of vector stores.
#     """
#     try:
#         vector_stores = client.beta.vector_stores.list()
#         logger.info(f"Retrieved {len(vector_stores.data)} vector stores")
#         return [
#             {
#                 "id": vs.id,
#                 "name": vs.name,
#                 "created_at": vs.created_at,
#                 "file_counts": vs.file_counts,
#                 "status": vs.status
#             } for vs in vector_stores.data
#         ]
#     except Exception as e:
#         logger.error(f"Failed to list vector stores: {e}")
#         raise
#@@@ ----------------------------------------------------------------------    
@router.get("/vector_stores")     
async def list_vector_stores_route(
    client: OpenAI = Depends(get_openai_client)
):
    """
    List all vector stores from OpenAI API.
    """
    try:
        logger.info("Attempting to list vector stores from OpenAI API")
        
        # Verificar se o cliente está inicializado corretamente
        if not client:
            raise ValueError("OpenAI client is not initialized")
            
        # Tentar listar as vector stores
        try:
            vector_stores = client.beta.vector_stores.list()
            logger.info(f"Raw API response received with {len(vector_stores.data)} stores")
        except Exception as api_error:
            logger.error(f"OpenAI API error: {str(api_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error accessing OpenAI API: {str(api_error)}"
            )
        
        formatted_stores = []
        for vs in vector_stores.data:
            try:
                # Log dos dados brutos para debug
                logger.debug(f"Processing vector store: ID={vs.id}, Name={vs.name}")
                logger.debug(f"File counts data: {vs.file_counts}")
                
                store_dict = {
                    "id_vector": str(vs.id),  # Garantir que é string
                    "name": str(vs.name),     # Garantir que é string
                    "created_at": int(vs.created_at),  # Garantir que é inteiro
                    "status": str(vs.status), # Garantir que é string
                    "file_counts": {
                        "total": int(getattr(vs.file_counts, 'total', 0)),
                        "completed": int(getattr(vs.file_counts, 'completed', 0)),
                        "in_progress": int(getattr(vs.file_counts, 'in_progress', 0)),
                        "failed": int(getattr(vs.file_counts, 'failed', 0)),
                        "cancelled": int(getattr(vs.file_counts, 'cancelled', 0))
                    }
                }
                formatted_stores.append(store_dict)
                logger.debug(f"Successfully formatted store: {store_dict}")
            except AttributeError as attr_error:
                logger.error(f"Attribute error for store {vs.id}: {str(attr_error)}")
                logger.error(f"Vector store data: {vars(vs)}")
                continue
            except Exception as format_error:
                logger.error(f"Error formatting store {vs.id}: {str(format_error)}")
                logger.error(f"Error type: {type(format_error).__name__}")
                continue
        
        if not formatted_stores:
            logger.warning("No vector stores were successfully formatted")
            return []
            
        logger.info(f"Successfully formatted {len(formatted_stores)} vector stores")
        return formatted_stores
        
    except Exception as e:
        logger.error(f"Unexpected error in list_vector_stores_route: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {vars(e) if hasattr(e, '__dict__') else 'No details available'}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing vector stores"
        )



@router.get("/vector_stores_all")     
async def list_vector_stores_route(
    client: OpenAI = Depends(get_openai_client)
):
    """
    List all vector stores from OpenAI API.
    """
    try:
        logger.info("Attempting to list vector stores from OpenAI API")
        
        # Verificar se o cliente está inicializado corretamente
        if not client:
            raise ValueError("OpenAI client is not initialized")
            
        # Tentar listar as vector stores
        try:
            vector_stores = client.beta.vector_stores.list()
            logger.info(f"Raw API response received with {len(vector_stores.data)} stores")
        except Exception as api_error:
            logger.error(f"OpenAI API error: {str(api_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error accessing OpenAI API: {str(api_error)}"
            )
        
        formatted_stores = []
        for vs in vector_stores.data:
            try:
                # Log dos dados brutos para debug
                logger.debug(f"Processing vector store: ID={vs.id}, Name={vs.name}")
                logger.debug(f"File counts data: {vs.file_counts}")
                
                store_dict = {
                    "id_vector": str(vs.id),  # Garantir que é string
                    "name": str(vs.name),     # Garantir que é string
                    "created_at": int(vs.created_at),  # Garantir que é inteiro
                    "status": str(vs.status), # Garantir que é string
                    "file_counts": {
                        "total": int(getattr(vs.file_counts, 'total', 0)),
                        "completed": int(getattr(vs.file_counts, 'completed', 0)),
                        "in_progress": int(getattr(vs.file_counts, 'in_progress', 0)),
                        "failed": int(getattr(vs.file_counts, 'failed', 0)),
                        "cancelled": int(getattr(vs.file_counts, 'cancelled', 0))
                    }
                }
                formatted_stores.append(store_dict)
                logger.debug(f"Successfully formatted store: {store_dict}")
            except AttributeError as attr_error:
                logger.error(f"Attribute error for store {vs.id}: {str(attr_error)}")
                logger.error(f"Vector store data: {vars(vs)}")
                continue
            except Exception as format_error:
                logger.error(f"Error formatting store {vs.id}: {str(format_error)}")
                logger.error(f"Error type: {type(format_error).__name__}")
                continue
        
        if not formatted_stores:
            logger.warning("No vector stores were successfully formatted")
            return []
            
        logger.info(f"Successfully formatted {len(formatted_stores)} vector stores")
        return formatted_stores
        
    except Exception as e:
        logger.error(f"Unexpected error in list_vector_stores_route: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {vars(e) if hasattr(e, '__dict__') else 'No details available'}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing vector stores"
        )

#@@@ ----------------------------------------------------------------------    




# from typing import List, Dict
# from fastapi import APIRouter, HTTPException
# from app.db.cruds_operations import read_vector_stores
# from app.core.settings.conf import logger
# from pydantic import BaseModel

# # Define o modelo de resposta
# class FileCountsResponse(BaseModel):
#     total: int
#     completed: int
#     in_progress: int
#     failed: int
#     cancelled: int

# class VectorStoreResponse(BaseModel):
#     id_vector: str  # Mudado de 'id' para 'id_vector' para corresponder aos dados
#     name: str
#     created_at: int
#     status: str
#     file_counts: FileCountsResponse

# @router.get("/vector_stores_all", response_model=List[VectorStoreResponse])
# async def list_vector_stores_from_db():
#     """
#     List all vector stores from the local database.
#     """
#     try:
#         logger.info("Attempting to list vector stores from database")
#         vector_stores = read_vector_stores()
        
#         # Convert SQLite rows to dictionary format
#         formatted_stores = []
#         for store in vector_stores:
#             try:
#                 store_dict = {
#                     "id_vector": store[0],  # Mantido como id_vector
#                     "name": store[1],
#                     "created_at": int(store[2]) if store[2] else 0,
#                     "status": store[3] or "unknown",
#                     "file_counts": {
#                         "total": int(store[4]) if store[4] is not None else 0,
#                         "completed": int(store[5]) if store[5] is not None else 0,
#                         "in_progress": int(store[6]) if store[6] is not None else 0,
#                         "failed": int(store[7]) if store[7] is not None else 0,
#                         "cancelled": int(store[8]) if store[8] is not None else 0
#                     }
#                 }
#                 formatted_stores.append(store_dict)
#             except Exception as format_error:
#                 logger.error(f"Error formatting store {store}: {str(format_error)}")
#                 continue
        
#         logger.info(f"Successfully retrieved {len(formatted_stores)} vector stores from database")
#         return formatted_stores
#     except Exception as e:
#         logger.error(f"Error listing vector stores from database: {str(e)}")
#         logger.error(f"Error type: {type(e).__name__}")
#         logger.error(f"Error details: {e.__dict__}")
#         raise HTTPException(status_code=500, detail=f"Error listing vector stores: {str(e)}")
#@@@ ----------------------------------------------------------------------    




#@@@ ----------------------------------------------------------------------    
#@@@ ----------------------------------------------------------------------    
# from app.db.cruds_operations import read_vector_stores
# @router.get("/vector_stores_all", response_model=List[VectorStoreListResponse])
# async def list_vector_stores_from_db():
#     """
#     List all vector stores from the local database.
#     """
#     try:
#         logger.info("Attempting to list vector stores from database")
#         vector_stores = read_vector_stores()
        
#         # Convert SQLite rows to dictionary format
#         formatted_stores = [
#             {
#                 "id_vector": store[0],  # id_vector
#                 "name": store[1],
#                 "created_at": store[2],
#                 "status": store[3],
#                 "file_counts": {
#                     "total": store[4],
#                     "completed": store[5],
#                     "in_progress": store[6],
#                     "failed": store[7],
#                     "cancelled": store[8]
#                 }
#             } for store in vector_stores
#         ]
        
#         logger.info(f"Successfully retrieved {len(formatted_stores)} vector stores from database")
#         return formatted_stores
#     except Exception as e:
#         logger.error(f"Error listing vector stores from database: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error listing vector stores: {str(e)}")
#@@@ ----------------------------------------------------------------------    
#@@@ ----------------------------------------------------------------------    