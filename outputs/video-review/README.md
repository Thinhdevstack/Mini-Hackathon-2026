# Interna — Video review sản phẩm

- Video chính: `INTERNA_REVIEW_1080p_VI.mp4`
- Thời lượng: **05:02.83**; khung hình **1920 × 1080**, **24 fps**; video H.264, âm thanh AAC stereo 48 kHz chuẩn phát thanh (−15.7 LUFS).
- Giọng thuyết minh: **Neural AI Voice tiếng Việt** tự nhiên, giàu ngữ điệu, kết hợp chuỗi mastering studio (EQ lọc ồn/tăng độ ấm, compressor mượt và chuẩn hóa âm lượng EBU R128). Bản giọng macOS Linh cũ được lưu trữ tại `outputs/video-review/audio_macOS_Linh_backup`.
- Có phụ đề gắn vào hình, slide giới thiệu/lộ trình/định hướng, cảnh phóng cận AI và nhạc nền tự tổng hợp.
- Tệp phụ đề riêng: `INTERNA_REVIEW_VI.srt`.
- Tệp lời đọc riêng: `audio/THUYET_MINH_VI.m4a`.
- Ảnh bìa: `INTERNA_POSTER.png`.
- Mốc nội dung: `CHAPTERS.txt`; các chương cũng được nhúng vào MP4.
- Lời thuyết minh: `LOI_THUYET_MINH.md`.

## Nội dung và tính xác thực

Video được dựng dựa trên `KICH_BAN_QUAY_VIDEO.md`. Các thao tác được thực hiện trên frontend thật của repository, được phục vụ tại `http://localhost:3000`. Các khung hình trình duyệt liên tiếp được ghi bằng công cụ điều khiển trình duyệt; không quay các ứng dụng hoặc nội dung cá nhân khác trên màn hình máy tính.

Hai câu hỏi AI trong video nhận phản hồi thật từ FastAPI của dự án và mô hình Ollama `StrictMentor`. Nội dung phản hồi trong cảnh quay được giữ nguyên. Phần dựng cắt thời gian chờ và giữ khung hình để khớp lời thuyết minh; không dùng phản hồi giả lập thay kết quả API.

Luồng demo đã hoàn tất: đọc tài liệu → hỏi AI → nộp bài có vướng mắc → mentor xem nhật ký, phản hồi và duyệt hoàn thành → tạo hồ sơ mẫu Nguyễn Văn An. Hồ sơ này dùng địa chỉ `an.nguyen@example.com`, chỉ được tạo trong dữ liệu minh họa của trình duyệt.

Phạm vi MVP được thể hiện đúng: đăng nhập mô phỏng, dữ liệu nghiệp vụ lưu trong trình duyệt. PostgreSQL, Cloud Run, Multi-Agent và báo cáo năng lực được trình bày như kế hoạch. Lời đọc đã bỏ tỷ lệ thời gian 30–40% và khẳng định “bảo mật 100%” do kịch bản không cung cấp minh chứng cho các khẳng định này.

## Nguồn dựng có thể chỉnh sửa

- `source/scenes.json`: nội dung và lời thuyết minh từng cảnh.
- `source/timeline.json`: thời điểm bắt đầu và thời lượng từng cảnh.
- `source/make_voice.py`: tạo giọng đọc cục bộ.
- `source/build_video.py`: tạo đồ họa, dựng cảnh, phụ đề và phối âm.
- `captures/`: khung hình trình duyệt gốc và thời điểm ghi.
- `assets/`: slide và hình kiểm tra.
- `source/render/`: các đoạn MP4 trung gian và phụ đề ASS.

Python cần Pillow, numpy và imageio-ffmpeg. `imageio-ffmpeg` đã được tải từ PyPI vào `source/vendor/`. Các font Arial dùng bản có sẵn trên macOS. Để dựng lại, chạy `make_voice.py` rồi `build_video.py` bằng môi trường Python đã có các thư viện trên.

## Kiểm tra bản bàn giao

- Giải mã toàn bộ 6.304 khung hình và âm thanh bằng FFmpeg: không lỗi.
- Đối chiếu trực quan 12 thời điểm trong video; xem `assets/QA_CONTACT_SHEET.jpg`.
- Âm lượng tổng hợp đo được: **−16,8 LUFS**, true peak **−4,4 dBFS**.
- Video được lưu cục bộ, chưa đăng tải ra dịch vụ công khai.
