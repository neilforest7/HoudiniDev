
import hou
import toolutils

renderobjnames = ["geo"]
rendercamnames = ["cam"]

targets = hou.selectedNodes()
targets = [node for node in targets if node.type().name() in renderobjnames + rendercamnames]
if not targets:
    scene_viewer = toolutils.sceneViewer()
    targets = scene_viewer.selectObjects(
                  prompt = toolutils.selectionPrompt(hou.objNodeTypeCategory()),
                  allowed_types = renderobjnames + rendercamnames,
                  allow_multisel = True)

rfhtree = hou.getenv("RFHTREE")

for target in targets:

    if target.type().name() in renderobjnames:
        path = rfhtree + "/3.7/19.5.569/soho/parameters/geoparms.ds"
    elif target.type().name() in rendercamnames:
        path = rfhtree + "/3.7/19.5.569/soho/parameters/camparms.ds"
    else:
        print("break1")
        break

    grp = target.parmTemplateGroup()
    spareparms = hou.ParmTemplateGroup()

    lastfolder = None
    for e in reversed(grp.entries()):
        if isinstance(e, hou.FolderParmTemplate):
            lastfolder = e
            print("break2")
            break
    
    with open(path) as file:
        ds = file.read()
        spareparms.setToDialogScript(ds)
        print("=========ds read=========")
        
    for template in spareparms.parmTemplates():
        if lastfolder:
            grp.insertAfter(lastfolder, template)
            print("=======insertAfter========")
        else:
            grp.append(template)
            print("=======append========")

    try:
        target.parmsInFolder(("RenderMan",))
        print("=========parmsInFolder=========")
    except:
        target.setParmTemplateGroup(grp)
        print("=========setParmTemplateGroup=========")

    if target.type().name() in renderobjnames:
        hou.hscript("opproperty %s prman25geo *" % target.path())
        print("=========prman25geo=========")
    elif target.type().name() in rendercamnames:
        hou.hscript("opproperty %s prman25cam *" % target.path())
        print("=========prman25cam=========")