import streamlit as st
import json
import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union
import tempfile
import os

st.set_page_config(page_title="GeoJSON Region Union", layout="wide")

st.title("🗺️ Merge Polygon GeoJSON Lựa Chọn")

# Bước 1: Upload tất cả các file GeoJSON
uploaded_files = st.file_uploader(
    "📂 Upload GeoJSON files",
    type=["geojson"],
    accept_multiple_files=True
)

# Kiểm tra xem có file được tải lên không
if uploaded_files:
    file_names = [file.name for file in uploaded_files]

    # Lưu trữ thông tin các nhóm merge
    if "merging_sessions" not in st.session_state:
        st.session_state.merging_sessions = []

    # Bước 2: Hiển thị các nhóm merge đã thêm
    for i, session in enumerate(st.session_state.merging_sessions):
        with st.expander(f"Nhóm merge {i+1}"):
            selected_files = st.multiselect(
                f"📌 Chọn các file cần merge (Nhóm {i+1})",
                options=file_names,
                default=session["files"]
            )
            output_filename = st.text_input(
                f"📁 Nhập tên file đầu ra cho nhóm {i+1}",
                value=session["output_filename"]
            )
            session["files"] = selected_files
            session["output_filename"] = output_filename

    # Bước 3: Nút Thêm nhóm merge mới
    if st.button("Thêm nhóm merge"):
        # Thêm nhóm merge vào session_state mà không cần gọi lại giao diện
        st.session_state.merging_sessions.append({
            "files": [],
            "output_filename": ""
        })

    # Bước 4: Thực thi các tác vụ merge
    if st.button("Thực Thi"):
        if not st.session_state.merging_sessions:
            st.warning("❌ Vui lòng thêm ít nhất 1 nhóm merge.")
        else:
            for session in st.session_state.merging_sessions:
                selected_files = session["files"]
                output_filename = session["output_filename"]

                gdfs = []

                with st.spinner(f"Processing {len(selected_files)} files..."):

                    for file in uploaded_files:
                        if file.name in selected_files:
                            # Lưu file tạm
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".geojson") as tmp:
                                tmp.write(file.getvalue())
                                tmp_path = tmp.name

                            # Đọc bằng geopandas
                            gdf = gpd.read_file(tmp_path)

                            # Thêm trường "name" vào properties của từng feature
                            base_filename = os.path.splitext(output_filename)[0]  # Loại bỏ phần mở rộng
                            gdf["name"] = base_filename

                            gdfs.append(gdf)

                            os.remove(tmp_path)

                if gdfs:
                    # Gộp tất cả lại
                    combined_gdf = gpd.GeoDataFrame(
                        pd.concat(gdfs, ignore_index=True),
                        crs=gdfs[0].crs
                    )

                    # Sửa geometry lỗi nếu có
                    combined_gdf["geometry"] = combined_gdf["geometry"].buffer(0)

                    # Union toàn bộ geometry
                    merged_geometry = unary_union(combined_gdf.geometry)

                    # Tạo GeoDataFrame mới với geometry và properties
                    merged_gdf = gpd.GeoDataFrame(
                        geometry=[merged_geometry],
                        crs=combined_gdf.crs
                    )

                    # Tạo properties cho merged geometry
                    merged_gdf["properties"] = [{"name": base_filename}]

                    # Chuyển GeoDataFrame thành GeoJSON
                    merged_geojson = json.loads(merged_gdf.to_json())

                    st.success(f"✅ Merge thành công: {output_filename}")
                    st.info(f"📊 Số vùng ban đầu: {len(combined_gdf)}")
                    st.info("🗺️ Sau merge: 1 geometry")

                    with st.expander(f"🔍 Preview {output_filename}"):
                        st.json(merged_geojson)

                    # Thêm button "Thực thu"
                    st.download_button(
                        label="⬇ Download merged region",
                        data=json.dumps(merged_geojson, indent=2),
                        file_name=output_filename,  # Tên file đầu ra
                        mime="application/json"
                    )
                else:
                    st.error("❌ Không có dữ liệu để gộp.")