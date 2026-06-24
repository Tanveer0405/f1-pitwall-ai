import os
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Setup path configurations focused explicitly on your D: drive storage
PROCESSED_FILE = r"D:\f1-chatbot\data\processed\master_f1_chunks.json"
CHROMA_DIR = r"D:\f1-chatbot\data\chroma_db"

def build_vector_db():
    # 1. Verify master chunk file exists
    if not os.path.exists(PROCESSED_FILE):
        print(f"✗ Master chunks array not found at {PROCESSED_FILE}. Run chunk_all_data.py first.")
        return

    print("Loading data chunk payload index...")
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    # 2. Re-instantiate array data back into standard LangChain Document classes
    documents = []
    for item in chunks_data:
        doc = Document(
            page_content=item["text"],
            metadata=item["metadata"]
        )
        documents.append(doc)
    
    print(f"Parsed {len(documents)} context document definitions.")

    # 3. Pull down the industry-standard embedding model
    print("Initializing HuggingFace BGE Embedding engine (bge-small-en-v1.5)...")
    # This runs fully local on your machine's CPU
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    # 4. Initialize and build the persistence engine
    print(f"Populating ChromaDB system vectors inside local index: {CHROMA_DIR}...")
    
    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )

    print("\n====================================================")
    print("✓ SUCCESS! Vector store generated and saved to disk!")
    print("====================================================")

if __name__ == "__main__":
    build_vector_db()