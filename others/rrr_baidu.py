from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.baidu.com/")
    with page.expect_popup() as page1_info:
        page.get_by_role("link", name="复杂问题就找文心助手，深入思考回答更优 ").click()
    page1 = page1_info.value

    # Step 1: 打开一级下拉菜单
    page1.get_by_test_id("chat-mode-selector").click()
    # Step 2: 等待一级菜单可见（防御性等待）
    expect(page1.get_by_role("menu", name="选择回答模式")).to_be_visible(timeout=5000)
    # Step 3: ⭐ 补全录制缺失的关键步骤 —— 点击"模型 自动"展开二级菜单
    # page1.get_by_text("模型 自动").click()
    page1.get_by_test_id("chat-mode-model-row").click()
    # Step 4: 等待二级菜单中的"文心"选项出现
    wenxin_option = page1.get_by_role("menuitemradio", name="文心 5.1")
    expect(wenxin_option).to_be_visible(timeout=5000)
    # Step 5: 点击"文心"
    wenxin_option.click()

    page1.get_by_role("textbox").fill("hello,world")
    page1.get_by_role("textbox").press("Enter")

    # ✅ 修复2：直接给 to_contain_text 足够的超时时间
    # Playwright 会在超时内持续轮询，一旦文本出现就通过
    expect(
        page1.locator("#conversation-flow-content")
    ).to_contain_text("hello,world", timeout=60000)

    expect(page1.get_by_text("文心 5.1 为你解答")).to_be_visible()

    expect(page1.locator(".cos-icon.cos-icon-exchange")).to_be_visible()
    expect(page1.locator("[id=\"0\"]")).to_match_aria_snapshot("- banner: 文心 5.1 为你解答")

    page1.screenshot(path="baidu.png")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

