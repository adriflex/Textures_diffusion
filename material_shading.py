import bpy


def create_sd_gen_node_group(image_path) -> bpy.types.NodeGroup:
    node_group = bpy.data.node_groups.new(type="ShaderNodeTree", name="Stable_diffusion_gen")

    group_input = node_group.nodes.new("NodeGroupInput")
    node_group.inputs.new('NodeSocketVector', "UV_proj")
    node_group.inputs[0].hide_value = True

    group_output = node_group.nodes.new("NodeGroupOutput")
    node_group.outputs.new('NodeSocketColor', "Color")

    # node Image Texture
    image_texture = node_group.nodes.new("ShaderNodeTexImage")
    image_texture.image = bpy.data.images.load(image_path, check_existing=True)

    # Set locations
    group_input.location = (-200.0, -200.0)
    group_output.location = (280.0, 0.0)
    image_texture.location = (0.0, 0.0)

    # initialize stable_diffusion_map links
    node_group.links.new(image_texture.outputs[0], group_output.inputs[0])
    node_group.links.new(group_input.outputs[0], image_texture.inputs[0])

    return node_group


def create_gradiant_tweaker_node_group() -> bpy.types.NodeGroup:
    node_group = bpy.data.node_groups.new(type="ShaderNodeTree", name="Gradiant_tweaker")

    # initialize gradiant_tweaker_001 nodes

    group_input = node_group.nodes.new("NodeGroupInput")

    node_group.inputs.new('NodeSocketFloat', "Gradiant")
    node_group.inputs[0].default_value = 0.0

    node_group.inputs.new('NodeSocketFloat', "Position")
    node_group.inputs[1].default_value = 1.0

    node_group.inputs.new('NodeSocketFloat', "Size")
    node_group.inputs[2].default_value = 1.0

    # node Map Range
    map_range = node_group.nodes.new("ShaderNodeMapRange")

    # node Group Output
    group_output = node_group.nodes.new("NodeGroupOutput")
    node_group.outputs.new('NodeSocketFloat', "Result")

    # node Math
    math = node_group.nodes.new("ShaderNodeMath")
    math.operation = 'ADD'

    # Set locations
    group_input.location = (-352.5, 133.5)
    map_range.location = (354.5, 226.0)
    group_output.location = (576.5, 211)
    math.location = (-40.5, 32.5)

    # initialize gradiant_tweaker_001 links

    node_group.links.new(map_range.outputs[0], group_output.inputs[0])
    node_group.links.new(group_input.outputs[0], map_range.inputs[0])
    node_group.links.new(group_input.outputs[1], math.inputs[0])
    node_group.links.new(group_input.outputs[2], math.inputs[1])
    node_group.links.new(math.outputs[0], map_range.inputs[2])
    node_group.links.new(group_input.outputs[1], map_range.inputs[1])

    return node_group


def create_mask_mix_node_group(gradiant_tweaker_node_group) -> bpy.types.NodeGroup:
    node_group = bpy.data.node_groups.new(type="ShaderNodeTree", name="Mask_mix")

    # initialize mask_mix nodes
    frame_1 = node_group.nodes.new("NodeFrame")
    frame_1.label = "Masks mix : facing + cam occlu"

    frame_2 = node_group.nodes.new("NodeFrame")
    frame_2.label = "Masks mix mirrored : facing + cam occlu"

    frame_3 = node_group.nodes.new("NodeFrame")
    frame_3.label = "Custom mask"

    frame_4 = node_group.nodes.new("NodeFrame")
    frame_4.label = "Activate Mirror"

    # mask_mix inputs
    # input Custom mask Color
    node_group.inputs.new('NodeSocketColor', "Custom mask Color")
    node_group.inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)

    # input Custom mask Alpha
    node_group.inputs.new('NodeSocketFloatFactor', "Custom mask Alpha")
    node_group.inputs[1].default_value = 0.0
    node_group.inputs[1].min_value = 0.0
    node_group.inputs[1].max_value = 1.0

    # input Cam occlu
    node_group.inputs.new('NodeSocketFloat', "Cam occlu")
    node_group.inputs[2].default_value = 0.5

    # input Cam occlu mirrored
    node_group.inputs.new('NodeSocketFloat', "Cam occlu mirrored")
    node_group.inputs[3].default_value = 0.0

    # input Facing
    node_group.inputs.new('NodeSocketFloat', "Facing")
    node_group.inputs[4].default_value = 0.5

    # input Facing Mirrored
    node_group.inputs.new('NodeSocketFloat', "Facing Mirrored")
    node_group.inputs[5].default_value = 0.0

    # input Facing intensity
    node_group.inputs.new('NodeSocketFloat', "Facing intensity")
    node_group.inputs[6].default_value = 0.0
    node_group.inputs[6].min_value = 0.0
    node_group.inputs[6].max_value = 2.0

    # input Facing Position
    node_group.inputs.new('NodeSocketFloat', "Facing Position")
    node_group.inputs[7].default_value = 0.2

    # input Facing Size
    node_group.inputs.new('NodeSocketFloat', "Facing Size")
    node_group.inputs[8].default_value = 0.2

    # input Custom mask intensity
    node_group.inputs.new('NodeSocketFloat', "Custom mask intensity")
    node_group.inputs[9].default_value = 1.0
    node_group.inputs[9].min_value = 0.0
    node_group.inputs[9].max_value = 1.0

    # input Mirror on/off
    node_group.inputs.new('NodeSocketFloat', "Mirror on/off")
    node_group.inputs[10].default_value = 0.0
    node_group.inputs[10].min_value = 0.0
    node_group.inputs[10].max_value = 1.0

    # reroute
    reroute_1 = node_group.nodes.new("NodeReroute")
    reroute_2 = node_group.nodes.new("NodeReroute")

    # node Group Input
    group_input_1 = node_group.nodes.new("NodeGroupInput")
    group_input_1.outputs[0].hide = True
    group_input_1.outputs[1].hide = True
    group_input_1.outputs[3].hide = True
    group_input_1.outputs[4].hide = True
    group_input_1.outputs[5].hide = True
    group_input_1.outputs[6].hide = True
    group_input_1.outputs[7].hide = True
    group_input_1.outputs[8].hide = True
    group_input_1.outputs[9].hide = True
    group_input_1.outputs[10].hide = True
    group_input_1.outputs[11].hide = True

    # node Math.001
    math_2 = node_group.nodes.new("ShaderNodeMath")
    math_2.operation = 'MULTIPLY'
    math_2.use_clamp = True

    # node math_2
    math_1 = node_group.nodes.new("ShaderNodeMath")
    math_1.operation = 'MULTIPLY'
    math_1.use_clamp = True

    # node Math.005
    math_3 = node_group.nodes.new("ShaderNodeMath")
    math_3.operation = 'MULTIPLY'
    math_3.use_clamp = True

    # node Group gradiant_tweaker
    gradiant_tweaker_2 = node_group.nodes.new("ShaderNodeGroup")
    gradiant_tweaker_2.node_tree = gradiant_tweaker_node_group

    # node Reroute
    reroute_003 = node_group.nodes.new("NodeReroute")
    reroute_002 = node_group.nodes.new("NodeReroute")

    # node Group Input.004
    group_input_004 = node_group.nodes.new("NodeGroupInput")
    group_input_004.outputs[0].hide = True
    group_input_004.outputs[1].hide = True
    group_input_004.outputs[2].hide = True
    group_input_004.outputs[4].hide = True
    group_input_004.outputs[5].hide = True
    group_input_004.outputs[6].hide = True
    group_input_004.outputs[7].hide = True
    group_input_004.outputs[8].hide = True
    group_input_004.outputs[9].hide = True
    group_input_004.outputs[10].hide = True
    group_input_004.outputs[11].hide = True

    # node Math.004
    math_004 = node_group.nodes.new("ShaderNodeMath")
    math_004.operation = 'MULTIPLY'
    math_004.use_clamp = True

    # node Group Input.005
    group_input_005 = node_group.nodes.new("NodeGroupInput")
    group_input_005.outputs[0].hide = True
    group_input_005.outputs[1].hide = True
    group_input_005.outputs[2].hide = True
    group_input_005.outputs[3].hide = True
    group_input_005.outputs[4].hide = True
    group_input_005.outputs[9].hide = True
    group_input_005.outputs[10].hide = True
    group_input_005.outputs[11].hide = True

    # node Mix
    mix_1 = node_group.nodes.new("ShaderNodeMixRGB")

    # node Mix.001
    mix_001 = node_group.nodes.new("ShaderNodeMixRGB")

    # node Group Input.002
    group_input_002 = node_group.nodes.new("NodeGroupInput")
    group_input_002.outputs[2].hide = True
    group_input_002.outputs[3].hide = True
    group_input_002.outputs[4].hide = True
    group_input_002.outputs[5].hide = True
    group_input_002.outputs[6].hide = True
    group_input_002.outputs[7].hide = True
    group_input_002.outputs[8].hide = True
    group_input_002.outputs[10].hide = True
    group_input_002.outputs[11].hide = True

    # node Math.002
    math_002 = node_group.nodes.new("ShaderNodeMath")
    math_002.operation = 'MULTIPLY'
    math_002.inputs[2].hide = True

    # node Math.003
    math_003 = node_group.nodes.new("ShaderNodeMath")
    math_003.operation = 'ADD'

    # node Group Input.003
    group_input_003 = node_group.nodes.new("NodeGroupInput")
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
    math_006 = node_group.nodes.new("ShaderNodeMath")
    math_006.operation = 'MULTIPLY'
    math_006.use_clamp = True
    # Value_002
    math_006.inputs[2].default_value = 0.5

    # node Group Input.001
    group_input_2 = node_group.nodes.new("NodeGroupInput")
    group_input_2.outputs[0].hide = True
    group_input_2.outputs[1].hide = True
    group_input_2.outputs[2].hide = True
    group_input_2.outputs[3].hide = True
    group_input_2.outputs[5].hide = True
    group_input_2.outputs[9].hide = True
    group_input_2.outputs[10].hide = True
    group_input_2.outputs[11].hide = True

    # node Gradiant_tweaker
    gradiant_tweaker_1 = node_group.nodes.new("ShaderNodeGroup")
    gradiant_tweaker_1.label = "Gradiant_tweaker"
    gradiant_tweaker_1.node_tree = bpy.data.node_groups["Gradiant_tweaker"]

    # node Group Output
    group_output_4 = node_group.nodes.new("NodeGroupOutput")
    node_group.outputs.new('NodeSocketFloat', "Mask")
    node_group.outputs[0].default_value = 0.0

    # Set parents
    reroute_1.parent = frame_1
    reroute_2.parent = frame_1
    group_input_1.parent = frame_1
    group_input_2.parent = frame_1
    math_1.parent = frame_1
    math_2.parent = frame_1
    gradiant_tweaker_1.parent = frame_1

    reroute_003.parent = frame_2
    reroute_002.parent = frame_2
    math_3.parent = frame_2
    gradiant_tweaker_2.parent = frame_2
    group_input_004.parent = frame_2
    math_004.parent = frame_2
    group_input_005.parent = frame_2

    mix_1.parent = frame_3
    mix_001.parent = frame_3
    group_input_002.parent = frame_3
    math_002.parent = frame_3

    group_input_003.parent = frame_4
    math_006.parent = frame_4


    # Set locations
    frame_1.location = (80.0, -20.0)
    frame_2.location = (-160.0, 220.0)
    frame_3.location = (-20.0, 20.0)
    frame_4.location = (-30.0, 10.0)
    reroute_1.location = (-180.0, -160.0)
    reroute_2.location = (-40.0, -160.0)
    math_1.location = (0.0, 20.0)
    group_input_1.location = (0.0, 100.0)
    math_2.location = (240.0, 180.0)
    math_3.location = (278.3137512207031, -667.3348388671875)
    gradiant_tweaker_2.location = (98.31375885009766, -667.3348388671875)
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
    group_output_4.location = (1840.0, 280.0)
    group_input_003.location = (1450.0, -110.0)
    math_006.location = (1450.0, 70.0)
    group_input_2.location = (-400.0, -20.0)
    gradiant_tweaker_1.location = (-180.0, 20.0)

    # Set dimensions
    frame_1.width, frame_1.height = 840.0, 408.0
    frame_2.width, frame_2.height = 800.0, 415.3348388671875
    frame_3.width, frame_3.height = 750.0, 421.0
    frame_4.width, frame_4.height = 200.0, 292.0
    reroute_1.width, reroute_1.height = 16.0, 100.0
    reroute_2.width, reroute_2.height = 16.0, 100.0
    math_1.width, math_1.height = 140.0, 100.0
    group_input_1.width, group_input_1.height = 140.0, 100.0
    math_2.width, math_2.height = 140.0, 100.0
    math_3.width, math_3.height = 140.0, 100.0
    gradiant_tweaker_2.width, gradiant_tweaker_2.height = 140.0, 100.0
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
    group_output_4.width, group_output_4.height = 140.0, 100.0
    group_input_003.width, group_input_003.height = 140.0, 100.0
    math_006.width, math_006.height = 140.0, 100.0
    group_input_2.width, group_input_2.height = 140.0, 100.0
    gradiant_tweaker_1.width, gradiant_tweaker_1.height = 150.2752685546875, 100.0

    # initialize mask_mix links
    # math_2.Value -> math_001_1.Value
    node_group.links.new(math_1.outputs[0], math_2.inputs[1])
    # gradiant_tweaker_1.Result -> math_2.Value
    node_group.links.new(gradiant_tweaker_1.outputs[0], math_1.inputs[0])
    # group_input_001_1.Facing -> gradiant_tweaker_1.Gradiant
    node_group.links.new(group_input_2.outputs[4], gradiant_tweaker_1.inputs[0])
    # group_input_001_1.Facing Size -> gradiant_tweaker_1.Size
    node_group.links.new(group_input_2.outputs[8], gradiant_tweaker_1.inputs[2])
    # group_input_001_1.Facing Position -> gradiant_tweaker_1.Position
    node_group.links.new(group_input_2.outputs[7], gradiant_tweaker_1.inputs[1])
    # group_input_001_1.Facing intensity -> reroute.Input
    node_group.links.new(group_input_2.outputs[6], reroute_1.inputs[0])
    # reroute.Output -> reroute_001.Input
    node_group.links.new(reroute_1.outputs[0], reroute_2.inputs[0])
    # math_001_1.Value -> mix_1.Color1
    node_group.links.new(math_2.outputs[0], mix_1.inputs[1])
    # math_003.Value -> group_output_4.Mask
    node_group.links.new(math_003.outputs[0], group_output_4.inputs[0])
    # group_input_3.Cam occlu -> math_001_1.Value
    node_group.links.new(group_input_1.outputs[2], math_2.inputs[0])
    # math_002.Value -> mix_1.Fac
    node_group.links.new(math_002.outputs[0], mix_1.inputs[0])
    # group_input_002.Custom mask Color -> mix_1.Color2
    node_group.links.new(group_input_002.outputs[0], mix_1.inputs[2])
    # group_input_002.Custom mask Alpha -> math_002.Value
    node_group.links.new(group_input_002.outputs[1], math_002.inputs[0])
    # group_input_002.Custom mask intensity -> math_002.Value
    node_group.links.new(group_input_002.outputs[9], math_002.inputs[1])
    # reroute_001.Output -> math_2.Value
    node_group.links.new(reroute_2.outputs[0], math_1.inputs[1])
    # math_005.Value -> math_004.Value
    node_group.links.new(math_3.outputs[0], math_004.inputs[1])
    # group_001.Result -> math_005.Value
    node_group.links.new(gradiant_tweaker_2.outputs[0], math_3.inputs[0])
    # group_input_005.Facing Size -> group_001.Size
    node_group.links.new(group_input_005.outputs[8], gradiant_tweaker_2.inputs[2])
    # group_input_005.Facing Position -> group_001.Position
    node_group.links.new(group_input_005.outputs[7], gradiant_tweaker_2.inputs[1])
    # group_input_005.Facing intensity -> reroute_002.Input
    node_group.links.new(group_input_005.outputs[6], reroute_002.inputs[0])
    # reroute_002.Output -> reroute_003.Input
    node_group.links.new(reroute_002.outputs[0], reroute_003.inputs[0])
    # reroute_003.Output -> math_005.Value
    node_group.links.new(reroute_003.outputs[0], math_3.inputs[1])
    # group_input_004.Cam occlu mirrored -> math_004.Value
    node_group.links.new(group_input_004.outputs[3], math_004.inputs[0])
    # group_input_005.Facing Mirrored -> group_001.Gradiant
    node_group.links.new(group_input_005.outputs[5], gradiant_tweaker_2.inputs[0])
    # math_004.Value -> mix_001.Color1
    node_group.links.new(math_004.outputs[0], mix_001.inputs[1])
    # math_002.Value -> mix_001.Fac
    node_group.links.new(math_002.outputs[0], mix_001.inputs[0])
    # group_input_002.Custom mask Color -> mix_001.Color2
    node_group.links.new(group_input_002.outputs[0], mix_001.inputs[2])
    # mix_1.Color -> math_003.Value
    node_group.links.new(mix_1.outputs[0], math_003.inputs[0])
    # math_006.Value -> math_003.Value
    node_group.links.new(math_006.outputs[0], math_003.inputs[1])
    # mix_001.Color -> math_006.Value
    node_group.links.new(mix_001.outputs[0], math_006.inputs[0])
    # group_input_003.Mirror on/off -> math_006.Value
    node_group.links.new(group_input_003.outputs[10], math_006.inputs[1])


def create_tweak_uvs_material(sd_gen_node_group) -> bpy.types.Material:
    material = bpy.data.materials.new(name="head_proj_tweaking")
    material.use_nodes = True

    nodes = material.node_tree

    # start with a clean node tree
    for node in nodes.nodes:
        nodes.nodes.remove(node)

    # node Material Output
    material_output = nodes.nodes.new("ShaderNodeOutputMaterial")

    # node sd_gen_node_group
    sd_gen = nodes.nodes.new("ShaderNodeGroup")
    sd_gen.node_tree = sd_gen_node_group

    sd_gen.use_custom_color = True
    sd_gen.color = (0.35, 0.3, 0.6)

    # Set locations
    material_output.location = (300.0, 300.0)
    sd_gen.location = (0.0, 300.0)

    # Set dimensions
    material_output.width, material_output.height = 140.0, 100.0
    sd_gen.width, sd_gen.height = 222.5, 100.0

    # initialize head_proj_tweaking links
    nodes.links.new(sd_gen.outputs[0], material_output.inputs[0])

    return material
