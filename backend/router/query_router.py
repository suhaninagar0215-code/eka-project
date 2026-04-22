import warnings
warnings.filterwarnings("ignore")

from backend.agent.agent_runner import run_agent
from backend.rag.rag_chain import get_rag_response
from backend.rag.vector_store import load_vector_store
from backend.llm.llm_provider import get_mini_llm


SQL_KEYWORDS = [
    "employee", "employees",
    "salary", "salaries",
    "department", "departments",
    "job", "history",
    "hire", "joining",
    "top", "highest", "lowest",
    "count", "average", "sum",
    "list", "show", "find", "get",
    "which", "who"
]

RAG_KEYWORDS = [
    "policy", "policies", "procedure", "guideline",
    "document", "handbook", "manual",
    "leave", "vacation", "holiday", "sick",
    "benefit", "benefits",
    "hr", "human resource",
    "rule", "rules", "compliance",
    "onboarding", "training", "termination",
    "resignation",
    "bonus", "incentive",
    "insurance", "medical",
    "working hours", "overtime",
    "dress code", "ethics",
    "promotion", "increment",
    "does the company",
    # Internship-specific additions
    "internship", "intern", "interns",
    "stipend",
    "internship duration", "internship period",
    "internship certificate", "completion certificate",
    "internship completion",
    "mentor", "supervisor",
    "on-site", "onsite",
    "apprentice", "trainee",
    "learning outcome", "learning objectives",
    "internship schedule",
    "internship policy",
    "internship agreement",
    "internship termination",
    "internship extension",
    "educational", "skill development",
    "employment consideration",
    "guaranteed employment",
    "internship working hours",
    "internship leave",
    "internship conduct",
    "data protection training",
    "internship eligibility",
    "can i get a job", "job after internship"
]


# Keyword Router 
def keyword_classify(question: str) -> str:
    
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
    try:
        llm = get_mini_llm()

        prompt = f"""You are a query router for an Enterprise Knowledge Assistant.

DATA SOURCES:

1. SQL DATABASE — contains structured HR data:
   - employees (name, department, salary, hire date)
   - departments
   - salaries (history)
   - job_history
   Use SQL for:
   - employee data
   - salary queries
   - department queries
   - counts, lists, aggregations

2. DOCUMENT KNOWLEDGE BASE — contains HR policies:
   - leave policy
   - benefits
   - company rules
   - HR guidelines
   - internship policy
   Use RAG for:
   - policy questions
   - HR rules
   - benefits explanation
   - internship questions
RULE:
- If question involves data (employees, salary, department) → SQL
- If question involves policy or explanation → RAG

Reply ONLY: SQL or RAG

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
    question_lower = question.lower().strip()

    if any(word in question_lower for word in ["employee", "salary", "department"]):
        print("Rule-based override → SQL")
        return "sql"

    sql_score = sum(1 for kw in SQL_KEYWORDS if kw in question_lower)
    rag_score = sum(1 for kw in RAG_KEYWORDS if kw in question_lower)

    print(f"Keyword scores — SQL: {sql_score} | RAG: {rag_score}")

    if sql_score > rag_score:
        print("Keyword decision → SQL")
        return "sql"

    if rag_score > sql_score:
        print("Keyword decision → RAG")
        return "rag"

    print("Ambiguous or no keywords — using LLM router...")
    return llm_classify(question)


def choose_model(route: str, question: str) -> str:

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
def route_question(question: str, username: str = "default_user") -> dict:

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
        "Show top 5 highest paid employees",
        "Which department has most employees?",
        "Show current department of all employees",
        "Who has highest salary?",
        "List employees hired after 2021"            
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