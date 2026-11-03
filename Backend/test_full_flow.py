import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_full_system():
    print("=" * 60)
    print("BƯỚC 1: TTS MINH AN GỬI CÂU HỎI TỚI TRỢ LÝ NỘI BỘ")
    print("=" * 60)

    # 1. Ghi nhận sự kiện TTS mở tài liệu cpp_rule.md trước
    requests.post(f"{BASE_URL}/activity", json={
        "intern_id": "intern_an",
        "intern_name": "Minh An",
        "task_id": "TSK-02",
        "event_type": "view_document",
        "title": "Mở tài liệu nội bộ",
        "content": "Quy chuẩn C++ của team (cpp_rule.md)"
    })

    # 2. TTS gửi câu hỏi đầu tiên
    chat_payload = {
        "intern_id": "intern_an",
        "intern_name": "Minh An",
        "task_id": "TSK-02",
        "task_name": "Thiết kế dữ liệu",
        "message": "Mã thực tập sinh bị trùng thì sao?"
    }
    print(f"Đang gửi câu hỏi: '{chat_payload['message']}'...")
    res = requests.post(f"{BASE_URL}/chat", json=chat_payload, timeout=90)
    print("Status:", res.status_code)
    data = res.json()
    print("\n--- PHẢN HỒI CHO TTS TRÊN GIAO DIỆN CHAT ---")
    print(data.get("reply"))
    print("Nguồn tài liệu tham chiếu:", data.get("sources"))

    print("\nĐợi 5 giây để Background Task đánh giá cho Mentor hoàn tất...")
    time.sleep(5)

    print("\n" + "=" * 60)
    print("BƯỚC 2: MENTOR MỞ DASHBOARD THEO DÕI THỰC TẬP SINH")
    print("=" * 60)
    summary_res = requests.get(f"{BASE_URL}/mentor/summary?intern_id=intern_an")
    summary = summary_res.json()

    print("\n[MÀN HÌNH MENTOR - TỔNG HỢP HỖ TRỢ MENTOR]")
    print("Tiến độ:", summary.get("progress_text"))
    print("\nTrao đổi gần nhất:")
    print("  Câu hỏi:", summary.get("recent_exchange", {}).get("question"))
    print("  Nguồn:", summary.get("recent_exchange", {}).get("source"))
    print("\nGợi ý trao đổi khi review (AI sinh ra cho Mentor):")
    print("  =>", summary.get("review_hint"))

    print("\n[DẤU VẾT QUÁ TRÌNH LÀM VIỆC (TIMELINE)]")
    print("Thống kê:", summary.get("timeline_stat"))
    for item in summary.get("timeline", []):
        print(f" - [{item['time']}] {item['title']}: {item['content'][:80]}... ({item['source_tag']})")

if __name__ == "__main__":
    test_full_system()
