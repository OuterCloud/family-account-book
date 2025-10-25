#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加人员管理功能
"""

from sqlalchemy import create_engine, text
from family_account_book.database import DATABASE_URL


def migrate_database():
    """执行数据库迁移"""
    engine = create_engine(DATABASE_URL, echo=True)

    with engine.connect() as conn:
        try:
            print("开始数据库迁移...")

            # 检查是否已存在persons表
            result = conn.execute(text("SHOW TABLES LIKE 'persons'"))
            if not result.fetchone():
                print("创建persons表...")
                conn.execute(
                    text("""
                    CREATE TABLE persons (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                )
                conn.commit()
                print("persons表创建成功")
            else:
                print("persons表已存在")

            # 检查transactions表是否已有person_id列
            result = conn.execute(text("DESCRIBE transactions"))
            columns = [row[0] for row in result.fetchall()]

            if "person_id" not in columns:
                print("添加person_id列到transactions表...")
                conn.execute(
                    text("""
                    ALTER TABLE transactions
                    ADD COLUMN person_id INT,
                    ADD CONSTRAINT fk_transactions_person_id
                    FOREIGN KEY (person_id) REFERENCES persons(id) ON DELETE SET NULL
                """)
                )
                conn.commit()
                print("person_id列添加成功")
            else:
                print("person_id列已存在")

            print("数据库迁移完成！")

        except Exception as e:
            print(f"迁移失败: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()


if __name__ == "__main__":
    migrate_database()
