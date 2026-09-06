@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Seasonings 菜谱推荐站 - 一键启动

echo.
echo   ============================================
echo      Seasonings 菜谱推荐站（带登录版）
echo   ============================================
echo.

REM ---------- 1. 找 Python ----------
set "PY="
py -3 --version >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if not defined PY (
    python --version >nul 2>nul
    if not errorlevel 1 set "PY=python"
)
if not defined PY goto nopython
echo   使用 %PY%

REM ---------- 2. 建虚拟环境（只做一次） ----------
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo   首次启动，正在创建虚拟环境...
    %PY% -m venv .venv
    if errorlevel 1 goto venvfail
)

set "VPY=.venv\Scripts\python.exe"

REM ---------- 3. 装依赖 ----------
echo.
echo   检查依赖包（首次要几分钟，请耐心等）...
%VPY% -m pip install --disable-pip-version-check -q -r requirements.txt
if errorlevel 1 (
    echo.
    echo   默认源装不上，改用清华源重试...
    %VPY% -m pip install --disable-pip-version-check -q -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 goto pipfail
)

REM ---------- 4. 启动 + 自动开浏览器 ----------
echo.
%VPY% start.py
echo.
echo   服务已停止。
pause
exit /b 0

:nopython
echo.
echo   [!] 这台电脑没有 Python，本站点运行不了。
echo.
echo   请到下面地址下载安装 3.9 ~ 3.11 版本：
echo       https://www.python.org/downloads/
echo.
echo   安装时务必勾选这一项，否则双击本文件还是没反应：
echo       [x] Add Python to PATH
echo.
echo   装完重新双击「双击启动-Windows.bat」即可。
echo.
pause
exit /b 1

:venvfail
echo.
echo   [!] 创建虚拟环境失败。常见原因：Python 装得不完整，或被杀毒软件拦截。
echo.
echo   可以跳过虚拟环境，直接用系统 Python 启：
echo       在本文件夹里打开命令行，执行   python start.py
echo.
pause
exit /b 1

:pipfail
echo.
echo   [!] 依赖包装不上，多数是网络问题。
echo.
echo   换个网（比如手机热点）再双击本文件重试；
echo   还是不行请看同目录的「运行说明.md」第五节。
echo.
pause
exit /b 1
