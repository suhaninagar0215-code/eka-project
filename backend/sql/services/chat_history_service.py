from backend.sql.model.chat_history_model import ChatHistory
from backend.sql.sql_database import SessionLocal

def save_message(username, role, message):  # no session parameter
    db = SessionLocal()
    try:
        chat = ChatHistory(
            username=username,
            role=role,
            message=message
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
    except Exception as e:
        db.rollback()
        print(f"Error saving message: {e}")
    finally:
        db.close()


def load_chat_history(username):  # no session parameter
    db = SessionLocal()
    try:
        chats = db.query(ChatHistory)\
            .filter(ChatHistory.username == username)\
            .order_by(ChatHistory.timestamp)\
            .all()
        return chats
    except Exception as e:
        print(f"Error loading history: {e}")
        return []
    finally:
        db.close()