from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define settings for database connection
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@db:5432/todo_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
