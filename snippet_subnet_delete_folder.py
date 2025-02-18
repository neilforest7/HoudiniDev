# code for deleting a folder using Python
# by SWest (2023)

import shutil
import os

# restore world peace
def restore():
    hou.parm('sanity_check').set(0)

# function to delete it
def deleteFolder():
    # get parm value for folder
    folder_to_delete = hou.parm('folder_to_delete_parm').eval()

    # get confirm
    confirm = hou.parm('sanity_check').eval()

    # folder don't exist
    if not os.path.isdir(folder_to_delete):
        hou.ui.displayMessage("It's gone. You better run!")
        restore()
        return
    
    # folder exist, get confirmation one way or another
    if confirm == 0:
        message="Delete "+folder_to_delete+"? You are about to get fired. Are you really sure you want to proceed?"
        buttons=("OK","Cancel")
        title="Delete a folder"
        user_choice = hou.ui.displayMessage(text=message, buttons=buttons, title=title)        

    # ready to delete folder
    if confirm == 1 or user_choice == 0:
        try:
            shutil.rmtree(folder_to_delete)
        # trouble message
        except OSError as e:
            hou.ui.displayMessage("Error: %s - %s." % (e.filename, e.strerror))

    restore()