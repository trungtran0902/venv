from playwright.sync_api import sync_playwright
import pandas as pd
import time
import os

# ======================
# CONFIG
# ======================
START_URL = "https://www.foody.vn/ha-noi/dia-diem?q=&ss=header_search_form"
OUTPUT_FILE = "foody_restaurants.csv"


# ======================
# FORCE REMOVE LOGIN POPUP (KEY)
# ======================
def force_remove_login_popup(page):
    try:
        page.evaluate("""
        () => {
            // remove popup / overlay
            document.querySelectorAll(`
                .modal,
                .modal-backdrop,
                .popup,
                .popup-login,
                .ReactModal__Overlay,
                .ReactModal__Content,
                [role="dialog"],
                .login-popup,
                .overlay,
                .backdrop
            `).forEach(el => el.remove());

            // remove fixed high z-index blockers
            document.querySelectorAll('*').forEach(el => {
                const style = window.getComputedStyle(el);
                if (style.position === 'fixed' && parseInt(style.zIndex || 0) > 1000) {
                    el.remove();
                }
            });

            // unlock scroll & interaction
            document.body.style.overflow = 'auto';
            document.body.style.pointerEvents = 'auto';
            document.documentElement.style.overflow = 'auto';

            document.body.classList.remove(
                'modal-open',
                'ReactModal__Body--open',
                'disable-scroll'
            );
        }
        """)
    except:
        pass


# ======================
# AUTO SAVE CSV
# ======================
def auto_save(row):
    df = pd.DataFrame([row])
    if not os.path.exists(OUTPUT_FILE):
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    else:
        df.to_csv(
            OUTPUT_FILE,
            mode="a",
            index=False,
            header=False,
            encoding="utf-8-sig"
        )


# ======================
# LOAD MORE BY BUTTON
# ======================
def load_more_by_button(page, max_round=100):
    print("🖱️ Load thêm kết quả bằng nút 'Xem tiếp kết quả'...")
    for i in range(max_round):
        force_remove_login_popup(page)

        btn = page.query_selector(
            "a:has-text('Xem tiếp kết quả'), a.btn-load-more"
        )
        if not btn:
            print("⛔ Không còn nút 'Xem tiếp kết quả'")
            break

        btn.scroll_into_view_if_needed()
        time.sleep(1)

        btn.click(force=True)
        print(f"➡️ Click 'Xem tiếp kết quả' ({i+1})")

        page.wait_for_timeout(2000)
        force_remove_login_popup(page)


# ======================
# GET SHOP LINKS (FILTERED)
# ======================
def get_shop_links(page):
    links = set()

    items = page.query_selector_all("div.foody-item a")
    for a in items:
        href = a.get_attribute("href")
        if not href:
            continue

        if not href.startswith("/ha-noi/"):
            continue

        # remove junk links
        if "?" in href or "/food/" in href or "top-thanh-vien" in href:
            continue

        if href.count("-") < 2:
            continue

        links.add("https://www.foody.vn" + href)

    return list(links)


# ======================
# CRAWL SINGLE SHOP
# ======================
def crawl_single_shop(page, url):
    print("🌐 Mở shop:", url)
    try:
        page.goto(url, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(1.5)

        force_remove_login_popup(page)

        name = None
        name_el = page.query_selector("h1.main-title")
        if name_el:
            name = name_el.inner_text().strip()

        if not name:
            print("⚠️ Không phải trang quán, bỏ qua")
            return False

        address = None
        addr_el = page.query_selector("span.street-address")
        if addr_el:
            address = addr_el.inner_text().strip()

        opening_hours = None
        hours_el = page.query_selector("div.time")
        if hours_el:
            opening_hours = hours_el.inner_text().strip()

        auto_save({
            "Name": name,
            "Address": address,
            "OpeningHours": opening_hours,
            "URL": url
        })

        print(f"💾 Saved: {name} | {address}")
        return True

    except Exception as e:
        print("❌ Lỗi shop:", e)
        return False


# ======================
# MAIN
# ======================
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        crawled = set()
        total_count = 0

        print("🌐 Mở Foody Hà Nội...")
        page.goto(START_URL, timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        force_remove_login_popup(page)

        # load list
        load_more_by_button(page)

        shop_links = get_shop_links(page)
        print(f"🔗 Tìm thấy {len(shop_links)} quán hợp lệ")

        for idx, url in enumerate(shop_links, start=1):
            if url in crawled:
                continue

            crawled.add(url)

            print(f"🔎 ({idx}/{len(shop_links)})")
            ok = crawl_single_shop(page, url)
            if ok:
                total_count += 1

            time.sleep(1.2)

            page.go_back()
            page.wait_for_load_state("domcontentloaded")
            time.sleep(1)

            force_remove_login_popup(page)

        browser.close()

    print(f"\n🎉 DONE – Tổng {total_count} quán đã crawl")


# ======================
# ENTRY
# ======================
if __name__ == "__main__":
    main()
