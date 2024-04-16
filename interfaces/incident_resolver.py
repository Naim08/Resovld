import asyncio
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
from langchain_core.prompts import ChatPromptTemplate
import time
import os


class IncidentResolver:
    def __init__(self, llm, embedder, csv_doc):
       

        self.setup(llm, embedder, csv_doc)

    def setup(self, llm, embedder, csv_doc):

        # Split text data into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(csv_doc)
        db = FAISS.from_documents(splits, embedder)
        retriever = db.as_retriever()
        self.retriever = retriever
        tool = create_retriever_tool(
            retriever,
            "vanguard_incident_logs",
            "Searches through old Vanguard incident logs to help resolve new Vanguard incidents.",
        )

        tools = [tool]
        prompt_config = hub.pull("rlm/rag-prompt")

        #create agent using tools
        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_tokens=8000
        )

        self.agent = agent

        text_splitter2 = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits2 = text_splitter2.split_documents(csv_doc)



        vectorstore = Chroma.from_documents(documents=splits2, embedding=embedder)
        vectorret = vectorstore.as_retriever()

        self.context = vectorret
        template = """You are helping someone at vanguard solve an incident. You have access to the following documents:
        {context}
        Question: {question}
        """
        prompt = ChatPromptTemplate.from_template(template)
        def format_docs(docs):
            # Assuming docs are a list of Document objects with a 'page_content' attribute
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": vectorret | format_docs, "question": RunnablePassthrough()}
            | prompt_config
            | llm
            | StrOutputParser()
        )       


        self.rag = rag_chain


    def answer(self, comment):
        if len(comment) > 8000:  # Check if input exceeds typical processing length
            responses = self.process_in_chunks(comment)
            # Optionally aggregate responses here, depending on your requirements
            return " ".join(responses)
        else:
            return self.agent.invoke(comment)
    

    def answer_with_rag(self, comment):
        return self.rag.invoke(comment)
    
    def process_in_chunks(document, chunk_size=8192):
        # Example function to split and process large documents
        chunks = []
        current_chunk = ""
        
        for sentence in document.split('.'):  # simplistic split by sentence
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + '.'
            else:
                chunks.append(current_chunk)
                current_chunk = sentence + '.'
        if current_chunk:
            chunks.append(current_chunk)

        responses = []
        for chunk in chunks:
            response = self.agent.run(chunk)  # Assuming this is the method to process each chunk
            responses.append(response)
        
        return responses