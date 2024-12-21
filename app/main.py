from app.middleware.question_interceptor import question_interceptor
from app.core.db import Base, engine
from fastapi import FastAPI
from app.api.api_v1.endpoints.users import router as users_router2
from app.api.api_v1.endpoints.items import router as items_router
from app.api.api_v1.endpoints.assistants import router as assistants_router
from app.api.api_v1.endpoints.questions import router as question_router
from app.api.api_v1.endpoints.vector_stores import router as vector_store_router
from app.api.api_v1.endpoints.threads import router as thread_router
from app.api.api_v1.endpoints.auth import router as auth_router
from app.api.api_v1.endpoints.prompts import router as prompt_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings.conf import logger
# from app.db.vector_store_db import init_question_log_db
from app.api.api_v1.endpoints import question_audio
from app.core.settings.conf import settings
from app.core.database import init_db
import sqlite3

app = FastAPI()


# init_db()  # Add this line
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        
        
# init_question_log_db()


app.middleware("http")(question_interceptor)


origins = [
    "http://localhost:3000",  # Assuming your frontend is running on port 3000
    "http://localhost:8080",  # Add any other origins you need
    "http://localhost:8000",  # Add any other origins you need
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
]

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # URL do Vite
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

logger.debug("CORS configurado com as origens permitidas: %s", "*")

app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
app.include_router(assistants_router, prefix="/api/v1", tags=["Assistants"])
app.include_router(vector_store_router, prefix="/api/v1", tags=["Vector Stores"])
app.include_router(thread_router, prefix="/api/v1", tags=["Theads"])
app.include_router(question_router, prefix="/api/v1", tags=["Questions"])
app.include_router(question_audio.router, prefix="/api/v1", tags=["Audio Questions"])
app.include_router(prompt_router, prefix="/api/v1", tags=["Optimizes prompt"])
# app.include_router(items_router, prefix="/items", tags=["items"])

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)
logger.debug("Tabelas criadas no banco de dados.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", reload=True)