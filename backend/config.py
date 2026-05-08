from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv() 
import os


class Settings(BaseSettings):
   
    DATABASE_URL: str = os.getenv("DATABASE_URL")    
    APP_HOST: str = os.getenv("APP_HOST")
    APP_PORT: int = int(os.getenv("APP_PORT"))
    DEBUG: bool = False
    DETECTION_CONFIDENCE: float = float(os.getenv("DETECTION_CONFIDENCE", "0.5"))
    FRAME_SKIP: int = int(os.getenv("FRAME_SKIP", "1"))
    BOX_COLOR: str = os.getenv("BOX_COLOR", "#00FF00")
    BOX_THICKNESS: int = int(os.getenv("BOX_THICKNESS", "3"))

    class Config:
        env_file = ".env"


settings = Settings()