import gradio as gr
import requests
import json
import yaml
from typing import Dict, Any, List
import tempfile
import io
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_NEUROCURSO_API_KEY"))

API_BASE_URL = "http://localhost:8000/api/v1"

LANGUAGE = 'ui_config_pt_br.yaml'

# Load configuration
with open(LANGUAGE, 'r') as file:
    config = yaml.safe_load(file)

def process_audio_question(audio, assistant_id, user_id, thread_id):
    if audio is None:
        return "No audio recorded. Please try again.", None, None, None, None
    try:
        audio_file = open(audio, "rb")
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        transcribed_text = transcription.text
        
        # Call send_question with the transcribed text
        question_response = send_question(assistant_id, transcribed_text, user_id, thread_id)
        
        return transcribed_text, question_response, assistant_id, user_id, thread_id
    except Exception as e:
        return f"An error occurred: {str(e)}", None, None, None, None

def create_assistant(name: str, model: str, instructions: str, description: str, user_id: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/assistant"
    payload = {
        "name": name,
        "model": model,
        "instructions": instructions,
        "description": description,
        "user_id": user_id
    }
    response = requests.post(url, json=payload)
    return json.loads(response.text)

def send_question(assistant_id: str, content: str, user_id: str, thread_id: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/question/{assistant_id}"
    payload = {
        "content": content,
        "user_id": user_id,
        "thread_id": thread_id
    }
    response = requests.post(url, json=payload)
    return json.loads(response.text)

def create_or_update_vector_store(assistant_id: str, file_paths: str, uploaded_files: List[tempfile._TemporaryFileWrapper]) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/vectorstores"
    file_paths_list = [path.strip() for path in file_paths.split(',') if path.strip()]
    
    # Add uploaded files to the list
    for uploaded_file in uploaded_files:
        file_paths_list.append(uploaded_file.name)
    
    payload = {
        "assistant_id": assistant_id,
        "file_paths": file_paths_list
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def list_assistants() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/assistants"
    response = requests.get(url)
    return json.loads(response.text)

def clear_create_assistant_form():
    return "", config['ui']['models'][0], "", "", ""

def clear_send_question_form():
    return "", "", "", "", None

def clear_create_vector_store_form():
    return "", "", None

with gr.Blocks() as demo:
    gr.Markdown(config['ui']['labels']['main_title'])
    
    with gr.Tab(config['ui']['labels']['create_assistant']['title']):
        with gr.Row():
            with gr.Column(scale=4):
                name_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['name'])
                model_input = gr.Dropdown(
                    label=config['ui']['labels']['create_assistant']['model'] + " LLM",
                    choices=config['ui']['models'],
                    value=config['ui']['models'][0]
                )
                instructions_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['instructions'] + " | Prompt", lines=10)
                description_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['description'] + " da Assistente")
                user_id_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['user_id'])
            with gr.Column(scale=1):
                temperature = gr.Slider(label="Temperature", minimum=0, maximum=2, step=0.1, value=1.0)
                top_p = gr.Slider(label="Top P", minimum=-1, maximum=1, step=0.1, value=1.0)
                create_btn = gr.Button(config['ui']['labels']['create_assistant']['create_button'], variant="primary")
                clear_btn = gr.Button(config['ui']['labels']['create_assistant']['clear_button'],  variant="secondary")
        create_output = gr.JSON(label=config['ui']['labels']['create_assistant']['result'])
        create_btn.click(create_assistant, inputs=[name_input, model_input, instructions_input, description_input, user_id_input], outputs=create_output)
        clear_btn.click(clear_create_assistant_form, outputs=[name_input, model_input, instructions_input, description_input, user_id_input])
    
    with gr.Tab(config['ui']['labels']['send_question']['title']):
        with gr.Row():
            with gr.Column(scale=3):
                assistant_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['assistant_id'])
                question_input = gr.Textbox(label=config['ui']['labels']['send_question']['question'])
                user_id_question = gr.Textbox(label=config['ui']['labels']['send_question']['user_id'])
                thread_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['thread_id'])
            with gr.Column(scale=1):
                send_btn = gr.Button(config['ui']['labels']['send_question']['send_button'], variant="primary")
                clear_question_btn = gr.Button(config['ui']['labels']['send_question']['clear_button'])
        question_output = gr.JSON(label=config['ui']['labels']['send_question']['result'])
        send_btn.click(send_question, inputs=[assistant_id_input, question_input, user_id_question, thread_id_input], outputs=question_output)
        clear_question_btn.click(clear_send_question_form, outputs=[assistant_id_input, question_input, user_id_question, thread_id_input])
    
    with gr.Tab(config['ui']['labels']['audio_question']['title']):
        gr.Markdown("# Ask a question using your voice")
        with gr.Row():
            with gr.Column(scale=3):
                audio_assistant_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['assistant_id'])
                audio_input = gr.Audio(sources="microphone", type="filepath")
                audio_question_input = gr.Textbox(label=config['ui']['labels']['send_question']['question'])
                audio_user_id_question = gr.Textbox(label=config['ui']['labels']['send_question']['user_id'])
                audio_thread_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['thread_id'])
            with gr.Column(scale=1):
                submit_audio_btn = gr.Button(config['ui']['labels']['audio_question']['submit_button'], variant="primary")
                clear_audio_question_btn = gr.Button(config['ui']['labels']['send_question']['clear_button'])
        audio_question_output = gr.JSON(label=config['ui']['labels']['send_question']['result'])
        submit_audio_btn.click(
            fn=process_audio_question,
            inputs=[audio_input, audio_assistant_id_input, audio_user_id_question, audio_thread_id_input],
            outputs=[audio_question_input, audio_question_output, audio_assistant_id_input, audio_user_id_question, audio_thread_id_input]
        )
        clear_audio_question_btn.click(clear_send_question_form, outputs=[audio_assistant_id_input, audio_question_input, audio_user_id_question, audio_thread_id_input])
    
    with gr.Tab(config['ui']['labels']['create_vector_store']['title']):
        with gr.Row():
            with gr.Column(scale=3):
                vs_assistant_id = gr.Textbox(label=config['ui']['labels']['create_vector_store']['assistant_id'])
                file_paths_input = gr.Textbox(label=config['ui']['labels']['create_vector_store']['file_paths'], visible=False)
                file_upload = gr.File(label="Or upload files", file_count="multiple")
            with gr.Column(scale=1):
                vs_create_btn = gr.Button(config['ui']['labels']['create_vector_store']['create_button'], variant="primary")
                clear_vs_btn = gr.Button(config['ui']['labels']['create_vector_store']['clear_button'])
        vs_output = gr.JSON(label=config['ui']['labels']['create_vector_store']['result'])
        vs_create_btn.click(create_or_update_vector_store, inputs=[vs_assistant_id, file_paths_input, file_upload], outputs=vs_output)
        clear_vs_btn.click(clear_create_vector_store_form, outputs=[vs_assistant_id, file_paths_input, file_upload])
    
    with gr.Tab(config['ui']['labels']['list_assistants']['title']):
        list_btn = gr.Button(config['ui']['labels']['list_assistants']['list_button'], variant="primary")
        list_output = gr.JSON(label=config['ui']['labels']['list_assistants']['result'])
        list_btn.click(list_assistants, outputs=list_output)

demo.launch(share=True)




# import gradio as gr
# import requests
# import json
# import yaml
# from typing import Dict, Any, List
# import tempfile
# import io
# # from app.utils.process_decode_text import process_text

# import os
# from openai import OpenAI
# client = OpenAI(api_key=os.getenv("OPENAI_NEUROCURSO_API_KEY"))

# API_BASE_URL = "http://localhost:8000/api/v1"

# LANGUAGE = 'ui_config_pt_br.yaml'

# # Load configuration
# with open(LANGUAGE, 'r') as file:
#     config = yaml.safe_load(file)
    
    
    
# #@@=================================
# # def g_(s):
# #     audio_file= open(s, "rb")
# #     transcription = client.audio.transcriptions.create(
# #         model="whisper-1", 
# #         file=audio_file
# #     )
# #     print(transcription.text)


# def process_audio_question(audio):
#     if audio is None:
#         return "No audio recorded. Please try again.", None
#     try:
#         audio_file= open(audio, "rb")
#         transcription = client.audio.transcriptions.create(
#             model="whisper-1", 
#             file=audio_file
#         )
#         print(transcription.text)
#         # return transcription.text
    
#     # with open(audio_path, 'rb') as audio_file:
#     #     files = {"audio_file": ("question.wav", audio_file, "audio/wav")}
#         # response = requests.post(f"{API_BASE_URL}/audio_question", files=files)
    
#     # if True: #response.status_code == 200:
#         # result = response.json()
#         return transcription.text, audio #result["text_response"], result["audio_response"]
#         # else:or: {response.status_code} - {response.text}", None
#     except Exception as e:
#         return f"An error occurred: {str(e)}", None
# #@@=================================    
    

# def create_assistant(name: str, model: str, instructions: str, description: str, user_id: str) -> Dict[str, Any]:
#     url = f"{API_BASE_URL}/assistant"
#     payload = {
#         "name": name,
#         "model": model,
#         "instructions": instructions,
#         "description": description,
#         "user_id": user_id
#     }
#     response = requests.post(url, json=payload)
#     return json.loads(response.text)


# def send_question(assistant_id: str, content: str, user_id: str, thread_id: str) -> Dict[str, Any]:
#     url = f"{API_BASE_URL}/question/{assistant_id}"
#     payload = {
#         "content": content,
#         "user_id": user_id,
#         "thread_id": thread_id
#     }
#     response = requests.post(url, json=payload)
#     return json.loads(response.text)
    
   
# def create_or_update_vector_store(assistant_id: str, file_paths: str, uploaded_files: List[tempfile._TemporaryFileWrapper]) -> Dict[str, Any]:
#     url = f"{API_BASE_URL}/vectorstores"
#     file_paths_list = [path.strip() for path in file_paths.split(',') if path.strip()]
    
#     # Add uploaded files to the list
#     for uploaded_file in uploaded_files:
#         file_paths_list.append(uploaded_file.name)
    
#     payload = {
#         "assistant_id": assistant_id,
#         "file_paths": file_paths_list
#     }
#     response = requests.post(url, json=payload)
#     if response.status_code == 200:
#         return json.loads(response.text)
#     else:
#         raise Exception(f"Error: {response.status_code}, {response.text}")

# def list_assistants() -> Dict[str, Any]:
#     url = f"{API_BASE_URL}/assistants"
#     response = requests.get(url)
#     return json.loads(response.text)

# def clear_create_assistant_form():
#     return "", config['ui']['models'][0], "", "", ""

# def clear_send_question_form():
#     return "", "", "", ""

# def clear_create_vector_store_form():
#     return "", "", None

# with gr.Blocks() as demo:
#     gr.Markdown(config['ui']['labels']['main_title'])
    
#     with gr.Tab(config['ui']['labels']['create_assistant']['title']):
#         with gr.Row():
#             with gr.Column(scale=4):
#                 name_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['name'])
#                 model_input = gr.Dropdown(
#                     label=config['ui']['labels']['create_assistant']['model'] + " LLM",
#                     choices=config['ui']['models'],
#                     value=config['ui']['models'][0]
#                 )
#                 instructions_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['instructions'] + " | Prompt", lines=10)
#                 description_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['description'] + " da Assistente")
#                 user_id_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['user_id'])
#             with gr.Column(scale=1):
#                 temperature = gr.Slider(label="Temperature", minimum=0, maximum=2, step=0.1, value=1.0)
#                 top_p = gr.Slider(label="Top P", minimum=-1, maximum=1, step=0.1, value=1.0)

#                 create_btn = gr.Button(config['ui']['labels']['create_assistant']['create_button'], variant="primary")
                
#                 clear_btn = gr.Button(config['ui']['labels']['create_assistant']['clear_button'],  variant="secondary")
#         create_output = gr.JSON(label=config['ui']['labels']['create_assistant']['result'])
#         create_btn.click(create_assistant, inputs=[name_input, model_input, instructions_input, description_input, user_id_input], outputs=create_output)
#         clear_btn.click(clear_create_assistant_form, outputs=[name_input, model_input, instructions_input, description_input, user_id_input])
    
#     with gr.Tab(config['ui']['labels']['send_question']['title']):
#         with gr.Row():
#             with gr.Column(scale=3):
#                 assistant_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['assistant_id'])
#                 question_input = gr.Textbox(label=config['ui']['labels']['send_question']['question'])
#                 user_id_question = gr.Textbox(label=config['ui']['labels']['send_question']['user_id'])
#                 thread_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['thread_id'])
#             with gr.Column(scale=1):
#                 send_btn = gr.Button(config['ui']['labels']['send_question']['send_button'], variant="primary")
#                 clear_question_btn = gr.Button(config['ui']['labels']['send_question']['clear_button'])
                
#         question_output = gr.JSON(label=config['ui']['labels']['send_question']['result'])
#         send_btn.click(send_question, inputs=[assistant_id_input, question_input, user_id_question, thread_id_input], outputs=question_output)
#         clear_question_btn.click(clear_send_question_form, outputs=[assistant_id_input, question_input, user_id_question, thread_id_input])
        
#     #@ ++++++++++++++++++++++
#     # with gr.Tab(config['ui']['labels']['audio_question']['title']):
#     #     gr.Markdown("# Ask a question using your voice")
#     #     # audio_input = gr.Audio(sources="microphone", type="filepath")
#     #     audio_input = gr.Audio(sources="microphone")
#     #     submit_audio_btn = gr.Button(config['ui']['labels']['audio_question']['submit_button'], variant="primary")
#     #     text_output = gr.Textbox(label=config['ui']['labels']['audio_question']['text_response'])
#     #     audio_output = gr.Audio(label=config['ui']['labels']['audio_question']['audio_response'])
        
#     #     submit_audio_btn.click(
#     #         fn=process_audio_question,
#     #         inputs=[audio_input],
#     #         outputs=[text_output, audio_output]
#     # )    
#     with gr.Tab(config['ui']['labels']['audio_question']['title']):
#         gr.Markdown("# Ask a question using your voice")
#         audio_input = gr.Audio(sources="microphone", type="filepath")
#         submit_audio_btn = gr.Button(config['ui']['labels']['audio_question']['submit_button'], variant="primary")
#         text_output = gr.Textbox(label=config['ui']['labels']['audio_question']['text_response'])
#         audio_output = gr.Audio(label=config['ui']['labels']['audio_question']['audio_response'])
        
#         submit_audio_btn.click(
#             fn=process_audio_question,
#             inputs=[audio_input],
#             outputs=[text_output, audio_output]
#         )    
#     #@ ++++++++++++++++++++++    
    
#     with gr.Tab(config['ui']['labels']['create_vector_store']['title']):
#         with gr.Row():
#             with gr.Column(scale=3):
#                 vs_assistant_id = gr.Textbox(label=config['ui']['labels']['create_vector_store']['assistant_id'])
#                 file_paths_input = gr.Textbox(label=config['ui']['labels']['create_vector_store']['file_paths'], visible=False)
#                 file_upload = gr.File(label="Or upload files", file_count="multiple")
#             with gr.Column(scale=1):
#                 vs_create_btn = gr.Button(config['ui']['labels']['create_vector_store']['create_button'], variant="primary")
#                 clear_vs_btn = gr.Button(config['ui']['labels']['create_vector_store']['clear_button'])
#         vs_output = gr.JSON(label=config['ui']['labels']['create_vector_store']['result'])
#         vs_create_btn.click(create_or_update_vector_store, inputs=[vs_assistant_id, file_paths_input, file_upload], outputs=vs_output)
#         clear_vs_btn.click(clear_create_vector_store_form, outputs=[vs_assistant_id, file_paths_input, file_upload])
    
#     with gr.Tab(config['ui']['labels']['list_assistants']['title']):
#         list_btn = gr.Button(config['ui']['labels']['list_assistants']['list_button'], variant="primary")
#         list_output = gr.JSON(label=config['ui']['labels']['list_assistants']['result'])
#         list_btn.click(list_assistants, outputs=list_output)

# demo.launch(share=True)


# # import gradio as gr
# # import requests
# # import json
# # import yaml
# # from typing import Dict, Any

# # API_BASE_URL = "http://localhost:8000/api/v1"

# # LANGUAGE = 'ui_config_pt_br.yaml'

# # # Load configuration
# # with open(LANGUAGE, 'r') as file:
# #     config = yaml.safe_load(file)

# # def create_assistant(name: str, model: str, instructions: str, description: str, user_id: str) -> Dict[str, Any]:
# #     url = f"{API_BASE_URL}/assistant"
# #     payload = {
# #         "name": name,
# #         "model": model,
# #         "instructions": instructions,
# #         "description": description,
# #         "user_id": user_id
# #     }
# #     response = requests.post(url, json=payload)
# #     return json.loads(response.text)

# # def send_question(assistant_id: str, content: str, user_id: str, thread_id: str) -> Dict[str, Any]:
# #     url = f"{API_BASE_URL}/question/{assistant_id}"
# #     payload = {
# #         "content": content,
# #         "user_id": user_id,
# #         "thread_id": thread_id
# #     }
# #     response = requests.post(url, json=payload)
# #     return json.loads(response.text)

# # def create_or_update_vector_store(assistant_id: str, file_paths: str) -> Dict[str, Any]:
# #     url = f"{API_BASE_URL}/vectorstores"
# #     file_paths_list = [path.strip() for path in file_paths.split(',') if path.strip()]
# #     payload = {
# #         "assistant_id": assistant_id,
# #         "file_paths": file_paths_list
# #     }
# #     response = requests.post(url, json=payload)
# #     if response.status_code == 200:
# #         return json.loads(response.text)
# #     else:
# #         raise Exception(f"Error: {response.status_code}, {response.text}")

# # def list_assistants() -> Dict[str, Any]:
# #     url = f"{API_BASE_URL}/assistants"
# #     response = requests.get(url)
# #     return json.loads(response.text)

# # def clear_create_assistant_form():
# #     return "", config['ui']['models'][0], "", "", ""

# # def clear_send_question_form():
# #     return "", "", "", ""

# # def clear_create_vector_store_form():
# #     return "", ""

# # with gr.Blocks() as demo:
# #     gr.Markdown(config['ui']['labels']['main_title'])
    
# #     with gr.Tab(config['ui']['labels']['create_assistant']['title']):
# #         with gr.Row():
# #             with gr.Column(scale=4):
# #                 name_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['name'])
# #                 model_input = gr.Dropdown(
# #                     label=config['ui']['labels']['create_assistant']['model'] + " LLM",
# #                     choices=config['ui']['models'],
# #                     value=config['ui']['models'][0]
# #                 )
# #                 instructions_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['instructions'] + " | Prompt", lines=10)
# #                 description_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['description'] + " da Assistente")
# #                 user_id_input = gr.Textbox(label=config['ui']['labels']['create_assistant']['user_id'])
# #             with gr.Column(scale=1):
# #                 temperature = gr.Slider(label="Temperature", minimum=0, maximum=2, step=0.1, value=1.0)
# #                 top_p = gr.Slider(label="Top P", minimum=-1, maximum=1, step=0.1, value=1.0)

# #                 create_btn = gr.Button(config['ui']['labels']['create_assistant']['create_button'], variant="primary")
                
# #                 clear_btn = gr.Button(config['ui']['labels']['create_assistant']['clear_button'],  variant="secondary")
# #         create_output = gr.JSON(label=config['ui']['labels']['create_assistant']['result'])
# #         create_btn.click(create_assistant, inputs=[name_input, model_input, instructions_input, description_input, user_id_input], outputs=create_output)
# #         clear_btn.click(clear_create_assistant_form, outputs=[name_input, model_input, instructions_input, description_input, user_id_input])
    
# #     with gr.Tab(config['ui']['labels']['send_question']['title']):
# #         with gr.Row():
# #             with gr.Column(scale=3):
# #                 assistant_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['assistant_id'])
# #                 question_input = gr.Textbox(label=config['ui']['labels']['send_question']['question'])
# #                 user_id_question = gr.Textbox(label=config['ui']['labels']['send_question']['user_id'])
# #                 thread_id_input = gr.Textbox(label=config['ui']['labels']['send_question']['thread_id'])
# #             with gr.Column(scale=1):
# #                 send_btn = gr.Button(config['ui']['labels']['send_question']['send_button'], variant="primary")
# #                 clear_question_btn = gr.Button(config['ui']['labels']['send_question']['clear_button'])
# #         question_output = gr.JSON(label=config['ui']['labels']['send_question']['result'])
# #         send_btn.click(send_question, inputs=[assistant_id_input, question_input, user_id_question, thread_id_input], outputs=question_output)
# #         clear_question_btn.click(clear_send_question_form, outputs=[assistant_id_input, question_input, user_id_question, thread_id_input])
    
# #     with gr.Tab(config['ui']['labels']['create_vector_store']['title']):
# #         with gr.Row():
# #             with gr.Column(scale=3):
# #                 vs_assistant_id = gr.Textbox(label=config['ui']['labels']['create_vector_store']['assistant_id'])
# #                 file_paths_input = gr.Textbox(label=config['ui']['labels']['create_vector_store']['file_paths'])
# #             with gr.Column(scale=1):
# #                 vs_create_btn = gr.Button(config['ui']['labels']['create_vector_store']['create_button'], variant="primary")
# #                 clear_vs_btn = gr.Button(config['ui']['labels']['create_vector_store']['clear_button'])
# #         vs_output = gr.JSON(label=config['ui']['labels']['create_vector_store']['result'])
# #         vs_create_btn.click(create_or_update_vector_store, inputs=[vs_assistant_id, file_paths_input], outputs=vs_output)
# #         clear_vs_btn.click(clear_create_vector_store_form, outputs=[vs_assistant_id, file_paths_input])
    
# #     with gr.Tab(config['ui']['labels']['list_assistants']['title']):
# #         list_btn = gr.Button(config['ui']['labels']['list_assistants']['list_button'], variant="primary")
# #         list_output = gr.JSON(label=config['ui']['labels']['list_assistants']['result'])
# #         list_btn.click(list_assistants, outputs=list_output)

# # demo.launch(share=True)