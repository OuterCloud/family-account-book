import sys
from datetime import datetime

import matplotlib
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

matplotlib.use("QtAgg")  # 使用QtAgg后端，兼容PyQt6
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from family_account_book.database import get_db
from family_account_book.services.analytics import AnalyticsService
from family_account_book.services.repository import (
    CategoryService,
    PersonService,
    TransactionService,
)


class MainWindow(QMainWindow):
    """主窗口"""

    # 中文字体列表
    CHINESE_FONTS = [
        "Songti SC",
        "STHeiti",
        "Yuanti SC",
        "Arial Unicode MS",
        "DejaVu Sans",
        "sans-serif",
    ]

    def __init__(self):
        super().__init__()
        # 设置matplotlib中文字体
        plt.rcParams["font.sans-serif"] = self.CHINESE_FONTS
        plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

        self.db = get_db()
        self.transaction_service = TransactionService(self.db)
        self.category_service = CategoryService(self.db)
        self.person_service = PersonService(self.db)
        self.analytics_service = AnalyticsService(self.db)

        # 存储历史记录的交易ID，用于编辑
        self.history_transaction_ids = []

        self.setWindowTitle("家庭账本应用")
        self.setGeometry(100, 100, 1200, 800)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # 记录标签页
        self.setup_record_tab()

        # 统计标签页
        self.setup_stats_tab()

        # 历史标签页
        self.setup_history_tab()

        # 人员标签页
        self.setup_person_tab()

    def setup_record_tab(self):
        """设置记录标签页"""
        record_tab = QWidget()
        self.tab_widget.addTab(record_tab, "记录")

        layout = QVBoxLayout(record_tab)

        # 支出记录组
        expense_group = QGroupBox("支出记录")
        expense_layout = QFormLayout(expense_group)

        self.expense_date_edit = QDateEdit()
        self.expense_date_edit.setDate(QDate.currentDate())
        expense_layout.addRow("日期:", self.expense_date_edit)

        self.expense_amount_edit = QLineEdit()
        expense_layout.addRow("金额:", self.expense_amount_edit)

        self.expense_category_combo = QComboBox()
        self.expense_category_combo.setEditable(True)
        expense_layout.addRow("分类:", self.expense_category_combo)

        self.expense_person_combo = QComboBox()
        self.expense_person_combo.setEditable(True)
        expense_layout.addRow("支出者:", self.expense_person_combo)

        self.expense_desc_edit = QTextEdit()
        self.expense_desc_edit.setMaximumHeight(60)
        expense_layout.addRow("描述:", self.expense_desc_edit)

        self.expense_button = QPushButton("记录支出")
        self.expense_button.clicked.connect(self.record_expense)
        expense_layout.addRow(self.expense_button)

        layout.addWidget(expense_group)

        # 收入记录组
        income_group = QGroupBox("收入记录")
        income_layout = QFormLayout(income_group)

        self.income_date_edit = QDateEdit()
        self.income_date_edit.setDate(QDate.currentDate())
        income_layout.addRow("日期:", self.income_date_edit)

        self.income_amount_edit = QLineEdit()
        income_layout.addRow("金额:", self.income_amount_edit)

        self.income_category_combo = QComboBox()
        self.income_category_combo.setEditable(True)
        income_layout.addRow("分类:", self.income_category_combo)

        self.income_person_combo = QComboBox()
        self.income_person_combo.setEditable(True)
        income_layout.addRow("收入者:", self.income_person_combo)

        self.income_desc_edit = QTextEdit()
        self.income_desc_edit.setMaximumHeight(60)
        income_layout.addRow("描述:", self.income_desc_edit)

        self.income_button = QPushButton("记录收入")
        self.income_button.clicked.connect(self.record_income)
        income_layout.addRow(self.income_button)

        layout.addWidget(income_group)

        layout.addStretch()

    def setup_stats_tab(self):
        """设置统计标签页"""
        stats_tab = QWidget()
        self.tab_widget.addTab(stats_tab, "统计")

        layout = QVBoxLayout(stats_tab)

        # 月份选择
        month_layout = QHBoxLayout()
        month_layout.addWidget(QLabel("选择月份:"))

        self.stats_year_combo = QComboBox()
        current_year = datetime.now().year
        for year in range(current_year - 2, current_year + 2):
            self.stats_year_combo.addItem(str(year))
        self.stats_year_combo.setCurrentText(str(current_year))
        month_layout.addWidget(self.stats_year_combo)

        self.stats_month_combo = QComboBox()
        for month in range(1, 13):
            self.stats_month_combo.addItem(f"{month:02d}")
        current_month = datetime.now().month
        self.stats_month_combo.setCurrentText(f"{current_month:02d}")
        month_layout.addWidget(self.stats_month_combo)

        self.refresh_stats_button = QPushButton("刷新统计")
        self.refresh_stats_button.clicked.connect(self.refresh_stats)
        month_layout.addWidget(self.refresh_stats_button)

        month_layout.addStretch()
        layout.addLayout(month_layout)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 统计表格
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setHorizontalHeaderLabels(["分类", "金额"])
        splitter.addWidget(self.stats_table)

        # 图表区域
        self.chart_canvas = FigureCanvas(Figure(figsize=(8, 4)))
        splitter.addWidget(self.chart_canvas)

        layout.addWidget(splitter)

    def setup_history_tab(self):
        """设置历史标签页"""
        history_tab = QWidget()
        self.tab_widget.addTab(history_tab, "历史")

        layout = QVBoxLayout(history_tab)

        # 过滤器
        filter_layout = QHBoxLayout()

        self.history_type_combo = QComboBox()
        self.history_type_combo.addItems(["全部", "收入", "支出"])
        filter_layout.addWidget(QLabel("类型:"))
        filter_layout.addWidget(self.history_type_combo)

        self.history_category_combo = QComboBox()
        self.history_category_combo.addItems(["全部"])
        filter_layout.addWidget(QLabel("分类:"))
        filter_layout.addWidget(self.history_category_combo)

        self.filter_button = QPushButton("筛选")
        self.filter_button.clicked.connect(self.filter_history)
        filter_layout.addWidget(self.filter_button)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # 历史表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(
            ["日期", "类型", "分类", "人员", "金额", "描述"]
        )
        # 使表格可编辑
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        layout.addWidget(self.history_table)

        # 编辑控制按钮
        edit_layout = QHBoxLayout()
        self.save_history_button = QPushButton("保存修改")
        self.save_history_button.clicked.connect(self.save_history_changes)
        edit_layout.addWidget(self.save_history_button)

        self.cancel_history_button = QPushButton("取消修改")
        self.cancel_history_button.clicked.connect(self.cancel_history_changes)
        edit_layout.addWidget(self.cancel_history_button)

        edit_layout.addStretch()
        layout.addLayout(edit_layout)

    def setup_person_tab(self):
        """设置人员标签页"""
        person_tab = QWidget()
        self.tab_widget.addTab(person_tab, "人员")

        layout = QVBoxLayout(person_tab)

        # 添加人员组
        add_group = QGroupBox("添加人员")
        add_layout = QFormLayout(add_group)

        self.person_name_edit = QLineEdit()
        add_layout.addRow("姓名:", self.person_name_edit)

        self.person_desc_edit = QTextEdit()
        self.person_desc_edit.setMaximumHeight(60)
        add_layout.addRow("描述:", self.person_desc_edit)

        self.add_person_button = QPushButton("添加人员")
        self.add_person_button.clicked.connect(self.add_person)
        add_layout.addRow(self.add_person_button)

        layout.addWidget(add_group)

        # 人员列表
        list_group = QGroupBox("人员列表")
        list_layout = QVBoxLayout(list_group)

        self.person_table = QTableWidget()
        self.person_table.setColumnCount(3)
        self.person_table.setHorizontalHeaderLabels(["ID", "姓名", "描述"])
        list_layout.addWidget(self.person_table)

        # 删除按钮
        self.delete_person_button = QPushButton("删除选中人员")
        self.delete_person_button.clicked.connect(self.delete_person)
        list_layout.addWidget(self.delete_person_button)

        layout.addWidget(list_group)

    def reload_categories(self):
        """重新加载分类列表"""
        categories = self.category_service.get_all_categories()
        self.expense_category_combo.clear()
        self.income_category_combo.clear()
        self.history_category_combo.clear()
        self.history_category_combo.addItem("全部")

        for category in categories:
            self.expense_category_combo.addItem(category.name)
            self.income_category_combo.addItem(category.name)
            self.history_category_combo.addItem(category.name)

    def reload_persons(self):
        """重新加载人员列表"""
        persons = self.person_service.get_all_persons()
        self.expense_person_combo.clear()
        self.income_person_combo.clear()

        for person in persons:
            self.expense_person_combo.addItem(person.name)
            self.income_person_combo.addItem(person.name)

    def load_data(self):
        """加载数据"""
        # 加载分类
        self.reload_categories()
        # 加载人员
        self.reload_persons()

        # 加载历史记录
        self.filter_history()

        # 加载统计
        self.refresh_stats()

        # 加载人员列表
        self.load_persons()

    def record_expense(self):
        """记录支出"""
        try:
            date = self.expense_date_edit.date().toPyDate()
            amount_text = self.expense_amount_edit.text().strip()
            category = self.expense_category_combo.currentText().strip()
            person = self.expense_person_combo.currentText().strip()
            description = self.expense_desc_edit.toPlainText().strip()

            if not amount_text or not category or not description:
                QMessageBox.warning(self, "输入错误", "请填写所有字段")
                return

            amount = float(amount_text)

            self.transaction_service.create_expense(
                date, amount, description, category, person_name=person
            )

            # 清空表单
            self.expense_amount_edit.clear()
            self.expense_desc_edit.clear()

            # 刷新数据
            self.load_data()

            QMessageBox.information(self, "成功", "支出记录成功")

        except ValueError:
            QMessageBox.warning(self, "输入错误", "金额格式不正确")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"记录失败: {str(e)}")

    def record_income(self):
        """记录收入"""
        try:
            date = self.income_date_edit.date().toPyDate()
            amount_text = self.income_amount_edit.text().strip()
            category = self.income_category_combo.currentText().strip()
            person = self.income_person_combo.currentText().strip()
            description = self.income_desc_edit.toPlainText().strip()

            if not amount_text or not category or not description:
                QMessageBox.warning(self, "输入错误", "请填写所有字段")
                return

            amount = float(amount_text)

            self.transaction_service.create_income(
                date, amount, description, category, person_name=person
            )

            # 清空表单
            self.income_amount_edit.clear()
            self.income_category_combo.setCurrentIndex(0)
            self.income_desc_edit.clear()

            # 刷新数据
            self.load_data()

            QMessageBox.information(self, "成功", "收入记录成功")

        except ValueError:
            QMessageBox.warning(self, "输入错误", "金额格式不正确")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"记录失败: {str(e)}")

    def refresh_stats(self):
        """刷新统计数据"""
        try:
            year = int(self.stats_year_combo.currentText())
            month = int(self.stats_month_combo.currentText())

            # 获取月度统计
            monthly_data = self.analytics_service.monthly_aggregation(year, month)

            # 更新表格
            self.stats_table.setRowCount(0)
            row = 0
            total = monthly_data.get("total", 0)

            # 添加总支出
            self.stats_table.insertRow(row)
            self.stats_table.setItem(row, 0, QTableWidgetItem("总支出"))
            self.stats_table.setItem(row, 1, QTableWidgetItem(f"¥{total:.2f}"))
            row += 1

            # 添加各分类
            for category_name, amount in monthly_data.items():
                if category_name != "total":
                    self.stats_table.insertRow(row)
                    self.stats_table.setItem(row, 0, QTableWidgetItem(category_name))
                    self.stats_table.setItem(row, 1, QTableWidgetItem(f"¥{amount:.2f}"))
                    row += 1

            # 更新图表
            self.update_chart(monthly_data)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新统计失败: {str(e)}")

    def update_chart(self, monthly_data):
        """更新图表"""
        self.chart_canvas.figure.clear()

        if not monthly_data or monthly_data.get("total", 0) == 0:
            return

        # 准备数据
        categories = []
        amounts = []

        for category_name, amount in monthly_data.items():
            if category_name != "total" and amount > 0:
                categories.append(category_name)
                amounts.append(amount)

        if not categories:
            return

        # 创建饼图
        ax = self.chart_canvas.figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(
            amounts, labels=categories, autopct="%1.1f%%", startangle=90
        )

        # 设置标题
        ax.set_title("月度支出分类占比", fontsize=12, fontweight="bold")

        # 确保标签正确显示
        for text in texts:
            text.set_fontsize(10)
            text.set_fontfamily(self.CHINESE_FONTS)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_fontfamily(self.CHINESE_FONTS)

        ax.axis("equal")

        self.chart_canvas.draw()

    def filter_history(self):
        """筛选历史记录"""
        try:
            transaction_type = self.history_type_combo.currentText()
            category_name = self.history_category_combo.currentText()

            # 转换类型
            type_filter = None
            if transaction_type == "收入":
                type_filter = "income"
            elif transaction_type == "支出":
                type_filter = "expense"

            category_filter = None
            if category_name != "全部":
                category_filter = category_name

            # 获取交易记录
            transactions = self.transaction_service.get_transactions(
                transaction_type=type_filter, category_name=category_filter
            )

            # 更新表格
            self.history_table.setRowCount(0)
            self.history_transaction_ids = []

            for transaction in transactions:
                row = self.history_table.rowCount()
                self.history_table.insertRow(row)
                self.history_transaction_ids.append(transaction.id)

                # 日期
                date_item = QTableWidgetItem(transaction.date.strftime("%Y-%m-%d"))
                self.history_table.setItem(row, 0, date_item)

                # 类型
                type_text = (
                    "收入" if transaction.transaction_type == "income" else "支出"
                )
                type_item = QTableWidgetItem(type_text)
                type_item.setFlags(
                    type_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )  # 类型不可编辑
                self.history_table.setItem(row, 1, type_item)

                # 分类
                category_text = ""
                if transaction.category:
                    category_text = transaction.category.name
                self.history_table.setItem(row, 2, QTableWidgetItem(category_text))

                # 人员
                person_combo = QComboBox()
                person_combo.setEditable(True)  # 允许编辑输入新的人员名
                # 添加空选项
                person_combo.addItem("")
                # 添加所有人员选项
                persons = self.person_service.get_all_persons()
                for person in persons:
                    person_combo.addItem(person.name)
                # 设置当前值
                if transaction.person:
                    person_combo.setCurrentText(transaction.person.name)
                self.history_table.setCellWidget(row, 3, person_combo)

                # 金额
                self.history_table.setItem(
                    row, 4, QTableWidgetItem(f"{transaction.amount:.2f}")
                )

                # 描述
                self.history_table.setItem(
                    row, 5, QTableWidgetItem(transaction.description)
                )

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载历史记录失败: {str(e)}")

    def save_history_changes(self):
        """保存历史记录的修改"""
        try:
            updated_count = 0
            for row in range(self.history_table.rowCount()):
                transaction_id = self.history_transaction_ids[row]

                # 获取修改后的数据
                date_text = self.history_table.item(row, 0).text()
                category_text = self.history_table.item(row, 2).text().strip()
                # 从人员下拉框获取值
                person_combo = self.history_table.cellWidget(row, 3)
                person_text = person_combo.currentText().strip() if person_combo else ""
                amount_text = self.history_table.item(row, 4).text()
                description_text = self.history_table.item(row, 5).text()

                # 验证必填字段
                if not category_text:
                    QMessageBox.warning(
                        self, "输入错误", f"第{row + 1}行的分类不能为空"
                    )
                    continue

                # 解析数据
                try:
                    date = datetime.strptime(date_text, "%Y-%m-%d").date()
                    amount = float(amount_text.replace("¥", "").strip())
                except ValueError:
                    QMessageBox.warning(
                        self, "输入错误", f"第{row + 1}行数据格式不正确"
                    )
                    continue

                # 更新交易
                result = self.transaction_service.update_transaction(
                    transaction_id,
                    date=date,
                    amount=amount,
                    description=description_text,
                    category_name=category_text,
                    person_name=person_text,
                )

                if result:
                    updated_count += 1
                else:
                    QMessageBox.warning(self, "保存失败", f"第{row + 1}行保存失败")

            if updated_count > 0:
                QMessageBox.information(self, "成功", f"成功更新{updated_count}条记录")
                # 刷新所有数据（包括新创建的分类）
                self.load_data()
            else:
                QMessageBox.information(self, "提示", "没有需要更新的记录")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def cancel_history_changes(self):
        """取消历史记录的修改，重新加载数据"""
        self.filter_history()

    def add_person(self):
        """添加人员"""
        try:
            name = self.person_name_edit.text().strip()
            description = self.person_desc_edit.toPlainText().strip()

            if not name:
                QMessageBox.warning(self, "输入错误", "请输入人员姓名")
                return

            self.person_service.create_person(name, description)

            # 清空表单
            self.person_name_edit.clear()
            self.person_desc_edit.clear()

            # 刷新数据
            self.load_data()

            QMessageBox.information(self, "成功", "人员添加成功")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加人员失败: {str(e)}")

    def delete_person(self):
        """删除选中人员"""
        try:
            current_row = self.person_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "选择错误", "请先选择要删除的人员")
                return

            person_id = int(self.person_table.item(current_row, 0).text())

            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                "删除人员将同时删除相关的交易记录，确定要删除吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.person_service.delete_person(person_id)

                # 刷新数据
                self.load_data()

                QMessageBox.information(self, "成功", "人员删除成功")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除人员失败: {str(e)}")

    def load_persons(self):
        """加载人员列表"""
        try:
            persons = self.person_service.get_all_persons()

            self.person_table.setRowCount(0)

            for person in persons:
                row = self.person_table.rowCount()
                self.person_table.insertRow(row)

                self.person_table.setItem(row, 0, QTableWidgetItem(str(person.id)))
                self.person_table.setItem(row, 1, QTableWidgetItem(person.name))
                self.person_table.setItem(
                    row, 2, QTableWidgetItem(person.description or "")
                )

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载人员列表失败: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置样式
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
