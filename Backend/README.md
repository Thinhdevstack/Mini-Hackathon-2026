# Interna - Backend (MVP 30% Checkpoint)

Hệ thống RAG Backend cơ bản phục vụ vòng Checkpoint 30% của cuộc thi Mini Hackathon 2026. Hỗ trợ **Kiến trúc Hybrid AI**: chuyển đổi linh hoạt giữa **Mạng cục bộ (Local Ollama)** và **Mạng Cloud (Google Gemini API)**.

---

## 🎯 Phạm vi chức năng (Mức độ hoàn thành 30%)
- [x] Khởi tạo FastAPI Server chuẩn REST API.
- [x] Luồng đọc và nhúng tài liệu quy chuẩn công ty vào ChromaDB (`all-MiniLM-L6-v2`).
- [x] Endpoint `POST /chat` tìm kiếm điều luật liên quan và sinh câu trả lời bám sát quy chuẩn.
- [x] **Cơ chế Hybrid Flag:** Chuyển đổi giữa Local Ollama (Bảo mật tối đa, 100% offline) và Google Gemini API (Theo yêu cầu BTC).
- [x] Tương thích kết nối với Frontend demo phân quyền Intern & Mentor.

---

## ⚙️ Cấu hình Chế độ Hybrid AI (`.env`)

Mở file `Backend/.env` để cấu hình cờ chuyển đổi:

### 1. Chế độ Mạng cục bộ (Offline Local - Bảo mật 100%)
Bật cờ:
```ini
USE_LOCAL_LLM=True
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=StrictMentor
```
👉 *Hệ thống chỉ chạy trong mạng nội bộ với Ollama, không gửi bất kỳ dữ liệu nào ra Internet.*

### 2. Chế độ Cloud (Google Gemini API - Tiêu chí kỹ thuật BTC)
Tắt cờ và điền API Key:
```ini
USE_LOCAL_LLM=False
GEMINI_API_KEY=AIzaSy... (Điền key do BTC hoặc Google Cloud cấp)
GEMINI_MODEL=gemini-1.5-flash
```
👉 *Hệ thống tự động sử dụng Google Gemini 1.5 Flash để suy luận tốc độ cao qua Cloud Credit.*

> **Lưu ý Fallback:** Nếu tắt cờ (`USE_LOCAL_LLM=False`) nhưng chưa kịp điền `GEMINI_API_KEY`, hệ thống sẽ tự động fallback an toàn về Ollama để không làm gián đoạn trải nghiệm của người dùng.

---

## 🚀 Khởi chạy Backend

```bash
# 1. Di chuyển vào thư mục Backend
cd Backend

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Khởi chạy server FastAPI
uvicorn main:app --reload --port 8000
```
- Endpoint kiểm tra trạng thái: `http://127.0.0.1:8000/`
- API Swagger Docs: `http://127.0.0.1:8000/docs`

---

## 🔮 Lộ trình phát triển các vòng tiếp theo (Roadmap)
- **Vòng 60%:** Đóng gói Dockerfile chuẩn và triển khai lên **Google Cloud Run**; Tích hợp Database PostgreSQL lưu trữ tập trung.
- **Vòng Chung kết (100%):** Mở rộng kiến trúc **Multi-Agent** (Code Review Agent, Mentor Evaluation Agent, Security Policy Auditor).
