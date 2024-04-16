import os
from abc import ABC, abstractmethod

from interfaces.vector_database import VectorDatabaseI

class BaseIndexer(ABC):
    def __init__(self, db: VectorDatabaseI) -> None:
        self.db = db

    @staticmethod
    def save_to_disk(path):
        if not os.path.exists(path):
            os.makedirs(path)
        elif os.listdir(path):  # Check if directory is not empty
            print(f"Directory {path} is not empty. Clearing contents...")
            for root, dirs, files in os.walk(path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))