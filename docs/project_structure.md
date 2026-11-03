# Cấu trúc thư mục dự án C++ mẫu

Mã tài liệu: PROJECT-STRUCTURE-01 · Phiên bản: 1.0  
Loại tài liệu: Luật công ty giả lập (Mock Data) cho bài thực tập và AI review code.

Đây là cấu trúc của **dự án C++ mẫu**, không phải yêu cầu di chuyển các thư mục `Backend/` hoặc `frontend/` của nền tảng Interna.

## STRUCT-01 · Cây thư mục chuẩn

Các đường dẫn `/src`, `/include`, `/build`, `/tests` dưới đây tính từ thư mục gốc của dự án mẫu, không phải thư mục gốc của hệ điều hành.

```text
cpp-intern-project/
├── CMakeLists.txt
├── README.md
├── docs/
│   ├── cpp_rule.md
│   └── project_structure.md
├── src/
│   ├── main.cpp
│   └── StudentRecord.cpp
├── include/
│   └── StudentRecord.hpp
├── build/
│   └── ...                  # File được sinh khi cấu hình và biên dịch
└── tests/
    └── StudentRecordTest.cpp
```

## STRUCT-02 · Vai trò từng thư mục

| Thư mục | Vai trò | Nội dung phù hợp |
| --- | --- | --- |
| `/src` | Chứa phần cài đặt và logic chính của ứng dụng. | Các file `.cpp`, điểm vào `main.cpp`, cài đặt phương thức và xử lý nghiệp vụ. |
| `/include` | Chứa header khai báo giao diện để các phần khác sử dụng. | Các file `.hpp` hoặc `.h`, khai báo class, hàm và kiểu dữ liệu. |
| `/build` | Chứa sản phẩm trung gian và kết quả biên dịch được sinh tự động. | Object file, executable, thư viện và cache của công cụ build. Không viết logic ứng dụng tại đây. |
| `/tests` | Chứa unit test kiểm tra các thành phần của ứng dụng. | Test cho hành vi hợp lệ, đầu vào không hợp lệ và trường hợp biên; ghi rõ kết quả mong đợi. |
| `/docs` | Chứa tài liệu để người phát triển và AI tra cứu quy định. | Quy chuẩn C++, sơ đồ thư mục và hướng dẫn dự án. |

`CMakeLists.txt` ở thư mục gốc khai báo cách build, chuẩn C++17 trở lên và các target cần thiết. `README.md` hướng dẫn cấu hình, biên dịch và chạy test.

## STRUCT-03 · Quy tắc tổ chức

- Đặt khai báo `StudentRecord` trong `include/StudentRecord.hpp`, phần cài đặt thông thường trong `src/StudentRecord.cpp` và unit test trong `tests/StudentRecordTest.cpp`.
- Header cần include guard hoặc `#pragma once`. Định nghĩa template hoặc hàm inline có thể nằm trong header khi cần.
- Không đặt unit test trong `src/` và không đặt mã nguồn do người viết trong `build/`.
- Thêm `/build/` vào `.gitignore` của dự án C++ mẫu; không commit sản phẩm biên dịch.
- Cấu hình đường dẫn include trong công cụ build để mã dùng `#include "StudentRecord.hpp"`; tránh đường dẫn tuyệt đối phụ thuộc máy cá nhân.

## STRUCT-04 · Hướng dẫn AI review

1. Xác định đường dẫn file đang được review và đối chiếu vai trò thư mục ở STRUCT-02.
2. Kiểm tra khai báo, cài đặt và unit test có nằm đúng vị trí theo STRUCT-03 hay không.
3. Đối chiếu mã C++ với [quy chuẩn C++](cpp_rule.md), đặc biệt chuẩn ngôn ngữ, raw pointer và quy ước đặt tên.
4. Khi phát hiện lỗi, nêu đường dẫn file, mã quy định và đề xuất vị trí phù hợp.
5. Nếu chỉ được cung cấp một đoạn code, không kết luận dự án thiếu thư mục hoặc thiếu test; yêu cầu thêm cây thư mục hay file liên quan để xác minh.
