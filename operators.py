from math import radians

import bpy
from . import functions

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
gen_node_group_prop_name = "SD Gen node group"
projection_scene_prop_name = "Projection scene"
breakdown_collection_prop_name = "Breakdown collection"
final_mesh_collection_prop_name = "Final mesh collection"
tweaking_collection_prop_name = "Tweaking collection"
custom_mask_prop_name = "Custom mask"


class TexDiff_OT_CreateNewProjScene(bpy.types.Operator):
    bl_idname = "textures_diffusion.create_new_proj_scene"
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
        sd_proj_scene.render.resolution_x = 910
        sd_proj_scene.render.resolution_y = 512

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


class TexDiff_OT_RenderRefImg(bpy.types.Operator):
    bl_idname = "textures_diffusion.render_ref_img"
    bl_label = "Render ref images"
    bl_description = "Render image to use in Stable Diffusion"

    # poll function
    @classmethod
    def poll(cls, context):
        camera_in_scene = context.scene.camera is not None
        proj_collection_in_scene = proj_collection_prop_name in context.scene.keys()
        subject_prop_in_scene = subject_prop_name in context.scene.keys()
        return camera_in_scene and proj_collection_in_scene and subject_prop_in_scene

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the .blend file before baking")
            return {'CANCELLED'}

        proj_scene = context.scene
        functions.create_img_dir(proj_scene)

        subject_name = proj_scene[subject_prop_name].name
        image_directory = proj_scene[img_dir_prop_name]

        beauty_path = f"{image_directory}/{subject_name}_beauty.png"
        normal_path = f"{image_directory}/{subject_name}_normal.png"
        depth_path = f"{image_directory}/{subject_name}_depth.png"

        bpy.context.window.cursor_set("WAIT")

        functions.render_beauty(beauty_path)

        functions.render_normal(normal_path)

        functions.render_depth(depth_path, proj_scene[proj_collection_prop_name])

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        # tell the user the maps have been baked
        self.report({'INFO'}, "Baking done ! Check the folder 'SD_maps' in the same folder as the .blend file")

        return {'FINISHED'}


class TexDiff_OT_BakeProjMasks(bpy.types.Operator):
    bl_idname = "textures_diffusion.bake_proj_masks"
    bl_label = "Bake projection masks"
    bl_description = "Bake camera occlusion and facing masks"

    # poll function
    @classmethod
    def poll(cls, context):
        camera_in_scene = context.scene.camera is not None
        proj_collection_in_scene = proj_collection_prop_name in context.scene.keys()
        return camera_in_scene and proj_collection_in_scene

    def execute(self, context):
        if not bpy.data.is_saved:
            self.report({'ERROR'}, "Please save the .blend file before baking")
            return {'CANCELLED'}

        proj_scene = context.scene

        functions.create_img_dir(proj_scene)

        collection = proj_scene[proj_collection_prop_name]
        image_directory = proj_scene[img_dir_prop_name]

        bpy.context.window.cursor_set("WAIT")

        masks_resolution = proj_scene.textures_diffusion_props.masks_resolution
        mask_samples = proj_scene.textures_diffusion_props.masks_samples

        for obj in collection.objects:
            assert obj.type == "MESH", f"Object {obj.name} is not a mesh"

            facing_path = f"{image_directory}/Masks/{obj.name}_facing_mask.exr"
            facing_mirrored_path = f"{image_directory}/Masks/{obj.name}_facing_mask_mirrored.exr"
            camera_occlusion_path = f"{image_directory}/Masks/{obj.name}_camera_occlusion_mask.exr"
            camera_occlusion_mirrored_path = f"{image_directory}/Masks/{obj.name}_camera_occlusion_mask_mirrored.exr"

            # bake masks
            functions.render_facing(obj, facing_path, masks_resolution, mask_samples)
            functions.render_camera_occlusion(obj, camera_occlusion_path, masks_resolution, mask_samples)

            # add file output to the object custom properties
            obj[facing_path_prop_name] = facing_path
            obj[camera_occlusion_prop_name] = camera_occlusion_path

            # mirror
            if proj_scene.textures_diffusion_props.use_mirror_X:
                functions.mirror_obj(obj, "X")

                functions.render_facing(obj, facing_mirrored_path, masks_resolution, mask_samples)
                functions.render_camera_occlusion(obj, camera_occlusion_mirrored_path, masks_resolution,
                                                  mask_samples)

                functions.mirror_obj(obj, "X")

                # add file output to the object custom properties
                obj[facing_path_mirrored_prop_name] = facing_mirrored_path
                obj[camera_occlusion_mirrored_prop_name] = camera_occlusion_mirrored_path

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        for image in bpy.data.images:
            image.reload()

        # tell the user the maps have been baked
        self.report({'INFO'}, "Baking done !")

        return {'FINISHED'}


class TexDiff_OT_CreateProjUVs(bpy.types.Operator):
    bl_idname = "textures_diffusion.create_proj_uvs"
    bl_label = "Create Projected UVs"
    bl_description = "Project the UVs of the collection from the camera"

    # poll function
    @classmethod
    def poll(cls, context):
        camera_in_scene = context.scene.camera is not None
        proj_collection_in_scene = proj_collection_prop_name in context.scene.keys()
        return camera_in_scene and proj_collection_in_scene

    def execute(self, context):
        proj_scene = context.scene

        collection = proj_scene[proj_collection_prop_name]
        camera = proj_scene.camera

        for obj in collection.objects:
            assert obj.type == "MESH", f"Object {obj.name} is not a mesh"

            uv_layer_name = f"{obj.name}_cam_proj"
            uv_layer_mirrored_name = f"{obj.name}_cam_proj_mirrored"

            # project the UVs
            functions.project_uvs_from_camera(obj, camera, uv_layer_name)

            # add file output to the object custom properties
            obj[uv_layer_proj_prop_name] = uv_layer_name

            # mirror
            if proj_scene.textures_diffusion_props.use_mirror_X:
                functions.mirror_obj(obj, "X")
                functions.project_uvs_from_camera(obj, camera, uv_layer_mirrored_name)
                functions.mirror_obj(obj, "X")

                # add file output to the object custom properties
                obj[uv_layer_proj_mirrored_prop_name] = uv_layer_mirrored_name

        # change the mouse cursor back to the default
        bpy.context.window.cursor_set("DEFAULT")

        # tell the user the maps have been baked
        self.report({'INFO'}, "UVs projected !")

        return {'FINISHED'}


class TexDiff_OT_CreateNewShadingScene(bpy.types.Operator):
    bl_idname = "textures_diffusion.create_new_shading_scene"
    bl_label = "Create new shading scene"
    bl_description = "Create a new shading scene to apply the SD generated texture"

    @classmethod
    def poll(cls, context):
        return proj_collection_prop_name in context.scene \
            and img_dir_prop_name in context.scene \
            and context.scene.textures_diffusion_props.img_generated_path != "//"

    def execute(self, context):

        proj_scene = context.scene
        subject_mesh = proj_scene[subject_prop_name]
        subject_name = subject_mesh.name
        proj_mesh_collection = proj_scene[proj_collection_prop_name]
        img_gen_path = context.scene.textures_diffusion_props.img_generated_path

        shading_scene_name = f"{subject_name} SD shading"

        # check if the proj mesh collection is ok

        for obj in proj_mesh_collection.objects:
            if not obj.type == "MESH":
                self.report({'ERROR'}, f"Object {obj.name} is not a mesh")

            if obj[uv_layer_proj_prop_name] not in obj.data.uv_layers.keys():
                self.report({'ERROR'}, f"Projection uvs not found in object {obj.name}")

        # create a new scene for the shading
        shading_scene = bpy.data.scenes.new(name=shading_scene_name)
        context.window.scene = shading_scene
        shading_scene.render.resolution_x = proj_scene.render.resolution_x
        shading_scene.render.resolution_y = proj_scene.render.resolution_y

        # set the color management to standard
        shading_scene.view_settings.view_transform = "Standard"

        # create Stable Diffusion gen group node
        sd_gen_node_group = functions.create_sd_gen_node_group(img_gen_path)
        shading_scene[gen_node_group_prop_name] = sd_gen_node_group

        # copy the subject into the shading scene

        shading_mesh = subject_mesh.copy()
        shading_mesh.data = subject_mesh.data.copy()
        shading_mesh.name = f"{subject_name}_shading"
        shading_mesh.data.name = f"{subject_name}_shading"

        final_shading_mesh_collection = bpy.data.collections.new(name=f"{shading_scene_name} final assembly")
        shading_scene.collection.children.link(final_shading_mesh_collection)

        final_shading_mesh_collection.objects.link(shading_mesh)

        shading_scene[shading_mesh_prop_name] = shading_mesh
        shading_scene[projection_scene_prop_name] = proj_scene
        shading_scene[final_mesh_collection_prop_name] = final_shading_mesh_collection
        shading_scene[img_dir_prop_name] = proj_scene[img_dir_prop_name]
        shading_scene.textures_diffusion_props.img_generated_path = img_gen_path
        shading_scene.textures_diffusion_props.use_mirror_X = proj_scene.textures_diffusion_props.use_mirror_X

        # create collection for tweaking

        tweak_mesh_collection = functions.clone_collection(context, proj_mesh_collection,
                                                           name=f"{shading_scene_name} projection tweaks",
                                                           suffix="_tweaks")
        shading_scene.view_layers[0].layer_collection.children[tweak_mesh_collection.name].hide_viewport = True
        shading_scene[tweaking_collection_prop_name] = tweak_mesh_collection

        aspect_x = proj_scene.render.resolution_x
        aspect_y = proj_scene.render.resolution_y
        camera = proj_scene.camera

        for obj in tweak_mesh_collection.objects:
            uv_layer = obj.data.uv_layers[0].name
            functions.add_uv_project_modifier(obj, uv_layer, aspect_x, aspect_y, camera)

        # transfer proj UVs
        shading_scene.collection.children.link(proj_mesh_collection)

        for obj in tweak_mesh_collection.objects:
            uv_layer = obj[uv_layer_proj_prop_name]
            functions.transfer_uvs(obj, shading_mesh, uv_layer)

            if shading_scene.textures_diffusion_props.use_mirror_X:
                uv_layer_mirrored = obj[uv_layer_proj_mirrored_prop_name]
                functions.transfer_uvs(obj, shading_mesh, uv_layer_mirrored)

        shading_scene.collection.children.unlink(proj_mesh_collection)

        # create the tweak uvs material
        tweak_uvs_mat = functions.create_tweak_uvs_material(sd_gen_node_group)

        for obj in tweak_mesh_collection.objects:
            obj.data.materials.clear()
            obj.data.materials.append(tweak_uvs_mat)

        # create a new collection "breakdown"

        breakdown_collection = bpy.data.collections.new(name=f"{shading_scene_name} breakdown")
        shading_scene.collection.children.link(breakdown_collection)
        shading_scene[breakdown_collection_prop_name] = breakdown_collection
        shading_scene.view_layers[0].layer_collection.children[breakdown_collection.name].hide_viewport = True

        offset = 0
        proj_node_groups = []
        for obj in proj_mesh_collection.objects:
            # duplicate the shading_mesh and move it sideways
            new_shading_mesh = shading_mesh.copy()
            new_shading_mesh.data = shading_mesh.data.copy()
            new_shading_mesh.name = f"{obj.name}_projection_shading"
            offset += shading_mesh.dimensions[0] + 0.5
            new_shading_mesh.location.x = offset
            breakdown_collection.objects.link(new_shading_mesh)

            # create custom map image
            custom_mask_image = bpy.data.images.new(name=f"{obj.name}_custom_mask", width=1024, height=1024, alpha=True)
            custom_mask_image.generated_color = (0, 0, 0, 0)
            custom_mask_image.filepath_raw = f"{proj_scene[img_dir_prop_name]}/Masks/{custom_mask_image.name}.exr"
            custom_mask_image.file_format = 'OPEN_EXR'

            custom_mask_image.save()

            # create Subject proj material
            proj_data = {
                "proj_mesh_name": obj.name,
                "use_mirror_X": proj_scene.textures_diffusion_props.use_mirror_X,
                "proj_uv_layer": obj[uv_layer_proj_prop_name],
                "sd_gen_node_group": sd_gen_node_group,
                "custom_mask_image": custom_mask_image,
                "cam_occlusion": obj[camera_occlusion_prop_name],
                "facing_mask": obj[facing_path_prop_name],
            }

            if shading_scene.textures_diffusion_props.use_mirror_X:
                proj_data["proj_uv_layer_mirrored"] = obj[uv_layer_proj_mirrored_prop_name]
                proj_data["cam_occlusion_mirrored"] = obj[camera_occlusion_mirrored_prop_name]
                proj_data["facing_mask_mirrored"] = obj[facing_path_mirrored_prop_name]

            # create material
            proj_node_group = functions.create_proj_node_group(proj_data)
            proj_node_groups.append(proj_node_group)

            proj_material = functions.create_proj_material(obj.name, proj_node_group, custom_mask_image)
            # proj_materials.append(proj_material)

            # append material at object level
            shading_mesh.data.materials.clear()
            new_shading_mesh.data.materials.append(None)
            new_shading_mesh.material_slots[0].link = "OBJECT"
            new_shading_mesh.material_slots[0].material = proj_material

            # add custom prop custom mask image
            new_shading_mesh[custom_mask_prop_name] = custom_mask_image

        # create Subject final material
        final_assembly_material = functions.create_final_assembly_material(proj_node_groups,
                                                                           sd_gen_node_group)
        shading_mesh.data.materials.clear()
        shading_mesh.data.materials.append(final_assembly_material)

        for obj in breakdown_collection.objects:
            obj.data = shading_mesh.data

        return {'FINISHED'}


class TexDiff_OT_ReloadSdImgPath(bpy.types.Operator):
    bl_idname = "textures_diffusion.reload_sd_img_path"
    bl_label = "Reload SD image path"
    bl_description = "Reload the Sable Diffusion image Path into the Stable_diffusion_gen node group"

    @classmethod
    def poll(cls, context):
        gen_node_group_exist = gen_node_group_prop_name in context.scene
        img_generated_path_exist = "img_generated_path" in context.scene.textures_diffusion_props
        return gen_node_group_exist and img_generated_path_exist

    def execute(self, context):
        new_img_generated_path = context.scene.textures_diffusion_props.img_generated_path
        gen_node_group = context.scene[gen_node_group_prop_name]

        functions.get_node('Stable_diffusion_gen', gen_node_group).image.filepath = new_img_generated_path

        return {'FINISHED'}


class TexDiff_OT_TransferTweakedUvs(bpy.types.Operator):
    bl_idname = "textures_diffusion.transfer_tweaked_uvs"
    bl_label = "Transfer projection tweaks"
    bl_description = "Transfer projection tweaks to the shading mesh and the breakdown collection meshes"

    @classmethod
    def poll(cls, context):
        tweaking_collection_exists = tweaking_collection_prop_name in context.scene
        shading_mesh_exists = shading_mesh_prop_name in context.scene
        proj_scene_exists = projection_scene_prop_name in context.scene

        return tweaking_collection_exists and shading_mesh_exists and proj_scene_exists

    def execute(self, context):
        # if edit mode exit
        if context.mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        active_scene = context.scene

        tweaking_collection = active_scene[tweaking_collection_prop_name]
        final_mesh_collection = active_scene[final_mesh_collection_prop_name]
        shading_mesh = active_scene[shading_mesh_prop_name]

        proj_scene_camera = active_scene[projection_scene_prop_name].camera
        active_scene.collection.objects.link(proj_scene_camera)

        for obj in tweaking_collection.objects:
            active_scene.view_layers[0].layer_collection.children[final_mesh_collection.name].hide_viewport = False

            uv_layer = obj[uv_layer_proj_prop_name]

            functions.project_uvs_from_camera(obj, proj_scene_camera, uv_layer)
            functions.transfer_uvs(obj, shading_mesh, uv_layer)

            if active_scene.textures_diffusion_props.use_mirror_X:
                uv_layer_mirrored = obj[uv_layer_proj_mirrored_prop_name]

                functions.mirror_obj(obj, "X")
                functions.project_uvs_from_camera(obj, proj_scene_camera, uv_layer_mirrored)
                functions.mirror_obj(obj, "X")

                functions.transfer_uvs(obj, shading_mesh, uv_layer_mirrored)

        # unlink the camera
        active_scene.collection.objects.unlink(proj_scene_camera)
        active_scene.view_layers[0].layer_collection.children[tweaking_collection.name].hide_viewport = True

        return {'FINISHED'}


class TexDiff_OT_PaintCustomMask(bpy.types.Operator):
    bl_idname = "textures_diffusion.paint_custom_mask"
    bl_label = "Paint custom mask"
    bl_description = "Enter painting mode and paint the custom mask of the selected object"

    @classmethod
    def poll(cls, context):
        custom_mask_image_exists = custom_mask_prop_name in context.active_object
        return custom_mask_image_exists

    def execute(self, context):
        custom_mask_image = context.active_object[custom_mask_prop_name]
        bpy.ops.view3d.view_selected(use_all_regions=False)

        bpy.ops.paint.texture_paint_toggle()
        bpy.context.scene.tool_settings.image_paint.mode = 'IMAGE'
        bpy.context.scene.tool_settings.image_paint.canvas = custom_mask_image
        # set uv_layer 0 active
        context.active_object.data.uv_layers.active_index = 0

        # todo : mettre le viewport en mode texture

        return {'FINISHED'}


class TexDiff_OT_TweakProjection(bpy.types.Operator):
    bl_idname = "textures_diffusion.tweak_projection"
    bl_label = "Tweak projection"
    bl_description = "Enter edit mode and tweak the projection of the selected object"

    @classmethod
    def poll(cls, context):
        UVProject_modifier_exists = "UVProject" in context.active_object.modifiers
        return UVProject_modifier_exists

    def execute(self, context):
        if "Subdivision" in context.active_object.modifiers:
            context.active_object.modifiers["Subdivision"].show_on_cage = True

        bpy.ops.view3d.view_selected(use_all_regions=False)
        bpy.ops.object.editmode_toggle()

        return {'FINISHED'}


class TexDiff_OT_BakeProjection(bpy.types.Operator):
    bl_idname = "textures_diffusion.bake_projection"
    bl_label = "Bake final texture"
    bl_description = "Bake the projected texture of the final mesh"

    @classmethod
    def poll(cls, context):
        shading_mesh_exists = shading_mesh_prop_name in context.scene
        img_dir_prop_name_exists = img_dir_prop_name in context.scene
        if shading_mesh_exists:
            shading_mesh_active = context.scene[shading_mesh_prop_name] == context.active_object
        return shading_mesh_exists and img_dir_prop_name_exists and shading_mesh_active

    def execute(self, context):
        # create a new collection
        new_name = context.scene[shading_mesh_prop_name].name + "_bake"
        bake_collection = bpy.data.collections.new(new_name)
        context.scene.collection.children.link(bake_collection)

        # copy the shading mesh into the new collection
        shading_mesh_copy = context.scene[shading_mesh_prop_name].copy()
        shading_mesh_copy.name = new_name
        shading_mesh_copy.data = context.scene[shading_mesh_prop_name].data.copy()
        shading_mesh_copy.data.name = new_name
        bake_collection.objects.link(shading_mesh_copy)

        # set the first uv_layer as active
        shading_mesh_copy.data.uv_layers.active_index = 0

        # Bake the emission
        bake_render_path = f"{context.scene[img_dir_prop_name]}/{new_name}.exr"
        bake_resolution = context.scene.textures_diffusion_props.bake_resolution
        functions.bake_emission(context,shading_mesh_copy, bake_render_path, bake_resolution)

        # create a new material and assign to shading_mesh_copy
        baked_image_material = functions.create_baked_image_material(new_name, bake_render_path)

        # clean the projection uvs
        functions.clean_cam_proj_uvs(shading_mesh_copy)

        # clear material and assign the new one
        shading_mesh_copy.data.materials.clear()
        shading_mesh_copy.data.materials.append(baked_image_material)

        # hide the final assembly collection and make the baked mesh active
        layer_collection = context.scene.view_layers[0].layer_collection
        layer_collection.children[context.scene[final_mesh_collection_prop_name].name].hide_viewport = True
        context.view_layer.objects.active = shading_mesh_copy

        return {'FINISHED'}
