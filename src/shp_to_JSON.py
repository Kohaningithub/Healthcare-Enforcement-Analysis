import geopandas as gpd
import json
import os

# 设置输入和输出路径
BASE_DIR = "/Users/kohanchen/Documents/Fall 2024/data315-au24/demos/animation-activity/start/public"
OUTPUT_DIR = "/Users/kohanchen/Documents/Fall 2024/data315-au24/demos/animation-activity/start/public"

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    # 转换州级数据
    state_path = os.path.join(BASE_DIR, "cb_2018_us_state_500k/cb_2018_us_state_500k.shp")
    print(f"Reading state shapefile from: {state_path}")
    state_shp = gpd.read_file(state_path)
    
    # 直接转换为 GeoJSON 字符串
    state_json = state_shp.to_json()
    
    # 写入文件
    state_output = os.path.join(OUTPUT_DIR, "us-states.json")
    with open(state_output, 'w') as f:
        f.write(state_json)
    print(f"Successfully saved states GeoJSON to: {state_output}")

    # 转换地区数据
    district_path = os.path.join(BASE_DIR, "US Attorney Districts Shapefile simplified_20241109/geo_export_d2278870-82b8-41a4-820b-fad368168f29.shp")
    print(f"Reading district shapefile from: {district_path}")
    district_shp = gpd.read_file(district_path)
    
    # 直接转换为 GeoJSON 字符串
    district_json = district_shp.to_json()
    
    # 写入文件
    district_output = os.path.join(OUTPUT_DIR, "us-districts.json")
    with open(district_output, 'w') as f:
        f.write(district_json)
    print(f"Successfully saved districts GeoJSON to: {district_output}")

except Exception as e:
    print(f"Error occurred: {str(e)}")