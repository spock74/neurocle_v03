
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import openai
from app.core.settings.conf import settings
from app.services.openai_service import OpenAIService
from app.services.audio_service import AudioService

router = APIRouter()

class AudioQuestionResponse(BaseModel):
    text_response: str
    audio_response: str  # This will be a URL or base64 encoded audio
    
@router.post("/audio_question", response_model=AudioQuestionResponse)
async def process_audio_question(audio_file: UploadFile = File(...)):
    try:
        # Initialize services
        openai_service = OpenAIService()
        audio_service = AudioService()

        # Step 1: Convert audio to text using Whisper
        audio_content = await audio_file.read()
        transcription = await audio_service.transcribe_audio(audio_content)

        # Step 2: Submit transcribed text to assistant
        assistant_response = await openai_service.get_assistant_response(transcription)

        # Step 3: Convert assistant's response to speech
        audio_response = await audio_service.text_to_speech(assistant_response)

        return AudioQuestionResponse(
            text_response=assistant_response,
            audio_response=audio_response
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    