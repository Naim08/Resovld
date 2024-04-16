import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders.csv_loader import CSVLoader

load_dotenv()
embedder = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
class Agent:
    def __init__(self, agent):
        self.agent = agent
       
    def create_agent(
        toolkit,
        llm,
        agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
    ) -> None:
       
        agent = initialize_agent(
            toolkit.get_tools(), llm, agent=agent_type, verbose=True, handle_parsing_errors=True
        )
     
        return Agent(agent)

    def execute(self, issue_number, filename):
        self.agent.invoke(
            f"""You are to function as a software engineer with the capabilities of a Google Principal Engineer. Your sole task is to address an issue on a gitlab repository based on the instructions below:

            Navigate to gitlab and locate the issue with ID #{issue_number}. It's imperative that you ONLY focus on issue #{issue_number} and no other issue.
            Analyze the content of the issue, specifically the code snippet provided as the solution.
            Open the file named {filename} from the repository. The issue itself is created by another person who sometimes gets the right filename wrong. So it's important you look at 
            {filename} and not the filename in the issue. 
            Identify the section of the code in {filename} that corresponds to the problem discussed in issue #{issue_number}. DO NOT remove or change any other parts of the code.
            Integrate the solution code snippet from the gitlab issue into the problematic section of {filename}. Ensure that the code is merged seamlessly without deleting unrelated parts.
            Create a commit addressing this fix. The commit message should summarize the solution succinctly.
            Initiate a pull request with the above commit. Use the example comment provided in the gitlab issue as the pull request description.
            Once you've completed these tasks for issue #{issue_number}, refrain from making any further modifications."""
        )
    def execute2(self, issue_number, filename):
        self.agent.run(
            f"""Acting as an expert software engineer with capabilities equivalent to a Google Principal Engineer, your primary objective is to resolve an issue in a GitLab repository. Utilize the pre-loaded historical data and your programming knowledge to devise the optimal solution. Follow these instructions:

            1. Load analyze the CSV file at {csv_file}, which is  focusing on similar previous incidents to issue ID #{issue_number}. Evaluate solutions and patterns that have successfully resolved these issues.
            2. Visit GitLab to locate and review the specific issue with ID #{issue_number}. Ensure your focus remains solely on this issue.
            3. Cross-reference the issue details with the insights gathered from the historical data to develop a comprehensive understanding of the problem and potential solutions.
            4. Open the specified file {filename} within the repository. Be cautious to verify the filename as sometimes there are discrepancies in the issue descriptions. Make sure the incident is related to code in the file.
            5. Pinpoint the exact code segment in {filename} that aligns with the issue described. Integrate the most suitable solution derived from the historical data analysis, ensuring that the integration is seamless and does not impact.
            6. Prepare and commit your changes with a clear and succinct message that encapsulates the solution, linking it to both the issue and the historical data used for decision-making.
            7. Create a pull request with the commit, using a detailed description that includes how the solution was derived from historical data analysis.
            8. After completing the resolution for issue #{issue_number}, do not proceed with further modifications without additional verification."""
        )
