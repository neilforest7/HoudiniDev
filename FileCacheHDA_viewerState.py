"""
State:          Sidefx File Cache
State type:     sidefx_filecache
Description:    Sidefx File Cache
Author:         ati
Date Created:   June 17, 2021 - 10:48:09
"""

import hou
import viewerstate.utils as su
import resourceutils as ru
import toolutils

cachedir = "cachedir"
cachename = "cachename"

class State(object):
    def __init__(self, state_name, scene_viewer):
        self.state_name = state_name
        self.scene_viewer = scene_viewer    
        
        template = {
            "title": "File Cache", "desc": "info", "icon": "SOP_filecache",
            "rows": [
                {"id": cachedir, "label": "Cache Folder"},      
                {"id": cachename, "label": "Cache Name"},                        
            ]
        }
        
        self.scene_viewer.hudInfo(hud_template=template)
           
    def updateInfoBox(self, node):
        """ Updates our info box to reflect the current state settings.
        """
        
        rows = {}
        self._fillCacheInfo(node,rows)
        self.scene_viewer.hudInfo(hud_values=rows)
        
    def updateParmInfo(self, **kwargs):
        """Updates info box on the fly as parameters change."""
        
        node = kwargs["node"]
        parmtup = kwargs["parm_tuple"]
        name = parmtup.name()        
        
        rows = {}
        if name in ("filemethod",
                    "timedependent",
                    "basename",
                    "filetype",                    
                    "basedir",
                    "enableversion",
                    "version",
                    "enablesubversion",
                    "subversion",
                    "sopoutput"):
            self._fillCacheInfo(node,rows)
            self.scene_viewer.hudInfo(hud_values=rows)

    def _fillCacheInfo(self, node, rows):
        """Updates cache path related parms"""
        
        if node.evalParm("filemethod"):
            import os
            rows[cachedir], rows[cachename] = os.path.split(node.evalParm("file"))             
        else:      
            rows[cachedir] = node.evalParm("cachedir") 
            rows[cachename] = node.evalParm("cachename")     
            
            if node.evalParm("timedependent"):
                rows[cachename] = rows[cachename].replace(node.evalParm("framestr"), ".$F4")    
            
    def onEnter(self, kwargs):
        """ Initializes the info
        """    
        
        node = kwargs['node']
        node.addEventCallback([hou.nodeEventType.ParmTupleChanged],
                              self.updateParmInfo)                              
       
        self.scene_viewer.hudInfo(show=True)
        self.updateInfoBox(node)
        self.scene_viewer.hudInfo(show=True)
        
    def onExit(self, kwargs):
        """ Close the HUD
        """
        
        node = kwargs.get("node")
        
        if node:
            node.removeEventCallback([hou.nodeEventType.ParmTupleChanged],
                                     self.updateParmInfo)

# Callback for triggering an info box update.
def updateInfoBox():
    sv = toolutils.sceneViewer()
    if sv.currentState() == 'neilforest_filecache':
        sv.runStateCommand( 'updateInfoBox' )
        
def createViewerStateTemplate():
    """ Mandatory entry point to create and return the viewer state 
        template to register. """

    state_typename = kwargs["type"].definition().sections()["DefaultState"].contents()
    state_label = "File Cache"
    state_cat = hou.sopNodeTypeCategory()

    template = hou.ViewerStateTemplate(state_typename, state_label, state_cat)
    template.bindFactory(State)
    template.bindIcon(kwargs["type"].icon())

    return template
