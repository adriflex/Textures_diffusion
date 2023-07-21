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
        column.operator("sd_texture_proj.create_new_proj_scene", icon="SCENE_DATA")
        column.operator("sd_texture_proj.render_ref_img")
        column.operator("sd_texture_proj.bake_proj_masks")
        column.operator("sd_texture_proj.create_proj_uvs")

        column = layout.column(align=True)
        if context.scene.img_generated_path:
            column.prop(context.scene, "img_generated_path", text="SD image path")

        column1 = layout.column(align=True)
        column1.operator("sd_texture_proj.create_new_shading_scene", icon="MATSHADERBALL")
        column1.operator("sd_texture_proj.transfer_tweaked_uvs")
        column1.operator("sd_texture_proj.reload_sd_img_path")

# todo another panel for the settings
