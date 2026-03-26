from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.sql.base import Base

class ChatHistory(Base):

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, nullable=False)

    role = Column(String, nullable=False)

    message = Column(Text, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)