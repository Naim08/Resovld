from interfaces.document_loader import DocumentLoader
from indexers.base_indexer import BaseIndexer
from interfaces.vector_database import VectorDatabaseI
from interfaces.indexer import IndexerI
from git import Repo


class GithubIndexer(IndexerI):
    def __init__(self, database: VectorDatabaseI, document_loader: DocumentLoader):
        self.database = database
        self.document_loader = document_loader

    def save_to_disk(self, user, token, repo, path):
        BaseIndexer.save_to_disk(path)
        Repo.clone_from(f"https://x-access-token:{token}@github.com/{repo}.git", path)

    def insert_to_db(self, path, repo):
        docs = self.document_loader.load_and_split_files(path, repo)
        self.database.add_documents(docs)
    
    def delete_from_db(self, repo):
        self.database.delete(repo)
