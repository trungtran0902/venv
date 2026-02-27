import requests
import time
import random
import tkinter as tk
from tkinter import filedialog
from openpyxl import Workbook, load_workbook
import os


# ======================
# COOKIE ĐĂNG NHẬP
# ======================
COOKIE = "..."   # 🔴 GIỮ NGUYÊN COOKIE BẠN ĐÃ CÓ


# ======================
# CHỌN FILE TXT
# ======================
def choose_txt_file():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Chọn file TXT chứa link API Foody",
        filetypes=[("Text files", "*.txt")]
    )
    return file_path


# ======================
# KHỞI TẠO / MỞ FILE EXCEL
# ======================
def init_excel(file_name="foody_data.xlsx"):
    if os.path.exists(file_name):
        wb = load_workbook(file_name)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Foody Map Data"
        ws.append([
            "STT",
            "Tên quán",
            "Địa chỉ",
            "Điện thoại",
            "Rating",
            "Latitude",
            "Longitude",
            "Distance",
            "IsDelivery",
            "IsOpening",
            "Google Maps"
        ])
        wb.save(file_name)

    return wb, ws


# ======================
# MAIN
# ======================
def main():
    # B1: chọn file TXT
    txt_file = choose_txt_file()
    if not txt_file:
        print("❌ Chưa chọn file TXT")
        return

    print("📂 File đã chọn:", txt_file)

    # đọc danh sách API
    with open(txt_file, "r", encoding="utf-8") as f:
        api_urls = [line.strip() for line in f if line.strip()]

    print(f"🔗 Tổng link API: {len(api_urls)}\n")

    # session request
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.foody.vn/",
        "X-Requested-With": "XMLHttpRequest",
        "Cookie": COOKIE
    })

    # Excel
    excel_file = "foody_data_HN_2.xlsx"
    wb, ws = init_excel(excel_file)

    # số dòng đã có
    total_place = ws.max_row - 1

    # B2: gọi từng API
    for idx, api_url in enumerate(api_urls, start=1):
        print(f"\n🌐 [{idx}/{len(api_urls)}] GET: {api_url}")

        try:
            r = s.get(api_url, timeout=15)
            print("Status:", r.status_code)

            if r.status_code != 200:
                print("❌ Lỗi request")
                continue

            js = r.json()
            items = js.get("Items", [])

            print(f"Số quán trong batch: {len(items)}")

            for place in items:
                total_place += 1

                lat = place.get("Latitude")
                lng = place.get("Longitude")
                distance = place.get("Distance")
                is_delivery = place.get("IsDelivery")
                is_opening = place.get("IsOpening")

                maps_url = ""
                if lat and lng:
                    maps_url = f"https://www.google.com/maps?q={lat},{lng}"

                ws.append([
                    total_place,
                    place.get("Name"),
                    place.get("Address"),
                    place.get("Phone", ""),
                    place.get("AvgRating"),
                    lat,
                    lng,
                    distance,
                    is_delivery,
                    is_opening,
                    maps_url
                ])

            # 💾 AUTO SAVE sau mỗi API
            wb.save(excel_file)
            print("💾 Đã lưu Excel")

            # ⏳ Delay ngẫu nhiên 2–3s
            sleep_time = random.uniform(2, 3)
            print(f"⏳ Nghỉ {sleep_time:.2f}s để tránh call API liên tục...")
            time.sleep(sleep_time)

        except Exception as e:
            print("❌ Lỗi:", e)

    print(f"\n🎉 DONE – Tổng số quán lấy được: {total_place}")
    print(f"📁 File Excel: {excel_file}")


if __name__ == "__main__":
    main()
