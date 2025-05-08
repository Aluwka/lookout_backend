from pydantic_settings import BaseSettings
from authx import AuthX, AuthXConfig, RequestToken

class Settings(BaseSettings):
    # Database
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str = "database"

    # Redis
    redis_host: str
    redis_port: int

    # JWT
    jwt_secret: str

    # S3
    s3_access_key: str
    s3_secret_key: str
    s3_bucket_name: str
    s3_region_name: str = "us-east-1"

    class Config:
        env_file = ".env"


    def db_async_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def db_sync_url(self):
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    
    def redis_url(self, db: int = 0):
        return f"redis://{self.redis_host}:{self.redis_port}/{db}"
    



    
settings = Settings()

auth_settings = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=settings.jwt_secret,
    JWT_TOKEN_LOCATION=["cookies", "headers"],
    JWT_COOKIE_CSRF_PROTECT=False
)


