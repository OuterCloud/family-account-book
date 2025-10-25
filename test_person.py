#!/usr/bin/env python3
"""
测试人员管理功能
"""

from family_account_book.database import get_db
from family_account_book.services.repository import PersonService


def test_person_service():
    """测试人员服务"""
    db = get_db()
    person_service = PersonService(db)

    try:
        print("测试人员服务...")

        # 获取现有人员
        existing_persons = person_service.get_all_persons()
        existing_names = {p.name for p in existing_persons}
        print(f"现有人员: {[p.name for p in existing_persons]}")

        # 创建测试人员（如果不存在）
        print("创建测试人员...")
        test_persons = []
        if "张三" not in existing_names:
            person1 = person_service.create_person("张三", "测试人员1")
            test_persons.append(person1)
        else:
            print("张三已存在，跳过创建")

        if "李四" not in existing_names:
            person2 = person_service.create_person("李四", "测试人员2")
            test_persons.append(person2)
        else:
            print("李四已存在，跳过创建")

        if test_persons:
            print(f"创建人员成功: {[p.name for p in test_persons]}")

        # 获取所有人员
        print("获取所有人员...")
        persons = person_service.get_all_persons()
        print(f"当前人员列表: {[p.name for p in persons]}")

        # 测试完成
        print("人员服务测试完成！")

    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_person_service()
