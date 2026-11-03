# Interna — demo giao diện thực tập sinh & mentor

HTML/CSS/JavaScript thuần, không cần cài package, không phụ thuộc CDN. Dùng dữ liệu công ty giả lập.

## Mở bản demo

- Mở `index.html` bằng Edge/Chrome, hoặc dùng Live Server trong VS Code.
- Hai nút **Thực tập sinh / Mentor** ở đầu trang chuyển màn hình. Đây là bộ chọn demo, không phải đăng nhập hay phân quyền thật.
- Dữ liệu lưu trong trình duyệt hiện tại. Máy khác, profile khác hoặc origin khác không dùng chung dữ liệu. Có thể dùng **Đặt lại dữ liệu demo** để bắt đầu lại.

## Kịch bản trình diễn 3 phút

1. Ở màn Thực tập sinh, chọn task **Thiết kế dữ liệu**.
2. Mở **Yêu cầu dự án Intern Portal**, rồi hỏi AI: “Mã thực tập sinh bị trùng thì sao?”. Phản hồi mặc định là giả lập, chưa chạy model.
3. Đánh dấu kết quả cần đạt, nhập **Kết quả / đường dẫn bài làm** và **Vướng mắc cần mentor giải đáp**, rồi chọn **Gửi mentor xem**. Task chỉ chuyển sang **Chờ mentor**, chưa hoàn thành.
4. Chuyển **Mentor**: xem lịch sử câu hỏi, phản hồi và lần mở tài liệu. Phần tổng hợp tính từ dữ liệu demo, chưa phải AI phân tích.
5. Chọn **Xem bài gửi**, nhập giải đáp và chọn **Gửi giải đáp**. Chuyển lại Thực tập sinh để thấy phản hồi ở **Trao đổi với mentor**, rồi gửi một câu hỏi thêm.
6. Mentor có thể **Yêu cầu chỉnh sửa** (bắt buộc nêu nội dung cần sửa). Thực tập sinh sửa kết quả và chọn **Gửi lại mentor**. Bản cũ và phản hồi cũ được giữ nguyên.
7. Mentor xem phiên bản mới nhất, trả lời vướng mắc/câu hỏi còn chờ rồi **Duyệt hoàn thành**. Hai màn cùng cập nhật tiến độ.

Chỉ hồ sơ **Minh An** có luồng tương tác. Hai hồ sơ còn lại minh họa trạng thái chưa có dữ liệu.

## Quy tắc luồng review

- `Chưa bắt đầu → Đang làm → Chờ mentor → Hoàn thành`.
- Nhánh trả bài: `Chờ mentor → Cần chỉnh sửa → Chờ mentor` sau khi nộp lại. Không duyệt bản cũ khi đang yêu cầu sửa.
- **Gửi giải đáp** chỉ thêm phản hồi, không tự duyệt hoặc trả bài. Thực tập sinh thấy lời giải đáp ngay trong task và có thể hỏi lại.
- Khi có vướng mắc hoặc câu hỏi mới chưa được trả lời, mentor cần nhập giải đáp trước khi duyệt. Đây là kiểm tra có phản hồi, không phải AI xác minh chất lượng lời giải đáp; mentor chịu trách nhiệm xác nhận bài đạt yêu cầu.
- Kết quả, vướng mắc và checklist được chụp lại theo từng lần nộp. Trong trạng thái Chờ mentor/Hoàn thành, không sửa bản đã gửi. Trao đổi thêm không tự biến thành một lần nộp mới.
- **Ghi chú đánh giá riêng của mentor** chỉ xuất hiện ở màn mentor, khác với giải đáp gửi trong nhiệm vụ.
- Dữ liệu phiên bản cũ được nâng cấp tại chỗ. Ghi chú nộp bài cũ vẫn giữ nguyên; vì bản cũ gộp cả vướng mắc trong ghi chú nên cần phản hồi trước khi duyệt.
- Dự thảo kết quả, giải đáp, câu hỏi thêm và lịch sử nộp bài được lưu trên cùng trình duyệt. Không cần đặt lại demo sau cập nhật.

## Kết nối backend ngày mai

Chỉnh `config.js`:

```js
window.INTERNA_CONFIG = {
  mode: "api",
  apiBaseUrl: "http://192.168.1.20:8000", // thay bằng IP máy chạy FastAPI
  chatPath: "/chat",
  timeoutMs: 90000
};
```

Dùng Live Server khi gọi API; backend cho phép chính xác origin frontend trong CORS, ví dụ `http://127.0.0.1:5500` và/hoặc `http://localhost:5500` theo địa chỉ thực tế. Hai máy cần kết nối được qua mạng. Ollama chạy trên máy backend và frontend không gọi trực tiếp Ollama.

Hợp đồng API **đề xuất, cần thống nhất với bạn backend**:

```json
{
  "code": "",
  "message": "Mã thực tập sinh bị trùng thì sao?",
  "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}],
  "task_id": "TSK-02",
  "task_context": {
    "title": "Đề xuất cấu trúc dữ liệu cho hồ sơ thực tập sinh",
    "description": "...",
    "document_ids": ["requirements", "cpp"]
  }
}
```

`history` chỉ gồm các lượt chat trước, không lặp câu hỏi hiện tại. Backend trả:

```json
{"reply": "Nội dung phản hồi của AI"}
```

Backend chịu trách nhiệm xác thực người dùng, phân quyền, truy xuất tài liệu thật, System Prompt và model. Các `document_ids` trên chỉ là ID của demo; cần map sang kho tài liệu backend. Không tin thông tin role/quyền/tài liệu từ frontend để quyết định quyền truy cập.

Khi bật API, lời chào đầu luồng vẫn được gắn nhãn **giả lập**; chỉ phản hồi nhận thành công từ backend được gắn nhãn **API**. Giao diện không tự bịa trích dẫn cho câu trả lời API.

## Phạm vi bản này

- Đã có: hai vai trò demo, ba task, checklist, tài liệu mẫu, chat theo task, nhật ký đúng người thực hiện, gửi kết quả/vướng mắc, trao đổi hai chiều với mentor, yêu cầu chỉnh sửa, nộp lại có lịch sử, duyệt hoàn thành, ghi chú riêng và lưu local.
- Chưa có: đăng nhập, DB dùng chung, backend FastAPI, Ollama/RAG thật, AI phân tích đánh giá, upload file, đồng bộ nhiều máy. Nhận xét không tự gửi đến người khác.
- Mọi số liệu trên màn mentor dựa vào dữ liệu demo trong trình duyệt. Không chấm điểm hay suy luận năng lực từ số lần hỏi AI.

## Cấu trúc

- `index.html`: khung giao diện, sidebar, đổi vai trò và hộp tài liệu.
- `style.css`: thiết kế responsive.
- `app.js`: dữ liệu mẫu, giao diện, sự kiện và hàm `sendToMentor()` kết nối API.
- `config.js`: chuyển demo/API và địa chỉ backend.

Các ví dụ nghiệp vụ/quy chuẩn trong ứng dụng là dữ liệu đề xuất cho demo, không khẳng định đã trích từ Google Docs của nhóm.

## Kiểm tra logic

`outputs/qa/check-demo.cjs` (chạy từ thư mục gốc dự án bằng Node) kiểm tra luồng review, giữ lịch sử, trạng thái không hợp lệ, nâng cấp dữ liệu cũ, hợp đồng API, lỗi mạng, bản nháp khi chờ AI, nội dung nhập được escape và đặt lại demo. Đây là mô phỏng DOM để kiểm tra logic, không thay thế kiểm tra bố cục trên trình duyệt hoặc tích hợp backend thật.


### Bản dự thi MVP 30% — cập nhật 04/11/2026
Mở `index.html`, chọn **Tôi là thực tập sinh** hoặc **Tôi là mentor** để dùng tài khoản mẫu. Có thể mở “Đăng nhập bằng tài khoản khác” khi cần. Chọn nhiệm vụ → bắt đầu làm → đọc tài liệu/hỏi AI → nhập kết quả và gửi mentor. Đăng xuất rồi chọn mentor để xem bài trên cùng trình duyệt.

Dữ liệu lưu tại `interna-v3` trên trình duyệt hiện tại; đăng nhập là mô phỏng. API mặc định trỏ tới `http://localhost:8000`. Khi backend không chạy, giao diện báo lỗi và giữ câu hỏi để gửi lại. Để demo offline, đặt `mode: "demo"` trong `config.js`; phản hồi sẽ được ghi rõ là giả lập.

Kiểm tra hồi quy từ thư mục gốc: `node outputs/qa/check-demo.cjs`. Phạm vi chưa bao gồm đồng bộ nhiều máy, xác thực thật hoặc multi-agent.
