import hou
import os
import hdefereval

def copy_scripts_and_ui(source_def, target_node):
    """
    复制HDA的所有脚本和UI设置到目标节点
    
    Args:
        source_def (hou.HDADefinition): 源HDA定义
        target_node (hou.Node): 目标Subnet节点
    """
    # 获取所有脚本部分
    sections = {
        "PythonModule": "PythonModule",
        "OnCreated": "OnCreated",
        "OnLoaded": "OnLoaded",
        "OnUpdated": "OnUpdated",
        "OnDeleted": "OnDeleted",
        "OnInputChanged": "OnInputChanged",
        "OnNameChanged": "OnNameChanged",
        "ExtraFileOptions": "ExtraFileOptions"
    }
    
    # 复制所有脚本内容
    for section_name, section_key in sections.items():
        try:
            script_content = source_def.sections().get(section_key, "")
            if script_content:
                target_node.type().setDefaultScript(section_name, script_content)
        except:
            continue

def copy_ui_components(source_def, target_node):
    """
    复制HDA的UI组件设置到目标节点
    
    Args:
        source_def (hou.HDADefinition): 源HDA定义
        target_node (hou.Node): 目标Subnet节点
    """
    # 获取源HDA的参数模板组
    source_parm_template_group = source_def.parmTemplateGroup()
    
    # 创建新的参数模板组
    new_parm_template_group = hou.ParmTemplateGroup()
    
    # 复制所有参数模板
    for parm_template in source_parm_template_group.entries():
        new_parm_template_group.append(parm_template)
    
    # 应用参数模板组到目标节点
    target_node.setParmTemplateGroup(new_parm_template_group)
    
    # 复制参数值
    for parm in target_node.parms():
        try:
            source_parm = source_def.nodeType().parmDefault(parm.name())
            parm.set(source_parm)
        except:
            continue

def copy_node_properties(source_node, target_node):
    """
    安全地复制节点属性
    
    Args:
        source_node (hou.Node): 源节点
        target_node (hou.Node): 目标节点
    """
    # 复制名称
    try:
        target_node.setName(source_node.name(), unique_name=True)
    except:
        pass
    
    # 复制位置
    try:
        target_node.setPosition(source_node.position())
    except:
        pass
    
    # 复制颜色
    try:
        target_node.setColor(source_node.color())
    except:
        pass
    
    # 复制用户数据
    try:
        shape_data = source_node.userData("nodeshape")
        if shape_data is not None and shape_data.strip():
            target_node.setUserData("nodeshape", shape_data)
    except:
        pass
    
    # 复制参数值
    for parm in source_node.parms():
        try:
            target_parm = target_node.parm(parm.name())
            if target_parm:
                # 直接设置原始值，保持表达式
                target_parm.set(parm.rawValue())
        except:
            continue

def should_copy_children(node):
    """
    判断节点是否需要递归复制其子节点
    
    Args:
        node (hou.Node): 要检查的节点
    
    Returns:
        bool: 是否需要递归复制
    """
    node_type = node.type().name().lower()
    # 需要递归复制的节点类型列表
    recursive_types = [
        'subnet',
        'subnetwork',
        'sopcreate',
        'materiallibrary',
        'sopnet',
        'lopnet',
        'dopnet',
        'ropnet',
        'chopnet',
        'shopnet',
        'vopnet',
        'matnet'
    ]
    
    return any(t in node_type for t in recursive_types)

def copy_node_recursive(source_node, target_parent, node_map):
    """
    递归复制节点及其所有子节点
    
    Args:
        source_node (hou.Node): 源节点
        target_parent (hou.Node): 目标父节点
        node_map (dict): 节点映射字典
    
    Returns:
        hou.Node: 复制的节点
    """
    # 创建新节点
    new_node = target_parent.createNode(source_node.type().name())
    
    # 复制节点属性
    copy_node_properties(source_node, new_node)
    
    # 将节点添加到映射字典
    node_map[source_node] = new_node
    
    # 如果需要递归复制子节点
    if should_copy_children(source_node):
        # 复制所有子节点
        for child in source_node.children():
            copy_node_recursive(child, new_node, node_map)
    
    return new_node

def setup_node_connections(node_map):
    """
    设置所有节点的连接关系
    
    Args:
        node_map (dict): 节点映射字典
    """
    for source_node, target_node in node_map.items():
        # 设置输入连接
        for connection in source_node.inputConnections():
            if connection:
                input_node = connection.inputNode()
                if input_node in node_map:
                    target_node.setInput(
                        connection.inputIndex(),
                        node_map[input_node],
                        connection.outputIndex()
                    )

def convert_hda_to_lop_subnet(source_node):
    """
    将输入的HDA节点转换为LOP Subnetwork
    
    Args:
        source_node (hou.Node): 源HDA节点
    
    Returns:
        hou.Node: 创建的LOP Subnetwork节点
    """
    if not source_node:
        raise ValueError("未找到源节点")
    
    if not source_node.type().definition():
        raise ValueError("输入节点不是HDA")
    
    # 获取HDA定义
    hda_def = source_node.type().definition()
    
    # 创建一个新的Subnet
    stage = source_node.parent()
    subnet = stage.createNode("subnet")
    subnet.setName(f"{source_node.name()}_converted")
    
    # 用于存储所有节点的映射关系
    node_map = {}
    
    # 递归复制所有节点
    for child in source_node.children():
        copy_node_recursive(child, subnet, node_map)
    
    # 设置所有节点的连接关系
    setup_node_connections(node_map)
    
    # 复制HDA的脚本内容
    copy_scripts_and_ui(hda_def, subnet)
    
    # 复制UI组件
    copy_ui_components(hda_def, subnet)
    
    # 设置Subnet的描述
    subnet.setComment(f"Converted from HDA: {source_node.name()}")
    
    # 布局网络
    subnet.layoutChildren()
    
    # 设置显示标志
    try:
        subnet.setDisplayFlag(True)
    except:
        pass
    
    # 设置输入连接
    input_connections = source_node.inputConnections()
    for connection in input_connections:
        if connection:
            input_idx = connection.inputIndex()
            subnet.setInput(input_idx, connection.inputNode(), connection.outputIndex())
    
    # 设置位置
    subnet.setPosition(source_node.position() + hou.Vector2(3.0, 0))
    
    return subnet

def main():
    """
    主函数：将当前选中的HDA节点转换为Subnet
    """
    # 获取当前选中的节点
    selected_nodes = hou.selectedNodes()
    if not selected_nodes:
        raise ValueError("请先选择一个HDA节点")
    
    # 使用第一个选中的节点
    source_node = selected_nodes[0]
    
    try:
        subnet = convert_hda_to_lop_subnet(source_node)
        print(f"成功将HDA转换为LOP Subnetwork: {subnet.path()}")
        return subnet
    except Exception as e:
        print(f"转换过程中出错: {str(e)}")
        raise

main()