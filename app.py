import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from groq import Groq

# Setup path configurations focused explicitly on your D: drive storage
CHROMA_DIR = r"D:\f1-chatbot\data\chroma_db"

def setup_rag_engine():
    """Initializes the local embedding translator and loads our ChromaDB tables."""
    print("Connecting to local ChromaDB semantic tables...")
    
    # Ensure we use the exact same embedding algorithm from Phase 3
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # Load up our persisted database from disk on D:
    db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_model)
    return db

def ask_f1_bot():
    # 1. Start up database connections
    db = setup_rag_engine()
    
    # 2. Check for the Groq Cloud API environment key
    if not os.environ.get("GROQ_API_KEY"):
        print("\n✗ Error: GROQ_API_KEY environment variable not found!")
        print("Please set it in your terminal session before execution:")
        print('  $env:GROQ_API_KEY="gsk_xxxxxxxxxxxx..."')
        return

    # Initialize the Groq processing engine
    client = Groq()
    
    print("\n====================================================")
    print("🏎️ F1 HISTORICAL CHATBOT INITIALIZED ENGINE ONLINE 🏎️")
    print("Type your questions below! (Type 'exit' to quit)")
    print("====================================================\n")

    while True:
        query = input("You: ")
        if query.strip().lower() == "exit":
            print("Shutting down pitwall systems. Goodbye!")
            break
            
        if not query.strip():
            continue
            
        print("\n[Retrieving matching context tracks...]")
        # Query ChromaDB to extract the top 4 most semantically matching text records
        matching_docs = db.similarity_search(query, k=4)
        
        # Merge contents together into a clean knowledge block
        context_block = "\n---\n".join([doc.page_content for doc in matching_docs])
        
        # Build an aggressive system engineering frame to force strict fact alignment
        system_prompt = f"""
You are an expert Formula 1 statistical analyst and historical query system.
Answer the user's question with professional engineering depth, matching their vocabulary and technical style.

CRITICAL INSTRUCTION:
You must formulate your response using ONLY the provided authentic data context below. 
If the context does not contain the information required to explicitly answer the question, state directly that you do not have that data on file—NEVER hallucinate or extrapolate details out of raw training weights.

AUTHENTIC DATA CONTEXT RETRIEVED FROM DISK:
{context_block}
"""

        try:
            print("[Streaming analysis from LLM execution engine...]\n")
            # Fire the full structured payload to Groq's high-speed Llama-3.1-8b engine
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1, # Keep temperature near absolute zero to minimize creative wandering
                max_tokens=800
            )
            
            # Print response output to terminal window
            response_text = completion.choices[0].message.content
            print(f"Bot: {response_text}\n")
            print("-" * 50)
            
        except Exception as e:
            print(f"✗ Core execution transmission failed: {e}\n")

if __name__ == "__main__":
    ask_f1_bot()