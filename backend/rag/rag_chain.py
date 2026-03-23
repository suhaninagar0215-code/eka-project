from backend.llm.llm_provider import get_llm

def get_rag_response(query, vectordb):

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    docs = retriever.invoke(query)

    context = "\n\n".join([doc.page_content for doc in docs])

    llm = get_llm()

    prompt = f"""
You are an enterprise knowledge assistant.

Rules:
- Answer ONLY from the provided context
- If answer is not in context, say "I don't know"
- Be concise and professional

Context:
{context}

Question:
{query}
"""

    response = llm.invoke(prompt)

    sources = [
    doc.metadata.get("source", "").split("\\")[-1]
    for doc in docs
    ]
    return {
        "answer": response.content,
        "sources": list(set(sources))
    }