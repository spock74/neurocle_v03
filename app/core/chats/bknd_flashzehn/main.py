# AKA Zehn
# ------------------------------------------------------------------------
# Last Update 17 Dez 2024
# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
from app.core.chats.bknd_flashzehn.prompts.prompt_clm_01 import prompt_sys
from app.core.settings.conf import logger
from app.core.settings.conf import LLM_MODEL_NAME_GPT_4_o_MINI
from app.core.openai_utils.create_client import create_client
from datetime import datetime

client = create_client()

def get_n_questoes(n_questoes:int, file_name:str):
    questoes = client.chat.completions.create(
        model=LLM_MODEL_NAME_GPT_4_o_MINI,
        temperature=0.2,
        top_p=1,
        messages= [ 
            {"role":"system", "content":f"{prompt_sys}"},
            {"role":"user", "content":f"Formule {n_questoes}"},
        ]
    )

    resp = questoes.choices[0].message.content.replace('\n', '')
    tk_in = questoes.usage.completion_tokens
    tk_out = questoes.usage.prompt_tokens
    resposta = {"resp": resp, "tk_in": tk_in, "tk_out": tk_out}
    
    prova = resposta['resp'].replace('\n', '')

    DM = datetime.now().strftime(f"{file_name}_json_v01_%d_%m_%Y_%H_%M_%S")
    with open(f'./provas/prova_{DM}.py', 'w', encoding='utf-8') as f:
        f.write(prova)



if __name__ ==  '__main__':
    
    get_n_questoes(20, "clinica_medica")