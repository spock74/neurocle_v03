# ------------------------------------------------------------------------
# CR Jose E Moraes
# AKA Zehn
# ------------------------------------------------------------------------
# Last Update 13 set 2024
# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
# Based on
# from https://platform.openai.com/docs/assistants/overview
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
import os
import time
import datetime
import glob
from openai import OpenAI, OpenAIError
from typing_extensions import override
from openai import AssistantEventHandler
from app.core.asst.a0_cefaleias_v01 import instructions
from app.api.api_v1.assistants_schema import QuestionRequest, QuestionResponse
from app.core.settings.conf import logger
# ------------------------------------------------------------------------


# ------------------------------------------------------------------------
# CREATE CLIENT
#! TODO it must ve balanced in future create a client per LOGGED USER
client = OpenAI(api_key=os.getenv("OPENAI_NEUROCURSO_API_KEY"))
# ------------------------------------------------------------------------
# # Create a vector store caled "Financial Statements"
# *** Create a vector store **********************************
def create_vector_store(client, assistant):
    vector_store = client.beta.vector_stores.create(name=f"vector_store_for_asst_{assistant.id}")
    return vector_store
# ------------------------------------------------------------------------
# *** Send files to vector store *****************************
def send_files_to_vector_store(client, vector_store, file_paths):
    # Open each file in binary mode and store the file streams in a list
    file_streams = [open(path, "rb") for path in file_paths]

    # Use the upload and poll SDK helper to upload the files, add them to 
    # the vector store, and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
    
    logger.info(f"::Zehn:: ::ZEHN:: ::zehn:: file_batch.status")
    logger.info(f"::Zehn:: ::ZEHN:: ::zehn:: file_batch.status: {file_batch.status}")
    logger.info(f"::Zehn:: ::ZEHN:: ::zehn:: file_batch.file_counts: {file_batch.file_counts}")

    return file_batch
# ------------------------------------------------------------------------



# *** Update the assistant to use the new Vector Store *******************
# Step 3: UPDATE THE ASSISTANT to to use the new Vector Store
# To make the files accessible to your assistant, update the assistant’s 
# tool_resources with the new vector_store id.
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
def update_assistant_with_vector_store(client, assistant, vector_store):
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": 
            {"vector_store_ids": 
                [vector_store.id]
                }
            },
    )
# 
# ************************************************************************
async def insert_to_vector_storage(assistant_id: str, vector):
    try:
        # Logic to insert the vector into the vector storage
        vector_store = await client.beta.vector_stores.create(name=f"{assistant_id}_vector_store")
        await client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=[vector]  # Assuming vector is in the correct format
        )
        return vector_store
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting vector: {e}")
# ************************************************************************
# ------------------------------------------------------------------------ 
# ------------------------------------------------------------------------ 

# ========================================================================
# STEP 4: CREATE A THREAD
# ------------------------------------------------------------------------
# thread = client.beta.threads.create()
def create_thread(client):
    thread = client.beta.threads.create()
    return thread

def create_message(client, thread, role, content):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role=role,
        content=content
    )
    print(f"{role} > {content}")
    return message


#! ----------------------------------------------------------------------
#! VECTOR STORES CREATED USING MESSAGE ATTACHEMENTS HAVE A DEFAULT 
#! EXPIRATION POLICY OF 7 DAYS AFTER THEY WERE LAST ACTIVE (DEFINED 
#! AS THE LAST TIME THE VECTOR STORE WAS PART OF A RUN). 
#! 
#! TO THIS DEFAULT: 
#! exists to help you manage your vector storage costs. You can override 
#! these expiration policies at any time. Learn more here.
#! ------------------------------------------------------------------------

# ========================================================================
# WITH STREAMING 
# ------------------------------------------------------------------------
# Step 5: Create a run and check the output
# Now, create a Run and observe that the model uses the File Search tool to provide a response to the user’s question.
# from typing_extensions import override
# from openai import AssistantEventHandler, OpenAI
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))
# -----------------------------------------------------




def send_question( question: QuestionRequest, client=client):
    thread_id = question.thread_id if question.thread_id else client.beta.threads.create().id
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question.content
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=question.assistant_id
    )
    
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        time.sleep(1)
    
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value
# def send_question(client=client, 
#                   assistant_id=assistant.id, 
#                   role="user", 
#                   content="O que é cefaleia?"):
#     thread = client.beta.threads.create()
#     client.beta.threads.messages.create(
#         thread_id=thread.id,
#         role=role,
#         content=content
#     )
    
#     run = client.beta.threads.runs.create(
#         thread_id=thread.id,
#         assistant_id=assistant_id
#     )
    
#     while run.status != "completed":
#         run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
#         time.sleep(1)
    
#     messages = client.beta.threads.messages.list(thread_id=thread.id)
#     return messages.data[0].content[0].text.value
# #  ------------------------------------------------------------------------
  


if __name__ == "__main__":
    # list_all_assistants_by_metadata(metadata={"user": "zehn_user"})
    # delete_all_assistants(client)
    pass