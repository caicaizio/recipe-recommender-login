"""一键启动：检查依赖 -> 起本地服务 -> 自动打开浏览器。

双击「双击启动-Windows.bat」（Mac/Linux 用对应的 .command / .sh）会调用本文件。
也可以自己敲命令：    python start.py
"""

import importlib.util
import os
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser

PORT = int(os.environ.get("PORT", "5000"))
URL = "http://127.0.0.1:%d" % PORT

# 运行 app.py 真正需要的包（web_scraper.py 用的 requests/bs4 不在其中，
# 只有重新爬菜谱时才需要，这里不强制安装）
REQUIRED = [("flask", "Flask"), ("pandas", "pandas"), ("numpy", "numpy"),
            ("scipy", "scipy"), ("sklearn", "scikit-learn")]


def _open_when_ready():
    """服务起来之前页面是打不开的，先轮询，通了再弹浏览器。"""
    deadline = time.time() + 300
    while time.time() < deadline:
        try:
            urllib.request.urlopen(URL, timeout=2)
            break
        except Exception:
            time.sleep(1)
    webbrowser.open(URL)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.getcwd())

    missing = [pip_name for module, pip_name in REQUIRED
               if importlib.util.find_spec(module) is None]
    if missing:
        print("\n[缺少依赖] %s" % "、".join(missing))
        print("请先运行启动脚本（它会自动装），或手动执行：")
        print("    %s -m pip install -r requirements.txt" % sys.executable)
        print("网络不好就在上面那条命令末尾加： -i https://pypi.tuna.tsinghua.edu.cn/simple")
        return 1

    print("\n正在加载菜谱数据，第一次要等 30~60 秒，请别关窗口…")
    threading.Thread(target=_open_when_ready, daemon=True).start()

    from app import app                      # 这一行会加载模型，比较慢
    print("\n好了！浏览器会自动打开 %s" % URL)
    print("没自动弹出来，就手动把这个地址粘到浏览器地址栏。")
    print("停止服务：在这个窗口按 Ctrl+C，或者直接关掉窗口。\n")
    app.run(host="127.0.0.1", port=PORT, debug=False)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已停止。")
