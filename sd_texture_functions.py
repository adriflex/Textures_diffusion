import pathlib
from math import radians

import bpy
from bpy.types import Camera, LayerCollection, Mesh, Scene

from . import materials

subject_prop_name = "Subject mesh"
proj_collection_prop_name = "Proj collection"
img_dir_prop_name = "Image directory"


def get_blend_name_without_ext() -> str:
    blend_file_path = pathlib.Path(bpy.data.filepath)
    blend_name = blend_file_path.name
    blend_name_without_ext = blend_name.split(".")[0]
    return blend_name_without_ext


def create_img_dir(scene: Scene):
    blend_name = get_blend_name_without_ext()
    image_directory = f"//{blend_name}_proj_maps"
    scene[img_dir_prop_name] = image_directory


def select_object_solo(obj: Mesh):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)


def get_scene_depth(camera: Camera, collection: LayerCollection) -> dict:
    # return the depth of the scene view by the camera
    # get the camera position
    camera_pos = camera.location

    # get objects in the collection
    objects = collection.all_objects

    # initialize the maximum distance
    max_distance = 0.0

    # initialize the minimum distance
    min_distance = 100000.0

    for obj in objects:
        # get the object position
        obj_pos = obj.location

        # get object dimensions
        obj_dimensions = obj.dimensions
        obj_max_pos = obj_pos + obj_dimensions / 2.0
        obj_min_pos = obj_pos - obj_dimensions / 2.0

        # get the distance between the camera and the object
        distance_for_max = (camera_pos - obj_max_pos).length
        # get the maximum distance
        max_distance = max(distance_for_max, max_distance)

        distance_for_min = (camera_pos - obj_min_pos).length
        # get the minimum distance
        min_distance = min(distance_for_min, min_distance)

    print(f"min: {min_distance}, max: {max_distance}")

    return {"min": min_distance, "max": max_distance}


def render_beauty(render_path: str):
    beauty_scene = bpy.context.scene.copy()

    beauty_scene.name = "Render_beauty"
    beauty_scene.render.engine = 'BLENDER_EEVEE'
    beauty_scene.render.image_settings.file_format = 'PNG'
    beauty_scene.render.image_settings.color_mode = 'RGB'
    beauty_scene.render.image_settings.color_depth = '8'

    # set the output path
    beauty_scene.render.filepath = render_path

    # set default environment
    world = bpy.data.worlds.new("World_beauty")
    beauty_scene.world = world

    # render the scene
    bpy.ops.render.render(scene=beauty_scene.name, write_still=True)

    # delete the scene
    bpy.data.scenes.remove(beauty_scene)


def render_normal(render_path: str):
    normal_scene = bpy.context.scene.copy()

    normal_scene.name = "Render_normal"
    normal_scene.render.engine = 'CYCLES'
    normal_scene.render.image_settings.file_format = 'PNG'
    normal_scene.render.image_settings.color_mode = 'RGB'
    normal_scene.render.image_settings.color_depth = '8'
    normal_scene.display_settings.display_device = 'None'
    normal_scene.view_settings.view_transform = 'Standard'

    # set the output path
    normal_scene.render.filepath = render_path

    # set the background color to normal map default color
    world = bpy.data.worlds.new("World_normal")
    normal_scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 1.0, 1.0)

    normal_material = materials.create_normal_material()

    normal_scene.view_layers["ViewLayer"].material_override = normal_material

    bpy.ops.render.render(scene=normal_scene.name, write_still=True)

    # clean up
    bpy.data.scenes.remove(normal_scene)


def render_depth(render_path: str, mesh_collection: LayerCollection):
    depth_scene = bpy.context.scene.copy()

    depth_scene.name = "Render_depth"
    depth_scene.render.engine = 'CYCLES'
    depth_scene.render.image_settings.file_format = 'PNG'
    depth_scene.render.image_settings.color_mode = 'RGB'
    depth_scene.render.image_settings.color_depth = '16'
    depth_scene.display_settings.display_device = 'None'
    depth_scene.view_settings.view_transform = 'Standard'

    # set the output path
    depth_scene.render.filepath = render_path

    # set default environment
    world = bpy.data.worlds.new("World_normal")
    depth_scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

    camera = depth_scene.camera

    scene_depth = get_scene_depth(camera, mesh_collection)

    depth_material = materials.create_depth_material(scene_depth["min"], scene_depth["max"])

    depth_scene.view_layers["ViewLayer"].material_override = depth_material

    bpy.ops.render.render(scene=depth_scene.name, write_still=True)

    # clean up
    bpy.data.scenes.remove(depth_scene)


def render_facing(obj: Mesh, render_path: str):
    print(f"Baking {obj} facing mask at : {render_path}")

    backup_scene = bpy.context.scene

    facing_scene = bpy.data.scenes.new(name=f"{obj.name} bake facing")
    facing_scene.render.engine = 'CYCLES'

    bpy.context.window.scene = facing_scene

    facing_scene.collection.objects.link(obj)
    select_object_solo(obj)

    # set up the material for baking
    backup_mat = None
    if obj.active_material:
        backup_mat = obj.active_material

    facing_material = materials.create_facing_material()
    obj.active_material = facing_material

    # image to bake into
    image_name = f"{obj.name}_facing"
    bake_image = bpy.data.images.new(image_name, width=1024, height=1024)

    nodes = facing_material.node_tree.nodes

    texture_node = nodes.new(type='ShaderNodeTexImage')
    texture_node.image = bake_image
    texture_node.name = 'Texture_Bake_Node'
    texture_node.location = -300, 300

    nodes.active = texture_node

    bpy.ops.object.bake(type='EMIT')

    # restore
    if backup_mat:
        obj.active_material = backup_mat

    bpy.data.materials.remove(facing_material)

    # save the baked image
    bake_image.filepath_raw = render_path
    bake_image.file_format = 'OPEN_EXR'
    bake_image.save()

    bpy.context.window.scene = backup_scene

    # delete the scene
    bpy.data.scenes.remove(facing_scene)
    del facing_scene


def render_camera_occlusion(obj: Mesh, render_path: str):
    print(f"Baking {obj} shadowing mask at : {render_path}")

    backup_scene = bpy.context.scene

    cam_occlusion_scene = bpy.context.scene.copy()
    cam_occlusion_scene.name = "SD_texture_bake_shadowing"
    cam_occlusion_scene.render.engine = 'CYCLES'
    cam_occlusion_scene.cycles.max_bounces = 0

    bpy.context.window.scene = cam_occlusion_scene

    select_object_solo(obj)

    # create a directional light
    shadowing_light = bpy.data.lights.new(name="shadowing_light", type='SUN')
    shadowing_light.angle = radians(10)
    shadowing_light_obj = bpy.data.objects.new(name="shadowing_light", object_data=shadowing_light)

    cam_occlusion_scene.collection.objects.link(shadowing_light_obj)

    # set default environment
    world = bpy.data.worlds.new("World_black")
    cam_occlusion_scene.world = world
    world.use_nodes = True
    cam_occlusion_scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

    # set the camera matrix to the shadowing light matrix
    camera = cam_occlusion_scene.camera
    shadowing_light_obj.matrix_world = camera.matrix_world

    # set up the material for baking
    backup_mat = None
    if obj.active_material:
        backup_mat = obj.active_material

    diffuse_material = materials.create_diffuse_material()
    obj.active_material = diffuse_material

    image_name = f"{obj.name}_camera_occlusion"
    bake_image = bpy.data.images.new(image_name, width=1024, height=1024)

    nodes = diffuse_material.node_tree.nodes

    texture_node = nodes.new(type='ShaderNodeTexImage')
    texture_node.image = bake_image
    texture_node.name = 'Texture_Bake_Node'
    texture_node.location = -300, 300

    nodes.active = texture_node

    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT'})

    # save the baked image
    bake_image.filepath_raw = render_path
    bake_image.file_format = 'OPEN_EXR'
    bake_image.save()

    # clean up
    if backup_mat:
        obj.active_material = backup_mat

    bpy.data.materials.remove(diffuse_material)

    # restore
    bpy.context.window.scene = backup_scene

    # clean up
    bpy.data.scenes.remove(cam_occlusion_scene)
    del cam_occlusion_scene
    del shadowing_light


def mirror_obj(obj: Mesh, axis: str):
    match axis:
        case ('X'):
            obj.scale.x *= -1
        case ('Y'):
            obj.scale.y *= -1
        case ('Z'):
            obj.scale.z *= -1
        case _:
            raise ValueError("Axis must be one of 'X', 'Y', 'Z'")


def project_uvs_from_camera(obj, camera, uv_layer_name):
    assert obj.type == 'MESH', "Object to project from is not a mesh"
    assert camera.type == 'CAMERA', "Camera is not a camera"

    print("Projecting from camera: ", camera.name)
    print("Projecting mesh: ", obj.name)

    if uv_layer_name not in obj.data.uv_layers.keys():
        obj.data.uv_layers.new(name=uv_layer_name)
    obj.data.uv_layers[uv_layer_name].active = True

    # select the camera
    bpy.context.view_layer.objects.active = camera
    bpy.ops.view3d.object_as_camera()

    # select the mesh
    select_object_solo(obj)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    obj.data.uv_layers[uv_layer_name].active = True
    bpy.ops.uv.project_from_view(camera_bounds=True, correct_aspect=False, scale_to_bounds=False)

    bpy.ops.object.mode_set(mode='OBJECT')

    obj.data.uv_layers[0].active = True

    return uv_layer_name


def transfer_uvs(obj_from, obj_to, uv_layer_name):
    select_object_solo(obj_from)
    obj_to.select_set(True)
    obj_from.data.uv_layers[uv_layer_name].active = True

    if uv_layer_name not in obj_to.data.uv_layers:
        obj_to.data.uv_layers.new(name=uv_layer_name)
    obj_to.data.uv_layers[uv_layer_name].active = True
    bpy.ops.object.join_uvs()
