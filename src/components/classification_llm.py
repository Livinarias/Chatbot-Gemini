import logging
from langchain_google_vertexai import ChatVertexAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Services
from src.components.repository.rate_exchange.service import RateExchangeService
from src.components.repository.llm.service import LLMService
from src.components.repository.pinecone_rag.service import PineconeRagService

# Repositories
from src.components.repository.rate_exchange.rate_exchange import RateExchangeRepository
from src.components.repository.llm.llm import LLMRepository
from src.components.repository.pinecone_rag.rag import PiceconeRag

# Configs
from src.config.config import config


class ClassificationLLM:

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

    def classify_topic(self, question: str) -> str:
        """Classify question topic depends posibilities about classification"""
        prompt_classification = (
            f"""
            Clasifica la siguiente pregunta como uno de los siguientes temas:
            - money (si habla sobre TRM o te preguntan sobre una moneda respecto a la otra)
            - rag (si habla sobre EduLearn o temas educativos que no se relacione con moneda)
            - none (si no pertenece a ninguno de estos temas)
            Pregunta: {question}
            una vez clasificada **solo** retornes la palabra de la clasificación:
            Ejemplo:
                - si preguntan ¿Cuánto está el peso colombiano respecto al dólar? retornas money
                - si preguntan por EduLearn o temas relacionados a una plataforma de estudio retornas rag
                - si preguntan por perros retornas none
            """
        )
        classification = self.conversation.predict(input=prompt_classification).strip()
        logging.info("Clasificación: %s",classification)
        if "money" in classification:
            logging.info("ingreso al if money")
            return RateExchangeService(RateExchangeRepository())
        if "rag" in classification:
            logging.info("ingreso al if rag")
            return PineconeRagService(PiceconeRag())
        else:
            logging.info("ingreso al else")
            return LLMService(LLMRepository())