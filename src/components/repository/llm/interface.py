from abc import ABC, abstractmethod

class IRepositoryLLM(ABC):
    """Interfaz para la conexión al LLM."""
    
    @abstractmethod
    def ask_llm(self, question: str) -> None:
        """Interfaz para la query de apartamenteos en la base de datos."""
        raise NotImplementedError
