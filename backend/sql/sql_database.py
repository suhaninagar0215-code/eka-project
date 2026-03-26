from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import text
import os
from dotenv import load_dotenv
from pathlib import Path
import warnings
from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import sessionmaker
from backend.sql.base import Base

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

_engine = None

def get_db_engine():
    global _engine
    if _engine is not None:
        return _engine

    warnings.filterwarnings(
        "ignore",
        category=sa_exc.SAWarning,
        message=".*Did not recognize type.*"
    )

    connection_url = URL.create(
        drivername="mssql+pyodbc",
        username=os.getenv("SQL_USERNAME"),
        password=os.getenv("SQL_PASSWORD"),
        host=os.getenv("SQL_SERVER"),
        port=1433,
        database=os.getenv("SQL_DATABASE"),
        query={
            "driver": "ODBC Driver 17 for SQL Server",
            "TrustServerCertificate": "yes",
        }
    )

    _engine = create_engine(
        connection_url,
        pool_size=5,          
        max_overflow=10,       
        pool_timeout=30,      
        pool_recycle=1800,     
        pool_pre_ping=True,    
    )

    return _engine

def init_db():
    from backend.sql.model.chat_history_model import ChatHistory
    Base.metadata.create_all(bind=get_db_engine())

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=get_db_engine()
)

def get_db_session():
    return SessionLocal()

def test_connection():
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("DB connection successful:", result.fetchone())
    except Exception as e:
        print("DB connection failed:", str(e))


if __name__ == "__main__":
    init_db()
    test_connection()