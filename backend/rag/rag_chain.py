import warnings
warnings.filterwarnings("ignore")
from pathlib import Path
from backend.llm.llm_provider import get_llm_by_name

def get_rag_response(query: str, vectordb, model: str = "gpt-4o-mini") -> dict:

    if not query or not query.strip():
        return {
            "answer": "Please provide a valid question.",
            "sources": [],
            "context_used": []
        }
    

    retriever = vectordb.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k":12,
            "fetch_k": 40,
            "lambda_mult": 0.5
        }
    )

    docs = retriever.invoke(query)

    print("\n Retrieved Documents:\n")
    for i, doc in enumerate(docs):
        print(f"\n--- Doc {i+1} ---")
        print(doc.page_content[:500])

    if not docs:
        return {
            "answer": "I could not find any relevant information in the documents.",
            "sources": [],
            "context_used": []
        }
    context_parts = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")
        context_parts.append(
            f"[Source {i+1}: {source}, Page {page}]\n{doc.page_content}"
        )

    context = "\n\n".join(context_parts)
    MAX_CONTEXT_LENGTH = 4000
    if len(context) > MAX_CONTEXT_LENGTH:
        context = context[:MAX_CONTEXT_LENGTH]
    llm = get_llm_by_name(model)
    print(f"[RAG] Using model: {model}")

    prompt = f"""You are an Enterprise Knowledge Assistant.
Your job is to answer questions based strictly on the provided document context.

STRICT RULES:
- Answer ONLY from the provided context
- If the answer is not in the context, say exactly: "I don't have information about this in the available documents."
- Never make up information
- Always mention which source/document your answer comes from
- Be concise and professional
- If multiple sources mention the same topic, combine them into one coherent answer

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""

    response = llm.invoke(prompt)

    sources = []
    for doc in docs:
        raw_source = doc.metadata.get("source", "")
        if raw_source:
            clean_source = Path(raw_source).name
            page = doc.metadata.get("page", None)
            source_str = clean_source
            if page is not None:
                source_str = f"{clean_source} (Page {page + 1})"
            if source_str not in sources:
                sources.append(source_str)

    return {
        "answer": response.content,
        "sources": sources,
        "context_used": [
            {
                "content": doc.page_content[:200] + "...",
                "source": doc.metadata.get("source", ""),
                "page": doc.metadata.get("page", "?"),
            }
            for doc in docs
        ]
    }

if __name__ == "__main__":
    from backend.rag.vector_store import load_vector_store

    db = load_vector_store()
    result = get_rag_response("What is the leave policy?", db, model="gpt-4o-mini")

    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nSources:")
    for s in result['sources']:
        print(f"  - {s}")

    docs = db.similarity_search("internship policy", k=8)

    for d in docs:
        print("\n---")
        print(d.metadata)