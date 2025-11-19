from gtts import gTTS
from pydub import AudioSegment

# Câu muốn đọc
text = "Tôi muốn biết về thủ tục hưởng trợ cấp khi người có công."

# Tạo file mp3 bằng gTTS
tts = gTTS(text=text, lang='vi')
tts.save("tests/audio.mp3")

# Chuyển mp3 -> m4a
audio = AudioSegment.from_file("tests/audio.mp3", format="mp3")
audio.export("tests/audio.m4a", format="ipod")  # m4a
audio.export("tests/audio.webm", format="webm")  # webm
audio.export("tests/audio.wav", format="wav")    # wav

print("Tạo file audio thành công: audio.mp3, audio.m4a, audio.webm, audio.wav")