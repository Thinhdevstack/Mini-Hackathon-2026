# TÀI LIỆU HƯỚNG DẪN KIỂM THỬ ĐẦU VÀO (TESTING GUIDE)
Mã tài liệu: TEST-GUIDE-2026

## 1. NGUYÊN TẮC KIỂM THỬ ĐẦU VÀO (INPUT VALIDATION)
- Mọi dữ liệu do người dùng hoặc client gửi lên phải được xác thực trước khi đưa vào tầng xử lý logic hoặc lưu vào database.
- Không tin tưởng dữ liệu đầu vào (Never trust user input).

## 2. CÁC TÌNH HUỐNG KIỂM THỬ BẮT BUỘC (TEST CASES)
- **Kiểm thử trùng lặp (Duplicate Key Test):**
  - Giả lập tình huống nhập một mã thực tập sinh đã tồn tại trong cơ sở dữ liệu.
  - Kỳ vọng: Hệ thống từ chối lưu, giữ nguyên dữ liệu cũ, và trả về thông báo lỗi thân thiện cho người dùng.
- **Kiểm thử biên thời gian (Date Boundary Test):**
  - Giả lập tình huống ngày kết thúc trước ngày bắt đầu.
  - Kỳ vọng: Báo lỗi logic ngày tháng ngay tại tầng validation.
- **Kiểm thử dữ liệu rỗng (Null/Empty Test):**
  - Kiểm tra các trường bắt buộc như họ tên, mã ID.
