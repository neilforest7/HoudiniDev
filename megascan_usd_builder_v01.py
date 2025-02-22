import os
import re
import hou

from PySide2 import QtGui as gui
from PySide2 import QtCore as core
from PySide2 import QtWidgets as wdg
from typing import List
### MODEL ###
#####################################################################################################################
#                                                                                                                   #
#                                                                                                                   #
#  ##     ## ######## ##       ########  ######## ########      ######   ######  ########  #### ########  ########  #
#  ##     ## ##       ##       ##     ## ##       ##     ##    ##    ## ##    ## ##     ##  ##  ##     ##    ##     #
#  ##     ## ##       ##       ##     ## ##       ##     ##    ##       ##       ##     ##  ##  ##     ##    ##     #
#  ######### ######   ##       ########  ######   ########      ######  ##       ########   ##  ########     ##     #
#  ##     ## ##       ##       ##        ##       ##   ##            ## ##       ##   ##    ##  ##           ##     #
#  ##     ## ##       ##       ##        ##       ##    ##     ##    ## ##    ## ##    ##   ##  ##           ##     #
#  ##     ## ######## ######## ##        ######## ##     ##     ######   ######  ##     ## #### ##           ##     #
#                                                                                                                   #
#                                                                                                                   #
#####################################################################################################################

import json
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# 数据类定义
@dataclass
class AssetInfo:
    id: str
    name: str
    type: str
    local_path: str
    variations: str = ""  # 新增：存储变体信息，如 "Var1,Var2,..."
    lods: str = ""  # 如 "High,LOD0,LOD1,..."
    texture_resolutions: str = ""  # 如 "4k,2k,1k"
    preview_image: Optional[str] = None  # 预览图路径
    
    def to_dict(self):
        return asdict(self)
    
@dataclass
class GeometryFile:
    fbx: Optional[str] = None  # 相对路径
    abc: Optional[str] = None
    tris: Optional[int] = None  # 面数
    lod_level: str = ""        # 当前几何体的LOD级别
    var_id: str = ""          # 所属的变体ID
    
    def to_dict(self):
        return asdict(self)
    
@dataclass
class TextureFile:
    path: str  # 相对路径
    format: str  # 文件格式(exr/jpg/png)
    color_space: str  # 颜色空间(Linear/sRGB)
    resolution: str = ""  # 纹理分辨率（如"4k"）
    type: str = ""  # 纹理类型（如"albedo"、"normal"等）
    var_id: Optional[str] = None  # 如果是变体专属纹理，存储变体ID
    lod: Optional[str] = None  # LOD级别，如果有

    def to_dict(self):
        result = {
            "path": self.path,
            "format": self.format,
            "color_space": self.color_space,
            "resolution": self.resolution,
            "type": self.type
        }
        if self.var_id is not None:
            result["var_id"] = self.var_id
        if self.lod is not None:
            result["lod"] = self.lod
        return result

@dataclass
class TextureResolution:
    files: List[TextureFile] = None  # 存储该分辨率下的所有贴图文件
    
    def __post_init__(self):
        if self.files is None:
            self.files = []
    
    def add_file(self, file: TextureFile):
        self.files.append(file)
    
    def to_dict(self):
        return {
            "files": [f.to_dict() for f in self.files]
        }
        
@dataclass
class GeometryVariation:
    """几何体变体类"""
    var_id: str  # 变体ID，如 "Var1"
    lods: Dict[str, GeometryFile] = None  # LOD模型字典，包括High
    is_packed: bool = False  # 新增：标识是否为打包变体
    packed_index: Optional[int] = None  # 新增：如果是打包变体，存储其在文件中的索引
    
    def __post_init__(self):
        if self.lods is None:
            self.lods = {}
    
    def to_dict(self):
        return {
            "var_id": self.var_id,
            "lods": {k: v.to_dict() for k, v in self.lods.items()},
            "is_packed": self.is_packed,
            "packed_index": self.packed_index
        }

class LocalMegascanAsset:
    """本地Megascan资产管理类"""
    
    def __init__(self, asset_folder: str):
        """
        初始化本地资产
        
        Args:
            asset_folder: 资产根目录的绝对路径
        """
        self.asset_folder = Path(asset_folder)
        self.json_data = None
        self.local_files = []
        self.asset_info = None
        self.geometries = {}  # 将存储 GeometryVariation 对象
        self.textures = {}
        self.is_3d_plant = False  # 新增：标识是否为3D植物资产
        self.asset_type = "3D"  # 默认为3D类型
        
        self._load_asset()


    #        #######     #     ######              #      #####    #####   #######  ####### 
    #        #     #    # #    #     #            # #    #     #  #     #  #           #    
    #        #     #   #   #   #     #           #   #   #        #        #           #    
    #        #     #  #     #  #     #          #     #   #####    #####   #####       #    
    #        #     #  #######  #     #          #######        #        #  #           #    
    #        #     #  #     #  #     #          #     #  #     #  #     #  #           #    
    #######  #######  #     #  ######           #     #   #####    #####   #######     #    
    def _load_asset(self):
        """加载并解析资产"""
        # 1. 扫描本地文件
        self._scan_local_files()
        
        # 2. 读取json
        json_files = [f for f in self.local_files if f.endswith('.json') and not f.startswith('UAsset/')]
        if not json_files:
            raise FileNotFoundError("No megascan json file found in asset folder")
            
        json_path = self.asset_folder / json_files[0]
        with open(json_path, 'r') as f:
            self.json_data = json.load(f)
            
        # 3. 判断资产类型
        self._determine_asset_type()
        
        # 4. 解析资产信息
        self._parse_asset_info()
        
        # 5. 解析几何体文件
        self._parse_geometries()
        
        # 6. 解析纹理文件
        self._parse_textures()
        
        # 7. 更新资产信息中的概述
        self._update_asset_info()
    
    def _determine_asset_type(self):
        """判断资产类型"""
        # 通过categories判断
        category = self.json_data.get("categories", [])
        if "3dplant" in category:
            self.is_3d_plant = True
            self.asset_type = "3DPlant"
        
        # 通过文件结构判断
        if "3dplant" in os.path.abspath(self.asset_folder):
            self.is_3d_plant = True
            self.asset_type = "3DPlant"
    
    def _scan_local_files(self):
        """扫描本地文件列表"""
        for root, _, files in os.walk(self.asset_folder):
            for file in files:
                # 转换为相对路径
                rel_path = os.path.relpath(os.path.join(root, file), self.asset_folder)
                rel_path = rel_path.replace('\\', '/')
                self.local_files.append(rel_path)
        print(f"local_files: {self.local_files}")
        
    def _find_preview_image(self) -> Optional[str]:
        """查找资产预览图"""
        # 按优先级定义可能的预览图文件名模式
        preview_patterns = [
            f"{self.json_data['id']}_Preview.png",  # 标准预览图
            f"{self.json_data['id']}_preview.png",  # 小写变体
            f"{self.json_data['id']}_Thumb_HighPoly.png",  # 高模缩略图
            f"{self.json_data['id']}_Thumb_HighPoly_Retina.png"  # 高分辨率缩略图
        ]
        
        # 检查Previews目录
        previews_dir = "Previews"
        for pattern in preview_patterns:
            # 检查根目录
            if pattern in self.local_files:
                return pattern
            
            # 检查Previews目录
            preview_path = f"{previews_dir}/{pattern}"
            if preview_path in self.local_files:
                return preview_path
            
        # 如果在json中有previews信息，尝试从中查找
        if "previews" in self.json_data and "images" in self.json_data["previews"]:
            for image in self.json_data["previews"]["images"]:
                if "uri" in image and image["uri"] in self.local_files:
                    # 优先选择高分辨率的预览图
                    if "preview" in image.get("tags", []) or "retina" in image.get("tags", []):
                        return image["uri"]
                    # 其次选择缩略图
                    if "fi" in image.get("tags", []) and not image["uri"].endswith("tiny.png"):
                        return image["uri"]
        
        return None
    
    def _parse_asset_info(self):
        """解析资产基本信息"""
        self.asset_info = AssetInfo(
            id=self.json_data["id"],
            name=self.json_data["name"],
            type=self.json_data["semanticTags"]["asset_type"],
            local_path=str(self.asset_folder)
        )
        
        # 查找预览图
        preview_image = self._find_preview_image()
        if preview_image:
            self.asset_info.preview_image = preview_image
    
    def _parse_geometries(self):
        """统一解析几何体文件"""
        print(f"\n开始解析几何体文件...")
        self.geometries = {}
        
        # 1. 首先检查是否有变体目录
        var_dirs = [d for d in os.listdir(self.asset_folder) 
                    if d.startswith("Var") and os.path.isdir(self.asset_folder / d)]
        print(f"找到的模型variation目录: {var_dirs}")
        
        if len(var_dirs) > 1:
            # 有变体目录的情况，使用目录式变体处理
            print(f"处理目录式variation {len(var_dirs)} 个...")
            var_dirs.sort()
            for var_dir in var_dirs:
                self._parse_variation(var_dir)
            
        else:
            # 无变体目录的情况，说明模型在根目录，检查其是否是打包的变体
            print(f"没有找到模型variation目录，检查是否存在packed variation...")
            
            # 按优先级查找主模型，high模型，LOD0模型
            main_geo = self._find_main_geometry()
            
            if not main_geo:
                print(f"没有找到主模型，使用默认变体Var1")
                self._parse_variation("Var1", default_variation=True)
            else:
                # 分析打包的变体
                variations = self.analyze_packed_variations(str(self.asset_folder / main_geo))
                
                if variations["num_variations"] > 1:  # 只有当检测到多个变体时才使用打包变体
                    print(f"找到打包的变体: {variations['num_variations']}个")
                    # 使用_parse_variation处理每个变体
                    for i in range(variations["num_variations"]):
                        var_id = f"Var{i+1}"
                        # 创建临时变体信息供_parse_variation使用
                        temp_var_info = {
                            "is_packed": True,
                            "packed_index": i,
                            "main_geo": main_geo,
                            # "tris": variations["primitive_counts"].get(var_name)
                        }
                        self._parse_variation(var_id, default_variation=True, packed_var_info=temp_var_info)
                else:
                    # 只有一个变体或没有检测到变体，使用默认变体
                    print(f"未检测到多个变体，使用默认变体Var1")
                    self._parse_variation("Var1", default_variation=True)
    
    def _find_main_geometry(self) -> Optional[str]:
        """按优先级查找主几何体文件
        
        Returns:
            str: 找到的文件路径，如果没找到则返回None
        """
        # 1. 查找high模型
        for file in self.local_files:
            if (file.endswith((".fbx", ".abc")) and ("_LOD" not in file) and ("_high." in file.lower())):
                return file
        
        # 2. 查找其他不带LOD的模型
        for file in self.local_files:
            if (file.endswith((".fbx", ".abc")) and ("_LOD" not in file)):
                return file
        
        # 3. 查找LOD0模型
        for file in self.local_files:
            if file.endswith((".fbx", ".abc")) and "LOD0" in file:
                return file
        
        return None
    
    def _parse_variation(self, var_id: str, default_variation: bool = False, packed_var_info: Dict = None):
        """解析单个变体的几何体
        
        Args:
            var_id: 变体ID
            default_variation: 是否为默认变体
            packed_var_info: 打包变体的额外信息，包含：
                - is_packed: 是否为打包变体
                - packed_index: 在文件中的索引
                - main_geo: 主几何体文件
                - tris: 面数
        """
        print(f"\n开始解析变体: {var_id} (is_default={default_variation}, is_packed={packed_var_info is not None})")
        var_geo = GeometryVariation(var_id=var_id)
        
        if packed_var_info:
            # 处理打包变体
            var_geo.is_packed = True
            var_geo.packed_index = packed_var_info["packed_index"]
            
            # 创建几何体文件对象
            main_geo = packed_var_info["main_geo"]
            geo_file = GeometryFile(
                fbx=main_geo if main_geo.endswith(".fbx") else None,
                abc=main_geo if main_geo.endswith(".abc") else None,
                # tris=packed_var_info["tris"],
                var_id=var_id,
                lod_level="High"
            )
            var_geo.lods["High"] = geo_file
            
            base_name = main_geo.rsplit(".", 1)[0]
            if "_high" in base_name.lower():
                base_name = base_name.lower().replace("_high", "")
            
            # 查找对应的LOD文件
            for file in self.local_files:
                if not file.endswith((".fbx", ".abc")) or "_LOD" not in file:
                    continue
                    
                # 确保是同一组文件
                file_base = file.rsplit("_LOD", 1)[0]
                if file_base.lower() != base_name.lower():
                    continue
                    
                # 提取LOD级别
                lod_match = file.split("_LOD")
                if len(lod_match) > 1:
                    lod_level = f"LOD{lod_match[-1].split('.')[0]}"
                    
                    # 创建几何体文件
                    lod_geo = GeometryFile(
                        fbx=file if file.endswith(".fbx") else None,
                        abc=file if file.endswith(".abc") else None,
                        var_id=var_geo.var_id,
                        lod_level=lod_level
                    )
                    
                    # 添加到变体
                    var_geo.lods[lod_level] = lod_geo
                    print(f"为变体 {var_geo.var_id} 添加 {lod_level} 模型: {file}")
            
        else:
            # 原有的目录式变体处理逻辑
            # 确定基础路径和资产ID
            base_path = f"{var_id}/" if not default_variation else ""
            asset_id = self.json_data['id']
            print(f"基础路径: {base_path}")
            print(f"资产ID: {asset_id}")
            
            # 从JSON中获取几何体信息
            if "models" in self.json_data:
                print("使用models字段解析...")
                for model in self.json_data["models"]:
                    # print(f"\n处理model: {model}")
                    
                    # 获取文件路径
                    if "uri" not in model or not model["uri"]:
                        print(f"没有uri字段或uri为空，跳过")
                        continue
                    
                    # 规范化路径以进行比较
                    model_uri = model["uri"]
                    
                    # 检查文件是否存在且属于当前变体
                    if not model_uri.startswith(base_path) and not default_variation:
                        print(f"文件不属于当前变体目录，跳过: {model_uri}")
                        continue
                    
                    if model_uri not in self.local_files:
                        print(f"文件不存在于本地文件列表中: {model_uri}")
                        continue
                    
                    print(f"找到文件: {model_uri}")
                    
                    # 创建几何体文件
                    lod_geo = GeometryFile()
                    lod_geo.var_id = var_id  # 设置变体ID
                    
                    if model["mimeType"] == "application/x-fbx":
                        lod_geo.fbx = model_uri
                        print(f"设置为FBX文件")
                    elif model["mimeType"] == "application/x-abc":
                        lod_geo.abc = model_uri
                        print(f"设置为ABC文件")
                    lod_geo.tris = model.get("tris")
                    
                    # 确定LOD级别
                    if model["type"] in ["original", "high", "High"]:
                        lod_geo.lod_level = "High"  # 设置LOD级别
                        var_geo.lods["High"] = lod_geo
                        print(f"添加为High模型")
                    elif model["type"] in ["lod", "LOD"]:
                        lod_level = str(model["lod"])
                        lod_geo.lod_level = f"LOD{lod_level}"  # 设置LOD级别
                        var_geo.lods[f"LOD{lod_level}"] = lod_geo
                        print(f"添加为LOD{lod_level}模型")
            
            elif "meshes" in self.json_data:
                print("\n使用meshes字段解析...")
                for mesh in self.json_data["meshes"]:
                    print(f"\n处理mesh: {mesh}")
                    
                    if mesh["type"] == "original":
                        print("处理original类型mesh")
                        for uri in mesh["uris"]:
                            # 检查文件是否属于当前变体
                            if not uri["uri"].startswith(base_path) and not default_variation:
                                print(f"文件不属于当前变体目录，跳过: {uri['uri']}")
                                continue
                                
                            if uri["uri"] in self.local_files:
                                print(f"找到文件: {uri['uri']}")
                                lod_geo = GeometryFile()
                                lod_geo.var_id = var_id  # 设置变体ID
                                lod_geo.lod_level = "High"  # 设置LOD级别
                                
                                if uri["mimeType"] == "application/x-fbx":
                                    lod_geo.fbx = uri["uri"]
                                    print(f"设置为FBX文件")
                                elif uri["mimeType"] == "application/x-abc":
                                    lod_geo.abc = uri["uri"]
                                    print(f"设置为ABC文件")
                                lod_geo.tris = mesh.get("tris")
                                var_geo.lods["High"] = lod_geo
                                print(f"添加为High模型")
                                break
                    elif mesh["type"] == "lod":
                        print("处理lod类型mesh")
                        for uri in mesh["uris"]:
                            # 检查文件是否属于当前变体
                            if not uri["uri"].startswith(base_path) and not default_variation:
                                print(f"文件不属于当前变体目录，跳过: {uri['uri']}")
                                continue
                                
                            if uri["uri"] in self.local_files:
                                print(f"找到文件: {uri['uri']}")
                                lod_geo = GeometryFile()
                                lod_geo.var_id = var_id  # 设置变体ID
                                
                                if uri["mimeType"] == "application/x-fbx":
                                    lod_geo.fbx = uri["uri"]
                                    print(f"设置为FBX文件")
                                elif uri["mimeType"] == "application/x-abc":
                                    lod_geo.abc = uri["uri"]
                                    print(f"设置为ABC文件")
                                lod_geo.tris = mesh.get("tris")
                                
                                # 从文件名提取LOD级别
                                lod_match = uri["uri"].split("_LOD")
                                if len(lod_match) > 1:
                                    lod_level = lod_match[-1].split(".")[0]
                                    lod_geo.lod_level = f"LOD{lod_level}"  # 设置LOD级别
                                    var_geo.lods[f"LOD{lod_level}"] = lod_geo
                                    print(f"添加为LOD{lod_level}模型")
        
        # 只有当变体包含几何体时才添加
        if var_geo.lods:
            print(f"\n变体 {var_id} 包含 {len(var_geo.lods)} 个LOD，添加到geometries")
            self.geometries[var_id] = var_geo
        else:
            print(f"\n变体 {var_id} 没有找到任何几何体，跳过")
    
    def analyze_packed_variations(self, geo_file: str) -> Dict[str, Any]:
        """分析打包在一个文件中的变体信息"""
        print(f"\n开始分析打包变体: {geo_file}")
        result = {
            "num_variations": 0,
            "variation_names": [],
            "primitive_counts": {}
        }
        # 获取文件格式
        file_format = geo_file.split(".")[-1].lower()
        print(f"文件格式: {file_format}")
        
        # 创建临时节点
        print("\n创建临时分析节点...")
        node = hou.pwd()
        print(f"当前节点: {node.path()}")
        megascanSubnet = node.node("megascans_variants")
        temp_sopcreate = megascanSubnet.createNode("sopcreate", "temp_analysis")
        create = temp_sopcreate.node("sopnet").node("create")
        print(f"创建临时geo节点: {create.path()}")
        
        file_node = create.createNode("file")
        print(f"创建file节点: {file_node.path()}")
        file_node.parm("file").set(geo_file)
        print(f"设置文件路径: {geo_file}")

        try:
            if file_format == "abc":
                print("\n处理ABC文件...")
                try:
                    geo = file_node.geometry()
                    print(f"获取几何体成功")
                    prims = geo.prims()
                    print(f"获取primitives成功，数量: {len(prims)}")
                    result["num_variations"] = len(prims)
                    
                    # 获取primitive信息
                    # print("\n分析primitive信息:")
                    # for i, prim in enumerate(prims):
                    #     try:
                    #         name = prim.attribValue("name") if prim.attribValue("name") else f"Var{i+1}"
                    #         vert_count = prim.intrinsicValue("vertexcount")
                    #         print(f"  Primitive {i}: name={name}, vertex_count={vert_count}")
                    #         result["variation_names"].append(name)
                    #         result["primitive_counts"][name] = vert_count
                    #     except Exception as e:
                    #         print(f"  处理primitive {i}时出错: {str(e)}")
                    
                except Exception as e:
                    print(f"处理ABC几何体时出错: {str(e)}")
                    
            else:
                print("\n处理FBX/OBJ文件...")
                try:
                    # 创建pack节点
                    pack = file_node.createOutputNode("pack")
                    print(f"创建pack节点: {pack.path()}")
                    pack.parm("packbyname").set(1)
                    
                    geo = pack.geometry()
                    print(f"获取packed几何体成功")
                    prims = geo.prims()
                    print(f"获取packed primitives成功，数量: {len(prims)}")
                    result["num_variations"] = len(prims)
                    
                    # 获取packed primitive信息
                    # print("\n分析packed primitive信息:")
                    # for i, prim in enumerate(prims):
                    #     try:
                    #         name = prim.attribValue("name") if prim.attribValue("name") else f"Var{i+1}"
                    #         tris_count = prim.intrinsicValue("packedtris")
                    #         print(f"  Primitive {i}: name={name}, tris_count={tris_count}")
                    #         result["variation_names"].append(name)
                    #         result["primitive_counts"][name] = tris_count
                    #     except Exception as e:
                    #         print(f"  处理packed primitive {i}时出错: {str(e)}")
                        
                except Exception as e:
                    print(f"处理FBX/OBJ几何体时出错: {str(e)}")
                    
        except Exception as e:
            print(f"分析几何体变体时出错: {str(e)}")
            print(f"错误类型: {type(e)}")
            import traceback
            print(f"错误堆栈:\n{traceback.format_exc()}")
            
        finally:
            # 清理临时节点
            try:
                if "temp_analysis" in locals():
                    print(f"\n清理临时节点: {temp_sopcreate.path()}")
                    temp_sopcreate.destroy()
            except Exception as e:
                print(f"清理临时节点时出错: {str(e)}")
        
        print(f"\n分析结果:")
        print(f"变体数量: {result['num_variations']}")
        print(f"变体名称: {result['variation_names']}")
        print(f"面数统计: {result['primitive_counts']}")
        
        return result
    
    def _parse_textures(self):
        """解析纹理文件"""
        print(f"\n开始解析纹理文件...")
        self.textures = {}
        
        # 确定纹理根目录
        texture_root = "Textures/Atlas/" if self.is_3d_plant else ""
        
        # 根据JSON结构选择解析方法
        if "components" in self.json_data:
            print("使用components格式解析纹理...")
            self._parse_components_textures(self.json_data["components"], texture_root)
        elif "maps" in self.json_data:
            print("使用maps格式解析纹理...")
            self._parse_maps_textures(self.json_data["maps"], texture_root)
        else:
            print("警告：JSON中没有找到components或maps字段")
    
    def _parse_components_textures(self, components, texture_root):
        """解析components格式的纹理"""
        for comp in components:
            # 从组件名称中提取纹理类型
            texture_type = comp["name"].lower()
            color_space = comp.get("colorSpace", "Linear")
            
            for uri in comp.get("uris", []):
                for resolution in uri.get("resolutions", []):
                    # 解析分辨率 (8192x8192 -> 8k)
                    res = resolution["resolution"].split("x")[0]
                    res_key = f"{res[0]}k" if len(res) == 4 else f"{res[0:2]}k"
                    
                    texture_res = TextureResolution()
                    has_files = False
                    
                    for fmt in resolution["formats"]:
                        filename = fmt["uri"]
                        full_path = os.path.join(texture_root, filename)
                        
                        # 只处理存在于本地且不在Thumbs目录的文件
                        if full_path in self.local_files and not full_path.startswith("Thumbs/"):
                            # 检查是否为变体专属纹理
                            var_id = None
                            var_match = re.search(r'Var(\d+)', filename)
                            if var_match:
                                var_id = f"Var{var_match.group(1)}"
                            
                            # 创建纹理文件对象
                            texture_file = TextureFile(
                                path=full_path,
                                format=filename.split(".")[-1].lower(),
                                color_space=color_space,
                                resolution=res_key,
                                type=texture_type,
                                var_id=var_id
                            )
                            
                            # 处理LOD贴图
                            if "lodType" in fmt:
                                lod_match = filename.split("_LOD")
                                if len(lod_match) > 1:
                                    texture_file.lod = lod_match[-1].split(".")[0]
                            
                            texture_res.add_file(texture_file)
                            has_files = True
                            print(f"添加纹理: {texture_type} ({res_key}): {full_path}")
                    
                    # 只有当有实际文件时才添加该分辨率
                    if has_files:
                        if texture_type not in self.textures:
                            self.textures[texture_type] = {}
                        self.textures[texture_type][res_key] = texture_res
    
    def _parse_maps_textures(self, maps, texture_root):
        """解析maps格式的纹理"""
        for map_info in maps:
            # 跳过billboard纹理和Thumbs目录的纹理
            if "Textures/Billboard" in map_info["uri"] or "Thumbs/" in map_info["uri"]:
                continue
            
            texture_type = map_info["name"].lower()
            color_space = map_info.get("colorSpace", "Linear")
            
            # 从uri中提取分辨率信息
            resolution_match = re.search(r'(\d+)K', map_info["uri"])
            if not resolution_match:
                continue
            
            res_key = resolution_match.group(0).lower()  # 例如: "4k"
            
            # 获取或创建该纹理类型的字典
            if texture_type not in self.textures:
                self.textures[texture_type] = {}
            
            # 获取或创建该分辨率的TextureResolution对象
            if res_key not in self.textures[texture_type]:
                self.textures[texture_type][res_key] = TextureResolution()
            
            # 直接使用uri作为路径，因为它已经包含了相对路径
            full_path = map_info["uri"]
            print(f"检查文件路径: {full_path}")
            
            # 只处理存在于本地且不在Thumbs目录的文件
            if full_path in self.local_files and not full_path.startswith("Thumbs/"):
                # 创建纹理文件对象
                # 检查是否为变体专属纹理
                var_id = None
                var_match = re.search(r'Var(\d+)', full_path)
                if var_match:
                    var_id = f"Var{var_match.group(1)}"
                
                texture_file = TextureFile(
                    path=full_path,
                    format=map_info["mimeType"].split("/")[-1].split("-")[-1].lower(),
                    color_space=color_space,
                    resolution=res_key,
                    type=texture_type,
                    var_id=var_id
                )
                
                # 处理LOD贴图
                if "lod" in map_info and map_info["lod"] != -1:
                    texture_file.lod = str(map_info["lod"])
                
                # 添加到对应的TextureResolution对象
                self.textures[texture_type][res_key].add_file(texture_file)
                print(f"添加纹理: {texture_type} ({res_key}): {full_path}")
    
    def _update_asset_info(self):
        """更新资产信息中的几何体和纹理概述"""
        # 收集变体信息
        self.asset_info.variations = ",".join(sorted(self.geometries.keys()))
        
        # 收集LOD信息（包括High）
        lods = set()
        for var_geo in self.geometries.values():
            lods.update(var_geo.lods.keys())
        
        # 确保LOD按精度排序（High > LOD0 > LOD1 > ...）
        def lod_sort_key(lod):
            if lod == "High":
                return -1
            return int(lod.replace("LOD", ""))
        
        # 设置LOD信息
        self.asset_info.lods = ",".join(sorted(list(lods), key=lod_sort_key))
        
        # 收集纹理分辨率
        texture_res = set()
        for tex_type, resolutions in self.textures.items():
            # 跳过预览和缩略图相关的纹理类型
            if tex_type.lower() in ['preview', 'thumb', 'thumbnail']:
                continue
                
            for res, res_data in resolutions.items():
                # 检查是否有非缩略图/预览图的文件
                valid_files = [f for f in res_data.files if not f.path.startswith(("Thumbs/", "Previews/"))]
                if valid_files:
                    texture_res.add(res)
                    
        # 按从高到低排序后设置
        self.asset_info.texture_resolutions = ",".join(sorted(list(texture_res), key=lambda x: int(x.replace('k', '')), reverse=True))

    def export_local_info(self) -> Dict:
        """导出本地资产信息"""
        mapping_manager = TextureMappingManager(self)
        return {
            "asset_info": self.asset_info.to_dict(),
            "geometries": {
                var_id: var_geo.to_dict()
                for var_id, var_geo in self.geometries.items()
            },
            "textures": {
                texture_type: {
                    res: res_data.to_dict()
                    for res, res_data in resolutions.items()
                }
                for texture_type, resolutions in self.textures.items()
            },
            "texture_mappings": mapping_manager.export_mappings()
        }
    
    def get_available_lods(self) -> List[str]:
        """获取可用的LOD级别"""
        lods = set()
        for var_geo in self.geometries.values():
            lods.update(var_geo.lods.keys())
        return sorted(list(lods))
    
    def get_available_texture_types(self) -> List[str]:
        """获取可用的纹理类型"""
        return list(self.textures.keys())
    
    def get_available_resolutions(self, texture_type: str) -> List[str]:
        """获取指定纹理类型的可用分辨率"""
        if texture_type in self.textures:
            return list(self.textures[texture_type].keys())
        return []
    
    def get_available_variants(self) -> List[str]:
        """获取可用的变体"""
        return list(self.geometries.keys())
    
    def get_texture_path(self, 
                        texture_type: str, 
                        resolution: str, 
                        format: str = "exr",
                        lod: Optional[str] = None) -> Optional[str]:
        """
        获取指定条件的纹理路径
        
        Args:
            texture_type: 纹理类型(albedo, normal等)
            resolution: 分辨率(1k, 2k等)
            format: 文件格式(exr或jpg或png)
            lod: LOD级别(可选)
            
        Returns:
            纹理文件的相对路径,如果不存在返回None
        """
        try:
            if texture_type not in self.textures:
                return None
            
            if resolution not in self.textures[texture_type]:
                return None
            
            texture_res = self.textures[texture_type][resolution]
            
            # 根据条件筛选文件
            for texture_file in texture_res.files:
                if texture_file.format.lower() != format.lower():
                    continue
                
                if lod is not None:
                    if texture_file.lod != lod:
                        continue
                elif texture_file.lod is not None:
                    continue
                
                return texture_file.path
                
            return None
        except Exception:
            return None

@dataclass
class TextureMapping:
    """纹理映射类，用于存储几何体和纹理的匹配关系"""
    geo_file: str  # 几何体文件名
    lod_level: Optional[str]  # LOD级别 (High, 0, 1, 2...)
    textures: Dict[str, str] = None  # 纹理类型到文件路径的映射
    
    def __post_init__(self):
        if self.textures is None:
            self.textures = {}
    
    def to_dict(self):
        return {
            "geo_file": self.geo_file,
            "lod_level": self.lod_level,
            "textures": self.textures
        }

class TextureMappingManager:
    """纹理映射管理器，负责创建和管理几何体与纹理的映射关系"""
    
    def __init__(self, asset: LocalMegascanAsset):
        self.asset = asset
        self.mappings: List[TextureMapping] = []
        self._create_mappings()
    
    def _get_best_texture(self) -> Tuple[str, Dict[str, str]]:
        """
        获取最佳纹理并确定它们的位置
        Returns:
            Tuple[str, Dict[str, str]]: (位置类型, 共享纹理映射)
            位置类型可以是: "root", "atlas", "default"
        """
        print(f"\n开始获取最佳纹理...")
        
        # 定义要检查的位置顺序
        locations = ["root", "atlas", "default"]
        
        for location in locations:
            print(f"\n检查{location}目录纹理...")
            textures = {}
            
            for texture_type in self.asset.textures:
                # 获取所有分辨率并按从高到低排序
                resolutions = sorted(self.asset.textures[texture_type].keys(), reverse=True)
                if not resolutions:
                    print(f"纹理类型 {texture_type} 没有可用分辨率")
                    continue
                    
                # 遍历所有分辨率，直到找到有效的纹理文件
                for res in resolutions:
                    print(f"尝试分辨率: {res}")
                    texture_files = self.asset.textures[texture_type][res].files
                    if not texture_files:
                        print(f"分辨率 {res} 没有可用文件")
                        continue
                        
                    # 根据位置筛选文件
                    print(f"筛选前的纹理文件: {[f.path for f in texture_files]}")
                    if location == "root":
                        valid_files = [f for f in texture_files 
                                    if not f.path.startswith(("Textures/Atlas/", "Thumbs/"))]
                    elif location == "atlas":
                        valid_files = [f for f in texture_files 
                                    if f.path.startswith("Textures/Atlas/")]
                    else:  # default
                        valid_files = texture_files
                    
                    print(f"筛选后的纹理文件: {[f.path for f in valid_files]}")
                    
                    # 如果找到有效文件，返回最佳格式的文件
                    if valid_files:
                        best_file = self._get_best_format(valid_files)
                        if best_file:
                            print(f"找到最佳纹理: {best_file.path}")
                            textures[texture_type] = best_file.path
                            break  # 找到该类型的纹理后跳出分辨率循环
            
            # 如果在当前位置找到了任何纹理，就返回结果
            if textures:
                print(f"在{location}目录找到纹理，使用此位置")
                return location, textures
        
        # 如果所有位置都没有找到纹理，返回默认位置和空字典
        print(f"所有位置都没有找到纹理，使用默认位置")
        return "default", {}
    
    def _has_variant_textures(self, shared_textures: Dict[str, str]) -> bool:
        """
        通过检查纹理文件名判断是否存在变体专属纹理
        """
        for texture_path in shared_textures.values():
            if texture_path:
                # 检查文件名中是否包含变体标识（如Var1, Var2等）
                filename = os.path.basename(texture_path)
                if re.search(r'Var\d+', filename):
                    return True
        return False
    
    def _create_mappings(self):
        """创建所有几何体的纹理映射"""
        # 1. 确定纹理位置并获取共享纹理
        location, shared_textures = self._get_best_texture()
        
        # 2. 检查是否有变体
        has_variants = len(self.asset.geometries) > 1
        has_variant_textures = self._has_variant_textures(shared_textures)
        
        # 3. 创建纹理映射
        for var_id, var_geo in self.asset.geometries.items():
            for lod_level, geo in var_geo.lods.items():
                if not (geo.fbx or geo.abc):
                    continue
                    
                # 创建基础映射
                mapping = TextureMapping(
                    geo_file=geo.fbx or geo.abc,
                    lod_level=lod_level
                )
                
                # 处理纹理映射
                for texture_type, texture_path in shared_textures.items():
                    if not texture_path:
                        continue
                        
                    # 尝试获取纹理，按优先级：变体专属 -> LOD专属 -> 共享纹理
                    final_texture = None
                    
                    # 1. 如果有变体专属纹理，尝试获取
                    if has_variants and has_variant_textures:
                        final_texture = self._find_variant_texture(
                            texture_type, var_id, location
                        )
                    
                    # 2. 如果没有变体专属纹理，尝试获取LOD专属纹理
                    if not final_texture:
                        final_texture = self._find_lod_texture(
                            texture_type, lod_level, location
                        )
                    
                    # 3. 如果都没有，使用共享纹理
                    if not final_texture:
                        final_texture = texture_path
                    
                    # 设置最终选择的纹理
                    if final_texture:
                        mapping.textures[texture_type] = final_texture
                
                self.mappings.append(mapping)
    
    def _find_lod_texture(self, texture_type: str, lod_level: str, location: str) -> Optional[str]:
        """
        查找LOD专属纹理，如果找不到对应级别的纹理，尝试使用最接近的较低LOD级别的纹理
        """
        if texture_type not in self.asset.textures:
            return None
        
        # 获取所有分辨率并按从高到低排序
        resolutions = sorted(self.asset.textures[texture_type].keys(), reverse=True)
        if not resolutions:
            return None
            
        # 遍历所有分辨率，直到找到对应LOD级别的纹理
        for res in resolutions:
            texture_files = self.asset.textures[texture_type][res].files
            valid_files = texture_files
            
            # 如果是High级别，使用不带LOD的纹理
            if lod_level == "High":
                non_lod_files = [f for f in valid_files if f.lod is None]
                if non_lod_files:
                    return self._get_best_format(non_lod_files).path
                continue
            
            # 获取当前LOD编号
            current_lod = int(lod_level.replace("LOD", ""))
            
            # 1. 首先尝试查找完全匹配的LOD级别
            lod_files = [f for f in valid_files if f.lod == str(current_lod)]
            if lod_files:
                return self._get_best_format(lod_files).path
            
            # 2. 如果没有找到完全匹配的，查找最接近的较低LOD级别
            available_lods = sorted([int(f.lod) for f in valid_files if f.lod is not None], reverse=True)
            closest_lod = None
            for lod in available_lods:
                if lod < current_lod:
                    closest_lod = str(lod)
                    break
                
            if closest_lod is not None:
                lod_files = [f for f in valid_files if f.lod == closest_lod]
                if lod_files:
                    print(f"使用LOD{closest_lod}纹理替代LOD{current_lod}")
                    return self._get_best_format(lod_files).path
            
            # 3. 如果没有找到任何较低LOD级别的纹理，使用不带LOD的纹理
            non_lod_files = [f for f in valid_files if f.lod is None]
            if non_lod_files:
                # print(f"使用无LOD纹理替代LOD{current_lod}")
                return self._get_best_format(non_lod_files).path
        
        return None
    
    def _get_best_format(self, available_files: List[TextureFile]) -> Optional[TextureFile]:
        """根据优先级选择最佳格式的纹理文件"""
        format_priority = ["exr", "png", "jpg"]
        for fmt in format_priority:
            for file in available_files:
                if file.format == fmt:
                    return file
        return available_files[0] if available_files else None
    
    def get_mapping_for_geo(self, geo_file: str) -> Optional[TextureMapping]:
        """获取指定几何体的纹理映射"""
        for mapping in self.mappings:
            if mapping.geo_file == geo_file:
                return mapping
        return None
    
    def export_mappings(self) -> List[Dict]:
        """导出所有映射关系"""
        return [mapping.to_dict() for mapping in self.mappings]

def create_local_asset(asset_folder: str) -> LocalMegascanAsset:
    """
    创建本地资产对象的工厂函数
    
    Args:
        asset_folder: 资产根目录的绝对路径
        
    Returns:
        LocalMegascanAsset对象
    """
    return LocalMegascanAsset(asset_folder)

################################################################################################################################
#                                                                                                                              #
#                                                                                                                              #
#   #######  ########  ####  ######   #### ##    ##    ###    ##           ######   ######  ########  #### ########  ########  #
#  ##     ## ##     ##  ##  ##    ##   ##  ###   ##   ## ##   ##          ##    ## ##    ## ##     ##  ##  ##     ##    ##     #
#  ##     ## ##     ##  ##  ##         ##  ####  ##  ##   ##  ##          ##       ##       ##     ##  ##  ##     ##    ##     #
#  ##     ## ########   ##  ##   ####  ##  ## ## ## ##     ## ##           ######  ##       ########   ##  ########     ##     #
#  ##     ## ##   ##    ##  ##    ##   ##  ##  #### ######### ##                ## ##       ##   ##    ##  ##           ##     #
#  ##     ## ##    ##   ##  ##    ##   ##  ##   ### ##     ## ##          ##    ## ##    ## ##    ##   ##  ##           ##     #
#   #######  ##     ## ####  ######   #### ##    ## ##     ## ########     ######   ######  ##     ## #### ##           ##     #
#                                                                                                                              #
#                                                                                                                              #
################################################################################################################################
## CREATE GEO FUNCTIONS ##    
########  ##     ## #### ##       ########      ######   ########  ####### 
##     ## ##     ##  ##  ##       ##     ##    ##    ##  ##       ##     ##
##     ## ##     ##  ##  ##       ##     ##    ##        ##       ##     ##
########  ##     ##  ##  ##       ##     ##    ##   #### ######   ##     ##
##     ## ##     ##  ##  ##       ##     ##    ##    ##  ##       ##     ##
##     ## ##     ##  ##  ##       ##     ##    ##    ##  ##       ##     ##
########   #######  #### ######## ########      ######   ########  ####### 
#Build geo function    
def buildGeo(node, asset_manager: LocalMegascanAsset, hasProxy: bool):
    """构建几何体"""
    # 获取megascansSubnet节点并清理
    megascansSubnet = node.node("megascans_variants")
    for child in megascansSubnet.children():
        child.destroy()
    
    # 创建变体控制节点
    addvariant = megascansSubnet.createNode("addvariant")
    addvariant.parm("primpath").set("/`chs(\"../name\")`")
    addvariant.parm("variantset").set("geo")
    
    configurePrim = addvariant.createOutputNode("configureprimitive")
    configurePrim.parm("setkind").set(1)
    configurePrim.parm("kind").set("component")
    
    setvariant = configurePrim.createOutputNode("setvariant")
    setvariant.parm("primpattern1").set("`chs(\"../name\")`")
    setvariant.parm("variantset1").set("geo")
    setvariant.parm("variantname1").set("VAR_1")
    
    output  = setvariant.createOutputNode("output")
    output.setDisplayFlag(True)
    # 处理每个变体
    createGeoVar(asset_manager, hasProxy, megascansSubnet, addvariant)

    
    megascansSubnet.layoutChildren()

def createGeoVar(asset_manager, hasProxy, megascansSubnet, addvariant):
    print("\n开始创建几何体变体...")
    print(f"几何体数据: {asset_manager.geometries}")
    
    for var_index, (var_id, var_data) in enumerate(asset_manager.geometries.items()):
        print(f"\n处理变体 {var_id}:")
        print(f"变体数据: {var_data.to_dict()}")
        print(f"LODs: {var_data.lods}")
        
        # 创建几何体节点
        geoVar = megascansSubnet.createNode("sopcreate", f"geo_var_{var_index}")
        geoVarCreate = geoVar.node("sopnet").node("create")
        if not geoVarCreate:
            print(f"错误：无法在 {geoVar.path()} 中找到geoVarCreate节点")
            continue
            
        nullGeo = megascansSubnet.createNode("null","IN_GEO_"+str(var_index))
        nullGeo.setInput(0,geoVar)
        
        #Create proxy var
        proxyVar = megascansSubnet.createNode("sopcreate","proxy_var_"+str(var_index))
        proxyVarCreate = proxyVar.node("sopnet").node("create")
        
        nullProxy = megascansSubnet.createNode("null","IN_PROXY_"+str(var_index))
        nullProxy.setInput(0,proxyVar)
        
        #Create switch proxy
        switchProxy = megascansSubnet.createNode("switch","switch_hasProxy")
        switchProxy.parm("input").setExpression("ch(\"../../hasProxy\")")
        nullEmpty = megascansSubnet.createNode("null","EMPTY")
        switchProxy.setInput(0,nullEmpty)
        switchProxy.setInput(1,nullProxy)
        
        merge = megascansSubnet.createNode("merge")
        merge.setInput(0,nullGeo)
        merge.setInput(1,switchProxy)
        
        nullVar = megascansSubnet.createNode("null","VAR_"+str(var_index+1))
        nullVar.setInput(0,merge)
        
        # 连接到addvariant
        addvariant.setInput(var_index+1, nullVar)
        
        # 获取主要几何体
        print(f"查找High LOD或LOD0几何体...")
        main_geo = var_data.lods.get("High")
        if not main_geo:
            print(f"未找到High LOD，尝试使用LOD0...")
            main_geo = var_data.lods.get("LOD0")
            if not main_geo:
                print(f"错误：在变体 {var_id} 中既没有High LOD也没有LOD0")
                print(f"可用的LOD级别: {list(var_data.lods.keys())}")
                continue
            print(f"使用LOD0作为主要几何体")
            
        geo_path = main_geo.fbx # if asset_manager.is_3d_plant else main_geo.abc
        if not geo_path:
            print(f"错误：无法在 {geoVar.path()} 中找到geo_path")
            continue
            
        # 创建几何体节点
        file = geoVarCreate.createNode("file")
        file.parm("file").set(str(asset_manager.asset_folder / geo_path))
        if not file:
            print(f"错误：无法在 {geoVar.path()} 中创建file节点")
            continue
        

        # 如果是打包变体，添加blast节点
        if var_data.is_packed:
            if not asset_manager.is_3d_plant:
                pack = file.createOutputNode("pack")
                pack.parm("packbyname").set(1)
                blast = pack.createOutputNode("blast")
            else:
                blast = file.createOutputNode("blast")
                
            blast.parm("group").set(str(var_data.packed_index))
            blast.parm("negate").set(1)
            last_node = blast
        else:
            last_node = file
            
        # 添加transform节点
        transform = last_node.createOutputNode("xform")
        transform.parm("scale").set(0.01)
        
        convert = transform.createOutputNode("convert")
        
        # 处理normalize
        matchsize = convert.createOutputNode("matchsize")
        if asset_manager.asset_type == "3DPlant":
            matchsize.parm("justify_y").set(1)
        matchsize.parm("sizex").set(2)
        matchsize.parm("sizey").set(2)
        matchsize.parm("sizez").set(2)
        matchsize.parm("doscale").set(1)
        
        # 创建normalize开关
        switchNormalize = geoVarCreate.createNode("switch", "switch_isNormalize")
        switchNormalize.setInput(0, convert)
        switchNormalize.setInput(1, matchsize)
        switchNormalize.parm("input").setExpression("ch(\"../../../../../normalize\")")
        
        # 设置路径
        wranglePath = geoVarCreate.createNode("attribwrangle", "setPath")
        if hasProxy:
            snippet_path = "s@path=chs(\"../../../../../proxyPrimPath\");"
        else:
            snippet_path = "s@path=chs(\"../../../../../geoPrimPath\");"
        wranglePath.parm("snippet").set(snippet_path)
        wranglePath.parm("class").set(1)
        wranglePath.setInput(0, switchNormalize)
        
        # 清理属性
        attribdelete = geoVarCreate.createNode("attribdelete")
        attribdelete.parm("negate").set(1)
        attribdelete.parm("ptdel").set("N P uv Cd")
        attribdelete.parm("vtxdel").set("uv N Cd")
        attribdelete.parm("primdel").set("path")
        attribdelete.setInput(0, wranglePath)
        
        groupdelete = geoVarCreate.createNode("groupdelete")
        groupdelete.parm("group1").set("*")
        groupdelete.setInput(0, attribdelete)
        
        outNull = groupdelete.createOutputNode("null", "OUT")
        outNull.setDisplayFlag(True)
        outNull.setRenderFlag(True)
        
        geoVarCreate.layoutChildren()
## END CREATE GEO FUNCTIONS ##

########  ##     ## #### ##       ########     ##     ##    ###    ########
##     ## ##     ##  ##  ##       ##     ##    ###   ###   ## ##      ##   
##     ## ##     ##  ##  ##       ##     ##    #### ####  ##   ##     ##   
########  ##     ##  ##  ##       ##     ##    ## ### ## ##     ##    ##   
##     ## ##     ##  ##  ##       ##     ##    ##     ## #########    ##   
##     ## ##     ##  ##  ##       ##     ##    ##     ## ##     ##    ##   
########   #######  #### ######## ########     ##     ## ##     ##    ##   
#Build material function
def buildMaterial(node, asset_manager: LocalMegascanAsset, assetDir, res, textFormat, hasProxy, plug_all_maps: bool):
    """构建材质"""
    # 获取materiallibrary1节点并删除所有内部节点
    materiallibrary = node.node("materiallibrary1")
    child_nodes = materiallibrary.children()
    for n in child_nodes:
        n.destroy()
        
    # 创建MaterialX subnet
    mtlx_subnet, mtlxstandard_surface, mtlxdisplacement = createMaterialXSubnet(materiallibrary)
    
    # 构建纹理路径
    texturesDir = os.path.join(assetDir, "Textures", "Atlas") if asset_manager.is_3d_plant else assetDir
    
    # 从asset_manager获取可用的纹理类型
    texturetypeNames = list(asset_manager.textures.keys())
    
    # 使用默认的High LOD获取纹理
    texturesDict = getTexturesDict(asset_manager, texturetypeNames, texturesDir, res, textFormat)
    
    # 获取assign material节点
    assignmaterial = node.node("material_assign").node("assignmaterial1")
    
    # 分配材质
    assignmaterial.parm("nummaterials").set(1)
    assignmaterial.parm("primpattern1").set("/`chs(\"../../CONTROL/name\")`"+"`chs(\"../../geoPrimPath\")`")
    assignmaterial.parm("matspecpath1").set("/`chs(\"../../CONTROL/name\")`/materials/mtlxmaterial_VAR_1")
    
    if hasProxy:
        assignmaterial.parm("nummaterials").set(2)
        assignmaterial.parm("primpattern2").set("/`chs(\"../../CONTROL/name\")`"+"`chs(\"../../proxyPrimPath\")`")
        assignmaterial.parm("matspecpath2").set("/`chs(\"../../CONTROL/name\")`/materials/mtlxmaterial_VAR_1")
    
    # 应用纹理
    applyTextures(mtlx_subnet, mtlxstandard_surface, mtlxdisplacement, texturesDict, texturesDir, plug_all_maps)
    
    # 更新映射信息
    mapping_info = format_mapping_info(asset_manager, texturesDict)
    try:
        mapping_label = node.parm("mapping_info_label")
        if mapping_label:
            mapping_label.set(mapping_info)
            print("\n更新映射信息标签成功")
    except Exception as e:
        print(f"\n更新映射信息标签失败: {str(e)}")

    return texturesDict
## END CREATE MATERIAL FUNCTIONS ##

# Create MaterialX subnet
def createMaterialXSubnet(parent):
    
    # Code for /stage/PB_asset_builder_usd1/materiallibrary1/mtlxmaterial
    mtlx_subnet = parent.createNode("subnet", "mtlxmaterial_VAR_1")
    mtlx_subnet_children = mtlx_subnet.children()
    for n in mtlx_subnet_children:
        n.destroy()
    mtlx_subnet.setMaterialFlag(True)
    
    # Create MaterialX Builder parameters
    hou_parm_template_group = hou.ParmTemplateGroup()
    # Code for parameter template
    hou_parm_template = hou.FolderParmTemplate("folder1", "MaterialX Builder", folder_type=hou.folderType.Collapsible, default_value=0, ends_tab_group=False)
    hou_parm_template.setTags({"group_type": "collapsible", "sidefx::shader_isparm": "0"})
    # Code for parameter template
    hou_parm_template2 = hou.IntParmTemplate("inherit_ctrl", "Inherit from Class", 1, default_value=([2]), min=0, max=10, min_is_strict=False, max_is_strict=False, look=hou.parmLook.Regular, naming_scheme=hou.parmNamingScheme.Base1, menu_items=(["0","1","2"]), menu_labels=(["Never","Always","Material Flag"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal, menu_use_token=False)
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_referencetype", "Class Arc", 1, default_value=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm(\'inherit_ctrl\')\nr = \'none\'\nif i == 1 or (n_hasFlag and i == 2):\n    r = \'inherit\'\nreturn r"]), default_expression=(["n = hou.pwd()\nn_hasFlag = n.isMaterialFlagSet()\ni = n.evalParm(\'inherit_ctrl\')\nr = \'none\'\nif i == 1 or (n_hasFlag and i == 2):\n    r = \'inherit\'\nreturn r"]), default_expression_language=([hou.scriptLanguage.Python]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=(["none","reference","inherit","specialize","represent"]), menu_labels=(["None","Reference","Inherit","Specialize","Represent"]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_baseprimpath", "Class Prim Path", 1, default_value=(["/__class_mtl__/`$OS`"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"script_action": "import loputils\nloputils.selectPrimsInParm(kwargs, False)", "script_action_help": "Select a primitive in the Scene Viewer or Scene Graph Tree pane.\nCtrl-click to select using the primitive picker dialog.", "script_action_icon": "BUTTONS_reselect", "sidefx::shader_isparm": "0", "sidefx::usdpathtype": "prim", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.SeparatorParmTemplate("separator1")
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("tabmenumask", "Tab Menu Mask", 1, default_value=(["karma USD ^mtlxramp* ^hmtlxramp* ^hmtlxcubicramp* MaterialX parameter constant collect null genericshader subnet subnetconnector suboutput subinput"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"spare_category": "Tab Menu"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.StringParmTemplate("shader_rendercontextname", "Render Context Name", 1, default_value=(["mtlx"]), naming_scheme=hou.parmNamingScheme.Base1, string_type=hou.stringParmType.Regular, menu_items=([]), menu_labels=([]), icon_names=([]), item_generator_script="", item_generator_script_language=hou.scriptLanguage.Python, menu_type=hou.menuType.Normal)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    # Code for parameter template
    hou_parm_template2 = hou.ToggleParmTemplate("shader_forcechildren", "Force Translation of Children", default_value=True)
    hou_parm_template2.setTags({"sidefx::shader_isparm": "0", "spare_category": "Shader"})
    hou_parm_template.addParmTemplate(hou_parm_template2)
    hou_parm_template_group.append(hou_parm_template)
    mtlx_subnet.setParmTemplateGroup(hou_parm_template_group)
    
    # Create standard surface node, inputs and outputs
    inputs = mtlx_subnet.createNode("subinput", "inputs")
    output = mtlx_subnet.createNode("subnetconnector", "surface_output")
    output.parm("connectorkind").set(1)
    output.parm("parmname").set("surface")
    output.parm("parmlabel").set("Surface")
    output.parm("parmtype").set("surface")
    
    mtlxstandard_surface = mtlx_subnet.createNode("mtlxstandard_surface","mtlxstandard_surface")
    output.setInput(0,mtlxstandard_surface)
    
    displacementOutput = mtlx_subnet.createNode("subnetconnector", "displacement_output")
    displacementOutput.parm("connectorkind").set(1)
    displacementOutput.parm("parmname").set("displacement")
    displacementOutput.parm("parmlabel").set("Displacement")
    displacementOutput.parm("parmtype").set("displacement")
    
    mtlxdisplacement = mtlx_subnet.createNode("mtlxdisplacement","mtlxdisplacement")
    displacementOutput.setInput(0,mtlxdisplacement)
    
    mtlx_subnet.layoutChildren()
    
    return mtlx_subnet, mtlxstandard_surface, mtlxdisplacement

#Return a dict with the texture name and the texture path
def getTexturesDict(asset_manager, texturetypeNames, texturesDir, res, textFormat, lod="High"):
    """获取纹理字典
    
    Args:
        asset_manager: LocalMegascanAsset实例
        texturetypeNames: 纹理类型列表
        texturesDir: 纹理目录
        res: 分辨率 (如 "2K", "4K")
        textFormat: 纹理格式 (如 "exr", "png")
        lod: LOD级别，默认为"High"
    """
    print(f"\n开始构建纹理字典...")
    print(f"输入参数: \n- 纹理类型: {texturetypeNames}\n- 目录: {texturesDir}\n- 分辨率: {res}\n- 格式: {textFormat}\n- LOD: {lod}")
    
    texturesDict = {}
    
    # 遍历每个纹理类型
    for texture_type in texturetypeNames:
        print(f"\n处理纹理类型: {texture_type}")
        
        # 检查纹理类型是否存在
        if texture_type not in asset_manager.textures:
            print(f"纹理类型 {texture_type} 不存在")
            texturesDict[texture_type] = ""
            continue
            
        # 检查分辨率是否可用
        res_key = res.lower()
        if res_key not in asset_manager.textures[texture_type]:
            print(f"分辨率 {res_key} 不可用于 {texture_type}")
            texturesDict[texture_type] = ""
            continue
            
        # 获取该分辨率下的所有纹理文件
        texture_files = asset_manager.textures[texture_type][res_key].files
        
        # 根据条件筛选文件
        valid_files = [f for f in texture_files 
                        if f.format.lower() == textFormat.lower() and 
                        not f.path.startswith("Thumbs/")]
        
        if not valid_files:
            print(f"没有找到符合条件的{texture_type}纹理")
            texturesDict[texture_type] = ""
            continue
            
        # 选择最合适的文件
        selected_file = None
        
        # 对于normal/displacement/albedo/basecolor的特殊处理
        if texture_type in ["normal", "displacement", "albedo", "basecolor"]:
            print(f"对{texture_type}进行特殊处理: lod = {lod} valid_files = {valid_files}")
            if lod == "High" or lod == "orig" or lod == "original":
                # 1. 优先使用lod = high的纹理
                high_lod_files = [f for f in valid_files if f.lod and f.lod.lower() == "high"]
                if high_lod_files:
                    selected_file = high_lod_files[0]
                    print(f"找到high LOD纹理: {selected_file.path}")
                else:
                    # 2. 其次使用没有high或lod后缀的纹理
                    non_lod_files = [f for f in valid_files if f.lod is None]
                    if non_lod_files:
                        selected_file = non_lod_files[0]
                        print(f"找到无LOD后缀纹理: {selected_file.path}")
                    else:
                        # 3. 再其次使用lod0
                        lod0_files = [f for f in valid_files if f.lod == "0"]
                        if lod0_files:
                            selected_file = lod0_files[0]
                            print(f"找到LOD0纹理: {selected_file.path}")
                        else:
                            # 4. 最后选择第一个有效lod
                            if valid_files:
                                selected_file = valid_files[0]
                                print(f"使用第一个有效纹理: {selected_file.path}")
                            else:
                                selected_file = None
                                print(f"没有找到任何有效纹理")
            else:
                # 如果不是高模，使用对应LOD的文件
                lod_files = [f for f in valid_files if f.lod == lod.replace("LOD", "")]
                if lod_files:
                    selected_file = lod_files[0]
                    print(f"找到对应LOD {lod}的纹理: {selected_file.path}")
                else:
                    selected_file = None
                    print(f"没有找到LOD {lod}的纹理")
        else:
            # 其他类型直接使用第一个有效文件
            selected_file = valid_files[0] if valid_files else None
        
        if selected_file:
            texturesDict[texture_type] = os.path.basename(selected_file.path)
            print(f"选择纹理: {texturesDict[texture_type]}")
        else:
            texturesDict[texture_type] = ""
            print(f"未找到合适的{texture_type}纹理")
    
    print(f"\n最终纹理字典: {texturesDict}")
    return texturesDict
    
def getMinMaxPixelValue(path):

    node = hou.node("/obj").createNode("geo")
    grid = node.createNode("grid")
    grid.parm("rows").set(512)
    grid.parm("cols").set(512)
    
    attribfrommap = grid.createOutputNode("attribfrommap")
    attribfrommap.parm("filename").set(path)
    
    attribwrangle = attribfrommap.createOutputNode("attribwrangle")
    attribwrangle.parm("snippet").set("f@value = v@Cd.x;")
    
    attribpromote1 = attribwrangle.createOutputNode("attribpromote","min")
    attribpromote1.parm("inname").set("value")
    attribpromote1.parm("outclass").set(0)
    attribpromote1.parm("method").set(1)
    attribpromote1.parm("useoutname").set(1)
    attribpromote1.parm("outname").set("min")
    attribpromote1.parm("deletein").set(0)
    
    attribpromote2 = attribpromote1.createOutputNode("attribpromote","max")
    attribpromote2.parm("inname").set("value")
    attribpromote2.parm("outclass").set(0)
    attribpromote2.parm("method").set(0)
    attribpromote2.parm("useoutname").set(1)
    attribpromote2.parm("outname").set("max")
    attribpromote2.parm("deletein").set(0)
    
    geo = attribpromote2.geometry()
    min = geo.floatAttribValue("min") 
    max = geo.floatAttribValue("max") 
    
    node.destroy()
    
    return min, max
    
#Apply textures function
def applyTextures(mtlx_subnet, mtlxstandard_surface, mtlxdisplacement, texturesDict, texturesDir, plug_all_maps: bool):
    """应用纹理到MaterialX节点"""
    print("\n开始应用纹理...")
    print(f"纹理字典内容: {texturesDict}")
    print(f"纹理目录: {texturesDir}")

    print("\n创建基础节点...")
    mtlxmultiply = mtlx_subnet.createNode("mtlxmultiply")
    print(f"创建mtlxmultiply节点: {mtlxmultiply.path()}")
    mtlxstandard_surface.setInput(1, mtlxmultiply)
    print("将mtlxmultiply连接到mtlxstandard_surface的basecolor输入端口(1)")
    
    mtlxnormalmap = mtlx_subnet.createNode("mtlxnormalmap")
    print(f"创建mtlxnormalmap节点: {mtlxnormalmap.path()}")
    mtlxstandard_surface.setInput(40, mtlxnormalmap)
    print("将mtlxnormalmap连接到mtlxstandard_surface的normal输入端口(40)")

    print("\n开始处理每个纹理...")
    for td in texturesDict:  # td是小写的纹理类型
        print(f"\n处理纹理类型: {td}")
        if texturesDict[td] != "" and plug_all_maps:
            print(f"找到纹理文件: {texturesDict[td]}")
            image = mtlx_subnet.createNode("mtlximage", td)
            path = texturesDir+"/"+texturesDict[td]
            print(f"设置纹理路径: {path}")
            image.parm("file").set(path)
            
            if td == "albedo":
                print("处理albedo纹理:")
                mtlxmultiply.setInput(0, image)
                print("- 连接到mtlxmultiply的第一个输入端口")
                
            if td == "metalness":
                print("处理metalness纹理:")
                mtlxstandard_surface.setInput(3, image)
                print("- 连接到mtlxstandard_surface的metalness输入端口(3)")
                image.parm("signature").set("float")
                print("- 设置signature为float")
                
            if td == "glossiness":
                print("处理glossiness纹理:")
                mtlxstandard_surface.setInput(5, image)
                print("- 连接到mtlxstandard_surface的glossiness输入端口(5)")
                image.parm("signature").set("float")
                print("- 设置signature为float")
                
            if td == "ao":
                print("处理ao纹理:")
                mtlxmultiply.setInput(1, image)
                print("- 连接到mtlxmultiply的第二个输入端口")
                image.parm("signature").set("float")
                print("- 设置signature为float")
                
            if td == "normal":
                print("处理normal纹理:")
                mtlxnormalmap.setInput(0, image)
                print("- 连接到mtlxnormalmap的输入端口")
                image.parm("signature").set("vector3")
                print("- 设置signature为vector3")
                
            if td == "specular":
                print("处理specular纹理:")
                mtlxstandard_surface.setInput(4, image)
                print("- 连接到mtlxstandard_surface的specular输入端口(4)")
                image.parm("signature").set("float")
                print("- 设置signature为float")
                
            if td == "roughness":
                print("处理roughness纹理:")
                mtlxstandard_surface.setInput(6, image)
                print("- 连接到mtlxstandard_surface的roughness输入端口(6)")
                image.parm("signature").set("float")
                print("- 设置signature为float")
                
            if td == "displacement":
                print("处理displacement纹理:")
                print("- 开始计算位移贴图的最小最大值...")
                min, max = getMinMaxPixelValue(path)
                print(f"- 位移值范围: min={min}, max={max}")
                
                mtlxrange = image.createOutputNode("mtlxrange")
                print(f"- 创建mtlxrange节点: {mtlxrange.path()}")
                mtlxrange.parm("inlow").set(0)
                mtlxrange.parm("inhigh").set(1)
                mtlxrange.parm("outlow").set(-.5)
                mtlxrange.parm("outhigh").set(.5)
                print("- 设置range参数: inlow=0, inhigh=1, outlow=-0.5, outhigh=0.5")
                
                mtlxdisplacement.setInput(0, mtlxrange)
                print("- 连接到mtlxdisplacement节点")
                mtlxdisplacement.parm("scale").set(0.01)
                print("- 设置displacement scale为0.01")
                image.parm("signature").set("float")
                print("- 设置signature为float")
                
            if td == "opacity":
                print("处理opacity纹理:")
                mtlxstandard_surface.setInput(38, image)
                print("- 连接到mtlxstandard_surface的opacity输入端口(38)")
                image.parm("signature").set("float")
                print("- 设置signature为float")
                
            if td == "transmission":
                print("处理transmission纹理:")
                mtlxstandard_surface.setInput(11, image)
                print("- 连接到mtlxstandard_surface的transmission输入端口(11)")
                
            if td == "translucency":
                print("处理translucency纹理:")
                mtlxstandard_surface.setInput(18, image)
                print("- 连接到mtlxstandard_surface的subsurface输入端口(18)")
                mtlxstandard_surface.setInput(17, image)
                print("- 连接到mtlxstandard_surface的subsurface color输入端口(17)")
        elif plug_all_maps == 0:
            print("plug all map is disabled")
        else:
            print(f"纹理类型 {td} 没有对应的文件")
                            
    print("\n布局MaterialX子网络中的节点...")
    mtlx_subnet.layoutChildren()
    print("纹理应用完成")



### VIEW ###
################################################################################################
#                                                                                              #
#                                                                                              #
#  ##     ##    ###    #### ##    ##    ########  ####    ###    ##        #######   ######    #
#  ###   ###   ## ##    ##  ###   ##    ##     ##  ##    ## ##   ##       ##     ## ##    ##   #
#  #### ####  ##   ##   ##  ####  ##    ##     ##  ##   ##   ##  ##       ##     ## ##         #
#  ## ### ## ##     ##  ##  ## ## ##    ##     ##  ##  ##     ## ##       ##     ## ##   ####  #
#  ##     ## #########  ##  ##  ####    ##     ##  ##  ######### ##       ##     ## ##    ##   #
#  ##     ## ##     ##  ##  ##   ###    ##     ##  ##  ##     ## ##       ##     ## ##    ##   #
#  ##     ## ##     ## #### ##    ##    ########  #### ##     ## ########  #######   ######    #
#                                                                                              #
#                                                                                              #
################################################################################################
# Global reference to the MainDialog instance
dialogWindow = None

class MainDialog(wdg.QDialog):
    def __init__(self, node, asset_manager: LocalMegascanAsset):
        super(MainDialog, self).__init__()
        
        # 存储核心引用
        self.node = node
        self.asset_manager = asset_manager
        
        # 从asset_manager获取UI所需信息
        self.hasProxy = node.parm("hasProxy").eval()
        
        self.plug_all_maps: bool = node.parm("plug_all_maps").eval()
        
        # 获取可用选项
        available_resolutions = self._get_available_resolutions()
        available_texture_formats = self._get_available_texture_formats()
        
        # 设置窗口
        self.setWindowTitle("Megascans Asset Builder")
        self.setFixedSize(core.QSize(700,325))
        
        # 创建UI
        self._create_ui(available_resolutions, available_texture_formats)
    
    def _get_available_resolutions(self) -> List[str]:
        """获取可用的纹理分辨率，直接使用asset_info中的信息"""
        # 如果asset_info中已经有分辨率信息，直接使用
        if self.asset_manager.asset_info and self.asset_manager.asset_info.texture_resolutions:
            return self.asset_manager.asset_info.texture_resolutions.split(",")
        
        # 如果没有(这种情况不应该发生，因为_load_asset时已经调用了_update_asset_info)
        # 作为后备方案，返回空列表
        print("警告：asset_info中没有找到纹理分辨率信息")
        return []
    
    def _get_available_texture_formats(self) -> List[str]:
        """获取可用的纹理格式"""
        formats = set()
        for tex_type in self.asset_manager.textures.values():
            for res in tex_type.values():
                for tex_file in res.files:
                    formats.add(tex_file.format)
        return sorted(list(formats))

    def _create_ui(self, available_resolutions, available_texture_formats):
        # Create main Layout
        mainLay = wdg.QVBoxLayout()
        
        # Create QFormLayout
        formLay = wdg.QFormLayout()
        mainLay.addLayout(formLay)
        
        # 只保留纹理相关的选项
        # Create Texture Res Combo Box        
        self.textRes_combo_box = wdg.QComboBox()
        self.textRes_combo_box.addItems(available_resolutions)
        self.textRes_combo_box.setFixedSize(250,30)
        formLay.addRow(self.tr("&纹理分辨率: "), self.textRes_combo_box)
        
        # Create Texture Format Combo Box
        self.textFormat_combo_box = wdg.QComboBox()
        self.textFormat_combo_box.addItems(available_texture_formats)
        self.textFormat_combo_box.setFixedSize(250,30)
        formLay.addRow(self.tr("&纹理格式: "), self.textFormat_combo_box)
        
        # Create buttons layout
        buttonsLay = wdg.QHBoxLayout()
        mainLay.addLayout(buttonsLay)
        
        buildAllButton = wdg.QPushButton("构建全部")
        buildAllButton.clicked.connect(self.viewBuildAll)
        buttonsLay.addWidget(buildAllButton)
        
        buildGeoButton = wdg.QPushButton("构建几何体")
        buildGeoButton.clicked.connect(self.viewBuildGeo)
        buttonsLay.addWidget(buildGeoButton)
        
        buildMaterialButton = wdg.QPushButton("构建材质")
        buildMaterialButton.clicked.connect(self.viewBuildMaterial)
        buttonsLay.addWidget(buildMaterialButton)
        
        cancelButton = wdg.QPushButton("取消")
        cancelButton.clicked.connect(self.reject)
        buttonsLay.addWidget(cancelButton)
        
        buttonsLay.setAlignment(core.Qt.AlignCenter)
        
        
        # Set main layout
        self.setLayout(mainLay)
        self.show()
        
        
    def viewBuildAll(self):
        # 获取纹理相关选项
        res = self.textRes_combo_box.currentText()
        textFormat = self.textFormat_combo_box.currentText()
        
        # 使用asset_manager的属性
        node = self.node
        asset_manager = self.asset_manager
        assetDir = str(asset_manager.asset_folder)
        hasProxy = self.hasProxy
        plug_all_maps = self.plug_all_maps
        
        # 构建纹理路径和获取texturesDict
        # texturesDir = os.path.join(assetDir, "Textures", "Atlas") if asset_manager.is_3d_plant else assetDir
        # textureNames = list(asset_manager.textures.keys())
        
        # 调用构建函数
        buildGeo(node, asset_manager, hasProxy)
        texturesDict  = buildMaterial(node, asset_manager, assetDir, res, textFormat, hasProxy, plug_all_maps)
        
        # 更新映射信息
        try:
            mapping_info = format_mapping_info(asset_manager, texturesDict)
            mapping_label = node.parm("mapping_info_label")
            if mapping_label:
                mapping_label.set(mapping_info)
            if node.parm("name").eval() == "assetName" or not node.parm("name").eval():
                dir = assetDir.split('/')[-1].split('\\')[-1]
                if not dir[0].isdigit():
                    node.parm("name").set(f"{dir}")
                else:
                    node.parm("name").set(f"{dir.split('_')[-1]}")
        except Exception as e:
            print(f"更新映射信息标签失败: {str(e)}")
        
        self.accept()
        message = "Megascan资产构建成功。"
        hou.ui.displayMessage(message)

    def viewBuildGeo(self):
        # 使用asset_manager的属性
        node = self.node
        asset_manager = self.asset_manager
        hasProxy = self.hasProxy
        
        # 调用buildGeo时不再传递lod和format参数
        buildGeo(node, asset_manager, hasProxy)
        self.accept()
        message = "Megascan几何体构建成功。"
        hou.ui.displayMessage(message)
        
        
    def viewBuildMaterial(self):
        res = self.textRes_combo_box.currentText()
        textFormat = self.textFormat_combo_box.currentText()
        node = self.node
        asset_manager = self.asset_manager
        assetDir = str(asset_manager.asset_folder)
        hasProxy = self.hasProxy
        plug_all_maps = self.plug_all_maps
        
        buildMaterial(node, asset_manager, assetDir, res, textFormat, hasProxy, plug_all_maps)
        self.accept()
        message = "Megascan材质构建成功。"
        hou.ui.displayMessage(message)


#Main button function, check errors and create dialog
def createBuildDialog():
    # 获取节点参数
    node = hou.pwd()
    asset_folder = node.parm("asset_folder").eval()
    
    # 检查错误
    if not os.path.isdir(asset_folder):
        hou.ui.displayMessage("Error: Asset folder does not exist.", 
                            severity=hou.severityType.Error)
        return
        
    try:
        # 创建资产管理器
        asset_manager = LocalMegascanAsset(asset_folder)
        
        # 创建对话框
        global dialogWindow
        if dialogWindow is None or not dialogWindow.isVisible():
            dialogWindow = MainDialog(node, asset_manager)
            
    except Exception as e:
        hou.ui.displayMessage(f"Error: {str(e)}", 
                            severity=hou.severityType.Error)
        return

#Main button function, check errors and create dialog
def clear():
    #Get node parameters
    node = hou.pwd() 
    geo_subnet = node.node("megascans_variants")
    mat_library = node.node("materiallibrary1")
    mat_assign = node.node("material_assign")
    mapping_label = node.parm("mapping_info_label")
    
    if mapping_label:
        mapping_label.set("")
    
    geo_childs = geo_subnet.children()
    for n in geo_childs:
        n.destroy()
        
    mat_childs = mat_library.children()
    for n in mat_childs:
        n.destroy()
        
    assignmaterial = mat_assign.node("assignmaterial1")
    assignmaterial.parm("nummaterials").set(0)
    mat_assign_childs = mat_assign.children()
    
    variantblock_end =   mat_assign.node("variantblock_end1")
    inputs = variantblock_end.inputs()
    
    while len(inputs) > 2:
        variantblock_end.setInput(2,None)
        inputs = variantblock_end.inputs()
    
    nodeList = ["variantblock_begin1","assignmaterial1","VAR_1","variantblock_end1","setvariant1","output0"]
    for n in mat_assign_childs:
        if n.name() not in nodeList:
            n.destroy()
            
    message = "Megascans Asset was successfully cleared."
    hou.ui.displayMessage(message)
    
def format_mapping_info(asset_manager: LocalMegascanAsset, texturesDict: dict) -> str:
    """生成格式化的映射信息
    
    Args:
        asset_manager: 资产管理器实例
        texturesDict: 纹理字典
    
    Returns:
        str: 格式化的映射信息文本
    """
    info_lines = []
    
    # 添加标题
    info_lines.append("=== 资产映射信息 ===\n")
    
    # 几何体信息
    info_lines.append("【几何体信息】")
    for var_id, var_data in asset_manager.geometries.items():
        info_lines.append(f"\n变体 {var_id}:")
        for lod_name, lod_data in var_data.lods.items():
            geo_file = lod_data.fbx or lod_data.abc
            if geo_file:
                info_lines.append(f"  - {lod_name}: {geo_file}")
                if var_data.is_packed:
                    info_lines.append(f"    (打包变体索引: {var_data.packed_index})")
    
    # 纹理信息
    info_lines.append("\n\n【纹理信息】")
    used_textures = {k: v for k, v in texturesDict.items() if v}  # 只显示有效的纹理
    if used_textures:
        for tex_type, tex_file in used_textures.items():
            info_lines.append(f"\n{tex_type}:")
            info_lines.append(f"  - {tex_file}")
    else:
        info_lines.append("\n(无有效纹理)")
    
    return "\n".join(info_lines)