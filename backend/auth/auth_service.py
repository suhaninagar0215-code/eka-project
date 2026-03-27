import bcrypt
from sqlalchemy import text
from backend.sql.sql_database import get_db_session


def authenticate_user(username, password):

    if not username or not password:
        return False, "Username and password cannot be empty"

    session = get_db_session()

    try:
        result = session.execute(
            text("SELECT password FROM dbo.Users WHERE username = :username"),
            {"username": username.strip()}
        ).fetchone()

        if not result:
            return False, "User not found"

        stored_password = result[0]

        if bcrypt.checkpw(
            password.strip().encode("utf-8"),
            stored_password.encode("utf-8")
        ):
            return True, "Login successful"

        return False, "Invalid password"

    except Exception as e:
        print("ERROR:", str(e))
        return False, str(e)

    finally:
        session.close()


def register_user(username, password):

    if not username or not password:
        return False, "Username and password cannot be empty"

    session = get_db_session()

    try:
        existing_user = session.execute(
            text("SELECT username FROM dbo.Users WHERE username = :username"),
            {"username": username.strip()}
        ).fetchone()

        if existing_user:
            return False, "User already exists"

        hashed_password = bcrypt.hashpw(
            password.strip().encode("utf-8"),
            bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

        session.execute(
            text("""
                INSERT INTO dbo.Users (username, password)
                VALUES (:username, :password)
            """),
            {
                "username": username.strip(),
                "password": hashed_password
            }
        )

        session.commit()

        return True, "User created successfully"

    except Exception as e:
        session.rollback()
        return False, str(e)

    finally:
        session.close()