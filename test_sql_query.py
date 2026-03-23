from backend.sql.sql_chain_runner import run_sql_query


if __name__ == "__main__":
    
    query = "product with highest price"

    result = run_sql_query(query)

    print(" Result:\n", result)