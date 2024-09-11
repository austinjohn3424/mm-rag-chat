# vector_db.py
from pinecone import Pinecone
from config import API_KEY, INDEX_NAME, logging

def initialize_pinecone():
    try:
        pc = Pinecone(api_key=API_KEY)
        index = pc.Index(INDEX_NAME)
        logging.info(f"Successfully connected to Pinecone index: {INDEX_NAME}")
        return index
    except Exception as e:
        logging.error(f"Failed to connect to Pinecone index: {str(e)}")
        raise

def query_pinecone(index, query_embedding, top_k=10):
    try:
        response = index.query(vector=query_embedding, top_k=top_k, include_values=False)
        return response.get('matches', [])
    except Exception as e:
        logging.error(f"Error querying Pinecone: {str(e)}")
        return []
