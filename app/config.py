import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Smart Recipe & Fridge Manager"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smart_recipe.db")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()