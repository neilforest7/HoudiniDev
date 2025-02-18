a = hou.shelves.shelves() # return a dict with all found shelves
tool_shelf = hou.shelves.shelves().pop('jupiter_tools') # return a hou.Shelf object
tool_shelf.filePath() # return shelf save location on disk
tool_shelf.fileLocation() # return shelf save location on disk

# file_path = 'A:/AppBase/Houdini/localLib/toolbar/jupiter_tools_shelf.shelf'
hou.shelves.loadFile(tool_shelf.filePath())
hou.shelves.reloadShelfFiles()