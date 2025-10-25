from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# MySQL 数据库连接配置
DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3306/family_account_book"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 设置为 True 可查看 SQL 语句
    pool_pre_ping=True,  # 检查连接是否有效
    pool_recycle=3600,  # 连接回收时间（秒）
)

# 创建不指定数据库的引擎，用于创建数据库
ADMIN_DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3306"
admin_engine = create_engine(ADMIN_DATABASE_URL, echo=False)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """获取数据库会话"""
    return SessionLocal()


def create_database():
    """创建数据库（如果不存在）"""
    try:
        with admin_engine.connect() as conn:
            conn.execute(
                text(
                    "CREATE DATABASE IF NOT EXISTS family_account_book CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            )
            conn.commit()
    except Exception as e:
        print(f"创建数据库失败: {e}")
        raise


def create_tables():
    """创建所有表"""
    from family_account_book.models import Base

    Base.metadata.create_all(bind=engine)


def init_db():
    """初始化数据库"""
    create_database()
    create_tables()
