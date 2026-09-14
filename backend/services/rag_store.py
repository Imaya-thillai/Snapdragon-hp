import os
import chromadb
from chromadb.utils import embedding_functions

class RAGStore:
    def __init__(self, persist_dir="./.chroma"):
        self.persist_dir = persist_dir
        # Use a small offline embedding model (downloads once, runs completely offline)
        # SentenceTransformers is the industry standard for this.
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Initialize the persistent local Chroma database
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.scheme_collection = self.client.get_or_create_collection(
            name="govt_schemes",
            embedding_function=self.embedding_fn
        )
        print("RAG Store Initialized (Fully Offline ChromaDB)")

    def query_scheme(self, query_text: str):
        """Queries the local vector store for matching government schemes."""
        try:
            results = self.scheme_collection.query(
                query_texts=[query_text],
                n_results=1
            )
            
            # Check if we have a valid match below an arbitrary distance threshold (closer to 0 is better)
            if results and results['distances'] and len(results['distances'][0]) > 0 and results['distances'][0][0] < 1.5: 
                meta = results['metadatas'][0][0]
                return {
                    "match_found": True,
                    "scheme_name": meta.get("scheme_name", "Unknown"),
                    "description": meta.get("description", "No description available.")
                }
        except Exception as e:
            print(f"Error querying RAG store: {e}")
            
        return {"match_found": False, "scheme_name": None, "description": None}

rag_store = RAGStore()
