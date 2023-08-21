import os
import pathlib
from math import radians

import bpy
import mathutils
from bpy.types import Camera, LayerCollection, Mesh, Scene, Material, NodeGroup, Node, NodeTree, Image

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
    image_directory = f"//{blend_name}_SD_maps"
    scene[img_dir_prop_name] = image_directory


def select_object_solo(obj: Mesh):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)


def import_shading_material(mat_name) -> Material:
    filepath = os.path.join(os.path.dirname(__file__), "materials.blend")
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.materials = [mat_name]

    if data_to.materials[0] is None:
        raise ValueError("Material not found: ", mat_name)

    print("Imported material: ", data_to.materials[0])
    return data_to.materials[0]


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

    normal_material = import_shading_material("Normal")

    normal_scene.view_layers["ViewLayer"].material_override = normal_material

    bpy.ops.render.render(scene=normal_scene.name, write_still=True)

    # clean up
    bpy.data.scenes.remove(normal_scene)
    bpy.data.materials.remove(normal_material)


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

    depth_material = import_shading_material("Depth")
    depth_material.node_tree.nodes['depth_input'].inputs[1].default_value = scene_depth["min"]
    depth_material.node_tree.nodes['depth_input'].inputs[2].default_value = scene_depth["max"]

    depth_scene.view_layers["ViewLayer"].material_override = depth_material

    bpy.ops.render.render(scene=depth_scene.name, write_still=True)

    # clean up
    bpy.data.scenes.remove(depth_scene)
    bpy.data.materials.remove(depth_material)


def render_facing(obj: Mesh, render_path: str, resolution, samples):
    print(f"Baking {obj} facing mask at : {render_path}")

    backup_scene = bpy.context.scene

    facing_scene = bpy.context.scene.copy()
    facing_scene.name = "Bake_facing"
    facing_scene.render.engine = 'CYCLES'
    facing_scene.cycles.samples = samples

    bpy.context.window.scene = facing_scene

    facing_scene.collection.objects.link(obj)
    select_object_solo(obj)

    # set up the material for baking
    backup_mat = None
    if obj.active_material:
        backup_mat = obj.active_material

    # facing_material = materials_baking.create_facing_material()
    facing_material = import_shading_material("Facing")
    obj.active_material = facing_material

    # image to bake into
    image_name = f"{obj.name}_facing"
    bake_image = bpy.data.images.new(image_name, width=resolution, height=resolution)

    nodes = facing_material.node_tree.nodes

    # set camera vector into the shader
    camera = facing_scene.camera
    camera_rotation = camera.rotation_euler

    vector = mathutils.Vector((0.0, 0.0, 1.0))
    vector.rotate(camera_rotation)
    print("Camera vector: ", vector)

    nodes['Camera_vector'].inputs[0].default_value = vector.x
    nodes['Camera_vector'].inputs[1].default_value = vector.y
    nodes['Camera_vector'].inputs[2].default_value = vector.z

    # set the image to bake into
    texture_node = nodes['Texture_Bake_Node']
    texture_node.image = bake_image

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


def render_camera_occlusion(obj: Mesh, render_path: str, resolution, samples):
    print(f"Baking {obj} shadowing mask at : {render_path}")

    backup_scene = bpy.context.scene

    cam_occlusion_scene = bpy.context.scene.copy()
    cam_occlusion_scene.name = "Bake_shadowing"
    cam_occlusion_scene.render.engine = 'CYCLES'
    cam_occlusion_scene.cycles.max_bounces = 0
    cam_occlusion_scene.cycles.samples = samples

    bpy.context.window.scene = cam_occlusion_scene

    select_object_solo(obj)

    # create a directional light
    shadowing_light = bpy.data.lights.new(name="shadowing_light", type='SUN')
    shadowing_light.angle = radians(10)
    shadowing_light_obj = bpy.data.objects.new(name="shadowing_light", object_data=shadowing_light)

    camera = cam_occlusion_scene.camera
    camera_rotation = camera.rotation_euler

    shadowing_light_obj.rotation_euler = camera_rotation

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

    diffuse_material = import_shading_material("Diffuse")
    obj.active_material = diffuse_material

    image_name = f"{obj.name}_camera_occlusion"
    bake_image = bpy.data.images.new(image_name, width=resolution, height=resolution)

    nodes = diffuse_material.node_tree.nodes

    texture_node = nodes['Texture_Bake_Node']
    texture_node.image = bake_image

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


def clone_collection(context, collection: LayerCollection, name: str, suffix: str) -> LayerCollection:
    new_collection = bpy.data.collections.new(name)
    context.scene.collection.children.link(new_collection)

    for obj in collection.objects:
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.name = obj.name + suffix
        new_obj.data.name = obj.data.name + suffix
        new_collection.objects.link(new_obj)

    return new_collection


def add_uv_project_modifier(obj, uv_layer, aspect_x, aspect_y, camera):
    uv_project_modifier = obj.modifiers.new(name="UVProject", type='UV_PROJECT')
    uv_project_modifier.uv_layer = uv_layer
    uv_project_modifier.aspect_x = aspect_x
    uv_project_modifier.aspect_y = aspect_y
    uv_project_modifier.projectors[0].object = camera


# shading scene functions


def import_shading_node_group(node_group_name) -> NodeGroup:
    filepath = os.path.join(os.path.dirname(__file__), "materials.blend")
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.node_groups = [node_group_name]

    if data_to.node_groups[0] is None:
        raise ValueError("Material not found: ", node_group_name)

    print("Imported node group: ", data_to.node_groups[0])
    return data_to.node_groups[0]


def get_node(base_name: str, node_tree: NodeTree) -> Node:
    for node in node_tree.nodes:
        if base_name in node.name:
            return node
    raise ValueError("Node not found: ", base_name)


def create_sd_gen_node_group(img_path) -> NodeGroup:
    base_node_group = import_shading_node_group("Stable_diffusion_gen")
    sd_img = bpy.data.images.load(img_path)
    base_node_group.nodes['Stable_diffusion_gen_image'].image = sd_img

    print("Created SD gen node group: ", base_node_group.name)

    return base_node_group


def create_tweak_uvs_material(sg_gen_node_group) -> Material:
    tweak_uvs_material = import_shading_material("Projections_tweaks_uvs")
    tweak_uvs_material.node_tree.nodes['Stable_diffusion_gen'].node_tree = sg_gen_node_group

    print("Created tweak UVs material: ", tweak_uvs_material.name)

    return tweak_uvs_material


def create_proj_node_group(proj_data: dict) -> NodeGroup:
    node_tree = import_shading_node_group("Proj")
    node_tree.name = proj_data['proj_mesh_name'] + "_proj"

    get_node('UV Proj', node_tree)

    get_node('UV Proj base', node_tree).uv_map = proj_data['proj_uv_layer']
    get_node('Stable_diffusion_gen base', node_tree).node_tree = proj_data['sd_gen_node_group']

    if proj_data['use_mirror_X']:
        get_node('Mirror on/off', node_tree).outputs[0].default_value = 1

        get_node('UV Proj mirrored', node_tree).mute = False
        get_node('UV Proj mirrored', node_tree).uv_map = proj_data['proj_uv_layer_mirrored']

        get_node('Stable_diffusion_gen mirrored', node_tree).mute = False
        get_node('Stable_diffusion_gen mirrored', node_tree).node_tree = proj_data['sd_gen_node_group']

    settings_masks_node_tree = get_node('Settings masks proj', node_tree).node_tree

    # create new images
    cam_occlusion_image = bpy.data.images.load(proj_data['cam_occlusion'])
    facing_mask_image = bpy.data.images.load(proj_data['facing_mask'])

    # set images
    get_node('Custom mask', settings_masks_node_tree).image = proj_data['custom_mask_image']
    get_node('Mask cam occlu base', settings_masks_node_tree).image = cam_occlusion_image
    get_node('Facing mask base', settings_masks_node_tree).image = facing_mask_image

    if proj_data['use_mirror_X']:
        cam_occlusion_mirrored_image = bpy.data.images.load(proj_data['cam_occlusion_mirrored'])
        facing_mask_mirrored_image = bpy.data.images.load(proj_data['facing_mask_mirrored'])

        get_node('Mask cam occlu mirrored', settings_masks_node_tree).mute = False
        get_node('Mask cam occlu mirrored', settings_masks_node_tree).image = cam_occlusion_mirrored_image
        get_node('Facing mask mirrored', settings_masks_node_tree).mute = False
        get_node('Facing mask mirrored', settings_masks_node_tree).image = facing_mask_mirrored_image

    print("Created projection node group: ", node_tree.name)

    return node_tree


def create_proj_material(proj_mesh_name, proj_node_group: Node, custom_mask_image: Image) -> Material:
    proj_material = import_shading_material("Projections_cleaning")
    proj_material.name = proj_mesh_name + "_Projections_cleaning"
    node_tree = proj_material.node_tree
    get_node('Proj', node_tree).node_tree = proj_node_group
    get_node('Custom mask', node_tree).image = custom_mask_image

    print("Created projection material: ", proj_material.name)

    return proj_material


def create_final_assembly_material(proj_node_groups: list, sd_gen_node_group: NodeGroup):
    final_assembly_material = import_shading_material("Projections_assembly")
    node_tree = final_assembly_material.node_tree

    last_mix_rgb = None
    last_math = None
    for i, proj_node_group in enumerate(reversed(proj_node_groups)):
        # assembly proj tree
        projection_node_group = node_tree.nodes.new('ShaderNodeGroup')
        projection_node_group.node_tree = proj_node_group
        projection_node_group.location = (-360, 400 - 200 * i)
        projection_node_group.name = "Projection " + str(i)
        projection_node_group.label = "Projection " + str(i)

        mix_shader = node_tree.nodes.new('ShaderNodeMixRGB')
        mix_shader.name = "Mix " + str(i)
        mix_shader.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
        mix_shader.location = (-160, 400 - 200 * i)

        # links
        node_tree.links.new(projection_node_group.outputs['Mask'], mix_shader.inputs[0])

        if last_mix_rgb is not None:
            node_tree.links.new(last_mix_rgb.outputs['Color'], mix_shader.inputs[1])

        last_mix_rgb = mix_shader

        node_tree.links.new(projection_node_group.outputs['Color'], mix_shader.inputs[2])

        # assembly mask tree
        mask_node_group = node_tree.nodes.new('ShaderNodeGroup')
        mask_node_group.node_tree = proj_node_group
        mask_node_group.location = (-360 + 1400, 400 - 200 * i)
        projection_node_group.name = "Projection mask " + str(i)
        projection_node_group.label = "Projection mask " + str(i)

        math_node = node_tree.nodes.new('ShaderNodeMath')
        math_node.operation = 'ADD'
        math_node.use_clamp = True
        math_node.inputs[0].default_value = 0.0
        math_node.inputs[1].default_value = 0.0
        math_node.location = (-160 + 1400, 400 - 200 * i)

        # links
        node_tree.links.new(mask_node_group.outputs['Mask'], math_node.inputs[1])

        if last_math is not None:
            node_tree.links.new(last_math.outputs['Value'], math_node.inputs[0])

        last_math = math_node

    input_reroute = get_node('input_mix_projections_node_group', node_tree)
    node_tree.links.new(last_mix_rgb.outputs['Color'], input_reroute.inputs[0])

    output_alpha = get_node('Material Output Alpha', node_tree)
    node_tree.links.new(last_math.outputs['Value'], output_alpha.inputs[0])

    # setup SD gen
    sd_gen_node = get_node('Stable_diffusion_gen', node_tree)
    sd_gen_node.node_tree = sd_gen_node_group

    print("Created final assembly material: ", final_assembly_material.name)

    return final_assembly_material


# function for final bake
def bake_emission(context, image_name, obj: Mesh, render_path: str, resolution: int) -> Image:
    backup_scene = bpy.context.scene

    # create new scene
    scene = bpy.data.scenes.new("Bake")
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 1
    bpy.context.window.scene = scene

    # link obj to new scene
    scene.collection.objects.link(obj)

    # set object as active
    context.view_layer.objects.active = obj

    # bake the emission
    bake_image = bpy.data.images.new(image_name, width=resolution, height=resolution, alpha=True)
    bake_image.filepath_raw = render_path
    bake_image.file_format = 'OPEN_EXR'

    material = obj.active_material
    node_tree = material.node_tree
    image_texture_node = node_tree.nodes.new('ShaderNodeTexImage')
    image_texture_node.image = bake_image

    node_tree.nodes.active = image_texture_node

    color_output = node_tree.nodes.get("Material Output Color")

    bpy.ops.object.bake(type='EMIT')

    bake_image.pack()

    print(f"Baked emission for {obj.name} in {render_path}")

    # delete the image texture node
    node_tree.nodes.remove(image_texture_node)

    # delete the scene
    bpy.data.scenes.remove(scene)

    # restore the scene
    bpy.context.window.scene = backup_scene

    return bake_image


def set_output_node_active(obj: Mesh, node_name: str):
    material = obj.active_material
    node_tree = material.node_tree
    output_node = node_tree.nodes.get(node_name)
    output_node.is_active_output = True


def set_alpha_channel(color_img, alpha_img):
    color_image_pixels = list(color_img.pixels)
    alpha_image_pixels = list(alpha_img.pixels)

    new_image_pixels = []
    for i in range(0, len(color_image_pixels), 4):
        color_image_pixels[i + 3] = alpha_image_pixels[i]

    color_img.pixels[:] = color_image_pixels


def create_baked_image_material(name, path):
    material = import_shading_material("Projections_baked")
    material.name = name
    node_tree = material.node_tree
    image_node = get_node('Baked image', node_tree)
    image_node.image = bpy.data.images.load(path)
    # channel packed
    image_node.image.alpha_mode = 'CHANNEL_PACKED'

    print("Created baked image material: ", material.name)

    return material


def clean_cam_proj_uvs(obj):
    # if obj uvs layer have _cam_proj in name, delete it
    layer_to_remove = []
    for uv_layer in list(obj.data.uv_layers):
        if "_cam_proj" in uv_layer.name:
            layer_to_remove.append(uv_layer.name)

    for uv_layer in layer_to_remove:
        obj.data.uv_layers.remove(obj.data.uv_layers[uv_layer])
