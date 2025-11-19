from pydub import AudioSegment
from io import BytesIO
import wave

def convert_audio(audio_bytes: bytes):
    audio = AudioSegment.from_file(BytesIO(audio_bytes))

    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

    raw = audio.raw_data

    buffer = BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)         
        wav_file.setsampwidth(2)          
        wav_file.setframerate(16000)      
        wav_file.writeframes(raw)

    return buffer.getvalue()