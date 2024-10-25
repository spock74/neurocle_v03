# _Ouline_ of OpenAI `assistants API` as on line in 15 may 2024

> Copied 'n pasted by Zehn Moraes from [Assistants API - V2](https://platform.openai.com/docs/assistants/tools/file-search?context=without-streaming)

*ALWAYS* see [changelog](https://platform.openai.com/docs/changelog) (Its beta version, yo)




```python
from openai import OpenAI 
client = OpenAI()



#  Step 1: Create a new Assistant with File Search Enabled
# Create a new assistant with file_search enabled in the tools parameter of the Assistant.
# ------------------------------------------------------------------------
assistant = client.beta.assistants.create(
  name="Financial Analyst Assistant",
  instructions="You are an expert financial analyst. Use you knowledge base to answer questions about audited financial statements.",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
)
# Once the file_search tool is enabled, the model decides when to retrieve content based on user messages.
# ------------------------------------------------------------------------



# Step 2: Upload files and add them to a Vector Store
# To access your files, the file_search tool uses the Vector Store object. Upload your files and create a Vector Store to contain them. Once the Vector Store is created, you should poll its status until all files are out of the in_progress state to ensure that all content has finished processing. The SDK provides helpers to uploading and polling in one shot.
# ------------------------------------------------------------------------
# Create a vector store caled "Financial Statements"
vector_store = client.beta.vector_stores.create(name="Financial Statements")
 
# Ready the files for upload to OpenAI
file_paths = ["edgar/goog-10k.pdf", "edgar/brka-10k.txt"]
file_streams = [open(path, "rb") for path in file_paths]
 
# Use the upload and poll SDK helper to upload the files, add them to the vector store,
# and poll the status of the file batch for completion.
file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
  vector_store_id=vector_store.id, files=file_streams
)
 
# You can print the status and the file counts of the batch to see the result of this operation.
print(file_batch.status)
print(file_batch.file_counts)
# ------------------------------------------------------------------------




# Step 3: Update the assistant to to use the new Vector Store
# To make the files accessible to your assistant, update the assistant’s tool_resources with the new vector_store id.
# ------------------------------------------------------------------------
assistant = client.beta.assistants.update(
  assistant_id=assistant.id,
  tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)
# ------------------------------------------------------------------------





# Step 4: Create a thread
# You can also attach files as Message attachments on your thread. 
# Doing so will create another vector_store associated with the 
# thread, or, if there is already a vector store attached to this 
# thread, attach the new files to the existing thread vector store. 
# When you create a Run on this thread, the file search tool will query 
# both the vector_store from your assistant and the vector_store 
# on the thread.
# ------------------------------------------------------------------------
# In this example, the user attached a copy of Apple’s latest 10-K filing.
# ------------------------------------------------------------------------
# Upload the user provided file to OpenAI
message_file = client.files.create(
  file=open("edgar/aapl-10k.pdf", "rb"), purpose="assistants"
)
 
# Create a thread and attach the file to the message
thread = client.beta.threads.create(
  messages=[
    {
      "role": "user",
      "content": "How many shares of AAPL were outstanding at the end of of October 2023?",
      # Attach the new file to the message.
      "attachments": [
        { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
      ],
    }
  ]
)
# The thread now has a vector store with that file in its tool resources.
print(thread.tool_resources.file_search)

# Vector stores created using message attachements have a default expiration policy of 7 days after they were last active (defined as the last time the vector store was part of a run). This default exists to help you manage your vector storage costs. You can override these expiration policies at any time. Learn more here.
# ------------------------------------------------------------------------





# ------------------------------------------------------------------------
# ***************************  streaming *********************************
# ------------------------------------------------------------------------
# Step 5: Create a run and check the output
# Now, create a Run and observe that the model uses the File Search tool to provide a response to the user’s question.
# from typing_extensions import override
# from openai import AssistantEventHandler, OpenAI
# ------------------------------------------------------------------------
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

# Then, we use the stream SDK helper
# with the EventHandler class to create the Run
# and stream the response.

with client.beta.threads.runs.stream(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Jane Doe. The user has a premium account.",
    event_handler=EventHandler(),
) as stream:
    stream.until_done()
# ------------------------------------------------------------------------
    
    
    
    
    
# ------------------------------------------------------------------------
# ************************** NO STREAMING ********************************
# ------------------------------------------------------------------------
# Use the create and poll SDK helper to create a run and poll the status of
# the run until it's in a terminal state.


run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id, assistant_id=assistant.id
)

messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

message_content = messages[0].content[0].text
annotations = message_content.annotations
citations = []
for index, annotation in enumerate(annotations):
    message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
    if file_citation := getattr(annotation, "file_citation", None):
        cited_file = client.files.retrieve(file_citation.file_id)
        citations.append(f"[{index}] {cited_file.filename}")

print(message_content.value)
print("\n".join(citations))

# Your new assistant will query both attached vector stores 
# (one containing goog-10k.pdf and brka-10k.txt, and the other containing 
# aapl-10k.pdf) and return this result from aapl-10k.pdf.
# ------------------------------------------------------------------------




# ------------------------------------------------------------------------
# How it works
# ------------------------------------------------------------------------

# The file_search tool implements several retrieval best practices out 
# of the box to help you extract the right data from your files and 
# augment the model’s responses. The file_search tool:

    # 1. Rewrites user queries to optimize them for search.
    # 2. Breaks down complex user queries into multiple searches it can 
    # run in parallel.
    # 3. Runs both keyword and semantic searches across both assistant and 
    # thread vector stores.
    # 4. Reranks search results to pick the most relevant ones before 
    # generating the final response.

# By default, the file_search tool uses the following settings:

    # 1. Chunk size: 800 tokens
    # 2. Chunk overlap: 400 tokens
    # 3. Embedding model: text-embedding-3-large at 256 dimensions
    # 4. Maximum number of chunks added to context: 20 (could be fewer)




# Known Limitations

    # We have a few known limitations we're working on adding support for in the coming months:

    # 1. Support for modifying chunking, embedding, and other retrieval configurations.
    # 2. Support for deterministic pre-search filtering using custom metadata.
    # 3. Support for parsing images within documents (including images of charts, graphs, tables etc.)
    # 4. Support for retrievals over structured file formats (like csv or jsonl).
    # 5. Better support for summarization — the tool today is optimized for search queries.

# Vector stores

# Vector Store objects give the File Search tool the ability to search your files. Adding a file to a vector_store automatically parses, chunks, embeds and stores the file in a vector database that's capable of both keyword and semantic search. Each vector_store can hold up to 10,000 files. Vector stores can be attached to both Assistants and Threads. Today, you can attach at most one vector store to an assistant and at most one vector store to a thread.

# Creating vector stores and adding files
# You can create a vector store and add files to it in a single API call:
# ------------------------------------------------------------------------
# Creating vector stores and adding files
# You can create a vector store and add files to it in a single API call:
vector_store = client.beta.vector_stores.create(
  name="Product Documentation",
  file_ids=['file_1', 'file_2', 'file_3', 'file_4', 'file_5']
)
# ------------------------------------------------------------------------






# ------------------------------------------------------------------------
#Adding files to vector stores is an async operation. To ensure the operation is complete, we recommend that you use the 'create and poll' helpers in our official SDKs. If you're not using the SDKs, you can retrieve the vector_store object and monitor it's file_counts property to see the result of the file ingestion operation.
#
#Files can also be added to a vector store after it's created by creating vector store files.
# ------------------------------------------------------------------------
file = client.beta.vector_stores.files.create_and_poll(
  vector_store_id="vs_abc123",
  file_id="file-abc123"

)
# ------------------------------------------------------------------------






# ------------------------------------------------------------------------
# Alternatively, you can add several files to a vector store by creating batches of up to 500 files.
# ------------------------------------------------------------------------
batch = client.beta.vector_stores.file_batches.create_and_poll(
  vector_store_id="vs_abc123",
  file_ids=['file_1', 'file_2', 'file_3', 'file_4', 'file_5']
)
# ------------------------------------------------------------------------




# ------------------------------------------------------------------------
# Similarly, these files can be removed from a vector store by either:
# ------------------------------------------------------------------------
    #   -- Deleting the vector store file object or,
    #   -- By deleting the underlying file object (which removes the file it from all vector_store and code_interpreter configurations across all assistants and threads in your organization)
# The maximum file size is 512 MB. Each file should contain no more than 5,000,000 tokens per file (computed automatically when you attach a file).

# File Search supports a variety of file formats including .pdf, .md, and .docx. More details on the file extensions (and their corresponding MIME-types) supported can be found in the Supported files section below.



# ------------------------------------------------------------------------
# Attaching vector stores
# You can attach vector stores to your Assistant or Thread using the 
#   tool_resources parameter.
# ------------------------------------------------------------------------
assistant = client.beta.assistants.create(
  instructions="You are a helpful product support assistant and you answer questions based on the files provided to you.",
  model="gpt-4o",
  tools=[{"type": "file_search"}],
  tool_resources={
    "file_search": {
      "vector_store_ids": ["vs_1"]
    }
  }
)

thread = client.beta.threads.create(
  messages=[ { "role": "user", "content": "How do I cancel my subscription?"} ],
  tool_resources={
    "file_search": {
      "vector_store_ids": ["vs_2"]
    }
  }
)
# ------------------------------------------------------------------------





# ************************************************************************
# ***************** KINDA GENERAL EXPLANATION ****************************
# ************************************************************************
# ------------------------------------------------------------------------
# You can also attach a vector store to Threads or Assistants after 
# they're created by updating them with the right tool_resources.
# ------------------------------------------------------------------------
# Ensuring vector store readiness before creating runs
# We highly recommend that you ensure all files in a vector_store are fully
# processed before you create a run. This will ensure that all the data in 
# your vector_store is searchable. You can check for vector_store readiness 
# by using the polling helpers in our SDKs, or by manually polling the 
# vector_store object to ensure the status is completed.

# As a fallback, we've built a 60 second maximum wait in the Run object 
# when the thread’s vector store contains files that are still being 
# processed. This is to ensure that any files your users upload in a thread 
# a fully searchable before the run proceeds. This fallback wait does not 
# apply to the assistant's vector store.
# ************************************************************************




# ------------------------------------------------------------------------
# Managing costs with expiration policies
# ------------------------------------------------------------------------
# The file_search tool uses the vector_stores object as its resource and 
# you will be billed based on the size of the vector_store objects created. 
# The size of the vector store object is the sum of all the parsed chunks 
# from your files and their corresponding embeddings.

# You first GB is free and beyond that, usage is billed at $0.10/GB/day of 
# vector storage. There are no other costs associated with vector store 
# operations.

# In order to help you manage the costs associated with these vector_store 
# objects, we have added support for expiration policies in the 
# vector_store object. You can set these policies when creating or 
# updating the vector_store object.
# ------------------------------------------------------------------------
vector_store = client.beta.vector_stores.create_and_poll(
  name="Product Documentation",
  file_ids=['file_1', 'file_2', 'file_3', 'file_4', 'file_5'],
  expires_after={
	  "anchor": "last_active_at",
	  "days": 7
  }
)
# ------------------------------------------------------------------------





# ------------------------------------------------------------------------
# ****** THREAD VECTOR STORES HAVE DEFAULT EXPIRATION POLICIES ***********
# ------------------------------------------------------------------------
# Vector stores created using thread helpers (like tool_resources.file_search.vector_stores in Threads or message.attachments in Messages) have a default expiration policy of 7 days after they were last active (defined as the last time the vector store was part of a run).

# When a vector store expires, runs on that thread will fail. To fix this, you can simply recreate a new vector_store with the same files and reattach it to the thread.

all_files = list(client.beta.vector_stores.files.list("vs_expired"))

vector_store = client.beta.vector_stores.create(name="rag-store")
client.beta.threads.update(
    "thread_abc123",
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
)

for file_batch in chunked(all_files, 100):
    client.beta.vector_stores.file_batches.create_and_poll(
        vector_store_id=vector_store.id, file_ids=[file.id for file in file_batch]
    )
# ------------------------------------------------------------------------

    
    
    
# ------------------------------------------------------------------------    
# ------------------------------------------------------------------------    
# Supported files
# For text/ MIME types, the encoding must be one of utf-8, utf-16, or ascii.
# ------------------------------------------------------------------------    
#
# ------------------------------------------------------------------------    
# FILE FORMAT	MIME TYPE
# ------------------------------------------------------------------------    
# .c	text/x-c
# .cs	text/x-csharp
# .cpp	text/x-c++
# .doc	application/msword
# .docx	application/vnd.openxmlformats-officedocument.wordprocessingml.document
# .html	text/html
# .java	text/x-java
# .json	application/json
# .md	text/markdown
# .pdf	application/pdf
# .php	text/x-php
# .pptx	application/vnd.openxmlformats-officedocument.presentationml.presentation
# .py	text/x
# .py	text/x-script
# .rb	text/x-ruby
# .tex	text/x-tex
# .txt	text/plain
# .css	text/css
# .js	text/javascript
# .sh	application/x-sh
# .ts	application/typescript
# ------------------------------------------------------------------------
```