import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import time
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_system():
    print("=" * 60)
    print("1. TEST TTS (THỰC TẬP SINH) GỬI CÂU HỎI HỎI BÀI")
    print("=" * 60)
    payload = {
        "intern_id": "intern_an",
        "message": "Anh ơi, em viết int* p = new int(10); xong không delete có sao không anh?"
    }
    print(f"Gửi: '{payload['message']}'...")
    res = requests.post(f"{BASE_URL}/chat", json=payload, timeout=90)
    print("HTTP Status:", res.status_code)
    data = res.json()
    session_id = data.get("session_id")
    print(f"Phiên chat (session_id): {session_id}")
    print("\n--- PHẢN HỒI CỦA TECH LEAD AI CHO TTS ---")
    print(data.get("reply"))

    print("\nĐợi 5 giây để Background AI Evaluation hoàn tất...")
    time.sleep(5)

    print("\n" + "=" * 60)
    print("2. TEST XEM LẠI LỊCH SỬ PHIÊN CHAT (GET /history/{session_id})")
    print("=" * 60)
    hist_res = requests.get(f"{BASE_URL}/history/{session_id}")
    hist_data = hist_res.json()
    print(f"Tổng số tin nhắn trong phiên: {len(hist_data.get('messages', []))}")
    for m in hist_data.get("messages", []):
        print(f" - [{m['sender']}]: {m['content'][:70]}...")

    print("\n" + "=" * 60)
    print("3. TEST MENTOR DASHBOARD (GET /mentor/dashboard)")
    print("=" * 60)
    dash_res = requests.get(f"{BASE_URL}/mentor/dashboard")
    dash_data = dash_res.json()
    print("Thống kê chung:", dash_data.get("stats"))
    print("\nDanh sách đánh giá mới nhất của AI dành cho Mentor:")
    for ev in dash_data.get("recent_evaluations", []):
        print(f" [ID #{ev['id']}] TTS: {ev['intern_id']} | Mức độ rủi ro: {ev['security_risk']}")
        print(f"   Lỗ hổng kiến thức: {ev['knowledge_gap']}")
        print(f"   Đề xuất cho Mentor: {ev['mentor_recommendation']}")

if __name__ == "__main__":
    test_system()
