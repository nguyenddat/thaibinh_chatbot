import os
from core import embeddings

import faiss
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_community.document_loaders.text import TextLoader
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core import setting

class Retriever:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

        self.data_path = os.path.join(setting.artifact_dir, "procedures")
        self.save_path = os.path.join(setting.artifact_dir, "vector_db")
    

    def build(self):
        texts = self.load_txt()
        index = faiss.IndexFlatL2(1024)
        vector_store = FAISS(
            embedding_function = embeddings,
            index = index,
            docstore = InMemoryDocstore(),
            index_to_docstore_id = {}
        )

        vector_store.add_documents(texts)
        vector_store.save_local(self.save_path)
        self.retriever = VectorStoreRetriever(vectorstore=vector_store)
        return self


    def load_txt(self):
        data = []
        for file in tqdm(os.listdir(self.data_path), desc = "Loading procedures for retriever"):
            file_path = os.path.join(self.data_path, file)
            loader = TextLoader(file_path = file_path, encoding = "utf-8")
            documents = loader.load()
            for doc in documents:
                data.append(doc.page_content)
        
        texts = self.text_splitter.create_documents(data)
        return texts

retriever = Retriever()