from backend.sql.sql_database import get_db_engine

def test_connection():
    try:
        engine = get_db_engine()
        with engine.connect() as conn:
            print(" Connected to database successfully!")

    except Exception as e:
        print(" Connection failed:")
        print(e)


if __name__ == "__main__":
    test_connection()