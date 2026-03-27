import warnings
warnings.filterwarnings("ignore")

from backend.agent.sql_agent import get_sql_agent
from backend.sql.sql_chain import run_sql_chain

_agent = None

def get_agent(model: str):
    global _agent
    if _agent is None:
        _agent = get_sql_agent(model)
    return _agent

def run_agent(question: str, model: str = "gpt-4o") -> str:
    try:
        agent = get_agent(model)
        result = agent.invoke({"input": question})
        return result.get("output", "No answer returned.")

    except Exception as agent_error:
        print(f"Agent failed: {type(agent_error).__name__}: {agent_error}")
        print("Falling back to direct SQL chain...")

        try:
            return run_sql_chain(question)
        except Exception as chain_error:
            return f"Both agent and chain failed.\nAgent error: {agent_error}\nChain error: {chain_error}"

if __name__ == "__main__":
    questions = [
        "Show top 5 highest paid employees",
        "Which department has most employees?",
        "Show current department of all employees",
        "Who has highest salary?",
        "List employees hired after 2021"
    ]
    for q in questions:
        print(f"\nQ: {q}")
        print(f"A: {run_agent(q)}")