# 
#
#
#
import os
from astrapy import DataAPIClient
from astrapy.constants import VectorMetric
from astrapy.ids import UUID
from astrapy.exceptions import InsertManyException
from app.core.settings.conf import Settings, logger
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from astrapy.info import CollectionVectorServiceOptions


# ***************************************************************************************
# ÀSTRA DB related environment variables
# -------------------------------------------------------
try:
    ASTRA_DB_APPLICATION_TOKEN = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
    logger.debug(f"::Zeh:: ASTRA_DB_APPLICATION_TOKEN: {ASTRA_DB_APPLICATION_TOKEN}")
except KeyError as e:
    logger.error(f"::Zeh:: Environment variable not found: {e}")
# -------------------------------------------------------
try:
    ASTRA_DB_API_ENDPOINT = os.environ["ASTRA_DB_API_ENDPOINT"]
    logger.debug(f"::Zeh:: ASTRA_DB_API_ENDPOINT: {ASTRA_DB_API_ENDPOINT}")
except KeyError as e:
    logger.error(f"::Zeh:: Environment variable not found: {e}")
    # https://945d988e-8ddd-4f36-91c9-eb0f661c1c9e-us-east-2.apps.astra.datastax.com
# -------------------------------------------------------
try:
    ASTRA_DB_NAMESPACE = os.environ["ASTRA_DB_NAMESPACE"]
    logger.debug(f"::Zeh:: ASTRA_DB_NAMESPACE: {ASTRA_DB_NAMESPACE}")
except KeyError as e:
    logger.error(f"::Zeh:: Environment variable not found: {e}")
# -------------------------------------------------------
try:
    ASTRA_DB_COLLECTION = os.environ["ASTRA_DB_COLLECTION"] = "collection_neurocle_01"
    logger.debug(f"::Zeh:: OPENAI_NEUROCURSO_API_KE: {ASTRA_DB_COLLECTION}")
except KeyError as e:
    logger.error(f"::Zeh:: Environment variable not found: {e}")
# ***************************************************************************************




# ***************************************************************************************
# OpenAI API related environment variables
# -------------------------------------------------------
try:
    OPENAI_NEUROCURSO_API_KEY = os.environ["OPENAI_NEUROCURSO_API_KEY"]
    logger.debug(f"::Zeh:: OPENAI_NEUROCURSO_API_KEY: {OPENAI_NEUROCURSO_API_KEY}")
except KeyError as e:
    logger.error(f"::Zeh:: Environment variable not found: {e}")
# -------------------------------------------------------
try:
    OPENAI_NEUROCURSO_ORGANIZATION_ID = os.environ["OPENAI_NEUROCURSO_ORGANIZATION_ID"]
    logger.debug(f"::Zeh:: OPENAI_NEUROCURSO_ORGANIZATION_ID: {OPENAI_NEUROCURSO_ORGANIZATION_ID}")
except KeyError as e:
    logger.error(f"::Zeh:: Environment variable not found: {e}")
# ***************************************************************************************



# ***************************************************************************************
# Initialize the client
client = DataAPIClient(ASTRA_DB_APPLICATION_TOKEN)
db = client.get_database_by_api_endpoint(
#   "https://945d988e-8ddd-4f36-91c9-eb0f661c1c9e-us-east-2.apps.astra.datastax.com",
    ASTRA_DB_API_ENDPOINT,
    namespace=ASTRA_DB_NAMESPACE,
)
      
print(f"Connected to Astra DB: {db.list_collection_names()}")
logger.info(f"::Zehn:: ::ZEHN:: Connected to Astra DB: {db.list_collection_names()}")


embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
#
openai_vectorize_options = CollectionVectorServiceOptions(
    provider="openai",
    model_name="text-embedding-3-small",
    authentication={
        "providerKey": "OPENAI_API_KEY",
    },
)

vector_store_integrated = AstraDBVectorStore(
    collection_name="collection_neurocle_01",
    api_endpoint=ASTRA_DB_API_ENDPOINT,
    token=ASTRA_DB_APPLICATION_TOKEN,
    namespace=ASTRA_DB_NAMESPACE,
    collection_vector_service_options=openai_vectorize_options,
)


#
#
#
#
#
#
#
#

# ***************************************************************************************
# ***************************************************************************************
from uuid import uuid4
from langchain_core.documents import Document

document_1 = Document(
    page_content="I had chocalate chip pancakes and scrambled eggs for breakfast this morning.",
    metadata={"source": "tweet"},
)

document_2 = Document(
    page_content="The weather forecast for tomorrow is cloudy and overcast, with a high of 62 degrees.",
    metadata={"source": "news"},
)

document_3 = Document(
    page_content="Building an exciting new project with LangChain - come check it out!",
    metadata={"source": "tweet"},
)

document_4 = Document(
    page_content="Robbers broke into the city bank and stole $1 million in cash.",
    metadata={"source": "news"},
)

document_5 = Document(
    page_content="Wow! That was an amazing movie. I can't wait to see it again.",
    metadata={"source": "tweet"},
)

document_6 = Document(
    page_content="Is the new iPhone worth the price? Read this review to find out.",
    metadata={"source": "website"},
)

document_7 = Document(
    page_content="The top 10 soccer players in the world right now.",
    metadata={"source": "website"},
)

document_8 = Document(
    page_content="LangGraph is the best framework for building stateful, agentic applications!",
    metadata={"source": "tweet"},
)

document_9 = Document(
    page_content="The stock market is down 500 points today due to fears of a recession.",
    metadata={"source": "news"},
)

document_10 = Document(
    page_content="I have a bad feeling I am going to get deleted :(",
    metadata={"source": "tweet"},
)

documents = [
    document_1,
    document_2,
    document_3,
    document_4,
    document_5,
    document_6,
    document_7,
    document_8,
    document_9,
    document_10,
]
uuids = [str(uuid4()) for _ in range(len(documents))]

vector_store_integrated.add_documents(documents=documents, ids=uuids)
# ***************************************************************************************
# QUERYING VECTOR STORE
# ***************************************************************************************
results = vector_store_integrated.similarity_search(
    "LangChain provides abstractions to make working with LLMs easy",
    k=10,
    filter={"source": "online"},
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")

results_no_metadata = vector_store_integrated.similarity_search(
    "LangChain provides abstractions to make working with LLMs easy",
    k=10,
    # filter={"source": "tweet"},
)
for res_ in results_no_metadata:
    print(f"* {res_.page_content} [{res_.metadata}]")
    
# -------------------------------------------------------
# Similarity search with score
results = vector_store_integrated.similarity_search_with_score(
    "Will it be hot tomorrow?", k=1, filter={"source": "news"}
)
for res, score in results:
    print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]") 

# Similarity search with score
results_ = vector_store_integrated.similarity_search_with_score(
    "Will it be hot tomorrow?", k=5
)
for res, score in results_:
    print(f"* [SIM={score:3f}] {res.page_content} [{res.metadata}]") 



# -------------------------------------------------------
# Query by turning into retriever
# -------------------------------------------------------
# You can also transform the vector store into a 
# retriever for easier usage in your chains.
#
# Here is how to transform your vector store into a 
# retriever and then invoke the retreiever with a simple 
# query and filter.

retriever = vector_store_integrated.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 1, "score_threshold": 0.5},
)
retriever.invoke("Stealing from the bank is a crime", 
                 filter={"source": "news"})
# -------------------------------------------------------


# -------------------------------------------------------
# Cleanup vector store
# -------------------------------------------------------
# If you want to completely delete the collection 
# from your Astra DB instance, run this.
# (You will lose the data you stored in it.)
vector_store_integrated.delete_collection()
# -------------------------------------------------------




# ***************************************************************************************

from langchain_openai import OpenAIEmbeddings
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS



embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))
vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)
vector_store.add_documents(documents=documents, ids=uuids)




