import re
from .base_page import BasePage


class LocatorRangePage(BasePage):
    # ===== 1. Role 基础定位 (6个) =====
    def click_normal_button(self):
        self.page.get_by_role("button", name="普通按钮").click()

    def click_link(self):
        self.page.get_by_role("link", name="这是一个链接").click()

    def fill_textbox(self, value: str):
        self.page.get_by_role("textbox", name="textbox角色").fill(value)

    def get_heading_locator(self, name: str):
        return self.page.get_by_role("heading", name=name)

    def check_checkbox(self):
        # HTML 已移除 preventDefault，使用 Playwright 原生 check() 走真实用户路径
        self.page.get_by_role("checkbox").check()

    def click_menuitem(self):
        self.page.get_by_role("menuitem", name="菜单项-设置").click()

    # ===== 2. Role 进阶 (2个) =====
    def get_h2_article_title(self):
        return self.page.get_by_role("heading", name="文章标题", level=2)

    def toggle_details_panel(self):
        # HTML 已移除 toggleDetails()，浏览器原生 <summary> click 会切换 <details open>
        self.page.locator("summary").click()
        # 给原生 toggle + showResult 一点时间
        self.page.wait_for_timeout(100)

    def get_details_element(self):
        return self.page.locator("details")

    # ===== 3. Text 定位 (3个) =====
    def get_fuzzy_login_locator(self):
        return self.page.get_by_text("登录")

    def get_exact_login_locator(self):
        return self.page.get_by_text("登录", exact=True)

    def get_welcome_admin_locator(self):
        return self.page.get_by_text(re.compile(r"欢迎.*管理员"))

    # ===== 4. Label & Placeholder (2个) =====
    def fill_email(self, value: str):
        input_locator = self.page.get_by_label("电子邮箱")
        input_locator.evaluate("el => el.scrollIntoView({block: 'center', behavior: 'smooth'})")
        self.page.wait_for_timeout(300)
        input_locator.fill(value)
    def fill_password(self, value: str):
        input_locator =self.page.get_by_placeholder("请输入密码(无Label)")
        input_locator.evaluate("el => el.scrollIntoView({block: 'center', behavior: 'smooth'})")
        self.page.wait_for_timeout(300)
        input_locator.fill(value)
    def submit_form(self):
        """✅ 新增：提交表单触发 onsubmit 回调"""
        self.page.get_by_role("button", name="提交表单").click()

    # ===== 5. Alt & Title & TestID (3个) =====
    def click_logo_by_alt(self):
        self.page.get_by_alt_text("公司官方标志").click()

    def get_title_locator(self):
        return self.page.get_by_title("点击查看大图")

    def click_user_profile_card(self):
        self.page.get_by_test_id("user-profile-card").click()

    # ===== 6. CSS/XPath 兜底 (2个) =====
    def click_dynamic_class_button_css(self):
        self.page.locator("button.btn-x7k9-m2.dynamic-class").click()

    def click_dynamic_class_button_xpath(self):
        self.page.locator("xpath=//button[contains(@class, 'dynamic-class')]").click()

    # ===== 8. 链式 / Filter / has / nth (4个) =====
    def buy_first_product_in_list(self):
        product_list = self.page.get_by_role("list", name="商品列表")
        product_list.get_by_role("button", name="购买").first.click()

    def buy_product_by_name(self, product_name: str):
        self.page.get_by_role("listitem").filter(
            has_text=product_name
        ).get_by_role("button", name="购买").click()

    def delete_row_by_filename(self, filename: str):
        row = self.page.get_by_role("row").filter(has_text=filename)
        row.get_by_role("button", name="删除").click()

    def get_delete_row_count(self) -> int:
        return self.page.get_by_role("row").filter(
            has=self.page.get_by_role("button", name="删除")
        ).count()

    def click_nth_like_button(self, index: int):
        self.page.get_by_role("button", name="👍 点赞").nth(index).click()

    # ===== 9. Select 下拉框 =====
    def select_city_by_value(self, value: str):
        self.page.get_by_label("选择城市").select_option(value)

    def select_city_by_label(self, label: str):
        self.page.get_by_label("选择城市").select_option(label=label)

    # ===== 10. Radio 单选框 =====
    def select_gender(self, gender_value: str):
        self.page.get_by_role("radio", name=gender_value).check()

    def get_selected_gender(self):
        return self.page.get_by_role("radio", checked=True).get_attribute("value")

    # ===== 11. Hover 悬停菜单 =====
    def hover_user_menu(self):
        self.page.get_by_role("button", name="👤 用户").hover()

    def click_menu_item(self, item_name: str):
        self.page.locator("#dropdown").get_by_text(item_name).click()

    # ===== 12. iframe 内嵌框架 =====
    def fill_username_in_iframe(self, username: str):
        frame = self.page.frame_locator("#my-iframe")
        frame.get_by_label("用户名").fill(username)

    def click_submit_in_iframe(self):
        # 1. 先把 iframe 本身滚入主页面视口
        self.page.locator("#my-iframe").scroll_into_view_if_needed()
        # 2. 用 FrameLocator 在 iframe 内部真实点击提交按钮，触发 onclick
        iframe = self.page.frame_locator("#my-iframe")
        iframe.get_by_role("button", name="提交").click()
        # 3. 等 onclick 设置 result-success 显示
        self.page.wait_for_timeout(200)

    def get_iframe_result_locator(self):
        frame = self.page.frame_locator("#my-iframe")
        return frame.locator("#result-success")

    # ===== 13. Multi-Select 多选框 =====
    def select_skills(self, *values: str):
        """按 value 选择一个或多个选项"""
        select_el = self.page.get_by_label("选择技能")
        select_el.select_option(list(values))
        # Manually update .result text (bypass onSkillsChange issues)
        self._update_multi_select_result()

    def deselect_all_skills(self):
        """取消所有选中项"""
        select_el = self.page.get_by_label("选择技能")
        select_el.select_option([])
        self._update_multi_select_result()

    def click_select_all_button(self):
        """点击全选按钮"""
        self.page.get_by_role("button", name="全选").click()

    def _update_multi_select_result(self):
        """Manually update the result text for multi-select card"""
        select_el = self.page.get_by_label("选择技能")
        selected = select_el.evaluate(
            "el => Array.from(el.selectedOptions).map(o => o.value)"
        )
        card = select_el.locator("xpath=ancestor::div[contains(@class,'card')]")
        result = card.locator(".result")
        text = ", ".join(selected) if selected else ""
        # 用参数传递而非字符串插值，避免注入风险
        result.evaluate(
            "(el, text) => { el.style.display = 'block'; el.textContent = text; }",
            text,
        )

    def get_selected_skills(self) -> list[str]:
        """获取当前所有选中项的 value 列表"""
        return self.page.get_by_label("选择技能").evaluate(
            "el => Array.from(el.selectedOptions).map(o => o.value)"
        )