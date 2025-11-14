import io

import librosa
import soundfile as sf
from omnilingual_asr.models.inference.pipeline import ASRInferencePipeline
from typing import Dict, Optional

from core import llm
from utils.get_prompt import get_prompt_by_task

pipe = ASRInferencePipeline(model_card="omniASR_CTC_7B")
class ChatService:
    @staticmethod
    def multiMediaInput(audio_file_bytes: bytes = None, text: str = None) -> str:
        """
        Nhận audio bytes hoặc text, trả về text.
        """
        if text:
            return text
        if audio_file_bytes:
            audio_buffer = io.BytesIO(audio_file_bytes)
            y, sr = librosa.load(audio_buffer, sr=16000)
            chunk_length_sec = 40
            chunk_size = chunk_length_sec * sr
            chunks = [y[i:i+chunk_size] for i in range(0, len(y), chunk_size)]
            lang_codes = ["vie_Latn"] * len(chunks)
            texts = pipe.transcribe(chunks, lang=lang_codes)
            return " ".join(texts)
        raise ValueError("Phải gửi ít nhất text hoặc audio file")

    @staticmethod
    def getChatCompletion(task: str, params: Dict[str, str]):
        prompt, parser = ChatService.getPromptByTask(task=task)

        chain = prompt | llm | parser
        response = chain.invoke(params).dict()
        return response

    @staticmethod
    def getChatStream(task: str, params: Dict[str, str]):
        prompt, parser = ChatService.getPromptByTask(task=task)

        chain = prompt | llm | parser
        for chunk in chain.stream(params):
            yield chunk

    @staticmethod
    def getPromptByTask(task: str):
        return get_prompt_by_task(task)