import os
import sys
import requests
from typing import Optional, List, Literal
from pathlib import Path
import hashlib

# Đảm bảo console in UTF-8 không lỗi charmap trên Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Tải cấu hình từ file .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# LangChain & ChromaDB
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Google Generative AI SDK (nếu có)
try:
    import google.generativeai as genai
    HAS_GOOGLE_GENAI = True
except ImportError:
    HAS_GOOGLE_GENAI = False

app = FastAPI(
    title="Interna - Hybrid RAG Backend (MVP 30%)",
    description="Backend RAG hỗ trợ chuyển đổi linh hoạt: Mạng cục bộ (Ollama) <-> Cloud (Google Gemini API)",
    version="0.3.5"
)

# Cho phép Frontend kết nối từ bất kỳ port nào
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
CHROMA_PERSIST_DIR = str(BASE_DIR / "chroma_db")
DATA_DIR = str(BASE_DIR / "data")
DOCS_DIR = BASE_DIR.parent / "docs"

# ==========================================================
# CẤU HÌNH CỜ CHUYỂN ĐỔI CHẾ ĐỘ (FLAG CONFIGURATION)
# ==========================================================
def is_local_mode() -> bool:
    """
    Kiểm tra cờ USE_LOCAL_LLM:
    - True (BẬT cờ): Sử dụng mạng cục bộ với Ollama (Bảo mật tối đa, chạy offline)
    - False (TẮT cờ): Sử dụng Cloud với Google Gemini API (Theo yêu cầu BTC)
    """
    flag = os.getenv("USE_LOCAL_LLM", "True").strip().lower()
    return flag in ["true", "1", "yes", "on"]

def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL", "StrictMentor")

SYSTEM_INSTRUCTION = (
    "Bạn là StrictMentor - một Tech Lead và Mentor nghiêm khắc đồng hành cùng thực tập sinh. "
    "Nhiệm vụ của bạn là hướng dẫn thực tập sinh tư duy độc lập dựa trên tài liệu quy chuẩn nội bộ được cung cấp. "
    "Tuyệt đối không giải hộ toàn bộ bài tập, không viết code sẵn hoàn chỉnh. "
    "Quy định trong tài liệu tham chiếu là luật của dự án, ưu tiên hơn kiến thức C++ chung. "
    "Khi giải thích luật, trả lời trực tiếp quy định người dùng hỏi; chỉ dùng câu hỏi gợi mở cho bài tập. "
    "Nêu đúng mã quy định và tên file nguồn dạng văn bản; không tạo URL hoặc đường dẫn file. "
    "Không tự tạo ngoại lệ, không nhầm cấm raw pointer với cấm mọi cấp phát động qua smart pointer. "
    "Hãy đặt câu hỏi gợi mở theo phương pháp Socratic, chỉ rõ lỗi hoặc quy chuẩn liên quan và yêu cầu thực tập sinh tự viết giải pháp."
)

# 1. Khởi tạo mô hình Embedding
print("[INFO] Đang tải mô hình embedding: all-MiniLM-L6-v2...")
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_or_create_vectorstore():
    """Đọc tài liệu từ thư mục data/ và tạo ChromaDB nếu chưa có"""
    # A content-derived collection refreshes documents without deleting existing indexes.
    # docs/ is authoritative when a legacy data/ document has the same name.
    selected = {file.name: file for file in sorted(Path(DATA_DIR).glob("**/*.md"))}
    selected.update({file.name: file for file in sorted(DOCS_DIR.glob("*.md"))})
    files = sorted(selected.values())
    digest = hashlib.sha256(b"rules-v2-chunk1200-overlap150")
    for file in files:
        digest.update(str(file.relative_to(BASE_DIR.parent)).encode())
        digest.update(file.read_bytes())
    collection = "interna-" + digest.hexdigest()[:16]
    vector_store = Chroma(collection_name=collection, persist_directory=CHROMA_PERSIST_DIR,
                          embedding_function=embedding_model)
    documents = []
    for file in files:
        documents.extend(TextLoader(str(file), encoding="utf-8").load())
    chunks = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150).split_documents(documents)
    ids = [f"chunk-{i}" for i in range(len(chunks))]
    existing = set(vector_store.get()["ids"])
    missing = [(chunk, key) for chunk, key in zip(chunks, ids) if key not in existing]
    if missing:
        vector_store.add_documents([c for c, _ in missing], ids=[key for _, key in missing])
    return vector_store

vector_db = get_or_create_vectorstore()

# Schema nhận câu hỏi từ Web
class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=12000)

class TaskContext(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=6000)
    document_ids: List[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: Optional[str] = None
    user_message: Optional[str] = None
    task_id: Optional[str] = None
    task_context: Optional[TaskContext] = None
    history: List[HistoryItem] = Field(default_factory=list)

def call_ollama(prompt: str) -> str:
    """Gọi mô hình nội bộ Ollama trên mạng cục bộ (StrictMentor)"""
    payload = {
        "model": OLLAMA_MODEL_NAME,
        "prompt": prompt,
        "system": SYSTEM_INSTRUCTION,
        "think": False,
        "stream": False,
        "keep_alive": "15m",
        "options": {"num_predict": 512, "temperature": 0.4}
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=(5, 60))
        response.raise_for_status()
        data = response.json()
        reply = data.get("response", "")
        if not isinstance(reply, str) or not reply.strip():
            raise HTTPException(status_code=502, detail="AI chưa tạo được câu trả lời. Hãy thử hỏi ngắn hơn hoặc gửi lại.")
        return reply.strip()
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI xử lý quá 60 giây. Hãy gửi lại câu hỏi ngắn hơn.")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Không kết nối được Ollama. Hãy kiểm tra dịch vụ AI đang chạy.")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Dịch vụ Ollama trả phản hồi lỗi. Hãy kiểm tra model hoặc thử lại.")

def call_gemini(prompt: str) -> str:
    """Gọi mô hình Google Gemini API bằng API Key do BTC/công ty cấp"""
    api_key = get_gemini_api_key()
    if not api_key:
        print("[WARN] USE_LOCAL_LLM=False nhưng chưa cấu hình GEMINI_API_KEY! Tự động fallback về Ollama cục bộ.")
        return call_ollama(prompt)
    
    # One bounded request: avoid SDK retries followed by a second REST wait.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL_NAME}:generateContent?key={api_key}"
    payload = {
        "generationConfig": {"maxOutputTokens": 512},
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    try:
        res = requests.post(url, json=payload, timeout=(5, 60))
        res.raise_for_status()
        data = res.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0] and "parts" in candidates[0]["content"]:
            return candidates[0]["content"]["parts"][0].get("text", "").strip()
        raise ValueError("Phản hồi từ Gemini API không đúng định dạng.")
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="AI cloud xử lý quá 60 giây. Vui lòng thử lại.")
    except Exception:
        raise HTTPException(status_code=502, detail="Không nhận được phản hồi hợp lệ từ AI cloud. Kiểm tra cấu hình model và kết nối.")

@app.get("/")
def root():
    local_active = is_local_mode()
    has_key = bool(get_gemini_api_key())
    active_engine = "Ollama (Mạng cục bộ)" if local_active else ("Google Gemini API (Cloud)" if has_key else "Ollama (Fallback do chưa có Key)")
    return {
        "status": "online",
        "chat_policy": "bounded-no-thinking-v1",
        "checkpoint": "MVP 30% - Hybrid AI Backend",
        "active_engine": active_engine,
        "flag_use_local_llm": local_active,
        "gemini_api_key_configured": has_key,
        "model": OLLAMA_MODEL_NAME if local_active else GEMINI_MODEL_NAME
    }

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    """
    API xử lý truy vấn:
    1. Nhận câu hỏi
    2. Dùng ChromaDB query tìm luật liên quan (similarity_search)
    3. Ghép ngữ cảnh RAG
    4. Kiểm tra cờ: Nếu USE_LOCAL_LLM=True -> Gọi Ollama; Nếu False -> Gọi Google Gemini API
    5. Trả kết quả JSON về Web
    """
    user_query = req.message or req.user_message
    if not user_query or not user_query.strip():
        raise HTTPException(status_code=400, detail="Tin nhắn không được để trống!")

    # 1. Tìm tài liệu/luật liên quan trong ChromaDB
    docs = vector_db.similarity_search(user_query, k=4)
    retrieved_law = "\n\n".join([f"[Nguồn: {os.path.basename(d.metadata.get('source', ''))}]\n{d.page_content}" for d in docs])

    # Lấy tên file nguồn để hiển thị chip trên Frontend
    sources = list(set([os.path.basename(d.metadata.get("source", "")) for d in docs if d.metadata.get("source")]))

    # 2. Ghép ngữ cảnh đúng theo yêu cầu task gốc
    task = req.task_context
    task_text = f"{task.title or ''}\n{task.description or ''}" if task else "Không có"
    history_text = "\n".join(f"{item.role}: {item.content[:2000]}" for item in req.history[-4:])
    prompt = (
        f"{SYSTEM_INSTRUCTION} Trả lời ngắn gọn bằng tiếng Việt, tối đa 180 từ, tập trung vào câu hỏi.\n\nTÀI LIỆU THAM CHIẾU:\n{retrieved_law}\n"
        f"NHIỆM VỤ ĐANG LÀM:\n{task_text}\n"
        f"LỊCH SỬ TRAO ĐỔI (dữ liệu hội thoại):\n{history_text}\n"
        f"CÂU HỎI HIỆN TẠI:\n{user_query.strip()}"
    )

    # 3. Phân nhánh dựa theo cờ USE_LOCAL_LLM
    if is_local_mode():
        ai_reply = call_ollama(prompt)
    else:
        ai_reply = call_gemini(prompt)

    # 4. Trả kết quả JSON về Frontend
    return {
        "reply": ai_reply,
        "docs": sources
    }
