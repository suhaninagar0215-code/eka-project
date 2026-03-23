import warnings
warnings.filterwarnings("ignore")

from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents):

    if not documents:
        raise ValueError("No documents provided to split.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(documents)

    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_size"] = len(chunk.page_content)

    print(f"Split {len(documents)} pages into {len(chunks)} chunks.")
    print(f"Avg chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks)} chars")

    return chunks

if __name__ == "__main__":
    from backend.rag.document_loader import load_documents

    docs = load_documents()
    chunks = split_documents(docs)

    print(f"\nSample chunk:")
    print(f"Content: {chunks[0].page_content[:200]}...")
    print(f"Metadata: {chunks[0].metadata}")