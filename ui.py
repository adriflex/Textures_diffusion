"""
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

"""
import os

import bpy
import bpy.utils.previews

shading_mesh_prop_name = "Shading mesh"

# Preview collections for icons
preview_collections = {}


class TexDiff_PT_Panel(bpy.types.Panel):
    bl_label = "Textures Diffusion"
    bl_idname = "TexDiff_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stable Diffusion"

    def draw(self, context):
        layout = self.layout

        # Icons
        preview_coll = preview_collections["main"]
        tex_diff_icon = preview_coll["text_diff"]

        column = layout.column(align=True)
        column.label(text="Projection scene :")
        column.operator("textures_diffusion.create_new_proj_scene", icon="SCENE_DATA")
        column.operator("textures_diffusion.render_ref_img")
        column.operator("textures_diffusion.bake_proj_masks")
        column.operator("textures_diffusion.create_proj_uvs")

        if "Proj collection" in context.scene:
            box = layout.box()
            box.use_property_split = True
            box.use_property_decorate = False

            column6 = box.column(align=True)
            column6.label(text="Scene format :")
            column6.prop(context.scene.render, "resolution_x")
            column6.prop(context.scene.render, "resolution_y", text="Y")

            column2 = box.column(align=True)
            column2.label(text="Image ref :")
            column2.prop(
                context.scene.textures_diffusion_props,
                "enable_normal_ref",
                text="Normal",
            )
            column2.prop(
                context.scene.textures_diffusion_props, "enable_depth_ref", text="Depth"
            )
            column2.prop(
                context.scene.textures_diffusion_props,
                "enable_beauty_ref",
                text="Beauty",
            )

            column5 = box.column(align=True)
            column5.label(text="Masks settings :")
            column5.prop(
                context.scene.textures_diffusion_props,
                "masks_resolution",
                text="Resolution",
            )
            column5.prop(
                context.scene.textures_diffusion_props, "masks_samples", text="Samples"
            )
            column5.prop(
                context.scene.textures_diffusion_props,
                "use_mirror_X",
                text="Symmetry X",
            )

        if "Proj collection" in context.scene or "Projection scene" in context.scene:
            column2 = layout.column(align=True)
            column2.label(text="Shading scene :")
            column2.prop(
                context.scene.textures_diffusion_props,
                "img_generated_path",
                text="SD image path",
            )

        column3 = layout.column(align=True)
        column3.operator(
            "textures_diffusion.create_new_shading_scene",
            icon_value=tex_diff_icon.icon_id,
        )  # "MATSHADERBALL"
        column3.operator("textures_diffusion.reload_sd_img_path")
        column3.operator("textures_diffusion.bake_projection", icon="RENDER_STILL")

        if context.active_object:
            if "Custom mask" in context.active_object:
                column4 = layout.column(align=True)
                column4.label(text="Custom mask :")
                column4.operator("textures_diffusion.paint_custom_mask")
                column4.operator(
                    "image.save_all_modified", text="Save all images", icon="FILE_TICK"
                )

            if "UVProject" in context.active_object.modifiers:
                column7 = layout.column(align=True)
                column7.label(text="Projection tweaks :")
                column7.operator(
                    "textures_diffusion.tweak_projection", text="Edit tweaks"
                )
                column7.operator(
                    "textures_diffusion.transfer_tweaked_uvs", text="Transfer tweaks"
                )

            if shading_mesh_prop_name in context.scene.keys():
                if context.scene[shading_mesh_prop_name] == context.active_object:
                    box2 = column3.box()
                    box2.use_property_split = True
                    box2.use_property_decorate = False

                    column8 = box2.column(align=True)
                    column8.prop(
                        context.scene.textures_diffusion_props, "bake_resolution"
                    )


def register():
    preview_coll = bpy.utils.previews.new()

    icons_dir = os.path.join(os.path.dirname(__file__), "tex_diff_icon.png")
    preview_coll.load("text_diff", icons_dir, "IMAGE")

    preview_collections["main"] = preview_coll

    bpy.utils.register_class(TexDiff_PT_Panel)


def unregister():
    for preview_coll in preview_collections.values():
        bpy.utils.previews.remove(preview_coll)
    preview_collections.clear()

    bpy.utils.unregister_class(TexDiff_PT_Panel)
