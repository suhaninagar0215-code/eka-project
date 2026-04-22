import warnings
warnings.filterwarnings("ignore")

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

CHROMA_DB_PATH = Path(__file__).resolve().parent.parent.parent / "chroma_db"

_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is not None:
        return _embeddings

    print("Loading embedding model...")
    _embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True, 
            "batch_size": 32,
        }              
    )
    print("Embedding model loaded.")
    return _embeddings

def create_vector_store(chunks):
    if not chunks:
        raise ValueError("No chunks provided to create vector store.")

    print(f"Creating vector store with {len(chunks)} chunks...")

    embeddings = get_embeddings()
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DB_PATH),
        collection_name="eka_documents"
    )

    print(f"Vector store created at: {CHROMA_DB_PATH}")
    print(f"Total vectors stored: {vectordb._collection.count()}")

    return vectordb

def load_vector_store():
    if not CHROMA_DB_PATH.exists():
        raise FileNotFoundError(
            f"No vector store found at: {CHROMA_DB_PATH}\n"
            f"Run ingest.py first to create the vector store."
        )

    embeddings = get_embeddings()

    vectordb = Chroma(
        persist_directory=str(CHROMA_DB_PATH),
        embedding_function=embeddings,
        collection_name="eka_documents",   
    )

    count = vectordb._collection.count()
    if count == 0:
        raise ValueError(
            f"Vector store exists but is empty at: {CHROMA_DB_PATH}\n"
            f"Run ingest.py again to rebuild it."
        )

    print(f"Vector store loaded: {count} vectors from {CHROMA_DB_PATH}")
    return vectordb

if __name__ == "__main__":
    try:
        db = load_vector_store()
        print("Vector store loaded successfully.")
        results = db.similarity_search("test query", k=2)
        print(f"Sample search returned {len(results)} results.")
    except FileNotFoundError as e:
        print(str(e))