from langchain_openai import ChatOpenAI, OpenAIEmbeddings


from dotenv import load_dotenv
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent

import os
load_dotenv()


embedder = OpenAIEmbeddings(openai_api_key=os.getenv('OPENAI_API_KEY'))
llm = ChatOpenAI(temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'), model_name="gpt-4")
Allm = ChatAnthropic(model="claude-3-sonnet-20240229")

csv_path = "../Unique_Incident_Logs.csv"
loader = CSVLoader(csv_path)
data = loader.load()

# Split text data into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(data)
db = FAISS.from_documents(splits, embedder)
retriever = db.as_retriever()

tool = create_retriever_tool(
    retriever,
    "vanguard_incident_logs",
    "Searches through old incident logs to help resolve new incidents.",
)

tools = [tool]
prompt_config = hub.pull("hwchase17/openai-functions-agent")
print(prompt_config.messages)

agent = create_openai_tools_agent(llm, tools, prompt_config)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


#create agent using tools
# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     handle_parsing_errors=True,
# )
msg = "actions to take for incidents related to swift?"
result = agent_executor.invoke({"input": "actions to take for incidents related to swift?"})
for chunk in agent_executor.stream({"input": "actions to take for incidents related to swift?"}):
    print(chunk)
print(result)


# text_splitter2 = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# splits2 = text_splitter2.split_documents(data)



# vectorstore = Chroma.from_documents(documents=splits2, embedding=embedder)
# vectorret = vectorstore.as_retriever()
# def format_docs(docs):
#     # Assuming docs are a list of Document objects with a 'page_content' attribute
#     return "\n\n".join(doc.page_content for doc in docs)

# rag_chain = (
#     {"context": vectorret | format_docs, "question": RunnablePassthrough()}
#     | prompt_config
#     | llm
#     | StrOutputParser()
# )
# query = "actions to take for incidents related to swift?"  # Example query
# response = rag_chain.invoke(query)
# print(response)

# # Clean up vector store
# vectorstore.delete_collection()



# # print(result)
# # # Create Chroma vector store from the chunks
# # vectorstore = Chroma.from_documents(documents=splits, embedding=embedder)

# # # Retrieve and generate using the relevant snippets
# # retriever = vectorstore.as_retriever()
# # prompt = hub.pull("rlm/rag-prompt")

# # def format_docs(docs):
# #     # Assuming docs are a list of Document objects with a 'page_content' attribute
# #     return "\n\n".join(doc.page_content for doc in docs)

# # rag_chain = (
# #     {"context": retriever | format_docs, "question": RunnablePassthrough()}
# #     | prompt
# #     | llm
# #     | StrOutputParser()
# # )

# # query = "What is swift?"  # Example query
# # response = rag_chain.invoke(query)
# # print(response)

# # # Clean up vector store
# # vectorstore.delete_collection()