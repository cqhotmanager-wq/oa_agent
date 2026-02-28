#!/usr/bin/env bash
# 使用 uv 初始化项目（macOS / Linux）
# 在项目根目录执行: bash scripts/uv_install.sh

set -e
cd "$(dirname "$0")/.."

if ! command -v uv &>/dev/null; then
    echo "正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "创建虚拟环境并安装依赖..."
uv sync

echo "完成。运行应用: uv run python run.py"
echo "运行测试: uv run pytest"
