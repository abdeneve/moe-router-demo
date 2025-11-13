from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = 'local'
    openai_api_key: str = ''
    gemini_api_key: str = ''
    aistudio_api_key: str = ''
    sqlite_path: str = 'db/moe_router.sqlite'
    request_timeout_seconds: int = 30

    model_config = SettingsConfigDict(env_file='.env')


@lru_cache
def get_settings() -> Settings:
    return Settings()
