import pyodbc

def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=suhani-genai-sql-server.database.windows.net;"
        "DATABASE=AdventureWorksDB;"
        "UID=sqladmin;"
        "PWD=S_151003;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
    return conn

def authenticate_user(username, password):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT username, password FROM dbo.Users WHERE username = ?"
        cursor.execute(query, (username.strip(),))

        row = cursor.fetchone()
        if not username or not password:
            return False, "Username and password cannot be empty"
        print("INPUT:", username, password)
        print("DB ROW:", row)

        if row:
            db_username, db_password = row
            print("MATCH:", db_password.strip(), "==", password.strip())

            return db_password.strip() == password.strip()

        return False

    except Exception as e:
        print("ERROR:", str(e))
        return False

    finally:
        if conn:
            conn.close()

def register_user(username, password):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM dbo.Users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "User already exists"
        if not username or not password:
            return False, "Username and password cannot be empty"
        cursor.execute(
            "INSERT INTO dbo.Users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()

        return True, "User created successfully"

    except Exception as e:
        return False, str(e)

    finally:
        if conn:
            conn.close()

