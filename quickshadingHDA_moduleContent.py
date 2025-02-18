def readValues(kwargs):
    node = kwargs['node']
    
    basepath = node.evalParm('basetex')
    
    bcol = node.evalParm('bcString')
    rocol = node.evalParm('roString')
    mecol = node.evalParm('meString')
    nocol = node.evalParm('noString')
    discol = node.evalParm('disString')
    
    abzug = len(bcol) + 4 
    
    base = basepath[:-abzug]
    ext =  basepath[-4:]
    
    basecolor = base + bcol + ext
    roughness = base + rocol + ext
    metallic = base + mecol + ext
    normal = base + nocol + ext
    displace = base + discol + ext


    node.parm("tex0").set(basecolor)
    node.parm("tex1").set(roughness)
    node.parm("tex2").set(metallic)
    node.parm("tex3").set(normal)
    node.parm("tex4").set(displace)
    
#hou.phm().readValues(kwargs)

# import hou
#My = kwargs['node']
#My.setMaterialFlag(1)