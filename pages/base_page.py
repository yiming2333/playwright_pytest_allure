# pages/base_page.py
"""BasePage - 所有 Page Object 的基类，封装通用操作 + 日志。"""
from playwright.sync_api import Page, expect

from utils.logger import get_logger


class BasePage:
    # 类级共享 logger，子类自动继承
    log = get_logger("pages.base_page")

    def __init__(self, page: Page):
        self.page = page

    # ---------- 通用导航 ----------
    def navigate(self, path: str = "/"):
        """跳转到指定路径"""
        from config import settings
        url = path if path.startswith("http") else f"{settings.base_url}{path}"
        self.log.info(f"navigate → {url}")
        self.page.goto(url)

    # ---------- 通用等待 ----------
    def wait_for_card_result_visible(self, card_title: str):
        """等待卡片 .result 元素可见。

        1. 定位卡片标题的父级（卡片容器）
        2. 滚动卡片到视口
        3. 等待卡片内 .result 可见
        """
        card_locator = self.page.get_by_role("heading", name=card_title).locator("..")
        card_locator.scroll_into_view_if_needed()

        result_locator = card_locator.locator(".result")
        result_locator.wait_for(state="visible", timeout=5000)
        return result_locator

    def expect_result_visible(self, card_title: str, timeout=5000):
        """等待卡片 .result 元素可见。

        不再隐式验证 "成功" 文本（与 HTML 默认文案耦合过深且语义薄弱）。
        如需断言具体文本，请用 wait_for_card_result_visible() 拿到 locator
        后再写 expect(...).to_contain_text("xxx")。
        """
        self.log.debug(f"等待卡片 .result 可见: {card_title}")
        result_locator = self.wait_for_card_result_visible(card_title)
        expect(result_locator).to_be_visible(timeout=timeout)

    # ---------- 通用操作 ----------
    def click(self, locator, **kwargs):
        """带日志的 click"""
        self.log.debug(f"click: {locator}")
        locator.click(**kwargs)

    def fill(self, locator, value: str, **kwargs):
        """带日志的 fill"""
        self.log.debug(f"fill: {value!r}")
        locator.fill(value, **kwargs)
