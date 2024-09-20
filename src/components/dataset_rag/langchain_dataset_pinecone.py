"""Organice data and upload data to Pinecone"""
import os
from uuid import uuid4
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from proccess_file import send_data_to_rag

# Configs
from src.config.config import config


def upload_data_to_rag():
    """
    Uploads the data from the PDF file to RAG and creates a Pinecone vector store.
    """
    index = create_index()

    documents, uuids = transform_dataset()

    embeddings = HuggingFaceEmbeddings(
        model_name=config.get("MODEL_TRANSFORM"),
        model_kwargs = {'device': 'cpu'},
        encode_kwargs = {'normalize_embeddings': False}
    )
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)
    vector_store.add_documents(documents=documents, ids=uuids)
    vector_store.delete(ids=[uuids[-1]])

def create_index():
    """Create index to pinecone vector store"""
    pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
    # Create Index
    index_name = config.get("INDEX_NAME_PINECONE")
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if index_name not in existing_indexes:
        print(f"Index {index_name} does not exist. Creating...")
        pc.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
    return pc.Index(index_name)

def find_dataset():
    """find path to pdf dataset"""
    script_path = os.path.abspath(__file__)
    project_path = os.path.dirname(script_path)
    return os.path.join(project_path, 'dataset_eduLearn.pdf')

def transform_dataset():
    """Reorganice info depend requirements to pinecone and langchain"""
    pdf_path = find_dataset()
    sentences = [(x["id"], x["text"]) for x in send_data_to_rag(pdf_path)]
    documents = [
        Document(page_content=data, metadata={"source": sentence[0]})
        for sentence in sentences
        for data in sentence[1]
    ]
    uuids = [str(uuid4()) for _ in range(len(documents))]
    return documents, uuids