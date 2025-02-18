#### create a node

root = hou.node('/obj')
node = root.createNode('node_type')

#### get some node properties

name = node.name()
type = node.type().name()
position = node.position()
color = node.color()
comment = node.comment()
position = node.position

#### set some node properties

node.setName('node_name')
node.setColor(hou.Color((1, 1, 1)))
node.setPosition([x, y])

node.setComment('comment')
node.setGenericFlag(hou.nodeFlag.DisplayComment, True)

#### delete a node

node = hou.node('/path/to/node')
node.destroy()

#### unlock a node

node = hou.node('/path/to/node')
node.allowEditingOfContents()

#### change node shape

node.setUserData('nodeshape', 'light') # light shape

#### check if a node exists

if hou.node('/path/to/node'):
    # the node does exist
else:
    # the node does not exist

#### get selected node(s)

selection = hou.selectedNodes()
the_only_selection = hou.selectedNodes()[0]

#### set current selected node

node.setCurrent(True, clear_all_selected=True)

#### get a list of nodes

nodes = hou.node('/obj').children() # get all top level nodes in a context
all_children = current_node.allSubChildren() # get all children of a node

#### get primitive groups

node = hou.node('/path/to/node')
group_list = node.geometry().primGroups()

#### get names

for group in group_list:
    name = group.name()

#### connect nodes

input_node = hou.node('/path/to/node')
output_node = hou.node('/path/to/node')

# option 1
output_node.setInput(0, input_node) # output_index, input_node

# option 2
output_node.setNamedInput('parm_name', input_node, 0) # parm_name, input_node, input_node_index


#### insert a new node between two existing connected nodes

start_node = hou.node('/path/to/node')
output_connections = start_node.outputConnections()

new_node = start_node.createOutputNode('node_type')

if output_connections:
    target = output_connections[0]
    output_node = target.outputNode()
    # output_index = target.outputIndex()
    # input_node = target.inputNode()
    input_index = target.inputIndex()
    output_node.setInput(input_index, new_node)

#### set display flag on a node

node.setGenericFlag(hou.nodeFlag.Render, 1)
node.setGenericFlag(hou.nodeFlag.Visible, 1)


#### layout nodes

# equal to hitting "L" in network view
root = hou.node('/obj')
root.layoutChildren()

# layout specific nodes
# note: laid out in reference to first node in list
root.layoutChildren(items=[list, of, nodes], horizontal_spacing=1.7, vertical_spacing=1.4)

# layout a single node
node.moveToGoodPosition()


#### get a parameter value

node = hou.node('/path/to/node')
value = node.parm('parm_name').eval() # method 1
value = node.evalParm('parm_name') # method 2
value = node.parm('parm_name').rawValue() # method 3

#### set a parameter

node.parm('parm_name').set(value)
node.parm('parm_name').setExpression(expression,language=hou.exprLanguage.Python)

#### create a parameter reference

master_node = hou.node('/path/to/node')
target_node = hou.node('/path/to/other/node')

master_parm = master_node.parm('parm_name')
target_node.parm('parm_name').set(master_parm)


#### create a parameter

node = hou.node('path/to/node')
parm_group = node.parmTemplateGroup()
new_parm = hou.FloatParmTemplate('name', 'label', 1)
parm_group.insertAfter('existing_parm_name', new_parm)
node.setParmTemplateGroup(parm_group)

#### get all parm templates in a parm group

parm_group = node.parmTemplateGroup()
templates = parm_group.parmTemplates()

#### remove a parm template from a parm group

parm_group.remove(template)
# note: will need to set parm_group as the new parmTemplateGroup

#### get node comment

comment = node.comment()
set node comment
node.setComment('comment')
node.setGenericFlag(hou.nodeFlag.DisplayComment, True)


#### get current node (very useful for callback scripts)

current_node = hou.pwd()
get parent of current node
parent = hou.parent()

#### create a sticky note

root = hou.node('/obj/')
note = root.createStickyNote()

#### customize a sticky note

note.setName('note_name')
note.setSize([w, h])
note.setPosition([x, y])
note.setText('sticky note text')
note.setTextSize(0.5)
note.setColor(hou.Color(1, 1, 1))
note.setTextColor(hou.Color(0, 0, 0))

#### create a network box

root = hou.node('/obj/')
box = root.createNetworkBox()

#### customize a network box

box.setName('box_name')
box.setSize([w, h])
box.setPosition([x, y])
box.setComment('title')
box.setColor(hou.Color(1, 1, 1))

#### get all network boxes (and some parameters)

root = hou.node('/obj/')
boxes = root.networkBoxes()

for box in boxes:
    name = box.name()
    size = box.size()
    position = box.position()
    comment = box.comment()
    color = box.color()

#### get a specific network box

root = hou.node('/obj/')
netbox = root.findNetworkBox('netbox_name')

#### get all nodes in a network box

nodes = netbox.nodes()


#### get current context

network_editor = None
for pane in hou.ui.paneTabs():
    if isinstance(pane, hou.NetworkEditor) and pane.isCurrentTab():
        network_editor = pane
if network_editor:
    network_node = network_editor.pwd()
    network_path = network_node.path()


#### display message

hou.ui.displayMessage('message to user')


#### create undo group

with hou.undos.group('group name'):
    #commands to fall under group


#### working with visualizers

visualize_node = hou.node('/path/to/visualize_node')
node_category = hou.viewportVisualizerCategory.Node

# get visualizers associated with a visualize node
visualizer_list = hou.viewportVisualizers.visualizers(category=node_category, node=visualize_node)

# get visualizer types
type_list = hou.viewportVisualizers.types()
marker_type = type_list[0]

# create a visualizer
visualizer = hou.viewportVisualizers.createVisualizer(marker_type, category=node_category, node=visualize_node)

# set type and parameters
visualizer.setType(marker_type)
visualizer.setParm('parm_name', value)

#### create an arnold shader

shop_name = 'shaders'
shader_name = 'example_shader'
shader_type = 'standard_surface'

# create shopnet
root = hou.node('/obj/')
shopnet = root.createNode('shopnet')
shopnet.setName(shop_name)
shopnet.moveToGoodPosition()

# create vopnet
shop_path = '/obj/' + shop_name + '/'
root = hou.node(shop_path)
vopnet = root.createNode('arnold_vopnet')
vopnet.setName(shader_name)
vopnet.moveToGoodPosition()

# create shader
vop_path = shop_path + shader_name + '/'
root = hou.node(vop_path)
shader = root.createNode(shader_type)

out = hou.node(vop_path + 'OUT_material')
out.setInput(0, shader)

root.layoutChildren()


#### create a new shelf

new_shelf = hou.shelves.newShelf(file_path='/full/path/to/shelf/file', name='shelf_name', label='shelf_label')

#### get an existing shelf

target_shelf = 'shelf_name'
shelf = None

shelves = hou.shelves.shelves()
for shelf_name, shelf_object in shelves.iteritems():
    if shelf_name == target_shelf:
        shelf = shelf_object

#### add a tool to a shelf

tool_list = list(shelf.tools())

file_path = '/full/path/to/shelf/file'
tool_name = 'toolname'
tool_label = 'Tool Label'
tool_script = 'print "Hello World"'
tool_icon = 'MISC_present'

new_tool = hou.shelves.newTool(file_path=file_path, name=tool_name, label=tool_label, script=tool_script, language=hou.scriptLanguage.Python, icon=tool_icon)

tool_list.append(new_tool)
shelf.setTools(tool_list)
