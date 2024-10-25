import os
from openai import OpenAI, AssistantEventHandler
from pydantic import BaseModel
from typing_extensions import override

# ------------------------------------------------------------------------
# CREATE CLIENT
#! TODO it must ve balanced in future create a client per LOGGED USER
# ------------------------------------------------------------------------

class OpenAIClientSchema(BaseModel):
    api_key: str = os.getenv("OPENAI_NEUROCURSO_API_KEY")
    organization: str = os.getenv("OPENAI_NEUROCURSO_ORGANIZATION_ID")