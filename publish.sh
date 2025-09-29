#!/bin/bash

# 发布脚本 - 构建和发布 je-analyzer

set -e

echo "📦 构建包..."
uv build

echo "📋 检查包..."
uv tree

echo "🧪 运行测试..."
uv run pytest tests/ -v

echo "📖 生成文档..."
uv run python -c "import src.je_analyzer; print('包导入成功')"

echo "✅ 构建完成！"

echo ""
echo "发布选项："
echo "1. 发布到 TestPyPI:"
echo "   uv publish --publish-url https://test.pypi.org/legacy/"
echo ""
echo "2. 发布到 PyPI:"
echo "   uv publish"
echo ""
echo "3. 本地安装测试："
echo "   uv pip install dist/*.whl --force-reinstall"
echo "   je-analyzer --help"