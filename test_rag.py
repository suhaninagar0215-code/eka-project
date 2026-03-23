from backend.rag.document_loader import load_documents
from backend.rag.text_splitter import split_documents
from backend.rag.vector_store import create_vector_store, load_vector_store
from backend.rag.rag_chain import get_rag_response


def build_vector_db():
    docs = load_documents()
    chunks = split_documents(docs)
    vectordb = create_vector_store(chunks)
    return vectordb


def load_existing_db():
    return load_vector_store()


def test_rag():

    try:
        USE_EXISTING_DB = True

        if USE_EXISTING_DB:
            vectordb = load_existing_db()
        else:
            vectordb = build_vector_db()

        query = "What is the leave policy?"

        response = get_rag_response(query, vectordb)

        print("\n Answer:")
        print(response["answer"])

        print("\n Sources:")
        for src in response["sources"]:
            print("-", src)

    except Exception as e:
        print("\n RAG Test Failed:")
        print(str(e))


if __name__ == "__main__":
    test_rag()