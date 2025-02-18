import toolutils

# Get the pane
pane = (kwargs['pane'])

# Get location. Compensate for a Network Editor not being the Pane it was launched from
if(pane == None):
    parent = toolutils.networkEditor().pwd()
else:
    parent = pane.pwd()

if isinstance(pane, hou.NetworkEditor):
    position = pane.cursorPosition()
else:
    try:
        netEd = toolutils.networkEditor().cursorPosition()
        position = netEd.cursorPosition()
    except:      
        position = hou.Vector2(0, 0)

# Make nodes and sarcastic comments
chip = parent.createNode('neilforet::shatter_hda')
chip.moveToGoodPosition()
chip.setColor(hou.Color(1, 0.5, 0.25))
chip.setGenericFlag(hou.nodeFlag.DisplayComment, True)
chip.setComment('Automate simple setups, and keep your HDAs simpler and more modular.') 
chip.setPosition(position)