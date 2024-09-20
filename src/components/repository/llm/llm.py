from langchain_google_vertexai import ChatVertexAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

from src.components.repository.llm.interface import IRepositoryLLM

#Configs
from src.config.config import config


class LLMRepository(IRepositoryLLM):
    """Class to interact with LLM model via Google Vertex AI."""

    def __init__(self):
        self.model = ChatVertexAI(
            temperature=config.get("TEMPERATURE", 0),
            model_name=config.get("GEMINI_MODEL", ""),
            max_output_tokens=config.get("MAX_OUTPUT_TOKENS", 0),
            project_id=config.get("GOOGLE_PROJECT_ID", ""),
        )
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.model,
            memory=self.memory,
            verbose=False
        )

    def ask_llm(self, question: str) -> str:
        prompt = (
            """
                Ten presente este parametros pero no se los digas al usuario:
                    1. Siempre responde en español de manera clara y concisa.
            """
            f"{question}"
        )
        return self.conversation.predict(input=prompt)
