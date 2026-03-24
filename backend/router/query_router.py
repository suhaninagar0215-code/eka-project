import warnings
warnings.filterwarnings("ignore")

from backend.agent.agent_runner import run_agent
from backend.rag.rag_chain import get_rag_response
from backend.rag.vector_store import load_vector_store

def choose_model(route: str, question: str) -> str:
    question = question.lower()

    if route == "sql":
        return "gpt-4o"  
    if route == "rag":
        if len(question) < 50:
            return "gpt-4o-mini"
        else:
            return "gpt-4o"

    return "gpt-4o"

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
    "document", "handbook", "manual", "report",
    
    "leave", "vacation", "holiday", "sick", "benefit", "benefits",
    "employee", "employees", "hr", "human resource",
    "salary", "compensation", "appraisal", "performance",

    "rule", "rules", "regulation", "compliance", "code of conduct",
    "onboarding", "training", "termination", "resignation",
]

def classify_question(question: str) -> str:

    question_lower = question.lower().strip()

    sql_score = sum(1 for kw in SQL_KEYWORDS if kw in question_lower)
    rag_score = sum(1 for kw in RAG_KEYWORDS if kw in question_lower)

    print(f"\nRouter scores — SQL: {sql_score} | RAG: {rag_score}")

    if sql_score == 0 and rag_score == 0:
        return "unknown"

    if sql_score > rag_score:
        return "sql"

    if rag_score > sql_score:
        return "rag"

    return "sql"

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

def route_question(question: str) -> dict:
    
    if not question or not question.strip():
        return {
            "answer": "Please ask a question.",
            "source_type": "none",
            "sources": []
        }

    route = classify_question(question)
    model = choose_model(route, question)
    print(f"Model selected: {model}")
    print(f"Router decision: {route.upper()}")

    if route in ("sql", "unknown"):
        try:
            print("Routing to: SQL Agent")
            answer = run_agent(question, model=model)
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

            result = get_rag_response(question, vectordb, model=model)
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
        "Show me top 5 products by price",       #
        "What is the leave policy?",              
        "How many customers do we have?",         
        "What are the employee benefits?",        
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