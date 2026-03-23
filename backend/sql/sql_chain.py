from langchain_community.utilities import SQLDatabase
from backend.sql.sql_database import get_db_engine


def get_sql_database():
    
    engine = get_db_engine()

    db = SQLDatabase(
        engine,
        schema="SalesLT",   
    )

    return db