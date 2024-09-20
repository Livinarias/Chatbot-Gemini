from abc import ABC, abstractmethod

class IRepository(ABC):
    """Interfaz para la conexión con la base de datos."""
    
    @abstractmethod
    def ask_gemini(self, question: str) -> None:
        """Interfaz para la query de apartamenteos en la base de datos."""
        raise NotImplementedError
