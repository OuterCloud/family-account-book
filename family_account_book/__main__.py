#!/usr/bin/env python3
"""
家庭账本应用包入口
"""

from .database import init_db
from .views.main_window import main as start_gui


def main():
    """主应用入口"""
    # 初始化数据库
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成")

    # 启动 GUI 应用
    print("启动家庭账本应用...")
    start_gui()


if __name__ == "__main__":
    main()
