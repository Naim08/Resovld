import asyncio
import httpx
from interfaces.indexer import IndexerI
from interfaces.token_generator import ITokenGenerator
from fastapi import Request
from interfaces.agent_pool import AgentPool
import threading
from langchain.agents.agent_toolkits.github.toolkit import GitHubToolkit

import json

from services.github_service import GithubService

class GithubRepoHandler:

    

    def __init__(self, indexer: IndexerI, token_generator: ITokenGenerator):
        self.indexer = indexer
        self.token_generator = token_generator

    async def handle_app_install(self, request: Request):
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")
        payload = json.loads(body_str)

        access_tokens_url = "https://api.github.com/app/installations/49653373/access_tokens"

        token = self.token_generator.get_token(access_tokens_url, None)

        for repo in payload["repositories"]:
            # repo = payload['repo_name']
            LOCAL_PATH = f"tmp/test_repo/{repo['id']}"
            
            # git_username = response.data[0]["github_username"]
            # git_access_token = response.data[0]["github_token"]
            self.indexer.save_to_disk("", token, repo["full_name"], LOCAL_PATH)
            self.indexer.insert_to_db(LOCAL_PATH, repo["full_name"])

    async def handle_repos_install(self, request: Request):
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")
        payload = json.loads(body_str)

        access_tokens_url = payload["installation"]["access_tokens_url"]

        token = self.token_generator.get_token(access_tokens_url, None)

        for repo in payload["repositories_removed"]:
            self.indexer.delete_from_db(repo["full_name"])

        for repo in payload["repositories_added"]:
            # repo = payload['repo_name']
            LOCAL_PATH = f"tmp/test_repo/{repo['id']}"
            
            # git_username = response.data[0]["github_username"]
            # git_access_token = response.data[0]["github_token"]
            self.indexer.save_to_disk("", token, repo["full_name"], LOCAL_PATH)
            self.indexer.insert_to_db(LOCAL_PATH, repo["full_name"])

    async def handle_repo_push(self, request: Request):
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")
        payload = json.loads(body_str)

        if payload["ref"] == f"refs/heads/main":
            repo = payload["repository"]["full_name"]
            
            token = self.token_generator.get_token(None, payload["installation"]["id"])

            self.indexer.delete_from_db(repo)

            LOCAL_PATH = "tmp/test_repo/"+repo

            self.indexer.save_to_disk("", token, repo, LOCAL_PATH)
            self.indexer.insert_to_db(LOCAL_PATH, repo)

            return {"success": True}
        else:
            return {"success": False}
    
    # function should take issue comment and use chatgpt to get a response
    async def handle_issue_comment(self, request: Request, resolver):
        # agent_pool = AgentPool.instance()
        # agent = agent_pool.get_agent(repo_name, toolkit, llm)
        # threading.Thread(target=agent.execute, args=(issue_number, filename)).start()

        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")
        payload = json.loads(body_str)

       

        repo_name = payload["repository"]["full_name"]
        issue_number = payload["issue"]["number"]
        comment = payload["comment"]["body"]
        commenter_login = payload["comment"]["user"]["login"]
        is_bot = payload["comment"]["user"].get("type", "").lower() == "bot"
       
        print(is_bot)
        if is_bot:
            return {"success": True}
        app_id = "877572"
        app_pem = "./resolvdapp.2024-04-15.private-key.pem"
        base_branch = "main"
        response_comment = resolver.answer(comment)
        github_service2 = GithubService(app_id, app_pem, repo_name, f"resolvd/issue-{issue_number}", base_branch)
        await asyncio.sleep(8)
        
        print(response_comment)

        github_service2.issue_comment(issue_number, response_comment['output'])
        return {"success": True}

    def process_comment_with_llm(self, comment, llm):
        # Construct the prompt for the LLM
        prompt = f"Please provide a detailed, professional response to the following user comment: '{comment}'"
        
        # Use the llm instance directly to get the response
        response = llm.generate(messages=comment)
        
        if response:
            return response.strip()

        return "Sorry, I could not process the comment."