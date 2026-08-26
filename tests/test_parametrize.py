"""Parameterized tests for search, form validation, and cart isolation."""

from __future__ import annotations

import allure
import pytest

BASE_URL = "http://127.0.0.1:5000"


@allure.feature("参数化测试")
@allure.story("商品搜索参数化")
@allure.severity(allure.severity_level.NORMAL)
class TestSearchParametrize:
    """Product search parameterized tests."""

    @pytest.mark.parametrize("keyword, expected_count", [
        ("", 8),
        ("Pro", 3),
        ("书籍", 3),
        ("iPhone", 1),
        ("不存在的商品", 0),
    ], ids=["全部商品", "搜索Pro", "搜索书籍", "搜索iPhone", "无结果"])
    def test_search_keyword(self, page, keyword, expected_count):
        if keyword:
            page.fill("#search-keyword", keyword)
        page.click("button:has-text('搜 索')")
        page.wait_for_load_state("networkidle")

        total_text = page.locator("#search-total").text_content()
        assert f"共 {expected_count} 件商品" in total_text

    @pytest.mark.parametrize("category, min_price, max_price, expected_count", [
        ("书籍", 0, 100, 3),
        ("", 5000, 20000, 3),
        ("手机", 0, 99999, 1),
    ], ids=["低价书籍", "高价商品", "手机分类"])
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
    """Register form validation - parameterized negative tests."""

    @pytest.mark.parametrize("name, email, password, password2, expected_error", [
        ("", "a@b.com", "Abc12345", "Abc12345", "用户名不能为空"),
        ("ab", "a@b.com", "Abc12345", "Abc12345", "用户名需要3-16位字符"),
        ("admin", "", "Abc12345", "Abc12345", "邮箱不能为空"),
        ("admin", "invalid", "Abc12345", "Abc12345", "邮箱格式不正确"),
        ("admin", "a@b.com", "", "Abc12345", "密码不能为空"),
        ("admin", "a@b.com", "short", "short", "密码至少需要8位"),
        ("admin", "a@b.com", "alllowercase1", "alllowercase1", "密码需包含大小写字母和数字"),
        ("admin", "a@b.com", "Abc12345", "Different1", "两次输入的密码不一致"),
    ], ids=[
        "空用户名", "用户名太短", "空邮箱", "邮箱格式错误",
        "空密码", "密码太短", "密码复杂度不够", "密码不一致"
    ])
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
