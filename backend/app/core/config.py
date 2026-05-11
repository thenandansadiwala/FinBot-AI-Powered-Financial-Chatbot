import os
from dotenv import load_dotenv

load_dotenv()

# Map the .env variables to the standard names expected by LangChain's Azure classes
if "AZURE_AI_ENDPOINT" in os.environ and "AZURE_OPENAI_ENDPOINT" not in os.environ:
    os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ["AZURE_AI_ENDPOINT"]
if "AZURE_AI_API_KEY" in os.environ and "AZURE_OPENAI_API_KEY" not in os.environ:
    os.environ["AZURE_OPENAI_API_KEY"] = os.environ["AZURE_AI_API_KEY"]

class Settings:
    SYNC_DB_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/financial_bot_db")
    ASYNC_DB_URL: str = os.getenv("ASYNC_DATABASE_URL", "postgresql+asyncpg://postgres:root@localhost:5432/financial_bot_db")
    
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")

settings = Settings()
