from langchain_community.document_loaders import PyPDFLoader
from pathlib import Path

def load_documents():

    data_path = Path(__file__).resolve().parent.parent.parent / "data"
    documents = []

    for file in data_path.glob("*.pdf"):
        loader = PyPDFLoader(str(file))
        docs = loader.load()

        documents.extend(docs)
        print(f"Loaded {file.name} ({len(docs)} pages)")

    return documents