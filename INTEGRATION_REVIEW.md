# BÁO CÁO ĐỐI SOÁT VÀ PHƯƠNG ÁN TỐI ƯU KẾT HỢP FRONTEND - BACKEND
**Dự án:** Interna - Nền tảng Đồng hành & Đánh giá Thực tập sinh (Nova Tech)  
**Mục tiêu:** Rà soát tính tương thích, phát hiện xung đột và đề xuất giải pháp tối ưu kết nối giữa Frontend và Backend  
**Ngày thực hiện:** 03/11/2026  

---

## 1. TỔNG QUAN HIỆN TRẠNG KẾT NỐI

Sau khi rà soát toàn bộ mã nguồn của cả hai phần:
- **Frontend (`frontend/`):** Gồm `index.html`, `app.js`, `style.css`, `config.js` (giao diện hoàn chỉnh, hỗ trợ chuyển đổi giữa Thực tập sinh và Mentor).
- **Backend (`Backend/`):** Gồm `main.py`, `database.py`, `models.py`, `data/` (FastAPI, RAG ChromaDB, Ollama StrictMentor, SQLAlchemy).

---

## 2. BẢNG ĐỐI SOÁT CHI TIẾT (FRONTEND VS BACKEND)

| Hạng mục | Frontend gửi đi (`app.js`) | Backend mong đợi (`main.py`) | Đánh giá tính tương thích |
| :--- | :--- | :--- | :--- |
| **URL Gọi API** | `POST http://localhost:8000/chat` | `POST /chat` trên port 8000 | ✅ **Hoàn toàn khớp** |
| **Trường tin nhắn** | `message: "Mã thực tập sinh bị trùng thì sao?"` | `message` hoặc `user_message` | ✅ **Hoàn toàn khớp** |
| **Dữ liệu ngữ cảnh Task** | Gửi kèm:<br>- `task_id: "TSK-02"`<br>- `task_context: {title, description, document_ids}` | Chưa khai báo nhận `task_context` trong Pydantic | ⚠️ **Cần tối ưu:** Backend bỏ qua `task_context` quý giá mà Frontend gửi lên. |
| **Bộ nhớ hội thoại** | Gửi kèm mảng: `history: [{role, content}]` | Backend đang tự query DB cũ | ⚠️ **Cần tối ưu:** Backend nên ưu tiên nạp `history` trực tiếp từ Frontend để đảm bảo ngữ cảnh đồng nhất 100%. |
| **Response định dạng** | Kiểm tra: `typeof result.reply === "string"` | Trả về: `{"reply": "...", ...}` | ✅ **Hoàn toàn khớp** |
| **Tài liệu tham chiếu** | Nhận `result.docs` để hiển thị chip tài liệu | Backend trả về `retrieved_laws` | ⚠️ **Cần tối ưu:** Nên trả thêm trường `docs: ["intern_portal.md"]` để Frontend hiển thị tag. |
| **Cấu hình `mode`** | `config.js` đang để `mode: "demo"` | Backend đã sẵn sàng chạy thật | ⚠️ **Điểm nghẽn chính:** Nếu để `mode: "demo"`, Frontend sẽ tự mock dữ liệu trong trình duyệt mà **KHÔNG gọi Backend**. |
| **Màn hình Mentor** | Đang lấy dữ liệu từ `localStorage` | Backend đã có sẵn `GET /mentor/dashboard` | 💡 **Cơ hội nâng cấp:** Kết nối API Mentor để hiển thị đánh giá AI thật thay vì dữ liệu tĩnh. |

---

## 3. CÁC ĐIỂM XUNG ĐỘT TIỀM ẨN VÀ GIẢI PHÁP KHẮC PHỤC

### 🔴 Xung đột 1: `mode: "demo"` trong `frontend/config.js`
* **Vấn đề:** Trong file `frontend/config.js`, biến cấu hình đang là:
  ```javascript
  window.INTERNA_CONFIG = {
    mode: "demo", // "demo" hoặc "api"
    apiBaseUrl: "http://localhost:8000",
    chatPath: "/chat"
  };
  ```
  Nếu giữ nguyên `mode: "demo"`, trình duyệt sẽ dùng hàm `mockResponse()` nội bộ, hoàn toàn không gọi sang FastAPI Backend.
* **Giải pháp:** Đổi `mode: "api"` trong `frontend/config.js` khi chạy thật với Backend.

---

### 🟡 Xung đột 2: Payload ngữ cảnh Task giữa Frontend và Backend
* **Vấn đề:** Frontend gửi một gói tin rất giàu thông tin:
  ```json
  {
    "code": "",
    "message": "Mã thực tập sinh bị trùng thì sao?",
    "history": [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."}
    ],
    "task_id": "TSK-02",
    "task_context": {
      "title": "Đề xuất cấu trúc dữ liệu cho hồ sơ thực tập sinh",
      "description": "Từ yêu cầu nghiệp vụ...",
      "document_ids": ["requirements", "cpp"]
    }
  }
  ```
  Backend hiện tại trong `main.py` chỉ khai báo nhận `message`, `intern_id`, `session_id`, bỏ qua `task_context` và `history` của client.
* **Giải pháp:** Cập nhật Pydantic Model `ChatRequest` trong `Backend/main.py` để hứng trọn vẹn `code`, `history`, `task_id`, `task_context`. Đưa trực tiếp thông tin task vào Prompt gửi cho Ollama để câu trả lời của AI bám sát 100% nhiệm vụ TTS đang làm.

---

### 🟡 Xung đột 3: Định dạng trường danh sách tài liệu tham khảo
* **Vấn đề:** `frontend/app.js` (dòng 106 & 119) mong đợi danh sách các tài liệu tham khảo ở dạng `result.docs` (mảng string), ví dụ `["intern_portal.md", "testing_guide.md"]`. Backend hiện tại đang trả về chuỗi `retrieved_laws`.
* **Giải pháp:** Backend trả về đồng thời:
  ```json
  {
    "reply": "Chào em, dựa vào REQ-01...",
    "docs": ["intern_portal.md", "testing_guide.md"],
    "retrieved_laws": "..."
  }
  ```
  Nhờ đó, widget chat của Frontend sẽ tự động render các chip tài liệu màu xanh đẹp mắt bên dưới câu trả lời!

---

## 4. PHƯƠNG ÁN TỐI ƯU HÓA SỰ KẾT HỢP (FULLSTACK SYNERGY)

Để bản demo hackathon đạt điểm tối đa từ ban giám khảo, chúng ta nên thực hiện 3 bước tối ưu sau:

### Bước 1: Nâng cấp `Backend/main.py` tương thích 100% với Frontend
- Khai báo Schema linh hoạt nhận cả dữ liệu từ `frontend/app.js` lẫn các client kiểm thử.
- Trả về đúng cấu trúc `{ "reply": "...", "docs": [...] }`.
- Sử dụng trực tiếp `task_context.title` và `task_context.description` để AI trả lời đúng trọng tâm.

### Bước 2: Bật `mode: "api"` trong `frontend/config.js`
- Chuyển `mode: "demo"` thành `mode: "api"`.
- Giữ timeout an toàn `timeoutMs: 90000` (90 giây) để phòng khi Ollama xử lý prompt dài.

### Bước 3: Đồng bộ luồng Mentor Dashboard
- Hiện tại màn hình Mentor của Frontend đang đọc từ `localStorage`.
- Ta có thể thêm 1 hàm fetch `GET /mentor/dashboard` khi Mentor bấm sang tab "Mentor" để nạp trực tiếp kết quả đánh giá năng lực của AI từ Database lên giao diện, tạo nên trải nghiệm tương tác 2 chiều thực tế giữa Thực tập sinh và Tech Lead.

---

## 5. BẢN TÓM TẮT MÃ NGUỒN CẦN ĐIỀU CHỈNH

### File `Backend/main.py`:
```python
class ChatRequest(BaseModel):
    message: Optional[str] = None
    user_message: Optional[str] = None
    code: Optional[str] = ""
    task_id: Optional[str] = "TSK-02"
    task_context: Optional[dict] = None
    history: Optional[List[dict]] = []
    intern_id: Optional[str] = "an"
    session_id: Optional[str] = None
```

### File `frontend/config.js`:
```javascript
window.INTERNA_CONFIG = {
  mode: "api", // Bật chế độ kết nối Backend thật
  apiBaseUrl: "http://localhost:8000",
  chatPath: "/chat",
  timeoutMs: 90000
};
```
