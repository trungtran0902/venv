import geopandas as gpd
import pandas as pd
import os

TARGET_CRS = "EPSG:4326"

def merge_geojson_files(input_folder, output_path, export_shapefile=True):
    input_folder = input_folder.replace("\\", "/")
    output_path = output_path.replace("\\", "/")

    files = sorted([
        os.path.join(input_folder, f)
        for f in os.listdir(input_folder)
        if f.lower().endswith(".geojson")
    ])

    if not files:
        print("❌ Không tìm thấy file GeoJSON nào.")
        return

    print(f"🔹 Phát hiện {len(files)} file cần gộp...")

    gdf_list = []

    for f in files:
        try:
            print(f"📄 Đang đọc: {os.path.basename(f)}")
            gdf = gpd.read_file(f)

            # CRS
            if gdf.crs is None:
                gdf = gdf.set_crs(TARGET_CRS)
            elif gdf.crs.to_string() != TARGET_CRS:
                gdf = gdf.to_crs(TARGET_CRS)

            gdf = gdf[gdf.geometry.notnull()]
            gdf_list.append(gdf)

        except Exception as e:
            print(f"   ❌ Lỗi đọc {f}: {e}")

    if not gdf_list:
        print("❌ Không có dữ liệu hợp lệ.")
        return

    merged = gpd.GeoDataFrame(
        pd.concat(gdf_list, ignore_index=True),
        crs=TARGET_CRS
    )

    # ===== XÁC ĐỊNH OUTPUT =====
    if os.path.isdir(output_path):
        geojson_path = os.path.join(output_path, "merged.geojson")
    else:
        geojson_path = output_path

    os.makedirs(os.path.dirname(geojson_path), exist_ok=True)

    # ===== XUẤT GEOJSON =====
    merged.to_file(geojson_path, driver="GeoJSON")
    print(f"✅ Đã xuất GeoJSON: {geojson_path}")

    # ===== XUẤT SHAPEFILE =====
    if export_shapefile:
        base_name = os.path.splitext(os.path.basename(geojson_path))[0]
        shp_folder = os.path.join(
            os.path.dirname(geojson_path),
            f"{base_name}_shp"
        )
        os.makedirs(shp_folder, exist_ok=True)

        shp_path = os.path.join(shp_folder, f"{base_name}.shp")

        merged_shp = merged.copy()
        merged_shp.columns = [
            c[:10] if c != "geometry" else c
            for c in merged_shp.columns
        ]

        merged_shp.to_file(shp_path, driver="ESRI Shapefile", encoding="utf-8")
        print(f"✅ Đã xuất Shapefile: {shp_path}")

    print("\n🎉 Hoàn tất!")
    print(f"📏 Tổng số feature: {len(merged)}")


# ===== RUN =====
if __name__ == "__main__":
    folder = input("Nhập folder chứa GeoJSON: ").strip()
    output = input("Nhập THƯ MỤC đầu ra: ").strip()

    merge_geojson_files(folder, output, export_shapefile=True)
