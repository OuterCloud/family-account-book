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

应用使用 **SQLite** 数据库，开箱即用，无需额外安装和配置：

- **数据库位置**: `~/Documents/家庭账本/family_account_book.db`
- **自动创建**: 首次运行时自动创建数据库和表结构
- **数据持久化**: 数据保存在本地文件中，无需网络连接

**优势：**

- ✅ 无需安装 MySQL 或其他数据库服务器
- ✅ 开箱即用，应用启动即可使用
- ✅ 数据文件易于备份和迁移
- ✅ 跨平台兼容

## 技术栈

- **GUI**: PyQt6
- **数据库**: MySQL + SQLAlchemy ORM
- **数据分析**: 自定义分析服务
- **图表**: Matplotlib
- **导出**: pandas + openpyxl
- **测试**: pytest

## 打包和分发

### 自动打包

运行打包脚本：

```bash
./build_app.sh
```

### 手动打包

1. 激活虚拟环境：

```bash
source venv/bin/activate
```

2. 安装 PyInstaller：

```bash
pip install pyinstaller
```

3. 打包应用：

```bash
pyinstaller --onedir --windowed --name="家庭账本" main.py
```

### 分发说明

打包完成后，在 `dist/` 目录下会生成：

- **`家庭账本.app`** - macOS 应用程序包（推荐）
- **`家庭账本/`** - 应用程序目录

**分发方法：**

1. 将 `dist/家庭账本.app` 文件复制到其他 macOS 电脑
2. 双击运行，无需安装 Python、MySQL 或其他依赖
3. 首次运行可能需要允许"从未知开发者运行"（在系统偏好设置 > 安全性与隐私中允许）
4. 应用程序会自动在用户 Documents 目录创建数据库文件

**数据库说明：**

- 数据存储在 `~/Documents/家庭账本/family_account_book.db`
- SQLite 数据库，开箱即用，无需额外配置
- 数据文件可轻松备份和迁移
