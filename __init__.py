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

from . import sd_texture_operators

register_classes = [
    sd_texture_operators.SDTextureProj_OT_CreateProjScene,
    sd_texture_operators.SDTextureProj_OT_BakeMapsForSD,
    sd_texture_operators.SDTextureProj_OT_BakeSDMeshes,
    sd_texture_operators.SDTextureProj_OT_CreateShadingScene,
]


def register():
    for cls in register_classes:
        bpy.utils.register_class(cls)
        print("Registered class: ", cls)


def unregister():
    for cls in register_classes:
        bpy.utils.unregister_class(cls)
        print("Unregistered class: ", cls)
