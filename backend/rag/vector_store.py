from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def create_vector_store(chunks):

    persist_dir = Path("chroma_db")

    embeddings = get_embeddings()

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(persist_dir)
    )

    vectordb.persist()
    print("Vector DB created and persisted")

    return vectordb


def load_vector_store():

    persist_dir = Path("chroma_db")

    embeddings = get_embeddings()

    vectordb = Chroma(
        persist_directory=str(persist_dir),
        embedding_function=embeddings
    )

    print("Loaded existing vector DB")

    return vectordb