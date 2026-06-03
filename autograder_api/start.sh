#!/bin/bash

set -e

cd "$(dirname "$0")"

echo "========================================"
echo "AutoGrader API 启动脚本"
echo "========================================"
echo ""

echo "[1/3] 检查Python环境..."
if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    echo "错误: 未找到Python，请先安装Python 3.8+"
    exit 1
fi
"$PYTHON" --version

echo ""
echo "[2/3] 检查依赖包..."
if ! "$PYTHON" -c "import fastapi, openpyxl" &> /dev/null; then
    echo "正在安装依赖包..."
    "$PYTHON" -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 依赖包安装失败"
        exit 1
    fi
else
    echo "依赖包已安装"
fi

echo ""
echo "[3/3] 启动API服务..."
echo "服务地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"
echo ""

"$PYTHON" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
