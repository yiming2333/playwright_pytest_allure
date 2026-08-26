"""Parameterized tests for search, form validation, and cart isolation."""

from __future__ import annotations

import allure
import pytest

from config import settings
from utils.data_loader import load_params, load_ids

BASE_URL = settings.base_url


@allure.feature("参数化测试")
@allure.story("商品搜索参数化")
@allure.severity(allure.severity_level.NORMAL)
class TestSearchParametrize:
    """Product search parameterized tests. 数据从 config/test_data.json 加载。"""

    @pytest.mark.parametrize(
        "keyword, expected_count",
        load_params("search_keywords", "keyword", "expected_count"),
        ids=load_ids("search_keywords"),
    )
    def test_search_keyword(self, page, keyword, expected_count):
        if keyword:
            page.fill("#search-keyword", keyword)
        page.click("button:has-text('搜 索')")
        page.wait_for_load_state("networkidle")

        total_text = page.locator("#search-total").text_content()
        assert f"共 {expected_count} 件商品" in total_text

    @pytest.mark.parametrize(
        "category, min_price, max_price, expected_count",
        load_params("search_filters", "category", "min_price", "max_price", "expected_count"),
        ids=load_ids("search_filters"),
    )
    def test_search_filter(self, page, category, min_price, max_price, expected_count):
        if category:
            page.select_option("#search-category", category)
        if min_price:
            page.fill("#search-min-price", str(min_price))
        if max_price < 99999:
            page.fill("#search-max-price", str(max_price))

        page.click("button:has-text('搜 索')")
        page.wait_for_load_state("networkidle")

        rows = page.locator("#product-tbody tr")
        assert rows.count() == expected_count


@allure.feature("参数化测试")
@allure.story("注册表单校验")
@allure.severity(allure.severity_level.CRITICAL)
class TestFormValidation:
    """Register form validation - parameterized negative tests. 数据外置在 test_data.json."""

    @pytest.mark.parametrize(
        "name, email, password, password2, expected_error",
        load_params("register_validations", "name", "email", "password", "password2", "expected_error"),
        ids=load_ids("register_validations"),
    )
    def test_register_validation(self, page, name, email, password, password2, expected_error):
        page.locator("h2:has-text('注册表单')").scroll_into_view_if_needed()

        page.fill("#reg-name", name)
        page.fill("#reg-email", email)
        page.fill("#reg-pass", password)
        page.fill("#reg-pass2", password2)
        page.click("form button:has-text('注 册')")

        error_elements = page.locator(".error-msg")
        all_errors = ""
        for i in range(error_elements.count()):
            el = error_elements.nth(i)
            if el.is_visible():
                all_errors += el.text_content()

        assert expected_error in all_errors, f"期望看到 '{expected_error}'，实际错误: '{all_errors}'"

    def test_register_success(self, page):
        """Positive test: all fields valid."""
        page.locator("h2:has-text('注册表单')").scroll_into_view_if_needed()

        page.fill("#reg-name", "testuser")
        page.fill("#reg-email", "test@example.com")
        page.fill("#reg-pass", "Abc12345")
        page.fill("#reg-pass2", "Abc12345")
        page.click("form button:has-text('注 册')")

        result = page.locator("#reg-result")
        assert result.is_visible()
        assert "注册成功" in result.text_content()


@allure.feature("参数化测试")
@allure.story("多角色登录")
@allure.severity(allure.severity_level.CRITICAL)
class TestLoginParametrize:
    """Login parameterized - multi-role tests."""

    @pytest.mark.no_home_navigation
    @pytest.mark.parametrize("username, password, expected_role", [
        ("admin", "admin123", "admin"),
        ("editor", "edit456", "editor"),
        ("viewer", "view789", "viewer"),
    ], ids=["管理员登录", "编辑员登录", "观察者登录"])
    def test_login_roles(self, page, username, password, expected_role):
        page.goto(f"{BASE_URL}/login")

        page.fill("#login-user", username)
        page.fill("#login-pass", password)
        page.click("#login-btn")

        result = page.locator("#login-result")
        result.wait_for(state="visible", timeout=5000)
        assert "登录成功" in result.text_content()


@allure.feature("并发测试")
@allure.story("购物车隔离验证")
@allure.severity(allure.severity_level.CRITICAL)
class TestCartParallel:
    """Cart tests - verify parallel execution isolation."""

    def test_add_to_cart(self, page):
        """Add product to cart."""
        page.evaluate("addToCart(1, 'iPhone 15 Pro', 8999)")

        toast = page.locator(".toast")
        toast.wait_for(state="visible", timeout=5000)
        assert "已加入购物车" in toast.text_content()

        count = page.locator("#cart-count").text_content()
        assert int(count) >= 1

    def test_cart_isolation(self, page):
        """Verify cart isolation - each context is independent."""
        count = page.locator("#cart-count").text_content()
        assert count == "0", "New context cart should be empty (parallel isolation)"
