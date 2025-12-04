history_prompt = """
You are a smart virtual assistant. Your task is to summarize the conversation provided.
You will receive questions and corresponding answers sequentially.

Conversation:
{question}

Return the result in JSON format according to the specified schema:
quesion: str = Field(..., description = "Summary of the conversation and user questions in Vietnamese")
response: str = Field(..., description = "Summary of the conversation and corresponding answers in Vietnamese")
"""