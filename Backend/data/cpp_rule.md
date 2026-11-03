# QUY CHUẨN LẬP TRÌNH C++ NỘI BỘ (COMPANY C++ CODING GUIDELINES)
Mã tài liệu: SEC-CPP-RULE-2026
Phiên bản: 1.0 (Áp dụng cho toàn bộ dự án & Thực tập sinh / Junior Dev)

---

## 1. TIÊU CHUẨN NGÔN NGỮ (LANGUAGE STANDARD)
- **Chuẩn bắt buộc**: Toàn bộ dự án phải sử dụng chuẩn **C++17** (hoặc C++20 nếu dự án yêu cầu).
- **Trình biên dịch**: GCC 11+, Clang 13+, hoặc MSVC 2019+ với flag `-std=c++17` (hoặc `/std:c++17`).

---

## 2. QUẢN LÝ BỘ NHỚ & TÀI NGUYÊN (MEMORY MANAGEMENT & RAII)
- **QUY TẮC CỐT LÕI - CẤM RAW POINTER ĐỂ SỞ HỮU BỘ NHỚ**:
  - TUYỆT ĐỐI KHÔNG sử dụng `new` và `delete` thủ công. Không dùng con trỏ thô (raw pointer) để quản lý vòng đời bộ nhớ vì dễ gây ra memory leak, dangling pointer và double free.
  - Sử dụng nguyên lý **RAII (Resource Acquisition Is Initialization)**.
  - Sử dụng **Smart Pointers**:
    - Ưu tiên sử dụng `std::unique_ptr` khi một đối tượng có quyền sở hữu độc quyền (sử dụng `std::make_unique<T>()`).
    - Chỉ sử dụng `std::shared_ptr` khi tài nguyên thực sự cần nhiều nơi cùng chia sẻ quyền sở hữu (sử dụng `std::make_shared<T>()`).
    - Dùng `std::weak_ptr` để phá vỡ vòng tham chiếu (circular reference) khi dùng `std::shared_ptr`.
  - Raw pointer hoặc reference (`T*`, `const T&`) CHỈ ĐƯỢC PHÉP dùng cho việc "mượn" (view/observer/borrow) tài nguyên mà không sở hữu, không chịu trách nhiệm giải phóng bộ nhớ.

---

## 3. AN TOÀN THÔNG TIN & BẢO MẬT (SECURITY & COMPLIANCE)
- **KHÔNG HARDCODE CREDENTIALS**:
  - Nghiêm cấm tuyệt đối việc hardcode thông tin nhạy cảm vào source code: Mật khẩu, DB Connection String, API Key, JWT Secret, Token xác thực hoặc dữ liệu thật của khách hàng.
  - Toàn bộ thông tin bí mật phải được nạp thông qua Environment Variables (`std::getenv`) hoặc nạp từ file cấu hình bảo mật được mã hóa.
- **CHỐNG SQL INJECTION & LỖ HỔNG TRUY VẤN**:
  - Không cộng chuỗi (string concatenation/formatting) để tạo câu lệnh SQL hoặc lệnh OS.
  - Bắt buộc dùng **Prepared Statements** và **Parameterized Queries** cho mọi thao tác cơ sở dữ liệu.
- **AN TOÀN BỘ ĐỆM & BỘ NHỚ**:
  - Không sử dụng các hàm C cổ điển không an toàn như `strcpy`, `strcat`, `gets`, `sprintf`. Thay thế bằng `snprintf`, `std::string`, `std::string_view` hoặc `std::span` (C++20).
  - Kiểm tra boundary đầy đủ, tránh tràn bộ đệm (Buffer Overflow).

---

## 4. QUY TẮC THIẾT KẾ & VIẾT MÃ (CODE QUALITY)
- **Header Files**:
  - Luôn sử dụng `#pragma once` ở đầu mỗi header file.
  - **TUYỆT ĐỐI CẤM** viết `using namespace std;` trong các file header `.h` / `.hpp` vì gây ô nhiễm namespace toàn cục (namespace pollution).
- **Const-Correctness**:
  - Mọi hàm thành viên không thay đổi trạng thái của object phải được đánh dấu `const`.
  - Ưu tiên truyền tham số dạng `const Type&` thay vì copy đối tượng lớn.
- **Auto & Modern Features**:
  - Tận dụng `auto`, `structured binding`, `constexpr`, `std::optional`, `std::variant` trong C++17 để code ngắn gọn, an toàn kiểu (type-safe).
- **Xử lý Ngoại lệ (Exception Handling)**:
  - Destructor bắt buộc phải là `noexcept`.
  - Quản lý tài nguyên lỗi bằng khối `try ... catch` hợp lý hoặc trả về `std::optional` / kết quả báo trạng thái, không để crash ứng dụng đột ngột.

---

## 5. QUY ƯỚC ĐẶT TÊN (NAMING CONVENTIONS)
- **Class / Struct / Enum**: `PascalCase` (Ví dụ: `UserManager`, `DatabaseConnection`).
- **Function / Method**: `camelCase` (Ví dụ: `processOrder()`, `calculateTotal()`).
- **Variable / Parameter**: `snake_case` hoặc `camelCase` (nhất quán trong dự án, ví dụ: `user_id`, `maxRetries`).
- **Member Variable (private/protected)**: tiền tố `m_` (Ví dụ: `m_connection`, `m_retryCount`).
- **Constant / Macro**: `UPPER_SNAKE_CASE` (Ví dụ: `MAX_BUFFER_SIZE`).
