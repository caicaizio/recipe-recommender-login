"""账号：昵称 + 口令，存在服务端 data/accounts.json。

口令用 hashlib.pbkdf2_hmac（SHA-256，每个账号独立随机盐），只存哈希不存明文。
同时记下每个人勾选过的菜，用来让推荐越来越准（见 app.py）。

注意：这只是本地小站的账号，没有邮箱验证、没有找回口令、没有防暴力破解的限流。
别在这里用你在别处用的密码。
"""

import hashlib
import hmac
import json
import os
import secrets
import threading
from datetime import date

ITER = 200000
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "accounts.json")

_lock = threading.Lock()


def _empty():
    return {"users": {}}


def _read():
    if not os.path.exists(DATA_FILE):
        return _empty()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (ValueError, OSError):
        return _empty()
    if not isinstance(data, dict) or not isinstance(data.get("users"), dict):
        return _empty()
    return data


def _write(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, DATA_FILE)  # 原子替换，写一半崩了也不会留下坏文件


def _hash(pwd, salt, iter=ITER):
    return hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt.encode("utf-8"), iter).hex()


def _today():
    return date.today().isoformat()


# ---------------- 对外接口 ----------------
def names():
    """所有账号名，按最近登录排序（给「选一个已有账号」用）"""
    users = _read()["users"]
    return sorted(users.keys(), key=lambda n: users[n].get("lastLoginAt", ""), reverse=True)


def all_users():
    """所有账号的完整信息（昵称 -> 字段），顺序同 names()"""
    users = _read()["users"]
    return {n: users[n] for n in names()}


def exists(name):
    return name in _read()["users"]


def province(name):
    """这个账号选的省份（没选是 ""）"""
    user = _read()["users"].get(name)
    return (user or {}).get("province", "") or ""


def set_province(name, value):
    """改省份。传空字符串就是清空"""
    if not name:
        return ""
    value = (value or "").strip()
    with _lock:
        data = _read()
        if name in data["users"]:
            data["users"][name]["province"] = value
            _write(data)
    return value


def create(name, password, province=""):
    """建账号。返回 (ok, message)"""
    name = (name or "").strip()
    if not name:
        return False, "请填昵称"
    if len(name) > 20:
        return False, "昵称最多 20 个字"
    if not password:
        return False, "请设置口令（至少 4 位）"
    if len(password) < 4:
        return False, "口令至少 4 位"
    with _lock:
        data = _read()
        if name in data["users"]:
            return False, "这个昵称已经有了，直接登录或换一个"
        salt = secrets.token_hex(16)
        data["users"][name] = {
            "salt": salt,
            "hash": _hash(password, salt),
            "iter": ITER,
            "createdAt": _today(),
            "lastLoginAt": _today(),
            "province": (province or "").strip(),
            "picks": {},   # 菜名 -> 评分，用来让推荐越来越准
        }
        _write(data)
    return True, name


def verify(name, password):
    """校验口令。返回 (ok, message)"""
    name = (name or "").strip()
    user = _read()["users"].get(name)
    if not user:
        return False, "没有这个账号，先注册一个"
    if not password:
        return False, "请输入口令"
    want = user["hash"]
    got = _hash(password, user["salt"], user.get("iter", ITER))
    if not hmac.compare_digest(want, got):   # 定长比较，避免计时侧信道
        return False, "口令不对"
    with _lock:
        data = _read()
        if name in data["users"]:
            data["users"][name]["lastLoginAt"] = _today()
            _write(data)
    return True, name


def picks(name):
    """这个账号以前勾选过的菜（列表）"""
    user = _read()["users"].get(name)
    if not user:
        return []
    return list(user.get("picks", {}).keys())


def add_picks(name, titles):
    """把这次勾选的菜记进账号，下次推荐会避开它们、协同过滤的向量也更长"""
    if not name:
        return 0
    titles = [t for t in titles if t]
    if not titles:
        return 0
    with _lock:
        data = _read()
        user = data["users"].get(name)
        if not user:
            return 0
        bag = user.setdefault("picks", {})
        for t in titles:
            bag[t] = 5
        _write(data)
    return len(bag)


def clear_picks(name):
    with _lock:
        data = _read()
        if name in data["users"]:
            data["users"][name]["picks"] = {}
            _write(data)


def delete(name):
    with _lock:
        data = _read()
        data["users"].pop(name, None)
        _write(data)
