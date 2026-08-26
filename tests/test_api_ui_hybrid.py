"""API + UI hybrid tests.

Demonstrates how to prepare/verify test data via API, then validate
the results through the UI layer.
"""

from __future__ import annotations

import allure
import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture
def api_session(auth_state: str) -> requests.Session:
    """API session fixture - reuses auth_state token to avoid duplicate login.

    auth_state (session-scoped) already performed login and persisted
    cookies into storage_state. We read those cookies and inject them
    into a requests.Session so API calls are authenticated without
    hitting /api/login a second time.
    """
    import json
    from pathlib import Path

    session = requests.Session()

    # storage_state JSON 包含 cookies 数组，复用即可避免重复登录
    state_path = Path(auth_state)
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for cookie in state.get("cookies", []):
            # requests 用的 cookie 字段名和 Playwright storage_state 一致
            session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain", "127.0.0.1"),
                path=cookie.get("path", "/"),
            )

    yield session
    session.close()


@allure.feature("API+UI 混合测试")
@allure.story("API 准备数据 + UI 验证")
@allure.severity(allure.severity_level.CRITICAL)
class TestAPIUIHybrid:
    """API + UI hybrid verification tests."""

    def test_api_search_then_ui_verify(self, page, api_session):
        """Search via API, then verify the same result through the UI."""
        api_resp = api_session.get(f"{BASE_URL}/api/products?q=Pro")
        api_data = api_resp.json()
        api_count = api_data["total"]

        page.goto(BASE_URL)
        page.fill("#search-keyword", "Pro")
        page.click("button:has-text('搜 索')")
        page.wait_for_load_state("networkidle")

        ui_total = page.locator("#search-total").text_content()
        assert f"共 {api_count} 件商品" in ui_total

    def test_api_login_then_ui_dashboard(self, page, api_session):
        """After API login, verify the browser can access protected pages."""
        # 验证复用的 session 能调通需要登录的 API
        userinfo = api_session.get(f"{BASE_URL}/api/userinfo")
        assert userinfo.status_code == 200
        assert userinfo.json()["role"] == "admin"

        page.goto(f"{BASE_URL}/dashboard")

        assert "/login" not in page.url, "Dashboard should be accessible with valid login state"

        user_info = page.locator("#user-detail")
        user_info.wait_for(state="visible", timeout=5000)
        assert "admin" in user_info.text_content().lower()
