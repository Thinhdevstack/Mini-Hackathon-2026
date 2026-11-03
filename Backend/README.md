# Interna - Backend Service

Hệ thống RAG Backend hỗ trợ Thực tập sinh C++ kèm AI đánh giá năng lực cho Mentor.

## 🚀 Hướng dẫn cài đặt & Khởi chạy

### 1. Tạo môi trường ảo & Cài đặt thư viện
```bash
# Di chuyển vào thư mục backend
cd Backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt môi trường ảo:
# Windows (PowerShell / CMD):
venv\Scripts\activate
# Mac / Linux:
source venv/bin/activate

# Cài đặt các gói phụ thuộc
pip install -r requirements.txt
```

### 2. Khởi tạo mô hình AI trên Ollama
Đảm bảo bạn đã cài đặt [Ollama](https://ollama.ai) và Ollama đang chạy (`ollama serve`).

```bash
# Tạo model StrictMentor từ Modelfile
ollama create StrictMentor -f Modelfile
```

### 3. Khởi động Backend API
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

- Server chạy tại: `http://127.0.0.1:8000`
- Tài liệu API tương tác (Swagger UI): `http://127.0.0.1:8000/docs`

### 4. Kiểm thử nhanh
```bash
python test_upgrade.py
```
