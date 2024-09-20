class RateExchangeService:
    def __init__(self, repository):
        self.repository = repository

    def ask(self, question: str):
        return self.repository.ask_gemini(question)
