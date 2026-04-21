#!/bin/bash

set -e

# 导出环境变量
WORK_DIR="${COZE_WORKSPACE_PATH:-/workspace/projects}"

# 激活虚拟环境
if [ -f "${WORK_DIR}/.venv/bin/activate" ]; then
    source "${WORK_DIR}/.venv/bin/activate"
fi

# 进入项目目录
cd "${WORK_DIR}"

# 启动 Streamlit 应用
echo "🚀 正在启动 Streamlit 应用..."
echo "📱 访问地址: http://localhost:8501"
echo ""

streamlit run src/app.py
