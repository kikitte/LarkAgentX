"""
Database session management and initialization
"""
from loguru import logger
from app.db.models import Base
from app.config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

def init_db():
    """初始化数据库，如果不存在则创建"""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f"初始化数据库时出错: {str(e)}")
        raise

def get_db_session():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise

def close_db_session(db):
    """关闭数据库会话"""
    if db:
        db.close() 