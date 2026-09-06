#!/bin/bash
cd "$(dirname "$0")" || exit 1

echo ""
echo "  ============================================"
echo "     Seasonings 菜谱推荐站（带登录版）"
echo "  ============================================"
echo ""

# ---------- 1. 找 Python ----------
if ! command -v python3 >/dev/null 2>&1; then
  echo ""
  echo "  [!] 这台电脑没有 Python3，本站点运行不了。"
  echo ""
  echo "  请到下面地址下载安装 3.9 ~ 3.11 版本："
  echo "      https://www.python.org/downloads/"
  echo ""
  echo "  装完重新双击「双击启动-Mac.command」即可。"
  echo ""
  read -r -p "  按回车关闭..." _
  exit 1
fi
echo "  使用 $(python3 --version)"

# ---------- 2. 建虚拟环境（只做一次） ----------
if [ ! -x ".venv/bin/python" ]; then
  echo ""
  echo "  首次启动，正在创建虚拟环境..."
  python3 -m venv .venv || {
    echo "  [!] 创建虚拟环境失败，请安装 Xcode 命令行工具：xcode-select --install"
    read -r -p "  按回车关闭..." _
    exit 1
  }
fi

VPY=.venv/bin/python

# ---------- 3. 装依赖 ----------
echo ""
echo "  检查依赖包（首次要几分钟，请耐心等）..."
"$VPY" -m pip install --disable-pip-version-check -q -r requirements.txt
if [ $? -ne 0 ]; then
  echo "  默认源装不上，改用清华源重试..."
  "$VPY" -m pip install --disable-pip-version-check -q -r requirements.txt \
      -i https://pypi.tuna.tsinghua.edu.cn/simple
  if [ $? -ne 0 ]; then
    echo ""
    echo "  [!] 依赖包装不上，多数是网络问题。换网后重试，或看「运行说明.md」。"
    read -r -p "  按回车关闭..." _
    exit 1
  fi
fi

# ---------- 4. 启动 + 自动开浏览器 ----------
echo ""
"$VPY" start.py
echo ""
echo "  服务已停止。"
read -r -p "  按回车关闭..." _
