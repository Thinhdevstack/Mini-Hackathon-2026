# Quy chuẩn C++ của dự án mẫu

Mã tài liệu: CPP-RULE-01 · Phiên bản: 1.0  
Loại tài liệu: Luật công ty giả lập (Mock Data) cho bài thực tập và AI review code.

## CPP-01 · Chuẩn ngôn ngữ

- Bắt buộc sử dụng **C++17 trở lên**.
- Cấu hình build phải khai báo chuẩn sử dụng, ví dụ `-std=c++17` với GCC/Clang hoặc `/std:c++17` với MSVC.
- Chỉ dùng tính năng của chuẩn đã khai báo; nếu dùng tính năng C++20, phải nâng cấu hình build tương ứng.

## CPP-02 · Con trỏ và quản lý bộ nhớ

- **Cấm sử dụng raw pointer trong mã của dự án mẫu**, kể cả con trỏ không sở hữu: ví dụ `int*`, `Student*`, `const Student*`.
- Không cấp phát hoặc giải phóng bộ nhớ bằng `new`, `delete`, `new[]`, `delete[]` trực tiếp.
- Khi cần con trỏ quản lý đối tượng động, **bắt buộc dùng smart pointer**:
  - `std::unique_ptr<T>`: ưu tiên khi chỉ có một chủ sở hữu; tạo bằng `std::make_unique<T>()`.
  - `std::shared_ptr<T>`: chỉ dùng khi thực sự có nhiều chủ sở hữu; tạo bằng `std::make_shared<T>()`.
- Không dùng `.get()` hoặc `.release()` để tạo raw pointer nhằm lách quy định.
- Không bắt buộc cấp phát động cho mọi biến. Ưu tiên biến giá trị, `std::string`, `std::vector` khi phù hợp. Khi chỉ mượn đối tượng để đọc hoặc sửa, dùng tham chiếu `const T&` hoặc `T&`.
- Đây là quy định riêng của dự án mẫu, không phải khẳng định rằng ngôn ngữ C++ cấm raw pointer.

## CPP-03 · Quy ước đặt tên

| Thành phần | Quy ước | Ví dụ đúng | Ví dụ sai |
| --- | --- | --- | --- |
| Biến, tham số và biến thành viên | `camelCase` | `studentCount`, `studentName` | `student_count`, `StudentCount` |
| Class | `PascalCase` | `StudentRecord`, `InternManager` | `student_record`, `internManager` |
| Hàm và phương thức | `camelCase` | `getScore()`, `updateStudent()` | `get_score()`, `UpdateStudent()` |

Không dùng tiền tố `m_` hoặc `snake_case` cho biến trong dự án mẫu này.

## CPP-04 · Ví dụ đúng

Đoạn mã hoàn chỉnh dưới đây dùng C++17, class đặt tên PascalCase, biến đặt tên camelCase và smart pointer sở hữu độc quyền.

```cpp
#include <iostream>
#include <memory>

class StudentRecord {
public:
    explicit StudentRecord(int initialScore) : score(initialScore) {}

    int getScore() const {
        return score;
    }

private:
    int score;
};

int main() {
    std::unique_ptr<StudentRecord> studentRecord =
        std::make_unique<StudentRecord>(85);
    int studentScore = studentRecord->getScore();
    std::cout << studentScore << '\n';
    return 0;
}
```

Kết quả mong đợi: in ra `85`. Bộ nhớ được giải phóng tự động khi `studentRecord` ra khỏi phạm vi.

## CPP-05 · Ví dụ sai

Đoạn mã sau có thể biên dịch nhưng **vi phạm quy chuẩn công ty**; chỉ dùng làm dữ liệu kiểm tra AI, không sao chép vào mã sản phẩm.

```cpp
#include <iostream>

class student_record {
public:
    int student_score = 85;
};

int main() {
    student_record* student_ptr = new student_record();
    int* score_ptr = new int(student_ptr->student_score);
    std::cout << *score_ptr << '\n';
    delete score_ptr;
    delete student_ptr;
    return 0;
}
```

Các lỗi AI cần chỉ ra:

1. **CPP-02:** `student_record*` và `int*` là raw pointer bị cấm; dùng `new`/`delete` thủ công cũng vi phạm, kể cả khi đã gọi `delete` đầy đủ.
2. **CPP-03:** class `student_record` không theo PascalCase.
3. **CPP-03:** các biến `student_score`, `student_ptr`, `score_ptr` không theo camelCase.

Khi review, AI phải nêu mã quy định, vị trí vi phạm và gợi ý hướng sửa; không coi việc biên dịch thành công là bằng chứng tuân thủ.
