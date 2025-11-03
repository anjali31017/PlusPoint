from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MYSQL_USER: str
    # MYSQL_PASSWORD: str
    # MYSQL_HOST: str
    # MYSQL_PORT: int
    # MYSQL_DB: str

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
