from fastapi import Request
from app.core.settings.conf import logger
from fastapi import Request
from app.core.settings.conf import logger
import json
import redis
from app.api.api_v1.assistants_schema import QuestionRequest
from app.core.settings.redis_client import redis_client

async def log_question_request(request: QuestionRequest):
    # Extract relevant information from the request
    user_id = request.user_id
    assistant = request.assistant_id
    trhead_id = request.thread_id
    
    # Log the information
    logger.info(f"::Zehn:: ::ZEHN:: ::ZEHN:: User_ID: {user_id}, Assistant_ID: {assistant}, Thread_ID: {trhead_id}")

async def question_interceptor(request: Request, call_next):
    # Call our logging function
    await log_question_request(request)
    
    # Continue with the request
    response = await call_next(request)
    return response


# funcao recebe um json e consulta se cada par key-value do mesmo esta em cache no redis se nao estiver, cria no redis o caache dar dados com chave sendo a chave do json prefixados com o valor da chave uder_id
def check_and_cache_json(user_id: str, json_data: dict, redis_client: redis.Redis):
    for key, value in json_data.items():
        cache_key = f"{user_id}:{key}"
        
        # Check if the key-value pair is in cache
        if not redis_client.exists(cache_key):
            # If not in cache, create it
            redis_client.set(cache_key, json.dumps(value))
            print(f"Cached: {cache_key}")
        else:
            print(f"Already in cache: {cache_key}")





async def log_question_request(request: Request):
    # Extract relevant information from the request
    method = request.method
    url = str(request.url)
    client_host = request.client.host if request.client else "Unknown"
    
    # Extract the request body
    body = await request.body()
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError:
        body_json = "Unable to parse JSON"

    # Log the information
    logger.info(f"::Zehn:: ::ZEHN::============ Question Request - Method: {method}, URL: {url}, Client: {client_host}")
    logger.info(f"::Zehn:: ::ZEHN::============ Request Body: {body_json}")
    
    check_and_cache_json("user123", {"name": "<NAME>", "age": 30, "city": "New York"}, redis_client)
    

async def question_interceptor(request: Request, call_next):
    # Call our logging function
    await log_question_request(request)
    
    # Continue with the request
    response = await call_next(request)
    return response