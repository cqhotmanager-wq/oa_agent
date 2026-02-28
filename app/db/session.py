"""数据库会话与引擎：创建引擎、会话工厂、初始化表、FastAPI 依赖 get_db。"""
import sys
from pathlib import Path

# 保证项目根在 path 中，便于 config 导入
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

try:
    from config.settings import settings
    DATABASE_URL = settings.database_url
except Exception:
    DATABASE_URL = "sqlite:///./oa_agent.db"


def get_engine(url: str = None):
    """根据 URL 创建引擎：SQLite 需 check_same_thread=False，其他库用 pool_pre_ping。"""
    url = url or DATABASE_URL
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True, echo=False)


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """根据 ORM 模型创建所有表（若不存在）。"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI 依赖：每次请求一个会话，请求结束后关闭。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
