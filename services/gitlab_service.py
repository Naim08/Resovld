import os

import requests

from interfaces.service import GitService


class GitlabService(GitService):

    def init(self, toolkit: any, repo_instance: object):
        self.toolkit = toolkit
        self.repo = repo_instance

    def create_branch(self, base_branch_name: str, new_branch_name: str):
        pass

    def create_issue(self, title, body):
        base_url = "https://gitlab.com/api/v4"
        project_id = 48829869  # pull from db later
        access_token = os.getenv('GITLAB_TOKEN')

        headers = {
            "PRIVATE-TOKEN": access_token
        }

        params = {
            "title": title,
            "description": body,
        }

        # Make the request
        response = requests.post(f"{base_url}/projects/{project_id}/issues", headers=headers, json=params)

        # Check the response
        if response.status_code == 201:
            print("Issue created successfully!")
            return response.json()["iid"]
        else:
            print(f"Failed to create issue. Status code: {response.status_code}")
            return None