import os
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
    

from sqlalchemy.orm import Session
# from app.models.assistant import Assistant

class AssistantCreate(BaseModel):
    name: str
    model: str = "gpt-4o-mini"
    instructions: Optional[str] = None
    description: Optional[str] = None
    tools: Optional[List[Dict]] = None
    metadata: Optional[dict] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    top_p: Optional[float] = Field(None, ge=-1, le=1)
    user_id: str


class AssistantResponse(BaseModel):
    id_asst: str
    object: str
    created_at: int
    name: str
    description: Optional[str] = None
    model: str
    instructions: Optional[str] = None
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    class Config:
        populate_by_name = True
    @validator("tools", pre=True)
    def validate_tools(cls, v):
        if isinstance(v, list):
            return [tool.dict() if hasattr(tool, "dict") else tool for tool in v]
        return v


class AssistantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    instructions: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    


class AssistantListParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=99, description="Number of assistants to return")
    after: Optional[str] = None
        
    
    
## ===========================================================================+    
    # Add this new schema
class VectorStoreListResponse(BaseModel):
    id: str
    name: str
    created_at: int
    file_counts: dict
    status: str
    
class FileCountsResponse(BaseModel):
    total: int
    completed: int
    in_progress: int
    failed: int
    cancelled: int

class VectorStoreResponse(BaseModel):
    id: str
    name: str
    created_at: int
    status: str
    file_counts: FileCountsResponse
## ===========================================================================+    
        
    
    

class QuestionRequest(BaseModel):
    content: str = ""
    user_id: str = ""
    assistant_id: str = ""
    thread_id: str = ""



class QuestionResponse(BaseModel):
    answer: str
    assistant_id: str
    user_id: str
    thread_id: str



class OpenAIClientSchema(BaseModel):
    api_key: str = os.getenv("OPENAI_NEUROCURSO_API_KEY")
    organization: str = os.getenv("OPENAI_NEUROCURSO_ORGANIZATION_ID")



class OpenAIAssistantSchema(BaseModel):
    api_key: str = os.getenv("OPENAI_NEUROCURSO_API_KEY"  )
    organization: str = os.getenv("OPENAI_NEUROCURSO_ORGANIZATION_ID")
    


class FileUpload(BaseModel):
    file_paths: List[str]



class FileUploadResponse(BaseModel):
    status: str
    file_counts: dict
    
    
class VectorStoreCreate(BaseModel):
    assistant_id: str
    file_paths: List[str]
    
    

class VectorStoreResponse(BaseModel):
    vector_store_id: str
    file_batch_status: str
    file_counts: Dict[str, int]

class ThreadCreate(BaseModel):
    pass

class  ThreadResponse(BaseModel):
    pass