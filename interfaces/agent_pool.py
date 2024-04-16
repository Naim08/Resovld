from interfaces.agent import Agent

class AgentPool(object):
    _instance = None
    _agents = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
        return cls._instance
    
    def get_agent(self, repo_name, toolkit, llm):
        if repo_name in self._agents:
            return self._agents[repo_name]
        
        # If agent doesn't exist for repo, create one
        agent = Agent.create_agent(toolkit, llm)
        self._agents[repo_name] = agent
        return agent

    def remove_agent(self, repo_name):
        if repo_name in self._agents:
            del self._agents[repo_name]