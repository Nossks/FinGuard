import os
import sys
from langchain_core.prompts import load_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import Field,BaseModel
from typing import Literal
from dotenv import load_dotenv
load_dotenv()
from src.logger import logging

class output(BaseModel):
    Decision:Literal['SEARCH','CHAT']=Field(description="Choose 'SEARCH' if the query requires technical fraud detection info. Choose 'CHAT' for general conversation.")
    query:str=Field(default="N/A",description="If decision is SEARCH, extract the core technical keywords. If CHAT, return 'N/A.")
    original_query:str=Field(description="give the user's original query")

class Router_llm:
    def __init__(self):
        logging.info('inititalizing router')
        self.router_llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')
        self.structured_router_llm = self.router_llm.with_structured_output(output)

        logging.info('loading router prompt template')
        self.template = load_prompt('/home/cry_more/ongoing/fraud-detection/router_template.json')
        self.router_llm_chain = self.template | self.structured_router_llm

        logging.info('router chain created')

    def initiate_routing(self):
        return self.router_llm_chain
    
# if __name__ == "__main__":
#     obj = Router_llm()
#     chain = obj.initiate_routing()
#     print(chain.invoke({'query':"hi what is up and i need to help you in analyzing this fraud"}))