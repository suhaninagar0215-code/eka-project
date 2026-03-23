from backend.sql.sql_chain import get_sql_database


def test_schema():
    try:
        db = get_sql_database()

        print("\n Tables in Database:")
        print(db.get_usable_table_names())

    except Exception as e:
        print(" Error:")
        print(e)


if __name__ == "__main__":
    test_schema()