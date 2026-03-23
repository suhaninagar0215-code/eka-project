from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def get_db_engine():
    
    username = os.getenv("SQL_USERNAME")
    password = os.getenv("SQL_PASSWORD")
    server = os.getenv("SQL_SERVER")
    database = os.getenv("SQL_DATABASE")

    connection_string = (
        f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )

    engine = create_engine(connection_string)

    return engine