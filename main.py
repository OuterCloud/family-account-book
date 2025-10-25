#!/usr/bin/env python3
"""
家庭账本应用主程序
"""

from family_account_book.database import init_db
from family_account_book.views.main_window import main


def main_app():
    """主应用入口"""
    # 初始化数据库
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成")

    # 启动 GUI 应用
    print("启动家庭账本应用...")
    main()


if __name__ == "__main__":
    main_app()
