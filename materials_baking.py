import bpy


def create_normal_material() -> bpy.types.Material:
    mat = bpy.data.materials.new(name="Normal")
    mat.use_nodes = True

    def material_node_group():
        material = mat.node_tree

        # start with a clean node tree
        for node in material.nodes:
            material.nodes.remove(node)
        # initialize camera_normal nodes
        # node Combine XYZ
        combine_xyz = material.nodes.new("ShaderNodeCombineXYZ")
        # X
        combine_xyz.inputs[0].default_value = 0.5
        # Y
        combine_xyz.inputs[1].default_value = 0.5
        # Z
        combine_xyz.inputs[2].default_value = -0.5

        # node Combine XYZ.001
        combine_xyz_001 = material.nodes.new("ShaderNodeCombineXYZ")
        # X
        combine_xyz_001.inputs[0].default_value = 0.5
        # Y
        combine_xyz_001.inputs[1].default_value = 0.5
        # Z
        combine_xyz_001.inputs[2].default_value = 0.5

        # node Mix
        mix = material.nodes.new("ShaderNodeMixRGB")
        # Fac
        mix.inputs[0].default_value = 1.0
        mix.blend_type = 'MULTIPLY'

        # node Vector Transform
        vector_transform = material.nodes.new("ShaderNodeVectorTransform")
        vector_transform.vector_type = 'NORMAL'
        vector_transform.convert_from = 'WORLD'
        vector_transform.convert_to = 'CAMERA'

        # node Mix.001
        mix_001 = material.nodes.new("ShaderNodeMixRGB")
        # Fac
        mix_001.inputs[0].default_value = 1.0
        mix_001.blend_type = 'ADD'

        # node Material Output
        material_output = material.nodes.new("ShaderNodeOutputMaterial")

        # node Geometry
        geometry = material.nodes.new("ShaderNodeNewGeometry")

        # Set locations
        combine_xyz.location = (-691.3909912109375, 1.5789947509765625)
        combine_xyz_001.location = (-504.3045959472656, -48.92665100097656)
        mix.location = (-504.3045959472656, 132.21095275878906)
        vector_transform.location = (-691.3909912109375, 167.3542022705078)
        mix_001.location = (-288.9167175292969, 102.45826721191406)
        material_output.location = (-44.356895446777344, 113.10558319091797)
        geometry.location = (-910.069091796875, 62.20948791503906)

        # initialize camera_normal links

        # geometry.Normal -> vector_transform.Vector
        material.links.new(geometry.outputs[1], vector_transform.inputs[0])
        # combine_xyz.Vector -> mix.Color2
        material.links.new(combine_xyz.outputs[0], mix.inputs[2])
        # combine_xyz_001.Vector -> mix_001.Color2
        material.links.new(combine_xyz_001.outputs[0], mix_001.inputs[2])
        # vector_transform.Vector -> mix.Color1
        material.links.new(vector_transform.outputs[0], mix.inputs[1])
        # mix.Color -> mix_001.Color1
        material.links.new(mix.outputs[0], mix_001.inputs[1])
        # mix_001.Color -> material_output.Surface
        material.links.new(mix_001.outputs[0], material_output.inputs[0])

    material_node_group()
    return mat


def create_depth_material(min_depth: float, max_depth: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name="Depth")
    mat.use_nodes = True

    def material_node_group():
        material = mat.node_tree

        # start with a clean node tree
        for node in material.nodes:
            material.nodes.remove(node)

        # initialize depth nodes
        # node Material Output
        material_output = material.nodes.new("ShaderNodeOutputMaterial")
        material_output.target = 'ALL'

        # node Map Range
        map_range = material.nodes.new("ShaderNodeMapRange")
        # From Min
        map_range.inputs[1].default_value = min_depth
        # From Max
        map_range.inputs[2].default_value = max_depth
        # To Min
        map_range.inputs[3].default_value = 1.0
        # To Max
        map_range.inputs[4].default_value = 0.0

        # node Camera Data
        camera_data = material.nodes.new("ShaderNodeCameraData")

        # Set locations
        material_output.location = (3.111602783203125, 309.34918212890625)
        map_range.location = (-315.3854675292969, 285.913818359375)
        camera_data.location = (-534.7982788085938, 181.81155395507812)

        # initialize depth links

        # map_range.Result -> material_output.Surface
        material.links.new(map_range.outputs[0], material_output.inputs[0])
        # camera_data.View Z Depth -> map_range.Value
        material.links.new(camera_data.outputs[1], map_range.inputs[0])

    material_node_group()
    return mat


def create_facing_material() -> bpy.types.Material:
    mat = bpy.data.materials.new(name="Facing")
    mat.use_nodes = True

    def material_node_group():
        material = mat.node_tree
        # start with a clean node tree
        for node in material.nodes:
            material.nodes.remove(node)
        # initialize material nodes
        # node Material Output
        material_output = material.nodes.new("ShaderNodeOutputMaterial")
        material_output.target = 'ALL'

        # node Geometry.001
        geometry = material.nodes.new("ShaderNodeNewGeometry")

        # node Vector Math
        vector_math = material.nodes.new("ShaderNodeVectorMath")
        vector_math.operation = 'DOT_PRODUCT'
        # Vector_001
        vector_math.inputs[1].default_value = (0.0, -1.0, 0.0)

        # Set locations
        material_output.location = (300.0, 300.0)
        geometry.location = (-79.71321105957031, 282.47711181640625)
        vector_math.location = (111.07402038574219, 296.83062744140625)

        # initialize material links
        # geometry.Normal -> vector_math.Vector
        material.links.new(geometry.outputs[1], vector_math.inputs[0])
        # vector_math.Value -> material_output.Surface
        material.links.new(vector_math.outputs[1], material_output.inputs[0])

    material_node_group()
    return mat


def create_diffuse_material() -> bpy.types.Material:
    mat = bpy.data.materials.new(name="Diffuse")
    mat.use_nodes = True

    def material_node_group():
        material = mat.node_tree

        # start with a clean node tree
        for node in list(material.nodes):
            material.nodes.remove(node)

        material_output = material.nodes.new("ShaderNodeOutputMaterial")
        material_output.target = 'ALL'

        diffuse_bsdf = material.nodes.new("ShaderNodeBsdfDiffuse")

        # Set locations
        material_output.location = (300.0, 300.0)
        diffuse_bsdf.location = (-30, 300)
        material.links.new(diffuse_bsdf.outputs[0], material_output.inputs[0])

    material_node_group()
    return mat
