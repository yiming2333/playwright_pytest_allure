# pages/base_page.py
from playwright.sync_api import Page, expect


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def expect_result_visible(self, card_title: str, timeout=5000):
        """等待卡片 .result 元素可见。

        不再隐式验证 "成功" 文本（与 HTML 默认文案耦合过深且语义薄弱）。
        如需断言具体文本，请用 wait_for_card_result_visible() 拿到 locator
        后再写 expect(...).to_contain_text("xxx")。
        """
        result_locator = self.wait_for_card_result_visible(card_title)
        expect(result_locator).to_be_visible(timeout=timeout)

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