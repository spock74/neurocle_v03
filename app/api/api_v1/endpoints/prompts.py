instr = """
Você é um modelo de linguagem de IA especializado em otimizar textos. 
Sua tarefa é receber um texto e transformá-lo em um prompt otimizado. 
O prompt resultante deve ser uma instrução para outro modelo de chat baseado na OpenAI sobre como converter um texto submetido em um prompt de alta qualidade e otimizado para uma tarefa específica. O prompt otimizado deve:
1. Declarar claramente o objetivo da tarefa.
2. Fornecer instruções passo a passo para orientar o modelo de IA na execução do objetivo.
3. Garantir que a saída seja precisa, prática e formatada para maximizar a usabilidade e clareza para o propósito pretendido.

Receba o texto fornecido e reescreva-o seguindo as instruções acima. Certifique-se de que o prompt otimizado criado seja autossuficiente e possa ser usado de forma eficaz para instruir um modelo de chat da OpenAI a realizar a mesma tarefa.
"""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter()


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# #! Refatorar schema e model para arquivos apropriados
# from app.api.api_v1.schemas.prompt_schema import PromptRequest, PromptResponse§
# ----------------------------------------------------------------------
class PromptRequest(BaseModel):
    prompt_down: str
# ----------------------------------------------------------------------
class PromptResponse(BaseModel):
    prompt_upsado: str
    tk_in: int
    tk_out: int
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
  
    
    
# ------------------------------------------------------------------------
# #! Refatorar para sources auxiliares adequados
# ------------------------------------------------------------------------
# from app.core.chats.bknd_flashzehn.prompts.prompt_clm_01 import prompt_sys
from app.core.settings.conf import logger
from app.core.settings.conf import LLM_MODEL_NAME_GPT_4_o_MINI
from app.core.openai_utils.create_client import create_client
from datetime import datetime

# prompt_down = "Prova escrita para neurologista como a prova da ABN"
def f_(prompt_down:str):
    client = create_client()
    p_ = client.chat.completions.create(
        model=LLM_MODEL_NAME_GPT_4_o_MINI,
        temperature=0.2,
        top_p=1,
        messages= [ 
            {"role":"system", "content":instr},
            {"role":"user", "content":f"O texto a ser otimizado é {prompt_down}"},
        ]
    )
    prompt_upsado = p_.choices[0].message.content#.replace('\n', '')
    tk_in = p_.usage.completion_tokens
    tk_out = p_.usage.prompt_tokens
    
    return PromptResponse(prompt_upsado=str(prompt_upsado), tk_in=tk_in, tk_out=tk_out)
    

    
    
    
    
@router.post("/prompt_up", response_model=PromptResponse)
async def rise_prompt(prompt_request: PromptRequest):
    """
    Endpoint to process the prompt and return the response.
    """
    try:
        return f_(prompt_request.prompt_down)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))