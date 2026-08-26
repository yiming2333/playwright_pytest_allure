import allure
import pytest
from playwright.sync_api import expect

from pages.locator_range_page import LocatorRangePage

CARD_ROLE_BASIC = "1. Role 定位 (首选 👑)"
CARD_ROLE_ADVANCED = "2. Role 进阶技巧 (level / expanded)"
CARD_TEXT = "3. Text 文本定位 (模糊/精确/正则)"
CARD_FORM = "4. Label & Placeholder 表单定位"
CARD_ATTR = "5. Alt & Title 属性定位"
CARD_TESTID = "6. Test-ID 定位 (终极防御 🛡️)"
CARD_CSS = "7. CSS / XPath 兜底 (不推荐 ⚠️)"
CARD_ADVANCED = "8. 进阶大招：链式 / Filter / has / nth"


@allure.feature("Role 定位")
@allure.story("基础 Role 定位")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.role
class TestRoleLocator:
    def test_button(self, page):
        pom = LocatorRangePage(page)
        pom.click_normal_button()
        pom.expect_result_visible(CARD_ROLE_BASIC)

    def test_link(self, page):
        pom = LocatorRangePage(page)
        pom.click_link()
        pom.expect_result_visible(CARD_ROLE_BASIC)

    def test_textbox(self, page):
        pom = LocatorRangePage(page)
        pom.fill_textbox("hello")
        assert page.get_by_role("textbox", name="textbox角色").input_value() == "hello"

    def test_heading(self, page):
        pom = LocatorRangePage(page)
        expect(pom.get_heading_locator("Playwright 定位器全能靶场 v2.0")).to_be_visible()

    def test_checkbox(self, page):
        pom = LocatorRangePage(page)
        pom.check_checkbox()
        expect(page.get_by_role("checkbox")).to_be_checked()

    def test_menuitem(self, page):
        pom = LocatorRangePage(page)
        pom.click_menuitem()
        pom.expect_result_visible(CARD_ROLE_BASIC)


@allure.feature("Role 定位")
@allure.story("Role 进阶技巧")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.role
class TestRoleAdvanced:
    def test_heading_level(self, page):
        pom = LocatorRangePage(page)
        h2 = pom.get_h2_article_title()
        expect(h2).to_be_visible()
        expect(h2).to_have_js_property("tagName", "H2")

    def test_expanded_state(self, page):
        pom = LocatorRangePage(page)
        details = pom.get_details_element()
        expect(details).not_to_have_attribute("open")
        pom.toggle_details_panel()
        expect(details).to_have_attribute("open")
        pom.expect_result_visible(CARD_ROLE_ADVANCED)


@allure.feature("文本定位")
@allure.story("模糊/精确/正则匹配")
@allure.severity(allure.severity_level.NORMAL)
class TestTextLocator:
    def test_fuzzy_match(self, page):
        pom = LocatorRangePage(page)
        expect(pom.get_fuzzy_login_locator()).to_have_count(4)

    def test_exact_match(self, page):
        pom = LocatorRangePage(page)
        expect(pom.get_exact_login_locator()).to_have_count(0)

    def test_regex_match(self, page):
        pom = LocatorRangePage(page)
        expect(pom.get_welcome_admin_locator()).to_be_visible()


@allure.feature("表单定位")
@allure.story("Label & Placeholder")
@allure.severity(allure.severity_level.NORMAL)
class TestFormLocators:
    def test_label(self, page):
        pom = LocatorRangePage(page)
        pom.fill_email("test@example.com")
        expect(page.get_by_label("电子邮箱")).to_have_value("test@example.com")

    def test_placeholder(self, page):
        pom = LocatorRangePage(page)
        pom.fill_password("secret123")
        expect(page.get_by_placeholder("请输入密码(无Label)")).to_have_value("secret123")

    def test_form_submit_triggers_result(self, page):
        pom = LocatorRangePage(page)
        pom.fill_email("test@example.com")
        pom.fill_password("secret123")
        pom.submit_form()
        pom.expect_result_visible(CARD_FORM)


@allure.feature("属性定位")
@allure.story("Alt & Title & Test-ID")
@allure.severity(allure.severity_level.NORMAL)
class TestAttributeLocators:
    def test_alt_text(self, page):
        pom = LocatorRangePage(page)
        pom.click_logo_by_alt()
        pom.expect_result_visible(CARD_ATTR)

    def test_title(self, page):
        pom = LocatorRangePage(page)
        expect(pom.get_title_locator()).to_be_visible()

    def test_test_id(self, page):
        pom = LocatorRangePage(page)
        pom.click_user_profile_card()
        pom.expect_result_visible(CARD_TESTID)


@allure.feature("兜底定位")
@allure.story("CSS / XPath")
@allure.severity(allure.severity_level.MINOR)
class TestCSSXPathFallback:
    def test_css_fallback(self, page):
        pom = LocatorRangePage(page)
        pom.click_dynamic_class_button_css()
        pom.expect_result_visible(CARD_CSS)

    def test_xpath_fallback(self, page):
        pom = LocatorRangePage(page)
        pom.click_dynamic_class_button_xpath()
        pom.expect_result_visible(CARD_CSS)


@allure.feature("进阶定位")
@allure.story("链式 / Filter / has / nth")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.advanced
class TestAdvancedChaining:
    def test_chain_locator(self, page):
        pom = LocatorRangePage(page)
        pom.buy_first_product_in_list()
        pom.expect_result_visible(CARD_ADVANCED)

    def test_filter_has_text(self, page):
        pom = LocatorRangePage(page)
        pom.buy_product_by_name("Playwright 实战指南")
        pom.expect_result_visible(CARD_ADVANCED)

    def test_filter_has_element(self, page):
        pom = LocatorRangePage(page)
        assert pom.get_delete_row_count() == 2
        pom.delete_row_by_filename("report.pdf")
        pom.expect_result_visible(CARD_ADVANCED)

    def test_nth_index(self, page):
        pom = LocatorRangePage(page)
        pom.click_nth_like_button(1)
        pom.expect_result_visible(CARD_ADVANCED)


@allure.feature("表单控件")
@allure.story("Select 下拉框")
@allure.severity(allure.severity_level.NORMAL)
class TestSelect:
    def test_select_by_value(self, page):
        pom = LocatorRangePage(page)
        pom.select_city_by_value("shanghai")
        assert page.get_by_label("选择城市").input_value() == "shanghai"
        pom.expect_result_visible("9. Select 下拉框")

    def test_select_by_label(self, page):
        pom = LocatorRangePage(page)
        pom.select_city_by_label("广州")
        assert page.get_by_label("选择城市").input_value() == "guangzhou"
        pom.expect_result_visible("9. Select 下拉框")


@allure.feature("表单控件")
@allure.story("Radio 单选框")
@allure.severity(allure.severity_level.NORMAL)
class TestRadio:
    def test_select_radio(self, page):
        pom = LocatorRangePage(page)
        pom.select_gender("女")
        assert pom.get_selected_gender() == "female"
        pom.expect_result_visible("10. Radio 单选框")


@allure.feature("高级交互")
@allure.story("Hover 悬停菜单")
@allure.severity(allure.severity_level.NORMAL)
class TestHover:
    def test_hover_and_click_menu(self, page):
        pom = LocatorRangePage(page)
        pom.hover_user_menu()
        page.get_by_text("个人中心").wait_for(state="visible")
        pom.click_menu_item("设置")
        pom.expect_result_visible("11. Hover 悬停菜单")


@allure.feature("高级交互")
@allure.story("iframe 交互")
@allure.severity(allure.severity_level.CRITICAL)
class TestIframe:
    def test_iframe_submit(self, page):
        pom = LocatorRangePage(page)
        pom.fill_username_in_iframe("playwright")
        pom.click_submit_in_iframe()
        expect(pom.get_iframe_result_locator()).to_be_visible()
        expect(pom.get_iframe_result_locator()).to_contain_text("✅ iframe 定位成功！")


@allure.feature("高级交互")
@allure.story("Multi-Select 多选框")
@allure.severity(allure.severity_level.CRITICAL)
class TestMultiSelect:
    CARD_TITLE = "13. Multi-Select 多选框"

    def test_select_multiple_by_value(self, page):
        pom = LocatorRangePage(page)
        pom.select_skills("playwright", "pytest")

        result_locator = pom.wait_for_card_result_visible(self.CARD_TITLE)
        assert pom.get_selected_skills() == ["playwright", "pytest"]
        expect(result_locator).to_contain_text("playwright, pytest")

    def test_select_all_via_button(self, page):
        pom = LocatorRangePage(page)
        pom.click_select_all_button()

        selected = pom.get_selected_skills()
        assert len(selected) == 5
        assert set(selected) == {"python", "playwright", "pytest", "docker", "k8s"}

        result_locator = pom.wait_for_card_result_visible(self.CARD_TITLE)
        expect(result_locator).to_be_visible()
        expect(result_locator).to_contain_text("python, playwright, pytest, docker, k8s")

    def test_deselect_and_reselect(self, page):
        pom = LocatorRangePage(page)
        pom.click_select_all_button()
        assert len(pom.get_selected_skills()) == 5

        pom.deselect_all_skills()
        assert pom.get_selected_skills() == []

        pom.select_skills("docker")

        result_locator = pom.wait_for_card_result_visible(self.CARD_TITLE)
        assert pom.get_selected_skills() == ["docker"]
        expect(result_locator).to_contain_text("docker")
