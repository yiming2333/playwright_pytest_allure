# pages/base_page.py
from playwright.sync_api import Page, expect

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def expect_result_visible(self, card_title: str, text: str = "成功", timeout=5000):
        """兼容旧用例：默认为'成功'，但也支持传入自定义文本"""
        result_locator = self.wait_for_card_result_visible(card_title)
        expect(result_locator).to_be_visible(timeout=timeout)
        expect(result_locator).to_contain_text(text, timeout=timeout)

    def wait_for_card_result_visible(self, card_title: str):
        # 1. 先定位到卡片容器（标题的父级）
        card_locator = (
            self.page.get_by_role("heading", name=card_title)
            .locator("..")  # 这里就是卡片 div
        )
        # 2. 滚动卡片本身到视口中央（卡片是可见的，滚动绝对有效）
        card_locator.scroll_into_view_if_needed()

        # 3. 再定位内部的 .result 并等待可见
        result_locator = card_locator.locator(".result")
        result_locator.wait_for(state="visible", timeout=5000)
        return result_locator