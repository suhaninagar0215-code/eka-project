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
        table_names=["Customer", "Product", "SalesOrderHeader", "SalesOrderDetail"]
    )

    prompt = f"""
    You are an expert SQL developer.

    Given the database schema below, write a SQL query.

    Rules:
    - Use only tables from the schema
    - Use correct table relationships
    - Limit results to TOP 5 unless specified
    - Do NOT use SELECT *
    - Avoid binary/image columns
    - Select only relevant columns
    - Use Microsoft SQL Server syntax
    - NEVER use ``` or markdown formatting
    - ONLY return plain SQL query
    - If unsure, make best logical assumption
    - Do not explain, only return SQL query
    - NEVER include ``` or ```sql in output
    - Return only raw SQL query

    Schema:
    {schema}

    Question:
    {question}
    """
    print("\n Cleaned SQL:\n", sql_query)
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