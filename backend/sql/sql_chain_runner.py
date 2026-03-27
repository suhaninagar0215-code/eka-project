import re
from backend.llm.llm_provider import get_llm
from backend.sql.sql_chain import get_sql_database
from sqlalchemy import text

print("LLM:", get_llm)
print("DB:", get_sql_database)

def clean_sql(response: str) -> str:
    response = re.sub(r"```sql", "", response, flags=re.IGNORECASE)
    response = re.sub(r"```", "", response)

    response = response.strip()

    return response

def run_sql_query(question: str):

    print("Initializing...")
    llm = get_llm()
    db = get_sql_database()

    print("Fetching schema...")
    schema = db.get_table_info(
        table_names=["employees", "departments", "salaries", "job_history"]
    )

    prompt = f"""
You are an expert SQL developer working with an enterprise HR database.

DATABASE TABLES:
- employees(id, first_name, last_name, department_id, hire_date, salary)
- departments(id, department_name)
- salaries(id, employee_id, salary, effective_date)
- job_history(id, employee_id, department_id, start_date, end_date)

RULES:
- Use only these tables
- Use proper JOINs
- Use TOP instead of LIMIT
- Do NOT use SELECT *
- Only return raw SQL query
- No explanations
- employees.id joins with salaries.employee_id
- employees.id = salaries.employee_id
- employees.department_id = departments.id

LOGIC:
- Latest salary → MAX(effective_date)
- Current department → WHERE end_date IS NULL

Question:
{question}
"""
    print("Sending to LLM...")
    response = llm.invoke(prompt).content

    sql_query = clean_sql(response)

    print("\n Generated SQL:\n", sql_query)

    try:
        with db._engine.connect() as connection:
            result = connection.execute(text(sql_query))
            rows = result.fetchall()

            cleaned_result = [tuple(row) for row in rows]

            return cleaned_result

    except Exception as e:
        print("SQL Execution Error:", e)

        if "syntax" in str(e).lower():
            return "SQL syntax error. Try rephrasing your question."

        return f"Error: {str(e)}"