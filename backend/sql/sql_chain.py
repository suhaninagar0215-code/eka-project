from langchain_community.utilities import SQLDatabase
from backend.sql.sql_database import get_db_engine
from backend.llm.llm_provider import get_llm
from sqlalchemy import text
import re


def get_sql_database():
    engine = get_db_engine()

    db = SQLDatabase(
        engine,
        schema="SalesLT",
    )

    return db

def clean_sql(query: str) -> str:
    query = re.sub(r"```sql", "", query, flags=re.IGNORECASE)
    query = re.sub(r"```", "", query)
    return query.strip()

def validate_sql(query: str):
    forbidden = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER"]

    for word in forbidden:
        if word in query.upper():
            raise ValueError(f"Unsafe query detected: {word}")

    return query

def run_query_with_retry(query, db, retries=2):
    engine = get_db_engine()
    for attempt in range(retries):
        try:
            result = engine.connect().execute(text(query))

            rows = result.fetchall()

            return rows

        except Exception as e:
            if attempt == retries - 1:
                raise e

def format_result(result):
    if not result:
        return "No results found."

    result_str = str(result)

    result_str = result_str.replace("Decimal(", "").replace(")", "")
    result_str = result_str.replace("datetime.datetime", "")
    result_str = result_str.replace("'", "")

    return result_str

def run_sql_chain(question: str):
    llm = get_llm()
    db = get_sql_database()

    schema = db.get_table_info()

    prompt = f"""
You are a SQL expert.

Schema:
{schema}

Rules:
- Only generate SELECT queries
- Do NOT use DELETE, UPDATE, INSERT, DROP
- Return ONLY SQL (no explanation)

Question:
{question}
"""

    response = llm.invoke(prompt)
    raw_sql = response.content

    print("\nRAW SQL:\n", raw_sql)

    cleaned_sql = clean_sql(raw_sql)
    print("\nCLEANED SQL:\n", cleaned_sql)

    validated_sql = validate_sql(cleaned_sql)

    result = run_query_with_retry(validated_sql, db)

    formatted_result = format_result(result)

    return formatted_result