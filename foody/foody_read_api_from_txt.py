import requests
import time
import tkinter as tk
from tkinter import filedialog


# ======================
# COOKIE ĐĂNG NHẬP
# ======================
COOKIE = "..."   # 🔴 GIỮ NGUYÊN COOKIE BẠN ĐÃ CÓ


# ======================
# CHỌN FILE TXT
# ======================
def choose_txt_file():
    root = tk.Tk()
    root.withdraw()  # ẩn cửa sổ chính

    file_path = filedialog.askopenfilename(
        title="Chọn file TXT chứa link API Foody",
        filetypes=[("Text files", "*.txt")]
    )
    return file_path


# ======================
# MAIN
# ======================
def main():
    # B1: mở hộp thoại chọn file
    txt_file = choose_txt_file()
    if not txt_file:
        print("❌ Chưa chọn file")
        return

    print("📂 File đã chọn:", txt_file)

    # đọc danh sách link
    with open(txt_file, "r", encoding="utf-8") as f:
        api_urls = [line.strip() for line in f if line.strip()]

    print(f"🔗 Tổng link API: {len(api_urls)}\n")

    # session requests
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.foody.vn/",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": COOKIE
    })

    total_place = 0

    # B2 + B3: gọi từng API và lấy dữ liệu
    for idx, api_url in enumerate(api_urls, start=1):
        print(f"\n🌐 [{idx}/{len(api_urls)}] GET:", api_url)

        try:
            r = s.get(api_url, timeout=15)
            print("Status:", r.status_code)

            if r.status_code != 200:
                print("❌ Lỗi request")
                continue

            js = r.json()
            items = js.get("Items", [])

            print(f"Số quán trong batch: {len(items)}\n")

            for i, place in enumerate(items, start=1):
                total_place += 1
                print(f"#{total_place}")
                print("Tên        :", place.get("Name"))
                print("Địa chỉ    :", place.get("Address"))
                print("Điện thoại :", place.get("Phone", "Không có"))
                print("Rating     :", place.get("AvgRating"))
                print("-" * 40)

            # nghỉ nhẹ cho an toàn
            time.sleep(1.2)

        except Exception as e:
            print("❌ Lỗi:", e)

    print(f"\n🎉 DONE – Tổng số quán lấy được: {total_place}")


if __name__ == "__main__":
    main()
