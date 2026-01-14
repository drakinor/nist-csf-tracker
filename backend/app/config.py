from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    database_url: str = "sqlite:///../../data/nist_csf_tracker.db"
    artifacts_path: str = "../../data/artifacts"
    feature_llm: bool = False
    ollama_url: str = "http://localhost:11434"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    @property
    def artifacts_path_absolute(self) -> Path:
        """Get absolute path to artifacts directory."""
        base = Path(__file__).parent.parent
        artifacts = (base / self.artifacts_path).resolve()
        artifacts.mkdir(parents=True, exist_ok=True)
        return artifacts
    
    @property
    def database_path_absolute(self) -> Path:
        """Get absolute path to database file."""
        base = Path(__file__).parent.parent
        # Extract path from sqlite:/// URL
        db_path = self.database_url.replace("sqlite:///", "")
        return (base / db_path).resolve()


# Global settings instance
settings = Settings()
