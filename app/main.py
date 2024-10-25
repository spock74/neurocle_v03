from app.middleware.question_interceptor import question_interceptor
from app.core.db import Base, engine
from fastapi import FastAPI
from app.api.api_v1.endpoints.users import router as users_router
from app.api.api_v1.endpoints.items import router as items_router
from app.api.api_v1.endpoints.assistants import router as assistants_router
from app.api.api_v1.endpoints.questions import router as question_router
from app.api.api_v1.endpoints.vector_stores import router as vector_store_router
from app.api.api_v1.endpoints.threads import router as thread_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings.conf import logger
from app.db.vector_store_db import init_db  # Add this line
from app.db.vector_store_db import init_question_log_db


# Configuração do logging
from app.core.settings.conf import logger

app = FastAPI()

init_db()  # Add this line
init_question_log_db()

app.middleware("http")(question_interceptor)

origins = [
    "http://localhost:3000",  # Assuming your frontend is running on port 3000
    "http://localhost:8080",  # Add any other origins you need
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assistants_router, prefix="/api/v1", tags=["Assistants"])
app.include_router(vector_store_router, prefix="/api/v1", tags=["Vector Stores"])
app.include_router(thread_router, prefix="/api/v1", tags=["Theads"])
app.include_router(question_router, prefix="/api/v1", tags=["Questions"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])
# app.include_router(items_router, prefix="/items", tags=["items"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)
logger.debug("Tabelas criadas no banco de dados.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logger.debug("CORS configurado com as origens permitidas: %s", "*")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)
    
    
    
# import os
# from anthropic import Anthropic


# client = anthropic.Anthropic(
#     # defaults to os.environ.get("ANTHROPIC_API_KEY")
#     api_key="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",
# )


# client = Anthropic(
#     # This is the default and can be omitted
#     api_key="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"
# )

# message = client.messages.create(
#     max_tokens=1024,
#     messages=[
#         {
#             "role": "user",
#             "content": "Hello, Claude",
#         }
#     ],
#     model="claude-3-opus-20240229",
# )
# print(message.content)
# print(message.content)    