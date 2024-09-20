import logging
import torch
import asyncio
from typing import List
from pinecone import Pinecone
from langchain_google_vertexai import ChatVertexAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from sentence_transformers import SentenceTransformer

# Interfaces
from src.components.repository.pinecone_rag.interface import IRepositoryPineconeRag

# Configs
from src.config.config import config

# Constants
from src.constants.constants import titles, example_rag


class PiceconeRag(IRepositoryPineconeRag):
    def __init__(self):
        self.model = ChatVertexAI(
            temperature=config.get("TEMPERATURE", 0),
            model_name=config.get("GEMINI_MODEL", ""),
            max_output_tokens=config.get("MAX_OUTPUT_TOKENS", 0),
            project_id=config.get("GOOGLE_PROJECT_ID", ""),
        )
        self.pc = Pinecone(api_key=config.get("PINECONE_API_KEY"))
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.model,
            memory=self.memory,
            verbose=False
        )

    def ask_gemini(self, question: str) -> str:
        """Ask gemini about information in Pinecone"""
        source = self.classify_source(question)
        logging.info("source: %s", source[source.find('**') + 2: source.rfind('**')])
        rag_response = self.call_pinecone_rag(
            question,
            source[source.find('**') + 2: source.rfind('**')]
        )
        logging.info("rag_response: %s",rag_response)
        prompt = (
            f"""
            Evalua la siguiente lista de respuestas: {rag_response},
            partiendo de la lista organiza la informacion para brindar
            un mensaje claro.

            una vez tengas organizada la informacion, brinda una frase coherente
            no inventes información, basate en la lista
            Ejemplo:
            si te llega la siguiente lista {example_rag}
            la respuesta seria:
            Si olvidaste tu contraseña, puedes restablecerla así:
                Vea la página de inicio de sesión
                Haz clic en "¿Olvidaste tu contraseña?"
                Ingresa el correo electrónico asociado a tu cuenta
                Recibirás un correo con instrucciones para crear una nueva contraseña
                Sigue las instrucciones del correo para establecer tu nueva contraseña 
            """
        )
        return self.conversation.predict(input=prompt)

    def classify_source(self, question: str) -> str:
        """Clasify question's source depends Pinecone metadata"""
        titles_rag = list(titles.keys())
        logging.info("titles_rag: %s",titles_rag)
        prompt_classification = (
            f"""
            Clasifica la siguiente pregunta: {question}
            en los siguientes títulos:{titles_rag}
            una vez clasificada **solo** retornes el titulo que le corresponde
            se consiso con la respuesta
            Ejemplo:
                - si preguntan: ¿Cómo puedo crear una cuenta en EduLearn? retornas crear cuenta
                - si preguntan: He olvidado mi contraseña, ¿cómo puedo restablecerla? retornas olvido contraseña
                - si preguntan ¿Es posible tener múltiples cuentas con el mismo correo electrónico? retornas multiples correos
            """
        )
        result = self.conversation.predict(
            input=prompt_classification).strip()
        logging.info("result: %s", result)
        return result

    def call_pinecone_rag(self, question: str, source: str) -> List[str]:
        """Call Pinecone RAG to find answers questiuons"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        index = self.pc.Index(config.get("INDEX_NAME_PINECONE"))
        model = SentenceTransformer(config.get(
            "MODEL_TRANSFORM")).to(self.device)
        query_embedding = model.encode(question).tolist()
        results = index.query(
            vector=query_embedding,
            top_k=100,
            include_values=False,
            include_metadata=True,
            filter={
                "source": {"$eq": f"{source}"}
            }
        )
        return [x["metadata"]["text"] for x in results["matches"]]
