"""Mock server for Playwright test framework.

Provides a simulated web application with pages and APIs for testing.
Run directly: python mock_server.py
"""

from __future__ import annotations

import uuid
from typing import Any

from flask import Flask, jsonify, make_response, redirect, render_template, request

app = Flask(__name__)
app.secret_key = "playwright-test-secret-key-2026"

# ==================== Mock Database ====================
USERS_DB: dict[str, dict[str, str]] = {
    "admin": {"password": "admin123", "role": "admin", "name": "管理员"},
    "editor": {"password": "edit456", "role": "editor", "name": "编辑员"},
    "viewer": {"password": "view789", "role": "viewer", "name": "观察者"},
}

PRODUCTS_DB: list[dict[str, Any]] = [
    {"id": 1, "name": "iPhone 15 Pro", "category": "手机", "price": 8999, "stock": 50},
    {"id": 2, "name": "MacBook Pro 16", "category": "笔记本", "price": 19999, "stock": 20},
    {"id": 3, "name": "AirPods Pro 2", "category": "耳机", "price": 1899, "stock": 100},
    {"id": 4, "name": "iPad Air", "category": "平板", "price": 4799, "stock": 35},
    {"id": 5, "name": "Playwright 实战指南", "category": "书籍", "price": 89, "stock": 200},
    {"id": 6, "name": "Python 编程从入门到实践", "category": "书籍", "price": 69, "stock": 150},
    {"id": 7, "name": "Docker 深入浅出", "category": "书籍", "price": 79, "stock": 80},
    {"id": 8, "name": "Apple Watch Ultra", "category": "手表", "price": 6299, "stock": 15},
]


# ==================== API Endpoints ====================

@app.route("/api/login", methods=["POST"])
def api_login():
    """API login endpoint for fixture-based authentication."""
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    user = USERS_DB.get(username)
    if user and user["password"] == password:
        token = str(uuid.uuid4())
        resp = make_response(jsonify({
            "success": True,
            "token": token,
            "user": {"name": user["name"], "role": user["role"]}
        }))
        resp.set_cookie("auth_token", token, httponly=False)
        resp.set_cookie("username", username, httponly=False)
        resp.set_cookie("user_role", user["role"], httponly=False)
        return resp

    return jsonify({"success": False, "error": "用户名或密码错误"}), 401


@app.route("/api/products")
def api_products():
    """Product search API with filtering parameters."""
    keyword = request.args.get("q", "").lower()
    category = request.args.get("category", "").lower()
    min_price = request.args.get("min_price", 0, type=int)
    max_price = request.args.get("max_price", 999999, type=int)

    results = PRODUCTS_DB
    if keyword:
        results = [p for p in results if keyword in p["name"].lower() or keyword in p["category"].lower()]
    if category:
        results = [p for p in results if p["category"].lower() == category]
    if min_price:
        results = [p for p in results if p["price"] >= min_price]
    if max_price < 999999:
        results = [p for p in results if p["price"] <= max_price]

    return jsonify({"total": len(results), "products": results})


@app.route("/api/userinfo")
def api_userinfo():
    """Get current user info, requires login."""
    username = request.cookies.get("username")
    if not username or username not in USERS_DB:
        return jsonify({"error": "未登录"}), 401
    user = USERS_DB[username]
    return jsonify({"name": user["name"], "role": user["role"]})


# ==================== Page Routes ====================

@app.route("/")
def index():
    """Home page - test range entry point."""
    return render_template("index.html")


@app.route("/login")
def login_page():
    """Login page."""
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    """Protected dashboard page."""
    return render_template("dashboard.html")


@app.route("/logout")
def logout():
    """Logout and clear cookies."""
    resp = make_response(redirect("/login"))
    resp.delete_cookie("auth_token")
    resp.delete_cookie("username")
    resp.delete_cookie("user_role")
    return resp

# 在 api_userinfo 后面添加
@app.route("/api/reset", methods=["POST"])
def api_reset():
    """Reset mock database to initial state for test isolation."""
    global PRODUCTS_DB
    PRODUCTS_DB = [
        {"id": 1, "name": "iPhone 15 Pro", "category": "手机", "price": 8999, "stock": 50},
        {"id": 2, "name": "MacBook Pro 16", "category": "笔记本", "price": 19999, "stock": 20},
        {"id": 3, "name": "AirPods Pro 2", "category": "耳机", "price": 1899, "stock": 100},
        {"id": 4, "name": "iPad Air", "category": "平板", "price": 4799, "stock": 35},
        {"id": 5, "name": "Playwright 实战指南", "category": "书籍", "price": 89, "stock": 200},
        {"id": 6, "name": "Python 编程从入门到实践", "category": "书籍", "price": 69, "stock": 150},
        {"id": 7, "name": "Docker 深入浅出", "category": "书籍", "price": 79, "stock": 80},
        {"id": 8, "name": "Apple Watch Ultra", "category": "手表", "price": 6299, "stock": 15},
    ]
    return jsonify({"status": "reset", "count": len(PRODUCTS_DB)})

if __name__ == "__main__":
    # Windows GBK 控制台下 emoji print 会抛 UnicodeEncodeError 直接崩溃，
    # 强制 stdout 走 UTF-8（兼容 PyCharm/UTF-8 终端，无副作用）
    try:
        import sys
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print("🚀 Playwright 全能靶场 v3.0 已启动")
    print("📍 访问地址: http://127.0.0.1:5000")
    print("📍 登录页面: http://127.0.0.1:5000/login")
    print("📍 API 文档:")
    print("   POST /api/login       - 登录 (username, password)")
    print("   GET  /api/products    - 搜索商品 (q, category, min_price, max_price)")
    print("   GET  /api/userinfo    - 获取用户信息 (需要登录)")
    print("\n🧪 测试账号:")
    print("   admin  / admin123  (管理员)")
    print("   editor / edit456   (编辑员)")
    print("   viewer / view789   (观察者)")
    app.run(host='0.0.0.0',debug=False, port=5000, threaded=True)