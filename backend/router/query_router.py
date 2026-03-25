import warnings
warnings.filterwarnings("ignore")

from backend.agent.agent_runner import run_agent
from backend.rag.rag_chain import get_rag_response
from backend.rag.vector_store import load_vector_store
from backend.llm.llm_provider import get_mini_llm


SQL_KEYWORDS = [
    "product", "products", "price", "cost", "stock", "inventory",
    "customer", "customers", "client", "clients",
    "order", "orders", "sales", "revenue", "total", "purchase",
    "salesperson", "sales person",
    "top", "list", "show", "how many", "count", "average", "sum",
    "highest", "lowest", "most", "least", "best", "worst",
    "compare", "between", "filter", "find", "get",
]

RAG_KEYWORDS = [
    "policy", "policies", "procedure", "procedures", "guideline", "guidelines",
    "document", "handbook", "manual", "report", "mentorship",
    "leave", "vacation", "holiday", "sick", "benefit", "benefits",
    "employee", "employees", "hr", "human resource",
    "salary", "compensation", "appraisal", "performance",
    "rule", "rules", "regulation", "compliance", "code of conduct",
    "onboarding", "training", "termination", "resignation",
    "bonus", "bonuses", "incentive", "incentives",
    "allowance", "allowances", "reimbursement",
    "insurance", "medical", "health", "dental",
    "pension", "provident", "gratuity",
    "working hours", "overtime", "remote", "work from home",
    "dress code", "conduct", "ethics",
    "promotion", "increment", "raise",
    "does the company", "does company",
]


# Keyword Router 
def keyword_classify(question: str) -> str:
    """
    Returns: 'sql', 'rag', or 'unknown'
    Fast keyword scoring — runs in microseconds, no API call needed.
    """
    question_lower = question.lower().strip()
    sql_score = sum(1 for kw in SQL_KEYWORDS if kw in question_lower)
    rag_score = sum(1 for kw in RAG_KEYWORDS if kw in question_lower)

    print(f"Keyword scores — SQL: {sql_score} | RAG: {rag_score}")

    if sql_score == 0 and rag_score == 0:
        return "unknown"
    if sql_score > rag_score:
        return "sql"
    if rag_score > sql_score:
        return "rag"
    return "sql"  


#  LLM Router 
def llm_classify(question: str) -> str:
    """
    Uses GPT-4o-mini to classify ambiguous questions.
    Only called when keyword router returns 'unknown' or scores are tied.
    Returns: 'sql' or 'rag'
    """
    try:
        llm = get_mini_llm()

        prompt = f"""You are a query router for an Enterprise Knowledge Assistant.

The system has two data sources:
1. SQL DATABASE — Contains structured business data:
   - Products (names, prices, costs, categories)
   - Customers (names, contacts, companies)
   - Sales Orders (order details, quantities, revenue)
   Use SQL for: counts, aggregations, lists, comparisons of business data

2. DOCUMENT KNOWLEDGE BASE — Contains company HR documents:
   - HR policies, leave policies, employee handbooks
   - Benefits, bonuses, incentives, compensation guidelines
   - Company rules, code of conduct, compliance documents
   Use RAG for: policy questions, HR questions, company guidelines

Classify this question into exactly one category.
Reply with ONLY one word: SQL or RAG

Question: {question}

Answer:"""

        response = llm.invoke(prompt)
        answer = response.content.strip().upper()

        if "SQL" in answer:
            print(f"LLM router decision: SQL")
            return "sql"
        elif "RAG" in answer:
            print(f"LLM router decision: RAG")
            return "rag"
        else:
            print(f"LLM router gave unexpected response: {answer} — defaulting to SQL")
            return "sql"

    except Exception as e:
        print(f"LLM router failed: {e} — falling back to keyword result")
        return "sql"


#  Combined Router 
def classify_question(question: str) -> str:
    """
    Two-stage routing:
    Stage 1 — keyword scoring (fast, free)
    Stage 2 — LLM classification (smart, only when needed)
    """
    keyword_result = keyword_classify(question)

    question_lower = question.lower().strip()
    sql_score = sum(1 for kw in SQL_KEYWORDS if kw in question_lower)
    rag_score = sum(1 for kw in RAG_KEYWORDS if kw in question_lower)

    if abs(sql_score - rag_score) >= 2:
        print(f"Clear keyword winner: {keyword_result.upper()} — skipping LLM router")
        return keyword_result

    print(f"Ambiguous question — using LLM router...")
    return llm_classify(question)


def choose_model(route: str, question: str) -> str:
    """
    SQL always uses gpt-4o — needs strong reasoning for complex queries.
    RAG uses gpt-4o-mini for short questions, gpt-4o for complex ones.
    """
    if route == "sql":
        return "gpt-4o"
    if route == "rag":
        if len(question) < 50:
            return "gpt-4o-mini"
        else:
            return "gpt-4o"
    return "gpt-4o"

_vectordb = None

def get_vectordb():
    global _vectordb
    if _vectordb is not None:
        return _vectordb
    try:
        _vectordb = load_vector_store()
        return _vectordb
    except Exception as e:
        print(f"Vector store load failed: {e}")
        return None


#  Main Router 
def route_question(question: str) -> dict:

    if not question or not question.strip():
        return {
            "answer": "Please ask a question.",
            "source_type": "none",
            "sources": []
        }

    route = classify_question(question)
    print(f"Final route: {route.upper()}")

    #  SQL  
    if route in ("sql", "unknown"):
        try:
            print("Routing to: SQL Agent")
            answer = run_agent(question)
            return {
                "answer": answer,
                "source_type": "sql",
                "sources": ["AdventureWorks Database"]
            }
        except Exception as e:
            print(f"SQL agent failed: {e}")
            if route == "unknown":
                return {
                    "answer": f"I could not process your question: {str(e)}",
                    "source_type": "error",
                    "sources": []
                }
            print("SQL failed — trying RAG as fallback...")
            route = "rag"
# rag
    if route == "rag":
        try:
            print("Routing to: RAG Pipeline")
            vectordb = get_vectordb()

            if vectordb is None:
                return {
                    "answer": "Document knowledge base is not available. Please run ingest.py first.",
                    "source_type": "error",
                    "sources": []
                }

            result = get_rag_response(question, vectordb)
            return {
                "answer": result["answer"],
                "source_type": "rag",
                "sources": result.get("sources", []),
                "context_used": result.get("context_used", [])
            }
        except Exception as e:
            print(f"RAG pipeline failed: {e}")
            return {
                "answer": f"Both SQL and document search failed: {str(e)}",
                "source_type": "error",
                "sources": []
            }

if __name__ == "__main__":
    test_questions = [
        "Show me top 5 products by price",            
        "What is the leave policy?",                  
        "How many customers do we have?",             
        "Does the company offer bonuses?",            
        "What are the working hours?",                
        "What is the weather today?",                 
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = route_question(q)
        print(f"Source: {result['source_type'].upper()}")
        print(f"Answer: {result['answer'][:200]}...")
        if result.get('sources'):
            print(f"Sources: {result['sources']}")
