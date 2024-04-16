from interfaces.database import DatabaseI
from interfaces.vector_database import VectorDatabaseI
from fastapi import Request

import hmac
import hashlib
import os

from loguru import logger

import threading

from services.github_service import GithubService

import json

from fastapi import HTTPException

from langchain.chains import RetrievalQA
from langchain.chains.question_answering import load_qa_chain

from langchain.agents.agent_toolkits.github.toolkit import GitHubToolkit

from interfaces.agent_pool import AgentPool

class SentryHandler:

    def __init__(self, db: DatabaseI, vector_db: VectorDatabaseI, app_id, app_pem):
        self.db = db
        self.vector_db = vector_db
        self.app_id = app_id
        self.app_pem = app_pem

    async def handle_request(self, request: Request, llm):
        
        signature = request.headers.get("Sentry-Hook-Signature", None)
        resource = request.headers.get("Sentry-Hook-Resource", None)

        # Verify signature
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")

        # Handle the payload based on resource or action
        # This is just a basic handling. Expand it according to your needs.
        payload = json.loads(body_str)
      
        if "error" in payload.get('data', {}):
            project_id = payload["data"]["error"]["project"]
        elif "issue" in payload.get('data', {}):
            project_id = int(payload["data"]["issue"]["project"]["id"])
        project_id = int(payload['id'])
        print(project_id)
        
        response = self.db.fetch_repo_info_with_alert_service_id("github_app_data", "sentry_project_id", project_id)

     

        client_secret = "https://78d72e47912aa5714715a62ac448a3e8@o4507090108284928.ingest.us.sentry.io/4507090758008832"
        repo_name = "Naim08/IncidentDemo1"
        base_branch = "main"

        digest = hmac.new(
            key=client_secret.encode('utf-8'),
            msg=body_str.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).hexdigest()
        # if not signature:  # The signature is missing
        #     raise HTTPException(status_code=401, detail="Unauthorized: Missing signature")

        # if not hmac.compare_digest(digest, signature):
        #     raise HTTPException(status_code=401, detail="Unauthorized: Invalid signature")
        
       
        action = payload.get("action", None)
        actor = payload.get("actor", None)
        data = payload

        action = "created"
        if action == "created":
            
            if "error" in data:
                error = data["error"]
                # print(issue["title"])
                error_str = error["exception"]["values"][0]["value"]
            elif "issue" in data:
                error_str = json.dumps(data["issue"]["metadata"])
            
  
            error_str = data["event"]["exception"]["values"][0]["value"]

            query = f"Pretend you're a senior site reliability engineer. Given this alert `{error_str}`, what in my code could be causing this error and how do I fix it? You MUST format your answer by file name and line and the code snippet/s, and code to resolve the issue. If you get an invalid literal, just take only the issue number and continue."

            qa_chain = load_qa_chain(llm, chain_type="stuff")
            qa = RetrievalQA(combine_documents_chain=qa_chain,
                            retriever=self.vector_db.filter_by_repo(repo_name))
            response = qa.run(query)

            docs = self.vector_db.search(response)


            filename = ""

            if len(docs) > 0:
                filename = docs[0].metadata["rpath"]

            issue_number = None

            github_service1 = GithubService(self.app_id, self.app_pem, repo_name, "main", base_branch)
            issue_number = github_service1.create_issue("Issue from Sentry", response)
            github_service1.create_branch(base_branch, f"resolvd/issue-{issue_number}")
            
            github_service2 = GithubService(self.app_id, self.app_pem, repo_name, f"resolvd/issue-{issue_number}", base_branch)
            toolkit = GitHubToolkit.from_github_api_wrapper(github_service2.git)


            if issue_number is not None:
                agent_pool = AgentPool.instance()
                agent = agent_pool.get_agent(repo_name, toolkit, llm)
                threading.Thread(target=agent.execute, args=(issue_number, filename)).start()

                # Simple print to check data
                print(f"Received {resource} with action {action} by actor {actor}")

                return {"status": "received"}