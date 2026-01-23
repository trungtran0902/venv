import time, random
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===== Mở hộp thoại chọn file =====
root = tk.Tk()
root.withdraw()  # Ẩn cửa sổ chính của Tkinter
file_path = filedialog.askopenfilename(title="Chọn file Excel", filetypes=[("Excel Files", "*.xlsx")])

if not file_path:
    print("Bạn chưa chọn file!")
    exit()

df = pd.read_excel(file_path)

print("DANH SÁCH CỘT:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

idx = int(input("Nhập số thứ tự cột làm keyword: "))
keyword_col = df.columns[idx]
keywords = df[keyword_col].dropna().astype(str).tolist()

print(f"Đã chọn cột: {keyword_col}")
print("5 keyword đầu:")
for k in keywords[:5]:
    print("-", k)

# ===== Cấu hình Chrome =====
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 20)

results = []

# ===== Chạy từng keyword =====
for kw in keywords:
    print(f"\nĐang tìm: {kw} legal name")
    driver.get("https://www.google.com")
    time.sleep(random.uniform(2, 4))

    search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))

    # Tạo từ khóa dạng: "MM Mega Market An Phú legal name"
    search_term = f"{kw} legal name"

    # Truyền từ khóa vào ô tìm kiếm
    search_box.clear()
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.ENTER)

    try:
        # Chờ kết quả tải và kiểm tra phần thông tin tổng quan
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//div[contains(@class, 'kp-header')]")))  # Xác nhận phần tử chứa thông tin tổng quan

    except Exception as e:
        print(f"Lỗi khi tìm thấy phần tử: {e}")
        continue

    data = {"keyword": kw}

    try:
        # Tìm phần tử chứa thông tin tổng quan (không phụ thuộc vào vị trí)
        ai_info_section = driver.find_element(By.XPATH, "//div[contains(@class, 'kno-rdesc')]")
        data["ai_info"] = ai_info_section.text.strip() if ai_info_section else "Không có dữ liệu"
    except Exception as e:
        print(f"Lỗi khi lấy dữ liệu từ AI info: {e}")
        data["ai_info"] = "Không lấy được thông tin"

    print(data)
    results.append(data)

    # ===== Autosave sau mỗi record =====
    out_df = pd.DataFrame(results)
    out_file = "ket_qua_google_legal_name.xlsx"
    out_df.to_excel(out_file, index=False)
    print(f"Đã lưu kết quả sau từ khóa: {kw}")

# ===== Đóng trình duyệt =====
print(f"\nTất cả kết quả đã được lưu vào: {out_file}")
input("Nhấn Enter để đóng trình duyệt...")
driver.quit()
