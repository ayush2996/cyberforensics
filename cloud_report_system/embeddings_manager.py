# embeddings_manager.py
import cohere
import os
from typing import List
import numpy as np
from config import settings

class CloudEmbeddingsManager:
    def __init__(self):
        self.cohere_client = cohere.Client(
            api_key=settings.COHERE_API_KEY
        )
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Cohere API
        """
        try:
            response = self.cohere_client.embed(
                texts=texts,
                model="embed-english-light-v3.0",
                input_type="search_document"
            )
            return response.embeddings
        
        except Exception as e:
            print(f"Cohere embedding failed: {e}")
            # Fallback to HuggingFace
            return await self._embed_hf(texts)
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query
        """
        response = self.cohere_client.embed(
            texts=[query],
            model="embed-english-light-v3.0",
            input_type="search_query"
        )
        return response.embeddings[0]
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Alias for embed_query - get embedding for a single text.
        Used by rag_retriever and corrective_rag.
        """
        return await self.embed_query(text)

    async def _embed_hf(self, texts: List[str]) -> List[List[float]]:
        """
        Fallback: HuggingFace Inference API
        """
        import httpx
        
        API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_URL,
                headers=headers,
                json={"inputs": texts}
            )
            return response.json()

embeddings_manager = CloudEmbeddingsManager()
