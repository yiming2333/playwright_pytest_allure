"""API + UI hybrid tests.

Demonstrates how to prepare/verify test data via API, then validate
the results through the UI layer.
"""

from __future__ import annotations

import allure
import pytest
import requests

from config import settings
from utils.api_client import ApiClient

BASE_URL = settings.base_url


@pytest.fixture
def api_session(auth_state: str) -> requests.Session:
    """API session fixture - reuses auth_state token to avoid duplicate login.

    推荐改用 conftest.py 提供的 api_client fixture（基于 ApiClient 封装），
    本 fixture 为兼容旧用例保留。
    """
    import json
    from pathlib import Path

    session = requests.Session()

    state_path = Path(auth_state)
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
        for cookie in state.get("cookies", []):
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

    def test_api_search_then_ui_verify(self, page, api_client: ApiClient):
        """通过 API 搜索商品，再用 UI 验证同一结果（示范 ApiClient 用法）。"""
        # 用 ApiClient 而非裸 requests
        api_resp = api_client.get("/api/products", params={"q": "Pro"})
        api_data = api_resp.json()
        api_count = api_data["total"]

        page.goto(BASE_URL)
        page.fill("#search-keyword", "Pro")
        page.click("button:has-text('搜 索')")
        page.wait_for_load_state("networkidle")

        ui_total = page.locator("#search-total").text_content()
        assert f"共 {api_count} 件商品" in ui_total

    def test_api_login_then_ui_dashboard(self, page, api_client: ApiClient):
        """复用登录态后，验证浏览器可访问受保护页面。"""
        # 用复用的 api_client 调通需要登录的 API
        userinfo = api_client.get("/api/userinfo")
        assert userinfo.status_code == 200
        assert userinfo.json()["role"] == "admin"

        page.goto(f"{BASE_URL}/dashboard")

        assert "/login" not in page.url, "Dashboard should be accessible with valid login state"

        user_info = page.locator("#user-detail")
        user_info.wait_for(state="visible", timeout=5000)
        assert "admin" in user_info.text_content().lower()
