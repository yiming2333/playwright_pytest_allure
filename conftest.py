"""Pytest configuration and shared fixtures for Playwright tests.

本文件集成【配置层】+【日志层】+【工具层】：
- config.settings: 集中管理 base_url / browser / 账号 / 超时 / 日志级别等
- utils.logger: 标准库 logging，控制台 + 文件双输出
- utils.screenshot: 失败自动截图 + attach Allure
- utils.api_client: HTTP 客户端封装
"""

from __future__ import annotations

import allure
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
def auth_state(tmp_path_factory, playwright) -> str:
    """
    Session 级登录一次，持久化 storage_state 供所有用例复用。

    使用 pytest-playwright 的 playwright fixture，避免 asyncio 事件循环冲突。
    账号从 settings 读取（敏感信息走环境变量）。
    """
    state_file = tmp_path_factory.mktemp("auth") / "state.json"

    log.info(f"开始 session 级登录: {settings.base_url}")
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # 用配置层的账号
    username, password = settings.account("admin")
    resp = __import__("requests").post(
        f"{settings.base_url}/api/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    resp.raise_for_status()
    token = resp.json().get("token", "")
    log.info(f"登录成功: user={username} role={resp.json().get('role')}")

    page.goto(settings.base_url)
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


# ========== Function-level Fixture: Navigate to home page ==========
@pytest.fixture(autouse=True)
def navigate_to_home(request, page: Page):
    """每个用例前重置到首页 + 清空 localStorage。

    使用绝对 URL（不依赖 pytest-base-url），确保 pytest-xdist 并发 worker 下稳定。
    带 @pytest.mark.no_home_navigation 的用例跳过（如需要从 /login 开始）。
    """
    if request.node.get_closest_marker("no_home_navigation"):
        return
    page.goto(f"{settings.base_url}/")
    try:
        page.evaluate("localStorage.clear()")
    except Exception:
        pass


# ========== 共享 fixture: ApiClient ==========
@pytest.fixture
def api_client(auth_state: str):
    """提供配置好的 ApiClient（已注入登录态 cookie）。

    用法：
        def test_xxx(api_client):
            resp = api_client.get("/api/products?q=Pro")
    """
    from utils.api_client import ApiClient
    import json
    from pathlib import Path

    client = ApiClient(base_url=settings.base_url)
    # 复用 auth_state 的 cookie，避免重复登录
    state = json.loads(Path(auth_state).read_text(encoding="utf-8"))
    client.inject_cookies(state.get("cookies", []))
    yield client
    client.close()
