from langchain.vectorstores import Pinecone
import pinecone

from interfaces.vector_database import VectorDatabaseI


class PineconeDatabase(VectorDatabaseI):

    def __init__(self, api_key, environment):
        pinecone.init(api_key=api_key, environment=environment)

    def add_documents(self, documents):
        # Assuming Pinecone has a batch add method or similar
        self.db.add_documents(documents)

    def search(self, query):
        return self.db.similarity_search(query)

    def delete(self, repo_name):
        self.db.delete(filter={"repo": repo_name})

    # Assuming you also want a method to create a Pinecone instance from an existing index
    def from_existing_index(self, index_name, embedder):
        self.db = Pinecone.from_existing_index(index_name, embedder)

    def filter_by_repo(self, repo_name):
        return self.db.as_retriever(search_kwargs={"filter": {"repo": repo_name}})
