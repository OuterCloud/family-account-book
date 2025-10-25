from datetime import date
from typing import Dict, List, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from family_account_book.models import Transaction


class AnalyticsService:
    """分析服务类，提供各种数据分析功能"""

    def __init__(self, db: Session):
        self.db = db

    def monthly_aggregation(self, year: int, month: int) -> Dict[str, float]:
        """
        月度支出统计，返回总支出和各分类支出

        Args:
            year: 年份
            month: 月份

        Returns:
            包含 'total' 和各分类名称及金额的字典
        """
        # 查询指定月份的支出交易
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)

        query = (
            self.db.query(
                Transaction.category_id,
                func.sum(Transaction.amount).label("total_amount"),
            )
            .filter(
                Transaction.transaction_type == "expense",
                Transaction.date >= start_date,
                Transaction.date < end_date,
            )
            .group_by(Transaction.category_id)
        )

        results = query.all()

        # 获取分类名称
        from ..models import Category

        category_totals = {}
        total_expense = 0.0

        for category_id, amount in results:
            if category_id:
                category = (
                    self.db.query(Category).filter(Category.id == category_id).first()
                )
                if category:
                    category_totals[category.name] = float(amount)
                    total_expense += float(amount)

        category_totals["total"] = total_expense
        return category_totals

    def category_sum_in_range(
        self, category_name: str, start_date: date, end_date: date
    ) -> float:
        """
        计算指定分类在时间段内的总支出

        Args:
            category_name: 分类名称
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            总支出金额
        """
        from ..models import Category

        # 查找分类
        category = (
            self.db.query(Category).filter(Category.name == category_name).first()
        )
        if not category:
            return 0.0

        # 查询该分类在时间段内的支出总和
        result = (
            self.db.query(func.sum(Transaction.amount))
            .filter(
                Transaction.transaction_type == "expense",
                Transaction.category_id == category.id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
            )
            .scalar()
        )

        return float(result) if result else 0.0

    def per_month_series_for_category(
        self,
        category_name: str,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
    ) -> List[Tuple[int, int, float]]:
        """
        获取指定分类的月度支出序列

        Args:
            category_name: 分类名称
            start_year: 开始年份
            start_month: 开始月份
            end_year: 结束年份
            end_month: 结束月份

        Returns:
            列表，每个元素为 (年, 月, 金额) 的元组
        """
        from ..models import Category

        # 查找分类
        category = (
            self.db.query(Category).filter(Category.name == category_name).first()
        )
        if not category:
            return []

        # 生成月份序列
        series = []
        current_year = start_year
        current_month = start_month

        while (current_year < end_year) or (
            current_year == end_year and current_month <= end_month
        ):
            # 计算该月的开始和结束日期
            month_start = date(current_year, current_month, 1)
            if current_month == 12:
                month_end = date(current_year + 1, 1, 1)
            else:
                month_end = date(current_year, current_month + 1, 1)

            # 查询该月该分类的支出总和
            result = (
                self.db.query(func.sum(Transaction.amount))
                .filter(
                    Transaction.transaction_type == "expense",
                    Transaction.category_id == category.id,
                    Transaction.date >= month_start,
                    Transaction.date < month_end,
                )
                .scalar()
            )

            amount = float(result) if result else 0.0
            series.append((current_year, current_month, amount))

            # 移动到下一个月
            if current_month == 12:
                current_year += 1
                current_month = 1
            else:
                current_month += 1

        return series

    def get_category_percentage(
        self, category_name: str, year: int, month: int
    ) -> float:
        """
        计算指定分类在月度支出中的百分比

        Args:
            category_name: 分类名称
            year: 年份
            month: 月份

        Returns:
            百分比（0-100）
        """
        monthly_data = self.monthly_aggregation(year, month)
        total_expense = monthly_data.get("total", 0.0)
        category_expense = monthly_data.get(category_name, 0.0)

        if total_expense == 0:
            return 0.0

        return (category_expense / total_expense) * 100
