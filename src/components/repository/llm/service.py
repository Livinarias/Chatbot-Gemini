class LLMService:
    """LLM service class"""

    def __init__(self, repository):
        self.repository = repository

    def ask(self, question: str) -> str:
        return self.repository.ask_llm(question)
