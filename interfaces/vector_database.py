from abc import ABC, abstractmethod


class VectorDatabaseI(ABC):

    @abstractmethod
    def add_documents(self, documents):
        pass

    @abstractmethod
    def search(self, query):
        pass

    @abstractmethod
    def delete(self, repo_name):
        pass

    @abstractmethod
    def filter_by_repo(self, repo_name):
        pass
