"""
Turns the raw AI-generated model into one small enough for the website.

  in:   blender/space-explorer/space-explorer_raw.glb   (about 65 MB, 1.9 M triangles)
  out:  blender/space-explorer/space-explorer.blend      the editable, reduced scene
        public/models/space-explorer.glb                 what the site loads
        blender/space-explorer/preview.png               a front-view check image

Run from the project root:

  /Applications/Blender.app/Contents/MacOS/Blender -b --python blender/space-explorer/optimize.py

Change TARGET_TRIANGLES or TEXTURE_SIZE below and run again to trade
quality against file size.
"""

import math
import os

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(HERE, "space-explorer_raw.glb")
BLEND = os.path.join(HERE, "space-explorer.blend")
PREVIEW = os.path.join(HERE, "preview.png")
GLB = os.path.join(ROOT, "public", "models", "space-explorer.glb")

TARGET_TRIANGLES = 60_000
TEXTURE_SIZE = 1024


def triangle_count(obj):
    return sum(len(polygon.vertices) - 2 for polygon in obj.data.polygons)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=RAW)

    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    model = bpy.context.view_layer.objects.active
    model.name = "Space explorer"

    before = triangle_count(model)
    decimate = model.modifiers.new("Reduce", "DECIMATE")
    decimate.ratio = min(1.0, TARGET_TRIANGLES / before)
    bpy.ops.object.modifier_apply(modifier=decimate.name)
    bpy.ops.object.shade_smooth()
    after = triangle_count(model)
    print(f"Triangles: {before} -> {after}")

    for image in bpy.data.images:
        if image.size[0] > TEXTURE_SIZE or image.size[1] > TEXTURE_SIZE:
            image.scale(TEXTURE_SIZE, TEXTURE_SIZE)
            image.pack()

    # Camera and light, so the .blend opens ready to look at and the preview renders.
    box = [model.matrix_world @ v.co for v in model.data.vertices]
    low = [min(p[i] for p in box) for i in range(3)]
    high = [max(p[i] for p in box) for i in range(3)]
    centre = [(low[i] + high[i]) / 2 for i in range(3)]
    span = max(high[0] - low[0], high[2] - low[2])

    camera_data = bpy.data.cameras.new("Camera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = span * 1.2
    camera = bpy.data.objects.new("Camera", camera_data)
    camera.location = (centre[0], low[1] - 5.0, centre[2])
    camera.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera

    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(55), 0, math.radians(-30))
    bpy.context.collection.objects.link(sun)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND)

    os.makedirs(os.path.dirname(GLB), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    model.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=GLB,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_image_format="WEBP",
        export_image_quality=80,
        export_draco_mesh_compression_enable=True,
    )
    print(f"Exported {GLB} ({os.path.getsize(GLB) / 1024:.0f} kB)")

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "TEXTURE"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)


main()
