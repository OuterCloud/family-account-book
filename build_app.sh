#!/bin/bash

# 家庭账本应用打包脚本

echo "开始打包家庭账本应用..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "错误：未找到虚拟环境，请先运行："
    echo "python -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查PyInstaller是否安装
if ! command -v pyinstaller &> /dev/null; then
    echo "安装PyInstaller..."
    pip install pyinstaller
fi

# 清理之前的构建
echo "清理之前的构建..."
rm -rf build dist *.spec

# 打包应用
echo "打包应用..."
pyinstaller --onedir --windowed --name="家庭账本" main.py

# 检查打包结果
if [ -d "dist/家庭账本.app" ]; then
    echo "✅ 打包成功！"
    echo ""
    echo "生成的文件："
    echo "  - dist/家庭账本.app (macOS应用程序，可双击运行)"
    echo "  - dist/家庭账本/ (应用程序目录)"
    echo ""
    echo "要分发应用，只需要将 dist/家庭账本.app 文件发送给其他macOS用户即可。"
    echo "他们可以直接双击打开使用，无需安装Python或其他依赖。"
else
    echo "❌ 打包失败！"
    exit 1
fi