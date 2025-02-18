import os
import hou
# import hrpyc
# connection, hou = hrpyc.import_remote_module()
# if False:
#     import hou
#

def LoadSpeedTreeGUI(node=None):
    # ask for filename
    print("=====================================")
    stmatFile = hou.ui.selectFile(title="Select SpeedTree File", file_type=hou.fileType.Any, pattern = "*.stmat")
    print(stmatFile)
    stmatFile = hou.expandString(stmatFile)
    print(stmatFile)
    stmatFile = os.path.expandvars(stmatFile).replace("\\", "/")
    print(stmatFile)
    stmatFile = os.path.realpath(stmatFile).replace("\\", "/")
    print(stmatFile)
    stmatPath = os.path.dirname(stmatFile).replace("\\", "/") + "/"
    print(stmatPath)

def Activate(node):
    node = hou.pwd()
    LoadSpeedTreeGUI(node)