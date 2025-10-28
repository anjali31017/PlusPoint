from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MYSQL_USER: str
    # MYSQL_PASSWORD: str
    # MYSQL_HOST: str
    # MYSQL_PORT: int
    # MYSQL_DB: str

    MONGO_HOST: str
    MONGO_PORT: str
    MONGO_USER: str
    MONGO_PASSWORD: str
    MONGO_DB_NAME: str

    APP_NAME: str 
    DEBUG: bool 

    #jwt
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    #Oauth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GITHUB_CLIENT_ID: str   
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str

    
    API_PREFIX: str
    @property
    def MYSQL_URI(self):
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
