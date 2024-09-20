
import logging
import json
from datetime import datetime
from pytz import timezone

from langchain_google_vertexai import ChatVertexAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Interfaces
from src.components.repository.rate_exchange.interface import IRepository

# Configs
from src.config.config import config

# Utils
from src.utils.utils_rate_exhange import get_code_by_country, get_trm

# Constants
from src.constants.constants import example, response


class RateExchangeRepository(IRepository):
    """Class to interact with LLM model via Google Vertex AI."""

    def __init__(self):
        self.model = ChatVertexAI(
            temperature=config.get("TEMPERATURE", 0),
            model_name=config.get("GEMINI_MODEL", ""),
            max_output_tokens=config.get("MAX_OUTPUT_TOKENS", 0),
            project_id=config.get("GOOGLE_PROJECT_ID", ""),
        )
        self.url = config.get("RATE_EXCHANGE_API", "")
        self.api_key = config.get("RATE_EXCHANGE_API_KEY", "")
        self.memory = ConversationBufferMemory()
        self.conversation = ConversationChain(
            llm=self.model,
            memory=self.memory,
            verbose=False
        )
        self.date = datetime.now(
            timezone(config.get("TIMEZONE", "America/Bogota")))

    def find_countries(self, question: str) -> str:
        """Find countries depend constant that show possibilities"""
        prompt_template = (
            f"""
            Cuando un usuario te haga preguntas relacionadas con tasas de cambio entre dos monedas
            debes encontrar los países involucrados y responder en el siguiente formato:
            {response}
            Por ejemplo:
            Entrada del usuario: "¿Cuánto está el peso colombiano respecto al dólar?"
            Respondes así: {example}
            Pregunta: {question}
            """
        )
        return self.conversation.predict(input=prompt_template).strip()

    def find_currency_codes(self, predict: str) -> str:
        """Find currency codes depend constant"""
        logging.info("esta es la prediccion: %s",predict)
        currency_dict = json.loads(
            predict[
                predict.find('{'):(predict.find('}')+1)
            ].replace("'", '"')
        )
        logging.info("currency_dict: %s",currency_dict)
        country_from_code = get_code_by_country(
            currency_dict["country_from"]
        )
        country_to_code = get_code_by_country(
            currency_dict["country_to"]
        )
        return get_trm(
            f'{config.get("RATE_EXCHANGE_API")}/{config.get("RATE_EXCHANGE_API_KEY")}/pair/{country_from_code}/{country_to_code}'
        )

    def ask_gemini(self, question: str):
        """Ask gemini depends api trm"""
        countries_prediction = self.find_countries(question)
        trm = self.find_currency_codes(countries_prediction)
        prompt = (
            f"""
            Evalua la siguiente pregunta: {question},
            partiendo de la pregunta contesta de manera consisa,
            basandote en {trm["conversion_rate"]}.
            Importante:
                - **Siempre** contesta con coherencia.
                - Dando detalles como si fueras un experto.
                - Recuerda que hoy es {self.date}
                - si te llega una estructura: {example},**no lo muestres**
            """
        )
        return self.conversation.predict(input=prompt)
