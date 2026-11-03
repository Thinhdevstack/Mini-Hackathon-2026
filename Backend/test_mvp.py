import requests

def test_chat():
    url = "http://127.0.0.1:8000/chat"
    payload = {
        "message": "Mã thực tập sinh bị trùng thì sao?"
    }
    print(f"Gửi câu hỏi tới {url}: {payload['message']}")
    res = requests.post(url, json=payload, timeout=60)
    print("Status:", res.status_code)
    data = res.json()
    print("Phản hồi từ AI:", data.get("reply"))
    print("Tài liệu tham chiếu:", data.get("docs"))

if __name__ == "__main__":
    test_chat()
