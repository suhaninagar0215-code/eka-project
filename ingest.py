import warnings
warnings.filterwarnings("ignore")

from backend.rag.document_loader import load_documents
from backend.rag.text_splitter import split_documents
from backend.rag.vector_store import create_vector_store, CHROMA_DB_PATH
import shutil
import sys


def run_ingest(force_rebuild: bool = False):

    if force_rebuild and CHROMA_DB_PATH.exists():
        print("Force rebuild — deleting existing vector store...")
        shutil.rmtree(CHROMA_DB_PATH)
        print("Deleted.")

    print("\nStep 1: Loading documents...")
    documents = load_documents()

    print("\nStep 2: Splitting documents...")
    chunks = split_documents(documents)
    print("\nStep 3: Creating vector store...")
    vectordb = create_vector_store(chunks)

    print("\nStep 4: Verifying...")
    count = vectordb._collection.count()
    print(f"Verification: {count} vectors in store.")

    if count == 0:
        raise RuntimeError("Ingest failed — vector store is empty after build.")

    print("\nIngest complete. Vector store is ready.")
    return vectordb


if __name__ == "__main__":
    force = "--rebuild" in sys.argv
    run_ingest(force_rebuild=force)