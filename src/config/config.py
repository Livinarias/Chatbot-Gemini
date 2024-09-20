import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "GEMINI_MODEL": os.getenv("GEMINI_MODEL"),
    "GOOGLE_PROJECT_ID": os.getenv("GOOGLE_PROJECT_ID"),
    "MAX_OUTPUT_TOKENS": os.getenv("MAX_OUTPUT_TOKENS"),
    "TEMPERATURE": os.getenv("TEMPERATURE"),
    "RATE_EXCHANGE_API_KEY": os.getenv("RATE_EXCHANGE_API_KEY"),
    "RATE_EXCHANGE_API": os.getenv("RATE_EXCHANGE_API"),
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "INDEX_NAME_PINECONE": os.getenv("INDEX_NAME_PINECONE"),
    "MODEL_TRANSFORM": os.getenv("MODEL_TRANSFORM"),
    "NAMESPACE_RAG": os.getenv("NAMESPACE_RAG"),
}
