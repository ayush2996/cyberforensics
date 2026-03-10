# vector_store.py
import chromadb
from chromadb.config import Settings
import json

class LightweightVectorStore:
    """
    Store vectors locally, but embeddings come from API
    """
    def __init__(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./vector_db",
            anonymized_telemetry=False
        ))
        
        self.collection = self.client.get_or_create_collection(
            name="reports",
            metadata={"hnsw:space": "cosine"}
        )
    
    async def add_documents(self, documents: list):
        """Add documents with cloud embeddings"""
        from embeddings_manager import embeddings_manager
        
        texts = [doc["text"] for doc in documents]
        embeddings = await embeddings_manager.embed_texts(texts)
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=[doc["metadata"] for doc in documents],
            ids=[doc["id"] for doc in documents]
        )
    
    async def search(self, query: str, k: int = 5):
        """Search with cloud embedding"""
        from embeddings_manager import embeddings_manager
        
        query_embedding = await embeddings_manager.embed_query(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        return results

vector_store = LightweightVectorStore()
