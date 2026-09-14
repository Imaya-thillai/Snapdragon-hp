import json
import os
import sys

# Add backend to path so we can import the RAGStore
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.rag_store import RAGStore

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def build_store():
    print("Loading data...")
    try:
        with open(os.path.join(DATA_DIR, 'govt_schemes.json'), 'r') as f:
            schemes = json.load(f)
            
        # Initialize RAG store pointing to the root-level .chroma folder
        store = RAGStore(persist_dir="../.chroma")
        
        docs = []
        metadatas = []
        ids = []
        
        for i, scheme in enumerate(schemes):
            docs.append(scheme['description'])
            metadatas.append({
                "scheme_name": scheme['scheme_name'],
                "description": scheme['description'],
                "official_url": scheme.get('official_url', '')
            })
            ids.append(f"scheme_{i}")
            
        print(f"Embedding {len(docs)} government schemes into local ChromaDB...")
        store.scheme_collection.add(
            documents=docs,
            metadatas=metadatas,
            ids=ids
        )
        print("Vector store built successfully! Fully offline RAG is now ready.")
    except Exception as e:
        print(f"Failed to build vector store: {e}")

if __name__ == "__main__":
    build_store()
