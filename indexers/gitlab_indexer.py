from indexers.base_indexer import BaseIndexer
from interfaces.indexer import IndexerI
from git import Repo


class GitlabIndexer(IndexerI):
    def insert_to_db(self, path, repo):
        docs = self.load_and_split_files(path, repo)
        self.db.add_documents(docs)

    def save_to_disk(self, user, token, repo, path):
        BaseIndexer.save_to_disk(path)
        Repo.clone_from(f"https://oauth2:{token}@gitlab.com/{repo}.git", path)
