import sys
import hou
subnets_of_nodes = []

def SpeedTreePostAction(node):
    sop_path = node.parm("sop_path").eval()
    sopmat_path = node.parm("sopmat_path").eval()
    matnet_path = node.parm("matnet_path").eval()
    treename = node.parm("treename").eval()

    if not sop_path or not treename or not sopmat_path or not matnet_path:
        print("Not Enough Paths Filled On Parameter")
        updated_node_color = hou.Color((0,0,0))
        node.setColor(updated_node_color)
        sys.exit(0)
    else:
        sopmat_node = hou.node(sopmat_path)
        geo_path = hou.node(sop_path).parent().path()

        xformnode = hou.node(geo_path).createNode("xform", run_init_scripts=True)
        outputnode = hou.node(geo_path).createNode("output", run_init_scripts=True)

        xformnode.setInput(0,sopmat_node)
        outputnode.setInput(0,xformnode)

        do_rotate = node.parm("rotate_to_y_up").eval()
        if do_rotate:
            xformnode.parm("rx").set(90)

        LopBuilder(sourcesop=outputnode.path(), sourcematlib=matnet_path, treename=treename)

        updated_node_color = hou.Color((0.31, 0.649, 0.345))
        node.setColor(updated_node_color)


def LopBuilder(sourcesop, sourcematlib, treename):
    print("-----------------------------------START SCRIPT-------------------------------------")
    try:
        pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)

        if not isinstance(pane, hou.NetworkEditor):
            pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
            if pane is None:
                hou.ui.displayMessage(
                    'Cannot create node: cannot find any network pane')
                sys.exit(0)

        pane.cd("/stage")
        pane_node = pane.pwd()
        child_type = pane_node.childTypeCategory().nodeTypes()

        if 'componentmaterial' not in child_type:
            hou.ui.displayMessage('Cannot create node: incompatible pane network type, should be in /stage network')
            sys.exit(0)

        # First clear the node selection
        pane_node.setSelected(False, True)
        # Store current view
        screenBound = pane.visibleBounds()
        screencenter = screenBound.center()-screenBound.size()*0.25

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
        lopcomoutput.parm("lopoutput").set("$JOB/04_Assets/USD/`chs('name')`/`chs('filename')`")

        lopcommat.setInput(1, lopmatlibrary)
        lopcommat.setInput(0, lopcomgeo)
        lopcomoutput.setInput(0, lopcommat)
        placeNicely(screencenter, lopcommat, lopcomgeo, lopmatlibrary, lopcomoutput)

        orig_matnetwork = hou.node(sourcematlib)
        if orig_matnetwork:
            c = orig_matnetwork.children()
            if c[0].type().name() == 'SpeedTreePrincipled':
                hou.copyNodesTo(c, lopmatlibrary)

        stage = lopcommat.stage()
        geomdict = {}
        matdict = {}

        for pt in stage.TraverseAll():
            if pt.GetTypeName() == "GeomSubset":
                if pt.GetParent().GetParent().GetName() == "render":
                    primname = pt.GetName()[:-10]  # remove "_Mat_group"
                    primpath = pt.GetPath()
                    primpath = str(primpath).replace('/render/', '/*/')  # replace "render" with wildcard"*"
                    print("GeomSubset:" + primname)
                    print("GeomSubsetPath:" + str(primpath))
                    geomdict[primname] = primpath
            if pt.GetTypeName() == "Material":
                matname = pt.GetName()[:-4]  # remove "_Mat"
                matpath = pt.GetPath()
                print("Material:" + matname)
                print("MaterialPath:" + str(matpath))
                matdict[matname] = matpath

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

        # set the current node using the node object
        pane.setCurrentNode(lopcomoutput)
        lopcommat.setDisplayFlag(True)

    except:
        print(sys.exc_info())
        print("LOPBUILDER ERROR: Failed to import to lop")

    print("------------------------------END SCRIPT------------------------------------")

def placeNicely(screencenter, *args):
    for node in args:
        node.move(screencenter)
        subnets_of_nodes.append(node)
    hou.node('/stage').layoutChildren(items=subnets_of_nodes, horizontal_spacing=2.0, vertical_spacing=-1.0)



