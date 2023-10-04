'''
Copyright (C) 2023 Blender Foundation and Adrien Rouquié
https://blender.org
https://www.linkedin.com/in/adrien-rouquie/

orangeturbine@cgcookie.com

Created by the Blender Foundation, modified by Adrien Rouquié.

This file is part of a Texture Diffusion add-on.

    Texture Diffusion is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <https://www.gnu.org/licenses>.

'''

bl_info = {
    "name": "Textures diffusion",
    "author": "Adrien Rouquié",
    "version": (1, 0),
    "blender": (3, 3, 7),
    "location": "View3D > Sidebar > Stable Diffusion",
    "description": "Project textures using Stable Diffusion web ui",
    "warning": "",
    "doc_url": "",
    "category": "Stable Diffusion",
}
import bpy

if "bpy" in locals():
    import importlib

    if "operators" in locals():
        importlib.reload(operators)
        importlib.reload(functions)
        importlib.reload(properties)
        importlib.reload(ui)

from . import operators
from . import properties
from . import ui

register_classes = [
    operators.TexDiff_OT_CreateNewProjScene,
    operators.TexDiff_OT_RenderRefImg,
    operators.TexDiff_OT_BakeProjMasks,
    operators.TexDiff_OT_CreateProjUVs,
    operators.TexDiff_OT_CreateNewShadingScene,
    operators.TexDiff_OT_TweakProjection,
    operators.TexDiff_OT_TransferTweakedUvs,
    operators.TexDiff_OT_ReloadSdImgPath,
    operators.TexDiff_OT_PaintCustomMask,
    operators.TexDiff_OT_BakeProjection,
    properties.TexDiff_prop_group,
]


def register():
    for cls in register_classes:
        bpy.utils.register_class(cls)
        print("Registered class: ", cls)
    bpy.types.Scene.textures_diffusion_props = bpy.props.PointerProperty(type=properties.TexDiff_prop_group)
    print("Registered property: ", bpy.types.Scene.textures_diffusion_props)
    ui.register()


def unregister():
    ui.unregister()
    del bpy.types.Scene.textures_diffusion_props
    for cls in register_classes:
        bpy.utils.unregister_class(cls)
        print("Unregistered class: ", cls)
    print("Unregistered property: ", bpy.types.Scene.textures_diffusion_props)
