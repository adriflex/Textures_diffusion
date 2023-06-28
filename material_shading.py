import bpy
from bpy.types import ShaderNodeTree, Material


def stable_diffusion_map_node_group() -> ShaderNodeTree:
    sd_map_nodegroup = bpy.data.node_groups.new(type="ShaderNodeTree", name="Stable_diffusion_map")

    # initialize stable_diffusion_map nodes

    # node Group Input
    group_input_1 = sd_map_nodegroup.nodes.new("NodeGroupInput")
    # stable_diffusion_map inputs
    # input UV_proj
    sd_map_nodegroup.inputs.new('NodeSocketVector', "UV_proj")
    sd_map_nodegroup.inputs[0].hide_value = True

    # node Group Output
    group_output_1 = sd_map_nodegroup.nodes.new("NodeGroupOutput")
    # stable_diffusion_map outputs
    # output Color
    sd_map_nodegroup.outputs.new('NodeSocketColor', "Color")
    sd_map_nodegroup.outputs[0].attribute_domain = 'POINT'

    # node Image Texture
    image_texture = sd_map_nodegroup.nodes.new("ShaderNodeTexImage")
    image_texture.label = "Stable diffusion generated image"

    # Set locations
    group_input_1.location = (-235.3, -188.6)
    group_output_1.location = (337.0, -46.6)
    image_texture.location = (5.3, -47.3)

    # initialize stable_diffusion_map links

    # image_texture.Color -> group_output_1.Color
    sd_map_nodegroup.links.new(image_texture.outputs[0], group_output_1.inputs[0])
    # group_input_1.UV_proj -> image_texture.Vector
    sd_map_nodegroup.links.new(group_input_1.outputs[0], image_texture.inputs[0])

    return sd_map_nodegroup


stable_diffusion_map_nodegroup = stable_diffusion_map_node_group()


def gradiant_tweaker_node_group() -> ShaderNodeTree:
    gradiant_tweaker = bpy.data.node_groups.new(type="ShaderNodeTree", name="Gradiant_tweaker")

    # initialize gradiant_tweaker nodes
    # node Group Input
    group_input = gradiant_tweaker.nodes.new("NodeGroupInput")

    # gradiant_tweaker inputs

    # input Gradiant
    gradiant_tweaker.inputs.new('NodeSocketFloat', "Gradiant")
    gradiant_tweaker.inputs[0].default_value = 0.0

    # input Position
    gradiant_tweaker.inputs.new('NodeSocketFloat', "Position")
    gradiant_tweaker.inputs[1].default_value = 0.0

    # input Size
    gradiant_tweaker.inputs.new('NodeSocketFloat', "Size")
    gradiant_tweaker.inputs[2].default_value = 1.0

    # node Map Range
    map_range = gradiant_tweaker.nodes.new("ShaderNodeMapRange")

    # To Min
    map_range.inputs[3].default_value = 0.0
    # To Max
    map_range.inputs[4].default_value = 1.0

    # node Group Output
    group_output = gradiant_tweaker.nodes.new("NodeGroupOutput")

    # gradiant_tweaker outputs

    # output Result
    gradiant_tweaker.outputs.new('NodeSocketFloat', "Result")

    # node Math
    math_1 = gradiant_tweaker.nodes.new("ShaderNodeMath")
    math_1.operation = 'ADD'

    # Set locations
    group_input.location = (-352.5, 133.0)
    map_range.location = (354.0, 226.0)
    group_output.location = (576.0, 211.0)
    math_1.location = (-40.5, 32.0)

    # initialize gradiant_tweaker links

    # map_range.Result -> group_output_4.Result
    gradiant_tweaker.links.new(map_range.outputs[0], group_output.inputs[0])
    # group_input_3.Gradiant -> map_range.Value
    gradiant_tweaker.links.new(group_input.outputs[0], map_range.inputs[0])
    # group_input_3.Position -> math_1.Value
    gradiant_tweaker.links.new(group_input.outputs[1], math_1.inputs[0])
    # group_input_3.Size -> math_1.Value
    gradiant_tweaker.links.new(group_input.outputs[2], math_1.inputs[1])
    # math_1.Value -> map_range.From Max
    gradiant_tweaker.links.new(math_1.outputs[0], map_range.inputs[2])
    # group_input_3.Position -> map_range.From Min
    gradiant_tweaker.links.new(group_input.outputs[1], map_range.inputs[1])

    return gradiant_tweaker


gradiant_tweaker_nodegroup = gradiant_tweaker_node_group()


def mirror_mask_node_group() -> ShaderNodeTree:
    mirror_mask = bpy.data.node_groups.new(type="ShaderNodeTree", name="Mirror mask")

    # initialize mirror_mask nodes
    # node Math
    math = mirror_mask.nodes.new("ShaderNodeMath")
    math.operation = 'MULTIPLY'
    # Value_001
    math.inputs[1].default_value = -0.5

    # node Separate XYZ
    separate_xyz = mirror_mask.nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz.outputs[1].hide = True
    separate_xyz.outputs[2].hide = True

    # node Texture Coordinate
    texture_coordinate = mirror_mask.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.outputs[0].hide = True
    texture_coordinate.outputs[1].hide = True
    texture_coordinate.outputs[2].hide = True
    texture_coordinate.outputs[4].hide = True
    texture_coordinate.outputs[5].hide = True
    texture_coordinate.outputs[6].hide = True

    # node Group Output
    group_output_3 = mirror_mask.nodes.new("NodeGroupOutput")
    # mirror_mask outputs
    # output Result
    mirror_mask.outputs.new('NodeSocketFloat', "Result")

    # node Group Input
    group_input_2 = mirror_mask.nodes.new("NodeGroupInput")
    # mirror_mask inputs
    # input Merge mirror size
    mirror_mask.inputs.new('NodeSocketFloat', "Merge mirror size")

    # input Mirror on/off
    mirror_mask.inputs.new('NodeSocketFloat', "Mirror on/off")

    # node Math.001
    math_001 = mirror_mask.nodes.new("ShaderNodeMath")
    math_001.operation = 'MULTIPLY'

    # initialize gradiant_tweaker node group

    # node Group
    group = mirror_mask.nodes.new("ShaderNodeGroup")
    group.node_tree = gradiant_tweaker_nodegroup

    # Set locations
    math.location = (-1.4791259765625, -8.542647361755371)
    separate_xyz.location = (10.93310546875, 92.9891586303711)
    texture_coordinate.location = (-171.0003662109375, 91.5197525024414)
    group_output_3.location = (658.2978515625, 72.97449493408203)
    group_input_2.location = (-417.95587158203125, -0.0)
    math_001.location = (438.0, 89.95614624023438)
    group.location = (217.955810546875, 82.66556549072266)

    # initialize mirror_mask links
    # math_001.Value -> group_output_3.Result
    mirror_mask.links.new(math_001.outputs[0], group_output_3.inputs[0])
    # texture_coordinate.Object -> separate_xyz.Vector
    mirror_mask.links.new(texture_coordinate.outputs[3], separate_xyz.inputs[0])
    # separate_xyz.X -> group.Gradiant
    mirror_mask.links.new(separate_xyz.outputs[0], group.inputs[0])
    # group_input_2.Merge mirror size -> group.Size
    mirror_mask.links.new(group_input_2.outputs[0], group.inputs[2])
    # group_input_2.Merge mirror size -> math.Value
    mirror_mask.links.new(group_input_2.outputs[0], math.inputs[0])
    # math.Value -> group.Position
    mirror_mask.links.new(math.outputs[0], group.inputs[1])
    # group.Result -> math_001.Value
    mirror_mask.links.new(group.outputs[0], math_001.inputs[0])
    # group_input_2.Mirror on/off -> math_001.Value
    mirror_mask.links.new(group_input_2.outputs[1], math_001.inputs[1])

    return mirror_mask


mirror_mask_nodegroup = mirror_mask_node_group()


def mask_mix_node_group() -> ShaderNodeTree:
    mask_mix = bpy.data.node_groups.new(type="ShaderNodeTree", name="Mask_mix")

    # initialize mask_mix nodes

    # node Frame
    frame = mask_mix.nodes.new("NodeFrame")
    frame.label = "Masks mix : facing + cam occlusion"

    # node Frame.001
    frame_001 = mask_mix.nodes.new("NodeFrame")
    frame_001.label = "Masks mix mirrored : facing + cam occlusion"

    # node Frame.002
    frame_002 = mask_mix.nodes.new("NodeFrame")
    frame_002.label = "Custom mask"

    # node Frame.003
    frame_003 = mask_mix.nodes.new("NodeFrame")
    frame_003.label = "Activate Mirror"

    # node Reroute
    reroute = mask_mix.nodes.new("NodeReroute")
    # node Reroute.001
    reroute_001 = mask_mix.nodes.new("NodeReroute")
    # node Group Input.001
    group_input_001 = mask_mix.nodes.new("NodeGroupInput")
    group_input_001.outputs[0].hide = True
    group_input_001.outputs[1].hide = True
    group_input_001.outputs[3].hide = True
    group_input_001.outputs[7].hide = True
    group_input_001.outputs[8].hide = True
    group_input_001.outputs[9].hide = True
    group_input_001.outputs[10].hide = True
    group_input_001.outputs[11].hide = True

    # mask_mix inputs

    # input Cam occlusion
    mask_mix.inputs.new('NodeSocketFloat', "Cam occlusion")

    # input Cam occlusion mirrored
    mask_mix.inputs.new('NodeSocketFloat', "Cam occlusion mirrored")

    # input Facing
    mask_mix.inputs.new('NodeSocketFloat', "Facing")

    # input Facing Mirrored
    mask_mix.inputs.new('NodeSocketFloat', "Facing Mirrored")

    # input Facing intensity
    mask_mix.inputs.new('NodeSocketFloat', "Facing intensity")
    mask_mix.inputs[4].default_value = 0.0
    mask_mix.inputs[4].min_value = 0.0
    mask_mix.inputs[4].max_value = 2.0
    mask_mix.inputs[4].attribute_domain = 'POINT'

    # input Facing Position
    mask_mix.inputs.new('NodeSocketFloat', "Facing Position")
    mask_mix.inputs[5].default_value = 0.2

    # input Facing Size
    mask_mix.inputs.new('NodeSocketFloat', "Facing Size")
    mask_mix.inputs[6].default_value = 0.2
    mask_mix.inputs[6].min_value = 0.0
    mask_mix.inputs[6].max_value = 10.0

    # input Custom mask Color
    mask_mix.inputs.new('NodeSocketColor', "Custom mask Color")

    # input Custom mask Alpha
    mask_mix.inputs.new('NodeSocketFloatFactor', "Custom mask Alpha")

    # input Custom mask intensity
    mask_mix.inputs.new('NodeSocketFloat', "Custom mask intensity")
    mask_mix.inputs[9].default_value = 1.0
    mask_mix.inputs[9].min_value = 0.0
    mask_mix.inputs[9].max_value = 1.0

    # input Mirror on/off
    mask_mix.inputs.new('NodeSocketFloat', "Mirror on/off")
    mask_mix.inputs[10].default_value = 0.0
    mask_mix.inputs[10].min_value = 0.0
    mask_mix.inputs[10].max_value = 1.0

    # node Math
    math_2 = mask_mix.nodes.new("ShaderNodeMath")
    math_2.operation = 'MULTIPLY'
    math_2.use_clamp = True

    # node Group Input
    group_input_7 = mask_mix.nodes.new("NodeGroupInput")
    group_input_7.outputs[1].hide = True
    group_input_7.outputs[2].hide = True
    group_input_7.outputs[3].hide = True
    group_input_7.outputs[4].hide = True
    group_input_7.outputs[5].hide = True
    group_input_7.outputs[6].hide = True
    group_input_7.outputs[7].hide = True
    group_input_7.outputs[8].hide = True
    group_input_7.outputs[9].hide = True
    group_input_7.outputs[10].hide = True
    group_input_7.outputs[11].hide = True

    # node Math.001
    math_001_1 = mask_mix.nodes.new("ShaderNodeMath")
    math_001_1.operation = 'MULTIPLY'
    math_001_1.use_clamp = True

    # node Math.005
    math_005 = mask_mix.nodes.new("ShaderNodeMath")
    math_005.operation = 'MULTIPLY'
    math_005.use_clamp = True

    # node Group.001
    group_001 = mask_mix.nodes.new("ShaderNodeGroup")
    group_001.node_tree = gradiant_tweaker_nodegroup

    # node Reroute.003
    reroute_003 = mask_mix.nodes.new("NodeReroute")
    # node Reroute.002
    reroute_002 = mask_mix.nodes.new("NodeReroute")
    # node Group Input.004
    group_input_004 = mask_mix.nodes.new("NodeGroupInput")
    group_input_004.outputs[0].hide = True
    group_input_004.outputs[2].hide = True
    group_input_004.outputs[3].hide = True
    group_input_004.outputs[4].hide = True
    group_input_004.outputs[5].hide = True
    group_input_004.outputs[6].hide = True
    group_input_004.outputs[7].hide = True
    group_input_004.outputs[8].hide = True
    group_input_004.outputs[9].hide = True
    group_input_004.outputs[10].hide = True
    group_input_004.outputs[11].hide = True

    # node Math.004
    math_004 = mask_mix.nodes.new("ShaderNodeMath")
    math_004.operation = 'MULTIPLY'
    math_004.use_clamp = True

    # node Group Input.005
    group_input_005 = mask_mix.nodes.new("NodeGroupInput")
    group_input_005.outputs[0].hide = True
    group_input_005.outputs[1].hide = True
    group_input_005.outputs[2].hide = True
    group_input_005.outputs[7].hide = True
    group_input_005.outputs[8].hide = True
    group_input_005.outputs[9].hide = True
    group_input_005.outputs[10].hide = True
    group_input_005.outputs[11].hide = True

    # node Mix
    mix_1 = mask_mix.nodes.new("ShaderNodeMixRGB")

    # node Mix.001
    mix_001 = mask_mix.nodes.new("ShaderNodeMixRGB")

    # node Group Input.002
    group_input_002 = mask_mix.nodes.new("NodeGroupInput")
    group_input_002.outputs[0].hide = True
    group_input_002.outputs[1].hide = True
    group_input_002.outputs[2].hide = True
    group_input_002.outputs[3].hide = True
    group_input_002.outputs[4].hide = True
    group_input_002.outputs[5].hide = True
    group_input_002.outputs[6].hide = True
    group_input_002.outputs[10].hide = True
    group_input_002.outputs[11].hide = True

    # node Math.002
    math_002 = mask_mix.nodes.new("ShaderNodeMath")
    math_002.operation = 'MULTIPLY'
    math_002.inputs[2].hide = True

    # node Math.003
    math_003 = mask_mix.nodes.new("ShaderNodeMath")
    math_003.operation = 'ADD'

    # node Group Output
    group_output_9 = mask_mix.nodes.new("NodeGroupOutput")

    # mask_mix outputs

    # output Mask
    mask_mix.outputs.new('NodeSocketFloat', "Mask")

    # node Group Input.003
    group_input_003 = mask_mix.nodes.new("NodeGroupInput")
    group_input_003.outputs[0].hide = True
    group_input_003.outputs[1].hide = True
    group_input_003.outputs[2].hide = True
    group_input_003.outputs[3].hide = True
    group_input_003.outputs[4].hide = True
    group_input_003.outputs[5].hide = True
    group_input_003.outputs[6].hide = True
    group_input_003.outputs[7].hide = True
    group_input_003.outputs[8].hide = True
    group_input_003.outputs[9].hide = True
    group_input_003.outputs[11].hide = True

    # node Math.006
    math_006 = mask_mix.nodes.new("ShaderNodeMath")
    math_006.operation = 'MULTIPLY'
    math_006.use_clamp = True

    # node Group
    group_2 = mask_mix.nodes.new("ShaderNodeGroup")
    group_2.node_tree = gradiant_tweaker_nodegroup

    # Set parents
    reroute.parent = frame
    reroute_001.parent = frame
    group_input_001.parent = frame
    math_2.parent = frame
    group_input_7.parent = frame
    math_001_1.parent = frame
    math_005.parent = frame_001
    group_001.parent = frame_001
    reroute_003.parent = frame_001
    reroute_002.parent = frame_001
    group_input_004.parent = frame_001
    math_004.parent = frame_001
    group_input_005.parent = frame_001
    mix_1.parent = frame_002
    mix_001.parent = frame_002
    group_input_002.parent = frame_002
    math_002.parent = frame_002
    group_input_003.parent = frame_003
    math_006.parent = frame_003
    group_2.parent = frame

    # Set locations
    frame.location = (80.0, -20.0)
    frame_001.location = (-160.0, 220.0)
    frame_002.location = (-20.0, 20.0)
    frame_003.location = (-30.0, 10.0)
    reroute.location = (-180.0, -160.0)
    reroute_001.location = (-40.0, -160.0)
    group_input_001.location = (-400.0, -20.0)
    math_2.location = (0.0, 20.0)
    group_input_7.location = (0.0, 100.0)
    math_001_1.location = (240.0, 180.0)
    math_005.location = (278.3137512207031, -667.3348388671875)
    group_001.location = (98.31375885009766, -667.3348388671875)
    reroute_003.location = (238.31375122070312, -847.3348388671875)
    reroute_002.location = (98.31375885009766, -847.3348388671875)
    group_input_004.location = (280.0, -580.0)
    math_004.location = (480.0, -500.0)
    group_input_005.location = (-120.0, -720.0)
    mix_1.location = (1110.0, 190.0)
    mix_001.location = (1100.0, 0.0)
    group_input_002.location = (560.0, 20.0)
    math_002.location = (820.0, -40.0)
    math_003.location = (1660.0, 280.0)
    group_output_9.location = (1840.0, 280.0)
    group_input_003.location = (1450.0, -110.0)
    math_006.location = (1450.0, 70.0)
    group_2.location = (-180.0, 20.0)

    # Set dimensions
    frame.width, frame.height = 840.0, 408.0
    frame_001.width, frame_001.height = 800.0, 415.3348388671875
    frame_002.width, frame_002.height = 750.0, 421.0
    frame_003.width, frame_003.height = 200.0, 292.0
    reroute.width, reroute.height = 16.0, 100.0
    reroute_001.width, reroute_001.height = 16.0, 100.0
    group_input_001.width, group_input_001.height = 140.0, 100.0
    math_2.width, math_2.height = 140.0, 100.0
    group_input_7.width, group_input_7.height = 140.0, 100.0
    math_001_1.width, math_001_1.height = 140.0, 100.0
    math_005.width, math_005.height = 140.0, 100.0
    group_001.width, group_001.height = 140.0, 100.0
    reroute_003.width, reroute_003.height = 16.0, 100.0
    reroute_002.width, reroute_002.height = 16.0, 100.0
    group_input_004.width, group_input_004.height = 140.0, 100.0
    math_004.width, math_004.height = 140.0, 100.0
    group_input_005.width, group_input_005.height = 140.0, 100.0
    mix_1.width, mix_1.height = 140.0, 100.0
    mix_001.width, mix_001.height = 140.0, 100.0
    group_input_002.width, group_input_002.height = 140.0, 100.0
    math_002.width, math_002.height = 140.0, 100.0
    math_003.width, math_003.height = 140.0, 100.0
    group_output_9.width, group_output_9.height = 140.0, 100.0
    group_input_003.width, group_input_003.height = 140.0, 100.0
    math_006.width, math_006.height = 140.0, 100.0
    group_2.width, group_2.height = 150.2752685546875, 100.0

    # initialize mask_mix links
    # math_2.Value -> math_001_1.Value
    mask_mix.links.new(math_2.outputs[0], math_001_1.inputs[1])
    # group_2.Result -> math_2.Value
    mask_mix.links.new(group_2.outputs[0], math_2.inputs[0])
    # group_input_001.Facing -> group_2.Gradiant
    mask_mix.links.new(group_input_001.outputs[2], group_2.inputs[0])
    # group_input_001.Facing Size -> group_2.Size
    mask_mix.links.new(group_input_001.outputs[6], group_2.inputs[2])
    # group_input_001.Facing Position -> group_2.Position
    mask_mix.links.new(group_input_001.outputs[5], group_2.inputs[1])
    # group_input_001.Facing intensity -> reroute.Input
    mask_mix.links.new(group_input_001.outputs[4], reroute.inputs[0])
    # reroute.Output -> reroute_001.Input
    mask_mix.links.new(reroute.outputs[0], reroute_001.inputs[0])
    # math_001_1.Value -> mix_1.Color1
    mask_mix.links.new(math_001_1.outputs[0], mix_1.inputs[1])
    # math_003.Value -> group_output_9.Mask
    mask_mix.links.new(math_003.outputs[0], group_output_9.inputs[0])
    # group_input_7.Cam occlusion -> math_001_1.Value
    mask_mix.links.new(group_input_7.outputs[0], math_001_1.inputs[0])
    # math_002.Value -> mix_1.Fac
    mask_mix.links.new(math_002.outputs[0], mix_1.inputs[0])
    # group_input_002.Custom mask Color -> mix_1.Color2
    mask_mix.links.new(group_input_002.outputs[7], mix_1.inputs[2])
    # group_input_002.Custom mask Alpha -> math_002.Value
    mask_mix.links.new(group_input_002.outputs[8], math_002.inputs[0])
    # group_input_002.Custom mask intensity -> math_002.Value
    mask_mix.links.new(group_input_002.outputs[9], math_002.inputs[1])
    # reroute_001.Output -> math_2.Value
    mask_mix.links.new(reroute_001.outputs[0], math_2.inputs[1])
    # math_005.Value -> math_004.Value
    mask_mix.links.new(math_005.outputs[0], math_004.inputs[1])
    # group_001.Result -> math_005.Value
    mask_mix.links.new(group_001.outputs[0], math_005.inputs[0])
    # group_input_005.Facing Size -> group_001.Size
    mask_mix.links.new(group_input_005.outputs[6], group_001.inputs[2])
    # group_input_005.Facing Position -> group_001.Position
    mask_mix.links.new(group_input_005.outputs[5], group_001.inputs[1])
    # group_input_005.Facing intensity -> reroute_002.Input
    mask_mix.links.new(group_input_005.outputs[4], reroute_002.inputs[0])
    # reroute_002.Output -> reroute_003.Input
    mask_mix.links.new(reroute_002.outputs[0], reroute_003.inputs[0])
    # reroute_003.Output -> math_005.Value
    mask_mix.links.new(reroute_003.outputs[0], math_005.inputs[1])
    # group_input_004.Cam occlusion mirrored -> math_004.Value
    mask_mix.links.new(group_input_004.outputs[1], math_004.inputs[0])
    # group_input_005.Facing Mirrored -> group_001.Gradiant
    mask_mix.links.new(group_input_005.outputs[3], group_001.inputs[0])
    # math_004.Value -> mix_001.Color1
    mask_mix.links.new(math_004.outputs[0], mix_001.inputs[1])
    # math_002.Value -> mix_001.Fac
    mask_mix.links.new(math_002.outputs[0], mix_001.inputs[0])
    # group_input_002.Custom mask Color -> mix_001.Color2
    mask_mix.links.new(group_input_002.outputs[7], mix_001.inputs[2])
    # mix_1.Color -> math_003.Value
    mask_mix.links.new(mix_1.outputs[0], math_003.inputs[0])
    # math_006.Value -> math_003.Value
    mask_mix.links.new(math_006.outputs[0], math_003.inputs[1])
    # mix_001.Color -> math_006.Value
    mask_mix.links.new(mix_001.outputs[0], math_006.inputs[0])
    # group_input_003.Mirror on/off -> math_006.Value
    mask_mix.links.new(group_input_003.outputs[10], math_006.inputs[1])

    return mask_mix


mask_mix_nodegroup = mask_mix_node_group()


def custom_mask_node_group(proj_name: str) -> ShaderNodeTree:
    custom_mask = bpy.data.node_groups.new(type="ShaderNodeTree", name=f"Custom mask {proj_name}")

    # node Custom mask 01
    custom_mask_01 = custom_mask.nodes.new("ShaderNodeTexImage")
    custom_mask_01.label = f"Custom mask {proj_name}"

    # node Group Output
    group_output = custom_mask.nodes.new("NodeGroupOutput")
    # custom_mask_proj_01 outputs

    # output Color
    custom_mask.outputs.new('NodeSocketColor', "Color")
    custom_mask.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0)
    custom_mask.outputs[0].attribute_domain = 'POINT'

    # output Alpha
    custom_mask.outputs.new('NodeSocketFloat', "Alpha")
    custom_mask.outputs[1].default_value = 0.0
    custom_mask.outputs[1].attribute_domain = 'POINT'

    # node Group Input
    group_input = custom_mask.nodes.new("NodeGroupInput")
    # input Vector
    custom_mask.inputs.new('NodeSocketVector', "Vector")
    custom_mask.inputs[0].hide_value = True

    # Set locations
    custom_mask_01.location = (0.0, 0.0)
    group_output.location = (372.0, -0.0)
    group_input.location = (-180.0, -120.0)

    # initialize custom_mask_proj_01 links

    # custom_mask_01.Color -> group_output.Color
    custom_mask.links.new(custom_mask_01.outputs[0], group_output.inputs[0])
    # custom_mask_01.Alpha -> group_output.Alpha
    custom_mask.links.new(custom_mask_01.outputs[1], group_output.inputs[1])
    # group_input.Vector -> custom_mask_01.Vector
    custom_mask.links.new(group_input.outputs[0], custom_mask_01.inputs[0])

    return custom_mask


def facing_mask_node_group(proj_name: str, image_path: str, image_mirrored_path: str) -> ShaderNodeTree:
    facing_mask = bpy.data.node_groups.new(type="ShaderNodeTree", name=f"Facing mask {proj_name}")

    # initialize facing_mask_proj_01 nodes

    # node Facing mask 01
    facing_mask_01 = facing_mask.nodes.new("ShaderNodeTexImage")
    facing_mask_01.label = f"Facing mask {proj_name}"
    facing_mask_01.image = bpy.data.images.load(image_path, check_existing=True)

    # node Facing mask mirror
    facing_mask_mirror = facing_mask.nodes.new("ShaderNodeTexImage")
    facing_mask_mirror.label = f"Facing mask {proj_name} mirror"
    facing_mask_mirror.image = bpy.data.images.load(image_mirrored_path, check_existing=True)

    # node Group Output
    group_output_6 = facing_mask.nodes.new("NodeGroupOutput")

    # facing_mask_proj_01 outputs

    # output Mask
    facing_mask.outputs.new('NodeSocketColor', "Mask")

    # output Mask mirrored
    facing_mask.outputs.new('NodeSocketColor', "Mask mirrored")

    # Set locations
    facing_mask_01.location = (100.0, 40.0)
    facing_mask_mirror.location = (100.27884674072266, -170.25985717773438)
    group_output_6.location = (560.0, 40.0)

    # initialize facing_mask_proj_01 links
    # facing_mask_01.Color -> group_output_6.Mask
    facing_mask.links.new(facing_mask_01.outputs[0], group_output_6.inputs[0])
    # facing_mask_mirror.Color -> group_output_6.Mask mirrored
    facing_mask.links.new(facing_mask_mirror.outputs[0], group_output_6.inputs[1])


def cam_occlusion_node_group(proj_name: str, image_path: str, image_mirrored_path: str) -> ShaderNodeTree:
    cam_occlusion = bpy.data.node_groups.new(type="ShaderNodeTree", name=f"Cam occlusion {proj_name}")

    # initialize cam_occlusion nodes

    # node Group Output
    group_output = cam_occlusion.nodes.new("NodeGroupOutput")

    # cam_occlusion outputs

    # output Cam occlusion
    cam_occlusion.outputs.new('NodeSocketFloat', "Cam occlusion")

    # output Cam occlusion
    cam_occlusion.outputs.new('NodeSocketFloat', "Cam occlusion mirrored")

    # node Proj 1 mask
    proj_mask = cam_occlusion.nodes.new("ShaderNodeTexImage")
    proj_mask.label = f"Mask cam occlusion {proj_name}"
    proj_mask.image = bpy.data.images.load(image_path, check_existing=True)

    # node Proj 1 mask.001
    proj_mask_mirrored = cam_occlusion.nodes.new("ShaderNodeTexImage")
    proj_mask_mirrored.label = f"Mask cam occlusion {proj_name} mirrored"
    proj_mask_mirrored.image = bpy.data.images.load(image_mirrored_path, check_existing=True)

    # Set locations
    group_output.location = (400.0, 0.0)
    proj_mask_mirrored.location = (0.0, -220.0)
    proj_mask.location = (0.0, 0.0)

    # initialize cam_occlusion links

    # proj_1_mask.Color -> group_output.Cam occlusion
    cam_occlusion.links.new(proj_mask.outputs[0], group_output.inputs[0])
    # proj_1_mask_001.Alpha -> group_output.Cam occlusion mirrored
    cam_occlusion.links.new(proj_mask_mirrored.outputs[1], group_output.inputs[1])

    return cam_occlusion


def setting_mask_proj_node_group(proj_name, facing_mask_nodegroup, cam_occlusion_nodegroup) -> ShaderNodeTree:
    setting_mask_proj = bpy.data.node_groups.new(type="ShaderNodeTree", name=f"Setting mask {proj_name}")

    # initialize setting_mask_proj nodes

    # node Group Output
    group_output = setting_mask_proj.nodes.new("NodeGroupOutput")

    # setting_mask_proj outputs

    # output Mask proj 01
    setting_mask_proj.outputs.new('NodeSocketFloat', f"Mask {proj_name}")

    custom_mask_nodegroup = custom_mask_node_group(proj_name)

    # node Custom mask proj 01
    custom_mask_proj_01_2 = setting_mask_proj.nodes.new("ShaderNodeGroup")
    custom_mask_proj_01_2.label = f"Custom mask {proj_name}"
    custom_mask_proj_01_2.node_tree = custom_mask_nodegroup
    # Input_2
    custom_mask_proj_01_2.inputs[0].default_value = (0.0, 0.0, 0.0)

    # node Group Input
    group_input = setting_mask_proj.nodes.new("NodeGroupInput")

    # setting_mask_proj inputs

    # input Mirror on/off
    setting_mask_proj.inputs.new('NodeSocketFloat', "Mirror on/off")

    # node Node.001
    facing_mask = setting_mask_proj.nodes.new("ShaderNodeGroup")
    facing_mask.node_tree = facing_mask_nodegroup

    # node Group
    group_1 = setting_mask_proj.nodes.new("ShaderNodeGroup")
    group_1.node_tree = cam_occlusion_nodegroup

    # initialize mask_mix node group

    # node Mask mix 01
    mask_mix_01 = setting_mask_proj.nodes.new("ShaderNodeGroup")
    mask_mix_01.label = "Mask mix 01"
    mask_mix_01.node_tree = mask_mix_node_group()
    # Input_5
    mask_mix_01.inputs[4].default_value = 1.0
    # Input_3
    mask_mix_01.inputs[5].default_value = 0.2
    # Input_4
    mask_mix_01.inputs[6].default_value = 0.2
    # Input_10
    mask_mix_01.inputs[9].default_value = 1.0

    # Set locations
    group_output.location = (580.0, 220.0)
    custom_mask_proj_01_2.location = (-20.0, -60.0)
    group_input.location = (40.0, -200.0)
    facing_mask.location = (20.0, 120.0)
    group_1.location = (-29.145263671875, 240.0)
    mask_mix_01.location = (320.0, 220.0)

    # initialize setting_mask_proj links

    # mask_mix_01.Mask -> group_output_5.Mask proj 01
    setting_mask_proj.links.new(mask_mix_01.outputs[0], group_output.inputs[0])
    # node_001.Mask -> mask_mix_01.Facing
    setting_mask_proj.links.new(facing_mask.outputs[0], mask_mix_01.inputs[2])
    # custom_mask_proj_01_2.Color -> mask_mix_01.Custom mask Color
    setting_mask_proj.links.new(custom_mask_proj_01_2.outputs[0], mask_mix_01.inputs[7])
    # custom_mask_proj_01_2.Alpha -> mask_mix_01.Custom mask Alpha
    setting_mask_proj.links.new(custom_mask_proj_01_2.outputs[1], mask_mix_01.inputs[8])
    # group_1.Cam occlusion -> mask_mix_01.Cam occlusion
    setting_mask_proj.links.new(group_1.outputs[0], mask_mix_01.inputs[0])
    # group_input_4.Mirror on/off -> mask_mix_01.Mirror on/off
    setting_mask_proj.links.new(group_input.outputs[0], mask_mix_01.inputs[10])
    # group_1.Cam occlusion mirrored -> mask_mix_01.Cam occlusion mirrored
    setting_mask_proj.links.new(group_1.outputs[1], mask_mix_01.inputs[1])
    # node_001.Mask mirrored -> mask_mix_01.Facing Mirrored
    setting_mask_proj.links.new(facing_mask.outputs[1], mask_mix_01.inputs[3])

    return setting_mask_proj


def proj_node_group(proj_name, uv_proj_name, uv_proj_mirrored_name) -> bpy.types.NodeGroup:
    proj = bpy.data.node_groups.new(type="ShaderNodeTree", name=f"Proj {proj_name}")

    # initialize proj_01 nodes

    # node Value Mirror on/off
    value = proj.nodes.new("ShaderNodeValue")
    value.label = "Mirror on/off"
    value.outputs[0].default_value = 0.0

    # node Value Mirror size
    value_001 = proj.nodes.new("ShaderNodeValue")
    value_001.label = "Mirror size"
    value_001.outputs[0].default_value = 0.5

    # node UV Map
    uv_map_proj = proj.nodes.new("ShaderNodeUVMap")
    uv_map_proj.uv_map = uv_proj_name

    # node UV Map.001
    uv_map_proj_mirrored = proj.nodes.new("ShaderNodeUVMap")
    uv_map_proj_mirrored.uv_map = uv_proj_mirrored_name

    # node Group Output
    group_output_2 = proj.nodes.new("NodeGroupOutput")

    # proj_01 outputs

    # output Mask proj 01
    proj.outputs.new('NodeSocketFloat', "Mask proj 01")

    # output Color Proj 01
    proj.outputs.new('NodeSocketColor', "Color Proj 01")

    # node Mix
    mix = proj.nodes.new("ShaderNodeMixRGB")
    mix.label = "Mirror Mix"

    # node Stable_diffusion_map
    stable_diffusion_map_2 = proj.nodes.new("ShaderNodeGroup")
    stable_diffusion_map_2.node_tree = stable_diffusion_map_nodegroup

    # node Stable_diffusion_map_mirror
    stable_diffusion_map_mirror = proj.nodes.new("ShaderNodeGroup")
    stable_diffusion_map_mirror.label = "Stable diffusion map mirror"
    stable_diffusion_map_mirror.node_tree = stable_diffusion_map_nodegroup

    # initialize mirror_mask node group

    # node Mirror mask
    mirror_mask_1 = proj.nodes.new("ShaderNodeGroup")
    mirror_mask_1.node_tree = mirror_mask_nodegroup

    # initialize setting_mask_proj node group

    setting_mask_proj_nodegroup = setting_mask_proj_node_group(proj_name, facing_mask_nodegroup,
                                                               cam_occlusion_nodegroup)  # todo: add inputs

    # node Setting mask proj 01
    setting_mask_proj_01 = proj.nodes.new("ShaderNodeGroup")
    setting_mask_proj_01.label = "Setting mask proj 01"
    setting_mask_proj_01.node_tree = setting_mask_proj_nodegroup

    # Set locations
    value.location = (-152.6248321533203, 173.09640502929688)
    value_001.location = (-151.71066284179688, 79.67152404785156)
    uv_map_proj.location = (-181.8487548828125, -60.0)
    uv_map_proj_mirrored.location = (-179.5960235595703, -190.60731506347656)
    group_output_2.location = (705.1361694335938, 12.770013809204102)
    mix.location = (440.0, 0.0)
    stable_diffusion_map_mirror.location = (78.4936294555664, -173.1095428466797)
    stable_diffusion_map_2.location = (80.0, -40.0)
    mirror_mask_1.location = (100.0, 100.0)
    setting_mask_proj_01.location = (100.0, 220.0)

    # initialize proj_01 links
    # setting_mask_proj_01.Mask proj 01 -> group_output_2.Mask proj 01
    proj.links.new(setting_mask_proj_01.outputs[0], group_output_2.inputs[0])
    # mirror_mask_1.Result -> mix.Fac
    proj.links.new(mirror_mask_1.outputs[0], mix.inputs[0])
    # stable_diffusion_map_2.Color -> mix.Color1
    proj.links.new(stable_diffusion_map_2.outputs[0], mix.inputs[1])
    # stable_diffusion_map_mirror.Color -> mix.Color2
    proj.links.new(stable_diffusion_map_mirror.outputs[0], mix.inputs[2])
    # mix.Color -> group_output_2.Color Proj 01
    proj.links.new(mix.outputs[0], group_output_2.inputs[1])
    # uv_map.UV -> stable_diffusion_map_2.UV_proj
    proj.links.new(uv_map_proj.outputs[0], stable_diffusion_map_2.inputs[0])
    # uv_map_001.UV -> stable_diffusion_map_mirror.UV_proj
    proj.links.new(uv_map_proj_mirrored.outputs[0], stable_diffusion_map_mirror.inputs[0])
    # value.Value -> mirror_mask_1.Mirror on/off
    proj.links.new(value.outputs[0], mirror_mask_1.inputs[1])
    # value_001.Value -> mirror_mask_1.Merge mirror size
    proj.links.new(value_001.outputs[0], mirror_mask_1.inputs[0])
    # value.Value -> setting_mask_proj_01.Mirror on/off
    proj.links.new(value.outputs[0], setting_mask_proj_01.inputs[0])

    return proj


def clean_map_proj_material(proj_name: str, proj_nodegroup: ShaderNodeTree) -> Material:
    mat = bpy.data.materials.new(name=f"clean_map_{proj_name}")
    mat.use_nodes = True

    # initialize clean_map_proj_01 node group
    def clean_map_proj_node_group():
        mat_nodetree = mat.node_tree
        # start with a clean node tree
        for node in mat_nodetree.nodes:
            mat_nodetree.nodes.remove(node)
        # initialize clean_map_proj_01 nodes
        # node Frame
        frame = mat_nodetree.nodes.new("NodeFrame")
        frame.label = "Stable diffusion image here"

        # node Frame.001
        frame_001 = mat_nodetree.nodes.new("NodeFrame")
        frame_001.label = "Custom mask for proj 01"

        # node Mix preview
        mix_preview = mat_nodetree.nodes.new("ShaderNodeMixRGB")

        # node Material Output
        material_output = mat_nodetree.nodes.new("ShaderNodeOutputMaterial")

        # initialize custom_mask node group

        custom_mask_nodetree = custom_mask_node_group(proj_name)

        # node Custom mask proj 01
        custom_mask_proj = mat_nodetree.nodes.new("ShaderNodeGroup")
        custom_mask_proj.label = f"Custom mask {proj_name}"
        custom_mask_proj.node_tree = custom_mask_nodetree

        # initialize stable_diffusion_map node group

        # node Stable_diffusion_map
        stable_diffusion_map = mat_nodetree.nodes.new("ShaderNodeGroup")
        stable_diffusion_map.node_tree = stable_diffusion_map_nodegroup

        # node Emission
        emission = mat_nodetree.nodes.new("ShaderNodeEmission")

        # initialize proj node group

        # node Node
        node = mat_nodetree.nodes.new("ShaderNodeGroup")
        node.node_tree = proj_nodegroup

        # Set parents
        custom_mask_proj.parent = frame_001
        stable_diffusion_map.parent = frame

        # Set locations
        frame.location = (-30.0, 10.0)
        frame_001.location = (-30.0, 10.0)
        mix_preview.location = (260.0, 280.0)
        material_output.location = (700.0, 280.0)
        custom_mask_proj.location = (-450.0, 130.0)
        stable_diffusion_map.location = (-490.0, 310.0)
        emission.location = (480.0, 260.0)
        node.location = (0.0, 200.0)

        # initialize clean_map_proj_01 links

        # node.Color Proj 01 -> mix_003.Color2
        mat_nodetree.links.new(node.outputs[1], mix_preview.inputs[2])
        # mix_003.Color -> emission.Color
        mat_nodetree.links.new(mix_preview.outputs[0], emission.inputs[0])
        # node.Mask proj 01 -> mix_003.Fac
        mat_nodetree.links.new(node.outputs[0], mix_preview.inputs[0])
        # emission.Emission -> material_output.Surface
        mat_nodetree.links.new(emission.outputs[0], material_output.inputs[0])

    clean_map_proj_node_group()

    return mat
