import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# SQLite 数据库配置 - 无需安装，开箱即用
DATABASE_DIR = os.path.expanduser("~/Documents/家庭账本")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/family_account_book.db"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 设置为 True 可查看 SQL 语句
    pool_pre_ping=True,  # 检查连接是否有效
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """获取数据库会话"""
    return SessionLocal()


def create_database():
    """SQLite 不需要预先创建数据库，文件会自动创建"""
    pass


def create_tables():
    """创建所有表"""
    from family_account_book.models import Base

    Base.metadata.create_all(bind=engine)


def init_db():
    """初始化数据库"""
    create_database()
    create_tables()
