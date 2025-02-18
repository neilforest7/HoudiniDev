import sys
import toolutils
import hou

matlib = "/obj/Broadleaf_var1/Materials"
sop = "/obj/Broadleaf_var1/Broadleaf_var1/output0"
treenametemp = "Broadleaf_var1"


def LopBuilder(sourcesop, sourcematlib, treename):
    print("---------------------------------------------------START "
          "SCRIPT--------------------------------------------------------")
    # TODO: import sourcematlib/sourcesop path from hda
    # TODO: safty check (adding error catcher?)
    # TODO: set tree name in componentoutput node
    # TODO: adding transform/pack/output to sop sub directory
    # TODO: autoexpand relative path to absolute in LOADSPEEDTREES funtion

    pane = toolutils.activePane(kwargs)

    if not isinstance(pane, hou.NetworkEditor):
        pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if pane is None:
            hou.ui.displayMessage(
                'Cannot create node: cannot find any network pane')
            sys.exit(0)

    pane_node = pane.pwd()
    child_type = pane_node.childTypeCategory().nodeTypes()

    if 'componentmaterial' not in child_type:
        hou.ui.displayMessage('Cannot create node: incompatible pane network type, should be in /stage network')
        sys.exit(0)

    # First clear the node selection
    pane_node.setSelected(False, True)
    # Store current view
    screenBound = pane.visibleBounds()
    screencenter = screenBound.center()

    h_path = pane_node.path()

    lopmatlibrary = hou.node(h_path).createNode("materiallibrary", run_init_scripts=True)
    lopcommat = hou.node(h_path).createNode("componentmaterial", run_init_scripts=True)
    lopcomgeo = hou.node(h_path).createNode("componentgeometry", run_init_scripts=True)
    lopcomoutput = hou.node(h_path).createNode("componentoutput", run_init_scripts=True)

    lopcomgeo.parm("sourceinput").set(2)
    lopcomgeo.parm("sourcesop").set(sourcesop)
    lopcomgeo.parm("sourcesopproxy").set(sourcesop)
    lopmatlibrary.parm("matpathprefix").set("/ASSET/mtl/")
    lopcomgeo.parm("subsetgroups").set("*")
    lopcomoutput.parm("rootprim").set("/" + str(treename))

    lopcommat.setInput(1, lopmatlibrary)
    lopcommat.setInput(0, lopcomgeo)
    lopcomoutput.setInput(0, lopcommat)
    placeNicely(screencenter, lopcommat, lopcomgeo, lopmatlibrary, lopcomoutput)

    orig_matnetwork = hou.node(sourcematlib)
    print(orig_matnetwork)
    if orig_matnetwork:
        c = orig_matnetwork.children()
        if c[0].type().name() == 'SpeedTreePrincipled':
            hou.copyNodesTo(c, lopmatlibrary)

    stage = lopcommat.stage()

    geomdict = {}
    matdict = {}

    for p in stage.TraverseAll():
        if p.GetTypeName() == "GeomSubset":
            if p.GetParent().GetParent().GetName() == "render":
                primname = p.GetName()[:-10]  # remove "_Mat_group"
                primpath = p.GetPath()
                primpath = str(primpath).replace('/render/', '/*/')  # replace "render" with wildcard"*"
                print("GeomSubset:" + primname)
                print("GeomSubsetPath:" + str(primpath))
                geomdict[primname] = primpath
        if p.GetTypeName() == "Material":
            matname = p.GetName()[:-4]  # remove "_Mat"
            matpath = p.GetPath()
            print("Material:" + matname)
            print("MaterialPath:" + str(matpath))
            matdict[matname] = matpath

    # print(type(lopcommat.parm("nummaterials")))
    # print("is multiparm :" + str(lopcommat.parm("nummaterials").isMultiParmInstance()))
    # print("is multiparmparent :" + str(lopcommat.parm("nummaterials").isMultiParmParent()))

    for g in geomdict:
        index = int(lopcommat.parm('nummaterials').evalAsInt())
        lopcommat.parm('nummaterials').insertMultiParmInstance(index)
        print("current index = " + str(index))
        parm_name = 'primpattern' + str(index)
        parm2_name = 'matspecpath' + str(index)
        lopcommat.parm(parm_name).set(str(geomdict.get(g)))
        lopcommat.parm(parm2_name).set(str(matdict.get(g)))

    # remove default parm at the end index
    n = int(lopcommat.parm('nummaterials').evalAsInt())
    lopcommat.parm('nummaterials').removeMultiParmInstance(n - 1)

    # Set the current node using the node object
    pane.setCurrentNode(lopcomoutput)
    lopcommat.setDisplayFlag(True)
    # center = lopcomoutput.position()
    # centerNetworkEditor(pane, center)


# def centerNetworkEditor(editor, center):
#     bounds = editor.visibleBounds()
#     bounds.translate(center - bounds.center())
#     editor.setVisibleBounds(bounds)

subnets_of_nodes = []


def placeNicely(screencenter, *args):
    for node in args:
        node.move(screencenter)
        subnets_of_nodes.append(node)
    hou.node('/stage').layoutChildren(items=subnets_of_nodes, horizontal_spacing=2.0, vertical_spacing=-1.0)

    print("---------------------------------------------------END "
          "SCRIPT--------------------------------------------------------")


LopBuilder(sourcesop=sop, sourcematlib=matlib, treename=treenametemp)
