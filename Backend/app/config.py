from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "FastAPI Admin API"
    admin_api_key: str = "super_secret_api_key" # TODO: Change this to an actual secret key

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
