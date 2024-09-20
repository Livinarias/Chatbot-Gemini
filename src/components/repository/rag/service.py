class RAGService:
    def __init__(self, repository):
        self.repository = repository

    def get_data(self, path: str):
        return self.repository.query(path)

    def close(self):
        self.repository.close()