from megascan_usd_helper_v01 import create_local_asset
import json

# 创建资产对象
asset_path = r"A:/AppBase/QuixelBridge/Downloaded/3dplant/houseplant_flowering_vgztealha"
asset = create_local_asset(asset_path)

# 获取并打印信息
info = asset.export_local_info()
print("资产信息:")
# print(json.dumps(info["asset_info"], indent=2, ensure_ascii=False))
print(json.dumps(info, indent=2, ensure_ascii=False))

# # 打印几何体信息
# print("\n几何体信息:")
# for var_id, var_data in info["geometries"].items():
#     print(f"\n变体 {var_id}:")
#     for lod_name, lod_data in var_data["lods"].items():
#         print(f"  {lod_name}:")
#         if lod_data["fbx"]:
#             print(f"    FBX: {lod_data['fbx']}")
#         if lod_data["abc"]:
#             print(f"    ABC: {lod_data['abc']}")
#         if lod_data["tris"]:
#             print(f"    面数: {lod_data['tris']}")

# # 测试各种获取方法
# print("\n基本信息测试:")
# print("可用的LOD级别:", asset.get_available_lods())
# print("可用的纹理类型:", asset.get_available_texture_types())
# print("可用的变体:", asset.get_available_variants())

# # 测试纹理位置和类型
# print("\n纹理位置和类型测试:")
# mapping_manager = asset.export_local_info()["texture_mappings"]
# location_types = {"root": [], "atlas": [], "default": []}
# for mapping in mapping_manager:
#     for texture_type, texture_path in mapping["textures"].items():
#         if texture_path.startswith("Textures/Atlas/"):
#             location_types["atlas"].append(texture_type)
#         elif texture_path.startswith("Thumbs/"):
#             location_types["default"].append(texture_type)
#         else:
#             location_types["root"].append(texture_type)

# for location, types in location_types.items():
#     if types:
#         print(f"{location}目录的纹理类型: {list(set(types))}")

# # 测试变体纹理
# print("\n变体纹理测试:")
# has_variant_textures = False
# for mapping in mapping_manager:
#     for texture_type, texture_path in mapping["textures"].items():
#         if "Var" in texture_path:
#             has_variant_textures = True
#             print(f"找到变体专属纹理: {texture_path}")
#             break
#     if has_variant_textures:
#         break

# if not has_variant_textures:
#     print("未找到变体专属纹理，所有变体共享同一套纹理")

# # 测试LOD专属纹理
# print("\nLOD专属纹理测试:")
# for mapping in mapping_manager:
#     if mapping["lod_level"] and mapping["textures"]:
#         for texture_type, texture_path in mapping["textures"].items():
#             if f"LOD{mapping['lod_level']}" in texture_path:
#                 print(f"找到LOD专属纹理: {texture_path} (用于 {mapping['geo_file']})")

# # 测试纹理映射完整性
# print("\n纹理映射完整性测试:")
# for mapping in mapping_manager:
#     print(f"\n几何体文件: {mapping['geo_file']}")
#     print(f"LOD级别: {mapping['lod_level']}")
    
#     # 检查是否所有纹理类型都有映射
#     missing_types = set(asset.get_available_texture_types()) - set(mapping["textures"].keys())
#     if missing_types:
#         print(f"警告: 缺少纹理类型: {missing_types}")
    
#     print("纹理映射:")
#     for texture_type, texture_path in mapping["textures"].items():
#         print(f"  {texture_type}: {texture_path}")

# # 测试特定变体和LOD的纹理映射
# print("\n测试特定变体和LOD的纹理映射:")
# test_variants = asset.get_available_variants()[:2]  # 测试前两个变体
# test_lods = ["LOD0", "LOD1"]  # 测试LOD0和LOD1

# for var_id in test_variants:
#     for lod in test_lods:
#         # 从geometries中获取对应的几何体文件路径
#         geo_file = info["geometries"][var_id]["lods"].get(lod, {}).get("fbx")
#         if not geo_file:
#             continue
            
#         print(f"\n变体 {var_id} - {lod}:")
#         print(f"几何体文件: {geo_file}")
        
#         # 查找对应的纹理映射
#         mapping = next((m for m in mapping_manager if m["geo_file"] == geo_file), None)
#         if mapping:
#             print("关联的纹理:")
#             for texture_type, texture_path in mapping["textures"].items():
#                 print(f"  {texture_type}: {texture_path}")
#         else:
#             print("未找到纹理映射")