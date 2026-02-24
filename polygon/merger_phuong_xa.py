import json
import glob
import os
import tkinter as tk
from tkinter import filedialog

# Ẩn cửa sổ chính
root = tk.Tk()
root.withdraw()

# Chọn thư mục
folder_path = filedialog.askdirectory(title="Chọn thư mục chứa các file GeoJSON")

if not folder_path:
    print("Bạn chưa chọn thư mục.")
    exit()

# Lấy file
files = glob.glob(os.path.join(folder_path, "*.geojson"))

if not files:
    print("Không tìm thấy file GeoJSON.")
    exit()

all_features = []

# Đọc từng file và giữ nguyên feature
for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

        if data["type"] == "FeatureCollection":
            all_features.extend(data["features"])

        elif data["type"] == "Feature":
            all_features.append(data)

# Tạo FeatureCollection mới
merged_geojson = {
    "type": "FeatureCollection",
    "features": all_features
}

# Xuất file
output_path = os.path.join(folder_path, "merged_keep_features.geojson")

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged_geojson, f, ensure_ascii=False)

print("✅ Đã merge xong!")
print(f"📁 File xuất tại: {output_path}")
print(f"📊 Tổng số feature: {len(all_features)}")