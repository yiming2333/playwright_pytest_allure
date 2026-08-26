import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": None,  # 👈 取消固定大小
        "no_viewport": True,  # 👈 让窗口自己决定
    }

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": False,
        "slow_mo": 500,  # 减慢速度，方便你跟踪
        "args": ["--start-maximized"],  # 👈 关键：启动就最大化
    }


@pytest.fixture(autouse=True)
def setup_target_page(page: Page):
    """每个测试前自动打开靶场首页"""
    page.goto("/")
    yield page