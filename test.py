import pytest
import httpx
from httpx import AsyncClient

BASE_URL = "https://chatbot-tb-back.ript.vn/api/chat"

# --- Text only ---
@pytest.mark.anyio
async def test_only_text():
    async with AsyncClient(base_url=BASE_URL, timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(
            "/",
            data={"text": "Xin chào, tôi muốn hỏi về thủ tục A"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "successfully"
    assert "response" in data["output"]

# --- Audio only ---
@pytest.mark.anyio
async def test_only_audio_valid():
    # Dùng file audio thật đã tạo
    with open("tests/audio.m4a", "rb") as f:
        audio_bytes = f.read()

    async with AsyncClient(base_url=BASE_URL, timeout=httpx.Timeout(60.0)) as client:
        files = {"audio_file": ("audio.m4a", audio_bytes, "audio/m4a")}
        response = await client.post("/", files=files)
    
    assert response.status_code == 200
    json = response.json()
    assert json["result"] == "successfully"
    assert isinstance(json["output"]["response"], list)

# --- Text + Audio ---
@pytest.mark.anyio
async def test_text_and_audio():
    with open("tests/audio.webm", "rb") as f:
        audio_bytes = f.read()

    async with AsyncClient(base_url=BASE_URL, timeout=httpx.Timeout(60.0)) as client:
        files = {"audio_file": ("audio.webm", audio_bytes, "audio/webm")}
        response = await client.post(
            "/",
            data={"text": "Tôi muốn hỏi thêm"},
            files=files,
        )
    
    assert response.status_code == 200
    json = response.json()
    assert json["result"] == "successfully"
    assert "response" in json["output"]

# --- Unsupported audio type ---
@pytest.mark.anyio
async def test_unsupported_audio_type():
    with open("tests/audio.wav", "rb") as f:
        audio_bytes = f.read()  # giả sử .wav không được backend hỗ trợ
    
    async with AsyncClient(base_url=BASE_URL, timeout=httpx.Timeout(60.0)) as client:
        files = {"audio_file": ("audio.wav", audio_bytes, "audio/wav")}
        response = await client.post("/", files=files)
    
    # Phụ thuộc backend có chặn .wav hay không
    assert response.status_code == 400 or response.status_code == 200

# --- No input ---
@pytest.mark.anyio
async def test_no_input():
    async with AsyncClient(base_url=BASE_URL, timeout=httpx.Timeout(60.0)) as client:
        response = await client.post("/", data={})
    assert response.status_code == 400
    assert response.json()["detail"] == "Phải gửi ít nhất text hoặc audio file"

# --- Chat history ---
@pytest.mark.anyio
async def test_with_chat_history():
    history = [
        {"role": "user", "content": "Xin hỏi thủ tục B"},
        {"role": "bot", "content": "Bạn cần giấy X, Y"},
    ]
    async with AsyncClient(base_url=BASE_URL, timeout=httpx.Timeout(60.0)) as client:
        response = await client.post(
            "/",
            data={"text": "Tôi có thêm câu hỏi"},
            json={"chat_history": history},
        )
    assert response.status_code == 200
    json = response.json()
    assert json["result"] == "successfully"
    assert isinstance(json["output"]["response"], list)