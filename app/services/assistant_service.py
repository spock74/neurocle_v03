
import asyncio
import os, time
import time
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAIError, OpenAI
from fastapi import Path
from fastapi import HTTPException   
from typing import Dict, List, Any
from app.api.api_v1.assistants_schema import QuestionRequest, QuestionResponse, AssistantCreate, AssistantResponse
from app.api.api_v1.assistants_schema import AssistantUpdate, AssistantResponse
from app.core.asst.prompt_cefaleias_v02 import formatted_instructions_1
from app.core.settings.conf import logger
import json
from app.db.vector_store_db import insert_question_log
# vs_1vxfeTQzvVyRWh6dZoEadbwN
# asst_CBuAZ5PoR8mnn8APqOKh79E9

async def get_assistant_vector_stores(client: OpenAI, assistant_id: str):
    try:
        vector_store_id = get_vector_store_id(assistant_id)
        return [vector_store_id] if vector_store_id else []
    except Exception as e:
        logger.error(f"Error retrieving vector stores for assistant: {str(e)}")
        return []

    
    

async def create_assistant(client: OpenAI, assistant_create: AssistantCreate) -> AssistantResponse:
    try:
        logger.info(f"::ZEHN:: Creating new assistant with data: {assistant_create.dict()}")
        
        if assistant_create.instructions is None or len(assistant_create.instructions) < 3:
            assistant_create.instructions = formatted_instructions_1
        
        assistant = client.beta.assistants.create(
            name=assistant_create.name,
            instructions=assistant_create.instructions,
            model=assistant_create.model,
            description=assistant_create.description,
            tools=assistant_create.tools or [{"type": "file_search"}, {"type": "code_interpreter"}],
            metadata={"user": assistant_create.user_id, **(assistant_create.metadata or {})},
            temperature=float(assistant_create.temperature) if assistant_create.temperature is not None else None,
            top_p=float(assistant_create.top_p) if assistant_create.top_p is not None else None,
        )
        
        
        response = AssistantResponse(
            id_asst=assistant.id,
            object=assistant.to_json(),
            created_at=int(assistant.created_at),
            name=assistant.name,
            description=assistant.description,
            model=assistant.model,
            instructions=assistant.instructions,
            tools=assistant.tools,
            metadata=assistant.metadata,
            temperature=float(assistant.temperature) if assistant.temperature is not None else None,
            top_p=float(assistant.top_p) if assistant.top_p is not None else None,
        )
        logger.info(f"::ZEHN:: ==== AssistantResponse created successfully: {response}")
        return response
    except OpenAIError as oe:
        logger.error(f"OpenAI API error: {str(oe)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}")
    except Exception as e:
        logger.error(f"Unexpected error in create_assistant: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {e.__dict__}")
        raise HTTPException(status_code=500, detail=f"Error creating assistant: {str(e)}")
    
    
    
    
    
async def get_assistant(client: OpenAI, assistant_id: str) -> AssistantResponse:
    try:
        logger.info(f"::ZEHN:: Retrieving assistant with ID {assistant_id}")
        assistant = client.beta.assistants.retrieve(assistant_id)
        
        response = AssistantResponse(
            id=assistant.id,
            created_at=assistant.created_at,
            name=assistant.name,
            description=assistant.description,
            model=assistant.model,
            instructions=assistant.instructions,
            tools=assistant.tools,
            metadata=assistant.metadata,
            temperature=getattr(assistant, 'temperature', None),
            top_p=getattr(assistant, 'top_p', None)
        )
        logger.info(f"::ZEHN:: AssistantResponse retrieved successfully: {response}")
        return response
    except OpenAIError as oe:
        logger.error(f"OpenAI API error: {str(oe)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}")
    except Exception as e:
        logger.error(f"Unexpected error in get_assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving assistant: {str(e)}")



async def send_question(client: OpenAI, question: QuestionRequest) -> Dict[str, Any]:
    try:
        logger.info(f"::ZEHN:: Sending question to assistant {question.assistant_id}")
        
        if not question.thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
        else:
            thread_id = question.thread_id

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question.content
        )
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=question.assistant_id
        )
        
        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run.status == "failed":
                raise Exception("Run failed")
            time.sleep(1)
        
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_response = messages.data[0].content[0].text.value
        
        logger.info(f"::ZEHN:: Received response from assistant {question.assistant_id}")
        
        response = {"answer": assistant_response, "thread_id": thread_id}
        
        # Insert the question log
        from app.db.vector_store_db import insert_question_log
        insert_question_log(question.assistant_id, thread_id, question.content, question.user_id, json.dumps(response))
        
        return response
    except OpenAIError as oe:
        logger.error(f"OpenAI API error in send_question: {str(oe)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}")
    except Exception as e:
        logger.error(f"Unexpected error in send_question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending question: {str(e)}")



# **********    
async def list_assistant_ids(client: OpenAI, limit: int = 99, after: str = None):
    try:
        logger.info(f"Calling OpenAI API to list assistants with limit: {limit}, after: {after}")
        response = client.beta.assistants.list(limit=limit, after=after)
        logger.info(f"Received response from OpenAI API with {len(response.data)} assistants")
        # Step 1: Retrieve the existing assistant
        assistant_ids = [assistant.id for assistant in response.data]
        if len(existing_assistant.instructions) < 3:
            next_cursor = response.first_id if hasattr(response, 'first_id') else None
            model=assistant.model,
        logger.info(f"Successfully processed {len(assistant_ids)} assistant IDs")
        return assistant_ids
    except Exception as e:
        logger.error(f"Error in list_assistant_ids: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {e.__dict__}")
        raise
# -------------------    
async def list_assistant_info(client: OpenAI, limit: int = 99, after: str = None):
    try:
        logger.info(f"Calling OpenAI API to list assistants with limit: {limit}, after: {after}")
        params = {"limit": limit}
        if after and after.lower() != "after":
            params["after"] = after
        response = client.beta.assistants.list(**params)
        logger.info(f"Received response from OpenAI API with {len(response.data)} assistants")
        
        assistants_info = [{"id": assistant.id, "name": assistant.name} for assistant in response.data]
        
        logger.info(f"Successfully processed {len(assistants_info)} assistant info")
        return assistants_info
    except OpenAIError as e:
        logger.error(f"OpenAI API error in list_assistant_info: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error in list_assistant_info: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error details: {e.__dict__}")
        raise
   

async def update_assistant(client: OpenAI, assistant_id: str, assistant_update: AssistantUpdate) -> AssistantResponse:
    try:
        logger.info(f"::ZEHN:: Updating assistant with ID: {assistant_id}")
        
            
        # Step 1: Retrieve the existing assistant
        existing_assistant = await get_assistant(client, assistant_id)
        if len(existing_assistant.instructions) < 3:
            existing_assistant.instructions = formatted_instructions_1
        
        # Step 2: Compare and create update_data with only modified fields
        update_data = {}
        for field, value in assistant_update.dict(exclude_unset=True, exclude_none=True).items():
            if field in ['temperature', 'top_p']:
                # Ensure temperature and top_p are float values
                if value is not None:
                    update_data[field] = float(value)
            elif getattr(existing_assistant, field, None) != value:
                update_data[field] = value
        
        # Step 3: Handle the 'tools' field separately
        if 'tools' in update_data:
            update_data['tools'] = [
                tool if isinstance(tool, dict) and 'type' in tool
                else {"type": "file_search"}
                for tool in update_data['tools']
            ]
        
        # Step 4: Apply the update if there are changes
        if update_data:
            logger.info(f"::ZEHN:: Updating assistant with data: {update_data}")
            assistant = client.beta.assistants.update(assistant_id, **update_data)
        else:
            logger.info("No changes detected. Skipping update.")
            assistant = existing_assistant
        
        # Step 5: Create and return the response
        response = AssistantResponse(
            id=assistant.id,
            created_at=int(assistant.created_at),
            name=assistant.name,
            description=assistant.description,
            model=assistant.model,
            instructions=assistant.instructions,
            tools=assistant.tools,
            metadata=assistant.metadata,
            temperature=getattr(assistant, 'temperature', None),
            top_p=getattr(assistant, 'top_p', None)
        )
        logger.info(f"::ZEHN:: AssistantResponse updated successfully: {response}")
        return response
    except OpenAIError as oe:
        logger.error(f"OpenAI API error: {str(oe)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}")
    except Exception as e:
        logger.error(f"Unexpected error in update_assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating assistant: {str(e)}")
    



async def delete_assistant(client: OpenAI, assistant_id: str) -> None:
    try:
        logger.info(f"::ZEHN:: Deleting assistant with ID: {assistant_id}")
        client.beta.assistants.delete(assistant_id)
        logger.info(f"::ZEHN:: Assistant {assistant_id} deleted successfully")
    except OpenAIError as oe:
        logger.error(f"OpenAI API error: {str(oe)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}")
    except Exception as e:
        logger.error(f"Unexpected error in delete_assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting assistant: {str(e)}")

    

def filter_assistants_by_metadata(client: OpenAI, metadata: Dict[str, str]) -> List[AssistantResponse]:
    try:
        filtered_assistants = []
        assistants = client.beta.assistants.list(order="desc", limit=100)
        for assistant in assistants:
            if all(assistant.metadata.get(key) == value for key, value in metadata.items()):
                filtered_assistants.append(AssistantResponse(
                    id=assistant.id,
                    object="assistant",
                    created_at=int(assistant.created_at),
                    name=assistant.name,
                    description=assistant.description,
                    model=assistant.model,
                    instructions=assistant.instructions,
                    tools=assistant.tools,
                    metadata=assistant.metadata,
                    temperature=getattr(assistant, 'temperature', None),
                    top_p=getattr(assistant, 'top_p', None)
                ))
        return filtered_assistants
    except OpenAIError as oe:
        logger.error(f"OpenAI API error: {str(oe)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}")
    except Exception as e:
        logger.error(f"Error in filter_assistants_by_metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error filtering assistants: {str(e)}")




async def create_thread(client: OpenAI, assistant_id: str):
    try:
        logger.info(f"::ZEHN:: Creating new thread for assistant {assistant_id}")
        thread = client.beta.threads.create()
        logger.info(f"::ZEHN:: Created new thread with ID {thread.id}")
        return thread
    except OpenAIError as oe:
        logger.error(f"OpenAI API error in create_thread: {str(oe)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(oe)}")
    except Exception as e:
        logger.error(f"Unexpected error in create_thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating thread: {str(e)}")



# *** Create a vector store **********************************
async def create_vector_store(client: OpenAI, assistant_id: str):
    vector_store = client.beta.vector_stores.create(name=f"vector_store_for_asst_{assistant_id}")
    return vector_store

#@@
async def get_assistant_vector_stores(client: OpenAI, assistant_id: str):
    try:
        assistant = await client.beta.assistants.retrieve(assistant_id)
        return assistant.tool_resources.get("file_search", {}).get("vector_store_ids", [])
    except Exception as e:
        logger.error(f"Error retrieving assistant vector stores: {str(e)}")
        return []




@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def send_files_to_vector_store(client: OpenAI, vector_store_id: str, file_paths: List[str]):
    file_streams = []
    try:
        for path in file_paths:
            full_path = os.path.abspath(path)
            if not os.path.exists(full_path):
                logger.error(f"File not found: {full_path}")
                raise FileNotFoundError(f"File not found: {full_path}")
            file_streams.append(open(full_path, "rb"))
#         for path in file_paths:
        logger.info(f"Uploading files to vector store: {vector_store_id}")
        logger.info(f"File paths: {file_paths}")
#                 raise FileNotFoundError(f"File not found: {path}")
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store_id,
            files=file_streams
        )
        logger.info(f"File batch uploaded successfully: {file_batch.id}")
        return file_batch
    except OpenAIError as oe:
        logger.error(f"OpenAI API error in send_files_to_vector_store: {str(oe)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in send_files_to_vector_store: {str(e)}")
        raise
    finally:
        for file in file_streams:
            file.close()
            
            
  
async def update_assistant_with_vector_store(client: OpenAI, assistant_id: str, vector_store_id: str):
    assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    return assistant
