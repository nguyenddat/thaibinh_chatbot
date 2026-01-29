import requests
import os
from typing import Dict
from io import BytesIO
from langchain_core.messages import HumanMessage, AIMessage

from core import llm, logger
from .get_prompt import get_prompt_by_task
from utils.convert import convert_audio

class LLMService:
    @staticmethod
    def get_chat_completion(task: str, params: Dict):
        prompt, parser = get_prompt_by_task(task)
        chain = prompt | llm | parser
        return chain.invoke(params).dict()
        
    @staticmethod
    def format_chat_history(chat_history):
        converted = []
        for message in chat_history:
            if message.get("human"):
                converted.append(HumanMessage(content=message["human"]))
            if message.get("ai"):
                converted.append(AIMessage(content=""))
        return converted


    @staticmethod
    def transcribe(audio_bytes: bytes) -> str:
        processed = convert_audio(audio_bytes)

        url = "https://api.openai.com/v1/audio/transcriptions"
        files = {
            "file": ("audio.wav", BytesIO(processed), "audio/wav")
        }
        data = {"model": "whisper-1", "language": "vi"}
        headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}

        resp = requests.post(url, data=data, files=files, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Whisper error {resp.status_code}: {resp.text}")

        return resp.json().get("text", "")