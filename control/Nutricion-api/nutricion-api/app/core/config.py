from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Nutricion API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None
    GOOGLE_POST_LOGIN_REDIRECT: str | None = "http://localhost:5173"
    GOOGLE_ALLOWED_REDIRECTS: str | None = None
    FIREBASE_CREDENTIALS_PATH: str | None = None
    FIREBASE_CREDENTIALS_JSON: str | None = None
    FIREBASE_PROJECT_ID: str | None = None

    ML_API_URL: str = "http://localhost:8001"
    ML_SERVICE_URL: str = "http://localhost:8001"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
