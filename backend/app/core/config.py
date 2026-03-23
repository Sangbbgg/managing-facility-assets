from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://assetuser:changeme@localhost:5432/assetdb"
    ASSET_PREFIX: str = "IC"

    class Config:
        env_file = ".env"


settings = Settings()
