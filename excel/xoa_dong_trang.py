import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# B1: Mở hộp thoại chọn file Excel
root = tk.Tk()
root.withdraw()  # Ẩn cửa sổ chính

input_file = filedialog.askopenfilename(
    title="Chọn file Excel",
    filetypes=[("Excel files", "*.xlsx *.xls")]
)

if not input_file:
    print("❌ Không chọn file. Kết thúc chương trình.")
    exit()

# B2: Đọc file Excel
df = pd.read_excel(input_file)

# B3: Xóa các dòng trắng
# - Xóa dòng mà toàn bộ ô rỗng
df_clean = df.dropna(how="all")

# - Xóa dòng mà cột 'Tên' rỗng (nếu có cột này)
if "Tên" in df_clean.columns:
    df_clean = df_clean.dropna(subset=["Tên"])

# B4: Tạo đường dẫn file output
folder = os.path.dirname(input_file)
filename = os.path.splitext(os.path.basename(input_file))[0]
output_file = os.path.join(folder, f"{filename}_clean.xlsx")

# B5: Lưu file mới
df_clean.to_excel(output_file, index=False)

print("✅ Hoàn tất!")
print("📂 File đã lưu:", output_file)
