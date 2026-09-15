from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/secureproof.db"
    upload_dir: Path = Path("./data/evidence")
    max_upload_bytes: int = 5 * 1024 * 1024
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    ai_provider: str = "local"
    blockchain_mode: str = "memory"
    blockchain_rpc_url: str | None = None
    blockchain_private_key: str | None = None
    contract_address: str | None = None
    chain_id: int = 31337

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
