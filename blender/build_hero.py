"""
Builds the base 3D scene for the portfolio's main page: a person resting in a
crescent moon. It writes two files:

  blender/hero.blend       the editable Blender scene (sculpt and detail here)
  public/models/hero.glb   the export the website loads

Run from the project root:

  /Applications/Blender.app/Contents/MacOS/Blender -b --python blender/build_hero.py

WARNING: running this again overwrites blender/hero.blend. Once you start
detailing the model by hand, save your work under another name.

Layout: X is left/right, Z is up, and the scene faces the camera along -Y
(Blender's Front view, numpad 1).
"""

import math
import os

import bmesh
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND_PATH = os.path.join(ROOT, "blender", "hero.blend")
GLB_PATH = os.path.join(ROOT, "public", "models", "hero.glb")

PALETTE = {
    "moon": "e9f0c9",
    "crater": "c8d3bd",
    "hoodie": "5b8aa3",
    "trousers": "3b657a",
    "skin": "d9b99a",
    "hair": "20130a",
    "shoe": "e9f0c9",
    "star": "e9c46a",
    "thought": "9cc3d8",
    "planet": "3b657a",
    "ring": "9cc3d8",
}


def srgb_to_linear(channel):
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def material(name, roughness=0.85):
    hex_color = PALETTE[name]
    rgb = [srgb_to_linear(int(hex_color[i : i + 2], 16) / 255) for i in (0, 2, 4)]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    return mat


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def smooth(obj, angle=None):
    """Smooth shading; with an angle, edges sharper than it stay crisp."""
    activate(obj)
    if angle is None:
        bpy.ops.object.shade_smooth()
    else:
        try:
            bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
        except Exception:
            bpy.ops.object.shade_smooth()


def add_object(name, mesh, mat, parent=None):
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    if parent is not None:
        obj.parent = parent
    return obj


def sphere(name, location, radius, mat, scale=(1, 1, 1), parent=None, segments=32):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=segments // 2, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    obj = add_object(name, mesh, mat, parent)
    obj.location = location
    obj.scale = scale
    smooth(obj)
    return obj


def arc(cx, cz, radius, start_deg, end_deg, steps):
    return [
        (
            cx + radius * math.cos(math.radians(start_deg + (end_deg - start_deg) * i / steps)),
            cz + radius * math.sin(math.radians(start_deg + (end_deg - start_deg) * i / steps)),
        )
        for i in range(steps + 1)
    ]


def build_moon(mats, parent):
    """Crescent: an outer circle with an offset circle cut out of it."""
    # Both edges run tip to tip with the same number of points, and the face
    # is filled as a strip of quads between them (a single concave polygon
    # would be filled straight across the hollow).
    steps = 96
    outer_points = arc(0, 0, 1.6, 74.1, -164.1, steps)
    inner_points = arc(-0.5, 0.5, 1.4, 47.9, -137.9, steps)
    mesh = bpy.data.meshes.new("Moon")
    bm = bmesh.new()
    outer = [bm.verts.new((x, 0.0, z)) for x, z in outer_points]
    inner = [outer[0]] + [bm.verts.new((x, 0.0, z)) for x, z in inner_points[1:-1]] + [outer[-1]]
    for i in range(steps):
        corners = []
        for vert in (outer[i], outer[i + 1], inner[i + 1], inner[i]):
            if vert not in corners:
                corners.append(vert)
        bm.faces.new(corners)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()

    moon = add_object("Moon", mesh, mats["moon"], parent)
    solidify = moon.modifiers.new("Thickness", "SOLIDIFY")
    solidify.thickness = 0.56
    solidify.offset = 0.0
    bevel = moon.modifiers.new("Soft edges", "BEVEL")
    bevel.width = 0.09
    bevel.segments = 5
    bevel.limit_method = "ANGLE"
    smooth(moon, angle=40)

    # Craters: shallow discs pressed into the front face.
    for index, (x, z, radius) in enumerate([(1.0, -0.9, 0.11), (1.3, -0.2, 0.07), (0.5, -1.35, 0.08), (1.18, -0.55, 0.045)]):
        sphere(f"Crater {index + 1}", (x, -0.275, z), radius, mats["crater"], scale=(1, 0.14, 1), parent=moon)
    return moon


def skin_body(name, joints, edges, mat, parent, root_index=0):
    """
    A smooth body part grown around a stick skeleton (Skin + Subdivision
    modifiers). joints is a list of ((x, y, z), radius).
    """
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([position for position, _ in joints], edges, [])
    mesh.update()
    obj = add_object(name, mesh, mat, parent)

    activate(obj)
    bpy.ops.object.modifier_add(type="SKIN")
    if len(mesh.skin_vertices) == 0:
        bpy.ops.mesh.customdata_skin_add()
    skin_layer = mesh.skin_vertices[0].data
    for index, (_, radius) in enumerate(joints):
        skin_layer[index].radius = (radius, radius)
        skin_layer[index].use_root = index == root_index

    subdivision = obj.modifiers.new("Smooth", "SUBSURF")
    subdivision.levels = 2
    subdivision.render_levels = 3
    smooth(obj)
    return obj


def build_figure(mats, parent):
    """The person, lying back in the curve of the moon with one knee up."""
    figure = bpy.data.objects.new("Figure", None)
    bpy.context.collection.objects.link(figure)
    figure.parent = parent

    # Torso and arms. Y < 0 is the side nearer the camera.
    upper = [
        ((0.05, 0.0, -0.73), 0.15),   # 0 pelvis
        ((0.25, 0.0, -0.49), 0.15),   # 1 waist
        ((0.44, 0.0, -0.27), 0.17),   # 2 chest
        ((0.53, 0.0, -0.13), 0.07),   # 3 neck
        ((0.47, 0.17, -0.2), 0.085),  # 4 far shoulder
        ((0.84, 0.2, 0.05), 0.06),    # 5 far elbow (arm folded behind the head)
        ((0.7, 0.1, 0.14), 0.05),     # 6 far wrist
        ((0.45, -0.17, -0.22), 0.085),  # 7 near shoulder
        ((0.36, -0.27, -0.5), 0.06),  # 8 near elbow (hand resting on the stomach)
        ((0.16, -0.16, -0.42), 0.05),  # 9 near wrist
    ]
    upper_edges = [(0, 1), (1, 2), (2, 3), (2, 4), (4, 5), (5, 6), (2, 7), (7, 8), (8, 9)]
    skin_body("Torso and arms", upper, upper_edges, mats["hoodie"], figure)

    legs = [
        ((0.05, 0.0, -0.73), 0.15),    # 0 pelvis
        ((0.0, -0.1, -0.7), 0.12),     # 1 near hip
        ((-0.34, -0.1, -0.24), 0.085),  # 2 near knee (raised)
        ((-0.55, -0.1, -0.84), 0.06),  # 3 near ankle
        ((0.0, 0.1, -0.72), 0.12),     # 4 far hip
        ((-0.34, 0.1, -0.6), 0.085),   # 5 far knee
        ((-0.82, 0.1, -0.8), 0.06),    # 6 far ankle
    ]
    leg_edges = [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6)]
    skin_body("Legs", legs, leg_edges, mats["trousers"], figure)

    sphere("Head", (0.62, 0.0, 0.03), 0.165, mats["skin"], scale=(0.95, 0.92, 1.05), parent=figure)
    sphere("Hair", (0.655, 0.01, 0.065), 0.165, mats["hair"], scale=(0.98, 0.98, 0.98), parent=figure)
    sphere("Far hand", (0.67, 0.08, 0.16), 0.055, mats["skin"], parent=figure)
    sphere("Near hand", (0.12, -0.15, -0.41), 0.055, mats["skin"], parent=figure)
    sphere("Near shoe", (-0.6, -0.1, -0.9), 0.075, mats["shoe"], scale=(1.5, 0.85, 0.75), parent=figure)
    sphere("Far shoe", (-0.88, 0.1, -0.76), 0.075, mats["shoe"], scale=(0.8, 0.85, 1.45), parent=figure)
    return figure


def build_props(mats, parent):
    # The thought: two dots rising to a star.
    sphere("Thought 1", (0.36, 0.0, 0.34), 0.035, mats["thought"], parent=parent, segments=16)
    sphere("Thought 2", (0.22, 0.0, 0.52), 0.05, mats["thought"], parent=parent, segments=16)

    star_mesh = bpy.data.meshes.new("Star")
    bm = bmesh.new()
    points = 4
    outer, inner, depth = 0.24, 0.09, 0.07
    ring = []
    for i in range(points * 2):
        radius = outer if i % 2 == 0 else inner
        angle = math.pi / 2 + i * math.pi / points
        ring.append(bm.verts.new((radius * math.cos(angle), 0.0, radius * math.sin(angle))))
    front = bm.verts.new((0.0, -depth, 0.0))
    back = bm.verts.new((0.0, depth, 0.0))
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        bm.faces.new((a, b, front))
        bm.faces.new((b, a, back))
    bm.normal_update()
    bm.to_mesh(star_mesh)
    bm.free()
    star = add_object("Star", star_mesh, mats["star"], parent)
    star.location = (-0.04, 0.0, 0.84)

    planet = sphere("Planet", (-1.36, 0.6, 1.26), 0.2, mats["planet"], parent=parent)
    ring_mesh = bpy.data.meshes.new("Planet ring")
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, radius=0.34, segments=64)
    bm.to_mesh(ring_mesh)
    bm.free()
    ring_obj = add_object("Planet ring", ring_mesh, mats["ring"], planet)
    ring_obj.rotation_euler = (math.radians(18), math.radians(18), 0)
    activate(ring_obj)
    bpy.ops.object.modifier_add(type="SKIN")
    if len(ring_mesh.skin_vertices) == 0:
        bpy.ops.mesh.customdata_skin_add()
    for vertex in ring_mesh.skin_vertices[0].data:
        vertex.radius = (0.012, 0.012)
    smooth(ring_obj)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mats = {name: material(name) for name in PALETTE}

    root = bpy.data.objects.new("Hero", None)
    bpy.context.collection.objects.link(root)

    build_moon(mats, root)
    build_figure(mats, root)
    build_props(mats, root)

    # A camera and light so the .blend opens ready to look at and render.
    camera_data = bpy.data.cameras.new("Camera")
    camera_data.lens = 85
    camera = bpy.data.objects.new("Camera", camera_data)
    camera.location = (0.0, -9.0, 0.0)
    camera.rotation_euler = (math.radians(90), 0, 0)
    bpy.context.collection.objects.link(camera)
    bpy.context.scene.camera = camera

    sun_data = bpy.data.lights.new("Sun", "SUN")
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("Sun", sun_data)
    sun.rotation_euler = (math.radians(55), 0, math.radians(-30))
    bpy.context.collection.objects.link(sun)

    os.makedirs(os.path.dirname(BLEND_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(GLB_PATH), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)

    # Export only the model, not the camera or light.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in bpy.data.objects:
        if obj.type in {"MESH", "EMPTY"}:
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=GLB_PATH,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
    )
    print(f"Saved {BLEND_PATH}")
    print(f"Exported {GLB_PATH} ({os.path.getsize(GLB_PATH) / 1024:.0f} kB)")


main()
