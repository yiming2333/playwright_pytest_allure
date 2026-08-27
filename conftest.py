"""Pytest configuration and shared fixtures for Playwright tests.

本文件集成【配置层】+【日志层】+【工具层】：
- config.settings: 集中管理 base_url / browser / 账号 / 超时 / 日志级别等
- utils.logger: 标准库 logging，控制台 + 文件双输出
- utils.screenshot: 失败自动截图 + attach Allure
- utils.api_client: HTTP 客户端封装
"""

from __future__ import annotations
# conftest.py
import threading
import time
import requests
from mock_server import app
import pytest
from playwright.sync_api import Page

# 引入配置层和日志层（import 即触发 logger 初始化）
from config import settings
from utils.logger import get_logger
from utils.screenshot import capture_failure_screenshot

log = get_logger(__name__)


# ========== Report Hooks ==========
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test execution result for Allure attachment on failure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.rep_call = report


@pytest.fixture(autouse=True)
def _screenshot_on_failure(request, page: Page):
    """失败自动截图 + HTML 源码，附加到 Allure 报告。"""
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        capture_failure_screenshot(page, request.node)


# ========== Session-level Fixture: Global login state ==========
@pytest.fixture(scope="session")
def auth_state(tmp_path_factory, playwright, mock_server: str) -> str:
    """
    Session 级登录一次，持久化 storage_state 供所有用例复用。

    ⚠️ 依赖 mock_server：确保 Flask 服务就绪后再发起登录请求。
    """
    state_file = tmp_path_factory.mktemp("auth") / "state.json"

    # ✅ 使用 mock_server 返回的动态 URL，而非硬编码 settings.base_url
    base_url = mock_server

    log.info(f"开始 session 级登录: {base_url}")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    username, password = settings.account("admin")
    resp = requests.post(
        f"{base_url}/api/login",  # ← 用动态 URL
        json={"username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    token = resp.json().get("token", "")
    log.info(f"登录成功: user={username} role={resp.json().get('role')}")

    page.goto(base_url)  # ← 用动态 URL
    context.add_cookies([
        {"name": "auth_token", "value": token, "domain": "127.0.0.1", "path": "/"},
        {"name": "username", "value": username, "domain": "127.0.0.1", "path": "/"},
        {"name": "user_role", "value": "admin", "domain": "127.0.0.1", "path": "/"},
    ])

    context.storage_state(path=str(state_file))
    browser.close()
    log.info(f"storage_state 已保存: {state_file}")
    return str(state_file)


# ========== Browser Context Configuration ==========
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, auth_state: str) -> dict:
    """所有 browser context 自动复用登录态 + 配置层 viewport。"""
    return {
        **browser_context_args,
        "storage_state": auth_state,
        "viewport": settings.viewport,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    """浏览器启动参数从配置层读取（headless / slow_mo）。"""
    return {
        **browser_type_launch_args,
        "headless": settings.headless,
        "slow_mo": settings.slow_mo,
    }


# ========== Multi-browser: 让 indirect 参数化真正生效 ==========
@pytest.fixture(scope="session")
def browser_type(request, playwright, browser_name):
    """覆写 pytest-playwright 的 browser_type：消费 indirect 参数化传入的浏览器名。

    为什么需要覆写：插件原生 fixture 签名是 `browser_type(playwright, browser_name)`，
    只认 `--browser` 命令行参数（browser_name），不读 request.param。因此
    @pytest.mark.parametrize("browser_type", [...], indirect=True) 传入的
    "firefox"/"webkit" 会被静默丢弃——用例 ID 显示 [chromium-firefox]，
    实际却始终跑 chromium（多浏览器测试形同虚设）。

    修复策略：优先消费用例传入的 request.param；未参数化的用例回退 browser_name，
    行为与原生完全一致。
    """
    name = getattr(request, "param", None) or browser_name
    if name != browser_name:
        log.info(f"多浏览器参数化生效: {name}（--browser 当前默认为 {browser_name}）")
    return getattr(playwright, name)


# ========== Function-level Fixture: Navigate to home page ==========
@pytest.fixture(autouse=True)
def navigate_to_home(request, page: Page, mock_server: str):
    """每个用例前重置到首页 + 清空 localStorage。"""
    if request.node.get_closest_marker("no_home_navigation"):
        return
    page.goto(f"{mock_server}/")  # ← 用动态 URL 替代 settings.base_url
    try:
        page.evaluate("localStorage.clear()")
    except Exception:
        pass


# ========== 共享 fixture: ApiClient ==========
@pytest.fixture
def api_client(auth_state: str, mock_server: str):
    """提供配置好的 ApiClient（已注入登录态 cookie）。

    用法：
        def test_xxx(api_client):
            resp = api_client.get("/api/products?q=Pro")
    """
    from utils.api_client import ApiClient
    import json
    from pathlib import Path

    client = ApiClient(base_url=mock_server)
    # 复用 auth_state 的 cookie，避免重复登录
    state = json.loads(Path(auth_state).read_text(encoding="utf-8"))
    client.inject_cookies(state.get("cookies", []))
    yield client
    client.close()


@pytest.fixture(scope="session", autouse=True)
def mock_server():
    """
    在整个测试会话期间自动启动 Mock Server。
    scope="session" 确保所有测试用例共享同一个服务实例和内存数据。
    """
    # ⚠️ 关键：Flask 的 render_template 依赖 templates 目录
    # 必须显式指定 template_folder，防止在 Docker WORKDIR 中找不到模板
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app.template_folder = os.path.join(base_dir, "templates")

    # 在后台线程启动 Flask
    # threaded=True 已在你的源码中设置，这里保持
    # use_reloader=False 禁止热重载，避免子进程 fork 导致端口冲突
    server_thread = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1",
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        ),
        daemon=True
    )
    server_thread.start()

    # 等待服务就绪（轮询健康检查）
    max_retries = 30
    for i in range(max_retries):
        try:
            resp = requests.get("http://127.0.0.1:5000/", timeout=2)
            if resp.status_code == 200:
                print(f"\n✅ Mock Server ready at http://127.0.0.1:5000")
                break
        except (requests.ConnectionError, requests.Timeout):
            time.sleep(0.5)
    else:
        raise RuntimeError(
            f"Mock Server failed to start after {max_retries * 0.5}s. "
            "Check if port 5000 is available or templates/ directory exists."
        )

    yield "http://127.0.0.1:5000"
    # daemon=True 线程随 pytest 主进程退出自动终止，无需手动 cleanup
