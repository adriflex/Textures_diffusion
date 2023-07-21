import bpy


class SDTextureProj_PT_Panel(bpy.types.Panel):
    bl_label = "SD Texture Projector"
    bl_idname = "SDTextureProj_PT_Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Stable Diffusion"

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)
        column.label(text="Projection scene :")
        column.operator("sd_texture_proj.create_new_proj_scene", icon="SCENE_DATA")
        column.operator("sd_texture_proj.render_ref_img")
        # column.prop(context.scene, "masks_resolution", text="Masks resolution")
        # column.prop(context.scene, "masks_sampling", text="Masks sampling")
        column.operator("sd_texture_proj.bake_proj_masks")
        column.operator("sd_texture_proj.create_proj_uvs")

        if "Proj collection" in context.scene:
            box = layout.box()
            box.use_property_split = True
            box.use_property_decorate = False

            column6 = box.column(align=True)
            column6.label(text="Scene format :")
            column6.prop(context.scene.render, "resolution_x")
            column6.prop(context.scene.render, "resolution_y", text="Y")

            column5 = box.column(align=True)
            column5.label(text="Masks settings :")
            column5.prop(context.scene.sd_texture_props, "masks_resolution", text="Resolution")
            column5.prop(context.scene.sd_texture_props, "masks_samples", text="Samples")
            column5.prop(context.scene.sd_texture_props, "use_mirror_X", text="Symmetry X")



        if "Proj collection" in context.scene or "Projection scene" in context.scene:
            column2 = layout.column(align=True)
            column2.label(text="Shading scene :")
            column2.prop(context.scene.sd_texture_props, "img_generated_path", text="SD image path")

        column3 = layout.column(align=True)
        column3.operator("sd_texture_proj.create_new_shading_scene", icon="MATSHADERBALL")
        column3.operator("sd_texture_proj.transfer_tweaked_uvs")
        column3.operator("sd_texture_proj.reload_sd_img_path")

        if "Custom mask" in context.active_object:
            column4 = layout.column(align=True)
            column4.label(text="Custom mask :")
            column4.operator("sd_texture_proj.paint_custom_mask")
            column4.operator("image.save_all_modified", text="Save all images", icon='FILE_TICK')

# todo another panel for the settings
