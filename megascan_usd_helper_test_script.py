from megascan_usd_helper_v01 import create_local_asset
import json

# 创建资产对象
asset_path = r"A:/AppBase/QuixelBridge/Downloaded/3dplant/3dplant_herb_umjjbjzja"
asset = create_local_asset(asset_path)

# 获取并打印信息
info = asset.export_local_info()
print("资产信息:")
print(json.dumps(info["asset_info"], indent=2, ensure_ascii=False))

# 打印几何体信息
print("\n几何体信息:")
for var_id, var_data in info["geometries"].items():
    print(f"\n变体 {var_id}:")
    for lod_name, lod_data in var_data["lods"].items():
        print(f"  {lod_name}:")
        if lod_data["fbx"]:
            print(f"    FBX: {lod_data['fbx']}")
        if lod_data["abc"]:
            print(f"    ABC: {lod_data['abc']}")
        if lod_data["tris"]:
            print(f"    面数: {lod_data['tris']}")

# 测试各种获取方法
print("\n基本信息测试:")
print("可用的LOD级别:", asset.get_available_lods())
print("可用的纹理类型:", asset.get_available_texture_types())
print("可用的变体:", asset.get_available_variants())

# 测试获取特定纹理路径
print("\n纹理路径测试:")
for texture_type in asset.get_available_texture_types():
    for resolution in asset.get_available_resolutions(texture_type):
        path = asset.get_texture_path(
            texture_type=texture_type,
            resolution=resolution,
            format="exr"
        )
        if path:
            print(f"{texture_type} ({resolution}): {path}")

# 测试获取带LOD的法线贴图
print("\nLOD纹理测试:")
for lod in ["0", "1", "2"]:
    normal_path = asset.get_texture_path(
        texture_type="normal",
        resolution="4k",
        format="exr",
        lod=lod
    )
    if normal_path:
        print(f"Normal (LOD{lod}): {normal_path}")

# 测试纹理映射关系
print("\n纹理映射测试:")
mapping_manager = asset.export_local_info()["texture_mappings"]
print("\n所有纹理映射:")
for mapping in mapping_manager:
    print(f"\n几何体文件: {mapping['geo_file']}")
    print(f"LOD级别: {mapping['lod_level']}")
    print("关联的纹理:")
    for texture_type, texture_path in mapping['textures'].items():
        print(f"  {texture_type}: {texture_path}")

# 测试特定几何体的纹理映射
print("\n测试特定变体和LOD的纹理映射:")
test_variants = asset.get_available_variants()[:2]  # 测试前两个变体
test_lods = ["LOD0", "LOD1"]  # 测试LOD0和LOD1

for var_id in test_variants:
    for lod in test_lods:
        # 从geometries中获取对应的几何体文件路径
        geo_file = info["geometries"][var_id]["lods"].get(lod, {}).get("fbx")
        if not geo_file:
            continue
            
        print(f"\n变体 {var_id} - {lod}:")
        print(f"几何体文件: {geo_file}")
        
        # 查找对应的纹理映射
        mapping = next((m for m in mapping_manager if m["geo_file"] == geo_file), None)
        if mapping:
            print("关联的纹理:")
            for texture_type, texture_path in mapping["textures"].items():
                print(f"  {texture_type}: {texture_path}")
        else:
            print("未找到纹理映射")

# 测试纹理分辨率的完整性
# print("\n纹理分辨率完整性测试:")
# for texture_type in asset.get_available_texture_types():
#     resolutions = asset.get_available_resolutions(texture_type)
#     print(f"\n{texture_type}:")
#     print(f"可用分辨率: {resolutions}")
    
#     # 测试每个分辨率的不同格式
#     for resolution in resolutions:
#         print(f"  {resolution}:")
#         for format in ["exr", "jpg", "png"]:
#             path = asset.get_texture_path(
#                 texture_type=texture_type,
#                 resolution=resolution,
#                 format=format
#             )
#             if path:
#                 print(f"    {format}: {path}")