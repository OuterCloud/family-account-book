from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Person(Base):
    """人员模型"""

    __tablename__ = "persons"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # 关联交易
    transactions = relationship("Transaction", back_populates="person")

    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.name}')>"


class Category(Base):
    """支出分类模型"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    # 自引用关系，用于子分类
    parent = relationship("Category", remote_side=[id], backref="subcategories")
    transactions = relationship("Transaction", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Transaction(Base):
    """交易模型（收入和支出）"""

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)  # 'income' 或 'expense'
    description = Column(Text, nullable=False)
    category_id = Column(
        Integer, ForeignKey("categories.id"), nullable=True
    )  # 支出才有分类
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=True)  # 交易相关人员
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    category = relationship("Category", back_populates="transactions")
    person = relationship("Person", back_populates="transactions")
    income_details = relationship(
        "IncomeDetail", back_populates="transaction", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, type='{self.transaction_type}', amount={self.amount})>"


class IncomeDetail(Base):
    """收入明细模型（用于五险一金等扣除）"""

    __tablename__ = "income_details"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    item_name = Column(String(100), nullable=False)  # 如 '五险一金', '个税' 等
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    transaction = relationship("Transaction", back_populates="income_details")

    def __repr__(self):
        return f"<IncomeDetail(id={self.id}, item='{self.item_name}', amount={self.amount})>"
