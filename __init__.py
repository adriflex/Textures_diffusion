bl_info = {
    "name": "Textures diffusion",
    "author": "Adrien Rouquié",
    "version": (1, 0),
    "blender": (3, 3, 7),
    "location": "View3D > Sidebar > Stable Diffusion",
    "description": "Project textures using Stable Diffusion web ui",
    "warning": "",
    "doc_url": "",
    "category": "Material",
}
import bpy

if "bpy" in locals():
    import importlib

    if "sd_texture_operators" in locals():
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
    operators.TexDiff_OT_transferTweakedUvs,
    operators.TexDiff_OT_reloadSdImgPath,
    operators.TexDiff_OT_paintCustomMask,
    operators.TexDiff_OT_tweakProjection,
    properties.TexDiff_prop_group,
    ui.TexDiff_PT_Panel,
]


def register():
    for cls in register_classes:
        bpy.utils.register_class(cls)
        print("Registered class: ", cls)
    bpy.types.Scene.textures_diffusion_props = bpy.props.PointerProperty(type=properties.TexDiff_prop_group)


def unregister():
    for cls in register_classes:
        bpy.utils.unregister_class(cls)
        print("Unregistered class: ", cls)
    del bpy.types.Scene.textures_diffusion_props
