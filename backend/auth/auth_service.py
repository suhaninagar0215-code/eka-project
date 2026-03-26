import pyodbc
import os
import bcrypt  

def get_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USERNAME')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"Connection Timeout=30;"
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

        if row:
            db_username, db_hashed_password = row
            if bcrypt.checkpw(password.strip().encode("utf-8"), db_hashed_password.strip().encode("utf-8")):
                return True, "Login successful"
            else:
                return False, "Invalid password"

        return False, "User not found"

    except Exception as e:
        print("ERROR:", str(e))
        return False, str(e)

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

        hashed_password = bcrypt.hashpw(password.strip().encode("utf-8"), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO dbo.Users (username, password) VALUES (?, ?)",
            (username.strip(), hashed_password.decode("utf-8"))
        )
        conn.commit()
        return True, "User created successfully"

    except Exception as e:
        return False, str(e)

    finally:
        if conn:
            conn.close()