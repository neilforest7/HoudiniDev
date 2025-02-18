################################################################
# SpeedTreeImporter.py
#
# *** INTERACTIVE DATA VISUALIZATION (IDV) PROPRIETARY INFORMATION ***
#
# This software is supplied under the terms of a license agreement or
# nondisclosure agreement with Interactive Data Visualization and may
# not be copied or disclosed except in accordance with the terms of
# that agreement.
#
# Copyright (c) 2003-2020 IDV, Inc.
# All Rights Reserved.
# IDV, Inc.
# Web: http://www.speedtree.com

import xml.dom.minidom as xmldom
import os
import subprocess
import sys
from pprint import pprint

from test_hrpyc import hou


################################################################
# class SpeedTreeMaterial

class SpeedTreeMap:
    def __init__(self, red = 1.0, green = 1.0, blue = 1.0, file = ""):
        self.red = red
        self.green = green
        self.blue = blue
        self.file = file

class SpeedTreeMaterial:
    def __init__(self, name, twoSided = False, vertexOpacity = False, userData = ""):
        self.name = name
        self.twoSided = twoSided
        self.vertexOpacity = vertexOpacity
        self.userData = userData
        self.maps = { }
        self.shader = None
                
       
################################################################
# SpeedTreeMaterialCreator

class SpeedTreeMaterialCreator(object):
    description = "unknown"
    def CanCreate(self):
        return False
        

################################################################
# SpeedTreeMaterialCreatorPrincipled

class SpeedTreeMaterialCreatorPrincipled(SpeedTreeMaterialCreator):
    description = "SpeedTree Principled"
    def CreateMaterial(self, stMaterial):
        shader = hou.node("/mat").createNode("SpeedTreePrincipled")
        shader.parm("TwoSided").set(True)
                   
        if (stMaterial.maps.has_key("Color")):
            stmap = stMaterial.maps["Color"]
            shader.parm("Colorr").set(stmap.red)
            shader.parm("Colorg").set(stmap.blue)
            shader.parm("Colorb").set(stmap.green)
            if (stmap.file):
                shader.parm("ColorMap").set(stmap.file)
                
        if (stMaterial.maps.has_key("Opacity")):
            stmap = stMaterial.maps["Opacity"]
            if (stmap.file):
                shader.parm("OpacityMap").set(stmap.file) 
             
        if (stMaterial.maps.has_key("Normal")):
            stmap = stMaterial.maps["Normal"]
            if (stmap.file):
                shader.parm("NormalMap").set(stmap.file)  
                
        if (stMaterial.maps.has_key("Gloss")):
            stmap = stMaterial.maps["Gloss"]
            shader.parm("Gloss").set(stmap.red)
            if (stmap.file):
                shader.parm("GlossMap").set(stmap.file)  
                   
        if (stMaterial.maps.has_key("Specular")):
            stmap = stMaterial.maps["Specular"]
            shader.parm("Specularr").set(stmap.red)
            shader.parm("Specularg").set(stmap.blue)
            shader.parm("Specularb").set(stmap.green)
            if (stmap.file):
                shader.parm("SpecularMap").set(stmap.file)
         
        if (stMaterial.maps.has_key("Metallic")):
            stmap = stMaterial.maps["Metallic"]
            shader.parm("Metallic").set(stmap.red)
            if (stmap.file):
                shader.parm("MetallicMap").set(stmap.file)
         
        if (stMaterial.maps.has_key("SubsurfaceColor")):
            stmap = stMaterial.maps["SubsurfaceColor"]
            shader.parm("Subsurfacer").set(stmap.red)
            shader.parm("Subsurfaceg").set(stmap.blue)
            shader.parm("Subsurfaceb").set(stmap.green)
            if (stmap.file):
                shader.parm("SubsurfaceMap").set(stmap.file)
         
        shader.parm("UseSubsurface").set(False)
        if (stMaterial.maps.has_key("SubsurfaceAmount")):
            stmap = stMaterial.maps["SubsurfaceAmount"]
            shader.parm("UseSubsurface").set(True)
            shader.parm("SubsurfaceAmount").set(stmap.red)
            if (stmap.file):
                shader.parm("SubsurfaceAmountMap").set(stmap.file)
                
        return shader
        

################################################################
# SpeedTreeMaterialCreatorMantra

class SpeedTreeMaterialCreatorMantra(SpeedTreeMaterialCreator):
    description = "SpeedTree Mantra"
    def CreateMaterial(self, stMaterial):
        shader = hou.node("/mat").createNode("SpeedTreeMantra")           
        shader.parm("TwoSided").set(True)
                
        if (stMaterial.maps.has_key("Color")):
            stmap = stMaterial.maps["Color"]
            shader.parm("Colorr").set(stmap.red)
            shader.parm("Colorg").set(stmap.blue)
            shader.parm("Colorb").set(stmap.green)
            if (stmap.file):
                shader.parm("ColorMap").set(stmap.file)
                
        if (stMaterial.maps.has_key("Opacity")):
            stmap = stMaterial.maps["Opacity"]
            if (stmap.file):
                shader.parm("OpacityMap").set(stmap.file) 
             
        if (stMaterial.maps.has_key("Normal")):
            stmap = stMaterial.maps["Normal"]
            if (stmap.file):
                shader.parm("NormalMap").set(stmap.file)  
                
        if (stMaterial.maps.has_key("Gloss")):
            stmap = stMaterial.maps["Gloss"]
            shader.parm("Gloss").set(stmap.red)
            if (stmap.file):
                shader.parm("GlossMap").set(stmap.file)  
                   
        if (stMaterial.maps.has_key("Specular")):
            stmap = stMaterial.maps["Specular"]
            shader.parm("Specularr").set(stmap.red)
            shader.parm("Specularg").set(stmap.blue)
            shader.parm("Specularb").set(stmap.green)
            if (stmap.file):
                shader.parm("SpecularMap").set(stmap.file)
         
        if (stMaterial.maps.has_key("Metallic")):
            stmap = stMaterial.maps["Metallic"]
            shader.parm("Metallic").set(stmap.red)
            if (stmap.file):
                shader.parm("MetallicMap").set(stmap.file)
         
        if (stMaterial.maps.has_key("SubsurfaceColor")):
            stmap = stMaterial.maps["SubsurfaceColor"]
            shader.parm("Subsurfacer").set(stmap.red)
            shader.parm("Subsurfaceg").set(stmap.blue)
            shader.parm("Subsurfaceb").set(stmap.green)
            if (stmap.file):
                shader.parm("SubsurfaceMap").set(stmap.file)
         
        shader.parm("UseSubsurface").set(False)
        if (stMaterial.maps.has_key("SubsurfaceAmount")):
            stmap = stMaterial.maps["SubsurfaceAmount"]
            shader.parm("UseSubsurface").set(True)
            shader.parm("SubsurfaceAmount").set(stmap.red)
            if (stmap.file):
                shader.parm("SubsurfaceAmountMap").set(stmap.file)
                
        return shader  
        

################################################################
# SpeedTreeMaterialCreatorRenderman

class SpeedTreeMaterialCreatorRenderman(SpeedTreeMaterialCreator):
    description = "SpeedTree Renderman"
    
    def MakeTexture(self, stMap, name, parent, linear):
        tex = parent.createNode("pxrtexture")
        tex.setName(name)
        tex.parm("linearize").set(linear)
        tex.parm("filename").set(stMap.file)
        bake = parent.createNode("pxrbaketexture")
        bake.setName(name + "_bake")
        bake.setNamedInput("inputRGB", tex, "resultRGB")
        bake.parm("filename").set(stMap.file)
        return bake
    
    def CreateMaterial(self, stMaterial):
        shader = hou.node("/mat").createNode("pxrmaterialbuilder")
        output = shader.children()[0]
        
        surface = shader.createNode("pxrsurface")
        surface.setName("Surface")
        output.setFirstInput(surface)
        
        surface.parm("diffuseDoubleSided").set(stMaterial.twoSided)
        surface.parm("specularDoubleSided").set(stMaterial.twoSided)
                   
        if (stMaterial.maps.has_key("Color")):
            stmap = stMaterial.maps["Color"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Color", shader, True)
                surface.setNamedInput("diffuseColor", tex, "resultRGB")
            else:
                surface.parm("diffuseColorr").set(stmap.red)
                surface.parm("diffuseColorg").set(stmap.blue)
                surface.parm("diffuseColorb").set(stmap.green)
                  
        if (stMaterial.maps.has_key("Opacity")):
            stmap = stMaterial.maps["Opacity"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Opacity", shader, False)
                surface.setNamedInput("presence", tex, "resultR")
        elif stMaterial.vertexOpacity:
            vopacity = shader.createNode("pxrprimvar")
            vopacity.setName("BranchBlend")
            vopacity.parm("varname").set("uv2")
            vopacity.parm("type").set("color")
            surface.setNamedInput("presence", vopacity, "resultF")
             
        if (stMaterial.maps.has_key("Normal")):
            stmap = stMaterial.maps["Normal"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Normal", shader, False)
                normalmap = shader.createNode("pxrnormalmap")
                normalmap.setName("NormalMap")
                surface.setNamedInput("bumpNormal", normalmap, "resultN")
                if (stMaterial.twoSided):
                    # set up normals on backside
                    pxrswitch = shader.createNode("pxrswitch")
                    normalmap.setNamedInput("inputRGB", pxrswitch, "resultRGB")
                    pxrshade = shader.createNode("pxrshadedside")
                    pxrswitch.setNamedInput("index", pxrshade, "resultF")
                    pxrinvert = shader.createNode("pxrinvert")
                    pxrinvert.parm("invertChannel2").set(False)
                    pxrinvert.setNamedInput("inputRGB", tex, "resultRGB")
                    colorarray = shader.createNode("dynamicarray")
                    colorarray.setNamedInput("input1", pxrinvert, "resultRGB")
                    colorarray.setNamedInput("input2", tex, "resultRGB")
                    pxrswitch.setNamedInput("inputsRGB", colorarray, "out_array")
                else:  
                    normalmap.setNamedInput("inputRGB", tex, "resultRGB")
                
        if (stMaterial.maps.has_key("Gloss")):
            stmap = stMaterial.maps["Gloss"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Gloss", shader, False)
                rough = shader.createNode("pxrinvert")
                rough.setName("Roughness")
                rough.setNamedInput("inputRGB", tex, "resultRGB")
                surface.setNamedInput("diffuseRoughness", rough, "resultR")
                surface.setNamedInput("specularRoughness", rough, "resultR")
            else:
                surface.parm("diffuseRoughness").set(1.0 - stmap.red)
                surface.parm("specularRoughness").set(1.0 - stmap.red)
                   
        surface.parm("specularDoubleSided").set(stMaterial.twoSided)
        surface.parm("roughSpecularDoubleSided").set(stMaterial.twoSided)
        surface.parm("specularFresnelMode").set(1)
        surface.parm("roughSpecularFresnelMode").set(1)
        surface.parm("specularModelType").set(1)
        surface.parm("roughSpecularModelType").set(1)
        if (stMaterial.maps.has_key("Specular")):
            stmap = stMaterial.maps["Specular"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Specular", shader, True)
                surface.setNamedInput("specularEdgeColor", tex, "resultRGB")
                surface.setNamedInput("roughSpecularEdgeColor", tex, "resultRGB")
            else:
                surface.parm("specularEdgeColorr").set(stmap.red)
                surface.parm("specularEdgeColorg").set(stmap.blue)
                surface.parm("specularEdgeColorb").set(stmap.green)
                surface.parm("roughSpecularEdgeColorr").set(stmap.red)
                surface.parm("roughSpecularEdgeColorg").set(stmap.blue)
                surface.parm("roughSpecularEdgeColorb").set(stmap.green)
       
        if (stMaterial.maps.has_key("SubsurfaceColor")):
            stmap = stMaterial.maps["SubsurfaceColor"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "SubsurfaceColor", shader, True)
                surface.setNamedInput("diffuseTransmitColor", tex, "resultRGB")
            else:
                surface.parm("diffuseTransmitColorr").set(stmap.red)
                surface.parm("diffuseTransmitColorg").set(stmap.blue)
                surface.parm("diffuseTransmitColorb").set(stmap.green)
            
        if (stMaterial.maps.has_key("SubsurfaceAmount")):
            stmap = stMaterial.maps["SubsurfaceAmount"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "SubsurfaceAmount", shader, False)
                exposure = shader.createNode("pxrexposure")
                exposure.setName("AdjustSubsurface")
                exposure.setNamedInput("inputRGB", tex, "resultRGB")
                surface.setNamedInput("diffuseTransmitGain", exposure, "resultR")
            else:
                surface.parm("diffuseTransmitGain").set(stmap.red)
                
        shader.layoutChildren()
        return shader  

        
################################################################
# SpeedTreeMaterialCreatorVray

class SpeedTreeMaterialCreatorVray(SpeedTreeMaterialCreator):
    description = "SpeedTree V-Ray"
    
    def MakeTexture(self, stMap, name, parent, linear):
        tex = parent.createNode("VRayNodeMetaImageFile")
        tex.setName(name)
        if linear:
            tex.parm("BitmapBuffer_color_space").set("0")
        tex.parm("BitmapBuffer_file").set(stMap.file)
        return tex
    
    def CreateMaterial(self, stMaterial):
        shader = hou.node("/mat").createNode("vray_vop_material")
        surface = shader.children()[1]
        
        surface.parm("option_double_sided").set(stMaterial.twoSided)
        surface.parm("option_reflect_on_back").set(stMaterial.twoSided)
        twoSidedNode = None
        if (stMaterial.twoSided):
            twoSidedNode = shader.createNode("VRayNodeMtl2Sided")
            twoSidedNode.setName("TwoSided")
            twoSidedNode.parm("translucency_texr").set(0)
            twoSidedNode.parm("translucency_texg").set(0)
            twoSidedNode.parm("translucency_texb").set(0)
            twoSidedNode.setNamedInput("front", surface, "brdf")
            twoSidedNode.setNamedInput("back", surface, "brdf")
            shader.children()[0].setNamedInput("Material", twoSidedNode, "material")
                
        if (stMaterial.maps.has_key("Color")):
            stmap = stMaterial.maps["Color"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Color", shader, False)
                surface.setNamedInput("diffuse", tex, "color")
            else:
                surface.parm("diffuser").set(stmap.red)
                surface.parm("diffuseg").set(stmap.blue)
                surface.parm("diffuseb").set(stmap.green)
                  
        if (stMaterial.maps.has_key("Opacity")):
            stmap = stMaterial.maps["Opacity"]
            if (stmap.file):
                surface.parm("opacity_mode").set("1")
                tex = self.MakeTexture(stmap, "Opacity", shader, True)
                surface.setNamedInput("opacity", tex, "intensity")
        elif stMaterial.vertexOpacity:
            vopacity = shader.createNode("VRayNodeTexUserColor")
            vopacity.setName("BranchBlend")
            vopacity.parm("user_attribute").set("uv2")
            channel = shader.createNode("VRayNodeTexAColorChannel")
            channel.setNamedInput("color", vopacity, "color")
            surface.setNamedInput("opacity", channel, "value")
             
        if (stMaterial.maps.has_key("Normal")):
            stmap = stMaterial.maps["Normal"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Normal", shader, True)
                bump = shader.createNode("VRayNodeBRDFBump")
                bump.setName("Bump")
                bump.parm("map_type").set("1")
                bump.parm("bump_tex_mult").set(0.5)
                bump.setNamedInput("base_brdf", surface, "brdf")
                bump.setNamedInput("bump_tex_color", tex, "color")
                if (twoSidedNode is None):
                    shader.children()[0].setNamedInput("Material", bump, "brdf")
                else:
                    bump2 = shader.createNode("VRayNodeBRDFBump")
                    bump2.setName("BumpBack")
                    bump2.parm("map_type").set("1")
                    bump2.parm("bump_tex_mult").set(-0.5)
                    bump2.setNamedInput("base_brdf", surface, "brdf")
                    scaleOp = shader.createNode("VRayNodeTexAColorOp")
                    scaleOp.setNamedInput("color_a", tex, "color")
                    scaleOp.parm("mode").set("2")
                    scaleOp.parm("color_br").set(-1)
                    scaleOp.parm("color_bg").set(-1)
                    scaleOp.parm("color_bb").set(1)
                    offsetOp = shader.createNode("VRayNodeTexAColorOp")
                    offsetOp.setNamedInput("color_a", scaleOp, "color")
                    offsetOp.parm("mode").set("3")
                    offsetOp.parm("color_br").set(1)
                    offsetOp.parm("color_bg").set(1)
                    offsetOp.parm("color_bb").set(0)
                    bump2.setNamedInput("bump_tex_color", offsetOp, "color")
                    twoSidedNode.setNamedInput("front", bump, "brdf")
                    twoSidedNode.setNamedInput("back", bump2, "brdf")                
                    
        if (stMaterial.maps.has_key("Gloss")):
            stmap = stMaterial.maps["Gloss"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Gloss", shader, True)
                rough = shader.createNode("VRayNodeTexInvertFloat")
                rough.setName("Roughness")
                rough.setNamedInput("texture", tex, "intensity")
                surface.setNamedInput("roughness", rough, "value")
                surface.setNamedInput("reflect_glossiness", tex, "intensity")
                surface.setNamedInput("refract_glossiness", tex, "intensity")
            else:
                surface.parm("roughness").set(1.0 - stmap.red)
                surface.parm("reflect_glossiness").set(stmap.red)
                surface.parm("refract_glossiness").set(1.0 - stmap.red)

        if (stMaterial.maps.has_key("Specular")):
            stmap = stMaterial.maps["Specular"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Specular", shader, False)
                surface.setNamedInput("reflect", tex, "color")
            else:
                surface.parm("reflectr").set(stmap.red)
                surface.parm("reflectg").set(stmap.blue)
                surface.parm("reflectb").set(stmap.green)
       
        if ((twoSidedNode is not None) and (stMaterial.maps.has_key("SubsurfaceColor") or stMaterial.maps.has_key("SubsurfaceAmount"))):
            sss = shader.createNode("VRayNodeTexRGBMultiplyMax")
            sss.setName("CombinedSSS")
            twoSidedNode.setNamedInput("translucency_tex", sss, "color")
            
            if (stMaterial.maps.has_key("SubsurfaceColor")):
                stmap = stMaterial.maps["SubsurfaceColor"]
                if (stmap.file):
                    tex = self.MakeTexture(stmap, "SubsurfaceColor", shader, False)
                    sss.setNamedInput("color_a", tex, "color")
                else:
                    sss.parm("color_ar").set(stmap.red)
                    sss.parm("color_ag").set(stmap.blue)
                    sss.parm("color_ab").set(stmap.green)
                
            if (stMaterial.maps.has_key("SubsurfaceAmount")):
                stmap = stMaterial.maps["SubsurfaceAmount"]
                if (stmap.file):
                    tex = self.MakeTexture(stmap, "SubsurfaceAmount", shader, True)
                    scalesss = shader.createNode("VRayNodeTexFloatOp")
                    scalesss.setName("ScaleSSS")
                    scalesss.parm("mode").set("0")
                    scalesss.setNamedInput("float_a", tex, "intensity")
                    sss.setNamedInput("color_b", scalesss, "product")
                else:
                    sss.parm("color_br").set(stmap.red)
                    sss.parm("color_bg").set(stmap.blue)
                    sss.parm("color_bb").set(stmap.green)
                
        shader.layoutChildren()
        return shader 
        
        
################################################################
# SpeedTreeMaterialCreatorRedshift

class SpeedTreeMaterialCreatorRedshift(SpeedTreeMaterialCreator):
    description = "SpeedTree Redshift"
    
    def MakeTexture(self, stMap, name, parent, linear):
        tex = parent.createNode("redshift::TextureSampler")
        tex.setName(name)
        tex.parm("tex0_gammaoverride").set(linear)
        tex.parm("tex0").set(stMap.file)
        return tex
    
    def CreateMaterial(self, stMaterial):
        shader = hou.node("/mat").createNode("redshift_vopnet")
        output = shader.children()[0]
        
        surface = shader.createNode("redshift::Material")
        surface.setName("Surface")
        output.setNamedInput("Surface", surface, "outColor")
                   
        if (stMaterial.maps.has_key("Color")):
            stmap = stMaterial.maps["Color"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Color", shader, False)
                surface.setNamedInput("diffuse_color", tex, "outColor")
            else:
                surface.parm("diffuse_colorr").set(stmap.red)
                surface.parm("diffuse_colorg").set(stmap.blue)
                surface.parm("diffuse_colorb").set(stmap.green)
                  
        if (stMaterial.maps.has_key("Opacity")):
            stmap = stMaterial.maps["Opacity"]
            if (stmap.file):
                spritecutout = shader.createNode("redshift::Sprite")
                spritecutout.parm("tex0").set(stmap.file)
                spritecutout.parm("threshold").set(0.1)
                spritecutout.setNamedInput("input", surface, "outColor")
                output.setNamedInput("Surface", spritecutout, "outColor")
        elif stMaterial.vertexOpacity:
            vopacity = shader.createNode("redshift::VertexAttributeLookup")
            vopacity.setName("BranchBlend")
            vopacity.parm("attribute").set("uv2")
            vopacity.parm("defaultColorr").set(1)
            splitter = shader.createNode("redshift::RSColorSplitter")
            splitter.setNamedInput("input", vopacity, "outColor")
            surface.setNamedInput("opacity_color", splitter, "outR")
            
        if (stMaterial.maps.has_key("Normal")):
            stmap = stMaterial.maps["Normal"]
            if (stmap.file):
                tex = shader.createNode("redshift::NormalMap")
                tex.setName("Normal")
                tex.parm("tex0").set(stmap.file)
                if (stMaterial.twoSided):
                    # set up normals on backside
                    invert = shader.createNode("redshift::RSMathMulVector")
                    invert.setNamedInput("input1", tex, "outDisplacementVector")
                    invert.parm("input21").set(-1)
                    invert.parm("input22").set(-1)
                    invert.parm("input23").set(1)
                    rayswitch = shader.createNode("redshift::RaySwitch")
                    rayswitch.parm("cameraSwitchFrontBack").set(True)
                    rayswitch.setNamedInput("cameraColor", tex, "outDisplacementVector")
                    rayswitch.setNamedInput("cameraColorBack", invert, "out")
                    output.setNamedInput("Bump Map", rayswitch, "outColor")
                else:  
                    output.setNamedInput("Bump Map", tex, "outDisplacementVector")
                
        if (stMaterial.maps.has_key("Gloss")):
            stmap = stMaterial.maps["Gloss"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Gloss", shader, True)
                rough = shader.createNode("redshift::RSMathInvColor")
                rough.setName("Roughness")
                rough.setNamedInput("input", tex, "outColor")
                surface.setNamedInput("diffuse_roughness", rough, "outColor")
                surface.setNamedInput("refl_roughness", rough, "outColor")
            else:
                surface.parm("diffuse_roughness").set(1.0 - stmap.red)
                surface.parm("refl_roughness").set(1.0 - stmap.red)
                   
        surface.parm("refl_brdf").set("1")
        if (stMaterial.maps.has_key("Specular")):
            stmap = stMaterial.maps["Specular"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "Specular", shader, False)
                surface.setNamedInput("refl_color", tex, "outColor")
            else:
                surface.parm("refl_colorr").set(stmap.red)
                surface.parm("refl_colorg").set(stmap.blue)
                surface.parm("refl_colorb").set(stmap.green)
       
        if (stMaterial.maps.has_key("SubsurfaceColor")):
            stmap = stMaterial.maps["SubsurfaceColor"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "SubsurfaceColor", shader, False)
                surface.setNamedInput("transl_color", tex, "outColor")
            else:
                surface.parm("transl_colorr").set(stmap.red)
                surface.parm("transl_colorg").set(stmap.blue)
                surface.parm("transl_colorb").set(stmap.green)
            
        if (stMaterial.maps.has_key("SubsurfaceAmount")):
            stmap = stMaterial.maps["SubsurfaceAmount"]
            if (stmap.file):
                tex = self.MakeTexture(stmap, "SubsurfaceAmount", shader, True)
                surface.setNamedInput("transl_weight", tex, "outColor")
            else:
                surface.parm("transl_weight").set(stmap.red)
                
        shader.layoutChildren()
        return shader  
        

################################################################
# LoadSpeedTree

def LoadSpeedTree(stmatFile, materialCreatorFunc, position):
    stmatFile = os.path.realpath(stmatFile)
    stmatPath = os.path.dirname(stmatFile).replace("\\", "/") + "/"
    
    try:
        doc = xmldom.parse(stmatFile)
        root = doc.getElementsByTagName("Materials");
        if not root:
            print "[" + stmatFile + "] is not a valid stmat file"
            return None
            
        mesh = root[0].attributes["Mesh"].value
        meshFile = stmatPath + mesh
        mesh = os.path.splitext(mesh)[0]
        
        # load speedtree materials and create shaders
        aNewMaterials = { }
        materials = root[0].getElementsByTagName("Material")
        for material in materials:
            stMaterial = SpeedTreeMaterial(material.attributes["Name"].value,
                                            material.attributes["TwoSided"].value == "1",
                                            material.attributes["VertexOpacity"].value == "1",
                                            material.attributes["UserData"].value)
            maps = material.getElementsByTagName("Map")
            for stmap in maps:
                newmap = SpeedTreeMap()
                if (stmap.attributes.has_key("File")):
                    newmap.file = stmatPath + stmap.attributes["File"].value
                    newmap.file = newmap.file.replace("<UDIM>", "%(UDIM)d")
                elif (stmap.attributes.has_key("Value")):
                    newmap.red = newmap.green = newmap.blue = float(stmap.attributes["Value"].value)
                else:
                    newmap.red = float(stmap.attributes["ColorR"].value)
                    newmap.green = float(stmap.attributes["ColorG"].value)
                    newmap.blue = float(stmap.attributes["ColorB"].value)

                stMaterial.maps[stmap.attributes["Name"].value] = newmap
            aNewMaterials[stMaterial.name] = stMaterial
    except:
        #print sys.exc_info()
        print "SpeedTree ERROR: Failed to read SpeedTree stmat file"
        return None
                
    # load mesh
    try:
        extension = os.path.splitext(meshFile)[1]
        if extension == ".obj":
        
            # handle OBJ files
            geoNode = hou.node("/obj").createNode("geo", run_init_scripts=False)
            geoNode.setName(mesh)
            geoNode.parm("tx").set(position[0])
            geoNode.parm("ty").set(position[1])
            geoNode.parm("tz").set(position[2])
            
            fileNode = geoNode.createNode("file")
            fileNode.parm("file").set(meshFile)
            
            if materialCreatorFunc != None:
                try:
                    partNode = fileNode.createOutputNode("partition")
                    partNode.parm("rule").set("$MAT")
                    
                    matNode = partNode.createOutputNode("material")
                    matNode.setDisplayFlag(True)
                    matNode.setRenderFlag(True)
                    matNode.parm("num_materials").set(len(aNewMaterials))
            
                    matNetwork = geoNode.createNode("matnet", "Materials")
                    matNetwork.moveToGoodPosition()
               
                    index = 1
                    for key, value in aNewMaterials.items():
                        value.shader = materialCreatorFunc(value)
                        newnode = hou.moveNodesTo([value.shader], matNetwork)[0]
                        newnode.setName(value.name)
                        value.shader = newnode
                        value.shader.moveToGoodPosition()
                        matNode.parm("group" + str(index)).set("_mat_" + value.name)
                        matNode.parm("shop_materialpath" + str(index)).set(matNode.relativePathTo(value.shader))
                        index += 1
                        
                except:
                    #print sys.exc_info()
                    print "SpeedTree ERROR: Material creation failed"
                    return None
        
        elif extension == ".abc":
            
            # handle Alembic files
            archiveNode = hou.node("/obj").createNode("alembicarchive");
            archiveNode.setName(mesh)
            archiveNode.parm("tx").set(position[0])
            archiveNode.parm("ty").set(position[1])
            archiveNode.parm("tz").set(position[2])
            archiveNode.parm("fileName").set(meshFile)
            archiveNode.parm("buildHierarchy").pressButton()
           
            rendermanMatType = hou.shopNodeTypeCategory().nodeTypes()["risnet"]
            
            if materialCreatorFunc != None:
                try:
                    matNetwork = archiveNode.createNode("matnet", "Materials")
                    matNetwork.moveToGoodPosition()
                    
                    for key, value in aNewMaterials.items():
                        value.shader = materialCreatorFunc(value)
                        newnode = hou.moveNodesTo([value.shader], matNetwork)[0]
                        newnode.setName(value.name)
                        value.shader = newnode
                        value.shader.moveToGoodPosition()
                        if value.shader.type() == rendermanMatType:
                            value.shader = value.shader.node("Surface")
                except:
                    #print sys.exc_info()
                    print "SpeedTree ERROR: Material creation failed"
                    return None
                    
                # unpack and add materials to all alembic sops
                alembicType = hou.sopNodeTypeCategory().nodeTypes()["alembic"]
                aNodeStack = []
                aNodeStack.append(archiveNode)
                while aNodeStack:
                    node = aNodeStack.pop()
                    if node.type() == alembicType:
                        node.parm("remapAttributes").set(1)
                        node.parm("abcName1").set("blend_ao")
                        node.parm("hName1").set("uv2")
                        unpackNode = node.createOutputNode("unpack")
                        matNode = unpackNode.createOutputNode("material")
                        matNode.setDisplayFlag(True)
                        matNode.setRenderFlag(True)
                        primGroups = [g.name() for g in matNode.geometry().primGroups()]
                        matNode.parm("num_materials").set(len(primGroups))
                        for index, group in enumerate(primGroups, 1):
                            matNode.parm("group" + str(index)).set(group)
                            matName = group[:-2] # remove "SG"
                            matNode.parm("shop_materialpath" + str(index)).set(matNode.relativePathTo(aNewMaterials[matName].shader))
                        
                    for child in node.children():
                        aNodeStack.append(child)
            
        
        elif extension == ".fbx":
        
            # handle FBX files
            aBeforeNodes = hou.node("/obj").children()
            hou.hscript('fbximport -o off -k on -s vex "' + meshFile + '"')
            aAfterNodes = hou.node("/obj").children()
            aNodeStack = []
            for node in aAfterNodes:
                if node not in aBeforeNodes:
                    node.setName(mesh)
                    node.parm("tx").set(position[0])
                    node.parm("ty").set(position[1])
                    node.parm("tz").set(position[2])
                    aNodeStack.append(node)
            
            shopType = hou.objNodeTypeCategory().nodeTypes()["shopnet"]
            geoType = hou.objNodeTypeCategory().nodeTypes()["geo"]
            fbxMatType = hou.shopNodeTypeCategory().nodeTypes()["v_fbx"]
            sopMatType = hou.sopNodeTypeCategory().nodeTypes()["material"]
            rendermanMatType = hou.shopNodeTypeCategory().nodeTypes()["risnet"]

            aGeometryNodes = []
            aSopNodes = []
            nodeMaterials = None
            while aNodeStack:
                node = aNodeStack.pop()
                if node.type() == shopType:
                    nodeMaterials = node
                else:
                    if node.type() == geoType:
                        if node.parm("shop_materialpath").eval():
                            aGeometryNodes.append(node)
                    if node.type() == sopMatType:
                        aSopNodes.append(node)
                    for child in node.children():
                        aNodeStack.append(child)

            # make new materials
            if materialCreatorFunc != None:
                try:
                    for key, value in aNewMaterials.items():
                        value.shader = materialCreatorFunc(value)
                        if value.shader.type() == rendermanMatType:
                            value.shader = value.shader.node("/Surface")
                except:
                    print sys.exc_info()
                    print "SpeedTree ERROR: Material creation failed"
                    return None
            
                # assign the unique materials to the geometry
                for node in aGeometryNodes:
                    matNode = node.node(node.parm("shop_materialpath").eval())
                    for matChild in matNode.children():
                        key = matChild.name()[:-8] # remove "_surface"
                        if aNewMaterials.has_key(key):
                            parameter = node.parm("shop_materialpath")
                            parameter.set(node.relativePathTo(aNewMaterials[key].shader))
                            parameter.eval()
                            break
                        
                for node in aSopNodes:
                    num = node.evalParm("num_materials")
                    for i in range(0, num):
                        matNode = node.node(node.parm("shop_materialpath" + str(i + 1)).eval())
                        for matChild in matNode.children():
                            key = matChild.name()[:-8] # remove "_surface"
                            if aNewMaterials.has_key(key):
                                parameter = node.parm('shop_materialpath' + str(i + 1))
                                parameter.set(node.relativePathTo(aNewMaterials[key].shader))
                                parameter.eval()
                                  
                # put the new shaders into the material node
                nodeMaterialsNew = nodeMaterials.parent().createNode("matnet", "Materials")
                nodeMaterials.destroy()
                nodeMaterialsNew.moveToGoodPosition()
                for key, value in aNewMaterials.items():
                    newnode = hou.moveNodesTo([value.shader], nodeMaterialsNew)[0]
                    newnode.setName(value.name)
                    newnode.moveToGoodPosition()
                    value.shader = newnode
                    
        elif extension == ".usd":
            
            # handle USD files
            geoNode = hou.node("/obj").createNode("geo", run_init_scripts=False)
            geoNode.setName(mesh)
            geoNode.parm("tx").set(position[0])
            geoNode.parm("ty").set(position[1])
            geoNode.parm("tz").set(position[2])
            
            fileNode = geoNode.createNode("usdimport")
            fileNode.parm("primpattern").set("* ^ */LeafMeshes/*")
            fileNode.parm("importtime").setExpression("$FF")
            fileNode.parm("input_unpack").set(True)
            fileNode.parm("unpack_geomtype").set(1)
            fileNode.parm("filepath1").set(meshFile)
            
            if materialCreatorFunc != None:
                try:
                    matNode = fileNode.createOutputNode("material")
                    matNode.setDisplayFlag(True)
                    matNode.setRenderFlag(True)
                    matNode.parm("num_materials").set(len(aNewMaterials))
            
                    matNetwork = geoNode.createNode("matnet", "Materials")
                    matNetwork.moveToGoodPosition()
               
                    index = 1
                    for key, value in aNewMaterials.items():
                        value.shader = materialCreatorFunc(value)
                        newnode = hou.moveNodesTo([value.shader], matNetwork)[0]
                        newnode.setName(value.name)
                        value.shader = newnode
                        value.shader.moveToGoodPosition()
                        matNode.parm("group" + str(index)).set(value.name + "SG")
                        matNode.parm("shop_materialpath" + str(index)).set(matNode.relativePathTo(value.shader))
                        index += 1
                        
                except:
                    print sys.exc_info()
                    print "SpeedTree ERROR: Material creation failed"
                    return None
                    
        else:
            print "SpeedTree ERROR: Unsupported mesh file type"
            return None
            
    except:
        #print sys.exc_info()
        print "SpeedTree ERROR: Failed to load mesh file [" + meshFile + "]"
        return None
        
    
################################################################
# LoadSpeedTreeGUI

def LoadSpeedTreeGUI(node=None):
    # ask for filename
    stmatFile = hou.ui.selectFile(title="Select SpeedTree File", file_type=hou.fileType.Any, pattern = "*.stmat")
    stmatFile = os.path.expandvars(stmatFile)
    if not stmatFile:
        print "SpeedTree import cancelled"
    else:
        # ask for the shader type to make
        aMaterialCreatorNames = []
        for subclass in SpeedTreeMaterialCreator.__subclasses__():
            aMaterialCreatorNames.append(subclass.description)
        aMaterialCreatorNames.append("No change")
        materialType = hou.ui.selectFromList(aMaterialCreatorNames, [0], True, "Choose the type of shader to use for the SpeedTree materials", "Materials")
        if not materialType:
            print "SpeedTree import cancelled"
        else:
            materialCreatorFunc = None
            if materialType[0] < len(SpeedTreeMaterialCreator.__subclasses__()):
                materialCreatorFunc = SpeedTreeMaterialCreator.__subclasses__()[materialType[0]]().CreateMaterial
            
            position = [0, 0, 0]
            if node != None:
                position = node.parmTuple('t').eval()
            LoadSpeedTree(stmatFile, materialCreatorFunc, position)
    
    if node != None:
        node.destroy()
    
            
            
    
