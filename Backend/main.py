import os
import sys
import uuid
import requests
from datetime import datetime
from typing import Optional, List

# Đảm bảo console Windows in tiếng Việt UTF-8 không bị lỗi charmap/cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import cấu hình Database & Models
from database import engine, Base, get_db, SessionLocal
from models import Conversation, Message, MentorEvaluation

# LangChain & ChromaDB
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Tạo các bảng cơ sở dữ liệu nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="C++ Intern Mentorship & AI Evaluation Backend",
    description="Hệ thống RAG hỗ trợ Thực tập sinh C++ kèm AI phân tích năng lực cho Mentor",
    version="2.0.0"
)

# Cấu hình CORS để Web Frontend dễ dàng kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_PERSIST_DIR = "./chroma_db"
DATA_DIR = "./data"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "StrictMentor"

# 1. Khởi tạo mô hình Embedding
print("[INFO] Đang tải mô hình embedding: all-MiniLM-L6-v2...")
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_or_create_vectorstore():
    """Tạo hoặc nạp Chroma Vector DB từ các tài liệu trong data/"""
    if not os.path.exists(CHROMA_PERSIST_DIR) or len(os.listdir(CHROMA_PERSIST_DIR)) == 0:
        print("[INFO] Đang đọc tài liệu quy chuẩn từ 'data/'...")
        loader = DirectoryLoader(DATA_DIR, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
        documents = loader.load()
        print(f"[INFO] Đã đọc {len(documents)} tài liệu.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        print(f"[INFO] Đã chia thành {len(chunks)} chunks.")

        vector_store = Chroma.from_documents(chunks, embedding_model, persist_directory=CHROMA_PERSIST_DIR)
        print("[INFO] Đã khởi tạo ChromaDB thành công!")
        return vector_store
    else:
        print("[INFO] Nạp dữ liệu có sẵn từ ChromaDB...")
        return Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embedding_model)

vector_db = get_or_create_vectorstore()

# ================= PYDANTIC SCHEMAS =================
class ChatRequest(BaseModel):
    intern_id: str = "intern_01"                  # Định danh Thực tập sinh
    session_id: Optional[str] = None             # Mã phiên chat (UUID), nếu rỗng sẽ tự tạo mới
    message: Optional[str] = None
    user_message: Optional[str] = None

    def get_message(self) -> str:
        text = self.message or self.user_message
        if not text or not text.strip():
            raise ValueError("Tin nhắn không được để trống!")
        return text.strip()

# ================= TÁC VỤ ĐÁNH GIÁ NĂNG LỰC NGẦM CHO MENTOR =================
def background_evaluate_question(message_id: int, intern_id: str, question: str, ai_reply: str):
    """
    Luồng 2: Quăng câu hỏi của TTS lên AI một lần nữa để phân tích chuyên sâu
    về lỗ hổng kiến thức, rủi ro bảo mật và gợi ý cho Mentor thật.
    """
    eval_prompt = f"""Bạn là một Senior Tech Lead C++ đang đánh giá câu hỏi của Thực tập sinh (TTS).
Mã thực tập sinh: {intern_id}
Câu hỏi / Đoạn code TTS vừa hỏi:
"{question}"

Câu trả lời AI đã hướng dẫn TTS:
"{ai_reply}"

Hãy phân tích nhanh câu hỏi của TTS này theo 3 tiêu chí cốt lõi:
1. LỖ HỔNG KIẾN THỨC: TTS đang hổng mảng kiến thức C++ nào (ví dụ: Con trỏ & Quản lý bộ nhớ, Nguyên lý RAII, Chuẩn C++17, v.v.)?
2. MỨC ĐỘ RỦI RO: Đánh giá một trong ba mức [LOW / MEDIUM / CRITICAL] (CRITICAL nếu có nguy cơ lộ mật khẩu/SQL Injection; MEDIUM nếu có rò rỉ bộ nhớ/memory leak; LOW nếu chỉ là thắc mắc cú pháp thông thường).
3. ĐỀ XUẤT CHO MENTOR THẬT: Mentor thật nên giao bài tập gì hoặc nhắc nhở điều gì cho TTS này khi gặp mặt trực tiếp?

Hãy trả lời súc tích, theo định dạng mẫu:
Lỗ hổng: <tóm tắt ngắn gọn trong 1 câu>
Rủi ro: <LOW hoặc MEDIUM hoặc CRITICAL>
Đề xuất: <1-2 câu hành động cụ thể cho Mentor>"""

    payload = {
        "model": MODEL_NAME,
        "prompt": eval_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        raw_text = response.json().get("response", "").strip()

        # Phân tích nội dung trả về
        knowledge_gap = "Quản lý bộ nhớ & Con trỏ C++"
        security_risk = "LOW"
        recommendation = "Mentor nên kiểm tra hiểu biết của TTS về RAII."

        for line in raw_text.splitlines():
            line_clean = line.strip()
            if line_clean.lower().startswith("lỗ hổng:"):
                knowledge_gap = line_clean.split(":", 1)[1].strip()
            elif line_clean.lower().startswith("rủi ro:"):
                risk_part = line_clean.split(":", 1)[1].strip().upper()
                if "CRITICAL" in risk_part:
                    security_risk = "CRITICAL"
                elif "MEDIUM" in risk_part:
                    security_risk = "MEDIUM"
                else:
                    security_risk = "LOW"
            elif line_clean.lower().startswith("đề xuất:"):
                recommendation = line_clean.split(":", 1)[1].strip()

        # Lưu vào bảng MentorEvaluation
        db = SessionLocal()
        try:
            evaluation = MentorEvaluation(
                message_id=message_id,
                intern_id=intern_id,
                question_content=question,
                knowledge_gap=knowledge_gap,
                security_risk=security_risk,
                mentor_recommendation=recommendation,
                raw_analysis=raw_text,
                created_at=datetime.utcnow()
            )
            db.add(evaluation)
            db.commit()
            print(f"[INFO] Đã tạo đánh giá cho Mentor (Intern: {intern_id}, Rủi ro: {security_risk})")
        finally:
            db.close()

    except Exception as e:
        print(f"[ERROR] Lỗi khi AI đánh giá ngầm câu hỏi: {e}")

# ================= API ENDPOINTS =================

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "C++ Intern Mentorship & AI Evaluation Backend",
        "version": "2.0.0",
        "database": "SQLAlchemy (SQLite / MySQL ready)",
        "model": MODEL_NAME
    }

@app.post("/chat")
def chat_with_mentor(request: ChatRequest, bg_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    API gửi câu hỏi của Thực tập sinh:
    - Quản lý phiên chat (session_id) theo từng intern_id
    - Tự động lấy lịch sử hội thoại gần nhất làm bộ nhớ (Conversation Memory)
    - RAG tìm kiếm điều luật C++ trong ChromaDB
    - Gửi tới Ollama (StrictMentor) sinh phản hồi
    - Lưu vào CSDL
    - Tự động kích hoạt luồng đánh giá ngầm tạo báo cáo cho Mentor Dashboard
    """
    try:
        user_msg_text = request.get_message()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 1. Tìm hoặc tạo phiên trò chuyện (Conversation)
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        conversation = Conversation(id=session_id, intern_id=request.intern_id, title=user_msg_text[:50])
        db.add(conversation)
        db.commit()
    else:
        conversation = db.query(Conversation).filter(Conversation.id == session_id).first()
        if not conversation:
            conversation = Conversation(id=session_id, intern_id=request.intern_id, title=user_msg_text[:50])
            db.add(conversation)
            db.commit()

    # 2. Lấy bộ nhớ hội thoại (4 tin nhắn gần nhất trong phiên này)
    recent_messages = db.query(Message).filter(Message.conversation_id == session_id).order_by(Message.created_at.desc()).limit(4).all()
    recent_messages.reverse() # Đưa về thứ tự thời gian tăng dần
    
    chat_history_str = ""
    if recent_messages:
        history_lines = []
        for m in recent_messages:
            role = "Thực tập sinh" if m.sender == "user" else "Tech Lead"
            history_lines.append(f"{role}: {m.content}")
        chat_history_str = "\n".join(history_lines)

    # 3. RAG: Tìm kiếm điều luật C++ liên quan từ ChromaDB
    docs = vector_db.similarity_search(user_msg_text, k=2)
    retrieved_law = "\n\n".join([doc.page_content for doc in docs])

    # 4. Ghép ngữ cảnh hoàn chỉnh cho Tech Lead AI
    prompt_parts = []
    if retrieved_law:
        prompt_parts.append(f"--- ĐIỀU LUẬT & QUY CHUẨN NỘI BỘ LIÊN QUAN ---\n{retrieved_law}")
    if chat_history_str:
        prompt_parts.append(f"--- LỊCH SỬ TRAO ĐỔI TRƯỚC ĐÓ CỦA HAI ANH EM ---\n{chat_history_str}")
    
    prompt_parts.append(f"--- CÂU HỎI MỚI CỦA THỰC TẬP SINH ---\n{user_msg_text}")
    prompt_parts.append("\nHãy đóng vai Tech Lead hướng dẫn em ấy (gợi mở tư duy, không đưa code hoàn chỉnh, nhắc bảo mật, đề xuất mini-roadmap):")
    
    full_prompt = "\n\n".join(prompt_parts)

    # 5. Gửi tới Ollama API
    payload = {
        "model": MODEL_NAME,
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        ai_reply = response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Không thể kết nối đến Ollama. Vui lòng kiểm tra Ollama có đang chạy tại http://localhost:11434 không."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý với AI: {str(e)}")

    # 6. Lưu tin nhắn của TTS vào CSDL
    user_msg_record = Message(
        conversation_id=session_id,
        sender="user",
        content=user_msg_text,
        retrieved_laws=retrieved_law,
        created_at=datetime.utcnow()
    )
    db.add(user_msg_record)
    db.commit()
    db.refresh(user_msg_record)

    # 7. Lưu phản hồi của AI vào CSDL
    ai_msg_record = Message(
        conversation_id=session_id,
        sender="assistant",
        content=ai_reply,
        retrieved_laws="",
        created_at=datetime.utcnow()
    )
    db.add(ai_msg_record)
    db.commit()

    # 8. Kích hoạt luồng đánh giá ngầm của AI cho Mentor (Background Task)
    bg_tasks.add_task(background_evaluate_question, user_msg_record.id, request.intern_id, user_msg_text, ai_reply)

    # 9. Trả kết quả về cho TTS
    return {
        "session_id": session_id,
        "intern_id": request.intern_id,
        "reply": ai_reply,
        "retrieved_laws": retrieved_law
    }

@app.get("/history/{session_id}")
def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """API xem lại toàn bộ lịch sử trò chuyện của một phiên chat"""
    conversation = db.query(Conversation).filter(Conversation.id == session_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Không tìm thấy phiên chat này.")

    messages = db.query(Message).filter(Message.conversation_id == session_id).order_by(Message.created_at.asc()).all()
    return {
        "session_id": session_id,
        "intern_id": conversation.intern_id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": [
            {
                "id": m.id,
                "sender": m.sender,
                "content": m.content,
                "created_at": m.created_at
            }
            for m in messages
        ]
    }

@app.get("/mentor/dashboard")
def get_mentor_dashboard(db: Session = Depends(get_db)):
    """API dành cho Dashboard của Mentor / Tech Lead: thống kê và danh sách đánh giá mới nhất"""
    total_questions = db.query(Message).filter(Message.sender == "user").count()
    critical_risks = db.query(MentorEvaluation).filter(MentorEvaluation.security_risk == "CRITICAL").count()
    medium_risks = db.query(MentorEvaluation).filter(MentorEvaluation.security_risk == "MEDIUM").count()
    low_risks = db.query(MentorEvaluation).filter(MentorEvaluation.security_risk == "LOW").count()

    recent_evaluations = db.query(MentorEvaluation).order_by(MentorEvaluation.created_at.desc()).limit(15).all()

    return {
        "stats": {
            "total_questions_asked": total_questions,
            "critical_risks": critical_risks,
            "medium_risks": medium_risks,
            "low_risks": low_risks
        },
        "recent_evaluations": [
            {
                "id": ev.id,
                "intern_id": ev.intern_id,
                "question": ev.question_content,
                "knowledge_gap": ev.knowledge_gap,
                "security_risk": ev.security_risk,
                "mentor_recommendation": ev.mentor_recommendation,
                "is_reviewed": ev.is_reviewed,
                "created_at": ev.created_at
            }
            for ev in recent_evaluations
        ]
    }

@app.get("/mentor/evaluations/{intern_id}")
def get_intern_evaluations(intern_id: str, db: Session = Depends(get_db)):
    """Xem toàn bộ các đánh giá năng lực của 1 Thực tập sinh cụ thể"""
    evaluations = db.query(MentorEvaluation).filter(MentorEvaluation.intern_id == intern_id).order_by(MentorEvaluation.created_at.desc()).all()
    return {
        "intern_id": intern_id,
        "total_evaluations": len(evaluations),
        "evaluations": [
            {
                "id": ev.id,
                "question": ev.question_content,
                "knowledge_gap": ev.knowledge_gap,
                "security_risk": ev.security_risk,
                "mentor_recommendation": ev.mentor_recommendation,
                "raw_analysis": ev.raw_analysis,
                "is_reviewed": ev.is_reviewed,
                "created_at": ev.created_at
            }
            for ev in evaluations
        ]
    }

@app.patch("/mentor/evaluations/{eval_id}/read")
def mark_evaluation_reviewed(eval_id: int, db: Session = Depends(get_db)):
    """Đánh dấu Mentor đã xem xét báo cáo đánh giá này"""
    evaluation = db.query(MentorEvaluation).filter(MentorEvaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Không tìm thấy đánh giá.")
    
    evaluation.is_reviewed = True
    db.commit()
    return {"status": "success", "message": f"Đã đánh dấu đánh giá #{eval_id} là đã xem."}
