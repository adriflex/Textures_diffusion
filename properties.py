'''
Copyright (C) 2023 Blender Foundation and Adrien Rouquié
https://blender.org
https://www.linkedin.com/in/adrien-rouquie/

orangeturbine@cgcookie.com

Created by the Blender Foundation, modified by Adrien Rouquié.

This file is part of a Texture Diffusion add-on.

    Texture Diffusion is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <https://www.gnu.org/licenses>.

'''

import bpy


class TexDiff_prop_group(bpy.types.PropertyGroup):
    img_generated_path: bpy.props.StringProperty(
        name="IMG Generated Path",
        description="Path to the Stable Diffusion image",
        default="//",
        subtype="FILE_PATH",
    )

    enable_beauty_ref: bpy.props.BoolProperty(
        name="Enable Beauty Ref",
        description="Render the beauty reference image",
        default=False,
    )

    enable_normal_ref: bpy.props.BoolProperty(
        name="Enable Normal Ref",
        description="Render the normal reference image",
        default=True,
    )

    enable_depth_ref: bpy.props.BoolProperty(
        name="Enable Depth Ref",
        description="Render the depth reference image",
        default=False,
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

