import os
import json
import re
from typing import Dict, List, Optional, Union, Tuple
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
    
    def to_dict(self):
        return asdict(self)
    
@dataclass
class TextureFile:
    path: str  # 相对路径
    format: str  # 文件格式(exr/jpg/png)
    color_space: str  # 颜色空间(Linear/sRGB)
    lod: Optional[str] = None  # LOD级别，如果有

    def to_dict(self):
        result = {
            "path": self.path,
            "format": self.format,
            "color_space": self.color_space
        }
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
    
    def __post_init__(self):
        if self.lods is None:
            self.lods = {}
    
    def to_dict(self):
        return {
            "var_id": self.var_id,
            "lods": {k: v.to_dict() for k, v in self.lods.items()}
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
        var_dirs = [d for d in os.listdir(self.asset_folder) if d.startswith("Var") and os.path.isdir(self.asset_folder / d)]
        print(f"找到的变体目录: {var_dirs}")
        
        if var_dirs:
            # 有变体目录的情况
            print(f"处理有变体目录的情况...")
            var_dirs.sort()
            for var_dir in var_dirs:
                print(f"\n处理变体目录: {var_dir}")
                self._parse_variation(var_dir)
        else:
            # 无变体目录的情况，创建默认变体
            print(f"没有找到变体目录，使用默认变体Var1")
            self._parse_variation("Var1", is_default=True)
        
        print(f"\n几何体解析结果:")
        print(f"找到的变体数量: {len(self.geometries)}")
        for var_id, var_geo in self.geometries.items():
            print(f"\n变体 {var_id}:")
            print(f"LOD数量: {len(var_geo.lods)}")
            for lod_name, lod_data in var_geo.lods.items():
                print(f"  {lod_name}:")
                if lod_data.fbx:
                    print(f"    FBX: {lod_data.fbx}")
                if lod_data.abc:
                    print(f"    ABC: {lod_data.abc}")
                if lod_data.tris:
                    print(f"    面数: {lod_data.tris}")
    
    def _parse_variation(self, var_id: str, is_default: bool = False):
        """解析单个变体的几何体"""
        print(f"\n开始解析变体: {var_id} (is_default={is_default})")
        var_geo = GeometryVariation(var_id=var_id)
        
        # 确定基础路径和资产ID
        base_path = f"{var_id}/" if not is_default else ""
        asset_id = self.json_data['id']
        print(f"基础路径: {base_path}")
        print(f"资产ID: {asset_id}")
        
        # 从JSON中获取几何体信息
        if "models" in self.json_data:
            print("\n使用models字段解析...")
            for model in self.json_data["models"]:
                print(f"\n处理model: {model}")
                
                # 检查变体匹配
                if "variations" in model:
                    if int(var_id[3:]) not in model["variations"]:
                        print(f"变体不匹配，跳过")
                        continue
                    print(f"变体匹配成功")
                
                # 获取文件路径
                if "uri" not in model or not model["uri"]:
                    print(f"没有uri字段或uri为空，跳过")
                    continue
                
                # 规范化路径以进行比较
                model_uri = model["uri"]#.replace("/", os.sep)
                print(f"规范化后的文件路径: {model_uri}")
                
                # 检查文件是否存在
                if model_uri not in self.local_files:
                    print(f"文件不存在于本地文件列表中: {model_uri}")
                    continue
                
                print(f"找到文件: {model_uri}")
                
                # 创建几何体文件
                lod_geo = GeometryFile()
                if model["mimeType"] == "application/x-fbx":
                    lod_geo.fbx = model_uri
                    print(f"设置为FBX文件")
                elif model["mimeType"] == "application/x-abc":
                    lod_geo.abc = model_uri
                    print(f"设置为ABC文件")
                lod_geo.tris = model.get("tris")
                
                # 确定LOD级别
                if model["type"] == "original":
                    var_geo.lods["High"] = lod_geo
                    print(f"添加为High模型")
                elif model["type"] == "lod":
                    lod_level = str(model["lod"])
                    var_geo.lods[f"LOD{lod_level}"] = lod_geo
                    print(f"添加为LOD{lod_level}模型")
                
        elif "meshes" in self.json_data:
            print("\n使用meshes字段解析...")
            for mesh in self.json_data["meshes"]:
                print(f"\n处理mesh: {mesh}")
                
                if mesh["type"] == "original":
                    print("处理original类型mesh")
                    for uri in mesh["uris"]:
                        if uri["uri"] in self.local_files:
                            print(f"找到文件: {uri['uri']}")
                            lod_geo = GeometryFile()
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
                        if uri["uri"] in self.local_files:
                            print(f"找到文件: {uri['uri']}")
                            lod_geo = GeometryFile()
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
                                var_geo.lods[f"LOD{lod_level}"] = lod_geo
                                print(f"添加为LOD{lod_level}模型")
        
        # 只有当变体包含几何体时才添加
        if var_geo.lods:
            print(f"\n变体 {var_id} 包含 {len(var_geo.lods)} 个LOD，添加到geometries")
            self.geometries[var_id] = var_geo
        else:
            print(f"\n变体 {var_id} 没有找到任何几何体，跳过")
    
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
                        
                        if full_path not in self.local_files:
                            # 检查Thumbs目录
                            thumb_path = f"Thumbs/{res_key}/{filename}"
                            if thumb_path not in self.local_files:
                                continue
                            full_path = thumb_path
                        
                        texture_file = TextureFile(
                            path=full_path,
                            format=filename.split(".")[-1].lower(),
                            color_space=color_space
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
            # 跳过billboard纹理
            if "Textures/Billboard" in map_info["uri"]:
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
            
            # 检查文件是否存在
            if full_path not in self.local_files:
                # 检查Thumbs目录
                thumb_path = f"Thumbs/{res_key}/{os.path.basename(map_info['uri'])}"
                if thumb_path.lower() not in [f.lower() for f in self.local_files]:
                    continue
                full_path = thumb_path
            
            # 创建纹理文件对象
            texture_file = TextureFile(
                path=full_path,
                format=map_info["mimeType"].split("/")[-1].split("-")[-1].lower(),
                color_space=color_space
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
    
    def _get_texture_location(self) -> Tuple[str, Dict[str, str]]:
        """
        确定纹理位置并获取共享纹理
        Returns:
            Tuple[str, Dict[str, str]]: (位置类型, 共享纹理映射)
            位置类型可以是: "root", "atlas", "default"
        """
        # 检查根目录纹理
        root_textures = {
            texture_type: self._get_best_texture(texture_type, "root")
            for texture_type in self.asset.textures
        }
        if any(root_textures.values()):
            return "root", root_textures
            
        # 检查Atlas目录纹理
        atlas_textures = {
            texture_type: self._get_best_texture(texture_type, "atlas")
            for texture_type in self.asset.textures
        }
        if any(atlas_textures.values()):
            return "atlas", atlas_textures
            
        # 使用默认位置纹理
        default_textures = {
            texture_type: self._get_best_texture(texture_type, "default")
            for texture_type in self.asset.textures
        }
        return "default", default_textures
    
    def _get_best_texture(self, texture_type: str, location: str) -> Optional[str]:
        """
        获取指定位置的最佳纹理
        Args:
            texture_type: 纹理类型
            location: 位置类型("root", "atlas", "default")
        """
        if texture_type not in self.asset.textures:
            return None
            
        # 获取最高分辨率
        resolutions = sorted(self.asset.textures[texture_type].keys(), reverse=True)
        if not resolutions:
            return None
            
        highest_res = resolutions[0]
        texture_files = self.asset.textures[texture_type][highest_res].files
        
        # 根据位置筛选文件
        if location == "root":
            valid_files = [f for f in texture_files 
                          if not f.path.startswith(("Textures/Atlas/", "Thumbs/"))]
        elif location == "atlas":
            valid_files = [f for f in texture_files 
                          if f.path.startswith("Textures/Atlas/")]
        else:  # default
            valid_files = texture_files
            
        return self._get_best_format(valid_files).path if valid_files else None
    
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
        location, shared_textures = self._get_texture_location()
        
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
                        
                    # 检查是否有LOD专属纹理
                    lod_texture = self._find_lod_texture(
                        texture_type, lod_level, location
                    )
                    
                    if lod_texture:
                        mapping.textures[texture_type] = lod_texture
                    else:
                        mapping.textures[texture_type] = texture_path
                
                self.mappings.append(mapping)
    
    def _find_lod_texture(self, 
                         texture_type: str, 
                         lod_level: str,
                         location: str) -> Optional[str]:
        """
        查找LOD专属纹理
        """
        if texture_type not in self.asset.textures:
            return None
            
        # 获取最高分辨率
        resolutions = sorted(self.asset.textures[texture_type].keys(), reverse=True)
        if not resolutions:
            return None
            
        highest_res = resolutions[0]
        texture_files = self.asset.textures[texture_type][highest_res].files
        
        # 根据位置筛选文件
        if location == "root":
            valid_files = [f for f in texture_files 
                          if not f.path.startswith(("Textures/Atlas/", "Thumbs/"))]
        elif location == "atlas":
            valid_files = [f for f in texture_files 
                          if f.path.startswith("Textures/Atlas/")]
        else:
            valid_files = texture_files
        
        # 查找匹配的LOD纹理
        lod_num = lod_level.replace("LOD", "") if lod_level != "High" else None
        if lod_num:
            lod_files = [f for f in valid_files if f.lod == lod_num]
            if lod_files:
                return self._get_best_format(lod_files).path
        
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

if __name__ == "__main__":
    import argparse
    import pprint
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='解析Megascan资产并生成本地资源清单')
    parser.add_argument('folder_path', type=str, help='Megascan资产文件夹的路径')
    parser.add_argument('--output', '-o', type=str, help='输出JSON文件的路径(可选)')
    parser.add_argument('--pretty', '-p', action='store_true', help='是否美化输出')
    
    args = parser.parse_args()
    
    try:
        # 创建资产对象
        asset = create_local_asset(args.folder_path)
        
        # 获取本地信息
        local_info = asset.export_local_info()
        
        # 输出信息
        if args.output:
            # 写入JSON文件
            with open(args.output, 'w', encoding='utf-8') as f:
                if args.pretty:
                    json.dump(local_info, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(local_info, f, ensure_ascii=False)
            print(f"结果已保存到: {args.output}")
        else:
            # 打印到控制台
            if args.pretty:
                pprint.pprint(local_info)
            else:
                print(json.dumps(local_info, ensure_ascii=False))
                
        # 打印一些基本统计信息
        print("\n资产统计信息:")
        print(f"资产ID: {asset.asset_info.id}")
        print(f"资产名称: {asset.asset_info.name}")
        print(f"几何体LOD数量: {len(asset.get_available_lods())}")
        print(f"可用纹理类型: {', '.join(asset.get_available_texture_types())}")
        
    except Exception as e:
        print(f"错误: {str(e)}")