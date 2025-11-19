# Mẫu gọi API ChatBot Thai Binh

## 1. Gọi API POST "/" - Multi-media Chat (Text + Audio)

### A. Curl - Chỉ Text

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Tôi muốn hỏi về thủ tục cấp giấy phép",
    "audio_file": null,
    "chat_history": [
      {
        "human": "Xin chào",
        "ai": "Xin chào bạn, tôi có thể giúp gì cho bạn?"
      },
      {
        "human": "Tôi cần tìm hiểu về quy trình làm hành chính",
        "ai": "Tôi sẽ hỗ trợ bạn tìm hiểu về các quy trình hành chính"
      }
    ]
  }'
```

### B. Curl - Text + Audio File

```bash
curl -X POST "http://localhost:8000/chat/" \
  -F "text=Tôi muốn hỏi về thủ tục cấp giấy phép" \
  -F "audio_file=@/path/to/audio.webm" \
  -F "chat_history=[{\"human\":\"Xin chào\",\"ai\":\"Xin chào bạn\"}]"
```

### C. Python - Gọi API với requests

```python
import requests
import json

url = "http://localhost:8000/chat/"

# Ví dụ 1: Chỉ gửi text
data = {
    "text": "Tôi muốn hỏi về thủ tục cấp giấy phép",
    "chat_history": [
        {
            "human": "Xin chào",
            "ai": "Xin chào bạn, tôi có thể giúp gì cho bạn?"
        },
        {
            "human": "Tôi cần tìm hiểu về quy trình làm hành chính",
            "ai": "Tôi sẽ hỗ trợ bạn tìm hiểu về các quy trình hành chính"
        }
    ]
}

response = requests.post(url, json=data)
print(response.json())

# Response mong đợi:
# {
#     "result": "successfully",
#     "status": 200,
#     "output": {
#         "user_answer": False,
#         "response": [
#             {
#                 "type": "text",
#                 "content": "Nội dung trả lời từ chatbot",
#                 "recommendations": [
#                     {"procedure_id": "1.001193", "name": "Thủ tục cấp giấy phép"},
#                     {"procedure_id": "1.001266", "name": "Thủ tục gia hạn giấy phép"}
#                 ]
#             }
#         ]
#     }
# }
```

### D. Python - Gửi Audio File

```python
import requests

url = "http://localhost:8000/chat/"

chat_history = [
    {
        "human": "Xin chào",
        "ai": "Xin chào bạn, tôi có thể giúp gì cho bạn?"
    },
    {
        "human": "Tôi muốn biết về quy trình",
        "ai": "Bạn muốn biết về quy trình nào cụ thể?"
    }
]

# Gửi với audio file
files = {
    'text': (None, 'Cho tôi biết thêm chi tiết'),
    'audio_file': ('audio.webm', open('/path/to/audio.webm', 'rb'), 'audio/webm'),
    'chat_history': (None, json.dumps(chat_history), 'application/json')
}

response = requests.post(url, files=files)
print(response.json())
```

### E. JavaScript - Fetch API

```javascript
// Ví dụ 1: Chỉ gửi text
async function chatWithText() {
  const chatHistory = [
    {
      "human": "Xin chào",
      "ai": "Xin chào bạn, tôi có thể giúp gì cho bạn?"
    },
    {
      "human": "Tôi cần tìm hiểu về quy trình cấp phép",
      "ai": "Tôi sẽ hỗ trợ bạn với thông tin về quy trình cấp phép"
    }
  ];

  const response = await fetch('http://localhost:8000/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text: "Tôi muốn hỏi về thủ tục cấp giấy phép",
      audio_file: null,
      chat_history: chatHistory
    })
  });

  const result = await response.json();
  console.log(result);
  // Output:
  // {
  //   "result": "successfully",
  //   "status": 200,
  //   "output": {
  //     "user_answer": false,
  //     "response": [
  //       {
  //         "type": "text",
  //         "content": "...",
  //         "recommendations": [...]
  //       }
  //     ]
  //   }
  // }
}
```

### F. JavaScript - Gửi Audio File

```javascript
// Ví dụ 2: Gửi text + audio file
async function chatWithAudio() {
  const formData = new FormData();
  
  // Thêm text
  formData.append('text', 'Cho tôi biết thêm chi tiết về quy trình');
  
  // Thêm audio file
  const audioInput = document.getElementById('audioFile');
  if (audioInput.files.length > 0) {
    formData.append('audio_file', audioInput.files[0]);
  }
  
  // Thêm chat history
  const chatHistory = [
    {
      "human": "Xin chào",
      "ai": "Xin chào bạn, tôi có thể giúp gì cho bạn?"
    }
  ];
  formData.append('chat_history', JSON.stringify(chatHistory));

  const response = await fetch('http://localhost:8000/chat/', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  console.log(result);
}
```

---

## 2. Gọi API POST "/stt" - Speech-to-Text

### A. Curl

```bash
curl -X POST "http://localhost:8000/chat/stt" \
  -F "audio_file=@/path/to/audio.webm"
```

### B. Python

```python
import requests

url = "http://localhost:8000/chat/stt"

with open('/path/to/audio.webm', 'rb') as f:
    files = {'audio_file': ('audio.webm', f, 'audio/webm')}
    response = requests.post(url, files=files)
    
print(response.json())
# Response mong đợi:
# {
#     "result": "successfully",
#     "status": 200,
#     "output": {
#         "type": "text",
#         "value": "Nội dung text được nhận diện từ audio"
#     }
# }
```

### C. JavaScript

```javascript
async function speechToText() {
  const formData = new FormData();
  
  const audioInput = document.getElementById('audioFile');
  if (audioInput.files.length > 0) {
    formData.append('audio_file', audioInput.files[0]);
  }

  const response = await fetch('http://localhost:8000/chat/stt', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();
  console.log(result);
}
```

---

## 3. Gọi API POST "/stream" - Streaming Response

### A. Python - Streaming Response

```python
import requests

url = "http://localhost:8000/chat/stream"

chat_history = [
    {
        "human": "Xin chào",
        "ai": "Xin chào bạn"
    }
]

data = {
    'text': 'Tôi muốn hỏi về quy trình',
    'chat_history': json.dumps(chat_history)
}

files = {
    'text': (None, 'Tôi muốn hỏi về quy trình'),
    'audio_file': None,
    'chat_history': (None, json.dumps(chat_history), 'application/json')
}

response = requests.post(url, files=files, stream=True)

# Nhận response từng dòng
for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
    if chunk:
        print(chunk, end='', flush=True)
```

### B. JavaScript - Streaming

```javascript
async function streamChat() {
  const formData = new FormData();
  formData.append('text', 'Tôi muốn hỏi về quy trình');
  formData.append('chat_history', JSON.stringify([
    {
      "human": "Xin chào",
      "ai": "Xin chào bạn"
    }
  ]));

  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    body: formData
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    
    const chunk = decoder.decode(value);
    console.log(chunk);
    // Cập nhật UI với từng phần response
  }
}
```

---

## 4. Chi tiết các trường thông tin

### Request Format để route "/"

```json
{
  "text": "string - Optional - Nội dung text của câu hỏi",
  "audio_file": "file - Optional - File audio (định dạng: webm, mp4, m4a, aac)",
  "chat_history": [
    {
      "human": "string - Câu hỏi/câu nói của người dùng",
      "ai": "string - Câu trả lời của AI từ lần tương tác trước"
    }
  ]
}
```

### Response Format

```json
{
  "result": "successfully",
  "status": 200,
  "output": {
    "user_answer": false,
    "response": [
      {
        "type": "text",
        "content": "Nội dung câu trả lời từ chatbot",
        "recommendations": [
          {
            "procedure_id": "1.001193",
            "name": "Tên thủ tục hành chính"
          }
        ]
      }
    ]
  }
}
```

---

## 5. Định dạng Audio được hỗ trợ

- **MIME Types:** 
  - audio/webm
  - video/webm (Android)
  - audio/mp4 (iOS Safari/Chrome)
  - audio/m4a (iOS/Mac)
  - audio/x-m4a
  - audio/aac

- **Extensions:**
  - .webm
  - .mp4
  - .m4a
  - .aac

---

## 6. Ghi chú quan trọng

1. **Chat History:** Tối đa lưu 6 tin nhắn gần nhất trong lịch sử
2. **Text hoặc Audio:** Phải gửi ít nhất một trong hai (text hoặc audio_file)
3. **Content-Type:** 
   - Khi gửi JSON: sử dụng `Content-Type: application/json`
   - Khi gửi form: sử dụng `multipart/form-data`
4. **Error Handling:** Nếu không gửi text và audio sẽ nhận lỗi:
   ```json
   {
     "detail": "Phải gửi ít nhất text hoặc audio file"
   }
   ```
