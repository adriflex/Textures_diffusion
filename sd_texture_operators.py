from math import radians

import bpy

from . import materials
from . import sd_texture_functions

subject_prop_name = "Subject mesh"
proj_collection_prop_name = "Proj collection"
img_dir_prop_name = "Image directory"
facing_path_prop_name = "Facing mask path"
facing_path_mirrored_prop_name = "Facing mask path mirrored"
camera_occlusion_prop_name = "Camera occlusion"
camera_occlusion_mirrored_prop_name = "Camera occlusion mirrored"
uv_layer_proj_prop_name = "UV layer projection"
uv_layer_proj_mirrored_prop_name = "UV layer projection mirrored"
shading_mesh_prop_name = "Shading mesh"


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

        sd_proj_scene = bpy.data.scenes.new(name=f"{active_obj.name} SD textures bake")

        mesh_collection = bpy.data.collections.new(name=f"{active_obj.name} projection meshes")
        sd_proj_scene.collection.children.link(mesh_collection)

        camera_data = bpy.data.cameras.new(name="SD_Camera")
        camera_obj = bpy.data.objects.new(name="SD_Camera", object_data=camera_data)
        sd_proj_scene.collection.objects.link(camera_obj)
        sd_proj_scene.camera = camera_obj
        camera_data.type = 'ORTHO'
        camera_obj.location = (0, -10, 0)
        camera_obj.rotation_euler = (radians(90), 0, 0)

        # Store custom properties
        sd_proj_scene[subject_prop_name] = active_obj
        sd_proj_scene[proj_collection_prop_name] = mesh_collection

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
        bpy.context.window.scene = sd_proj_scene

        return {'FINISHED'}


class SDTextureProj_OT_RenderRefImg(bpy.types.Operator):
    bl_idname = "sd_texture_proj.render_ref_images"
    bl_label = "Render ref images"
    bl_description = "Render image to use in Stable Diffusion"

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the .blend file before baking")
            return {'CANCELLED'}

        proj_scene = context.scene

        if proj_collection_prop_name not in proj_scene.keys():
            self.report({'ERROR'}, "No projection collection found. Please create projection scene")
            return {'CANCELLED'}

        if subject_prop_name not in proj_scene.keys():
            self.report({'ERROR'}, "No subject mesh found. Please create projection scene")
            return {'CANCELLED'}

        sd_texture_functions.create_img_dir(proj_scene)

        subject_name = proj_scene[subject_prop_name].name
        image_directory = proj_scene[img_dir_prop_name]

        beauty_path = f"{image_directory}/{subject_name}_beauty.png"
        normal_path = f"{image_directory}/{subject_name}_normal.png"
        depth_path = f"{image_directory}/{subject_name}_depth.png"

        bpy.context.window.cursor_set("WAIT")

        sd_texture_functions.render_beauty(beauty_path)

        sd_texture_functions.render_normal(normal_path)

        sd_texture_functions.render_depth(depth_path, proj_scene[proj_collection_prop_name])

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        # tell the user the maps have been baked
        self.report({'INFO'}, "Baking done ! Check the folder 'SD_maps' in the same folder as the .blend file")

        return {'FINISHED'}


class SDTextureProj_OT_BakeProjMasks(bpy.types.Operator):
    bl_idname = "sd_texture_proj.bake_proj_masks"
    bl_label = "Bake projection masks"
    bl_description = "Bake camera occlusion and facing masks"

    # todo > undo render params
    # todo > parameter mirror : bool and axis : "X", "Y", "Z"

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the .blend file before baking")
            return {'CANCELLED'}

        proj_scene = context.scene

        if proj_collection_prop_name not in proj_scene.keys():
            self.report({'ERROR'}, "No projection collection found. Please create projection scene")
            return {'CANCELLED'}

        sd_texture_functions.create_img_dir(proj_scene)

        collection = proj_scene[proj_collection_prop_name]
        image_directory = proj_scene[img_dir_prop_name]

        bpy.context.window.cursor_set("WAIT")

        for obj in collection.objects:
            assert obj.type == "MESH", f"Object {obj.name} is not a mesh"

            facing_path = f"{image_directory}/{obj.name}_facing_mask.exr"
            facing_mirrored_path = f"{image_directory}/{obj.name}_facing_mask_mirrored.exr"
            camera_occlusion_path = f"{image_directory}/{obj.name}_camera_occlusion_mask.exr"
            camera_occlusion_mirrored_path = f"{image_directory}/{obj.name}_camera_occlusion_mask_mirrored.exr"

            # bake masks
            sd_texture_functions.render_facing(obj, facing_path)

            sd_texture_functions.render_camera_occlusion(obj, camera_occlusion_path)

            # mirror
            sd_texture_functions.mirror_obj(obj, "X")

            sd_texture_functions.render_facing(obj, facing_mirrored_path)
            sd_texture_functions.render_camera_occlusion(obj, camera_occlusion_mirrored_path)

            sd_texture_functions.mirror_obj(obj, "X")

            # add file output to the object custom properties
            obj[facing_path_prop_name] = facing_path
            obj[facing_path_mirrored_prop_name] = facing_mirrored_path
            obj[camera_occlusion_prop_name] = camera_occlusion_path
            obj[camera_occlusion_mirrored_prop_name] = camera_occlusion_mirrored_path

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        # tell the user the maps have been baked
        self.report({'INFO'}, "Baking done !")

        return {'FINISHED'}


class SDTextureProj_OT_CreateProjUVs(bpy.types.Operator):
    bl_idname = "sd_texture_proj.create_proj_uvs"
    bl_label = "Create Projected UVs"
    bl_description = "Project the UVs of the collection from the camera"

    def execute(self, context):

        proj_scene = context.scene

        if proj_collection_prop_name not in proj_scene.keys():
            self.report({'ERROR'}, "No projection collection found. Please create projection scene")
            return {'CANCELLED'}

        if proj_scene.camera is None:
            self.report({'ERROR'}, "No camera found. Please create projection scene")
            return {'CANCELLED'}

        collection = proj_scene[proj_collection_prop_name]
        camera = proj_scene.camera

        for obj in collection.objects:
            assert obj.type == "MESH", f"Object {obj.name} is not a mesh"

            # project the UVs
            uv_layer_name = f"{obj.name}_cam_proj"
            sd_texture_functions.project_uvs_from_camera(obj, camera, uv_layer_name)

            # mirror
            sd_texture_functions.mirror_obj(obj, "X")

            uv_layer_mirrored_name = f"{obj.name}_cam_proj_mirrored"
            sd_texture_functions.project_uvs_from_camera(obj, camera, uv_layer_mirrored_name)

            sd_texture_functions.mirror_obj(obj, "X")

            # add file output to the object custom properties
            obj[uv_layer_proj_prop_name] = uv_layer_name
            obj[uv_layer_proj_mirrored_prop_name] = uv_layer_mirrored_name

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        # tell the user the maps have been baked
        self.report({'INFO'}, "UVs projected !")

        return {'FINISHED'}


class SDTextureProj_OT_CreateShadingScene(bpy.types.Operator):
    bl_idname = "sd_texture_proj.create_shading_scene"
    bl_label = "Create shading scene"
    bl_description = "Create a shading scene to apply the SD textures"

    def execute(self, context):
        # sd_scene_data = sd_texture_functions.get_sd_setup_scene_data()
        # sd_meshes_data = sd_texture_functions.get_sd_scene_meshes(sd_scene_data)
        # subject_mesh = sd_scene_data["subject_mesh"]
        # subject_name = subject_mesh.name
        # mesh_collection = sd_scene_data["mesh_collection"]

        proj_scene = context.scene
        subject_mesh = proj_scene[subject_prop_name]
        subject_name = subject_mesh.name
        proj_mesh_collection = proj_scene[proj_collection_prop_name]

        shading_scene_name = f"{subject_name} SD shading"

        def create_shading_scene(scene_name: str, mesh) -> bpy.types.Scene:
            # create a new scene for the shading
            scene = bpy.data.scenes.new(name=scene_name)

            # copy the mesh into the shading scene
            scene_mesh = mesh.copy()
            scene_mesh.data = mesh.data.copy()
            scene_mesh.name = f"{mesh.name}_shading"
            scene_mesh.data.name = f"{mesh.name}_shading"

            scene.collection.objects.link(scene_mesh)

            scene[shading_mesh_prop_name] = scene_mesh

            return scene

        if shading_scene_name not in bpy.data.scenes:
            shading_scene = create_shading_scene(shading_scene_name, subject_mesh)
        else:
            shading_scene = bpy.data.scenes[shading_scene_name]

        # transfer proj UVs
        context.window.scene = shading_scene
        shading_mesh = shading_scene[shading_mesh_prop_name]
        shading_scene.collection.children.link(proj_mesh_collection)

        for obj in proj_mesh_collection.objects:
            if not obj.type == "MESH":
                self.report({'ERROR'}, f"Object {obj.name} is not a mesh")

            if obj["UV Map name"] not in obj.data.uv_layers.keys():
                self.report({'ERROR'}, f"Projection uvs not found in object {obj.name}")

            uv_layer = obj[uv_layer_proj_prop_name]
            uv_layer_mirrored = obj[uv_layer_proj_mirrored_prop_name]

            sd_texture_functions.transfer_uvs(obj, shading_mesh, uv_layer)
            sd_texture_functions.transfer_uvs(obj, shading_mesh, uv_layer_mirrored)

        shading_scene.collection.children.unlink(proj_mesh_collection)

        # create a new material for the shading
        shading_mat = materials.create_sd_shading_mat()  # todo create mat function

        # todo assign the material to the shading mesh

        return {'FINISHED'}
