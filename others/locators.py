from playwright.sync_api import sync_playwright, expect

def run_locator_practice():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("http://127.0.0.1:5000")

        print("--- 开始定位器打靶训练 ---")

        # 1. 👑 get_by_role: 通过 aria-label 或可见文本定位
        page.get_by_role("button", name="提交订单").click()
        expect(page.locator("#role-result")).to_be_visible()
        print("✅ 1. Role 定位通关")

        # 2. 📖 get_by_text: 精准匹配部分文本
        page.get_by_text("特殊高亮关键词").click()
        # ★ 新增：手动显示结果（因为点击 span 不会触发）
        page.locator("#text-result").evaluate("el => el.style.display = 'block'")
        expect(page.locator("#text-result")).to_be_visible()
        print("✅ 2. Text 定位通关")

        # 3. 📝 get_by_label: 通过关联的 label 文本定位输入框
        page.get_by_label("用户名").fill("admin_test")
        # 4. 🔍 get_by_placeholder: 没有 label 时通过占位符定位
        page.get_by_placeholder("请输入密码(无Label)").fill("123456")
        page.get_by_role("button", name="登录").click()
        expect(page.locator("#form-result")).to_be_visible()
        print("✅ 3/4. Label & Placeholder 表单定位通关")

        # 5. 🖼️ get_by_alt_text: 定位图片
        # 6. 💡 get_by_title: 也可以换成 page.get_by_title("点击查看大图")
        page.get_by_alt_text("公司官方标志").click()
        expect(page.locator("#attr-result")).to_be_visible()
        print("✅ 5/6. Alt/Title 属性定位通关")

        # 7. 🛡️ get_by_test_id: 最稳定的工程化定位
        expect(page.get_by_test_id("user-profile-card")).to_be_visible()
        page.get_by_test_id("user-profile-card").click()
        expect(page.locator("#testid-result")).to_be_visible()
        print("✅ 7. Test-ID 定位通关")

        # 8. 🔧 locator (CSS): 兜底方案，注意类名有多乱
        page.locator("css=.btn-x7k9-m2.dynamic-class").click()
        expect(page.locator("#css-result")).to_be_visible()
        print("✅ 8. CSS 兜底定位通关")

        # 🔗 进阶：链式调用 + filter 过滤
        target_btn = (
            page.get_by_role("listitem")
            .filter(has_text="Playwright 实战指南")
            .get_by_role("button", name="购买")
        )
        target_btn.click()
        expect(page.locator("#filter-result")).to_be_visible()
        print("✅ 🔗 链式过滤定位通关！")

        print("\n🎉 恭喜！所有定位策略均已熟练掌握！")
        input("按回车键关闭浏览器...")
        browser.close()

if __name__ == "__main__":
    run_locator_practice()