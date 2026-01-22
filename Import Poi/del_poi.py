import os
import requests
import pandas as pd
from datetime import datetime
import csv

# ====== CẤU HÌNH ======
API_BASE_URL = "https://api-data.map4d.vn/map/manage/place/delete/"
AUTH_TOKEN = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJNMUtocHl1OGg1cjlxVkNfN29hbDJaUERseU9CRjJMazkwdlVBS2hTNko0In0.eyJqdGkiOiIxNDVlNTMzMi0yNGJlLTQ2OWQtYjE5Yy1kZGNhNWY0MDViMjQiLCJleHAiOjE3NjY2MzIyMjEsIm5iZiI6MCwiaWF0IjoxNzY1NzY4MjIyLCJpc3MiOiJodHRwczovL2FjY291bnRzLm1hcDRkLnZuL2F1dGgvcmVhbG1zL3ZpbWFwIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjM2MzZkMjhlLTRiYzctNGUxNy04YzUxLWEzZGFmOGQzY2EwNSIsInR5cCI6IkJlYXJlciIsImF6cCI6Im1hcDRkIiwiYXV0aF90aW1lIjoxNzY1NzY4MjIxLCJzZXNzaW9uX3N0YXRlIjoiNjNkMWRmYjEtMjU4Ny00M2QzLWE4MjEtMzFhNjcyNDE5MTNmIiwiYWNyIjoiMSIsInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJUcuG6p24gQW5oIFRydW5nIiwicHJlZmVycmVkX3VzZXJuYW1lIjoidHJ1bmciLCJsb2NhbGUiOiJ2aSIsImdpdmVuX25hbWUiOiJUcuG6p24gQW5oIiwiZmFtaWx5X25hbWUiOiJUcnVuZyIsImVtYWlsIjoidHJ1bmd0YUBpb3RsaW5rLmNvbS52biJ9.QNYhyzhxQhEQf4_Jy9CaL4MqsZii15aq5AqKPFbRqkS_pNpdgsNPMxxJGhGZ_sNXU3EdTRJsLCM1D7J0SAJkY6oWrS42QR-LLruYP0AZAwFhBCu3sSUppHmYHxbGXmrC8knFRBKbirBVW7DuPqM84_xtl_TFJpGg7LtlirI1d0Yoie1MWytNkgb9-2P2VLeHVZiMe_dSWvsGoI2ux0J17pDViiVeQHYeOdmcRinAbnfbuLGiO74OQAImXpd-ddW1M0HSNd1VOyxa4Xhi4BkCDSEuU0JXe8X1YDZZ2Y4UERVkI4MOiAZRXbmYEcFpZMXEZF0NC91nxEZLjh8j9IqaTQ"

headers = {
    "accept": "text/plain",
    "Authorization": AUTH_TOKEN
}

# ====== LOG ======
def get_log_file():
    today = datetime.now().strftime("%Y%m%d")
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return os.path.join(log_dir, f"del_poi_{today}.csv")


def write_log(place_id, status, message):
    log_file = get_log_file()
    file_exists = os.path.isfile(log_file)

    with open(log_file, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["time", "place_id", "status", "message"])

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, place_id, status, message])

# ====== KIỂM TRA TOKEN ======
def check_token():
    if not AUTH_TOKEN or "token_cua_ban" in AUTH_TOKEN:
        print("❗ Chưa cấu hình token. Vui lòng thêm token hợp lệ.")
        return False

    test_id = "test_invalid_id"  # ID giả, chỉ để kiểm tra xác thực
    url = f"{API_BASE_URL}{test_id}"
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 401:
            print("❗ Token không hợp lệ hoặc đã hết hạn.")
            return False
        else:
            print("✅ Token hợp lệ. Sẵn sàng xoá dữ liệu.")
            return True
    except Exception as e:
        print(f"⚠️ Không thể kết nối API để kiểm tra token: {e}")
        return False

# ====== XOÁ THEO ID ======
def delete_place_by_id(place_id):
    url = f"{API_BASE_URL}{place_id}"
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ Xoá thành công: {place_id}")
            write_log(place_id, "success", "Deleted successfully")
        else:
            print(f"❌ Lỗi xoá {place_id}: {response.status_code} - {response.text}")
            write_log(place_id, "error", f"{response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Lỗi kết nối cho {place_id}: {e}")
        write_log(place_id, "error", f"Connection error: {e}")

# ====== XOÁ THEO CÁCH NHẬP TAY ======
def delete_by_manual_input():
    while True:
        place_id = input("Nhập ID (hoặc Enter để thoát): ").strip()
        if not place_id:
            break
        delete_place_by_id(place_id)

# ====== XOÁ TỪ FILE ======
def delete_from_file():
    folder_path = input("Nhập đường dẫn thư mục chứa file: ").strip()
    file_name = input("Nhập tên file (ví dụ: data.csv hoặc data.xlsx): ").strip()

    file_path = os.path.join(folder_path, file_name)

    if not os.path.exists(file_path):
        print(f"❗ Không tìm thấy file: {file_path}")
        write_log("-", "error", f"File not found: {file_path}")
        return

    try:
        # Đọc dữ liệu
        if file_name.lower().endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file_name.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            print("❗ Định dạng file không được hỗ trợ. Hãy dùng CSV hoặc Excel.")
            write_log("-", "error", f"Unsupported file format: {file_name}")
            return

        if 'id' not in df.columns:
            print("❗ File phải có cột 'id'")
            write_log("-", "error", "File missing 'id' column")
            return

        ids = df['id'].dropna().astype(str).tolist()
        print(f"📄 Đọc được {len(ids)} ID từ file {file_name}")
        write_log("-", "info", f"Read {len(ids)} IDs from {file_name}")

        for idx, place_id in enumerate(ids, start=1):
            print(f"[{idx}/{len(ids)}] Đang xoá ID: {place_id}")
            write_log(place_id, "info", "Deleting...")
            delete_place_by_id(place_id)

    except Exception as e:
        print(f"⚠️ Lỗi khi đọc file: {e}")
        write_log("-", "error", f"File read error: {e}")

# ====== MENU CHÍNH ======
if __name__ == "__main__":
    print("=== KIỂM TRA TOKEN ===")
    if not check_token():
        print("⛔ Dừng chương trình vì token không hợp lệ.")
    else:
        print("=== CHỌN CHẾ ĐỘ ===")
        print("1. Nhập ID thủ công")
        print("2. Đọc ID từ file (CSV hoặc Excel)")

        choice = input("Nhập lựa chọn (1/2): ").strip()

        if choice == "1":
            delete_by_manual_input()
        elif choice == "2":
            delete_from_file()
        else:
            print("❗ Lựa chọn không hợp lệ.")
            write_log("-", "error", "Invalid menu choice")
