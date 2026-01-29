from dotenv import load_dotenv
from fastembed import SparseTextEmbedding 
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

llm = ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)

# bm25_embeddings = SparseTextEmbedding("Qdrant/bm25")
openai_embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1024)