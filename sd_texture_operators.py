from math import radians

import bpy
from . import material_shading
# from . import materials_baking
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
projection_scene_prop_name = "Projection scene"
breakdown_collection_prop_name = "Breakdown collection"
final_mesh_collection_prop_name = "Final mesh collection"
tweaking_collection_prop_name = "Tweaking collection"
sd_gen_img_path_prop_name = "Stable diffusion image generated path"


class SDTextureProj_OT_CreateNewProjScene(bpy.types.Operator):
    bl_idname = "sd_texture_proj.create_new_proj_scene"
    bl_label = "Create new projection scene"
    bl_description = "Create a projection scene to create data for Stable Diffusion and shading scene"

    # poll function
    @classmethod
    def poll(cls, context):
        return context.active_object and subject_prop_name not in context.scene

    def execute(self, context):
        # Duplicate the active object and link it to the subjects collection
        active_obj = context.active_object

        sd_proj_scene = bpy.data.scenes.new(name=f"{active_obj.name} SD projection scene")

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
    bl_idname = "sd_texture_proj.render_ref_img"
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

    # poll function

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


class SDTextureProj_OT_CreateNewShadingScene(bpy.types.Operator):
    bl_idname = "sd_texture_proj.create_new_shading_scene"
    bl_label = "Create new shading scene"
    bl_description = "Create a new shading scene to apply the SD generated texture"

    @classmethod
    def poll(cls, context):
        return proj_collection_prop_name in context.scene \
            and img_dir_prop_name in context.scene \
            and context.scene.img_generated_path != "//"

    def execute(self, context):

        proj_scene = context.scene
        subject_mesh = proj_scene[subject_prop_name]
        subject_name = subject_mesh.name
        proj_mesh_collection = proj_scene[proj_collection_prop_name]
        img_gen_path = context.scene.img_generated_path

        shading_scene_name = f"{subject_name} SD shading"

        # check if the proj mesh collection is ok

        for obj in proj_mesh_collection.objects:
            if not obj.type == "MESH":
                self.report({'ERROR'}, f"Object {obj.name} is not a mesh")

            if obj[uv_layer_proj_prop_name] not in obj.data.uv_layers.keys():
                self.report({'ERROR'}, f"Projection uvs not found in object {obj.name}")

            if obj[uv_layer_proj_mirrored_prop_name] not in obj.data.uv_layers.keys():
                self.report({'ERROR'}, f"Projection uvs not found in object {obj.name}")

        # create a new scene for the shading
        shading_scene = bpy.data.scenes.new(name=shading_scene_name)
        context.window.scene = shading_scene

        # create materials and node trees
        sd_gen_node_group = material_shading.create_sd_gen_node_group(img_gen_path)
        uv_tweak_material = material_shading.create_tweak_uvs_material(sd_gen_node_group)



        # copy the subject into the shading scene

        shading_mesh = subject_mesh.copy()
        shading_mesh.data = subject_mesh.data.copy()
        shading_mesh.name = f"{subject_mesh.name}_shading"
        shading_mesh.data.name = f"{subject_mesh.name}_shading"

        final_shading_mesh_collection = bpy.data.collections.new(name=f"{shading_scene_name} final assembly")
        shading_scene.collection.children.link(final_shading_mesh_collection)

        final_shading_mesh_collection.objects.link(shading_mesh)

        shading_scene[shading_mesh_prop_name] = shading_mesh
        shading_scene[projection_scene_prop_name] = proj_scene
        shading_scene[final_mesh_collection_prop_name] = final_shading_mesh_collection

        # todo : add material

        # create collection for tweaking

        tweak_mesh_collection = sd_texture_functions.clone_collection(context, proj_mesh_collection,
                                                                      f"{shading_scene_name} projection tweaks")
        shading_scene.view_layers[0].layer_collection.children[tweak_mesh_collection.name].hide_viewport = True

        aspect_x = proj_scene.render.resolution_x
        aspect_y = proj_scene.render.resolution_y
        camera = proj_scene.camera

        for obj in tweak_mesh_collection.objects:
            uv_layer = obj.data.uv_layers[0].name
            sd_texture_functions.add_uv_project_modifier(obj, uv_layer, aspect_x, aspect_y, camera)

            # assign the tweak material
            obj.data.materials.append(uv_tweak_material)

        # transfer proj UVs

        shading_scene.collection.children.link(proj_mesh_collection)

        for obj in tweak_mesh_collection.objects:
            uv_layer = obj[uv_layer_proj_prop_name]
            uv_layer_mirrored = obj[uv_layer_proj_mirrored_prop_name]

            sd_texture_functions.transfer_uvs(obj, shading_mesh, uv_layer)
            sd_texture_functions.transfer_uvs(obj, shading_mesh, uv_layer_mirrored)

        shading_scene.collection.children.unlink(proj_mesh_collection)

        # create a new collection "breakdown"

        breakdown_collection = bpy.data.collections.new(name=f"{shading_scene_name} breakdown")
        shading_scene.collection.children.link(breakdown_collection)
        shading_scene[breakdown_collection_prop_name] = breakdown_collection
        shading_scene.view_layers[0].layer_collection.children[breakdown_collection.name].hide_viewport = True

        offset = 0
        for obj in proj_mesh_collection.objects:
            # duplicate the shading_mesh and move it sideways
            new_shading_mesh = shading_mesh.copy()
            new_shading_mesh.name = f"{obj.name}_projection_shading"
            offset += shading_mesh.dimensions[0] + 0.5
            new_shading_mesh.location.x = offset
            breakdown_collection.objects.link(new_shading_mesh)

        # todo : add material

        return {'FINISHED'}

# todo : a operator to transfer the tweaked uvs
