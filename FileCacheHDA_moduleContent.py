def setRange(kwargs):

    node = kwargs['node']
    
    parm = kwargs['parm']
    r1 = node.parm("f1")
    r2 = node.parm("f2")
    r3 = node.parm("f3")   
    ss = node.parm("substeps")
        
    if parm.evalAsString() == "fstartend":
        r1.deleteAllKeyframes()
        r2.deleteAllKeyframes()
        r1.setExpression('$FSTART')
        r2.setExpression('$FEND')
    elif parm.evalAsString() == "rfstartend":
        r1.deleteAllKeyframes()
        r2.deleteAllKeyframes()
        r1.setExpression('$RFSTART')
        r2.setExpression('$RFEND')        
    elif parm.evalAsString() == "nosubsteps":
        r3.deleteAllKeyframes()
        r3.set(1)
        node.parm("substeps").set(1)
    elif parm.evalAsString() == "substeps2":
        r3.deleteAllKeyframes()
        r3.set(1)
        ss.deleteAllKeyframes()
        ss.set(2)       
    elif parm.evalAsString() == "substeps4":
        r3.deleteAllKeyframes()
        r3.set(1)
        ss.deleteAllKeyframes()
        ss.set(4)  
    elif parm.evalAsString() == "substeps5":
        r3.deleteAllKeyframes()
        r3.set(1)   
        ss.deleteAllKeyframes()
        ss.set(5)  
    elif parm.evalAsString() == "every2":
        r3.deleteAllKeyframes()
        r3.set(2)
        ss.set(1)
    elif parm.evalAsString() == "every5":
        r3.deleteAllKeyframes()
        r3.set(5)
        ss.set(1)
    elif parm.evalAsString() == "every10":
        r3.deleteAllKeyframes()
        r3.set(10)
        ss.set(1)
    
def setExpressionParm(_parm_from,_parm_to):
    
    node_from = _parm_from.node()
    node_to   = _parm_to.node()
    
    relative_path = node_to.relativePathTo(node_from)
    
    parm_template = _parm_from.parmTemplate()
    
    chref = "ch"
    if (parm_template.type() == hou.parmTemplateType.String):
        chref = "chs"
    
    expression = '%s("%s/%s")' % (chref,relative_path,_parm_from.name())
    _parm_to.setExpression(expression)
    
def setRelativePath(_node_from,_parm_to):

    node_to   = _parm_to.node()
    relative_path = node_to.relativePathTo(_node_from)   
    
    _parm_to.set(relative_path)
    
def copyNodeWithNameRef(kwargs):
    node = kwargs["node"]
    
    copied = hou.copyNodesTo([node],node.parent())[0]
    copied.setPosition(node.position()+ hou.Vector2(4,0))
    setExpressionParm(node.parm("basename"), copied.parm("basename"))   
    copied.parm("loadfromdisk").set(True)
    
    copied.setGenericFlag(hou.nodeFlag.Display,True)
    copied.setGenericFlag(hou.nodeFlag.Render,True)   
    copied.setCurrent(True,True)  

def quickSetups(kwargs):    
    selected = kwargs["script_value"]  
    
    if selected == "copy":    
        copyNodeWithNameRef(kwargs)
        
    kwargs['parm'].set(0)   
    
def hardenBaseName(node):

    if node.evalParm('hardenbasename') and node.evalParm('filemethod') == 0:        
        if node.parm('basename').rawValue() is not node.parm('basename').evalAsString():
            basename = node.parm('basename').evalAsString()
            node.parm('basename').deleteAllKeyframes()
            node.parm('basename').revertToDefaults()
            node.parm('basename').set(basename,follow_parm_reference=False)  
            
def enableLoadFromDisk(node):

    if node.evalParm('loadfromdiskonsave'):
        node.parm('loadfromdisk').deleteAllKeyframes()
        node.parm('loadfromdisk').revertToDefaults()
        node.parm('loadfromdisk').set(1,follow_parm_reference=False)
        
def saveToDisk(kwargs):

    node = kwargs['node']     
             
    hardenBaseName(node)
    enableLoadFromDisk(node)
    node.node('read_back').parm('reload').pressButton()
    node.setColor(hou.Color((0.435, 0.921, 0.360)))
    
def saveToDiskInBackground(kwargs):

    import nodegraphtopui
    
    node = kwargs['node']  
        
    nodegraphtopui.dirtyAll(kwargs['node'].parm('targettopnetwork').evalAsNode(), False)
    nodegraphtopui.cookOutputNode(kwargs['node'].parm('targettopnetwork').evalAsNode())
    
    hardenBaseName(node)
    enableLoadFromDisk(node)
    
def getOpenCommand(filepath):

    import platform
    
    OS = platform.system().lower()
    
    if 'windows' in OS:
        opener = 'start'
    elif 'osx' in OS or 'darwin' in OS:
        opener = 'open'
    else:
        opener = 'xdg-open'
    return '{opener} {filepath}'.format(opener=opener, filepath=filepath)     
    
def openPath(kwargs):
    import os
    
    node = kwargs['node']     
    
    dir = node.evalParm("basedir") 
    if node.evalParm("filemethod"):
        dir = os.path.dirname(node.evalParm("file"))
    
    if os.path.exists(dir):
        if dir[-1] is not '/':
            dir += '/'
        hou.ui.showInFileBrowser(dir)
    else:
        # hou.ui.displayMessage(text="Could not open directory:\n{dir}.".format(dir=dir),
        #                       severity=hou.severityType.ImportantMessage)
        os.makedirs(dir)
        hou.ui.displayMessage(f"{dir}\nJust been Created")
        hou.ui.showInFileBrowser(dir)
def verBump(kwargs, operation='add'):  
    node = kwargs['node']          
        
    if 'add' in operation:
        node.parm("ver").set(node.evalParm("ver") + 1)
    else:
        node.parm("ver").set(max(node.evalParm("ver") - 1,1))
        
def subverBump(kwargs, operation='add'):
    node = kwargs['node']
   
    if 'add' in operation:
        node.parm("subver").set(node.evalParm("subver") + 1)
    else:  
        node.parm("subver").set(max(node.evalParm("subver") - 1,0))
