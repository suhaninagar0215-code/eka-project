from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_core.prompts import PromptTemplate
from backend.llm.llm_provider import get_llm
from backend.sql.sql_chain import get_sql_database
from langchain_core.tools import Tool
import re


def clean_sql(query: str) -> str:
    query = re.sub(r"```sql", "", query, flags=re.IGNORECASE)
    query = re.sub(r"```", "", query)
    query = query.strip().strip('"').strip("'")  
    return query


def safe_query_tool(db):
    def run(query: str):
        cleaned_query = clean_sql(query)
        print("\n CLEANED SQL:", cleaned_query)
        return db.run(cleaned_query)

    return Tool(
        name="sql_db_query",
        func=run,
        description="Executes SQL queries safely"
    )


def get_sql_agent():
    try:
        llm = get_llm()
        print("LLM loaded")

        db = get_sql_database()
        print("DB connected")
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = []

        for tool in toolkit.get_tools():
            if "query_checker" in tool.name:
                continue
            if tool.name == "sql_db_query":
                continue
            tools.append(tool)

        tools.append(safe_query_tool(db))

        print("Tools ready")

        custom_prompt = PromptTemplate.from_template("""
        You are a SQL expert agent.

        STRICT RULES:
        - NEVER use ``` or markdown
        - ONLY return SQL in Action Input
        - NEVER explain SQL

        CRITICAL:
        - You MUST ALWAYS follow EXACTLY this format
        - Do NOT add any extra text before Final Answer

        FORMAT:

        Question: {question}

        Thought: step by step reasoning
        Action: sql_db_query
        Action Input: <SQL QUERY>

        Observation: <result>

        Final Answer:
        You MUST repeat the exact results from Observation.
        Do NOT summarize.
        Do NOT say "listed above".

        """)

        agent = create_sql_agent(
            llm=llm,
            db=db,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=20,
            early_stopping_method="force",
            agent_kwargs={"prompt": custom_prompt}
        )

        print("Agent created successfully")

        return agent

    except Exception as e:
        print("AGENT CREATION ERROR:", e)
        return None