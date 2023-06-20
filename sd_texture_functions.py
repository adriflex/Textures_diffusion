import pathlib
from math import radians

import bpy
from bpy.types import Material, Camera, LayerCollection, Mesh


def normal_mat_nodes(material: bpy.types.Material):
    normal_mat = material.node_tree
    # start with a clean node tree
    for node in normal_mat.nodes:
        normal_mat.nodes.remove(node)
    # initialize camera_normal nodes
    # node Combine XYZ
    combine_xyz = normal_mat.nodes.new("ShaderNodeCombineXYZ")
    # X
    combine_xyz.inputs[0].default_value = 0.5
    # Y
    combine_xyz.inputs[1].default_value = 0.5
    # Z
    combine_xyz.inputs[2].default_value = -0.5

    # node Combine XYZ.001
    combine_xyz_001 = normal_mat.nodes.new("ShaderNodeCombineXYZ")
    # X
    combine_xyz_001.inputs[0].default_value = 0.5
    # Y
    combine_xyz_001.inputs[1].default_value = 0.5
    # Z
    combine_xyz_001.inputs[2].default_value = 0.5

    # node Mix
    mix = normal_mat.nodes.new("ShaderNodeMixRGB")
    # Fac
    mix.inputs[0].default_value = 1.0
    mix.blend_type = 'MULTIPLY'

    # node Vector Transform
    vector_transform = normal_mat.nodes.new("ShaderNodeVectorTransform")
    vector_transform.vector_type = 'NORMAL'
    vector_transform.convert_from = 'WORLD'
    vector_transform.convert_to = 'CAMERA'

    # node Mix.001
    mix_001 = normal_mat.nodes.new("ShaderNodeMixRGB")
    # Fac
    mix_001.inputs[0].default_value = 1.0
    mix_001.blend_type = 'ADD'

    # node Material Output
    material_output = normal_mat.nodes.new("ShaderNodeOutputMaterial")
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Geometry
    geometry = normal_mat.nodes.new("ShaderNodeNewGeometry")
    geometry.outputs[0].hide = True
    geometry.outputs[2].hide = True
    geometry.outputs[3].hide = True
    geometry.outputs[4].hide = True
    geometry.outputs[5].hide = True
    geometry.outputs[6].hide = True
    geometry.outputs[7].hide = True
    geometry.outputs[8].hide = True

    # Set locations
    combine_xyz.location = (-691.3909912109375, 1.5789947509765625)
    combine_xyz_001.location = (-504.3045959472656, -48.92665100097656)
    mix.location = (-504.3045959472656, 132.21095275878906)
    vector_transform.location = (-691.3909912109375, 167.3542022705078)
    mix_001.location = (-288.9167175292969, 102.45826721191406)
    material_output.location = (-44.356895446777344, 113.10558319091797)
    geometry.location = (-910.069091796875, 62.20948791503906)

    # Set dimensions
    combine_xyz.width, combine_xyz.height = 140.0, 100.0
    combine_xyz_001.width, combine_xyz_001.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    vector_transform.width, vector_transform.height = 140.0, 100.0
    mix_001.width, mix_001.height = 140.0, 100.0
    material_output.width, material_output.height = 140.0, 100.0
    geometry.width, geometry.height = 140.0, 100.0

    # initialize camera_normal links
    # geometry.Normal -> vector_transform.Vector
    normal_mat.links.new(geometry.outputs[1], vector_transform.inputs[0])
    # combine_xyz.Vector -> mix.Color2
    normal_mat.links.new(combine_xyz.outputs[0], mix.inputs[2])
    # combine_xyz_001.Vector -> mix_001.Color2
    normal_mat.links.new(combine_xyz_001.outputs[0], mix_001.inputs[2])
    # vector_transform.Vector -> mix.Color1
    normal_mat.links.new(vector_transform.outputs[0], mix.inputs[1])
    # mix.Color -> mix_001.Color1
    normal_mat.links.new(mix.outputs[0], mix_001.inputs[1])
    # mix_001.Color -> material_output.Surface
    normal_mat.links.new(mix_001.outputs[0], material_output.inputs[0])


def depth_mat_nodes(material: Material, min_depth: float, max_depth: float):
    depth_mat = material.node_tree
    # start with a clean node tree
    for node in depth_mat.nodes:
        depth_mat.nodes.remove(node)
    # initialize depth nodes
    # node Material Output
    material_output = depth_mat.nodes.new("ShaderNodeOutputMaterial")
    material_output.target = 'ALL'
    # Displacement
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Thickness
    material_output.inputs[3].default_value = 0.0

    # node Map Range
    map_range = depth_mat.nodes.new("ShaderNodeMapRange")
    map_range.data_type = 'FLOAT'
    map_range.interpolation_type = 'LINEAR'
    map_range.clamp = True
    # From Min
    map_range.inputs[1].default_value = min_depth
    # From Max
    map_range.inputs[2].default_value = max_depth
    # To Min
    map_range.inputs[3].default_value = 1.0
    # To Max
    map_range.inputs[4].default_value = 0.0
    # Steps
    map_range.inputs[5].default_value = 4.0
    # Vector
    map_range.inputs[6].default_value = (0.0, 0.0, 0.0)
    # From_Min_FLOAT3
    map_range.inputs[7].default_value = (0.0, 0.0, 0.0)
    # From_Max_FLOAT3
    map_range.inputs[8].default_value = (1.0, 1.0, 1.0)
    # To_Min_FLOAT3
    map_range.inputs[9].default_value = (0.0, 0.0, 0.0)
    # To_Max_FLOAT3
    map_range.inputs[10].default_value = (1.0, 1.0, 1.0)
    # Steps_FLOAT3
    map_range.inputs[11].default_value = (4.0, 4.0, 4.0)

    # node Camera Data
    camera_data = depth_mat.nodes.new("ShaderNodeCameraData")
    camera_data.outputs[0].hide = True
    camera_data.outputs[2].hide = True

    # Set locations
    material_output.location = (3.111602783203125, 309.34918212890625)
    map_range.location = (-315.3854675292969, 285.913818359375)
    camera_data.location = (-534.7982788085938, 181.81155395507812)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    map_range.width, map_range.height = 140.0, 100.0
    camera_data.width, camera_data.height = 140.0, 100.0

    # initialize depth links
    # map_range.Result -> material_output.Surface
    depth_mat.links.new(map_range.outputs[0], material_output.inputs[0])
    # camera_data.View Z Depth -> map_range.Value
    depth_mat.links.new(camera_data.outputs[1], map_range.inputs[0])


def facing_mat_nodes(material: Material):
    facing_mat = material.node_tree
    # start with a clean node tree
    for node in facing_mat.nodes:
        facing_mat.nodes.remove(node)
    # initialize material nodes
    # node Material Output
    material_output = facing_mat.nodes.new("ShaderNodeOutputMaterial")

    # node Layer Weight
    layer_weight = facing_mat.nodes.new("ShaderNodeLayerWeight")

    # node Invert
    invert = facing_mat.nodes.new("ShaderNodeInvert")

    # Set locations
    material_output.location = (300.0, 300.0)
    layer_weight.location = (-95.3, 279.6)
    invert.location = (85.6, 276.9)

    # initialize material links
    # invert.Color -> material_output.Surface
    facing_mat.links.new(invert.outputs[0], material_output.inputs[0])
    # layer_weight.Facing -> invert.Color
    facing_mat.links.new(layer_weight.outputs[1], invert.inputs[1])

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


def render_beauty(scene_name: str, obj_name: str):
    beauty_scene = bpy.context.scene.copy()

    beauty_scene.name = "SD_texture_bake_beauty"
    beauty_scene.render.engine = 'BLENDER_EEVEE'
    beauty_scene.render.image_settings.file_format = 'PNG'
    beauty_scene.render.image_settings.color_mode = 'RGB'
    beauty_scene.render.image_settings.color_depth = '8'

    # set the output path
    beauty_scene.render.filepath = f"//{scene_name}_SD_maps/{obj_name}_beauty.png"

    # set default environment
    world = bpy.data.worlds.new("World_beauty")
    beauty_scene.world = world

    # render the scene
    bpy.ops.render.render(scene=beauty_scene.name, write_still=True)

    # delete the scene
    bpy.data.scenes.remove(beauty_scene)


def render_normal(scene_name: str, subject_mesh_name: str):
    normal_scene = bpy.context.scene.copy()

    normal_scene.name = "SD_texture_bake_normal"
    normal_scene.render.engine = 'CYCLES'
    normal_scene.render.image_settings.file_format = 'PNG'
    normal_scene.render.image_settings.color_mode = 'RGB'
    normal_scene.render.image_settings.color_depth = '8'
    normal_scene.display_settings.display_device = 'None'
    normal_scene.view_settings.view_transform = 'Standard'

    # set the output path
    normal_scene.render.filepath = f"//{scene_name}_SD_maps/{subject_mesh_name}_normal.png"

    # set the background color to normal map default color
    world = bpy.data.worlds.new("World_normal")
    normal_scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.5, 0.5, 1.0, 1.0)

    # override the materials with a new material displaying the tangent space normal
    normal_material = bpy.data.materials.new(name="SD_texture_normal")
    normal_material.use_nodes = True
    normal_mat_nodes(normal_material)
    normal_scene.view_layers["ViewLayer"].material_override = normal_material

    # render the scene
    bpy.ops.render.render(scene=normal_scene.name, write_still=True)

    # delete the scene
    bpy.data.scenes.remove(normal_scene)


def render_depth(scene_name: str, subject_mesh_name: str):
    depth_scene = bpy.context.scene.copy()

    depth_scene.name = "SD_texture_bake_depth"
    depth_scene.render.engine = 'CYCLES'
    depth_scene.render.image_settings.file_format = 'PNG'
    depth_scene.render.image_settings.color_mode = 'RGB'
    depth_scene.render.image_settings.color_depth = '16'
    depth_scene.display_settings.display_device = 'None'
    depth_scene.view_settings.view_transform = 'Standard'

    # set the output path
    depth_scene.render.filepath = f"//{scene_name}_SD_maps/{subject_mesh_name}_depth.png"

    # set default environment
    world = bpy.data.worlds.new("World_normal")
    depth_scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

    camera = depth_scene.camera
    mesh_collection = bpy.data.collections["Mesh"]

    scene_depth = get_scene_depth(camera, mesh_collection)

    # override the materials with a new material displaying the tangent space normal
    depth_material = bpy.data.materials.new(name="SD_texture_depth")
    depth_material.use_nodes = True

    depth_mat_nodes(depth_material, scene_depth["min"], scene_depth["max"])
    depth_scene.view_layers["ViewLayer"].material_override = depth_material

    # render the scene
    bpy.ops.render.render(scene=depth_scene.name, write_still=True)

    # delete the scene
    bpy.data.scenes.remove(depth_scene)


def render_facing(scene_name: str, subject_mesh_name: str):
    facing_scene = bpy.context.scene.copy()

    facing_scene.name = "SD_texture_bake_facing"
    facing_scene.render.engine = 'CYCLES'
    facing_scene.render.image_settings.file_format = 'OPEN_EXR'
    facing_scene.render.image_settings.color_mode = 'RGB'
    facing_scene.render.image_settings.color_depth = '16'
    facing_scene.display_settings.display_device = 'None'
    facing_scene.view_settings.view_transform = 'Standard'

    # set the output path
    facing_img_mask_path = f"//{scene_name}_SD_maps/{subject_mesh_name}_facing.exr"
    facing_scene.render.filepath = facing_img_mask_path

    # set default environment
    world = bpy.data.worlds.new("World_facing")
    facing_scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

    # override the materials with a new material displaying the tangent space normal
    facing_material = bpy.data.materials.new(name="SD_texture_facing")
    facing_material.use_nodes = True

    facing_mat_nodes(facing_material)
    facing_scene.view_layers["ViewLayer"].material_override = facing_material

    # render the scene
    bpy.ops.render.render(scene=facing_scene.name, write_still=True)

    # delete the scene
    bpy.data.scenes.remove(facing_scene)

    return facing_img_mask_path

def get_blend_name_without_ext() -> str:
    blend_file_path = pathlib.Path(bpy.data.filepath)
    blend_name = blend_file_path.name
    blend_name_without_ext = blend_name.split(".")[0]
    return blend_name_without_ext


def get_sd_setup_scene_data() -> dict:
    active_scene = bpy.context.scene

    assert active_scene.camera is not None, "No camera in the custom properties of the scene"
    assert active_scene["Mesh collection"] is not None, "No mesh collection set in the custom properties of the scene"
    assert active_scene["Subject mesh"] is not None, "No subject mesh set in the custom properties of the scene"

    mesh_collection = active_scene["Mesh collection"]
    camera = active_scene.camera
    blend_name = get_blend_name_without_ext()
    subject_mesh = active_scene["Subject mesh"]
    facing_img_path = None

    if "Facing img path" in active_scene.keys():
        facing_img_path = active_scene["Facing img path"]


    print(f"Blend name: {blend_name}")
    print(f"Subject name: {subject_mesh.name}")
    print(f"Camera: {camera}")
    print(f"Mesh collection: {mesh_collection}")

    sd_scene = {"blend_name": blend_name,
                "subject_mesh": subject_mesh,
                "camera": camera,
                "mesh_collection": mesh_collection,
                "facing_img_path": facing_img_path
                }

    return sd_scene


def diffuse_bake_nodes(material: Material):
    material.use_nodes = True
    diffuse_bake_mat = material.node_tree

    # start with a clean node tree
    for node in list(diffuse_bake_mat.nodes):
        diffuse_bake_mat.nodes.remove(node)

    material_output = diffuse_bake_mat.nodes.new("ShaderNodeOutputMaterial")
    material_output.target = 'ALL'

    diffuse_bsdf = diffuse_bake_mat.nodes.new("ShaderNodeBsdfDiffuse")

    # Set locations
    material_output.location = (300.0, 300.0)
    diffuse_bsdf.location = (-30, 300)
    diffuse_bake_mat.links.new(diffuse_bsdf.outputs[0], material_output.inputs[0])


def render_shadowing(obj: Mesh, scene_name: str, image_name: str):
    print("Object to bake: ", obj)
    print("Object to bake type: ", type(obj))
    print("Object to bake name: ", obj.name)

    backup_scene = bpy.context.scene

    # Create a full copy of the scene
    shadowing_scene = bpy.context.scene.copy()
    shadowing_scene.name = "SD_texture_bake_shadowing"
    shadowing_scene.render.engine = 'CYCLES'
    shadowing_scene.cycles.max_bounces = 0

    # set the active scene to the shadowing scene
    bpy.context.window.scene = shadowing_scene

    select_object_solo(obj)

    # create a directional light
    shadowing_light = bpy.data.lights.new(name="shadowing_light", type='SUN')
    shadowing_light.angle = radians(10)
    shadowing_light_obj = bpy.data.objects.new(name="shadowing_light", object_data=shadowing_light)

    shadowing_scene.collection.objects.link(shadowing_light_obj)

    # set default environment
    world = bpy.data.worlds.new("World_black")
    shadowing_scene.world = world
    world.use_nodes = True
    # set the background color to black
    shadowing_scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

    # get the camera
    camera = shadowing_scene.camera

    # set the camera matrix to the shadowing light matrix
    shadowing_light_obj.matrix_world = camera.matrix_world

    # set up the material for baking
    backup_mat = None
    if obj.active_material:
        backup_mat = obj.active_material

    bake_material = bpy.data.materials.new(name=f"Bake_Mat_{obj.name}")
    obj.active_material = bake_material

    diffuse_bake_nodes(bake_material)

    # bake the light map
    # image_name = f"{obj.name}_shadowing_mask"

    # image to bake into
    if image_name in bpy.data.images.keys():
        bpy.data.images.remove(bpy.data.images[image_name])

    bake_image = bpy.data.images.new(image_name, width=1024, height=1024)

    nodes = bake_material.node_tree.nodes

    texture_node = nodes.new(type='ShaderNodeTexImage')
    texture_node.image = bake_image
    texture_node.name = 'Texture_Bake_Node'
    texture_node.location = -300, 300

    nodes.active = texture_node

    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT'})

    # restore
    if backup_mat:
        obj.active_material = backup_mat

    bpy.data.materials.remove(bake_material)

    # save the baked image
    bake_image_path = f'//{scene_name}_SD_maps/{image_name}.exr'
    bake_image.filepath_raw = bake_image_path
    bake_image.file_format = 'OPEN_EXR'
    bake_image.save()

    # restore
    bpy.context.window.scene = backup_scene
    del shadowing_light

    # delete the scene
    bpy.data.scenes.remove(shadowing_scene)

    return bake_image_path


def select_object_solo(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)


def project_uvs_from_camera(obj, camera, uv_layer_name):
    assert obj.type == 'MESH', "Object to project from is not a mesh"
    assert camera.type == 'CAMERA', "Camera is not a camera"

    print("Projecting from camera: ", camera.name)
    print("Projecting mesh: ", obj.name)

    proj_uv_layer_name = uv_layer_name

    if proj_uv_layer_name not in obj.data.uv_layers.keys():
        obj.data.uv_layers.new(name=proj_uv_layer_name)
    obj.data.uv_layers[proj_uv_layer_name].active = True

    # select the camera
    bpy.context.view_layer.objects.active = camera
    bpy.ops.view3d.object_as_camera()

    # select the mesh
    select_object_solo(obj)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    assert not obj.data.uv_layers[0].active, "First uv layer is active"
    print("Active uv layer: ", obj.data.uv_layers.active.name)

    obj.data.uv_layers[proj_uv_layer_name].active = True
    bpy.ops.uv.project_from_view(camera_bounds=True, correct_aspect=False, scale_to_bounds=False)

    bpy.ops.object.mode_set(mode='OBJECT')

    obj.data.uv_layers[0].active = True

    return proj_uv_layer_name


def get_sd_scene_meshes(sd_scene_data):
    sd_scene_meshes = []

    for mesh in sd_scene_data['mesh_collection'].objects:
        assert mesh.type == 'MESH', f"Object {mesh.name} is not a mesh"
        assert mesh['Shadowing img path'] or mesh['UV Map name'], f"Object {mesh.name} not baked"

        mesh_data = {
            "name": mesh.name,
            "shadowing_img_path": mesh['Shadowing img path'],
            "uv_map_name": mesh['UV Map name'],
        }
        sd_scene_meshes.append(mesh_data)

    return sd_scene_meshes


def transfer_uvs_from_proj_to_shading(context, sd_scene_data: dict, shading_mesh: Mesh):
    active_scene = context.scene
    mesh_collection = sd_scene_data["mesh_collection"]

    active_scene.collection.children.link(sd_scene_data["mesh_collection"])

    for obj in mesh_collection.objects:
        assert obj.type == "MESH", f"Object {obj.name} is not a mesh"

        transfer_uvs(obj, shading_mesh, obj["UV Map name"])
        transfer_uvs(obj, shading_mesh, obj["UV Map mirrored name"])

    active_scene.collection.children.unlink(sd_scene_data["mesh_collection"])


def transfer_uvs(obj_from, obj_to, uv_layer_name):
    select_object_solo(obj_from)
    obj_to.select_set(True)
    obj_from.data.uv_layers[uv_layer_name].active = True

    if uv_layer_name not in obj_to.data.uv_layers:
        obj_to.data.uv_layers.new(name=uv_layer_name)
    obj_to.data.uv_layers[uv_layer_name].active = True
    bpy.ops.object.join_uvs()


def create_sd_shading_mat(subject_name, sd_meshes_data) -> Material:
    for mesh_data in sd_meshes_data:
        print("Mesh name : ", mesh_data["name"])
        print("Mesh shadowing img path : ", mesh_data["shadowing_img_path"])
        print("Mesh UV Map name : ", mesh_data["uv_map_name"])

    return  # todo material


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

def create_shading_scene(shading_scene_name: str, subject_mesh) -> bpy.types.Scene:
    # create a new scene for the shading
    shading_scene = bpy.data.scenes.new(name=shading_scene_name)

    # copy the mesh into the shading scene
    shading_mesh = subject_mesh.copy()
    shading_mesh.data = subject_mesh.data.copy()
    shading_mesh.name = f"{subject_mesh.name}_shading"
    shading_mesh.data.name = f"{subject_mesh.name}_shading"

    shading_scene.collection.objects.link(shading_mesh)

    shading_scene['Subject mesh'] = shading_mesh

    return shading_scene

