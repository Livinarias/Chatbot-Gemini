"""Upload data without langchain, directly from Pinecone"""
import os
import torch
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from src.utils.proccess_file import send_data_to_rag

# Configs
from src.config.config import config


def upload_data_to_rag():
    script_path = os.path.abspath(__file__)
    project_path = os.path.dirname(script_path)
    pdf_path = os.path.join(project_path, 'dataset_eduLearn.pdf')

    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    model = SentenceTransformer(
        config.get("MODEL_TRANSFORM")).to(device)

    sentences = [x["text"] for x in send_data_to_rag(pdf_path)]
    embeddings = model.encode(sentences)

    vectors = []
    for i, (d, e) in enumerate(zip(send_data_to_rag(pdf_path), embeddings)):
        vectors.append({
            "id": f"vec{i}",
            "values": e,
            "metadata": {'text': d['text']}
        })

    index = create_index()

    index.upsert(
        vectors=vectors,
        namespace=config.get("NAMESPACE_RAG")
    )

def create_index():
    pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))

    # Create Index
    index_name = config.get("INDEX_NAME_PINECONE")
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