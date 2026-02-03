from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://www.foody.vn")

    print("👉 Đăng nhập Foody bằng tay (Google / Facebook / Email)")
    print("👉 Sau khi login xong, CHỜ 5–10s")

    page.wait_for_timeout(60000)  # 60 giây cho bạn login

    # LƯU COOKIE
    context.storage_state(path="foody_state_hcm.json")
    print("✅ Đã tạo foody_state_hcm.json")

    browser.close()
