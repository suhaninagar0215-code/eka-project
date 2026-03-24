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
           
            return f"QUERY_ERROR: {str(e)}. Check table names and column names and retry."

    return Tool(
        name="sql_db_query",
        func=run,
        description=(
            "Execute a SQL SELECT query against the SalesLT database. "
            "Input must be a raw SQL query with NO markdown, NO backticks. "
            "Only SELECT queries are allowed. "
            "Always qualify table names: SalesLT.TableName. "
            "Use TOP instead of LIMIT. "
            "Never select: ThumbNailPhoto, rowguid, ModifiedDate, ThumbnailPhotoFileName."
        )
    )

SYSTEM_PROMPT = """You are an expert SQL Agent for an Enterprise Knowledge Assistant.
You work with Microsoft SQL Server, SalesLT schema (AdventureWorks database).

YOUR JOB:
- Understand the user's question
- Use available tools to explore the schema if needed
- Write correct, optimized SQL
- Return the query results clearly

STRICT SQL RULES:
- Only SELECT queries allowed
- Always prefix tables: SalesLT.TableName
- Use TOP N instead of LIMIT N (this is SQL Server, not MySQL)
- Never select binary/blob columns: ThumbNailPhoto, rowguid, ModifiedDate, ThumbnailPhotoFileName
- For JOINs, always use explicit JOIN syntax, never implicit comma joins

TOOL USAGE RULES:
- Use sql_db_list_tables FIRST if you are unsure which tables exist
- Use sql_db_schema to inspect specific table columns before writing SQL
- Use sql_db_query to execute your final SQL
- If sql_db_query returns QUERY_ERROR, read the error, fix the SQL, and retry
- If sql_db_query returns QUERY_BLOCKED, rewrite without the forbidden keyword
- Never give up after one error — always attempt self-correction

RESPONSE FORMAT:
- After getting results, present them clearly
- Include the row count
- Do not expose raw SQL to the user in the final answer
- Do not say "listed above" — always repeat the actual results
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
    result = agent.invoke({"input": "Show me the top 5 products by list price"})
    print("\nFINAL ANSWER:\n", result.get("output", "No output"))