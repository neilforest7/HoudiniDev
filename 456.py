## Created by Paul Ambrosiussen
## January 19th, 2021

import hou, time, threading, os

# User controlled things
flipbookdir, extension = "A:/Projects/2d/kon_gif", "png"
frames = 14
flagdisableframe = 17
framerate = 20
flipbookscale = 2.0


def flag_changed(node, event_type, **kwargs):
	if node.isDisplayFlagSet() and node.isTemplateFlagSet():
		
		# Get all open pane tabs of type NetworkEditor
		pane_tab = [t for t in hou.ui.paneTabs() if t.type() == hou.paneTabType.NetworkEditor and t.isCurrentTab()]

		# None found, aborting.
		if len(pane_tab)==0:
			return

		# Storing reference to primary open network editor
		_networkeditor = pane_tab[0]
		
		def flipbook_image():

			# Creating a flipbook image
			_flipbook = hou.NetworkImage()
			
			# Playing the flipbook at target FPS
			for _frame in range(0, frames+1):

				# Update the frame used by network image
				_flipbook.setPath(os.path.join(flipbookdir, "{0}.{1}".format(_frame, extension)))

				# Setting position and scale of flipbook image
				_bounds = _networkeditor.itemRect(node, adjusted=True)
				_bounds.expand((_bounds.size()[0]*flipbookscale, _bounds.size()[1]*flipbookscale))
				_flipbook.setRect(_bounds)
				
				# Update the images to be drawn by network editor
				_networkeditor.setBackgroundImages([_flipbook])

				# Check if we need to disable the template flag this frame
				if _frame == flagdisableframe:
					node.setTemplateFlag(False)

				# Redraw the network editor
				_networkeditor.redraw()

				# Sleep for duration of 1 frame
				time.sleep(1.0/framerate)

			# Done playing flipbook. Removing Image.
			_networkeditor.setBackgroundImages([])

		# This is a really dirty hack to get around the UI freezing. 
		# By spawning a new thread we can sleep in a loop without blocking the UI
		_thread = threading.Thread(target = flipbook_image)
		_thread.start()

# Adding a callback to argument node when the type of event is the changing of a node flag.
def add_flag_watcher(node, event_type, child_node, **kwargs):
	child_node.addEventCallback( (hou.nodeEventType.FlagChanged,) , flag_changed)

# Creating a geometry container where we want to watch for any created nodes.
GEO = hou.node("obj/").createNode("geo", "WARNING_CONTAINS_KITTIES")
GEO.addEventCallback((hou.nodeEventType.ChildCreated, ), add_flag_watcher)