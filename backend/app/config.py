from pydantic_settings import BaseSettings

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
    
    
    #kafka
    KAFKA_BOOTSTRAP_SERVERS=str
    KAFKA_BROKER_ID=int
    KAFKA_ZOOKEEPER_CONNECT=str
    KAFKA_ADVERTISED_LISTENERS=str
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=str
    
    #Oauth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GITHUB_CLIENT_ID: str   
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str

    
    API_PREFIX: str

    class Config:
        env_file = ".env"

settings = Settings()
