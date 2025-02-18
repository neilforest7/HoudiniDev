¡ú€(öéE(,>u˘rnTªî;æzÏ—¯pÌÿW
ùhode(newNode, selNodes, connectToNearestNodeIfNoSelection=False):
    category = newNode.type().category()
    isSop = category == hou.sopNodeTypeCategory()
    isVop = category == hou.vopNodeTypeCategory()

    selectedNodes = selNodes
    nodecount = len(selectedNodes)
    if nodecount == 0 and connectToNearestNodeIfNoSelection:
        editor = hou.ui.paneTabUnderCursor()
        if editor:
            nearestNode = findNearestNode(editor)
            if nearestNode:
                selectedNodes = [nearestNode]
                nodecount = 1

    if nodecount > 0:
        ninputs = newNode.type().maxNumInputs()
        if ninputs > 1:
            #sort nodes from left to right and connect by position
            selectedNodes = sorted(selectedNodes, key=lambda n: n.position().x())

        if len(selectedNodes) == 1 and (isSop or isVop):
            selectedNode = selectedNodes[0]
            outputConnectors = selectedNode.outputConnectors()
            inputConnectors = newNode.inputConnectors()

            if selectedNode.type().name() == 'subnet':
                outputConnectors = [outputConnectors[0]]

            if isSop:
                for i in range(min(len(outputConnectors), len(inputConnectors))):
                    newNode.setInput(i, selectedNode, i)
            if isVop:
                outputIndex = 0
                outputDataTypes = selectedNode.outputDataTypes()
                inputDataTypes = newNode.inputDataTypes()
                numOutputDataTypes = len(outputDataTypes)
                numInputDataTypes = len(inputDataTypes)
                for i in range(numInputDataTypes):
                    if outputIndex == numOutputDataTypes:
                        break
                    if outputDataTypes[outputIndex] == inputDataTypes[i]:
                        newNode.setInput(i, selectedNode, outputIndex)
                        outputIndex += 1
        else:
            index = 0
            for i in range(nodecount):
                if selectedNodes[i].type().maxNumOutputs() > 0 and index < ninputs:
                    newNode.setInput(index, selectedNodes[i])
                    index += 1



def createNewNode(editor, nodetypename, parms=None):
    import nodegraphutils as utils

    pwd = editor.pwd()
    path = pwd.path()
    context = pwd.childTypeCategory().name()
    if pwd and path and context:
        nodetype = hou.nodeType(pwd.childTypeCategory(), nodetypename)
        if nodetype:
            selectedNodes = hou.selectedNodes()
            with hou.undos.group("Create New Node: " + nodetype.description()):
                pos = editor.cursorPosition()
                
                newNode = hou.node(path).createNode(nodetypename)

                if parms:
                    if isinstance(parms, dict):
                        for i, (key, value) in enumerate(parms.items()):
                            newNode.parm(key).set(value)
                    elif isinstance(parms, types.StringTypes):
                        hou.hscript("oppresetload " + newNode.path() + " '{0}'".format(parms))

                connectSelectedNodesToNewNode(newNode, selectedNodes)
                
                size = utils.getNewNodeHalfSize()
                pos[0] -= size.x()
                pos[1] -= size.y()

                newNode.setPosition(pos)
                newNode.setSelected(True, clear_all_selected=True)

                nodecount = len(selectedNodes)
                if nodecount != 0:
                    if context != "Driver" and context != "Dop" and context != "Shop" and context != "Chop" and context != "Vop":
                        if hasattr(newNode, "setDisplayFlag"):
                            newNode.setDisplayFlag(True)
                    if context != "Object" and context != "Driver" and context != "Dop" and context != "Shop" and context != "Chop" and context != "Vop" and context != "Lop":
                        if hasattr(newNode, "setDisplayFlag"):
‰sı˛b&∞}ï:ÚI(îZ˜·»ênR}kÊñ>b˙¬»ode.setRenderFlag(True)

                return newNode

def objectMergeFromSelection(uievent):
    with hou.undos.group("Object Merge From Selection"):
        editor = uievent.editor
        pos = editor.cursorPosition()
        currentPath = editor.pwd().path()
        currentNode = hou.node(currentPath)
        selNodes = hou.selectedNodes()
        for node in selNodes:
            mergeNode = currentNode.createNode("object_merge")
            mergeNode.setName("IN_" + node.name(), unique_name=True)
            mergeNode.parm("objpath1").set("../" + node.name())

            if len(selNodes) > 1:
                pos = node.position()
                pos[1] -= 1
                mergeNode.setPosition(pos)
            else:
                size = mergeNode.size ( )
                pos [ 0 ] -= size [ 0 ] / 2
                pos [ 1 ] -= size [ 1 ] / 2
                mergeNode.setPosition ( pos )



def objectMergeOutputConnections(uievent):
    import math, re
    import toolutils as tutils

    with hou.undos.group("Object Merge Output Connections"):
        editor = uievent.editor
        currentPath = editor.pwd().path()
        currentNode = hou.node(currentPath)
        selNodes = hou.selectedNodes()
        sourceNodes = selNodes
        for node in selNodes:
            connectedNodes = tutils.findConnectedNodes(node, 'output', None)

            outputsReplaced = []
            newNullNodes = []
            newOutputNodes = []
            outputIndices = []

            childrenNames = []
            childrenNodes = []
            
            outputs = node.outputConnections()
            for o in outputs:
                outputIndex = o.outputIndex()
                outputNode = o.outputNode()
                if outputIndex not in outputsReplaced:
                    outputsReplaced.append(outputIndex)

                    outputIndices.append(outputIndex)

                    outputName = o.inputLabel().replace(' ', '_').upper()
                    re.sub(r'\W+', '', outputName)
                    
                    newNullNode = currentNode.createNode("null", outputName)
                    newNullNode.setInput(0, node, outputIndex)
                    
                    mergeNodeName = newNullNode.name()
                    mergeNode = currentNode.createNode("object_merge")
                    mergeNode.setName("IN_" + mergeNodeName, unique_name=True)
                    mergeNode.parm("objpath1").set("../" + mergeNodeName)
                    
                    newNullNodes.append(newNullNode)
                    newOutputNodes.append(mergeNode)
                    

                outputNodeName = outputNode.name()
                if outputNodeName not in childrenNames:
                    childrenNames.append(outputNodeName)
                    childrenNodes.append(outputNode)
            

            lowestPosY = 0
            outputCount = len(outputsReplaced)
            for index, newNode in enumerate(newNullNodes):
                outputIndex = outputIndices[index]
                
                xoffset = math.ceil((outputCount - 0) / 2) - outputIndex
                yoffset = outputIndex + 1
                pos = node.position()
                pos[0] -= xoffset
                pos[1] -= yoffset

                newNode.setPosition(pos)
                pos[1] -= min(3, outputCount)
                lowestPosY = pos[1]

                newOutputNodes[index].setPosition(pos)


            for o in outputs:
                outputNode = o.outputNode()
                outputIndex = o.outputIndex()
                inputIndex = o.inputIndex()
                
                outputNode.setInput(inputIndex, newOutputNodes[outputIndex])
            

            maxPosY = -999999999
            for connectedNode in connectedNodes:
                maxPosY = max(maxPosY, connectedNode.position().y())

            dist = lowestPosY - maxPosY
            minOfU√≥.«rSêêÆ≈$ÇœœuÓÿÜÏe¡˛BkminOffset:
                diff = minOffset - dist
                for connectedNode in connectedNodes:
                    pos = connectedNode.position()
                    pos[1] -= diff
                    connectedNode.setPosition(pos)



def objectMergeInputConnections(uievent):
    import math, re
    import toolutils as tutils

    with hou.undos.group("Object Merge Output Connections"):
        editor = uievent.editor
        currentPath = editor.pwd().path()
        currentNode = hou.node(currentPath)
        selNodes = hou.selectedNodes()
        sourceNodes = []
        for node in selNodes:
            inputNodes = node.inputs()
            for n in inputNodes:
                if n not in sourceNodes:
                    sourceNodes.append(n)

        for node in sourceNodes:
            connectedNodes = tutils.findConnectedNodes(node, 'output', None)

            outputsReplaced = []
            newNullNodes = []
            newOutputNodes = []
            outputIndices = []

            childrenNames = []
            childrenNodes = []
            
            outputs = node.outputConnections()
            outputs = [output for output in outputs if output.outputNode() in selNodes]

            for o in outputs:
                outputIndex = o.outputIndex()
                outputNode = o.outputNode()
                if outputIndex not in outputsReplaced:
                    outputsReplaced.append(outputIndex)

                    outputIndices.append(outputIndex)

                    outputName = o.inputLabel().replace(' ', '_').upper()
                    re.sub(r'\W+', '', outputName)
                    
                    newNullNode = currentNode.createNode("null", outputName)
                    newNullNode.setInput(0, node, outputIndex)
                    
                    mergeNodeName = newNullNode.name()
                    mergeNode = currentNode.createNode("object_merge")
                    mergeNode.setName("IN_" + mergeNodeName, unique_name=True)
                    mergeNode.parm("objpath1").set("../" + mergeNodeName)
                    
                    newNullNodes.append(newNullNode)
                    newOutputNodes.append(mergeNode)
                    

                outputNodeName = outputNode.name()
                if outputNodeName not in childrenNames:
                    childrenNames.append(outputNodeName)
                    childrenNodes.append(outputNode)
            

            lowestPosY = 0
            outputCount = len(outputsReplaced)
            for index, newNode in enumerate(newNullNodes):
                outputIndex = outputIndices[index]
                
                xoffset = math.ceil((outputCount - 0) / 2) - outputIndex
                yoffset = outputIndex + 1
                pos = node.position()
                pos[0] -= xoffset
                pos[1] -= yoffset

                newNode.setPosition(pos)
                pos[1] -= min(3, outputCount)
                lowestPosY = pos[1]

                newOutputNodes[index].setPosition(pos)


            for o in outputs:
                outputNode = o.outputNode()
                outputIndex = o.outputIndex()
                inputIndex = o.inputIndex()

                outputNode.setInput(inputIndex, newOutputNodes[outputIndex])
            

            maxPosY = -999999999
            for connectedNode in connectedNodes:
                maxPosY = max(maxPosY, connectedNode.position().y())

            dist = lowestPosY - maxPosY
            minOffset = 2
            if dist < minOffset:
                diff = minOffset - dist
                for connectedNode in connectedNodes:
                    pos = connectedNode.position()
                    pos[1] -= diff
                    connectedNode.setPosition(pos)