import bpy

shading_mesh_prop_name = "Shading mesh"

class TexDiff_PT_Panel(bpy.types.Panel):
    bl_label = "SD Texture Projector"
    bl_idname = "TexDiff_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stable Diffusion"

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        column.label(text="Projection scene :")
        column.operator("textures_diffusion.create_new_proj_scene", icon="SCENE_DATA")
        column.operator("textures_diffusion.render_ref_img")
        # column.prop(context.scene, "masks_resolution", text="Masks resolution")
        # column.prop(context.scene, "masks_sampling", text="Masks sampling")
        column.operator("textures_diffusion.bake_proj_masks")
        column.operator("textures_diffusion.create_proj_uvs")

        if "Proj collection" in context.scene:
            box = layout.box()
            box.use_property_split = True
            box.use_property_decorate = False

            column8 = box.column(align=True)
            column8.label(text="Scene format :")
            column8.prop(context.scene.render, "resolution_x")
            column8.prop(context.scene.render, "resolution_y", text="Y")

            column5 = box.column(align=True)
            column5.label(text="Masks settings :")
            column5.prop(context.scene.textures_diffusion_props, "masks_resolution", text="Resolution")
            column5.prop(context.scene.textures_diffusion_props, "masks_samples", text="Samples")
            column5.prop(context.scene.textures_diffusion_props, "use_mirror_X", text="Symmetry X")

        if "Proj collection" in context.scene or "Projection scene" in context.scene:
            column2 = layout.column(align=True)
            column2.label(text="Shading scene :")
            column2.prop(context.scene.textures_diffusion_props, "img_generated_path", text="SD image path")

        column3 = layout.column(align=True)
        column3.operator("textures_diffusion.create_new_shading_scene", icon="MATSHADERBALL")
        column3.operator("textures_diffusion.reload_sd_img_path")
        column3.operator("textures_diffusion.bake_projection", icon="RENDER_STILL")

        if context.active_object:
            if "Custom mask" in context.active_object:
                column4 = layout.column(align=True)
                column4.label(text="Custom mask :")
                column4.operator("textures_diffusion.paint_custom_mask")
                column4.operator("image.save_all_modified", text="Save all images", icon='FILE_TICK')

            if "UVProject" in context.active_object.modifiers:
                column7 = layout.column(align=True)
                column7.label(text="Projection tweaks :")
                column7.operator("textures_diffusion.tweak_projection", text="Edit tweaks")
                column7.operator("textures_diffusion.transfer_tweaked_uvs", text="Transfer tweaks")

            if shading_mesh_prop_name in context.scene.keys():
                if context.scene[shading_mesh_prop_name] == context.active_object:
                    box2 = column3.box()
                    box2.use_property_split = True
                    box2.use_property_decorate = False

                    column8 = box2.column(align=True)
                    column8.prop(context.scene.textures_diffusion_props, "bake_resolution")


# todo another panel for the ref image settings
