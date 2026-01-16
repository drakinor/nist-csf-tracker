# config.py
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    database_url: str = f"sqlite:///{BASE_DIR}/data/nist_csf_tracker.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    artifact_storage_path: str = str(BASE_DIR / "data" / "artifacts")
    feature_llm: bool = False
    ollama_url: str = "http://localhost:11434"
    
    @property
    def artifacts_path_absolute(self) -> Path:
        """Return absolute path to artifacts directory as Path object."""
        return Path(self.artifact_storage_path).resolve()

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()
