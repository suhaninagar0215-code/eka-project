from backend.agent.sql_agent import get_sql_agent

def run_agent(question: str):
    try:
        agent = get_sql_agent()
        response = agent.invoke({"input": question})
        return response["output"]

    except Exception as e:
        print("RAW ERROR:", e)

        if "Could not parse LLM output" in str(e):
            return " Output formatting issue, but query likely succeeded. Check logs above."

        return f"Error : {str(e)}"