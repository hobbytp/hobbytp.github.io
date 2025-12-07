#!/usr/bin/env bash
set -euo pipefail

# Args: FILE_PATH FORCE ENV_FILE
FILE_PATH="${1:-}"
FORCE_INPUT="${2:-}"
ENV_FILE_INPUT="${3:-}"

echo "开始博客内容摄取..."

# Resolve and load .env
ENV_CANDIDATES=()
if [[ -n "${ENV_FILE_INPUT}" ]]; then
  ENV_CANDIDATES+=("${ENV_FILE_INPUT}")
fi
ENV_CANDIDATES+=(".env" "scripts/.env" "tools/content-analysis/.env")

LOADED_ENV=""
for f in "${ENV_CANDIDATES[@]}"; do
  if [[ -f "${f}" ]]; then
    LOADED_ENV="${f}"
    break
  fi
done

if [[ -n "${LOADED_ENV}" ]]; then
  echo "加载环境变量: ${LOADED_ENV}"
  set -a
  # shellcheck disable=SC1090
  . "${LOADED_ENV}"
  set +a
else
  echo "未找到 .env 文件，跳过环境加载（可用 ENV_FILE 指定）"
fi

# Pick Python from venv if available
PYTHON_BIN="python"
if [[ -x ".venv/Scripts/python.exe" ]]; then
  PYTHON_BIN=".venv/Scripts/python.exe"
elif [[ -x ".venv/bin/python" ]]; then
  PYTHON_BIN=".venv/bin/python"
fi

# Build flags
FORCE_FLAG=""
if [[ "${FORCE_INPUT}" == "true" || "${FORCE_INPUT}" == "1" ]]; then
  FORCE_FLAG="--force"
fi

# Execute
if [[ -n "${FILE_PATH}" ]]; then
  # Normalize for ingest.py (expects path relative to content/)
  NORMALIZED_FILE="${FILE_PATH}"
  if [[ "${NORMALIZED_FILE}" == ./content/* ]]; then
    NORMALIZED_FILE="${NORMALIZED_FILE#./content/}"
  elif [[ "${NORMALIZED_FILE}" == content/* ]]; then
    NORMALIZED_FILE="${NORMALIZED_FILE#content/}"
  fi
  echo "处理单个文件: ${NORMALIZED_FILE}"
  "${PYTHON_BIN}" scripts/ingest.py --file "${NORMALIZED_FILE}" ${FORCE_FLAG}
else
  echo "处理所有文件..."
  "${PYTHON_BIN}" scripts/ingest.py ${FORCE_FLAG}
fi
