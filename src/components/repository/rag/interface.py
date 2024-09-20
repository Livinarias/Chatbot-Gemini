from abc import ABC, abstractmethod

class IRepository(ABC):
    """Interfaz para la conexión con la base de datos."""
    
    @abstractmethod
    def ask(self, path: str):
        """Interfaz para la query de apartamenteos en la base de datos."""
        raise NotImplementedError
