import time
import sys
import os
from dataclasses import dataclass
import pandas as pd
from cyborgdb_core.integrations.langchain import CyborgVectorStore
from cyborgdb_core import DBConfig
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma,FAISS
from dotenv import load_dotenv
load_dotenv()

from src.exception import CustomException
from src.logger import logging

@dataclass
class DataIngestionConfig:
    raw_data_path = os.path.join('data','financial_synthetic.csv')
    faiss_data_path = os.path.join('data','faiss_index')
    chroma_data_path = os.path.join('data','chroma_db')

class DataIngestion:
    def __init__(self):
        self.ingestion_config=DataIngestionConfig()
        self.embedding_model = HuggingFaceEmbeddings(model='sentence-transformers/all-MiniLM-L6-v2')

    def get_documents(self):
        df = pd.read_csv(self.ingestion_config.raw_data_path)
        docs=[Document(
            page_content=row['text'],
            metadata={
                'amount':row['amount'],
                'label':row['label'],
                'other_info':row['metadata']
            }
        ) for _,row in df.iterrows()]

        return docs

    def store_embedding(self,docs):
        metrics={}
        logging.info('starting chroma')
        st_time=time.time()
        vdb1 = Chroma.from_documents(
            documents=docs,
            embedding=self.embedding_model,
            persist_directory=self.ingestion_config.chroma_data_path
        )
        en_time=time.time()
        metrics['chroma']=en_time-st_time
        logging.info(f"chroma done in {metrics['chroma']}sec")

        logging.info('starting faiss')
        st_time=time.time()
        vdb2 = FAISS.from_documents(
            documents=docs,
            embedding=self.embedding_model,
        )
        vdb2.save_local(self.ingestion_config.faiss_data_path)
        en_time=time.time()
        metrics['faiss']=en_time-st_time
        logging.info(f"faiss done in {metrics['faiss']}sec")

        logging.info("starting cyborgdb")
        st_time=time.time()
        store = CyborgVectorStore.from_documents(
            documents=docs,
            embedding=self.embedding_model,
            index_key=CyborgVectorStore.generate_key(),
            api_key="cyborg_36c89c513cac4c1c871a",        ##enter the api key here
            index_location=DBConfig('memory'),
            config_location=DBConfig('memory'),
            index_type="ivfflat",
            metric="cosine"
        )
        en_time=time.time()
        metrics['cyborgdb']=en_time-st_time
        logging.info(f"cyborg done in {metrics['cyborgdb']}sec")

        return metrics,store

    def initiate_data_ingestion(self):
        logging.info('entered data ingestion')
        try:
            logging.info(f'reading data from {self.ingestion_config.raw_data_path}')
            if not os.path.exists(self.ingestion_config.raw_data_path):
                raise FileNotFoundError(f'file not found: {self.ingestion_config.raw_data_path}')

            logging.info('converting df to documents')
            docs = self.get_documents()
            logging.info(f'{len(docs)} documents prepared!')

            logging.info("feeding data into vector db's")
            return self.store_embedding(docs)

        except Exception as e:
            raise CustomException(e,sys)
        
# if __name__ == "__main__":
#     obj = DataIngestion()
#     metrics,store = obj.initiate_data_ingestion()
#     print(metrics)
