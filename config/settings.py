"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """App settings from env / .env."""

    # App
    app_name: str = "OA Agent"
    debug: bool = False

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None  # for proxy
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    # MySQL
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root123"
    mysql_database: str = "oa_agent"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )

    # Paths
    skills_dir: str = "skills"
    policies_dir: str = "policies"
    faiss_index_dir: str = "data/faiss"

    # RAG
    chunk_size: int = 500
    chunk_overlap: int = 50
    rag_top_k: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
