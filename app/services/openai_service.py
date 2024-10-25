import openai
from app.core.settings.conf import settings

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    async def get_assistant_response(self, question: str) -> str:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content