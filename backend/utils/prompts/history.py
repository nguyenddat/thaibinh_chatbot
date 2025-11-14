history_prompt = """
Bạn là một trợ lý ảo thông minh. Nhiệm vụ của bạn là tóm tắt cuộc hội thoại mà chúng tôi cung cấp.
Bạn sẽ nhận được lần lượt các câu hỏi và câu trả lời tương ứng.

Cuộc hội thoại:
{question}

Hãy trả về kết quả dưới dạng JSON theo schema chỉ định:
quesion: str = Field(..., description = "Tóm tắt cuộc trò chuyện và các câu hỏi của người dùng")
response: str = Field(..., description = "Tóm tắt cuộc trò chuyện và các câu trả lời tương ứng")
"""