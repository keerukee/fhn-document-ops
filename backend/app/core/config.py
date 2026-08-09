import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FHN Document Ops API"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "supersecretkey-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    USE_MOCK_DB: bool = os.getenv("USE_MOCK_DB", "True").lower() == "true"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./fhn_mock.db") 
    
    # Expiration
    DEFAULT_LINK_EXPIRATION_DAYS: int = int(os.getenv("DEFAULT_LINK_EXPIRATION_DAYS", "7"))
    
    # Azure Settings
    USE_MOCK_STORAGE: bool = os.getenv("USE_MOCK_STORAGE", "True").lower() == "true"
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_STORAGE_CONTAINER_NAME: str = os.getenv("AZURE_STORAGE_CONTAINER_NAME", "documents")
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
    AZURE_DOCUMENT_INTELLIGENCE_KEY: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")
    AZURE_FOUNDRY_URL: str = os.getenv("AZURE_FOUNDRY_URL", "")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_UPLOAD_TOPIC: str = os.getenv("KAFKA_UPLOAD_TOPIC", "fhn.docops.upload")

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
