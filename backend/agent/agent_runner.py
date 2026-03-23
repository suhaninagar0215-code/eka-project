from backend.sql.sql_chain import run_sql_chain

def run_agent(question: str):
    try:
        return run_sql_chain(question)
    except Exception as e:
        return f"Error: {str(e)}"