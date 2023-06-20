from math import radians

import bpy

from . import sd_texture_functions


class SDTextureProj_OT_CreateProjScene(bpy.types.Operator):
    bl_idname = "sd_texture_proj.create_scene"
    bl_label = "Create scene"
    bl_description = "Create a scene to bake maps to send to Stable Diffusion"

    # poll function
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        # Duplicate the active object and link it to the subjects collection
        active_obj = context.active_object

        sd_scene_data = bpy.data.scenes.new(name=f"{active_obj.name} SD textures bake")

        # Create collection to store the objects
        mesh_collection = bpy.data.collections.new(name="Mesh")
        sd_scene_data.collection.children.link(mesh_collection)
        sd_scene_data["Mesh collection"] = mesh_collection

        # Create a new camera
        camera_data = bpy.data.cameras.new(name="SD_Camera")
        camera_obj = bpy.data.objects.new(name="SD_Camera", object_data=camera_data)
        sd_scene_data.collection.objects.link(camera_obj)

        # set the scene camera
        sd_scene_data.camera = camera_obj

        camera_data.type = 'ORTHO'
        camera_obj.location = (0, -10, 0)
        camera_obj.rotation_euler = (radians(90), 0, 0)

        # Store the subject name in a custom property
        sd_scene_data["Subject mesh"] = active_obj

        active_obj_copy_1 = active_obj.copy()
        active_obj_copy_1.data = active_obj.data.copy()
        active_obj_copy_1.location = (-1.5, 0, 0)
        active_obj_copy_1.rotation_euler = (0, 0, 0)
        mesh_collection.objects.link(active_obj_copy_1)

        active_obj_copy_2 = active_obj.copy()
        active_obj_copy_2.data = active_obj.data.copy()
        active_obj_copy_2.location = (1.5, 0, 0)
        active_obj_copy_2.rotation_euler = (0, 0, radians(90))
        mesh_collection.objects.link(active_obj_copy_2)

        # Set the scene the active one
        bpy.context.window.scene = sd_scene_data

        return {'FINISHED'}


class SDTextureProj_OT_BakeMapsForSD(bpy.types.Operator):
    bl_idname = "sd_texture_proj.bake_maps"
    bl_label = "Bake maps"
    bl_description = "Bake maps to send to Stable Diffusion"

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the .blend file before baking")
            return {'CANCELLED'}

        # get the scene info
        sd_scene_data = sd_texture_functions.get_sd_setup_scene_data()

        # change the mouse cursor to a watch
        bpy.context.window.cursor_set("WAIT")

        scene_name = sd_scene_data["blend_name"]
        subject_name = sd_scene_data["subject_mesh"].name

        sd_texture_functions.render_beauty(scene_name, subject_name)

        sd_texture_functions.render_normal(scene_name, subject_name)

        sd_texture_functions.render_depth(scene_name, subject_name)

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        # tell the user the maps have been baked
        self.report({'INFO'}, "Baking done ! Check the folder 'SD_maps' in the same folder as the .blend file")

        return {'FINISHED'}


class SDTextureProj_OT_BakeSDMeshes(bpy.types.Operator):
    bl_idname = "sd_texture_proj.bake_sd_mesh"
    bl_label = "Bake SD mesh"
    bl_description = "Bake projection masks and UVs"

    # todo > undo render params
    # todo > parameter mirror : bool and axis : "X", "Y", "Z"

    def execute(self, context):

        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the .blend file before baking")
            return {'CANCELLED'}

        sd_scene_data = sd_texture_functions.get_sd_setup_scene_data()
        mesh_collection = sd_scene_data["mesh_collection"]
        scene_name = sd_scene_data["blend_name"]
        subject_name = sd_scene_data["subject_mesh"].name

        # change the mouse cursor to a watch
        bpy.context.window.cursor_set("WAIT")

        for obj in mesh_collection.objects:
            assert obj.type == "MESH", f"Object {obj.name} is not a mesh"

            # bake the facing mask
            facing_img_mask_path = sd_texture_functions.render_facing(scene_name, subject_name)
            bpy.data.images.load(facing_img_mask_path)

            # bake the shadowing mask
            image_name = f"{obj.name}_shadowing_mask"
            shadowing_img_path = sd_texture_functions.render_shadowing(obj, sd_scene_data['blend_name'], image_name)

            # project the UVs
            uv_layer_name = f"{obj.name}_cam_proj"
            uv_layer_proj_name = sd_texture_functions.project_uvs_from_camera(obj, sd_scene_data['camera'],
                                                                              uv_layer_name)

            # mirror
            sd_texture_functions.mirror_obj(obj, "X")

            image_name = f"{obj.name}_shadowing_mask_mirrored"
            shadowing_mirrored_img_path = sd_texture_functions.render_shadowing(obj, sd_scene_data['blend_name'],
                                                                                image_name)

            uv_layer_name = f"{obj.name}_cam_proj_mirrored"
            uv_layer_proj_mirrored_name = sd_texture_functions.project_uvs_from_camera(obj, sd_scene_data['camera'],
                                                                                       uv_layer_name)

            sd_texture_functions.mirror_obj(obj, "X")

            # add file output to the object custom properties
            obj["Shadowing img path"] = shadowing_img_path
            obj["UV Map name"] = uv_layer_proj_name

            obj["Shadowing mirrored img path"] = shadowing_mirrored_img_path
            obj["UV Map mirrored name"] = uv_layer_proj_mirrored_name

            # get active scene
            scene = bpy.context.scene
            scene["Facing img path"] = facing_img_mask_path

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        # tell the user the maps have been baked
        self.report({'INFO'}, "Baking done !")

        return {'FINISHED'}


class SDTextureProj_OT_CreateShadingScene(bpy.types.Operator):
    bl_idname = "sd_texture_proj.create_shading_scene"
    bl_label = "Create shading scene"
    bl_description = "Create a shading scene to apply the SD textures"

    def execute(self, context):
        sd_scene_data = sd_texture_functions.get_sd_setup_scene_data()
        sd_meshes_data = sd_texture_functions.get_sd_scene_meshes(sd_scene_data)
        subject_mesh = sd_scene_data["subject_mesh"]
        subject_name = subject_mesh.name

        shading_scene_name = f"{subject_name} SD shading"

        if shading_scene_name not in bpy.data.scenes:
            shading_scene = sd_texture_functions.create_shading_scene(shading_scene_name, subject_mesh)
        else:
            shading_scene = bpy.data.scenes[shading_scene_name]

        context.window.scene = shading_scene

        sd_texture_functions.transfer_uvs_from_proj_to_shading(context, sd_scene_data, shading_scene['Subject mesh'])

        # create a new material for the shading
        shading_mat = sd_texture_functions.create_sd_shading_mat(subject_name, sd_meshes_data)

        # todo assign the material to the shading mesh

        return {'FINISHED'}
