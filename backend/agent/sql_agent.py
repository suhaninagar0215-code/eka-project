from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_core.tools import Tool
from backend.llm.llm_provider import get_llm
from backend.llm.llm_provider import get_llm_by_name
from backend.sql.sql_chain import get_sql_database, clean_sql, validate_sql, run_query_with_retry, format_result
import re
import warnings
warnings.filterwarnings("ignore")

def safe_query_tool(db):
    def run(query: str) -> str:
        try:
            cleaned = clean_sql(query)
            validated = validate_sql(cleaned)
            result = run_query_with_retry(validated)
            return format_result(result)
        except ValueError as e:
            return f"QUERY_BLOCKED: {str(e)}. Rewrite the query using only SELECT."
        except Exception as e:
            return f"QUERY_ERROR: {str(e)}. Check table/column names and retry."

    return Tool(
        name="sql_db_query",
        func=run,
        description=(
            "Execute a SQL SELECT query against the enterprise database. "
            "Available tables: employees, departments, salaries, job_history. "
            "Use correct column names. "
            "Only SELECT queries allowed. "
            "Use TOP instead of LIMIT (SQL Server)."
        )
    )

SYSTEM_PROMPT = """
You are an expert SQL Agent for an Enterprise Knowledge Assistant.

DATABASE SCHEMA:

employees(id, first_name, last_name, department_id, hire_date, salary)
departments(id, department_name)
salaries(id, employee_id, salary, effective_date)
job_history(id, employee_id, department_id, start_date, end_date)

YOUR JOB:
- Understand the user's question
- Write correct SQL queries
- Use joins where required
- Return clear answers

STRICT RULES:
- Only SELECT queries allowed
- Use TOP instead of LIMIT (SQL Server)
- Use proper JOINs (no implicit joins)

LOGIC RULES:
- Latest salary → use MAX(effective_date)
- Current department → WHERE end_date IS NULL
- Always join employees with departments using department_id
- Use salaries table for salary-related queries
- If user asks about salary → use salaries table
- If user asks about department → use departments or job_history
- employees.id = salaries.employee_id
- employees.department_id = departments.id

TOOL USAGE:
- Use sql_db_query to execute queries
- If error occurs, fix and retry

FINAL OUTPUT:
- Show results clearly
- Include number of rows
- Do NOT show SQL query
"""

def get_sql_agent(model: str = "gpt-4o"):
    try:
        llm = get_llm_by_name(model)
        print("LLM loaded")

        db = get_sql_database()
        print("DB connected")

        agent = create_sql_agent(
            llm=llm,
            db=db,
            extra_tools=[safe_query_tool(db)],
            agent_type="openai-tools",
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,
            max_execution_time=60,
            agent_kwargs={
                "system_message": SYSTEM_PROMPT,
            }
        )

        print("Agent created successfully")
        return agent

    except Exception as e:
        print(f"AGENT CREATION ERROR: {type(e).__name__}: {e}")
        raise
     
if __name__ == "__main__":
    agent = get_sql_agent()
    result = agent.invoke({"input": "Show top 5 highest paid employees"})
    print("\nFINAL ANSWER:\n", result.get("output", "No output"))