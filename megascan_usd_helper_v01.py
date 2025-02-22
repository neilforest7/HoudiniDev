import os
import json
import re
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hou

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
        
        # 通过文件结构判断
        if "3dplant" in os.path.abspath(self.asset_folder):
            self.is_3d_plant = True
    
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
        print(f"找到的变体目录: {var_dirs}")
        
        if var_dirs:
            # 有变体目录的情况，使用目录式变体处理
            print(f"处理目录式变体...")
            var_dirs.sort()
            for var_dir in var_dirs:
                self._parse_variation(var_dir)
            
        else:
            # 无变体目录的情况，检查是否是打包的变体
            print(f"没有找到变体目录，检查是否存在打包变体...")
            
            # 按优先级查找主几何体文件
            main_geo = self._find_main_geometry()
            
            if main_geo:
                # 分析打包的变体
                variations = self.analyze_packed_variations(str(self.asset_folder / main_geo))
                
                if variations["num_variations"] > 1:  # 只有当检测到多个变体时才使用打包变体
                    print(f"找到打包的变体: {variations['num_variations']}个")
                    # 使用_parse_variation处理每个变体
                    for i, var_name in enumerate(variations["variation_names"]):
                        var_id = f"Var{i+1}"
                        # 创建临时变体信息供_parse_variation使用
                        temp_var_info = {
                            "is_packed": True,
                            "packed_index": i,
                            "main_geo": main_geo,
                            "tris": variations["primitive_counts"].get(var_name)
                        }
                        self._parse_variation(var_id, default_variation=True, packed_var_info=temp_var_info)
                else:
                    # 只有一个变体或没有检测到变体，使用默认变体
                    print(f"未检测到多个变体，使用默认变体Var1")
                    self._parse_variation("Var1", default_variation=True)
            else:
                # 没有找到几何体文件，使用默认变体
                print(f"没有找到几何体文件，使用默认变体Var1")
                self._parse_variation("Var1", default_variation=True)
    
    def _find_main_geometry(self) -> Optional[str]:
        """按优先级查找主几何体文件
        
        Returns:
            str: 找到的文件路径，如果没找到则返回None
        """
        # 1. 查找high模型
        for file in self.local_files:
            if (file.endswith((".fbx", ".abc")) and 
                "_LOD" not in file and 
                "_high." in file.lower()):
                return file
        
        # 2. 查找其他不带LOD的模型
        for file in self.local_files:
            if file.endswith((".fbx", ".abc")) and "LOD" not in file:
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
                tris=packed_var_info["tris"],
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
                print("\n使用models字段解析...")
                for model in self.json_data["models"]:
                    print(f"\n处理model: {model}")
                    
                    # 获取文件路径
                    if "uri" not in model or not model["uri"]:
                        print(f"没有uri字段或uri为空，跳过")
                        continue
                    
                    # 规范化路径以进行比较
                    model_uri = model["uri"]
                    print(f"规范化后的文件路径: {model_uri}")
                    
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
                    if model["type"] == "original" or model["type"] == "high" or model["type"] == "High":
                        lod_geo.lod_level = "High"  # 设置LOD级别
                        var_geo.lods["High"] = lod_geo
                        print(f"添加为High模型")
                    elif model["type"] == "lod":
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
        """分析打包在一个文件中的变体信息
        
        Args:
            geo_file: 几何体文件路径
            
        Returns:
            Dict包含:
            - num_variations: 变体数量
            - variation_names: 变体名称列表（如果可用）
            - primitive_counts: 每个变体的面数
        """
        result = {
            "num_variations": 0,
            "variation_names": [],
            "primitive_counts": {}
        }
        
        # 获取文件格式
        file_format = geo_file.split(".")[-1].lower()
        
        try:
            # 创建临时节点进行分析
            temp_obj = hou.node("/obj").createNode("geo", "temp_analysis")
            file_node = temp_obj.createNode("file")
            file_node.parm("file").set(geo_file)
            
            if file_format == "abc":
                # ABC文件直接读取
                geo = file_node.geometry()
                prims = geo.prims()
                result["num_variations"] = len(prims)
                
                # 尝试获取primitive名称作为变体名
                for i, prim in enumerate(prims):
                    name = prim.attribValue("name") if prim.attribValue("name") else f"Var{i+1}"
                    result["variation_names"].append(name)
                    result["primitive_counts"][name] = prim.intrinsicValue("vertexcount")
                    
            else:
                # FBX/OBJ等需要pack处理
                pack = file_node.createOutputNode("pack")
                pack.parm("packbyname").set(1)
                
                geo = pack.geometry()
                prims = geo.prims()
                result["num_variations"] = len(prims)
                
                # 获取packed primitive的信息
                for i, prim in enumerate(prims):
                    name = prim.attribValue("name") if prim.attribValue("name") else f"Var{i+1}"
                    result["variation_names"].append(name)
                    result["primitive_counts"][name] = prim.intrinsicValue("packedtris")
                    
        except Exception as e:
            print(f"分析几何体变体时出错: {str(e)}")
            
        finally:
            # 清理临时节点
            if "temp_obj" in locals():
                temp_obj.destroy()
                
        return result
    
    def _parse_textures(self):
        """解析纹理文件"""
        print(f"\n开始解析纹理文件...")
        self.textures = {}
        
        # 确定纹理根目录
        texture_root = "Textures/Atlas/" if self.is_3d_plant else ""
        print(f"纹理根目录: {texture_root}")
        
        # 判断JSON结构类型并获取纹理列表
        if "components" in self.json_data:
            print("使用components字段解析纹理...")
            texture_list = self.json_data["components"]
            self._parse_components_textures(texture_list, texture_root)
        elif "maps" in self.json_data:
            print("使用maps字段解析纹理...")
            texture_list = self.json_data["maps"]
            self._parse_maps_textures(texture_list, texture_root)
        else:
            print("警告: 未找到纹理信息")
            return
        
        # 打印解析结果
        print(f"\n纹理解析结果:")
        for texture_type, resolutions in self.textures.items():
            print(f"\n纹理类型: {texture_type}")
            for res_key, texture_res in resolutions.items():
                print(f"  分辨率 {res_key}:")
                for texture_file in texture_res.files:
                    print(f"    - {texture_file.path} ({texture_file.format})")
    
    def _parse_components_textures(self, components, texture_root):
        """解析components格式的纹理"""
        for comp in components:
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
        for tex_type in self.textures.values():
            texture_res.update(tex_type.keys())
        self.asset_info.texture_resolutions = ",".join(sorted(texture_res))
    
                                                                                                                                
    ######  #    #  #####    ####   #####   #####      #        ####    ####     ##    #           #  #    #  ######   ####  
    #        #  #   #    #  #    #  #    #    #        #       #    #  #    #   #  #   #           #  ##   #  #       #    # 
    #####     ##    #    #  #    #  #    #    #        #       #    #  #       #    #  #           #  # #  #  #####   #    # 
    #         ##    #####   #    #  #####     #        #       #    #  #       ######  #           #  #  # #  #       #    # 
    #        #  #   #       #    #  #   #     #        #       #    #  #    #  #    #  #           #  #   ##  #       #    # 
    ######  #    #  #        ####   #    #    #        ######   ####    ####   #    #  ######      #  #    #  #        ####  
                                                                                                                            
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