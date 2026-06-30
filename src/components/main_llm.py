from src.logger import logging
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
from langchain_core.messages import SystemMessage,HumanMessage
from dotenv import load_dotenv
load_dotenv()

class Main_llm:
    def __init__(self):
        logging.info("initializing main llm")
        self.llm = HuggingFaceEndpoint(repo_id='deepseek-ai/DeepSeek-V3.2')
        self.main_llm = ChatHuggingFace(llm=self.llm)
        logging.info('initializing chat history')
        self.system_content = """
            You are a Senior Fraud Detection Analyst. 
            You have access to a secure, encrypted vector database (CyborgDB).
            
            YOUR RULES:
            1. Analyze the "RETRIEVED EVIDENCE" provided by the user.
            2. Compare it to the "INCOMING TRANSACTION".
            3. End with a Verdict: [FRAUD] or [SAFE].
            4. If asked follow-up questions, use the conversation history.
            """
        self.chat_history=[
            SystemMessage(content=self.system_content)
        ]
        logging.info('both created successfully!')

    def initiate_main_llm(self):
        return self.main_llm,self.chat_history

# if __name__ == "__main__":
#     obj = Main_llm()
#     chat_bot,chat_history = obj.initiate_main_llm()
#     chat_history.append(HumanMessage(content='hi how are you?'))
#     print(chat_bot.invoke(chat_history))