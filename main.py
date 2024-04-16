import os

from fastapi import FastAPI, Request, Depends
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

from interfaces.document_loader import DocumentLoader
from indexers.github_indexer import GithubIndexer
from github_token_generator import GitHubTokenGenerator
from indexers.github_repo_handler import GithubRepoHandler
from databases.pinecone_db import PineconeDatabase
from databases.supabase_db import Supabase
from interfaces.sentry_handler import SentryHandler
from interfaces.incident_resolver import IncidentResolver
from dotenv import load_dotenv

from loguru import logger
from posthog import Posthog
from langchain_community.document_loaders.csv_loader import CSVLoader

app = FastAPI()

load_dotenv()



APP_ID = "877572"
APP_PEM = "./resolvdapp.2024-04-15.private-key.pem"

incident_csv = "./Unique_Incident_Logs.csv"
db_url: str = os.environ.get("SUPABASE_URL")
db_key: str = os.environ.get("SUPABASE_KEY")
supabase = Supabase(db_key, db_url)

vectordb = PineconeDatabase(os.getenv('PINECONE_API_KEY'), "us-west4-gcp-free")

embedder = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'), model_name="gpt-4")
# Figure out the index name storage and the embeddar.
# What happened if we want to use different embeddars in the future?
vectordb.from_existing_index('git-code', embedder)

document_loader = DocumentLoader()
csv_doc = CSVLoader(incident_csv)
load_csv = csv_doc.load()
# Inject database instance to the GithubIndexer
github_indexer = GithubIndexer(vectordb, document_loader)
github_token_generator = GitHubTokenGenerator(APP_ID, APP_PEM)

github_repo_handler = GithubRepoHandler(github_indexer, github_token_generator)
sentry_handler = SentryHandler(supabase, vectordb, APP_ID, APP_PEM)
resolver = IncidentResolver(llm, embedder, load_csv)

posthog = Posthog(project_api_key='phc_akGTYuud5Tk78tfAq504PXYGxU5PoO1PfrmBFtagFLf', host='https://app.posthog.com')

def log_to_posthog(message):
    posthog.capture("placeholder", message)

logger.add(log_to_posthog)

@app.post("/github")
async def handle_github_event(request: Request):
    event = request.headers.get("X-GitHub-Event", None)
    logger.info(event)
    if event == "installation":  # Index all installed repos
        await github_repo_handler.handle_app_install(request)
    elif event == "installation_repositories":  # Index all installed repos
        await github_repo_handler.handle_repos_install(request)
    elif event == "push":  # Reindex updated repos
        await github_repo_handler.handle_repo_push(request)
    elif event == "issue_comment":
        await github_repo_handler.handle_issue_comment(request, resolver)


@app.get("/health")
async def test(request: Request):
    logger.info("thisis a test")
    return {"health": "healthy"}


@app.post("/sentry")
async def handle_sentry_event(request: Request):
    await sentry_handler.handle_request(request, llm)

 