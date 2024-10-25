
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from openai import OpenAI
from app.api.dependencies import get_openai_client
from app.services.assistant_service import send_question, QuestionRequest, QuestionResponse
from app.core.settings.conf import logger
from app.core.settings.redis_client import redis_client

# ------------------------------------------------------------- 
router = APIRouter()


# ********
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from openai import OpenAI
from app.api.dependencies import get_openai_client
from app.services.assistant_service import send_question, create_thread, QuestionRequest, QuestionResponse
from app.core.settings.conf import logger
from app.core.settings.redis_client import redis_client
import json

router = APIRouter()

@router.post("/question/{assistant_id}", response_model=QuestionResponse)
async def send_question_route(
    assistant_id: str,
    question: QuestionRequest,
    client: OpenAI = Depends(get_openai_client)
):
    try:
        question.assistant_id = assistant_id
        
        # Check if we need to create a new thread
        if question.thread_id.lower() == "create":
            new_thread = await create_thread(client, assistant_id)
            question.thread_id = new_thread.id
            
            # Cache the new thread_id in Redis
            redis_client.set(f"{question.user_id}:thread_id", question.thread_id)
        
        # Check if we need to create a new user_id
        if question.user_id.lower() == "create":
            question.user_id = f"user_{assistant_id}_{question.thread_id}"
            
            # Cache the new user_id in Redis
            redis_client.set(f"{assistant_id}:user_id", question.user_id)
        
        logger.info(f"::Zehn:: ::ZEHN:: Sending question to assistant {assistant_id}: {question.content}")
        response = await send_question(client, question)
        logger.info(f"::Zehn:: ::ZEHN:: Received response from assistant {assistant_id}")
        
        return QuestionResponse(
            answer=response["answer"],
            assistant_id=assistant_id,
            user_id=question.user_id,
            thread_id=question.thread_id
        )
    except Exception as e:
        logger.error(f"Error in send_question_route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")