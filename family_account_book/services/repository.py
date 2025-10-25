from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from family_account_book.models import Category, Person, Transaction


class TransactionService:
    """交易服务类，处理交易的增删改查"""

    def __init__(self, db: Session):
        self.db = db

    def create_expense(
        self,
        date: datetime,
        amount: float,
        description: str,
        category_name: str,
        person_name: Optional[str] = None,
    ) -> Transaction:
        """
        创建支出交易

        Args:
            date: 交易日期
            amount: 金额
            description: 描述
            category_name: 分类名称
            person_name: 支出者名称（可选）

        Returns:
            创建的交易对象
        """
        # 获取或创建分类
        category = self._get_or_create_category(category_name)

        # 获取人员（如果提供）
        person = None
        if person_name:
            person = self._get_or_create_person(person_name)

        transaction = Transaction(
            date=date,
            amount=amount,
            transaction_type="expense",
            description=description,
            category_id=category.id,
            person_id=person.id if person else None,
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def create_income(
        self,
        date: datetime,
        amount: float,
        description: str,
        category_name: str,
        person_name: Optional[str] = None,
    ) -> Transaction:
        """
        创建收入交易

        Args:
            date: 交易日期
            amount: 金额
            description: 描述
            category_name: 分类名称
            person_name: 收入者名称（可选）

        Returns:
            创建的交易对象
        """
        # 获取或创建分类
        category = self._get_or_create_category(category_name)

        # 获取人员（如果提供）
        person = None
        if person_name:
            person = self._get_or_create_person(person_name)

        transaction = Transaction(
            date=date,
            amount=amount,
            transaction_type="income",
            description=description,
            category_id=category.id,
            person_id=person.id if person else None,
        )

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_transactions(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        transaction_type: Optional[str] = None,
        category_name: Optional[str] = None,
    ) -> List[Transaction]:
        """
        查询交易记录

        Args:
            start_date: 开始日期
            end_date: 结束日期
            transaction_type: 交易类型 ('income' 或 'expense')
            category_name: 分类名称

        Returns:
            交易列表
        """
        query = self.db.query(Transaction)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        if category_name:
            # 查找分类
            category = (
                self.db.query(Category).filter(Category.name == category_name).first()
            )
            if category:
                query = query.filter(Transaction.category_id == category.id)

        return query.order_by(Transaction.date.desc()).all()

    def update_transaction(
        self, transaction_id: int, **kwargs
    ) -> Optional[Transaction]:
        """
        更新交易

        Args:
            transaction_id: 交易ID
            **kwargs: 要更新的字段

        Returns:
            更新后的交易对象
        """
        transaction = (
            self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        )
        if not transaction:
            return None

        for key, value in kwargs.items():
            if key == "category_name" and value:
                category = self._get_or_create_category(value)
                setattr(transaction, "category_id", category.id)
            elif key == "person_name" and value:
                person = self._get_or_create_person(value)
                setattr(transaction, "person_id", person.id)
            elif hasattr(transaction, key):
                setattr(transaction, key, value)

        transaction.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete_transaction(self, transaction_id: int) -> bool:
        """
        删除交易

        Args:
            transaction_id: 交易ID

        Returns:
            是否删除成功
        """
        transaction = (
            self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
        )
        if not transaction:
            return False

        self.db.delete(transaction)
        self.db.commit()
        return True

    def _get_or_create_category(self, category_name: str) -> Category:
        """获取或创建分类"""
        category = (
            self.db.query(Category).filter(Category.name == category_name).first()
        )
        if not category:
            category = Category(name=category_name)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
        return category

    def _get_or_create_person(self, person_name: str) -> Person:
        """获取或创建人员"""
        person = self.db.query(Person).filter(Person.name == person_name).first()
        if not person:
            person = Person(name=person_name)
            self.db.add(person)
            self.db.commit()
            self.db.refresh(person)
        return person


class CategoryService:
    """分类服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_categories(self) -> List[Category]:
        """获取所有分类"""
        return self.db.query(Category).order_by(Category.name).all()

    def create_category(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
    ) -> Category:
        """创建分类"""
        category = Category(name=name, description=description, parent_id=parent_id)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int) -> bool:
        """删除分类（如果没有关联交易）"""
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False

        # 检查是否有关联交易
        transaction_count = (
            self.db.query(Transaction)
            .filter(Transaction.category_id == category_id)
            .count()
        )

        if transaction_count > 0:
            return False  # 不能删除有交易的分类

        self.db.delete(category)
        self.db.commit()
        return True


class PersonService:
    """人员服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_persons(self) -> List[Person]:
        """获取所有人员"""
        return self.db.query(Person).order_by(Person.name).all()

    def create_person(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> Person:
        """创建人员"""
        person = Person(name=name, description=description)
        self.db.add(person)
        self.db.commit()
        self.db.refresh(person)
        return person

    def delete_person(self, person_id: int) -> bool:
        """删除人员（如果没有关联交易）"""
        person = self.db.query(Person).filter(Person.id == person_id).first()
        if not person:
            return False

        # 检查是否有关联交易
        transaction_count = (
            self.db.query(Transaction)
            .filter(Transaction.person_id == person_id)
            .count()
        )

        if transaction_count > 0:
            return False  # 不能删除有交易的人员

        self.db.delete(person)
        self.db.commit()
        return True
