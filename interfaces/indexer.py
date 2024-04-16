from abc import ABC, abstractmethod
import os


class IndexerI(ABC):

    @abstractmethod
    def save_to_disk(self, user, token, repo, path):
        pass

    @abstractmethod
    def insert_to_db(self, path, repo):
        pass

    @abstractmethod
    def delete_from_db(self, repo):
        pass