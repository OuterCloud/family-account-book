import csv
import os
from datetime import date
from typing import List

import pandas as pd

from family_account_book.models import Transaction


class ExportService:
    """数据导出服务"""

    def __init__(self, db_session):
        self.db = db_session

    def export_to_csv(self, transactions: List[Transaction], filename: str) -> str:
        """
        导出交易记录到 CSV 文件

        Args:
            transactions: 交易记录列表
            filename: 输出文件名（不含扩展名）

        Returns:
            输出文件路径
        """
        output_file = f"{filename}.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["日期", "类型", "分类", "金额", "描述"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 写入表头
            writer.writeheader()

            # 写入数据
            for transaction in transactions:
                row = {
                    "日期": transaction.date.strftime("%Y-%m-%d"),
                    "类型": "收入"
                    if transaction.transaction_type == "income"
                    else "支出",
                    "分类": transaction.category.name if transaction.category else "",
                    "金额": f"{transaction.amount:.2f}",
                    "描述": transaction.description,
                }
                writer.writerow(row)

        return output_file

    def export_to_excel(self, transactions: List[Transaction], filename: str) -> str:
        """
        导出交易记录到 Excel 文件

        Args:
            transactions: 交易记录列表
            filename: 输出文件名（不含扩展名）

        Returns:
            输出文件路径
        """
        output_file = f"{filename}.xlsx"

        # 准备数据
        data = []
        for transaction in transactions:
            row = {
                "日期": transaction.date.strftime("%Y-%m-%d"),
                "类型": "收入" if transaction.transaction_type == "income" else "支出",
                "分类": transaction.category.name if transaction.category else "",
                "金额": transaction.amount,
                "描述": transaction.description,
            }
            data.append(row)

        # 创建 DataFrame 并导出
        df = pd.DataFrame(data)
        df.to_excel(output_file, index=False, engine="openpyxl")

        return output_file

    def export_monthly_report(self, year: int, month: int, filename: str) -> str:
        """
        导出月度报告

        Args:
            year: 年份
            month: 月份
            filename: 输出文件名（不含扩展名）

        Returns:
            输出文件路径
        """
        output_file = f"{filename}_monthly_report.xlsx"

        # 获取月度数据
        from ..services.analytics import AnalyticsService

        analytics = AnalyticsService(self.db)
        monthly_data = analytics.monthly_aggregation(year, month)

        # 准备数据
        summary_data = []
        for category_name, amount in monthly_data.items():
            summary_data.append(
                {
                    "分类": category_name,
                    "金额": amount,
                    "占比": f"{(amount / monthly_data.get('total', 1) * 100):.1f}%"
                    if category_name != "total"
                    else "",
                }
            )

        # 创建 Excel 文件
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            # 汇总表
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name="月度汇总", index=False)

            # 详细交易记录
            start_date = date(year, month, 1)
            end_date = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

            from ..services.repository import TransactionService

            transaction_service = TransactionService(self.db)
            transactions = transaction_service.get_transactions(
                start_date=start_date, end_date=end_date
            )

            detail_data = []
            for transaction in transactions:
                detail_data.append(
                    {
                        "日期": transaction.date.strftime("%Y-%m-%d"),
                        "类型": "收入"
                        if transaction.transaction_type == "income"
                        else "支出",
                        "分类": transaction.category.name
                        if transaction.category
                        else "",
                        "金额": transaction.amount,
                        "描述": transaction.description,
                    }
                )

            detail_df = pd.DataFrame(detail_data)
            detail_df.to_excel(writer, sheet_name="交易明细", index=False)

        return output_file

    def get_export_directory(self) -> str:
        """获取导出目录"""
        export_dir = "exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        return export_dir
