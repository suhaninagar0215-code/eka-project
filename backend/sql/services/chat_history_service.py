from backend.sql.model.chat_history_model import ChatHistory


def save_message(username, role, message, session):

    chat = ChatHistory(
        username=username,
        role=role,
        message=message
    )

    session.add(chat)
    session.commit()


def load_chat_history(username, session):

    chats = session.query(ChatHistory)\
        .filter(ChatHistory.username == username)\
        .order_by(ChatHistory.timestamp)\
        .all()

    return chats