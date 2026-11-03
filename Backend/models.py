import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Conversation(Base):
    """Bảng quản lý phiên trò chuyện của từng Thực tập sinh"""
    __tablename__ = "conversations"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    intern_id = Column(String(50), index=True, nullable=False) # ID hoặc Username của Thực tập sinh
    title = Column(String(200), default="Cuộc trò chuyện C++")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ 1-Nhiều với bảng Message
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    """Bảng lưu trữ lịch sử tin nhắn (hỏi - đáp)"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(50), ForeignKey("conversations.id"), index=True, nullable=False)
    sender = Column(String(20), nullable=False) # "user" (TTS) hoặc "assistant" (StrictMentor AI)
    content = Column(Text, nullable=False)
    retrieved_laws = Column(Text, default="")    # Điều luật C++ trích xuất từ RAG
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
    evaluations = relationship("MentorEvaluation", back_populates="message", cascade="all, delete-orphan")

class MentorEvaluation(Base):
    """Bảng lưu trữ báo cáo phân tích năng lực và đánh giá câu hỏi TTS dành cho Mentor"""
    __tablename__ = "mentor_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), index=True, nullable=False)
    intern_id = Column(String(50), index=True, nullable=False)
    question_content = Column(Text, default="")           # Câu hỏi cụ thể của TTS
    knowledge_gap = Column(String(255), default="")      # Lỗ hổng kiến thức C++
    security_risk = Column(String(50), default="LOW")    # Mức độ rủi ro: LOW / MEDIUM / CRITICAL
    mentor_recommendation = Column(Text, default="")     # Khuyến nghị hành động cho Mentor thật
    raw_analysis = Column(Text, default="")              # Bài phân tích chi tiết của AI
    is_reviewed = Column(Boolean, default=False)         # Mentor thật đã xem xét chưa
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="evaluations")
