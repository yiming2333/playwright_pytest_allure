from playwright.sync_api import Playwright, sync_playwright, expect

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc")
    page.get_by_role("textbox").fill("学习 Playwright")
    page.get_by_role("textbox").press("Enter")
    # 方案二：直接用 first() 或 nth()（适合只有一个待办项的场景）
    page.get_by_role("checkbox").first.click()

    page.get_by_role("textbox").fill("666")
    page.get_by_role("textbox").press("Enter")
    # page.get_by_role(role="checkbox",name="Toggle Todo").click()
    # 方案一：先定位到包含特定文本的待办项，再找它的 checkbox
    page.get_by_role("listitem").filter(has_text="666").get_by_role("checkbox").click()

    page.get_by_role(role="button",name="Clear completed").click()

    expect(page.get_by_role("listitem").filter(has_text="学习 Playwright")).to_have_count(0)
    expect(page.get_by_role("listitem").filter(has_text="666")).to_have_count(0)
    # expect(page.get_by_role("checkbox")).to_have_count(0)
    page.screenshot(path="mvctodo.png")

    # ---------------------
    context.close()
    browser.close()


def run_3_item(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demo.playwright.dev/todomvc")
    # 优化：把定位器存起来复用（不仅快一点点，而且更优雅）
    input_box = page.get_by_role("textbox")
    for i in range(3):
        input_box.fill(f"任务{i}")
        input_box.press("Enter")

    page.get_by_role("listitem").filter(has_text="任务1").get_by_role("checkbox").click()

    page.get_by_role(role="button",name="Clear completed").click()

    expect(page.get_by_role("listitem").filter(has_text="任务")).to_have_count(2)
    expect(page.get_by_role("listitem").filter(has_text="任务1")).to_have_count(0)
    # 方案A：分别断言剩下的两个任务可见
    expect(page.get_by_role("listitem").filter(has_text="任务0")).to_be_visible()
    expect(page.get_by_role("listitem").filter(has_text="任务2")).to_be_visible()

    # 方案B（如果你依然想数个数，可以限定得更死）：要求列表项必须精确等于"任务0"或"任务2"
    # 但因为没有正则，目前你这种写法在实战中已经够用了，我上面说的只是“吹毛求疵”的工程洁癖。
    page.screenshot(path="mvctodo.png")

    # ---------------------
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run_3_item(playwright)

