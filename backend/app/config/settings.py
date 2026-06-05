from functools import lru_cache
import os
from pathlib import Path

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # pragma: no cover
    BaseSettings = object
    SettingsConfigDict = None


class Settings(BaseSettings):
    app_name: str = "MinePredict"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_url: str = "http://localhost:3000"
    # Production CORS origins (for Render + Vercel)
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    data_raw_dir: Path = Path("data/raw")
    data_processed_dir: Path = Path("data/processed")
    model_dir: Path = Path("backend/saved_models")
    log_level: str = "INFO"
    training_max_rows: int = 60000
    cache_ttl_seconds: int = 300
    enable_rate_limiting: bool = True

    if SettingsConfigDict is not None:
        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def __init__(self, **kwargs):
        if BaseSettings is not object:
            super().__init__(**kwargs)
            return
        for name, default in self.__class__.__dict__.items():
            if name.startswith("_") or callable(default) or name == "model_config":
                continue
            value = kwargs.get(name, os.getenv(name.upper(), default))
            if isinstance(default, Path):
                value = Path(value)
            elif isinstance(default, int):
                value = int(value)
            elif isinstance(default, bool):
                value = value == "True" if isinstance(value, str) else bool(value)
            setattr(self, name, value)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_raw_dir.mkdir(parents=True, exist_ok=True)
    settings.data_processed_dir.mkdir(parents=True, exist_ok=True)
    settings.model_dir.mkdir(parents=True, exist_ok=True)
    return settings
