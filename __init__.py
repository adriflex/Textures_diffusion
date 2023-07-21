bl_info = {
    "name": "SD texture projector",
    "author": "Adrien Rouquié",
    "version": (0, 1),
    "blender": (3, 3, 7),
    "location": "View3D > Sidebar > Stable Diffusion",
    "description": "Generate textures using Stable Diffusion web ui",
    "warning": "",
    "doc_url": "",
    "category": "Texture",
}
import bpy

if "bpy" in locals():
    import importlib

    if "sd_texture_operators" in locals():
        importlib.reload(sd_texture_operators)
        importlib.reload(sd_texture_functions)
        importlib.reload(properties)
        importlib.reload(sd_texture_ui)

from . import sd_texture_operators
from . import properties
from . import sd_texture_ui

register_classes = [
    sd_texture_operators.SDTextureProj_OT_CreateNewProjScene,
    sd_texture_operators.SDTextureProj_OT_RenderRefImg,
    sd_texture_operators.SDTextureProj_OT_BakeProjMasks,
    sd_texture_operators.SDTextureProj_OT_CreateProjUVs,
    sd_texture_operators.SDTextureProj_OT_CreateNewShadingScene,
    sd_texture_operators.SD_OT_transfer_tweaked_uvs,
    sd_texture_operators.SD_OT_reload_sd_img_path,
    properties.sd_texture_prop_group,
    sd_texture_ui.SDTextureProj_PT_Panel,
]


def register():
    for cls in register_classes:
        bpy.utils.register_class(cls)
        print("Registered class: ", cls)
    bpy.types.Scene.sd_texture_props = bpy.props.PointerProperty(type=properties.sd_texture_prop_group)


def unregister():
    for cls in register_classes:
        bpy.utils.unregister_class(cls)
        print("Unregistered class: ", cls)
    del bpy.types.Scene.sd_texture_props
