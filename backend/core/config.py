import os

from pydantic import BaseModel

class Setting(BaseModel):
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def artifact_dir(self):
        path = os.path.join(self.base_dir, "artifacts")
        return path


setting = Setting()
