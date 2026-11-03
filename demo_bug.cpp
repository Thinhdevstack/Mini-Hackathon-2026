// Dữ liệu mồi cho video demo Interna: cố tình vi phạm luật công ty.
// Chỉ dùng để copy/paste vào Web App, không dùng trong mã sản phẩm.

#include <iostream>

class DatabaseConnection {
public:
    DatabaseConnection() {
        data[0] = My_var;
    }

    ~DatabaseConnection() {
        // Cố tình bỏ quên giải phóng mảng đã cấp phát.
        std::cout << "Connection closed\n";
    }

    int readFirstValue() const {
        return data[0];
    }

private:
    int* data = new int[100];
    int My_var = 42;
};

int main() {
    DatabaseConnection connection;
    std::cout << "First value: " << connection.readFirstValue() << '\n';
    return 0;
}
