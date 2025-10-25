# 家庭账本 (family-account-book)

一个功能完整的家庭收支记录和分析应用，使用 Python + PyQt6 + SQLite 开发。

## 功能特性

- **支出记录**：记录日常支出，支持自定义分类
- **收入记录**：记录工资收入及五险一金等扣除明细
- **月度统计**：查看月度支出统计和分类占比
- **分类分析**：特定时间段分类支出统计、纵向对比、百分比分析
- **数据导出**：支持 CSV 和 Excel 格式导出
- **直观界面**：基于 PyQt6 的现代图形界面

## 安装和运行

### 环境要求

- Python 3.11+
- pip

### 安装步骤

1. 克隆项目：

```bash
git clone <repository-url>
cd family-account-book
```

2. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. 安装依赖：

```bash
pip install -r requirements.txt
pip install openpyxl  # 用于 Excel 导出
```

4. 运行应用：

```bash
# 方式1：直接运行主文件
python main.py

# 方式2：作为模块运行（推荐）
python -m family_account_book

# 方式3：使用 Poetry（如果已安装）
poetry install
poetry run family-account-book
```

## 项目结构

```
family-account-book/
├── src/
│   ├── models/          # 数据模型
│   ├── views/           # 用户界面
│   ├── controllers/     # 控制器逻辑
│   ├── services/        # 业务服务层
│   └── database.py      # 数据库配置
├── tests/               # 单元测试
├── specs/               # 功能规格说明
├── main.py              # 应用入口
├── requirements.txt     # 依赖列表
└── README.md           # 说明文档
```

## 使用说明

### 记录支出

1. 在"记录"标签页选择日期
2. 输入支出金额
3. 选择或输入分类（如：餐饮、交通、房租等）
4. 添加描述信息
5. 点击"记录支出"

### 记录收入

1. 选择日期和输入毛收入金额
2. 添加描述
3. 在扣除项文本框中输入扣除项目（格式：项目名称:金额）
4. 点击"记录收入"

### 查看统计

1. 在"统计"标签页选择年月
2. 点击"刷新统计"查看月度支出汇总和饼图

### 查看历史

1. 在"历史"标签页选择类型和分类过滤条件
2. 点击"筛选"查看交易记录

## 开发

### 运行测试

```bash
python -m pytest tests/ -v
```

### 代码规范

- 使用 Black 格式化代码
- 使用 isort 整理导入
- 使用 flake8 检查代码质量

## 数据库配置

应用支持 MySQL 数据库。在运行应用前，请确保：

1. **安装 MySQL 服务器** 并启动服务
2. **创建数据库用户** 或使用现有用户
3. **修改数据库配置**（在 `family_account_book/database.py` 中）：

```python
# 修改为您的 MySQL 连接信息
DATABASE_URL = "mysql+pymysql://用户名:密码@localhost:3306/数据库名"
```

**示例配置：**

```python
DATABASE_URL = "mysql+pymysql://root:12345678@localhost:3306/family_account_book"
```

应用会自动创建数据库和表结构，无需手动创建。

**注意：** 如果使用其他数据库，请相应修改 `requirements.txt` 和连接字符串。

## 技术栈

- **GUI**: PyQt6
- **数据库**: MySQL + SQLAlchemy ORM
- **数据分析**: 自定义分析服务
- **图表**: Matplotlib
- **导出**: pandas + openpyxl
- **测试**: pytest

## 许可证

MIT License
