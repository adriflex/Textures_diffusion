import bpy


class TexDiff_prop_group(bpy.types.PropertyGroup):
    img_generated_path: bpy.props.StringProperty(
        name="IMG Generated Path",
        description="Path to the Stable Diffusion image",
        default="//",
        subtype="FILE_PATH",
    )

    masks_resolution: bpy.props.IntProperty(
        name="Masks Resolution",
        description="Resolution of the projection masks",
        default=512,
        min=1,
        max=4096,
    )

    masks_samples: bpy.props.IntProperty(
        name="Masks Sampling",
        description="Sampling of the projection masks",
        default=512,
    )

    use_mirror_X: bpy.props.BoolProperty(
        name="Mirror X",
        description="Use symmetry on the X axis",
        default=False,
    )

    bake_resolution: bpy.props.IntProperty(
        name="Bake Resolution",
        description="Resolution of the baked projection",
        default=1024,
        min=1,
        soft_max=4096,
    )

