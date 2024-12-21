
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from openai import OpenAI
from app.api.dependencies import get_openai_client
from app.services.assistant_service import send_question, QuestionRequest, QuestionResponse
from app.core.settings.conf import logger
from app.core.settings.redis_client import redis_client
import json
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.api.api_v1.assistants_schema import QuestionResponse
from app.core.security import get_current_user
from app.db.cruds_operations import get_questions
from app.services.assistant_service import create_thread
# ------------------------------------------------------------- 


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
            # redis_client.set(f"{question.user_id}:thread_id", question.thread_id)
        
        # Check if we need to create a new user_id
        if question.user_id.lower() == "create":
            question.user_id = f"user_{assistant_id}_{question.thread_id}"
            
            # Cache the new user_id in Redis
            # redis_client.set(f"{assistant_id}:user_id", question.user_id)
        
        logger.info(f"::Zehn:: ::ZEHN:: Sending question to assistant {assistant_id}: {question.content}")
        response = await send_question(client, question)
        logger.info(f"::Zehn:: ::ZEHN:: Received response from assistant {assistant_id}")
        
        return QuestionResponse(
            answer=response['answer'],
            assistant_id=question.assistant_id,
            user_id=question.user_id,
            thread_id=response['thread_id']
        )
    except Exception as e:
        logger.error(f"Error in send_question_route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
##  ----------------------------------------------------------------------------------------
    




## listar questoes
##  ----------------------------------------------------------------------------------------
@router.get("/questions", response_model=List[QuestionResponse])
async def list_questions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    tag: Optional[str] = None
):
    """
    List all questions with optional filtering.
    """
    try:
        logger.info("Requesting questions list")
        logger.info(f"Filters: subject={subject}, difficulty={difficulty}, tag={tag}")
        
        questions = get_questions(
            skip=skip,
            limit=limit,
            subject=subject,
            difficulty=difficulty,
            tag=tag
        )
        
        # Validar cada questão antes de retornar
        validated_questions = []
        for q in questions:
            try:
                validated_question = QuestionResponse(**q)
                validated_questions.append(validated_question)
            except Exception as validation_error:
                logger.error(f"Validation error for question: {q}")
                logger.error(f"Error: {str(validation_error)}")
                continue
        
        logger.info(f"Found {len(validated_questions)} valid questions")
        return validated_questions
        
    except Exception as e:
        logger.error(f"Error listing questions: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing questions: {str(e)}"
        )


