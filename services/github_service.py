from interfaces.service import GitService
from langchain.utilities.github import GitHubAPIWrapper
from langchain.agents.agent_toolkits.github.toolkit import GitHubToolkit

import os

class GithubService(GitService):

    def __init__(self, app_id, pem, repo_name, branch_name, base_branch_name):
        os.environ["GITHUB_APP_ID"] = app_id
        os.environ["GITHUB_APP_PRIVATE_KEY"] = pem
        os.environ["GITHUB_REPOSITORY"] = repo_name
        os.environ["GITHUB_BRANCH"] = branch_name
        os.environ["GITHUB_BASE_BRANCH"] = base_branch_name

        self.git = GitHubAPIWrapper()

        self.repo = self.git.github_repo_instance

    def create_branch(self, base_branch_name: str, new_branch_name: str):
        sb = self.repo.get_branch(base_branch_name)
        self.repo.create_git_ref(ref='refs/heads/' + new_branch_name, sha=sb.commit.sha)

    def create_issue(self, title, body):
        issue = self.repo.create_issue(title=title, body=body)

        return issue.number

    def issue_comment(self, issue_number, comment):
        issue = self.repo.get_issue(issue_number)
        issue.create_comment(comment)

        
       