bl_info = {
    "name": "SD texture projector",
    "author": "Adrien Rouquié",
    "version": (0, 1),
    "blender": (3, 3, 7),
    "location": "View3D",
    "description": "Create a scene to bake maps to send to Stable Diffusion",
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
        importlib.reload(sd_texture_ui)

from . import sd_texture_operators
from . import sd_texture_ui

register_classes = [
    sd_texture_operators.SDTextureProj_OT_CreateNewProjScene,
    sd_texture_operators.SDTextureProj_OT_RenderRefImg,
    sd_texture_operators.SDTextureProj_OT_BakeProjMasks,
    sd_texture_operators.SDTextureProj_OT_CreateProjUVs,
    sd_texture_operators.SDTextureProj_OT_CreateNewShadingScene,
    sd_texture_operators.SD_OT_transfer_tweaked_uvs,
    sd_texture_operators.SD_OT_reload_sd_img_path,
    sd_texture_ui.SDTextureProj_PT_Panel,
]


def register():
    for cls in register_classes:
        bpy.types.Scene.img_generated_path = bpy.props.StringProperty(
            name="IMG Generated Path",
            description="Path to the Stable Diffusion image",
            default="//",
            subtype="FILE_PATH",
        )
        bpy.utils.register_class(cls)
        print("Registered class: ", cls)


def unregister():
    for cls in register_classes:
        del bpy.types.Scene.img_generated_path
        bpy.utils.unregister_class(cls)
        print("Unregistered class: ", cls)
