#!/bin/bash

# 测试打包应用

echo "测试打包的家庭账本应用..."

# 检查应用是否存在
if [ ! -d "dist/家庭账本.app" ]; then
    echo "❌ 错误：未找到打包的应用文件 dist/家庭账本.app"
    echo "请先运行 ./build_app.sh 进行打包"
    exit 1
fi

echo "✅ 找到打包的应用文件"

# 检查应用结构
echo "检查应用结构..."
if [ -f "dist/家庭账本.app/Contents/MacOS/家庭账本" ]; then
    echo "✅ 可执行文件存在"
else
    echo "❌ 可执行文件不存在"
    exit 1
fi

# 检查文件大小
APP_SIZE=$(du -sh "dist/家庭账本.app" | cut -f1)
echo "📦 应用大小: $APP_SIZE"

echo ""
echo "🎉 打包测试通过！"
echo ""
echo "分发说明："
echo "1. 将 dist/家庭账本.app 文件复制到其他macOS电脑"
echo "2. 双击即可运行，无需安装Python"
echo "3. 首次运行可能需要允许'从未知开发者运行'"