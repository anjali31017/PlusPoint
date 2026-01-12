from pydantic_settings import BaseSettings
import os
from typing import ClassVar

class Settings(BaseSettings):
    
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str

    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB_NAME: str
    MONGO_PORT: str
    MONGODB_URI: str
    
    APP_NAME: str 
    DEBUG: bool 

    #jwt
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    
    BASE_DIR: ClassVar[str] = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    KYC_UPLOAD_FOLDER: ClassVar[str] = os.path.join(BASE_DIR, "images", "kyc")

    KYC_FINGERPRINT_SECRET: str


    #kafka
    # KAFKA_BROKER_ID: str
    # KAFKA_ZOOKEEPER_CONNECT: str
    # KAFKA_LISTENERS: str
    # KAFKA_ADVERTISED_LISTENERS: str
    # KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: str
    # KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: str
    # KAFKA_INTER_BROKER_LISTENER_NAME: str
    # KAFKA_LOG_RETENTION_HOURS: str
    KAFKA_BOOTSTRAP_SERVERS: str

    
    #Oauth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GITHUB_CLIENT_ID: str   
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str

    
    API_PREFIX: str
    WS_PREFIX: str

    class Config:
        env_file = "backend/.env"


settings = Settings()
