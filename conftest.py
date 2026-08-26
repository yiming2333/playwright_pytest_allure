"""Pytest configuration and shared fixtures for Playwright tests."""

from __future__ import annotations

from datetime import datetime

import allure
import pytest
import requests
from playwright.sync_api import Page

BASE_URL = "http://127.0.0.1:5000"


# ========== Report Hooks ==========
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test execution result for Allure attachment on failure."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        item.rep_call = report


@pytest.fixture(autouse=True)
def _screenshot_on_failure(request, page):
    """Attach screenshot and HTML trace to Allure report on test failure."""
    yield
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            shot = page.screenshot(full_page=True)
            allure.attach(
                shot,
                name=f"failure_screenshot_{ts}",
                attachment_type=allure.attachment_type.PNG,
            )
            html = page.content()
            allure.attach(
                html,
                name=f"page_source_{ts}",
                attachment_type=allure.attachment_type.HTML,
            )
        except Exception:
            pass


# ========== Session-level Fixture: Global login state ==========
@pytest.fixture(scope="session")
def auth_state(tmp_path_factory, playwright) -> str:
    """
    Login once per test session and persist storage_state.
    All subsequent test cases automatically reuse the login state.

    Uses pytest-playwright's playwright fixture to avoid asyncio event loop conflict.
    """
    state_file = tmp_path_factory.mktemp("auth") / "state.json"

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    resp = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": "admin", "password": "admin123"},
        timeout=10,
    )
    resp.raise_for_status()
    token = resp.json().get("token", "")

    page.goto(BASE_URL)
    context.add_cookies([
        {"name": "auth_token", "value": token, "domain": "127.0.0.1", "path": "/"},
        {"name": "username", "value": "admin", "domain": "127.0.0.1", "path": "/"},
        {"name": "user_role", "value": "admin", "domain": "127.0.0.1", "path": "/"},
    ])

    context.storage_state(path=str(state_file))
    browser.close()

    return str(state_file)


# ========== Browser Context Configuration ==========
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, auth_state: str) -> dict:
    """All browser contexts automatically carry the login state."""
    return {
        **browser_context_args,
        "storage_state": auth_state,
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    """Configure browser launch arguments. slow_mo=0 for speed; bump up for debugging."""
    return {
        **browser_type_launch_args,
        "headless": True,
        "slow_mo": 0,
    }


# ========== Function-level Fixture: Navigate to home page ==========
@pytest.fixture(autouse=True)
def navigate_to_home(request, page: Page):
    """Navigate to the home page before each test.

    使用绝对 URL（不依赖 pytest-base-url 的 base_url 配置），
    确保 pytest-xdist 并发 worker 下也能正常跳转。

    Tests marked with @pytest.mark.no_home_navigation will skip this,
    useful when they need to start from a different URL (e.g. /login).
    """
    if request.node.get_closest_marker("no_home_navigation"):
        return
    page.goto(f"{BASE_URL}/")
    try:
        page.evaluate("localStorage.clear()")
    except Exception:
        pass
