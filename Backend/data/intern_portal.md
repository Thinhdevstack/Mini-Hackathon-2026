# TÀI LIỆU YÊU CẦU DỰ ÁN: INTERN PORTAL
Mã tài liệu: REQ-SPEC-INTERN-01
Phiên bản: 1.0

## 1. MỤC TIÊU DỰ ÁN
Xây dựng hệ thống quản lý hồ sơ thực tập sinh (Intern Portal) phục vụ việc tiếp nhận, giao việc và đánh giá kết quả thực tập tại Nova Tech.

## 2. CÁC QUY TẮC NGHIỆP VỤ (BUSINESS RULES)

### REQ-01: Quy tắc quản lý Mã thực tập sinh
- **Tính duy nhất:** Mã thực tập sinh (Intern ID) là khóa định danh chính, bắt buộc phải là DUY NHẤT trong toàn bộ hệ thống.
- **Xử lý trùng lặp:** 
  - Trước khi thêm mới hồ sơ, hệ thống bắt buộc phải kiểm tra sự tồn tại của mã thực tập sinh trong cơ sở dữ liệu.
  - Nếu mã đã tồn tại, hệ thống không được ghi đè mà phải chặn thao tác, trả về mã lỗi `DUPLICATE_INTERN_ID` kèm thông báo rõ ràng để người dùng nhập mã khác.

### REQ-02: Quy tắc thời gian thực tập
- **Tính hợp lệ của ngày tháng:** Ngày kết thúc thực tập (`end_date`) tuyệt đối không được trước ngày bắt đầu (`start_date`).
- **Thời hạn tối thiểu:** Kỳ thực tập tiêu chuẩn kéo dài từ 2 đến 6 tháng.

### REQ-03: Cấu trúc dữ liệu hồ sơ
- Mã thực tập sinh (`intern_id`): Chuỗi ký tự chuẩn hóa (Ví dụ: `INT-2026-001`).
- Họ và tên (`full_name`): Bắt buộc.
- Email công ty (`company_email`): Phải có đuôi `@novatech.internal`.
- Vị trí (`role`): Backend, Frontend, hoặc QA.
- Người hướng dẫn (`mentor_id`): Mã của Mentor phụ trách.
