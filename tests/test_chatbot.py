from fastapi.testclient import TestClient


def test_chatbot_endpoint(client: TestClient):
    """Tests POST /api/chat/ask with Maestro AI music analyst."""
    payload = {"question": "What is the difference between major and minor modes?"}
    response = client.post("/api/chat/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
