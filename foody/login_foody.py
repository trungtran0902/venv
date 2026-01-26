from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir="foody_profile",
        headless=False
    )
    page = browser.new_page()
    page.goto("https://www.foody.vn")

    print("👉 HÃY LOGIN BẰNG TAY, XONG THÌ ĐÓNG TAB")
    page.wait_for_timeout(600000)  # 10 phút
