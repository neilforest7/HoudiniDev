import os
import re
import hou

from PySide2 import QtGui as gui
from PySide2 import QtCore as core
from PySide2 import QtWidgets as wdg
### MODEL ###

## CREATE GEO FUNCTIONS ##
#Get geo and proxy path 
def getGeoAndProxyPath(dirList, geoFormat, lod, lodProxy, assetDir):
    
    geoFile=""
    proxyFile=""
    
    proxyLodLower = lodProxy.lower()
    proxyLodUpper = lodProxy.upper()
        
    #Find geo file in folder
    for file in dirList:
        if lod in file and geoFormat in file:
            geoFile=file
        
    #Find proxy file in folder if needed
    if lodProxy != "None":
        for file in dirList:
            if lodProxy in file and geoFormat in file:
                proxyFile=file
        
    #Set geo and proxy paths
    geoPath=assetDir+"/"+geoFile
    proxyPath=assetDir+"/"+proxyFile
    
    return geoPath, proxyPath

#Function that creates a temporary geo to get the number of variations of a 3D asset
def getNumVars(node,geoPath,geoFormat):

    aux = node.createNode("sopcreate","aux")
    create = aux.node("sopnet").node("create")
        
    #Create file node and set path to geoPath
    file = create.createNode("file")
    file.parm("file").set(geoPath)
    
    if geoFormat == "abc":
        geo = file.geometry()
        prims = geo.prims()
    else:
        pack = file.createOutputNode("pack")
        pack.parm("packbyname").set(1)
        
        geo = pack.geometry()
        prims = geo.prims()
        
    numVars = len(prims)
        
    aux.destroy()
    
    return numVars

#Create Var Nodes function
def createVarNodes(node,i,input):
    geoVar = node.createNode("sopcreate","geo_var_"+str(i))
    geoVarCreate = geoVar.node("sopnet").node("create")
    
    nullGeo = node.createNode("null","IN_GEO_"+str(i))
    nullGeo.setInput(0,geoVar)
    
    #Create proxy var
    proxyVar = node.createNode("sopcreate","proxy_var_"+str(i))
    proxyVarCreate = proxyVar.node("sopnet").node("create")
    
    nullProxy = node.createNode("null","IN_PROXY_"+str(i))
    nullProxy.setInput(0,proxyVar)
    
    #Create switch proxy
    switchProxy = node.createNode("switch","switch_hasProxy")
    switchProxy.parm("input").setExpression("ch(\"../../hasProxy\")")
    nullEmpty = node.createNode("null","EMPTY")
    switchProxy.setInput(0,nullEmpty)
    switchProxy.setInput(1,nullProxy)
    
    merge = node.createNode("merge")
    merge.setInput(0,nullGeo)
    merge.setInput(1,switchProxy)
    
    nullVar = node.createNode("null","VAR_"+str(i+1))
    nullVar.setInput(0,merge)
    
    #Add variant
    input.setInput(i+1,nullVar)
    
    return geoVarCreate,proxyVarCreate
    
#Create and set geo inside var nodes
def createGeoVar(hda, node, assetName, filePath, i, path, type, geoFormat):

    #Create file node and set path to geoPath
    file = node.createNode("file")
    file.parm("file").set(filePath)
    
    #Create convert and transform node
    if type == "3DPlant":
        convert1 = file.createOutputNode("convert")
        transform = convert1.createOutputNode("xform")
    else:
        transform = file.createOutputNode("xform")
        
    transform.parm("scale").set(0.01)
    
    if type == "3D":
        #Blast current var
        if geoFormat != "abc":
            pack = transform.createOutputNode("pack")
            pack.parm("packbyname").set(1)
            blast = pack.createOutputNode("blast")
        else:
            blast = transform.createOutputNode("blast")
            
        blast.parm("group").set(str(i))
        blast.parm("negate").set(1)
        
        convert2 = blast.createOutputNode("convert")
        
        #Create match size
        matchsize = convert2.createOutputNode("matchsize")
    else:
        matchsize = transform.createOutputNode("matchsize")
        matchsize.parm("justify_y").set(1)
    
    matchsize.parm("sizex").set(2)
    matchsize.parm("sizey").set(2)
    matchsize.parm("sizez").set(2)
    matchsize.parm("doscale").set(1)
    
        
    #Create normalize switch
    switchNormalize = node.createNode("switch","switch_isNormalize")
    if type == "3D":
        switchNormalize.setInput(0,convert2)
    else:
        switchNormalize.setInput(0,transform)
        
    switchNormalize.setInput(1,matchsize)
    switchNormalize.parm("input").setExpression("ch(\"../../../../../normalize\")")
    
    #Create attribute wrangle and set path for the geo
    wranglePath = node.createNode("attribwrangle","setPath")
    wranglePath.parm("snippet").set(path)  
    wranglePath.parm("class").set(1)  
    wranglePath.setInput(0,switchNormalize)
    
    attribdelete = node.createNode("attribdelete")
    attribdelete.parm("negate").set(1)
    attribdelete.parm("ptdel").set("N P uv Cd")
    attribdelete.parm("vtxdel").set("uv N Cd")
    attribdelete.parm("primdel").set("path")
    attribdelete.setInput(0,wranglePath)
    
    groupdelete = node.createNode("groupdelete")
    groupdelete.parm("group1").set("*")
    groupdelete.setInput(0,attribdelete)
    
    outNull = groupdelete.createOutputNode("null","OUT")
    
    outNull.setDisplayFlag(True)  
    outNull.setRenderFlag(True)
    
    node.layoutChildren()
    
    return

    
#Build geo function    
def buildGeo(node, assetDir, lod, lodProxy, geoFormat, assetType, assetTexturesFolder, assetObjFolder, hasProxy):

    #Get asset name
    assetName = node.parm("name").eval()

    #Get list of files on assetFolder dir
    dirList = os.listdir(assetDir)
    
    #Get megascansSubnet node and delete all nodes inside it
    megascansSubnet = node.node("megascans_variants")
    child_nodes = megascansSubnet.children()
    
    for child in child_nodes:
        child.destroy()
    
    #Create variant control nodes        
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
    
    #Process 3D type asset
    if assetType == "3D":
        #Get geo and proxy files
        assetObjFolderList = os.listdir(assetObjFolder)
        geoPath, proxyPath = getGeoAndProxyPath(assetObjFolderList, geoFormat, lod, lodProxy, assetObjFolder)
        
        #Get num of vars
        numVars = getNumVars(megascansSubnet,geoPath,geoFormat)
        
        #Create geo and proxy nodes for each variation
        for i in range(numVars):
            
            #Create geo var
            geoVarCreate, proxyVarCreate = createVarNodes(megascansSubnet, i, addvariant)
            
            #Create geo inside geo_var node
            path = "s@path=chs(\"../../../../../geoPrimPath\");"
            createGeoVar(node, geoVarCreate, assetName, geoPath, i, path, assetType, geoFormat)
            
            #Create proxy inside geo_var node if needed
            if lodProxy != "None":
                path = "s@path=chs(\"../../../../../proxyPrimPath\");"
                createGeoVar(node, proxyVarCreate, assetName, proxyPath, i, path, assetType, geoFormat)
            
            
                
        #Create output node
        output = setvariant.createOutputNode("output")
        output.setDisplayFlag(True) 
        
        
    
    #Process plant type asset
    elif assetType == "3DPlant":
        numVars = sum(1 for s in dirList if "Var" in s)
        
        for i in range(numVars):
            varAssetFolder=assetDir+"Var"+str(i+1)+"/"
            varList = os.listdir(varAssetFolder)
            
            #Get geo and proxy files            
            geoPath, proxyPath = getGeoAndProxyPath(varList, geoFormat, lod, lodProxy, varAssetFolder)
            
            #Create geo and proxy var nodes
            geoVarCreate, proxyVarCreate = createVarNodes(megascansSubnet, i, addvariant)
            
            #Create geo inside geo_var node
            path = "s@path=chs(\"../../../../../geoPrimPath\");"
            createGeoVar(node, geoVarCreate, assetName, geoPath, i, path, assetType, geoFormat)
            
            #Create proxy inside geo_var node if needed
            if lodProxy != "None":
                path = "s@path=chs(\"../../../../../proxyPrimPath\");"
                createGeoVar(node, proxyVarCreate, assetName, proxyPath, i, path, assetType, geoFormat)
            
        #Create output node
        output = megascansSubnet.createNode("output")
        output.setInput(0,setvariant)
        output.setDisplayFlag(True) 
        
    megascansSubnet.layoutChildren()
    
## END CREATE GEO FUNCTIONS ##

## CREATE MATERIAL FUNCTIONS ##

# Create MaterialX subnet
def createMaterialXSubnet(parent):
    
    # Code for /stage/PB_asset_builder_usd1/materiallibrary1/mtlxmaterial
    mtlx_subnet = parent.createNode("subnet", "mtlxmaterial__VAR_1")
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
def getTexturesDict(texturesNames, texturesDir, res, textFormat, lod):

    textures = os.listdir(texturesDir)
    texturesDict = {}
    
    for tn in texturesNames:
        texture = ""
        for tp in textures:
            format = tp.split(".")[-1]
            if tn in tp and "Normal" in tp and "LOD" in tp:
                if textFormat == format and res in tp and lod in tp:
                    texture = tp
                    break    
            elif lod != "High" and tn in tp and "Displacement" in tp and textFormat != format and format == "exr":
                if res in tp:
                    texture = tp
                    break
                '''
                message = f"A .exr Displacement texture was found but .{textFormat} was the selected format.\nDo you want to replace it?.\nThis only affects Displacement map."
                messageButtons = ("Replace" , "Pass")
                button = hou.ui.displayMessage(message, buttons = messageButtons)
                
                #Check which button was pressed
                if button == 0:
                    if res in tp:
                        texture = tp
                        break
                elif button == 1:
                    if textFormat == format and res in tp:
                        texture = tp
                        break
                '''
                
                    
            elif tn in tp and textFormat == format and res in tp:
                texture = tp
                break
        texturesDict[tn] = texture
        
    if lod == "High":
        texturesDict["Normal"] = ""
        texturesDict["Displacement"] = ""
        
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
def applyTextures(mtlx_subnet, mtlxstandard_surface, mtlxdisplacement, texturesDict, texturesDir):

    mtlxmultiply = mtlx_subnet.createNode("mtlxmultiply")
    mtlxstandard_surface.setInput(1,mtlxmultiply)
    
    mtlxnormalmap = mtlx_subnet.createNode("mtlxnormalmap")
    mtlxstandard_surface.setInput(40,mtlxnormalmap)
    
    for td in texturesDict:
        if texturesDict[td] != "":
            image = mtlx_subnet.createNode("mtlximage",td)
            path = texturesDir+texturesDict[td]
            image.parm("file").set(path)
            
            if td == "Albedo":
                mtlxmultiply.setInput(0,image)
            if td == "Metalness":
                mtlxstandard_surface.setInput(3,image)
                image.parm("signature").set("float")
            if td == "AO":
                mtlxmultiply.setInput(1,image)
                image.parm("signature").set("float")
            if td == "Normal":
                mtlxnormalmap.setInput(0,image)
                image.parm("signature").set("vector3")
            if td == "Roughness":
                mtlxstandard_surface.setInput(6,image)
                image.parm("signature").set("float")
            if td == "Displacement":
                min, max = getMinMaxPixelValue(path)
                                
                mtlxrange = image.createOutputNode("mtlxrange")
                mtlxrange.parm("inlow").set(0)
                mtlxrange.parm("inhigh").set(1)
                mtlxrange.parm("outlow").set(-.5)
                mtlxrange.parm("outhigh").set(.5)
                
                mtlxdisplacement.setInput(0,mtlxrange)
                mtlxdisplacement.parm("scale").set(0.01)
                image.parm("signature").set("float")
            if td == "Opacity":
                mtlxstandard_surface.setInput(38,image)
                image.parm("signature").set("float")
            if td == "Transmission":
                mtlxstandard_surface.setInput(11,image)
            if td == "Translucency":
                mtlxstandard_surface.setInput(18,image)
                mtlxstandard_surface.setInput(17,image)
                
                            
    mtlx_subnet.layoutChildren()


#Build material function
def buildMaterial(node, assetDir, lod, res, textFormat, assetType, hasProxy):

    #Get materiallibrary1 node and delete all nodes inside it
    materiallibrary = node.node("materiallibrary1")
    child_nodes = materiallibrary.children()

    for n in child_nodes:
        n.destroy()
        
    #Create MaterialX subnet inside materialibrary node
    mtlx_subnet, mtlxstandard_surface, mtlxdisplacement = createMaterialXSubnet(materiallibrary)
    
    #Build texture path
    if assetType == "3D":
        texturesDir=assetDir+"/"
    else:
        texturesDir=assetDir+"/Textures/Atlas/"
        
    #Set textures types list    
    textureNames = ["Albedo", "Metalness", "Roughness", "Displacement", "Normal", "AO", "Opacity", "Translucency", "Transmission"]
    
    texturesDict = getTexturesDict(textureNames, texturesDir, res, textFormat, lod)
    
    #Get assign material node
    assignmaterial = node.node("material_assign").node("assignmaterial1")
    
    #Assign material
    assignmaterial.parm("nummaterials").set(1)
    assignmaterial.parm("primpattern1").set("/`chs(\"../../CONTROL/name\")`"+"`chs(\"../../geoPrimPath\")`")
    assignmaterial.parm("matspecpath1").set("/`chs(\"../../CONTROL/name\")`/materials/mtlxmaterial__VAR_1")
    if hasProxy:
        assignmaterial.parm("nummaterials").set(2)
        assignmaterial.parm("primpattern2").set("/`chs(\"../../CONTROL/name\")`"+"`chs(\"../../proxyPrimPath\")`")
        assignmaterial.parm("matspecpath2").set("/`chs(\"../../CONTROL/name\")`/materials/mtlxmaterial__VAR_1")
    
    #Apply textures
    applyTextures(mtlx_subnet, mtlxstandard_surface, mtlxdisplacement, texturesDict, texturesDir)


## END CREATE MATERIAL FUNCTIONS ##


#Build geo and material function
def buildAll(node, assetDir, lod, lodProxy, geoFormat, res, textFormat, assetType, assetTexturesFolder, assetObjFolder, hasProxy):
    #print(f"Asset Type: {assetType} Selected: LOD -> {lod}, LOD Proxy -> {lodProxy}, Geo Format -> {geoFormat}, Texture Resolution -> {res}, Texture Format -> {textFormat}")
    buildGeo(node, assetDir, lod, lodProxy, geoFormat, assetType, assetTexturesFolder, assetObjFolder, hasProxy)
    buildMaterial(node, assetDir, lod, res, textFormat, assetType, hasProxy)

    
    
    
### VIEW ###

# Global reference to the MainDialog instance
dialogWindow = None

class MainDialog(wdg.QDialog):

    def __init__(self, node, assetDir, LOD, geoFormat, textRes, textFormat, assetType, assetTexturesFolder, assetObjFolder, hasProxy):
        super(MainDialog, self).__init__()
        
        #Store attributes
        self.assetType = assetType
        self.hasProxy = hasProxy
        self.assetDir = assetDir
        self.assetTexturesFolder = assetTexturesFolder
        self.assetObjFolder = assetObjFolder
        self.node = node
        
        # Set window
        self.setWindowTitle("Megascans Asset Builder")
        self.setFixedSize(core.QSize(400,225))
        
        # Create main Layout
        mainLay = wdg.QVBoxLayout()
        
        # Create QFormLayout
        formLay = wdg.QFormLayout()
        mainLay.addLayout(formLay)
        
        # Create LOD Combo Box        
        self.lod_combo_box = wdg.QComboBox()
        self.lod_combo_box.addItems(LOD)  
        self.lod_combo_box.setFixedSize(250, 30)
        formLay.addRow(self.tr("&LOD: "), self.lod_combo_box)        
        
        # Create LOD Proxy Combo Box    
        if self.hasProxy:
            self.lod_proxy_combo_box = wdg.QComboBox()
            self.lod_proxy_combo_box.addItems(LOD)  
            self.lod_proxy_combo_box.setFixedSize(250, 30)
            formLay.addRow(self.tr("&LOD Proxy: "), self.lod_proxy_combo_box)
            
        # Create Geo Format Combo Box 
        self.geoFormat_combo_box = wdg.QComboBox()
        self.geoFormat_combo_box.addItems(geoFormat)  
        self.geoFormat_combo_box.setFixedSize(250, 30)
        formLay.addRow(self.tr("&Geo Format: "), self.geoFormat_combo_box)
        
        # Create Texture Res Combo Box        
        self.textRes_combo_box = wdg.QComboBox()
        self.textRes_combo_box.addItems(textRes)
        self.textRes_combo_box.setFixedSize(250,30)
        formLay.addRow(self.tr("&Texture Resolution: "), self.textRes_combo_box)
        
        # Create Texture Format Combo Box
        self.textFormat_combo_box = wdg.QComboBox()
        self.textFormat_combo_box.addItems(textFormat)
        self.textFormat_combo_box.setFixedSize(250,30)
        formLay.addRow(self.tr("&Texture Format: "), self.textFormat_combo_box)
        
        # Create buttons layout
        buttonsLay = wdg.QHBoxLayout()
        mainLay.addLayout(buttonsLay)
        
        buildAllButton = wdg.QPushButton("Build All")
        buildAllButton.clicked.connect(self.viewBuildAll)
        buttonsLay.addWidget(buildAllButton)
        
        buildGeoButton = wdg.QPushButton("Build Geo")
        buildGeoButton.clicked.connect(self.viewBuildGeo)
        buttonsLay.addWidget(buildGeoButton)
        
        buildMaterialButton = wdg.QPushButton("Build Material")
        buildMaterialButton.clicked.connect(self.viewBuildMaterial)
        buttonsLay.addWidget(buildMaterialButton)
        
        cancelButton = wdg.QPushButton("Cancel")
        cancelButton.clicked.connect(self.reject)
        buttonsLay.addWidget(cancelButton)
        
        buttonsLay.setAlignment(core.Qt.AlignCenter)
        
        
        # Set main layout
        self.setLayout(mainLay)
        self.show()
        
        
    def viewBuildAll(self):
        # Get the selected items from the combo boxes
        lod = self.lod_combo_box.currentText()
        lodProxy = "None"
        if self.hasProxy:
            lodProxy = self.lod_proxy_combo_box.currentText()
        geoFormat = self.geoFormat_combo_box.currentText()
        res = self.textRes_combo_box.currentText()
        textFormat = self.textFormat_combo_box.currentText()
        
        assetType = self.assetType
        hasProxy = self.hasProxy
        assetDir = self.assetDir
        assetTexturesFolder = self.assetTexturesFolder
        assetObjFolder = self.assetObjFolder
        node = self.node
        
        buildAll(node, assetDir, lod, lodProxy, geoFormat, res, textFormat, assetType, assetTexturesFolder, assetObjFolder, hasProxy)
        self.accept()
        message = "Megascans Asset was successfully built."
        hou.ui.displayMessage(message)

    def viewBuildGeo(self):
        # Get the selected items from the combo boxes
        lod = self.lod_combo_box.currentText()
        lodProxy = "None"
        if self.hasProxy:
            lodProxy = self.lod_proxy_combo_box.currentText()
        geoFormat = self.geoFormat_combo_box.currentText()
        
        assetType = self.assetType
        hasProxy = self.hasProxy
        assetDir = self.assetDir
        assetTexturesFolder = self.assetTexturesFolder
        assetObjFolder = self.assetObjFolder
        node = self.node
        
        buildGeo(node, assetDir, lod, lodProxy, geoFormat, assetType, assetTexturesFolder, assetObjFolder, hasProxy)
        self.accept()
        message = "Megascans Asset geo was successfully built."
        hou.ui.displayMessage(message)
        
        
    def viewBuildMaterial(self):
        # Get the selected items from the combo boxes
        lod = self.lod_combo_box.currentText()
        res = self.textRes_combo_box.currentText()
        textFormat = self.textFormat_combo_box.currentText()
        
        assetType = self.assetType
        assetDir = self.assetDir
        hasProxy = self.hasProxy
        node = self.node
    
        buildMaterial(node, assetDir, lod, res, textFormat, assetType, hasProxy)
        self.accept()
        
        message = "Megascans Asset material was successfully built."
        hou.ui.displayMessage(message)


#Get asset type
def getAssetType(assetDir):
    dirs = os.listdir(assetDir)
    
    if "Textures" in dirs:
        assetType = "3DPlant"
    else:
        assetType = "3D"
    return assetType

#Get asset info
def getAssetInfo(assetDir, assetType):
    
    LOD=[]
    geoFormat=[]
    textRes=[]
    textFormat=[]
    
    if assetType == "3D":
        assetTexturesFolder = assetDir
        dirList = os.listdir(assetDir)
        if "Var1" in dirList:
            assetObjFolder = assetDir+"/Var1"
        else:
            assetObjFolder = assetDir
    else:
        assetTexturesFolder = assetDir+"/Textures/Atlas"
        assetObjFolder = assetDir+"/Var1"
    
    #Get LODs and geo format list
    lodFiles = [f for f in os.listdir(assetObjFolder) if "abc" in f or "fbx" in f or "obj" in f]
    lodList = []
    formList = []
    
    for f in lodFiles:
        filename = os.path.splitext(f)[0]
        ext = f.split(".")[-1]
        lodItem = filename.split("_")[-1]
        if "." not in lodItem:
            lodList.append(lodItem)
        formList.append(ext)
    
    lodList = set(lodList)
    LOD = list(lodList)
    LOD.sort()
    
    formList = set(formList)
    geoFormat = list(formList)
    geoFormat.sort()
    
    
    #Get texture resolutions and format list
    pattern = r"_\d+K_"
    
    textureFiles = [f for f in os.listdir(assetTexturesFolder) if re.search(pattern, f)]
    textureList = []
    formList = []
    
    exrNum = 0
    
    for f in textureFiles:
        filename = os.path.splitext(f)[0]
        ext = f.split(".")[-1]
        if ext == "exr":
            exrNum += 1
        textureList.append(filename.split("_")[1])
        formList.append(ext)
    
    textureList = set(textureList)
    textRes = list(textureList)
    textRes.sort()
    
    formList = set(formList)
    textFormat = list(formList)
    if exrNum == 1: textFormat.remove("exr")
    textFormat.sort()
        
    return LOD, geoFormat, textRes, textFormat, assetTexturesFolder, assetObjFolder


#Main button function, check errors and create dialog
def createBuildDialog():
    
    #Get node parameters
    node = hou.pwd() 
    assetDir = node.parm("asset_folder").eval()
    assetName = node.parm("name").eval()
    hasProxy = node.parm("hasProxy").eval()
    
    #Check errors
    if os.path.isdir(assetDir) == False: 
        hou.ui.displayMessage("Error: Asset folder does not exists.", severity=hou.severityType.Error)
        return
    
    if len(assetName) <= 1: 
        hou.ui.displayMessage("Error: Asset Name should contain 2 or more letters.", severity=hou.severityType.Error)
        return
        
        
    assetType = getAssetType(assetDir)
    LOD, geoFormat, textRes, textFormat, assetTexturesFolder, assetObjFolder = getAssetInfo(assetDir, assetType)
    
    if len(LOD) == 0 or len(geoFormat) == 0: 
        hou.ui.displayMessage("Error: Can't find any abc, fbx or obj geometry.", severity=hou.severityType.Error)
        return
        
    if len(textRes) == 0 or len(textFormat) == 0: 
        hou.ui.displayMessage("Error: Can't find any textures.", severity=hou.severityType.Error)
        return
    
        
    #Create dialog
    global dialogWindow
    if dialogWindow is None or not dialogWindow.isVisible():
        dialogWindow = MainDialog(node, assetDir, LOD, geoFormat, textRes, textFormat, assetType, assetTexturesFolder, assetObjFolder, hasProxy)

#Main button function, check errors and create dialog
def clear():
    #Get node parameters
    node = hou.pwd() 
    geo_subnet = node.node("megascans_variants")
    mat_library = node.node("materiallibrary1")
    mat_assign = node.node("material_assign")
    
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
            