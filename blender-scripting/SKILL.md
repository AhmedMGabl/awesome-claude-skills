---
name: blender-scripting
description: Blender Python scripting patterns covering bpy API, mesh operations, modifiers, materials, animation keyframes, add-on development, and batch processing.
---

# Blender Python Scripting

This skill should be used when automating Blender workflows with Python scripting. It covers bpy API, mesh operations, modifiers, materials, animation, add-on development, and batch processing.

## When to Use This Skill

Use this skill when you need to:

- Automate Blender 3D workflows with Python
- Create and manipulate meshes programmatically
- Set up materials, lighting, and render settings
- Animate objects with keyframes
- Build Blender add-ons for custom tools

## Basic Operations

```python
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
import math

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create objects
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "MyCube"

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(3, 0, 0.5))
sphere = bpy.context.active_object

bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
```

## Mesh Operations with bmesh

```python
# Create custom mesh
mesh = bpy.data.meshes.new("custom_mesh")
obj = bpy.data.objects.new("CustomObject", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

# Create vertices
v1 = bm.verts.new((0, 0, 0))
v2 = bm.verts.new((1, 0, 0))
v3 = bm.verts.new((1, 1, 0))
v4 = bm.verts.new((0, 1, 0))
v5 = bm.verts.new((0.5, 0.5, 1))

bm.verts.ensure_lookup_table()

# Create faces
bm.faces.new([v1, v2, v3, v4])  # base
bm.faces.new([v1, v2, v5])       # side
bm.faces.new([v2, v3, v5])
bm.faces.new([v3, v4, v5])
bm.faces.new([v4, v1, v5])

bm.to_mesh(mesh)
bm.free()
mesh.update()
```

## Materials

```python
# Create PBR material
mat = bpy.data.materials.new("PBR_Material")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Principled BSDF
bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (0, 0)
bsdf.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1)
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 0.4

# Output
output = nodes.new("ShaderNodeOutputMaterial")
output.location = (300, 0)
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

# Add texture
tex_node = nodes.new("ShaderNodeTexImage")
tex_node.location = (-300, 0)
tex_node.image = bpy.data.images.load("/path/to/texture.png")
links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])

# Assign to object
cube.data.materials.append(mat)
```

## Animation

```python
# Keyframe animation
obj = bpy.data.objects["MyCube"]
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 120

# Position keyframes
obj.location = (0, 0, 1)
obj.keyframe_insert(data_path="location", frame=1)

obj.location = (5, 0, 1)
obj.keyframe_insert(data_path="location", frame=30)

obj.location = (5, 5, 3)
obj.keyframe_insert(data_path="location", frame=60)

obj.location = (0, 0, 1)
obj.keyframe_insert(data_path="location", frame=120)

# Rotation keyframes
obj.rotation_euler = Euler((0, 0, 0))
obj.keyframe_insert(data_path="rotation_euler", frame=1)

obj.rotation_euler = Euler((0, 0, math.radians(360)))
obj.keyframe_insert(data_path="rotation_euler", frame=120)

# Set interpolation to smooth
for fcurve in obj.animation_data.action.fcurves:
    for keyframe in fcurve.keyframe_points:
        keyframe.interpolation = 'BEZIER'
```

## Add-on Template

```python
bl_info = {
    "name": "My Custom Tool",
    "author": "Developer",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > My Tool",
    "description": "Custom modeling tool",
    "category": "Object",
}

import bpy
from bpy.props import FloatProperty, IntProperty, BoolProperty

class MY_OT_custom_operator(bpy.types.Operator):
    bl_idname = "object.my_custom_operator"
    bl_label = "Custom Operation"
    bl_options = {'REGISTER', 'UNDO'}

    scale: FloatProperty(name="Scale", default=1.0, min=0.1, max=10.0)
    count: IntProperty(name="Count", default=5, min=1, max=100)

    def execute(self, context):
        for i in range(self.count):
            bpy.ops.mesh.primitive_cube_add(size=self.scale, location=(i * 2, 0, 0))
        return {'FINISHED'}

class MY_PT_panel(bpy.types.Panel):
    bl_label = "My Tool"
    bl_idname = "MY_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "My Tool"

    def draw(self, context):
        layout = self.layout
        layout.operator("object.my_custom_operator")

def register():
    bpy.utils.register_class(MY_OT_custom_operator)
    bpy.utils.register_class(MY_PT_panel)

def unregister():
    bpy.utils.unregister_class(MY_PT_panel)
    bpy.utils.unregister_class(MY_OT_custom_operator)

if __name__ == "__main__":
    register()
```

## Additional Resources

- Blender Python API: https://docs.blender.org/api/current/
- Scripting Guide: https://docs.blender.org/manual/en/latest/advanced/scripting/
- Templates: Blender > Text Editor > Templates > Python
