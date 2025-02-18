editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
print(editor.nodeShapes())

# Returned tuple of strings:
# ('rect', 'bone', 'bulge', 'bulge_down', 'burst', 'camera', 
# 'chevron_down', 'chevron_up', 'cigar', 'circle', 'clipped_left', 
# 'clipped_right', 'cloud', 'diamond', 'ensign', 'gurgle', 'light', 
# 'null', 'oval', 'peanut', 'pointy', 'slash', 'squared', 'star', 
# 'tabbed_left', 'tabbed_right', 'tilted', 'trapezoid_down', 
# 'trapezoid_up', 'wave')