from src.components.data_ingestion import DataIngestion
from src.components.data_generation import DataGenerator
from src.components.database_retrival import Retrieval
from src.components.router_llm import Router_llm
from src.components.main_llm import Main_llm
import subprocess
from src.logger import logging
from src.exception import CustomException
from langchain_core.messages import AIMessage,HumanMessage
from langchain_core.runnables import RunnableBranch,RunnableLambda

class Prediction:
    def __init__(self):
        self.generation = DataGenerator()
        self.generation.initiate_data_generation(1000)
        self.ingestion = DataIngestion()
        _, self.cyborg_db = self.ingestion.initiate_data_ingestion()
        subprocess.run(['python3', 'src/components/router_template_generator.py'])
        self.retriever = Retrieval()
        self.router_llm = Router_llm()
        self.router = self.router_llm.initiate_routing()
        self.llm = Main_llm()
        self.chatbot, self.chat_history = self.llm.initiate_main_llm()
        self.metrics_of_retrieved_context = {'cyborg': 0, 'faiss': 0, 'chroma': 0}
        
    def _search_path(self,router_output):
        logging.info('entering search path')
        self.metrics_of_retrieved_context, retrieved_context = self.retriever.initiate_retrival(self.cyborg_db,router_output.query)
        prompt = f"""
            Human query {router_output.original_query} and retrieved context is {retrieved_context}
        """
        self.chat_history.append(HumanMessage(content=prompt))
        return self.chat_history

    def _chat_path(self,router_output):
        logging.info('entering chat path')
        self.chat_history.append(HumanMessage(content=router_output.original_query))
        return self.chat_history

    def predict(self,query):
        self.metrics_of_retrieved_context = {'cyborg': 0, 'faiss': 0, 'chroma': 0}
        logging.info('getting ready to predict')
        branch_chain = RunnableBranch(
            (lambda x: x.Decision == 'SEARCH', RunnableLambda(self._search_path)),
            (lambda x: x.Decision == 'CHAT', RunnableLambda(self._chat_path)),
            (self._chat_path)
        )

        final_chain = self.router | branch_chain | self.chatbot
        reply = final_chain.invoke({'query':query})

        self.chat_history.append(AIMessage(content=reply.content))

        return reply,self.metrics_of_retrieved_context
        
# if __name__ == "__main__":
#     predictor = Prediction()
#     reply, metrics = predictor.predict("hi what is up?")
#     print(reply)
#     if metrics['cyborg']!=0:
#         print(metrics)