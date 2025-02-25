def run_onloaded(current_node):
    import hou
    auto_load_external_script(current_node)

def onloaded_sym():
    import hou
    current_node=hou.pwd()
    auto_load_external_script(current_node)

def auto_load_external_script(current_node):
    import os, sys, hou, importlib
    current_node.setColor(hou.Color(0.3,0.6,1))


 ######   ######## ########    ######## ##     ## ########    ##       ####  ######  ########
##    ##  ##          ##       ##        ##   ##     ##       ##        ##  ##    ##    ##
##        ##          ##       ##         ## ##      ##       ##        ##  ##          ##
##   #### ######      ##       ######      ###       ##       ##        ##   ######     ##
##    ##  ##          ##       ##         ## ##      ##       ##        ##        ##    ##
##    ##  ##          ##       ##        ##   ##     ##       ##        ##  ##    ##    ##
 ######   ########    ##       ######## ##     ##    ##       ######## ####  ######     ##

def get_extention_list():
    ImportFileExtentionList = ['fbx','abc']
    ExportFileExtentionList = ['usd','usda','usdc']
    return ImportFileExtentionList, ExportFileExtentionList


def GetImageExtentionList():
    ImageExtentionList = ['jpg','exr','png','tga','tif']
    return ImageExtentionList

def GetImageResolutionList():
    ImageResolutionList = ['AUTO','1K','2K','4K','8K','16K']

    return ImageResolutionList



########  ########  #### ##    ## ########       ##       #### ##    ## ########
##     ## ##     ##  ##  ###   ##    ##          ##        ##  ###   ## ##
##     ## ##     ##  ##  ####  ##    ##          ##        ##  ####  ## ##
########  ########   ##  ## ## ##    ##          ##        ##  ## ## ## ######
##        ##   ##    ##  ##  ####    ##          ##        ##  ##  #### ##
##        ##    ##   ##  ##   ###    ##          ##        ##  ##   ### ##
##        ##     ## #### ##    ##    ##          ######## #### ##    ## ########

def PrintLine():
    import inspect
    # Get the current frame and the line number
    frame = inspect.currentframe().f_back
    line_number = frame.f_lineno
    # Print the formatted line number
    print(f"*** LINE {line_number:04d} ***")


 ######   #######  ##        #######  ########     ##     ##    ###    ##       ##     ## ########  ######
##    ## ##     ## ##       ##     ## ##     ##    ##     ##   ## ##   ##       ##     ## ##       ##    ##
##       ##     ## ##       ##     ## ##     ##    ##     ##  ##   ##  ##       ##     ## ##       ##
##       ##     ## ##       ##     ## ########     ##     ## ##     ## ##       ##     ## ######    ######
##       ##     ## ##       ##     ## ##   ##       ##   ##  ######### ##       ##     ## ##             ##
##    ## ##     ## ##       ##     ## ##    ##       ## ##   ##     ## ##       ##     ## ##       ##    ##
 ######   #######  ########  #######  ##     ##       ###    ##     ## ########  #######  ########  ######

def GetColorValues():
    node_color={'white':(1,1,1), 'yellow':(1,1,0), 'orange':(1,0.5,0),'lightred':(1,0.8,0.8),'red':(1,0,0),'lightgreen':(0.5,1,0.5),'green':(0,1,0),'turquoise':(0.6159999966621399, 0.8709999918937683, 0.7689999938011169),'purple':(1,0,1),'lightblue':(0,1,1),'blue':(0,0.5,1),'black':(0,0,0),'default':False}
    return node_color



def texture_list_from_TextureDirSource(TextureDirSource):
    import os

    # SOS now

    HDA = hou.pwd()

    ImageResolutionList = GetImageResolutionList()

    RevImageResolutionList = []
    for i in range (0,len(ImageResolutionList)):
        RevImageResolutionList.append(ImageResolutionList[len(ImageResolutionList)-1-i])
    RevImageResolutionList = RevImageResolutionList[:-1]

    ImageResolution = ImageResolutionList[HDA.parm('ImageResolution').eval()]
    ImageExtentionList = GetImageExtentionList()
    AO_Extention = ImageExtentionList[HDA.parm('AO_Extention').eval()]
    Albedo_Extention = ImageExtentionList[HDA.parm('Albedo_Extention').eval()]
    Gloss_Extention = ImageExtentionList[HDA.parm('Gloss_Extention').eval()]
    Specular_Extention = ImageExtentionList[HDA.parm('Specular_Extention').eval()]
    Metalness_Extention = ImageExtentionList[HDA.parm('Metalness_Extention').eval()]
    Roughness_Extention = ImageExtentionList[HDA.parm('Roughness_Extention').eval()]
    Bump_Extention = ImageExtentionList[HDA.parm('Bump_Extention').eval()]
    Opacity_Extention = ImageExtentionList[HDA.parm('Opacity_Extention').eval()]
    Normal_Extention = ImageExtentionList[HDA.parm('Normal_Extention').eval()]
    Displacement_Extention = ImageExtentionList[HDA.parm('Displacement_Extention').eval()]
    Translucency_Extention = ImageExtentionList[HDA.parm('Translucency_Extention').eval()]
    Transmission_Extention = ImageExtentionList[HDA.parm('Transmission_Extention').eval()]
    Fuzz_Extention = ImageExtentionList[HDA.parm('Fuzz_Extention').eval()]

    texture_file_detect_list =  [
                                   ImageResolution + '_AO.'+ AO_Extention,
                                   ImageResolution + '_Albedo.' + AO_Extention,
                                   ImageResolution + '_Gloss.' + Gloss_Extention,
                                   ImageResolution + '_Specular.' + Specular_Extention,
                                   ImageResolution + '_Metalness.' + Metalness_Extention,
                                   ImageResolution + '_Roughness.' + Roughness_Extention,
                                   ImageResolution + '_Bump.' + Bump_Extention,
                                   ImageResolution + '_Opacity.' + Opacity_Extention,
                                   ImageResolution + '_Normal.' + Normal_Extention,
                                   ImageResolution + '_Normal_LOD0.' + Normal_Extention,
                                   ImageResolution + '_Displacement.'+ Displacement_Extention,
                                   ImageResolution + '_Translucency.' + Translucency_Extention,
                                   ImageResolution + '_Transmission.' + Transmission_Extention,
                                   ImageResolution + '_Fuzz.' + Fuzz_Extention
                                ] # SOS

    #texture_file_detect_list = ['_AO.', '_Albedo.', '_Displacement.exr', '_Normal.', '_Normal_LOD0.', '_Roughness.', '_Specular.', '_Opacity.', '_Translucency.']
    TextureList = []

    if TextureDirSource != False:
        CheckList = os.listdir(TextureDirSource)
        ResolutionValue = 0
        PreviousResolutionValue = 0

        CheckResolutionValueList = [0]
        for ImgToCheck in CheckList:
            for check in texture_file_detect_list: # SOS now now
                if check.replace(ImageResolution,'') in ImgToCheck:
                    CheckResolutionValue = int(ImgToCheck.split('K_')[0].split('_')[-1])
                    CheckResolutionValueList.append(CheckResolutionValue)
            CheckMaxResolution = str(max(CheckResolutionValueList))+'K'

        for ImgToCheck in CheckList:
            if not ImageResolution == 'AUTO':   # This will check for Image Resolutions within the range of '1K','2K','4K','8K','16K'
                for check in texture_file_detect_list:
                    if check in ImgToCheck:
                        if not '.rat' in ImgToCheck: # Don't include *.rat files in source, they are created by Houdini and are not part of teh MagaScan Source
                            #print(f'ImgToCheck: {ImgToCheck}')
                            TextureList.append(ImgToCheck)

            else:                               # This will check for Image with the Max Resolutions within the range of '1K','2K','4K','8K','16K'
                for check in texture_file_detect_list:
                    CheckAutoResolution = check.replace('AUTO',CheckMaxResolution)
                    if CheckAutoResolution in ImgToCheck: # SOS now
                        if not '.rat' in ImgToCheck: # Don't include *.rat files in source, they are created by Houdini and are not part of teh MagaScan Source
                            #print(f'ImgToCheck: {ImgToCheck}')
                            TextureList.append(ImgToCheck)


    else:
        TextureList = False

    return TextureList

def GetColorFromSelectedNode():
    import hou
    SelectedNode = hou.selectedNodes()[0]
    print(SelectedNode.color().rgb())


def remove_previous_subfolder(directory):
    directory = directory.replace("\\","/")
    if list(directory)[-1] =='/':
        directory_stripped = directory.rsplit('/',2)[0]+'/'
    else:
        directory_stripped = directory.rsplit('/',1)[0]+'/'
    return directory_stripped


 ######  ########  ########    ###    ######## ########       ##    ## ######## ######## ##      ##  #######  ########  ##    ##
##    ## ##     ## ##         ## ##      ##    ##             ###   ## ##          ##    ##  ##  ## ##     ## ##     ## ##   ##
##       ##     ## ##        ##   ##     ##    ##             ####  ## ##          ##    ##  ##  ## ##     ## ##     ## ##  ##
##       ########  ######   ##     ##    ##    ######         ## ## ## ######      ##    ##  ##  ## ##     ## ########  #####
##       ##   ##   ##       #########    ##    ##             ##  #### ##          ##    ##  ##  ## ##     ## ##   ##   ##  ##
##    ## ##    ##  ##       ##     ##    ##    ##             ##   ### ##          ##    ##  ##  ## ##     ## ##    ##  ##   ##
 ######  ##     ## ######## ##     ##    ##    ########       ##    ## ########    ##     ###  ###   #######  ##     ## ##    ##

def CreateNetwork(NetworkPath,network_cfg,AutoPosition,AnkerPoint): # AutoPosition = True, this wil use the "network_target.layoutChildren()" command. // AutoPosition = False, this wil use the "NewNode.setPosition(position - hou.Vector2(0, 1))" command
    import hou
    hou.setUpdateMode(hou.updateMode.Manual)    # This fixes the slow speed of cooking while the python script adds all the nodes
    try:

        network_target = hou.node(NetworkPath)
        NodeCreated_List = []
        AnkerPoint = hou.Vector2(AnkerPoint)

        for Node in network_cfg:

            NODE_TYPE=(network_cfg[Node]['NODE_TYPE'])
            NODE_COLOR=(network_cfg[Node]['NODE_COLOR'])
            TARGET_NODE_DICT=(network_cfg[Node]['TARGET_NODE_DICT']) # {'TargetNode':'TargetInput1','TargetNode':'TargetInput2' }
            PRE_EXIST=(network_cfg[Node]['PRE_EXIST'])
            PTU_INPUT_FLAG=(network_cfg[Node]['PTU_INPUT_FLAG'])
            ACTIVATE=(network_cfg[Node]['ACTIVATE'])
            PARAMETER=(network_cfg[Node]['PARAMETER'])

            #print(f'<{Node}>  NODE_TYPE: {NODE_TYPE}, NODE_COLOR: {NODE_COLOR}, TARGET_NODE_DICT: {TARGET_NODE_DICT}, PRE_EXIST: {PRE_EXIST}, PTU_INPUT_FLAG: {PTU_INPUT_FLAG}, ACTIVATE: {ACTIVATE}, PARAMETER: {PARAMETER}')

            if (PRE_EXIST==False):
                if (PTU_INPUT_FLAG==True):
                    if not hou.node(NetworkPath+'/'+Node):

                        NodeCreated=network_target.createNode(NODE_TYPE)
                        NodeCreated.setName(Node)
                        NodeCreated_List.append(NodeCreated)

                        if (ACTIVATE==False):
                            NodeCreated.bypass(True)
                        else:
                            NodeCreated.bypass(False)
                        if (NODE_COLOR != False):
                            NodeCreated.setColor(hou.Color(NODE_COLOR))

                        if (TARGET_NODE_DICT != False):
                            for TARGET_NODE in TARGET_NODE_DICT:
                                TARGET=(hou.node(NetworkPath+'/'+TARGET_NODE))
                                target_index=TARGET.inputIndex(TARGET_NODE_DICT[TARGET_NODE])   # TARGET_INDEX_NAME
                                TARGET.setInput(target_index, NodeCreated)

                        if (len(PARAMETER)!=0):
                            for parm in PARAMETER:
                                parm_val=PARAMETER[parm]
                                try:
                                    NodeCreated.setParms({parm:parm_val})
                                    #print("Setting Parameters in "+str(NodeCreated)+" {"+str(parm)+":"+str(parm_val)+"}")
                                except Exception as error:
                                    print("ERROR: Next PARMAMETER doesn't exist in "+str(NodeCreated)+" {"+str(parm)+":"+str(parm_val)+"}")
                                    print("Create_network, NodeCreated-A Error: ", error)
                    else:
                        print('**** NODE: '+NetworkPath+Node+' Already exists! ****')
                        pass


            else:
                NodeCreated=hou.node(NetworkPath+Node)
                NodeCreated_List.append(NodeCreated)

                if (NODE_COLOR != False):
                    NodeCreated.setColor(hou.Color(NODE_COLOR))

                if (TARGET_NODE_DICT != False):
                    for TARGET_NODE in TARGET_NODE_DICT:
                        TARGET=(hou.node(NetworkPath+'/'+TARGET_NODE))
                        target_index=TARGET.inputIndex(TARGET_NODE_DICT[TARGET_NODE])   # TARGET_INDEX_NAME
                        TARGET.setInput(target_index, NodeCreated)

                if (len(PARAMETER)!=0):
                    for parm in PARAMETER:
                        parm_val=PARAMETER[parm]
                        try:
                            NodeCreated.setParms({parm:parm_val})
                            #print("Setting Parameters in "+str(NodeCreated)+" {"+str(parm)+":"+str(parm_val)+"}")
                        except Exception as error:
                            print("ERROR: Next PARMAMETER doesn't exist in "+str(NodeCreated)+" {"+str(parm)+":"+str(parm_val)+"}")
                            print("Create_network, NodeCreated-B Error: ", error)

        if AutoPosition == True:
            network_target.layoutChildren()
        if AutoPosition == False:
            position = AnkerPoint
            for NodeToPos in reversed(NodeCreated_List):
                position = position - hou.Vector2(0, 1)
                NodeToPos.setPosition(position)
    except Exception as error2:
        print(f'There is an issue with NetworkPath: {NetworkPath}')
        #hou.node(NetworkPath+'/'+Node).setColor(hou.Color(node_color['red']))
    hou.setUpdateMode(hou.updateMode.AutoUpdate) # End slow speed fix

 ######  ########  ########    ###    ######## ########    ##    ##    ###    ########  ##     ##    ###       ##     ##    ###    ########    ##    ## ######## ######## ##      ##
##    ## ##     ## ##         ## ##      ##    ##          ##   ##    ## ##   ##     ## ###   ###   ## ##      ###   ###   ## ##      ##       ###   ## ##          ##    ##  ##  ##
##       ##     ## ##        ##   ##     ##    ##          ##  ##    ##   ##  ##     ## #### ####  ##   ##     #### ####  ##   ##     ##       ####  ## ##          ##    ##  ##  ##
##       ########  ######   ##     ##    ##    ######      #####    ##     ## ########  ## ### ## ##     ##    ## ### ## ##     ##    ##       ## ## ## ######      ##    ##  ##  ##
##       ##   ##   ##       #########    ##    ##          ##  ##   ######### ##   ##   ##     ## #########    ##     ## #########    ##       ##  #### ##          ##    ##  ##  ##
##    ## ##    ##  ##       ##     ##    ##    ##          ##   ##  ##     ## ##    ##  ##     ## ##     ##    ##     ## ##     ##    ##       ##   ### ##          ##    ##  ##  ##
 ######  ##     ## ######## ##     ##    ##    ########    ##    ## ##     ## ##     ## ##     ## ##     ##    ##     ## ##     ##    ##       ##    ## ########    ##     ###  ###

def CreateKarmaMatNetwork(MatLibPath,material_list):
    import hou, voptoolutils
    node_color=GetColorValues()
    karma_materials_list=[]
    MatLibNode=hou.node(MatLibPath)
    for MatName in material_list:

        DigAssetSubNetworkNode = hou.node(MatLibPath+'/'+MatName)
        if not DigAssetSubNetworkNode:
            subnet_node = None
            name = MatName
            mask = voptoolutils.KARMAMTLX_TAB_MASK
            folder_label= 'Karma Material Builder'
            render_context = "kma"
            mat_builder=voptoolutils._setupMtlXBuilderSubnet(subnet_node=subnet_node, destination_node=MatLibNode, name=name, mask=mask, folder_label=folder_label, render_context=render_context)
            mat_builder.setColor(hou.Color(node_color['lightblue']))
            karma_materials_list.append(mat_builder)

    MatLibNode.layoutChildren()
    return karma_materials_list


########  ##          ###     ######  ########    ########  ########  ######## ##     ## #### ######## ##      ##    #### ##     ##    ###     ######   ########
##     ## ##         ## ##   ##    ## ##          ##     ## ##     ## ##       ##     ##  ##  ##       ##  ##  ##     ##  ###   ###   ## ##   ##    ##  ##
##     ## ##        ##   ##  ##       ##          ##     ## ##     ## ##       ##     ##  ##  ##       ##  ##  ##     ##  #### ####  ##   ##  ##        ##
########  ##       ##     ## ##       ######      ########  ########  ######   ##     ##  ##  ######   ##  ##  ##     ##  ## ### ## ##     ## ##   #### ######
##        ##       ######### ##       ##          ##        ##   ##   ##        ##   ##   ##  ##       ##  ##  ##     ##  ##     ## ######### ##    ##  ##
##        ##       ##     ## ##    ## ##          ##        ##    ##  ##         ## ##    ##  ##       ##  ##  ##     ##  ##     ## ##     ## ##    ##  ##
##        ######## ##     ##  ######  ########    ##        ##     ## ########    ###    #### ########  ###  ###     #### ##     ## ##     ##  ######   ########

def place_preview_images():
    import hou
    hou.setUpdateMode(hou.updateMode.Manual)
    HDA = hou.pwd()
    MegaScanAssetsNode = hou.node(HDA.parent().path()+'/MegaScanAssets/')
    MegaScanDict = GetMegaScanDict(False,False)
    SubNetworkList = []
    network_images = []


    if MegaScanAssetsNode:
        MegaScanAssetsNodeChildren= MegaScanAssetsNode.children()
        editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        editor.setPwd(MegaScanAssetsNode)

        for SubNetwork in MegaScanAssetsNodeChildren:
            if 'subnet' in str(SubNetwork.type()):
                SubNetworkList.append(SubNetwork)

        image_size = hou.Vector2(3,3)
        ImageOffset = hou.Vector2(-image_size[0]/2.9,0.5)

        for SubNetwork in SubNetworkList:
            image_file = MegaScanDict[SubNetwork.name()]['PreviewTargetFile']
            #print(f'image_file: {image_file}')
            image = hou.NetworkImage()
            image.setPath(image_file)

            position = SubNetwork.position() + ImageOffset
            image.setRect(hou.BoundingRect(position, position + image_size))
            network_images.append(image)

        editor.setBackgroundImages(network_images)
    else:
        print('MISSING SUBNET NODE: '+KMBParent.path()+'/MEGASCAN_USD')
    hou.setUpdateMode(hou.updateMode.AutoUpdate) # End slow speed fix


##      ## ########  #### ######## ########    ########  ####  ######  ########    ########  #######           ##  ######   #######  ##    ##
##  ##  ## ##     ##  ##     ##    ##          ##     ##  ##  ##    ##    ##          ##    ##     ##          ## ##    ## ##     ## ###   ##
##  ##  ## ##     ##  ##     ##    ##          ##     ##  ##  ##          ##          ##    ##     ##          ## ##       ##     ## ####  ##
##  ##  ## ########   ##     ##    ######      ##     ##  ##  ##          ##          ##    ##     ##          ##  ######  ##     ## ## ## ##
##  ##  ## ##   ##    ##     ##    ##          ##     ##  ##  ##          ##          ##    ##     ##    ##    ##       ## ##     ## ##  ####
##  ##  ## ##    ##   ##     ##    ##          ##     ##  ##  ##    ##    ##          ##    ##     ##    ##    ## ##    ## ##     ## ##   ###
 ###  ###  ##     ## ####    ##    ########    ########  ####  ######     ##          ##     #######      ######   ######   #######  ##    ##

def write_dict_to_json(MyDict,File):
    import json, os

    os.makedirs(os.path.dirname(File), exist_ok=True)
    with open(File, "w") as file:
        json.dump(MyDict, file, indent=4)
    file.close()


 ######   #######  ########  ##    ##     ######   #######  ##     ## ########   ######  ########     #######     ########    ###    ########   ######   ######## ########
##    ## ##     ## ##     ##  ##  ##     ##    ## ##     ## ##     ## ##     ## ##    ## ##          ##     ##       ##      ## ##   ##     ## ##    ##  ##          ##
##       ##     ## ##     ##   ####      ##       ##     ## ##     ## ##     ## ##       ##                 ##       ##     ##   ##  ##     ## ##        ##          ##
##       ##     ## ########     ##        ######  ##     ## ##     ## ########  ##       ######       #######        ##    ##     ## ########  ##   #### ######      ##
##       ##     ## ##           ##             ## ##     ## ##     ## ##   ##   ##       ##          ##              ##    ######### ##   ##   ##    ##  ##          ##
##    ## ##     ## ##           ##       ##    ## ##     ## ##     ## ##    ##  ##    ## ##          ##              ##    ##     ## ##    ##  ##    ##  ##          ##
 ######   #######  ##           ##        ######   #######   #######  ##     ##  ######  ########    #########       ##    ##     ## ##     ##  ######   ########    ##

def copy_source_to_target(SourceFile, TargetFile):
    import os, shutil
    os.makedirs(os.path.dirname(TargetFile), exist_ok=True)
    shutil.copy2(SourceFile, TargetFile)


 ######   ######## ########    ##     ##    ###    ########    ########  ####  ######  ########
##    ##  ##          ##       ###   ###   ## ##      ##       ##     ##  ##  ##    ##    ##
##        ##          ##       #### ####  ##   ##     ##       ##     ##  ##  ##          ##
##   #### ######      ##       ## ### ## ##     ##    ##       ##     ##  ##  ##          ##
##    ##  ##          ##       ##     ## #########    ##       ##     ##  ##  ##          ##
##    ##  ##          ##       ##     ## ##     ##    ##       ##     ##  ##  ##    ##    ##
 ######   ########    ##       ##     ## ##     ##    ##       ########  ####  ######     ##

def get_material_dict(SOP_Create_Node_Path):
    import hou, voptoolutils

    SOP_Create_Node = hou.node(SOP_Create_Node_Path)
    material_list=[]
    material_path_list=[]
    material_dict={}

    # Define the selection rule for Mesh primitives using a pattern
    mesh_pattern = "%type:Mesh"
    selection_rule = hou.LopSelectionRule(mesh_pattern)
    # Get the paths to all Mesh primitives, passing the LOP node instead of the stage
    mesh_paths = selection_rule.expandedPaths(SOP_Create_Node)
    #mesh_paths = selection_rule.collectionAwarePaths(SOP_Create_Node)

    for mesh in mesh_paths:
        material_path=(str(mesh))
        #path_count=(material_path.count('/'))
        material=(str(mesh).split("/")[-1])
        #material_path='*/'+material
        material_dict[material]=material_path#+material

    return material_dict


 ######  ######## ########    ##     ##    ###    ########    ##       #### ########     ########     ###    ########  ##     ##  ######
##    ## ##          ##       ###   ###   ## ##      ##       ##        ##  ##     ##    ##     ##   ## ##   ##     ## ###   ### ##    ##
##       ##          ##       #### ####  ##   ##     ##       ##        ##  ##     ##    ##     ##  ##   ##  ##     ## #### #### ##
 ######  ######      ##       ## ### ## ##     ##    ##       ##        ##  ########     ########  ##     ## ########  ## ### ##  ######
      ## ##          ##       ##     ## #########    ##       ##        ##  ##     ##    ##        ######### ##   ##   ##     ##       ##
##    ## ##          ##       ##     ## ##     ##    ##       ##        ##  ##     ##    ##        ##     ## ##    ##  ##     ## ##    ##
 ######  ########    ##       ##     ## ##     ##    ##       ######## #### ########     ##        ##     ## ##     ## ##     ##  ######


def set_mat_lib_parms(MatLibPath,SOP_Create_Node_Path,CustomName,material_dict):
    import hou, voptoolutils
    MatLibNode=hou.node(MatLibPath)
    #material_dict=get_material_dict(SOP_Create_Node_Path)
    material_list=MatLibNode.children()
    Nr_Materials=len(MatLibNode.children())
    MatLibNode.setParms({'matpathprefix':CustomName+'_mtl/materials/'}) # SOS add custom name, example: /xiwcfassc_High_mtl/materials/
    MatLibNode.setParms({'materials':Nr_Materials})

    for material in material_list:
        GeoPath = (material_dict[str(material)])
        index=(list(material_dict).index(str(material))+1)
        MatLibNode.setParms({'matnode'+str(index):str(material)})
        MatLibNode.setParms({'matpath'+str(index):str(material)})


 ######   ######## ########    ##     ## ########  ######      ###     ######   ######     ###    ##    ##    ########  ####  ######  ########
##    ##  ##          ##       ###   ### ##       ##    ##    ## ##   ##    ## ##    ##   ## ##   ###   ##    ##     ##  ##  ##    ##    ##
##        ##          ##       #### #### ##       ##         ##   ##  ##       ##        ##   ##  ####  ##    ##     ##  ##  ##          ##
##   #### ######      ##       ## ### ## ######   ##   #### ##     ##  ######  ##       ##     ## ## ## ##    ##     ##  ##  ##          ##
##    ##  ##          ##       ##     ## ##       ##    ##  #########       ## ##       ######### ##  ####    ##     ##  ##  ##          ##
##    ##  ##          ##       ##     ## ##       ##    ##  ##     ## ##    ## ##    ## ##     ## ##   ###    ##     ##  ##  ##    ##    ##
 ######   ########    ##       ##     ## ########  ######   ##     ##  ######   ######  ##     ## ##    ##    ########  ####  ######     ##

def GetMegaScanDict(debug,printdata):
    import hou, os, glob, time, shutil, json

    hou.setUpdateMode(hou.updateMode.Manual)
    HDA = hou.pwd()
    MegaScanDir = (HDA.parm('Source_Directory').eval()+'/').replace("\\","/").replace("//","/")
    UsdTargetDir = (HDA.parm('Target_Directory').eval()+'/').replace("\\","/").replace("//","/")
    ImportFileExtentionList, ExportFileExtentionList = get_extention_list()
    ObjectFileExtention = ImportFileExtentionList[HDA.parm('FileFormat').eval()]

    MegaScanDir_USD = UsdTargetDir
    MegaScanDict_FilePath = MegaScanDir+"MegaScanDebug.json"
    preview_file_detect = '_Preview.png'
    TextureDirSourceAtlas = ''
    TextureDirSourceBillboard = ''
    TextureListAtlas = []
    TextureListBillboard = []
    TargetSubDirNameList = []
    VariantList = []
    LodList = []
    LodListPrevious = []
    LodListComplete = []
    NAMEPrevious = ''
    MegaScanDict = {}
    ObjectSourceDict = {}
    MegaScanDict = {}
    if printdata == True:
        TextLine = '---- Collecting MegaScans Data ----'
        print(f'\n{TextLine}')
    SourceFiles = glob.glob(os.path.join(MegaScanDir, '**', '*.'+ObjectFileExtention), recursive=True)
    for SourceFile in SourceFiles:
        SourceFile = SourceFile.replace('\\','/')
        SourceFileName = SourceFile.split('/')[-1]

        if ObjectFileExtention in SourceFile:
            SourceFileName.split('/')[-1]

            # **************************************************************************
            root_list = []
            if "/Var" in SourceFile:
                SourceFileSubDir = SourceFile.split("/Var")[0]+'/'
                for root, dirs, files in os.walk(SourceFileSubDir ):
                    root_list.append(root.upper().replace('\\','/').split('/')[-1])

                if 'ATLAS' in root_list: # Some SoureFiles have a SubDir '/Var' but don't have the TextureSubDir'/Textures/Atlas/'
                    #NewFile = (SourceFile.split("/Var")[0].split("/")[-1]+"_Var"+SourceFile.split("/Var")[1].split("/")[-1]+"_"+SourceFile.split("_")[-1]).replace("3dplant_plant_","").replace("plants_3d_","")
                    NewFile = SourceFile.split("/Var")[0].split("/")[-1].split('_')[-1]+'_'+SourceFile.split("/")[-1]
                    TextureDirSourceAtlas = SourceFileSubDir+'Textures/Atlas/'
                    TextureDirSourceBillboard = SourceFileSubDir+'Textures/Billboard/'
                    TYPE='PLANT'

                else:
                    NewFile = SourceFile.split("/")[-1]
                    TextureDirSourceAtlas = SourceFileSubDir
                    TextureDirSourceBillboard = False
                    TYPE='OBJ'



            else:
                NewFile = SourceFile.split("/")[-1]
                TextureDirSourceAtlas = SourceFile.replace(NewFile,"")
                TextureDirSourceBillboard = False
                SourceFileSubDir = SourceFile.rsplit("/",1)[0]+'/'
                TYPE='OBJ'


            # **************************************************************************
            #print(f'SourceFile: {SourceFile}   NewFile: {NewFile}')
            TargetSubDirName = NewFile.rsplit('_',1)[0]
            NAME = TargetSubDirName.split('_Var')[0].split('_')[-1]
            LONGNAME = TargetSubDirName.split('_Var')[0]
            NewFileName=NewFile.split('.'+ObjectFileExtention)[0]

            if NAME != NAMEPrevious:
                if printdata == True:
                    print(f'- Found MegaScan Object: {NAME}')
                TargetSubDirNameList = []
                VariantList = []
                LodList = []
                ObjectSourceDict ={}
                HighResObjLOD = ''
                LowResObjLOD = ''

            TargetSubDirNameList.append(TargetSubDirName)
            TargetSubDirNameList = list(dict.fromkeys(TargetSubDirNameList))

            Variant = SourceFileName.split('.'+ObjectFileExtention)[0].rsplit('_',1)[0].split('_')[-1] # SOS now
            VariantList.append(Variant)
            VariantList = list(dict.fromkeys(VariantList))

            LOD = SourceFileName.split('.'+ObjectFileExtention)[0].split('_')[-1]
            LodList.append(LOD)
            LodList = list(dict.fromkeys(LodList))

            NAMEPrevious = NAME
            FBXsourcefile = SourceFile
            FBXtargetfile = MegaScanDir_USD + NAME +'/04_FBX_SourceFiles/'+NewFile

            TextureListAtlas = texture_list_from_TextureDirSource(TextureDirSourceAtlas)
            TextureListBillboard = texture_list_from_TextureDirSource(TextureDirSourceBillboard)

            UsdTargetDir = MegaScanDir_USD+NAME+'/01_USD_Files/'
            TextureDirTargetAtlas = MegaScanDir_USD+NAME+'/02_Textures/Atlas/'
            TextureDirTargetBillboard = MegaScanDir_USD+NAME+'/02_Textures/Billboard/'

            # ******************* Get PreviewSourceFile & PreviewTargetFile *******************

            for root, dirs, files in os.walk(SourceFileSubDir):
                for file in files:
                    if preview_file_detect in file:
                        PreviewSourceFile=root+file
                        PreviewTargetFile = MegaScanDir_USD + NAME +'/03_Preview/'+file
            # *********************************************************************************

            for Variant in VariantList:

                if TYPE == 'PLANT':
                    ObjectSourceSubDir = SourceFile.rsplit('/',2)[0]+'/'
                if TYPE == 'OBJ':
                    ObjectSourceSubDir = SourceFile.rsplit('/',1)[0]+'/'

                if Variant+'_'+LodList[0]+'.'+ObjectFileExtention in SourceFile:
                    #print(f'SourceFileHigh: {SourceFile}')
                    HighResObjLOD = LodList[0]

                # SOS now ***************
                try:
                    LODNr = int(LodList[-1].upper().split('LOD')[-1])
                    FixLOD= LodList[-1].replace(str(LODNr),str(LODNr-1))
                    #print(f'FixLOD: {FixLOD}')
                except:
                    FixLOD = LodList[-1]

                if Variant+'_'+LodList[-1]+'.'+ObjectFileExtention in SourceFile:
                    #print(f'SourceFileLow: {SourceFile}')
                    #LowResObjLOD = SourceFile.replace(LodList[-1]+'.',FixLOD+'.')
                    LowResObjLOD = FixLOD


            MegaScanDict[NAME]={
                                'LONGNAME':LONGNAME,
                                'TYPE':TYPE,
                                'VariantList':VariantList,
                                'LodList':LodList,
                                'TextureDirSourceAtlas':TextureDirSourceAtlas,
                                'TextureListAtlas':TextureListAtlas,
                                'TextureDirSourceBillboard':TextureDirSourceBillboard,
                                'TextureListBillboard':TextureListBillboard,
                                'TextureDirTargetAtlas': TextureDirTargetAtlas,
                                'TextureDirTargetBillboard': TextureDirTargetBillboard,
                                'PreviewSourceFile':PreviewSourceFile,
                                'PreviewTargetFile':PreviewTargetFile,
                                'ObjectSourceSubDir':ObjectSourceSubDir,
                                'HighResObjLOD':HighResObjLOD,
                                'LowResObjLOD':LowResObjLOD,
                                'UsdTargetDir': UsdTargetDir
                            }

    if debug == True:
        write_dict_to_json(MegaScanDict,MegaScanDict_FilePath)
    if printdata == True:
        TextLine = '---- Collecting MegaScans Data Finished ----'
        print(f'{TextLine}\n')
    return MegaScanDict
    hou.setUpdateMode(hou.updateMode.AutoUpdate) # End slow speed fix


 ######   #######  ########  ##    ##       ###    ##       ##          ######## ######## ##     ## ########     #######     ########    ###    ########   ######      ########  #### ########
##    ## ##     ## ##     ##  ##  ##       ## ##   ##       ##             ##    ##        ##   ##     ##       ##     ##       ##      ## ##   ##     ## ##    ##     ##     ##  ##  ##     ##
##       ##     ## ##     ##   ####       ##   ##  ##       ##             ##    ##         ## ##      ##              ##       ##     ##   ##  ##     ## ##           ##     ##  ##  ##     ##
##       ##     ## ########     ##       ##     ## ##       ##             ##    ######      ###       ##        #######        ##    ##     ## ########  ##   ####    ##     ##  ##  ########
##       ##     ## ##           ##       ######### ##       ##             ##    ##         ## ##      ##       ##              ##    ######### ##   ##   ##    ##     ##     ##  ##  ##   ##
##    ## ##     ## ##           ##       ##     ## ##       ##             ##    ##        ##   ##     ##       ##              ##    ##     ## ##    ##  ##    ##     ##     ##  ##  ##    ##
 ######   #######  ##           ##       ##     ## ######## ########       ##    ######## ##     ##    ##       #########       ##    ##     ## ##     ##  ######      ########  #### ##     ##

def CopyAllImagesToTargetDir():
    import hou
    MegaScanDict = GetMegaScanDict(False,False)
    LengthDict = len(MegaScanDict)
    Count = 1
    print('\n'+'-'*5+' Start copy MegaScan Source Texture to USD '+'-'*5)
    for NAME in MegaScanDict:

        PreviewSourceFile = MegaScanDict[NAME]['PreviewSourceFile']
        PreviewTargetFile = MegaScanDict[NAME]['PreviewTargetFile']
        copy_source_to_target(PreviewSourceFile, PreviewTargetFile)

        for TextureAtlas in (MegaScanDict[NAME]['TextureListAtlas']):
            TextureAtlasSource = MegaScanDict[NAME]['TextureDirSourceAtlas']+TextureAtlas
            TextureAtlasTarget = MegaScanDict[NAME]['TextureDirTargetAtlas']+TextureAtlas
            copy_source_to_target(TextureAtlasSource, TextureAtlasTarget)
        '''
        TextureDirSourceBillboard = (MegaScanDict[NAME]['TextureDirSourceBillboard'])
        if TextureDirSourceBillboard != False:
            for TextureBillboard in (MegaScanDict[NAME]['TextureListBillboard']):
                TextureBillboardSource = MegaScanDict[NAME]['TextureDirSourceBillboard']+TextureBillboard
                TextureBillboardTarget = MegaScanDict[NAME]['TextureDirTargetBillboard']+TextureBillboard
                copy_source_to_target(TextureBillboardSource, TextureBillboardTarget)
        '''
        CopyProgress = str(int(100*Count/LengthDict))
        Space = '.'*(28-len(NAME)-len(CopyProgress))
        print(f' Copy Images from "{NAME}": {Space} {CopyProgress}%')
        Count += 1
    print('-'*54+'\n')


 ######     ###    ##     ## ########       ###    ##       ##          ##     ##  ######  ########     ######## #### ##       ########  ######
##    ##   ## ##   ##     ## ##            ## ##   ##       ##          ##     ## ##    ## ##     ##    ##        ##  ##       ##       ##    ##
##        ##   ##  ##     ## ##           ##   ##  ##       ##          ##     ## ##       ##     ##    ##        ##  ##       ##       ##
 ######  ##     ## ##     ## ######      ##     ## ##       ##          ##     ##  ######  ##     ##    ######    ##  ##       ######    ######
      ## #########  ##   ##  ##          ######### ##       ##          ##     ##       ## ##     ##    ##        ##  ##       ##             ##
##    ## ##     ##   ## ##   ##          ##     ## ##       ##          ##     ## ##    ## ##     ##    ##        ##  ##       ##       ##    ##
 ######  ##     ##    ###    ########    ##     ## ######## ########     #######   ######  ########     ##       #### ######## ########  ######

def SaveAllUsdFiles(ExportEnabled):
    import hou
    hou.setUpdateMode(hou.updateMode.Manual)
    if ExportEnabled == True:
        print('\n'+'-'*5+' Start Saving all USD Files '+'-'*5)
    else:
        print('\n'+'-'*5+' Updating All USD Settings '+'-'*5)



    HDA = hou.pwd()
    ImportFileExtentionList, ExportFileExtentionList = get_extention_list()

    FileNameExtention = ExportFileExtentionList[HDA.parm('FileNameExtention').eval()]
    PayloadExtention = ExportFileExtentionList[HDA.parm('PayloadExtention').eval()]
    GeometryExtention = ExportFileExtentionList[HDA.parm('GeometryExtention').eval()]
    MaterialLayer = ExportFileExtentionList[HDA.parm('MaterialLayer').eval()]
    ExtraLayerExtention = ExportFileExtentionList[HDA.parm('ExtraLayerExtention').eval()]

    CompOutConfig =     {
                            'CompOut':   {'NODE_TYPE':'componentoutput','NODE_COLOR':False,'TARGET_NODE_DICT':False,'PRE_EXIST':True,'PTU_INPUT_FLAG':True,'ACTIVATE':True,
                        }}

    HDA = hou.pwd()
    MegaScanDict = GetMegaScanDict(False,False)
    AssetsNr = len(MegaScanDict)
    Count = 1

    for NAME in MegaScanDict:
        try:
            filename = NAME+'.'+FileNameExtention
            lopoutput = MegaScanDict[NAME]['UsdTargetDir']+filename
            payloadlayer = 'payload.'+PayloadExtention
            geolayer = 'geo.'+GeometryExtention
            mtllayer = 'mtl.'+MaterialLayer
            extralayer = 'extra.'+ExtraLayerExtention
            variantdefaultgeo = MegaScanDict[NAME]['VariantList'][0]

            CompOutNode = hou.node(HDA.parent().path()+'/MegaScanAssets/'+NAME+'/CompOut/')
            CompOutNode.setParms({
                                    'name':NAME,
                                    'filename':filename,
                                    'lopoutput':lopoutput,
                                    'payloadlayer':payloadlayer,
                                    'geolayer':geolayer,
                                    'mtllayer':mtllayer,
                                    'extralayer':extralayer,
                                    'localize':False,
                                    'variantlayers':True,
                                    'setdefaultvariants':True,
                                    'variantdefaultgeo':variantdefaultgeo
                                })

            if ExportEnabled == True:
                print(f' Saving USD File: {Count}/{AssetsNr} of {NAME}')
                CompOutNode.parm('execute').pressButton()
                Count += 1
            else:
                print(f' Update USD Settings: {Count}/{AssetsNr} of {NAME}')
                Count += 1
        except:
            print(f' *** There is an issue saving USD File: {Count}/{AssetsNr} of {NAME} ***')
            Count += 1

    if ExportEnabled == True:
        print('-'*5+' Saving USD Files is Complete '+'-'*5+'\n')
    else:
        print('\n'+'-'*5+' Updating USD Settings Complete'+'-'*5)
    hou.setUpdateMode(hou.updateMode.AutoUpdate) # End slow speed fix


 ######  ##     ## ########  ######  ##    ##     ######  ##     ## ########  ##    ## ######## ######## ##      ##  #######  ########  ##    ##
##    ## ##     ## ##       ##    ## ##   ##     ##    ## ##     ## ##     ## ###   ## ##          ##    ##  ##  ## ##     ## ##     ## ##   ##
##       ##     ## ##       ##       ##  ##      ##       ##     ## ##     ## ####  ## ##          ##    ##  ##  ## ##     ## ##     ## ##  ##
##       ######### ######   ##       #####        ######  ##     ## ########  ## ## ## ######      ##    ##  ##  ## ##     ## ########  #####
##       ##     ## ##       ##       ##  ##            ## ##     ## ##     ## ##  #### ##          ##    ##  ##  ## ##     ## ##   ##   ##  ##
##    ## ##     ## ##       ##    ## ##   ##     ##    ## ##     ## ##     ## ##   ### ##          ##    ##  ##  ## ##     ## ##    ##  ##   ##
 ######  ##     ## ########  ######  ##    ##     ######   #######  ########  ##    ## ########    ##     ###  ###   #######  ##     ## ##    ##

def CheckSubNetwork():
    import hou
    print('\n'+'-'*5+' Start Checking for errors in MegaScanss Assets '+'-'*5)
    HDA = hou.pwd()
    node_color = GetColorValues()
    MegaScanAssetsNode = hou.node(HDA.path().rsplit('/',1)[0]+'/MegaScanAssets/')
    SubNetworkList = MegaScanAssetsNode.children()
    CheckForGeo = False
    SubNetworkPathPrevious = ''

    for SubNetwork in SubNetworkList:
        SubNetChildLength = len(SubNetwork.children())
        if SubNetChildLength < 6:
            SubNetwork.setColor(hou.Color(node_color['red']))
            print(f'There is an issue with SubNetWork: {SubNetwork}')

        ChildList = SubNetwork.children()
        for Child in ChildList:
            if '<hou.OpNodeType for Lop componentgeometry>' in str(Child.type()):
                ChildPath = Child.path()
                SubNetworkPath = SubNetwork.path()
                if SubNetworkPath != SubNetworkPathPrevious:
                    #print(f'Checking for errors in : {SubNetworkPath}')
                    SubNetworkPathPrevious = SubNetworkPath
                if not has_mesh_geometry(Child):
                    SubNetwork.setColor(hou.Color(node_color['red']))
                    Child.setColor(hou.Color(node_color['red']))
                    ChildPath = Child.path()
                    print(f'There is an issue with SubNetWork: {SubNetwork}  No Geometry in ComponentGeometry: {Child}')
                else:
                    SubNetwork.setColor(hou.Color(node_color['lightblue']))
                    Child.setColor(hou.Color(node_color['white']))

    print('-'*5+' Finished Checking for errors in MegaScanss Assets '+'-'*5)

def has_mesh_geometry(node):
    # Get the USD stage from the node
    stage = node.stage()

    if stage:
        # Traverse the stage and check for any Mesh primitives
        for prim in stage.Traverse():
            if prim.GetTypeName() == "Mesh":
                return True
    else:
        return False


def CheckTexturesInMatLibNodes():
    import hou, os
    print('\n'+'-'*5+' Start Checking for Texture Conflicts in MatLib Nodes '+'-'*5)
    HDA = hou.pwd()
    node_color = GetColorValues()
    MegaScanAssetsNode = hou.node(HDA.path().rsplit('/',1)[0]+'/MegaScanAssets/')
    SubNetworkList = MegaScanAssetsNode.children()
    CheckForGeo = False
    SubNetworkPathPrevious = ''

    for SubNetwork in SubNetworkList:
        SubNetworkPath = SubNetwork.path()
        #print(f'Checking for errors in : {SubNetworkPath}')
        ChildrensList = SubNetwork.allSubChildren()
        for child in ChildrensList:
            if '<hou.OpNodeType for Vop mtlximage>' in str(child.type()):
                file = child.parm('file').eval()
                if not os.path.isfile(file):
                    print(f'There is an issue with the SubNetwork: {SubNetworkPath}\nThe next Texture file does not exist: {file}\nInside the MtlxImage Node: {child.path()}')
                    SubNetwork.setColor(hou.Color(node_color['red']))
                else:
                    SubNetwork.setColor(hou.Color(node_color['lightblue']))



    print('-'*5+' Finished Checking for Texture Conflicts in MatLib Nodes '+'-'*5)


 ######  ########    ###    ########  ########       ##     ##    ###    #### ##    ##
##    ##    ##      ## ##   ##     ##    ##          ###   ###   ## ##    ##  ###   ##
##          ##     ##   ##  ##     ##    ##          #### ####  ##   ##   ##  ####  ##
 ######     ##    ##     ## ########     ##          ## ### ## ##     ##  ##  ## ## ##
      ##    ##    ######### ##   ##      ##          ##     ## #########  ##  ##  ####
##    ##    ##    ##     ## ##    ##     ##          ##     ## ##     ##  ##  ##   ###
 ######     ##    ##     ## ##     ##    ##          ##     ## ##     ## #### ##    ##

def BuildSolarisNodes():
    import hou

    hou.setUpdateMode(hou.updateMode.Manual)    # This fixes the slow speed of cooking while the python script adds all the nodes

    HDA = hou.pwd()
    HDA.setParms({'batch_convert_finished':False})
    ImportFileExtentionList, ExportFileExtentionList = get_extention_list()

    FileNameExtention = ExportFileExtentionList[HDA.parm('FileNameExtention').eval()]
    PayloadExtention = ExportFileExtentionList[HDA.parm('PayloadExtention').eval()]
    GeometryExtention = ExportFileExtentionList[HDA.parm('GeometryExtention').eval()]
    MaterialLayer = ExportFileExtentionList[HDA.parm('MaterialLayer').eval()]
    ExtraLayerExtention = ExportFileExtentionList[HDA.parm('ExtraLayerExtention').eval()]
    ObjectFileExtention = ImportFileExtentionList[HDA.parm('FileFormat').eval()]

    CopyAllImagesEnable = HDA.parm('CopyAllImagesEnable').eval()
    scale = HDA.parm('scale').eval()
    DisplacementScale = HDA.parm('DisplacementScale').eval()

    MegaScanDict = GetMegaScanDict(False,True)
    node_color = GetColorValues()

    if CopyAllImagesEnable == True:
        CopyAllImagesToTargetDir()

    # ******************************* Build Layer0 *******************************
    Config = {'MegaScanAssets':{'NODE_TYPE':'subnet','NODE_COLOR':node_color['green'],'TARGET_NODE_DICT':False,'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}}}
    MegaScanAssetsNodePath = HDA.parent().path()+'/MegaScanAssets/'
    MegaScanAssetsNode = hou.node(MegaScanAssetsNodePath)

    if not MegaScanAssetsNode:
        print(f'Adding MegaScanAssetsNode: {MegaScanAssetsNodePath}\n')
        CreateNetwork(HDA.parent().path(),Config,False,HDA.position())
        OutPutNode = hou.node(HDA.parent().path()+'/MegaScanAssets/output0/')
        OutPutNode.destroy()

    # ******************************* Build Layer1 *******************************
    x_steps = 4     # X Distance between each node
    y_steps = 5     # Y Distance between each node
    columns = 6     # Max amount of columns
    w=-1            # Needed to calculate the Y position
    i=0             # increment counter

    for NAME in MegaScanDict:

        Config = {NAME:{'NODE_TYPE':'subnet','NODE_COLOR':node_color['lightblue'],'TARGET_NODE_DICT':False,'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}}}

        # *** Calculate the ankerpoints X and Y ***
        x=(i%columns)*x_steps
        if x == 0:
            w=w+1
        y=(w)*-y_steps
        AnkerPoint=(x,y)
        i+=1
        # *****************************************

        CreateNetwork(MegaScanAssetsNodePath,Config,False,AnkerPoint)
        print(f'- Adding SubNetWorkNode: {NAME}  ')
    place_preview_images()

    # ******************************* Build Layer2 *******************************
    MegaScanAssetsNode = hou.node(MegaScanAssetsNodePath)

    for Child in MegaScanAssetsNode.children():
        OutPutNode = hou.node(Child.path()+'/output0/')
        if OutPutNode:
            OutPutNode.destroy()
        NAME=Child.name()
        matpathprefix = '/ASSET/mtl/'
        filename = NAME+'.'+FileNameExtention
        lopoutput = MegaScanDict[NAME]['UsdTargetDir']+filename
        payloadlayer = 'payload.'+PayloadExtention
        geolayer = 'geo.'+GeometryExtention
        mtllayer = 'mtl.'+MaterialLayer
        extralayer = 'extra.'+ExtraLayerExtention
        variantdefaultgeo = MegaScanDict[NAME]['VariantList'][0]

        Config =    {
                        NAME+'_OUT':{'NODE_TYPE':'output','NODE_COLOR':node_color['default'],'TARGET_NODE_DICT':False,'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}},
                        'CompOut':   {'NODE_TYPE':'componentoutput','NODE_COLOR':node_color['green'],'TARGET_NODE_DICT':{NAME+'_OUT':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,
                        'PARAMETER':{
                                        'name':NAME,
                                        'filename':filename,
                                        'lopoutput':lopoutput,
                                        'payloadlayer':payloadlayer,
                                        'geolayer':geolayer,
                                        'mtllayer':mtllayer,
                                        'extralayer':extralayer,
                                        'localize':False,
                                        'variantlayers':True,
                                        'setdefaultvariants':True,
                                        'variantdefaultgeo':variantdefaultgeo
                                    }
                                },

                        'CompMat':{'NODE_TYPE':'componentmaterial','NODE_COLOR':node_color['default'],'TARGET_NODE_DICT':{'CompOut':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}},
                        'MatLib':{'NODE_TYPE':'materiallibrary','NODE_COLOR':node_color['orange'],'TARGET_NODE_DICT':{'CompMat':'input2'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'matpathprefix':matpathprefix,'matnode1':NAME,'matpath1':NAME}},
                        'CompVar':{'NODE_TYPE':'componentgeometryvariants','NODE_COLOR':node_color['default'],'TARGET_NODE_DICT':{'CompMat':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}}
                    }

        NetWorkPath = Child.path()+'/'
        CreateNetwork(NetWorkPath,Config,True,(0,0))

        # *********************** Build Layer3 in MatLib ***********************
        MatLibNodePath = NetWorkPath+'MatLib'
        material_list = [NAME]
        karma_materials_list = CreateKarmaMatNetwork(MatLibNodePath,material_list)
        MaterialNodePath = NetWorkPath+'MatLib/'+NAME+'/'

        MtlxPreConfig = {
                            'mtlxdisplacement':{'NODE_TYPE':'mtlxdisplacement','NODE_COLOR':node_color['lightgreen'],'TARGET_NODE_DICT':False,'PRE_EXIST':True,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'scale':DisplacementScale}},
                            'MtxlNormalMap':{'NODE_TYPE':'mtlxnormalmap','NODE_COLOR':node_color['lightblue'],'TARGET_NODE_DICT':{'mtlxstandard_surface':'normal'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'scale':DisplacementScale}},
                        }

        CreateNetwork(MaterialNodePath,MtlxPreConfig,True,(0,0))

        for TextureImageName in MegaScanDict[NAME]['TextureListAtlas']:
            MtlxImageNodeName = TextureImageName.split('.')[0].split('_')[-1].replace('LOD0','Normal')
            #print(f'NAME: {NAME}   MtlxImageNodeName: {MtlxImageNodeName}')
            TextureFile = MegaScanDict[NAME]['TextureDirTargetAtlas']+TextureImageName

            # SOS look at connections in ParmsDict
            ParmsDict = {
                                'AO':{'signature':'default','TARGET_NODE_DICT':{'mtlxstandard_surface':'base'},'NodeColor':'orange'},
                                'Albedo':{'signature':'color3','TARGET_NODE_DICT':{'mtlxstandard_surface':'base_color'},'NodeColor':'orange'},
                                'Gloss':{'signature':'default','TARGET_NODE_DICT':False,'NodeColor':'red'},
                                'Specular':{'signature':'default','TARGET_NODE_DICT':{'mtlxstandard_surface':'specular'},'NodeColor':'orange'},
                                'Metalness':{'signature':'default','TARGET_NODE_DICT':{'mtlxstandard_surface':'metalness'},'NodeColor':'orange'},
                                'Roughness':{'signature':'default','TARGET_NODE_DICT':{'mtlxstandard_surface':'specular_roughness'},'NodeColor':'orange'},
                                'Bump':{'signature':'default','TARGET_NODE_DICT':False,'NodeColor':'red'},
                                'Opacity':{'signature':'default','TARGET_NODE_DICT':{'mtlxstandard_surface':'opacity'},'NodeColor':'orange'},
                                'Normal':{'signature':'vector3','TARGET_NODE_DICT':{'MtxlNormalMap':'in'},'NodeColor':'lightblue'},
                                'Displacement':{'signature':'default','TARGET_NODE_DICT':{'mtlxdisplacement':'displacement'},'NodeColor':'lightgreen'},
                                'Translucency':{'signature':'default','TARGET_NODE_DICT':{'mtlxstandard_surface':'thin_walled'},'NodeColor':'orange'},
                                'Transmission':{'signature':'default','TARGET_NODE_DICT':False,'NodeColor':'red'},
                                'Fuzz':{'signature':'default','TARGET_NODE_DICT':False,'NodeColor':'red'}
                        }

            signature = ParmsDict[MtlxImageNodeName]['signature']
            TARGET_NODE_DICT = ParmsDict[MtlxImageNodeName]['TARGET_NODE_DICT']
            NodeColor = ParmsDict[MtlxImageNodeName]['NodeColor']

            MtlxConfig =    {
                                MtlxImageNodeName:{'NODE_TYPE':'mtlximage','NODE_COLOR':node_color[NodeColor],'TARGET_NODE_DICT':TARGET_NODE_DICT,'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'file':TextureFile,'signature':signature}}
                            }
            CreateNetwork(MaterialNodePath,MtlxConfig,True,(0,0))

        # *********************** Build Layer3 in Component Geometry ***********************
        InputIndex = 1
        for Variant in MegaScanDict[NAME]['VariantList']:
            # SOS now xxx
            Config = {
                        Variant:{'NODE_TYPE':'componentgeometry','NODE_COLOR':node_color['default'],'TARGET_NODE_DICT':{'CompVar':'input'+str(InputIndex)},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}}
            }

            CreateNetwork(NetWorkPath,Config,True,(0,0))
            InputIndex += 1

            CheckType =  MegaScanDict[NAME]['TYPE']

            if CheckType == 'PLANT':
                File_HR = MegaScanDict[NAME]['ObjectSourceSubDir']+Variant+'/'+Variant+'_'+MegaScanDict[NAME]['HighResObjLOD']+'.'+ObjectFileExtention
                File_LR = MegaScanDict[NAME]['ObjectSourceSubDir']+Variant+'/'+Variant+'_'+MegaScanDict[NAME]['LowResObjLOD']+'.'+ObjectFileExtention
                snippet = f'''//This VEX code seams to work best for MegaScan Plants.
    s@name = '{NAME}';
    removeattrib(0, "prim", "shop_materialpath");
    removeattrib(0, "prim", "fbx_node_path");
    removeattrib(0, "prim", "class");
'''

            if CheckType == 'OBJ': # SOS now
                File_HR = MegaScanDict[NAME]['ObjectSourceSubDir']+MegaScanDict[NAME]['LONGNAME']+'_'+MegaScanDict[NAME]['HighResObjLOD']+'.'+ObjectFileExtention
                File_LR = MegaScanDict[NAME]['ObjectSourceSubDir']+MegaScanDict[NAME]['LONGNAME']+'_'+MegaScanDict[NAME]['LowResObjLOD']+'.'+ObjectFileExtention

                snippet =   '''//This VEX code seams to work best for MegaScan Objects.
    s@name = split((split(s@name,"/")[-1]),"_")[4];
    removeattrib(0, "prim", "shop_materialpath");
    removeattrib(0, "prim", "fbx_node_path");
    removeattrib(0, "prim", "class");
'''

            ConfigVar =    {
                            'default':{'NODE_TYPE':'output','NODE_COLOR':False,'TARGET_NODE_DICT':False,'PRE_EXIST':True,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}},
                            NAME+'_HR_VEX':{'NODE_TYPE':'attribwrangle','NODE_COLOR':node_color['green'],'TARGET_NODE_DICT':{'default':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'snippet':snippet,'class':1}},
                            NAME+'_HR_TX':{'NODE_TYPE':'xform','NODE_COLOR':node_color['yellow'],'TARGET_NODE_DICT':{NAME+'_HR_VEX':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'scale':scale}},
                            NAME+'_HR_Import':{'NODE_TYPE':'file','NODE_COLOR':node_color['default'],'TARGET_NODE_DICT':{NAME+'_HR_TX':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'file':File_HR}},

                            'proxy':{'NODE_TYPE':'output','NODE_COLOR':False,'TARGET_NODE_DICT':False,'PRE_EXIST':True,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{}},
                            NAME+'_LR_VEX':{'NODE_TYPE':'attribwrangle','NODE_COLOR':node_color['green'],'TARGET_NODE_DICT':{'proxy':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'snippet':snippet,'class':1}},
                            NAME+'_LR_TX':{'NODE_TYPE':'xform','NODE_COLOR':node_color['yellow'],'TARGET_NODE_DICT':{NAME+'_LR_VEX':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'scale':scale}},
                            NAME+'_LR_Import':{'NODE_TYPE':'file','NODE_COLOR':node_color['default'],'TARGET_NODE_DICT':{NAME+'_LR_TX':'input1'},'PRE_EXIST':False,'PTU_INPUT_FLAG':True,'ACTIVATE':True,'PARAMETER':{'file':File_LR}}
                        }

            VariantPath = NetWorkPath+Variant+'/sopnet/geo/'

            if not (File_HR or File_LR):
                SubNetworkNode = hou.node(NetWorkPath)
                VarNode = hou.node(NetWorkPath+Variant+'/')
                SubNetworkNode.setColor(hou.Color(node_color['red']))
                VarNode.setColor(hou.Color(node_color['red']))

            CreateNetwork(VariantPath,ConfigVar,True,(0,0))

    #CheckSubNetwork()
    HDA.setParms({'batch_convert_finished':True})
    print('\n'+'-'*5+' MegaScans Build Finished '+'-'*5)
    hou.setUpdateMode(hou.updateMode.AutoUpdate) # End slow speed fix







