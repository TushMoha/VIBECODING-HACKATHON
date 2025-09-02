from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ChatSession(Base):
    __tablename__ = "chatsession"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chatmessage"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chatsession.id"))
    role = Column(String)   # "user" or "bot"
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    session = relationship("ChatSession", back_populates="messages")
