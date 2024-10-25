import openai
from app.core.settings.conf import settings

class AudioService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def transcribe_audio(self, audio_content: bytes) -> str:
        response = await openai.Audio.atranscribe("whisper-1", audio_content)
        return response['text']

    async def text_to_speech(self, text: str) -> str:
        response = await openai.Audio.aspeech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        return response.url