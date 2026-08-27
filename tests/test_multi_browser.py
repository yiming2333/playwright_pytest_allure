"""Cross-browser compatibility tests.

Verifies that key UI interactions work correctly across browsers
(chromium, firefox, webkit) using pytest-playwright's browser_type fixture.
"""

from __future__ import annotations

import allure
import pytest

from config import settings

BASE_URL = settings.base_url

BROWSERS = ["chromium", "firefox", "webkit"]


@pytest.fixture(autouse=True)
def _verify_real_browser(page, request):
    """防回归断言：真实启动的浏览器必须与用例参数指定的浏览器一致。

    历史教训：indirect 参数化曾被插件原生 browser_type fixture 静默忽略
    （原生 fixture 只认 --browser 命令行参数，不读 request.param），
    导致 12 条用例 ID 显示 firefox/webkit、实际全程跑 chromium。
    conftest.py 已覆写 browser_type 修复此问题；本断言确保它永不复发——
    只要参数与真实浏览器不符，用例会立刻失败而不是静默降级。
    """
    callspec = getattr(request.node, "callspec", None)
    if callspec and "browser_type" in callspec.params:
        expected = callspec.params["browser_type"]
        actual = page.context.browser.browser_type.name
        assert actual == expected, (
            f"用例参数要求 {expected}，实际启动的是 {actual} —— "
            f"indirect 参数化失效，请检查 conftest.py 的 browser_type 覆写"
        )


@allure.feature("多浏览器测试")
@allure.story("跨浏览器兼容性")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.parametrize("browser_type", BROWSERS, indirect=True, ids=BROWSERS)
class TestCrossBrowser:
    """Cross-browser compatibility verification.

    Each test is automatically executed on chromium, firefox, and webkit.
    （依赖 conftest.py 覆写的 browser_type fixture 消费 indirect 参数；
    _verify_real_browser 会校验浏览器真实切换。）
    """

    def test_homepage_loads(self, page, browser_type):
        """Verify homepage loads correctly in all browsers."""
        page.wait_for_load_state("networkidle")
        assert page.title() == "Playwright 全能靶场 v3.0"

        assert page.locator("h1").is_visible()
        assert page.locator("#search-keyword").is_visible()

    def test_hover_menu(self, page, browser_type):
        """Hover menu interaction - cross-browser sensitive."""
        page.hover("#user-menu")

        dropdown = page.locator("#dropdown")
        dropdown.wait_for(state="visible", timeout=3000)

        page.locator(".menu-item", has_text="个人中心").click()

        toast = page.locator(".toast.info").first
        toast.wait_for(state="visible", timeout=5000)
        toast_text = toast.text_content(timeout=1000)
        assert "个人中心" in toast_text

    def test_iframe_interaction(self, page, browser_type):
        """iframe interaction - cross-browser."""
        page.wait_for_load_state("networkidle")

        iframe = page.frame_locator("#my-iframe")
        iframe.locator("#iframe-input").fill("测试用户")
        # 真实点击 iframe 内的提交按钮，触发 onclick 设置 result-success
        page.locator("#my-iframe").scroll_into_view_if_needed()
        iframe.get_by_role("button", name="提交").click()

        result = iframe.locator("#result-success")
        result.wait_for(state="visible", timeout=5000)
        result_text = result.text_content(timeout=1000)
        assert "✅ iframe 定位成功" in result_text

    def test_select_and_radio(self, page, browser_type):
        """Select and Radio form controls - cross-browser."""
        page.wait_for_load_state("networkidle")

        page.select_option("#city", "shanghai")
        toast = page.locator(".toast.info").first
        toast.wait_for(state="visible", timeout=5000)
        assert "上海" in toast.text_content(timeout=1000)

        page.check('input[type="radio"][value="female"]')
        toast_locator = page.locator(".toast.info")
        toast_locator.last.wait_for(state="visible", timeout=5000)
        assert "女" in toast_locator.last.text_content(timeout=1000)
