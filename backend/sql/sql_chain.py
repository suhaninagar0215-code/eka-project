from langchain_community.utilities import SQLDatabase
from backend.sql.sql_database import get_db_engine
from backend.llm.llm_provider import get_llm
from sqlalchemy import text
import re

_db = None

def get_sql_database():
    global _db
    if _db is not None:
        return _db

    engine = get_db_engine()
    _db = SQLDatabase(
        engine,
        schema="SalesLT",
        sample_rows_in_table_info=2,
        max_string_length=300,
        view_support=False,
    )
    return _db

def clean_sql(query: str) -> str:
    query = re.sub(r"```sql", "", query, flags=re.IGNORECASE)
    query = re.sub(r"```", "", query)
    query = query.strip().strip('"').strip("'")
    return query

FORBIDDEN_KEYWORDS = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "EXEC", "EXECUTE"]

def validate_sql(query: str) -> str:
    query_upper = query.upper()
    for word in FORBIDDEN_KEYWORDS:

        pattern = r'\b' + word + r'\b'
        if re.search(pattern, query_upper):
            raise ValueError(f"Unsafe query detected: '{word}' is not allowed.")
    return query


def run_query_with_retry(query: str, retries: int = 2) -> list:
    engine = get_db_engine()  

    last_error = None
    for attempt in range(retries):
        try:
           
            with engine.connect() as conn:
                result = conn.execute(text(query))
                rows = result.fetchall()
                columns = list(result.keys())  
                return {"columns": columns, "rows": rows}

        except Exception as e:
            last_error = e
            print(f"Query attempt {attempt + 1} failed: {str(e)}")

    raise RuntimeError(f"Query failed after {retries} attempts: {str(last_error)}")


def format_result(result: dict) -> str:
    if not result or not result["rows"]:
        return "No results found."

    columns = result["columns"]
    rows = result["rows"]

    skip_cols = set()
    for i, col in enumerate(columns):
        for row in rows[:2]: 
            val = row[i]
            if isinstance(val, (bytes, bytearray)):
                skip_cols.add(i)
                break

    display_cols = [col for i, col in enumerate(columns) if i not in skip_cols]

    lines = []
    lines.append(" | ".join(display_cols))
    lines.append("-" * (sum(len(c) for c in display_cols) + 3 * len(display_cols)))

    for row in rows:
        formatted_row = []
        for i, val in enumerate(row):
            if i in skip_cols:
                continue
            if val is None:
                formatted_row.append("NULL")
            else:
                formatted_row.append(str(val))
        lines.append(" | ".join(formatted_row))

    lines.append(f"\n{len(rows)} row(s) returned.")
    return "\n".join(lines)

def run_sql_chain(question: str) -> str:
    llm = get_llm()
    db = get_sql_database()

    schema = db.get_table_info()

    prompt = f"""
You are a SQL expert working with Microsoft SQL Server (SalesLT schema).

DATABASE SCHEMA:
{schema}

STRICT RULES:
- Only generate SELECT queries
- Never use DELETE, UPDATE, INSERT, DROP, TRUNCATE, EXEC
- Return ONLY the SQL query — no explanation, no markdown, no backticks
- Always qualify table names with schema: SalesLT.TableName
- Use TOP instead of LIMIT for SQL Server
- NEVER select these columns under any circumstance: ThumbNailPhoto, rowguid, ModifiedDate, ThumbnailPhotoFileName
- Always include the Name column when selecting from Product table
- If user asks for "all columns" or uses *, explicitly list all columns EXCEPT the banned ones above

Question: {question}

SQL Query:
"""

    response = llm.invoke(prompt)
    raw_sql = response.content

    print("\n--- RAW SQL ---\n", raw_sql)

    cleaned_sql = clean_sql(raw_sql)
    print("\n--- CLEANED SQL ---\n", cleaned_sql)

    validated_sql = validate_sql(cleaned_sql)

    result = run_query_with_retry(validated_sql)

    formatted = format_result(result)
    print("\n--- RESULT ---\n", formatted)

    return formatted

if __name__ == "__main__":
    output = run_sql_chain("Show me the top 5 customers by total order amount")
    print(output)