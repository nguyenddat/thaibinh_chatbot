import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Setting(BaseSettings):
    # directory
    base_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    artifact_dir: str = os.path.join(base_dir, 'artifacts')
    log_dir: str = os.path.join(base_dir, 'logs')
    
    log_file: str = os.path.join(log_dir, 'backend.log')
    
    # database
    database_url: str = os.getenv('DATABASE_URL', '')
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_collection_name: str = os.getenv("QDRANT_COLLECTION_NAME", "Chatbot-Thaibinh")

    # types
    allowed_mimes: set[str] = {"audio/webm", "video/webm", "audio/mp4", "audio/m4a",    
                               "audio/x-m4a", "audio/aac", "audio/mpeg", "audio/wav", "audio/mp3"}
    allowed_exts: set[str] = {"webm", "mp4", "m4a", "aac"}
    
    class Config:
        env_file = ".env"
        extra = "ignore"

setting = Setting()
os.makedirs(setting.artifact_dir, exist_ok=True)
os.makedirs(setting.log_dir, exist_ok=True)