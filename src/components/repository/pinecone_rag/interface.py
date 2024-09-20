from abc import ABC, abstractmethod

class IRepositoryPineconeRag(ABC):
    """Interfaz para la conexión con la base de datos."""
    
    @abstractmethod
    def ask_gemini(self, question: str):
        """Interfaz para la query de apartamenteos en la base de datos."""
        raise NotImplementedError
