from datetime import date
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from family_account_book.services.analytics import AnalyticsService


class TestAnalyticsService:
    """测试分析服务"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def analytics_service(self, mock_db):
        """创建分析服务实例"""
        return AnalyticsService(mock_db)

    def test_monthly_aggregation_no_data(self, analytics_service, mock_db):
        """测试月度聚合 - 无数据"""
        # 模拟查询返回空结果
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []

        result = analytics_service.monthly_aggregation(2023, 10)

        assert result == {"total": 0.0}
        assert mock_db.query.called

    def test_monthly_aggregation_with_data(self, analytics_service, mock_db):
        """测试月度聚合 - 有数据"""
        # 模拟分类查询
        mock_category = Mock()
        mock_category.name = "餐饮"
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_category
        )

        # 模拟交易查询结果 - 只有一个分类
        mock_result = [(1, 100.0)]
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = mock_result

        result = analytics_service.monthly_aggregation(2023, 10)

        assert result["total"] == 100.0
        assert result["餐饮"] == 100.0
        assert len(result) == 2  # total + 1 category

    def test_category_sum_in_range_no_data(self, analytics_service, mock_db):
        """测试分类时间段总和 - 无数据"""
        # 模拟分类不存在
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = analytics_service.category_sum_in_range(
            "餐饮", date(2023, 1, 1), date(2023, 12, 31)
        )

        assert result == 0.0

    def test_category_sum_in_range_with_data(self, analytics_service, mock_db):
        """测试分类时间段总和 - 有数据"""
        # 模拟分类存在
        mock_category = Mock()
        mock_category.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_category
        )

        # 模拟总和查询
        mock_db.query.return_value.filter.return_value.scalar.return_value = 500.0

        result = analytics_service.category_sum_in_range(
            "餐饮", date(2023, 1, 1), date(2023, 12, 31)
        )

        assert result == 500.0

    def test_per_month_series_for_category_no_category(
        self, analytics_service, mock_db
    ):
        """测试月度序列 - 分类不存在"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = analytics_service.per_month_series_for_category(
            "餐饮", 2023, 1, 2023, 12
        )

        assert result == []

    def test_per_month_series_for_category_with_data(self, analytics_service, mock_db):
        """测试月度序列 - 有数据"""
        # 模拟分类存在
        mock_category = Mock()
        mock_category.id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_category
        )

        # 模拟每月查询返回不同金额
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [
            100.0,
            150.0,
            200.0,
        ]

        result = analytics_service.per_month_series_for_category(
            "餐饮", 2023, 1, 2023, 3
        )

        expected = [(2023, 1, 100.0), (2023, 2, 150.0), (2023, 3, 200.0)]
        assert result == expected

    def test_get_category_percentage_no_expense(self, analytics_service, mock_db):
        """测试分类百分比 - 无支出"""
        # 模拟月度聚合返回无数据
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []

        result = analytics_service.get_category_percentage("餐饮", 2023, 10)

        assert result == 0.0

    def test_get_category_percentage_with_data(self, analytics_service, mock_db):
        """测试分类百分比 - 有数据"""
        # 模拟分类查询
        mock_category = Mock()
        mock_category.name = "餐饮"
        mock_db.query.return_value.filter.return_value.first.return_value = (
            mock_category
        )

        # 模拟交易查询结果
        mock_result = [(1, 200.0)]  # 餐饮分类支出200
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = mock_result

        result = analytics_service.get_category_percentage("餐饮", 2023, 10)

        assert result == 100.0  # 200/200 = 100%
