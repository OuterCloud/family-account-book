from datetime import datetime
from typing import List, Tuple
from family_account_book.database import get_db
from family_account_book.services.repository import TransactionService, CategoryService
from family_account_book.services.analytics import AnalyticsService


class AccountBookController:
    """家庭账本控制器"""

    def __init__(self):
        self.db = next(get_db())
        self.transaction_service = TransactionService(self.db)
        self.category_service = CategoryService(self.db)
        self.analytics_service = AnalyticsService(self.db)

    def record_expense(
        self, date: datetime, amount: float, description: str, category_name: str
    ):
        """记录支出"""
        return self.transaction_service.create_expense(
            date, amount, description, category_name
        )

    def record_income(
        self,
        date: datetime,
        gross_amount: float,
        description: str,
        deductions: List[Tuple[str, float]],
    ):
        """记录收入"""
        return self.transaction_service.create_income(
            date, gross_amount, description, deductions
        )

    def get_monthly_stats(self, year: int, month: int):
        """获取月度统计"""
        return self.analytics_service.monthly_aggregation(year, month)

    def get_category_sum_in_range(self, category_name: str, start_date, end_date):
        """获取分类在时间段内的总支出"""
        return self.analytics_service.category_sum_in_range(
            category_name, start_date, end_date
        )

    def get_monthly_series_for_category(
        self,
        category_name: str,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
    ):
        """获取分类的月度支出序列"""
        return self.analytics_service.per_month_series_for_category(
            category_name, start_year, start_month, end_year, end_month
        )

    def get_transactions(
        self, start_date=None, end_date=None, transaction_type=None, category_name=None
    ):
        """获取交易记录"""
        return self.transaction_service.get_transactions(
            start_date, end_date, transaction_type, category_name
        )

    def get_categories(self):
        """获取所有分类"""
        return self.category_service.get_all_categories()

    def create_category(
        self, name: str, description: str = None, parent_id: int = None
    ):
        """创建分类"""
        return self.category_service.create_category(name, description, parent_id)

    def close(self):
        """关闭数据库连接"""
        if self.db:
            self.db.close()
