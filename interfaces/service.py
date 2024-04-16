from abc import ABC, abstractmethod
import os


class GitService(ABC):

    @abstractmethod
    def create_branch(self, base_branch_name: str, new_branch_name: str):
        pass

    @abstractmethod
    def create_issue(self, title, body):
        pass