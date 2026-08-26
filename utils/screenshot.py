# utils/screenshot.py
"""
截图工具：失败自动截图 + 附加到 Allure 报告。

被 conftest.py 的 pytest_runtest_makereport 钩子调用。
"""
from __future__ import annotations

from typing import Optional

from utils.logger import get_logger

log = get_logger(__name__)


def capture_failure_screenshot(page, item) -> Optional[str]:
    """失败时截图并附加到 Allure。

    Args:
        page: Playwright Page 对象（可能为 None，如 fixture setup 失败）
        item: pytest Item

    Returns:
        截图文件路径，失败返回 None
    """
    if page is None:
        log.warning("Page 为 None，跳过截图（可能是 fixture setup 阶段失败）")
        return None

    try:
        screenshot_bytes = page.screenshot(full_page=True)
    except Exception as e:
        log.error(f"截图失败: {e}")
        return None

    # 附加到 Allure
    try:
        import allure
        allure.attach(
            screenshot_bytes,
            name=f"失败截图 - {item.name}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass

    # 同时附加页面源码（调试定位用）
    try:
        import allure
        html = page.content()
        allure.attach(
            html,
            name=f"页面源码 - {item.name}",
            attachment_type=allure.attachment_type.HTML,
        )
    except Exception:
        pass

    log.info(f"已为 {item.name} 生成失败截图")
    return "allure-attached"


def capture_step_screenshot(page, step_name: str) -> None:
    """主动截图记录关键步骤（非失败场景）。

    Args:
        page: Playwright Page 对象
        step_name: 步骤名（会作为 Allure 附件名）
    """
    if page is None:
        return
    try:
        screenshot_bytes = page.screenshot()
        import allure
        allure.attach(
            screenshot_bytes,
            name=step_name,
            attachment_type=allure.attachment_type.PNG,
        )
        log.debug(f"步骤截图已记录: {step_name}")
    except Exception as e:
        log.warning(f"步骤截图失败 ({step_name}): {e}")
