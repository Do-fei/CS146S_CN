#!/usr/bin/env bash
# 导出网页版并发布到 Surge（固定域名，手机可直接打开）
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DOMAIN="${SURGE_DOMAIN:-city11-dawei.surge.sh}"
STORE="$HOME/.config/sfc-vn/surge.env"

if [[ -f "$STORE" ]]; then
  # shellcheck disable=SC1090
  source "$STORE"
fi

if [[ -z "${SURGE_TOKEN:-}" ]]; then
  echo "缺少 SURGE_TOKEN。"
  echo "一次性：surge.sh 注册后在 Account → Token 复制，在 Cursor 里发给 Agent 即可。"
  echo "或 export SURGE_TOKEN=... 后再运行本脚本。"
  exit 1
fi

cd "$ROOT"
python3 tools/export_web.py

if ! command -v surge >/dev/null 2>&1; then
  npm install -g surge
fi

cd player
surge . "$DOMAIN" --token "$SURGE_TOKEN"
echo "已发布: https://${DOMAIN}"
