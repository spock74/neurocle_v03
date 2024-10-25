import os
from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI, OpenAIError
from app.api.dependencies import get_openai_client
from app.core.settings.conf import logger
from typing import List
from app.services import assistant_service
from app.api.api_v1.assistants_schema import VectorStoreCreate, VectorStoreResponse
from app.db.vector_store_db import get_vector_store_id, set_vector_store_id

router = APIRouter()

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

        # Update assistant with vector store (only if it's a new vector store)
        if not vector_store_id:
            logger.info(f"Updating assistant with vector store: {vector_store.assistant_id}")
            updated_assistant = await assistant_service.update_assistant_with_vector_store(client, vector_store.assistant_id, vector_store_obj.id)
            logger.info(f"Assistant updated successfully: {updated_assistant.id}")

        response = VectorStoreResponse(
            vector_store_id=vector_store_obj.id,
            file_batch_status=file_batch.status,
            file_counts=file_batch.file_counts.__dict__  # Convert FileCounts to a dictionary
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