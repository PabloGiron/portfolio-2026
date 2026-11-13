"""
Builds the 3D scene for the portfolio's main page, following the reference
drawing: an astronaut lying back in a cratered crescent moon, hands behind
the head, with the helmet floating beside them. It writes:

  blender/hero.blend       the editable Blender scene, one object per part
  public/models/hero.glb   the export the website loads, with the parts of
                           each group joined into one mesh

Run from the project root:

  /Applications/Blender.app/Contents/MacOS/Blender -b --python blender/build_hero.py

Set HERO_PREVIEW to a folder to also render check images there.

WARNING: running this again overwrites blender/hero.blend. Once you start
detailing the model by hand, save your work under another name.

Layout: X is left/right, Z is up, and the scene faces the camera along -Y
(Blender's Front view, numpad 1). Most positions are given as pixel
coordinates measured on the 1254 px reference drawing, see px().
"""

import math
import os
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND_PATH = os.path.join(ROOT, "blender", "hero.blend")
GLB_PATH = os.path.join(ROOT, "public", "models", "hero.glb")
PREVIEW_DIR = os.environ.get("HERO_PREVIEW")

# name: (colour, roughness)
PALETTE = {
    "moon": ("f3eebc", 0.9),
    "crater": ("7f9fb2", 0.9),
    "suit": ("ece2b4", 0.8),
    "suit_blue": ("3d6c8a", 0.8),
    "navy": ("1e3d53", 0.8),
    "sole": ("14283a", 0.9),
    "skin": ("eab594", 0.7),
    "lip": ("c98672", 0.7),
    "hair": ("3a2a22", 0.9),
    "hair_fade": ("54423a", 0.9),
    "eye_white": ("f4efe2", 0.5),
    "eye": ("1a1410", 0.4),
    "glasses": ("27333b", 0.4),
    "visor": ("12283a", 0.12),
    "star": ("f5f0c4", 0.6),
    "orbit": ("c9d6c0", 0.8),
    "outline": ("0b1620", 1.0),
}

# The dark line drawn around each group, as a fraction of the scene's units.
OUTLINE = {"Moon": 0.011, "Astronaut": 0.007, "Helmet": 0.007}

X = Vector((1.0, 0.0, 0.0))
Y = Vector((0.0, 1.0, 0.0))
Z = Vector((0.0, 0.0, 1.0))
TOWARDS_CAMERA = -Y

# --- Moon outline: an outer circle with an offset circle cut out of it. ---
OUTER_RADIUS = 1.6
TIP_TOP_DEG = 82.0      # where the upper tip sits on the outer circle
TIP_LEFT_DEG = 189.0    # where the lower-left tip sits
MOON_WIDTH = 0.87       # widest part of the crescent, across its face
MOON_DEPTH = 0.6        # thickest part, front to back
MOON_ROUNDNESS = 3.5    # 2 = oval cross-section, higher = boxier

_half_gap = math.radians((TIP_LEFT_DEG - TIP_TOP_DEG) / 2)
_opening = math.radians((TIP_LEFT_DEG + TIP_TOP_DEG) / 2)
_inner_reach = OUTER_RADIUS - MOON_WIDTH
_hollow_offset = (OUTER_RADIUS**2 - _inner_reach**2) / (
    2 * (_inner_reach + OUTER_RADIUS * math.cos(_half_gap))
)
HOLLOW_RADIUS = _hollow_offset + _inner_reach
HOLLOW_CENTRE = (_hollow_offset * math.cos(_opening), _hollow_offset * math.sin(_opening))


def _hollow_angle(tip_deg):
    x = OUTER_RADIUS * math.cos(math.radians(tip_deg)) - HOLLOW_CENTRE[0]
    z = OUTER_RADIUS * math.sin(math.radians(tip_deg)) - HOLLOW_CENTRE[1]
    return math.degrees(math.atan2(z, x))


# Both edges are walked clockwise from the upper tip to the lower-left tip.
OUTER_SWEEP = (TIP_TOP_DEG, TIP_LEFT_DEG - 360.0)
_inner_start = _hollow_angle(TIP_TOP_DEG)
INNER_SWEEP = (_inner_start, _inner_start + (_hollow_angle(TIP_LEFT_DEG) - _inner_start) % 360.0 - 360.0)


def px(x, y, depth=0.0):
    """A point of the reference drawing (in its pixels) placed in the scene."""
    return Vector(((x - 620) / 369, depth, (650 - y) / 369))


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def srgb_to_linear(channel):
    return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4


def material(name):
    hex_color, roughness = PALETTE[name]
    rgb = [srgb_to_linear(int(hex_color[i : i + 2], 16) / 255) for i in (0, 2, 4)]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    mat.diffuse_color = (*rgb, 1.0)  # the colour shown in Blender's Solid view
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


def group(name, parent):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    return obj


def plain(obj):
    """Leave this part out of the dark outline (for fine details)."""
    obj["plain"] = True
    return obj


def perpendicular(direction, hint):
    """The part of hint that is at right angles to direction, normalised."""
    direction = Vector(direction).normalized()
    result = Vector(hint) - direction * Vector(hint).dot(direction)
    if result.length < 1e-6:
        result = direction.orthogonal()
    return result.normalized()


def point_along(obj, location, direction):
    """Place obj so its local Z axis points along direction."""
    obj.location = location
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = Vector(direction).normalized().to_track_quat("Z", "Y")


def frame(origin, x_axis, z_axis, size):
    """A transform with local X and Z along the given axes, scaled by size."""
    x = Vector(x_axis).normalized()
    z = perpendicular(x, z_axis)
    y = z.cross(x).normalized()
    rotation = Matrix((x, y, z)).transposed().to_4x4()
    return Matrix.Translation(Vector(origin)) @ rotation @ Matrix.Diagonal((*size, 1.0))


def sphere(name, location, radius, mat, parent, segments=24):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=segments // 2, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    obj = add_object(name, mesh, mat, parent)
    obj.location = location
    smooth(obj)
    return obj


def ellipsoid(name, centre, x_axis, z_axis, radii, mat, parent, segments=24):
    """A stretched ball: radii are its half-sizes along local X, Y and Z."""
    obj = sphere(name, (0, 0, 0), 1.0, mat, parent, segments)
    obj.matrix_basis = frame(centre, x_axis, z_axis, radii)
    return obj


def disc(name, centre, axis, radius, depth, mat, parent):
    """A short cylinder whose flat faces look along axis."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = add_object(name, mesh, mat, parent)
    point_along(obj, centre, axis)
    smooth(obj, angle=50)
    return obj


def box(name, origin, x_axis, z_axis, size, mat, parent, bevel=0.012):
    """A box centred on origin, with its local X and Z along the given axes."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    obj = add_object(name, mesh, mat, parent)
    obj.matrix_basis = frame(origin, x_axis, z_axis, size)
    soften = obj.modifiers.new("Soft edges", "BEVEL")
    soften.width = bevel
    soften.segments = 2
    return obj


def spline(joints, per=8):
    """
    A smooth path through joints, a list of (position, radius). Returns
    samples of [position, radius, t], where t runs 0..1 along the length.
    """
    points = [Vector(p) for p, _ in joints]
    radii = [r for _, r in joints]
    last = len(points) - 1
    samples = []
    for i in range(last):
        p0, p1, p2, p3 = points[max(i - 1, 0)], points[i], points[i + 1], points[min(i + 2, last)]
        for k in range(per):
            u = k / per
            position = 0.5 * (
                2 * p1
                + (p2 - p0) * u
                + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                + (3 * p1 - p0 - 3 * p2 + p3) * u * u * u
            )
            samples.append([position, radii[i] + (radii[i + 1] - radii[i]) * u, 0.0])
    samples.append([points[last], radii[last], 0.0])
    travelled = 0.0
    for i in range(1, len(samples)):
        travelled += (samples[i][0] - samples[i - 1][0]).length
        samples[i][2] = travelled
    for sample in samples:
        sample[2] /= travelled
    return samples


def path_at(samples, t):
    """Position, direction and radius of a path at t."""
    for a, b in zip(samples, samples[1:]):
        if a[2] <= t <= b[2]:
            u = (t - a[2]) / max(b[2] - a[2], 1e-9)
            return a[0].lerp(b[0], u), (b[0] - a[0]).normalized(), a[1] + (b[1] - a[1]) * u
    a, b = samples[-2], samples[-1]
    return b[0].copy(), (b[0] - a[0]).normalized(), b[1]


def cut(samples, t0, t1):
    """The stretch of a path between t0 and t1, with exact end points."""

    def at(t):
        position, _, radius = path_at(samples, t)
        return [position, radius, t]

    middle = [s for s in samples if t0 + 1e-6 < s[2] < t1 - 1e-6]
    return [at(t0)] + middle + [at(t1)]


def tube(name, samples, mat, parent, t0=0.0, t1=1.0, swell=1.0, caps="round", side=None, flatten=1.0, segments=16):
    """
    A tube along a path from spline(). Between t0 and t1 only, it makes a
    band around the limb; swell makes it that much fatter than the path.
    With side, the cross-section is `radius` wide along side and
    `radius * flatten` deep.
    """
    path = cut(samples, t0, t1)
    count = len(path)
    rings = []  # (centre, tangent, radius)
    for i, (position, radius, _) in enumerate(path):
        tangent = (path[min(i + 1, count - 1)][0] - path[max(i - 1, 0)][0]).normalized()
        rings.append((position, tangent, radius * swell))

    poles = [None, None]
    if caps == "round":
        steps = (25, 50, 75)
        position, tangent, radius = rings[0]
        depth = radius * min(flatten, 1.0)
        start = [
            (position - tangent * depth * math.sin(math.radians(a)), tangent, radius * math.cos(math.radians(a)))
            for a in reversed(steps)
        ]
        poles[0] = position - tangent * depth
        position, tangent, radius = rings[-1]
        depth = radius * min(flatten, 1.0)
        end = [
            (position + tangent * depth * math.sin(math.radians(a)), tangent, radius * math.cos(math.radians(a)))
            for a in steps
        ]
        poles[1] = position + tangent * depth
        rings = start + rings + end

    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    loops = []
    across = None
    for position, tangent, radius in rings:
        across = perpendicular(tangent, side if side is not None else (across or tangent.orthogonal()))
        deep = tangent.cross(across)
        loops.append(
            [
                bm.verts.new(
                    position
                    + across * math.cos(2 * math.pi * k / segments) * radius
                    + deep * math.sin(2 * math.pi * k / segments) * radius * flatten
                )
                for k in range(segments)
            ]
        )
    for a, b in zip(loops, loops[1:]):
        for k in range(segments):
            j = (k + 1) % segments
            bm.faces.new((a[k], a[j], b[j], b[k]))
    for pole, loop in ((poles[0], loops[0]), (poles[1], loops[-1])):
        if pole is not None:
            tip = bm.verts.new(pole)
            for k in range(segments):
                bm.faces.new((loop[k], loop[(k + 1) % segments], tip))
        elif caps == "flat":
            bm.faces.new(loop)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    obj = add_object(name, mesh, mat, parent)
    smooth(obj, angle=50)
    return obj


def rod(name, start, end, radius, mat, parent, segments=8):
    """A straight round-ended stick between two points."""
    return tube(name, spline([(start, radius), (end, radius)], per=2), mat, parent, segments=segments)


def circle(centre, normal, radius, count=48):
    normal = Vector(normal).normalized()
    u = normal.orthogonal().normalized()
    v = normal.cross(u)
    return [
        Vector(centre) + (u * math.cos(2 * math.pi * i / count) + v * math.sin(2 * math.pi * i / count)) * radius
        for i in range(count)
    ]


def loop_tube(name, points, plane_normal, minor, mat, parent, flatten=1.0, segments=8):
    """A closed ring of tube through points that all lie in one plane."""
    up = Vector(plane_normal).normalized()
    count = len(points)
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    loops = []
    for i, point in enumerate(points):
        tangent = (points[(i + 1) % count] - points[i - 1]).normalized()
        outward = tangent.cross(up)
        loops.append(
            [
                bm.verts.new(
                    point
                    + outward * math.cos(2 * math.pi * k / segments) * minor
                    + up * math.sin(2 * math.pi * k / segments) * minor * flatten
                )
                for k in range(segments)
            ]
        )
    for i in range(count):
        a, b = loops[i], loops[(i + 1) % count]
        for k in range(segments):
            j = (k + 1) % segments
            bm.faces.new((a[k], a[j], b[j], b[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    obj = add_object(name, mesh, mat, parent)
    smooth(obj)
    return obj


def ring(name, centre, normal, radius, minor, mat, parent, flatten=1.0, count=48):
    return loop_tube(name, circle(centre, normal, radius, count), normal, minor, mat, parent, flatten)


def star(name, location, size, mat, parent, facing=TOWARDS_CAMERA, turn=0.0):
    """A four-pointed sparkle, flat side towards `facing`."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    points = 4
    outline = []
    for i in range(points * 2):
        radius = size if i % 2 == 0 else size * 0.3
        angle = turn + math.pi / 2 + i * math.pi / points
        outline.append(bm.verts.new((radius * math.cos(angle), radius * math.sin(angle), 0.0)))
    front = bm.verts.new((0.0, 0.0, size * 0.22))
    back = bm.verts.new((0.0, 0.0, -size * 0.22))
    for i in range(len(outline)):
        a, b = outline[i], outline[(i + 1) % len(outline)]
        bm.faces.new((a, b, front))
        bm.faces.new((b, a, back))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    obj = add_object(name, mesh, mat, parent)
    point_along(obj, location, facing)
    return obj


# --------------------------------------------------------------------------
# Moon
# --------------------------------------------------------------------------


def power(value, exponent):
    return math.copysign(abs(value) ** exponent, value)


def moon_section(s):
    """
    The slice of the crescent at s (0 = upper tip, 1 = lower-left tip):
    its centre, the vector from the centre to the outer edge, and half its
    depth.
    """
    a = math.radians(OUTER_SWEEP[0] + (OUTER_SWEEP[1] - OUTER_SWEEP[0]) * s)
    b = math.radians(INNER_SWEEP[0] + (INNER_SWEEP[1] - INNER_SWEEP[0]) * s)
    outer = Vector((OUTER_RADIUS * math.cos(a), 0.0, OUTER_RADIUS * math.sin(a)))
    inner = Vector(
        (HOLLOW_CENTRE[0] + HOLLOW_RADIUS * math.cos(b), 0.0, HOLLOW_CENTRE[1] + HOLLOW_RADIUS * math.sin(b))
    )
    half = (outer - inner) / 2
    depth = (MOON_DEPTH / 2) * (half.length / (MOON_WIDTH / 2)) ** 0.6
    return (outer + inner) / 2, half, depth


def moon_face(s, u):
    """A point on the moon's front face; u runs -1 (inner edge) to 1 (outer)."""
    centre, half, depth = moon_section(s)
    bulge = (1 - abs(u) ** MOON_ROUNDNESS) ** (1 / MOON_ROUNDNESS)
    return centre + half * u + TOWARDS_CAMERA * depth * bulge


def moon_face_normal(s, u):
    step = 0.004
    along = moon_face(s + step, u) - moon_face(s - step, u)
    across = moon_face(s, u + step) - moon_face(s, u - step)
    normal = along.cross(across).normalized()
    return normal if normal.dot(TOWARDS_CAMERA) > 0 else -normal


def build_moon(mats, parent):
    moon_group = group("Moon", parent)
    steps, around = 160, 48
    margin = 0.003  # stop just short of the tips, where the slice has no size
    mesh = bpy.data.meshes.new("Moon body")
    bm = bmesh.new()
    loops = []
    for i in range(steps + 1):
        centre, half, depth = moon_section(margin + (1 - 2 * margin) * i / steps)
        loop = []
        for k in range(around):
            angle = 2 * math.pi * k / around
            loop.append(
                bm.verts.new(
                    centre
                    + half * power(math.cos(angle), 2 / MOON_ROUNDNESS)
                    + Y * depth * power(math.sin(angle), 2 / MOON_ROUNDNESS)
                )
            )
        loops.append(loop)
    for a, b in zip(loops, loops[1:]):
        for k in range(around):
            j = (k + 1) % around
            bm.faces.new((a[k], a[j], b[j], b[k]))
    bm.faces.new(loops[0])
    bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    moon = add_object("Moon body", mesh, mats["moon"], moon_group)

    # Craters are scooped out of the front face with balls that only just
    # dip below the surface. The seed is fixed so every run gives the same
    # moon. Each entry: (position, radius, surface normal).
    rng = random.Random(21)
    craters, pits = [], []

    def scatter(found, wanted, sizes, spacing, u_range):
        attempts = 0
        while len(found) < wanted and attempts < 20000:
            attempts += 1
            s = rng.uniform(0.04, 0.965)
            # Lean towards the outer edge, where the drawing has most of them.
            u = u_range[0] + (u_range[1] - u_range[0]) * rng.random() ** 0.8
            radius = rng.choice(sizes)
            _, half, _ = moon_section(s)
            if radius > half.length * (0.9 - abs(u)):
                continue
            position = moon_face(s, u)
            if any((position - other).length < radius + other_radius + spacing for other, other_radius, _ in craters + pits):
                continue
            found.append((position, radius, moon_face_normal(s, u)))

    scatter(craters, 52, [0.035, 0.045, 0.045, 0.055, 0.065, 0.08, 0.095, 0.11, 0.13, 0.155], 0.04, (-0.72, 0.82))
    scatter(pits, 70, [0.012, 0.015, 0.018, 0.022], 0.02, (-0.8, 0.86))

    cutter_mesh = bpy.data.meshes.new("Crater cutter")
    bm = bmesh.new()

    def scoop(position, radius, normal, depth, segments):
        ball = (radius**2 + depth**2) / (2 * depth)
        bmesh.ops.create_uvsphere(
            bm, u_segments=segments, v_segments=segments // 2, radius=ball,
            matrix=Matrix.Translation(position + normal * (ball - depth)),
        )

    rims = []
    for position, radius, normal in craters:
        scoop(position, radius, normal, radius * 0.3, 48)
        lobes = 0
        if radius >= 0.055:
            # Larger craters get side lobes, so they are not perfect circles.
            lobes = rng.choice([1, 2, 2, 3])
            u_dir = normal.orthogonal().normalized()
            v_dir = normal.cross(u_dir)
            start = rng.uniform(0, 2 * math.pi)
            for index in range(lobes):
                angle = start + index * 2 * math.pi / lobes + rng.uniform(-0.4, 0.4)
                offset = (u_dir * math.cos(angle) + v_dir * math.sin(angle)) * radius * 0.62
                lobe_radius = radius * rng.uniform(0.55, 0.72)
                scoop(position + offset, lobe_radius, normal, lobe_radius * 0.3, 40)
        if lobes == 0:
            rims.append((position, radius, normal))
    for position, radius, normal in pits:
        scoop(position, radius, normal, radius * 0.5, 16)
    bm.to_mesh(cutter_mesh)
    bm.free()
    cutter = add_object("Crater cutter", cutter_mesh, mats["crater"])

    # The outline is drawn from the moon as it was before carving: swelling
    # the small pits would turn them inside out.
    silhouette = moon.copy()
    silhouette.data = moon.data.copy()
    silhouette.name = "Moon silhouette"
    silhouette["outline_only"] = True
    bpy.context.collection.objects.link(silhouette)
    plain(moon)

    activate(moon)
    carve = moon.modifiers.new("Craters", "BOOLEAN")
    carve.operation = "DIFFERENCE"
    carve.object = cutter
    carve.solver = "EXACT"
    carve.use_self = True
    carve.material_mode = "TRANSFER"
    bpy.ops.object.modifier_apply(modifier=carve.name)
    bpy.data.objects.remove(cutter)
    smooth(moon, angle=38)

    for index, (position, radius, normal) in enumerate(rims):
        ring(
            f"Crater rim {index + 1}", position, normal, radius * 1.02, radius * 0.07 + 0.003,
            mats["moon"], moon_group, flatten=0.7, count=32,
        )
    return moon_group


# --------------------------------------------------------------------------
# Astronaut
# --------------------------------------------------------------------------


def limb(name, joints, bands, mats, parent):
    """A suit limb with coloured bands: (from t, to t, material name)."""
    samples = spline(joints)
    tube(name, samples, mats["suit"], parent)
    for index, (t0, t1, mat_name) in enumerate(bands):
        tube(f"{name} band {index + 1}", samples, mats[mat_name], parent, t0, t1, swell=1.1, caps="flat")
    return samples


def joint_pad(name, samples, t, out_hint, mats, parent, size=1.0):
    """An armour plate over a knee or elbow, with a bolt at each side."""
    position, along, radius = path_at(samples, t)
    out = perpendicular(along, out_hint)
    across = along.cross(out)
    centre = position + out * radius * 0.55
    ellipsoid(f"{name} pad", centre, along, out, (0.125 * size, 0.118 * size, 0.085 * size), mats["navy"], parent)
    ellipsoid(f"{name} pad plate", centre + out * 0.03 * size, along, out, (0.085 * size, 0.08 * size, 0.07 * size), mats["suit_blue"], parent)
    for index, sign in enumerate((-1, 1)):
        sphere(f"{name} pad bolt {index + 1}", position + across * sign * radius * 1.12, 0.022 * size, mats["suit"], parent, segments=10)


def boot(name, ankle, toe, shin, down_hint, mats, parent):
    foot = (toe - ankle).normalized()
    down = perpendicular(foot, down_hint)
    across = down.cross(foot)
    length = (toe - ankle).length
    middle = ankle.lerp(toe, 0.5)
    upper = spline([(ankle - foot * 0.02, 0.1), (ankle.lerp(toe, 0.55), 0.105), (toe, 0.088)])
    tube(f"{name} boot", upper, mats["suit"], parent)
    for index, (t0, t1) in enumerate(((0.3, 0.4), (0.55, 0.63))):
        tube(f"{name} boot strap {index + 1}", upper, mats["suit_blue"], parent, t0, t1, swell=1.07, caps="flat")
        buckle, _, radius = path_at(upper, (t0 + t1) / 2)
        box(f"{name} boot buckle {index + 1}", buckle - down * radius * 1.07, foot, -down, (0.04, 0.05, 0.02), mats["suit"], parent, bevel=0.005)
    ellipsoid(f"{name} toe cap", toe + foot * 0.012 + down * 0.012, across, down, (0.096, 0.1, 0.085), mats["suit_blue"], parent)
    ring(f"{name} boot cuff", ankle - shin.normalized() * 0.05, shin, 0.098, 0.03, mats["suit_blue"], parent, count=32)
    box(f"{name} sole", middle + foot * 0.015 + down * 0.1, foot, down, (length + 0.23, 0.215, 0.06), mats["sole"], parent, bevel=0.02)
    box(f"{name} welt", middle + foot * 0.015 + down * 0.068, foot, down, (length + 0.215, 0.2, 0.02), mats["suit"], parent, bevel=0.008)
    box(f"{name} heel", ankle - foot * 0.035 + down * 0.14, foot, down, (0.12, 0.2, 0.035), mats["navy"], parent, bevel=0.008)
    # Tread: ridges across the front of the sole.
    for index in range(4):
        along = 0.06 + (length + 0.02) * index / 3
        box(
            f"{name} tread {index + 1}",
            ankle + foot * along + down * 0.138,
            foot, down, (0.035, 0.195, 0.025), mats["navy"], parent, bevel=0.006,
        )


def glove(name, wrist, reach, palm, mats, parent):
    """A gloved hand: fingers point along reach, the palm faces `palm`."""
    reach = Vector(reach).normalized()
    palm = perpendicular(reach, palm)
    across = palm.cross(reach)
    ring(f"{name} glove cuff", wrist - reach * 0.02, reach, 0.07, 0.022, mats["suit"], parent, count=24)
    ellipsoid(f"{name} glove", wrist + reach * 0.05, across, palm, (0.065, 0.07, 0.04), mats["navy"], parent, segments=16)
    for index, offset in enumerate((-0.045, -0.015, 0.015, 0.045)):
        knuckle = wrist + reach * 0.105 + across * offset
        middle = knuckle + reach * 0.045 + palm * 0.012
        tip = middle + reach * 0.03 + palm * 0.03
        tube(f"{name} finger {index + 1}", spline([(knuckle, 0.019), (middle, 0.018), (tip, 0.016)], per=3), mats["navy"], parent, segments=8)
    thumb = wrist + reach * 0.04 + across * 0.06
    rod(f"{name} thumb", thumb, thumb + reach * 0.05 + across * 0.03 + palm * 0.02, 0.02, mats["navy"], parent)


def build_astronaut(mats, parent):
    """Lying back in the curve of the moon: hands behind the head, one knee up."""
    astronaut = group("Astronaut", parent)

    # --- Torso. The chest is turned three-quarters towards the camera. ---
    pelvis, waist, chest, upper_chest, neck = (
        px(705, 792), px(737, 733), px(774, 664), px(794, 620), px(808, 590)
    )
    spine_up = (neck - pelvis).normalized()
    hollow = Vector((HOLLOW_CENTRE[0], 0.0, HOLLOW_CENTRE[1]))
    off_moon = perpendicular(spine_up, hollow - chest)             # away from the moon, in the picture plane
    chest_out = (off_moon * 0.55 + TOWARDS_CAMERA * 0.83).normalized()
    moon_side = (-off_moon * 0.83 + TOWARDS_CAMERA * 0.55).normalized()  # towards the shoulder on the moon
    free_side = -moon_side
    oval = dict(side=moon_side, flatten=0.8, segments=28)

    torso = spline([(pelvis, 0.17), (waist, 0.16), (chest, 0.2), (upper_chest, 0.185), (neck, 0.1)])
    tube("Suit torso", torso, mats["suit"], astronaut, **oval)
    tube("Vest", torso, mats["suit_blue"], astronaut, 0.4, 0.9, swell=1.05, caps="flat", **oval)
    tube("Chest strap", torso, mats["suit"], astronaut, 0.47, 0.52, swell=1.09, caps="flat", **oval)
    tube("Belt", torso, mats["navy"], astronaut, 0.15, 0.25, swell=1.07, caps="flat", **oval)
    tube("Hip band", torso, mats["suit_blue"], astronaut, 0.02, 0.1, swell=1.04, caps="flat", **oval)

    belt, _, belt_radius = path_at(torso, 0.2)
    belt_front = belt + chest_out * belt_radius * 0.87
    box("Belt buckle", belt_front, moon_side, chest_out, (0.075, 0.055, 0.03), mats["suit"], astronaut)
    box("Belt buckle pin", belt_front + chest_out * 0.012, moon_side, chest_out, (0.03, 0.035, 0.02), mats["navy"], astronaut, bevel=0.004)
    for label, side in (("Moon-side", moon_side), ("Free", free_side)):
        pouch = belt + side * 0.115 + chest_out * belt_radius * 0.72 - spine_up * 0.015
        outward = (chest_out + side * 0.55).normalized()
        box(f"{label} belt pouch", pouch, spine_up, outward, (0.1, 0.085, 0.05), mats["suit"], astronaut)
        box(f"{label} belt pouch flap", pouch + spine_up * 0.03 + outward * 0.02, spine_up, outward, (0.045, 0.09, 0.025), mats["suit_blue"], astronaut, bevel=0.006)
        sphere(f"{label} belt pouch stud", pouch + outward * 0.032, 0.01, mats["navy"], astronaut, segments=8)

    ring("Collar", neck - spine_up * 0.03, spine_up, 0.128, 0.036, mats["suit"], astronaut)
    ring("Collar trim", neck - spine_up * 0.066, spine_up, 0.148, 0.02, mats["navy"], astronaut)
    disc("Collar seal", neck - spine_up * 0.02, spine_up, 0.115, 0.03, mats["navy"], astronaut)
    for index, turn in enumerate(range(0, 360, 60)):
        angle = math.radians(turn + 30)
        outward = chest_out * math.cos(angle) + moon_side * math.sin(angle)
        box(
            f"Collar latch {index + 1}", neck - spine_up * 0.03 + outward * 0.158,
            spine_up.cross(outward), outward, (0.045, 0.035, 0.022), mats["suit_blue"], astronaut, bevel=0.005,
        )

    # Chest pack with a screen and buttons.
    pack = chest + spine_up * 0.045 + chest_out * 0.165
    box("Chest pack", pack, spine_up, chest_out, (0.2, 0.25, 0.09), mats["suit"], astronaut, bevel=0.018)
    box("Chest screen", pack + chest_out * 0.045 + spine_up * 0.04, spine_up, chest_out, (0.07, 0.19, 0.02), mats["navy"], astronaut, bevel=0.006)
    box("Chest readout", pack + chest_out * 0.052 + spine_up * 0.04 + moon_side * 0.03, spine_up, chest_out, (0.025, 0.09, 0.015), mats["star"], astronaut, bevel=0.003)
    box("Chest panel", pack + chest_out * 0.045 - spine_up * 0.045, spine_up, chest_out, (0.065, 0.19, 0.02), mats["suit_blue"], astronaut, bevel=0.006)
    for index, offset in enumerate((-0.06, -0.02, 0.02)):
        box(
            f"Chest button {index + 1}", pack + chest_out * 0.058 - spine_up * 0.045 + moon_side * offset,
            spine_up, chest_out, (0.03, 0.025, 0.015), mats["suit"], astronaut, bevel=0.004,
        )
    disc("Chest dial", pack + chest_out * 0.058 - spine_up * 0.045 + moon_side * 0.066, chest_out, 0.017, 0.02, mats["navy"], astronaut)
    disc("Chest valve", pack + free_side * 0.13 - spine_up * 0.03, free_side, 0.03, 0.03, mats["suit_blue"], astronaut)
    for label, side in (("Moon-side", moon_side), ("Free", free_side)):
        strap = spline(
            [
                (pack + spine_up * 0.08 + side * 0.09 + chest_out * 0.03, 0.026),
                (upper_chest + side * 0.11 + chest_out * 0.165, 0.026),
                (upper_chest + spine_up * 0.06 + side * 0.125 + chest_out * 0.075, 0.026),
                (upper_chest + spine_up * 0.07 + side * 0.125 - chest_out * 0.06, 0.026),
            ]
        )
        tube(f"{label} harness strap", strap, mats["suit"], astronaut, side=side, flatten=0.4, segments=10)

    # Life-support pack on the back, with two small tanks and a hose.
    back = chest.lerp(upper_chest, 0.3) - chest_out * 0.185
    box("Backpack", back, spine_up, -chest_out, (0.33, 0.27, 0.12), mats["suit"], astronaut, bevel=0.025)
    box("Backpack cap", back + spine_up * 0.15, spine_up, -chest_out, (0.05, 0.25, 0.11), mats["suit_blue"], astronaut, bevel=0.012)
    box("Backpack panel", back - chest_out * 0.06, spine_up, -chest_out, (0.16, 0.14, 0.02), mats["suit_blue"], astronaut, bevel=0.006)
    for index, side in enumerate((moon_side, free_side)):
        rod(f"Backpack tank {index + 1}", back - spine_up * 0.2 + side * 0.07, back - spine_up * 0.08 + side * 0.07, 0.04, mats["navy"], astronaut, segments=12)
    hose = spline(
        [
            (pack + free_side * 0.14 - spine_up * 0.03, 0.016),
            (chest + free_side * 0.24 - spine_up * 0.02, 0.016),
            (back + free_side * 0.15 - spine_up * 0.05, 0.016),
        ]
    )
    tube("Air hose", hose, mats["navy"], astronaut, segments=8)

    # --- Head: looking up at the helmet, turned a little to the camera. ---
    head = px(838, 512)
    head_radius = 0.19
    face = Vector((-0.5, -0.74, 0.42)).normalized()
    crown = perpendicular(face, Vector((0.3, 0.0, 0.95)))
    ear_side = face.cross(crown).normalized()

    def on_ball(up_deg, around_deg, centre, radii):
        """
        A point on a head-shaped ball, by angles from the way the face
        looks. radii: half-sizes across the ears, front to back, and up.
        """
        up, around = math.radians(up_deg), math.radians(around_deg)
        return (
            centre
            + ear_side * radii[0] * math.cos(up) * math.sin(around)
            + face * radii[1] * math.cos(up) * math.cos(around)
            + crown * radii[2] * math.sin(up)
        )

    skull = (head_radius * 0.94, head_radius, head_radius * 1.05)

    def on_head(up_deg, around_deg, lift=1.0):
        return on_ball(up_deg, around_deg, head, [r * lift for r in skull])

    ellipsoid("Head", head, ear_side, crown, skull, mats["skin"], astronaut, segments=32)
    jaw_centre = head - crown * 0.085 + face * 0.022
    jaw = (head_radius * 0.76, head_radius * 0.8, head_radius * 0.7)
    ellipsoid("Jaw", jaw_centre, ear_side, crown, jaw, mats["skin"], astronaut)
    tube("Neck", spline([(head - crown * 0.1, 0.075), (neck, 0.08)], per=2), mats["skin"], astronaut, caps=None)

    # Short hair on the sides and back, a mass of curls on top.
    ellipsoid(
        "Hair sides", head + crown * 0.022 - face * 0.042, ear_side, crown,
        [r * 1.035 for r in skull], mats["hair_fade"], astronaut, segments=32,
    )
    ellipsoid(
        "Hair top", head + crown * 0.075 - face * 0.03, ear_side, crown,
        (head_radius * 0.86, head_radius * 0.95, head_radius * 0.82), mats["hair"], astronaut, segments=32,
    )
    rng = random.Random(5)
    curls = 0
    while curls < 44:
        direction = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        height, forward = direction.dot(crown), direction.dot(face)
        if height < 0.5 or forward > 0.72:
            continue
        curls += 1
        # Curls near the forehead are bigger and sit further out: a quiff.
        size = rng.uniform(0.04, 0.062) + max(forward, 0) * 0.02
        sphere(f"Curl {curls}", head + crown * 0.03 + direction * head_radius * (1.0 + max(forward, 0) * 0.12), size, mats["hair"], astronaut, segments=12)

    # Beard: a shell around the jaw, with the mouth drawn on it.
    beard_centre = head - crown * 0.1 + face * 0.024
    beard = (head_radius * 0.81, head_radius * 0.845, head_radius * 0.68)
    ellipsoid("Beard", beard_centre, ear_side, crown, beard, mats["hair"], astronaut, segments=32)
    for label, sign in (("Left", -1), ("Right", 1)):
        sideburn = [(on_head(up, sign * 82, 1.02), 0.024) for up in (8, -12, -30)]
        tube(f"{label} sideburn", spline(sideburn, per=3), mats["hair"], astronaut, segments=8)
    beard_skin = [r * 1.015 for r in beard]
    smile = [(on_ball(-18 + 17 * (a / 36) ** 2, a, beard_centre, beard_skin), 0.0075) for a in range(-36, 37, 12)]
    plain(tube("Smile", spline(smile, per=3), mats["lip"], astronaut, segments=8))
    moustache = [(on_ball(1 - 7 * (a / 34) ** 2, a, beard_centre, [r * 1.025 for r in beard]), 0.013) for a in range(-34, 35, 17)]
    plain(tube("Moustache", spline(moustache, per=3), mats["hair"], astronaut, segments=8))

    nose = on_head(-8, 0, 0.99)
    ellipsoid("Nose", nose + face * 0.012, ear_side, crown, (0.03, 0.04, 0.036), mats["skin"], astronaut, segments=16)
    ellipsoid("Nose bridge", on_head(4, 0, 0.98), ear_side, crown, (0.02, 0.022, 0.045), mats["skin"], astronaut, segments=12)

    gaze = (face + crown * 0.35 - ear_side * 0.0).normalized()
    for label, sign in (("Left", -1), ("Right", 1)):
        ellipsoid(
            f"{label} ear", head + ear_side * sign * head_radius * 0.93 - crown * 0.03 - face * 0.03,
            ear_side, crown, (0.02, 0.032, 0.048), mats["skin"], astronaut, segments=12,
        )
        eye = on_head(9, sign * 23, 0.955)
        plain(sphere(f"{label} eye white", eye, 0.021, mats["eye_white"], astronaut, segments=14))
        plain(sphere(f"{label} pupil", eye + gaze * 0.0125, 0.0125, mats["eye"], astronaut, segments=12))
        lid = [(on_head(14.5, sign * around, 1.0), 0.006) for around in (14, 23, 32)]
        plain(tube(f"{label} eyelid", spline(lid, per=3), mats["hair"], astronaut, segments=6))
        brow = [(on_head(26 - 2.5 * k, sign * (10 + 10 * k), 1.02), 0.012) for k in range(3)]
        plain(tube(f"{label} eyebrow", spline(brow, per=4), mats["hair"], astronaut, segments=8))

        # Squared-off glasses, held just in front of the eyes.
        lens = head + face * (head_radius + 0.02) + crown * 0.03 + ear_side * sign * 0.068
        rim = []
        for k in range(36):
            angle = 2 * math.pi * k / 36
            rim.append(lens + ear_side * 0.054 * power(math.cos(angle), 0.5) + crown * 0.039 * power(math.sin(angle), 0.5))
        plain(loop_tube(f"{label} glasses frame", rim, face, 0.008, mats["glasses"], astronaut))
        hinge = lens + ear_side * sign * 0.054 + crown * 0.02
        plain(rod(f"{label} glasses arm", hinge, head + ear_side * sign * (head_radius * 0.94 + 0.012) + crown * 0.03 - face * 0.02, 0.0065, mats["glasses"], astronaut))
    bridge = head + face * (head_radius + 0.02) + crown * 0.042
    plain(rod("Glasses bridge", bridge - ear_side * 0.014, bridge + ear_side * 0.014, 0.0065, mats["glasses"], astronaut))

    # --- Arms: hands clasped behind the head, elbows out to each side. ---
    arm_bands = [
        (0.12, 0.21, "suit_blue"), (0.29, 0.36, "suit_blue"),
        (0.44, 0.6, "navy"),
        (0.68, 0.75, "suit_blue"), (0.83, 0.93, "suit_blue"),
    ]
    free_shoulder = upper_chest + free_side * 0.21
    moon_shoulder = upper_chest + moon_side * 0.21
    behind_head = head - face * (head_radius + 0.07)
    to_free = perpendicular(face, free_shoulder - head)
    free_hand = behind_head + to_free * 0.085
    moon_hand = behind_head - to_free * 0.085
    free_elbow = px(652, 518, 0.27)
    # The elbow on the moon's side sticks out past the moon's front face.
    moon_elbow = px(985, 562, -0.3)
    arms = (
        ("Free", free_shoulder, free_elbow, free_hand, free_side, -to_free),
        ("Moon-side", moon_shoulder, moon_elbow, moon_hand, moon_side, to_free),
    )
    for label, shoulder, elbow, hand, side, reach in arms:
        arm = limb(f"{label} arm", [(shoulder, 0.105), (elbow, 0.085), (hand - reach * 0.1, 0.07)], arm_bands, mats, astronaut)
        ellipsoid(f"{label} shoulder", shoulder + side * 0.02, spine_up, side, (0.135, 0.13, 0.12), mats["suit_blue"], astronaut)
        ellipsoid(f"{label} shoulder plate", shoulder + side * 0.06 + spine_up * 0.03, spine_up, side, (0.1, 0.1, 0.1), mats["suit"], astronaut)
        joint_pad(f"{label} elbow", arm, 0.52, elbow - shoulder.lerp(hand, 0.5), mats, astronaut, size=0.72)
        glove(label, hand - reach * 0.1, reach, face, mats, astronaut)

    # --- Legs: one knee raised, the other leg stretched along the moon. ---
    leg_bands = [
        (0.14, 0.2, "suit_blue"), (0.27, 0.32, "suit_blue"),
        (0.42, 0.58, "navy"),
        (0.66, 0.71, "suit_blue"), (0.78, 0.83, "suit_blue"), (0.9, 1.0, "navy"),
    ]
    # Raised leg, on the side away from the camera.
    raised_hip = pelvis + free_side * 0.09
    raised_knee, raised_ankle, raised_toe = px(470, 622, 0.13), px(356, 808, 0.13), px(292, 848, 0.13)
    raised = limb("Raised leg", [(raised_hip, 0.14), (raised_knee, 0.108), (raised_ankle, 0.088)], leg_bands, mats, astronaut)
    joint_pad("Raised knee", raised, 0.5, raised_knee - raised_hip.lerp(raised_ankle, 0.5), mats, astronaut)
    boot("Raised", raised_ankle, raised_toe, raised_ankle - raised_knee, raised_ankle - raised_knee, mats, astronaut)

    # Resting leg, nearer the camera, lying along the moon.
    resting_hip = pelvis + moon_side * 0.09
    resting_knee, resting_ankle, resting_toe = px(508, 848, -0.16), px(374, 903, -0.2), px(302, 934, -0.2)
    resting = limb("Resting leg", [(resting_hip, 0.14), (resting_knee, 0.108), (resting_ankle, 0.088)], leg_bands, mats, astronaut)
    joint_pad("Resting knee", resting, 0.5, TOWARDS_CAMERA + Z * 0.8, mats, astronaut)
    boot("Resting", resting_ankle, resting_toe, resting_ankle - resting_knee, resting_ankle - hollow, mats, astronaut)

    # A pocket strapped to the thigh nearest the camera.
    thigh, along, thigh_radius = path_at(resting, 0.23)
    thigh_out = perpendicular(along, TOWARDS_CAMERA + Z * 0.9)
    pocket = thigh + thigh_out * thigh_radius * 1.08
    box("Thigh pocket", pocket, along, thigh_out, (0.12, 0.1, 0.05), mats["suit"], astronaut)
    box("Thigh pocket flap", pocket - along * 0.035 + thigh_out * 0.02, along, thigh_out, (0.05, 0.105, 0.025), mats["suit_blue"], astronaut, bevel=0.006)
    sphere("Thigh pocket stud", pocket - along * 0.02 + thigh_out * 0.036, 0.011, mats["navy"], astronaut, segments=8)
    return astronaut


# --------------------------------------------------------------------------
# Helmet
# --------------------------------------------------------------------------


def build_helmet(mats, parent):
    """The helmet, floating up and to the left with a thin orbit around it."""
    helmet = group("Helmet", parent)
    centre = px(430, 302, -0.05)
    radius = 0.28
    forward = Vector((0.55, -0.8, 0.2)).normalized()   # the way the visor looks
    up = perpendicular(forward, Vector((-0.3, 0.0, 0.95)))
    side = up.cross(forward).normalized()

    def on_shell(turn_deg, lift_deg, lean_deg=0.0, scale=1.0):
        """A point on the shell: turn from the visor over the top, lean sideways."""
        turn, lean = math.radians(turn_deg), math.radians(lean_deg)
        lift = math.radians(lift_deg)
        direction = (
            (forward * math.cos(turn) + up * math.sin(turn)) * math.cos(lean) * math.cos(lift)
            + side * math.sin(lean)
            + up * math.sin(lift)
        ).normalized()
        return centre + direction * radius * scale

    sphere("Helmet shell", centre, radius, mats["suit"], helmet, segments=48)

    # The visor is a second, darker ball pushed out through the front.
    visor_centre = centre + forward * radius * 0.27 + up * radius * 0.045
    visor_radius = radius * 0.88
    sphere("Visor", visor_centre, visor_radius, mats["visor"], helmet, segments=48)
    visor_axis = (visor_centre - centre).normalized()
    gap = (visor_centre - centre).length
    rim_distance = (gap**2 + radius**2 - visor_radius**2) / (2 * gap)
    rim_radius = math.sqrt(radius**2 - rim_distance**2)
    ring("Visor rim", centre + visor_axis * rim_distance, visor_axis, rim_radius, 0.022, mats["suit_blue"], helmet, count=64)
    ring("Visor frame", centre + visor_axis * (rim_distance - 0.026), visor_axis, rim_radius + 0.03, 0.017, mats["navy"], helmet, count=64)
    bolt_distance = rim_distance - 0.075
    for index, bolt in enumerate(circle(centre + visor_axis * bolt_distance, visor_axis, math.sqrt(radius**2 - bolt_distance**2), 14)):
        sphere(f"Visor bolt {index + 1}", bolt, 0.011, mats["navy"], helmet, segments=8)

    # Reflections on the glass: a streak of light and two sparkles.
    def on_visor(right, lift):
        direction = (forward + side * right + up * lift).normalized()
        return visor_centre + direction * (visor_radius + 0.004), direction

    glint = [(on_visor(-0.6 + 0.13 * k, 0.62 - 0.025 * k * k)[0], 0.01) for k in range(4)]
    plain(tube("Visor glint", spline(glint, per=4), mats["star"], helmet, segments=8))
    plain(sphere("Visor glint dot", on_visor(-0.05, 0.5)[0], 0.011, mats["star"], helmet, segments=8))
    for index, (right, lift, size) in enumerate(((0.08, 0.08, 0.032), (0.38, -0.22, 0.02))):
        position, direction = on_visor(right, lift)
        plain(star(f"Visor sparkle {index + 1}", position, size, mats["star"], helmet, facing=direction))

    # Two stripes over the top, from above the visor to the back.
    for label, lean in (("Left", -19), ("Right", 19)):
        stripe = [(on_shell(turn, 0, lean), 0.05) for turn in range(64, 215, 10)]
        tube(f"{label} top stripe", spline(stripe, per=3), mats["suit_blue"], helmet, side=side, flatten=0.24, segments=12)
    crest = [(on_shell(turn, 0), 0.016) for turn in range(70, 200, 10)]
    tube("Crest", spline(crest, per=3), mats["navy"], helmet, segments=8)

    for label, sign in (("Left", -1), ("Right", 1)):
        out = side * sign
        ear = centre + out * radius * 0.93 - up * 0.025
        disc(f"{label} ear cap", ear, out, 0.095, 0.06, mats["suit"], helmet)
        ring(f"{label} ear cap edge", ear + out * 0.03, out, 0.088, 0.012, mats["navy"], helmet, count=32)
        disc(f"{label} ear cap ring", ear + out * 0.026, out, 0.066, 0.03, mats["suit_blue"], helmet)
        disc(f"{label} ear cap hub", ear + out * 0.04, out, 0.034, 0.028, mats["suit"], helmet)
        sphere(f"{label} ear cap stud", ear + out * 0.055, 0.012, mats["navy"], helmet, segments=8)
    # A short aerial on one ear cap.
    aerial = centre - side * radius * 0.93 - up * 0.025 - side * 0.02 + up * 0.07
    rod("Aerial", aerial, aerial + up * 0.16 - side * 0.02, 0.008, mats["navy"], helmet)
    sphere("Aerial tip", aerial + up * 0.165 - side * 0.02, 0.018, mats["star"], helmet, segments=10)

    # Chin guard under the visor, and a vent on the back.
    chin = centre + forward * radius * 0.78 - up * radius * 0.66
    chin_out = (forward * 0.8 - up * 0.6).normalized()
    box("Chin guard", chin, side, chin_out, (0.19, 0.07, 0.07), mats["suit"], helmet, bevel=0.015)
    for index, offset in enumerate((-0.05, 0.0, 0.05)):
        box(f"Chin slot {index + 1}", chin + chin_out * 0.034 + side * offset, side, chin_out, (0.03, 0.04, 0.012), mats["navy"], helmet, bevel=0.003)
    vent = centre - forward * radius * 0.95 - up * 0.03
    box("Back vent", vent, side, -forward, (0.17, 0.12, 0.05), mats["suit_blue"], helmet, bevel=0.012)
    for index, offset in enumerate((-0.03, 0.0, 0.03)):
        box(f"Back vent slot {index + 1}", vent - forward * 0.024 + up * offset, side, -forward, (0.12, 0.014, 0.012), mats["navy"], helmet, bevel=0.003)

    # Neck ring, with latches all the way around.
    ring("Neck ring", centre - up * radius * 0.76, up, radius * 0.69, 0.04, mats["suit"], helmet)
    ring("Neck ring trim", centre - up * radius * 0.94, up, radius * 0.62, 0.026, mats["suit_blue"], helmet)
    disc("Neck lining", centre - up * radius * 0.9, up, radius * 0.61, 0.03, mats["navy"], helmet)
    for index, turn in enumerate(range(0, 360, 45)):
        angle = math.radians(turn + 22.5)
        outward = forward * math.cos(angle) + side * math.sin(angle)
        box(
            f"Neck latch {index + 1}",
            centre - up * radius * 0.76 + outward * (radius * 0.69 + 0.034),
            up.cross(outward), outward, (0.07, 0.05, 0.035), mats["suit_blue"], helmet, bevel=0.007,
        )
    return helmet


def build_sky(mats, parent):
    """Sparkles, specks and the helmet's orbit. These get no dark outline."""
    sky = group("Sky", parent)

    # The orbit: a thin tilted ring with specks travelling along it.
    orbit_normal = Vector((-0.326, -0.3, 0.897)).normalized()
    orbit = circle(px(468, 346, -0.05), orbit_normal, 0.8, 120)
    loop_tube("Orbit", orbit, orbit_normal, 0.0055, mats["orbit"], sky, segments=6)
    for index, (at, size) in enumerate(((6, 0.02), (33, 0.012), (71, 0.016), (98, 0.011))):
        sphere(f"Orbit speck {index + 1}", orbit[at], size, mats["star"], sky, segments=10)

    sparkles = [
        (px(625, 130, 0.3), 0.13),
        (px(200, 245, 0.4), 0.1),
        (px(245, 492, 0.2), 0.085),
        (px(1112, 1068, -0.1), 0.1),
    ]
    for index, (position, size) in enumerate(sparkles):
        star(f"Star {index + 1}", position, size, mats["star"], sky)

    specks = [
        (515, 70), (575, 130), (750, 180), (90, 220), (232, 213), (700, 290), (115, 410),
        (210, 600), (120, 575), (550, 490), (600, 235), (690, 210), (330, 150), (60, 560),
        (1050, 110), (1225, 200), (1228, 330), (1170, 910), (100, 1050), (45, 1000), (160, 940),
    ]
    rng = random.Random(2)
    for index, (x, y) in enumerate(specks):
        sphere(f"Speck {index + 1}", px(x, y, rng.uniform(0.15, 0.5)), rng.choice([0.008, 0.011, 0.014]), mats["star"], sky, segments=8)
    return sky


# --------------------------------------------------------------------------
# Joining and outlines
# --------------------------------------------------------------------------


def parts_of(owner, outline=False):
    """The meshes of a group, or the ones its outline is drawn from."""
    skip = "plain" if outline else "outline_only"
    return [obj for obj in owner.children_recursive if obj.type == "MESH" and not obj.get(skip)]


def joined_copy(name, parts, parent):
    """One mesh made from copies of parts, with their modifiers applied."""
    copies = []
    for part in parts:
        copy = part.copy()
        copy.data = part.data.copy()
        bpy.context.collection.objects.link(copy)
        copies.append(copy)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    for copy in copies:
        copy.select_set(True)
    bpy.context.view_layer.objects.active = copies[0]
    bpy.ops.object.convert(target="MESH")
    if len(copies) > 1:
        bpy.ops.object.join()
    joined = bpy.context.view_layer.objects.active
    world = joined.matrix_world.copy()
    joined.parent = parent
    joined.matrix_world = world
    joined.name = name
    joined.data.name = name
    return joined


def outline_of(name, source, thickness, mat, parent):
    """
    The dark line around a shape: a copy of it, slightly swollen and turned
    inside out, so only the part that sticks out past the edge is seen.
    """
    mesh = source.data.copy()
    mesh.name = name
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0002)
    bm.normal_update()
    for vert in bm.verts:
        vert.co += vert.normal * thickness
    bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.clear()
    mesh.materials.append(mat)
    mesh.polygons.foreach_set("material_index", [0] * len(mesh.polygons))
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    obj.matrix_world = source.matrix_world.copy()
    obj.visible_shadow = False
    return obj


# --------------------------------------------------------------------------


def render_previews(camera):
    """Check images for the model; only made when HERO_PREVIEW is set."""
    scene = bpy.context.scene
    world = bpy.data.worlds.new("Night")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.012, 0.035, 0.06, 1.0)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 3.0
    scene.world = world
    for engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine
            break
        except TypeError:
            continue
    try:
        scene.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    scene.render.resolution_x = scene.render.resolution_y = 1100
    views = {
        "front": ((0.0, -9.0, 0.0), (90, 0, 0)),
        "left": ((-4.2, -8.0, 0.9), (84, 0, -27.7)),
        "right": ((4.2, -8.0, 0.9), (84, 0, 27.7)),
        "astronaut": ((0.25, -4.6, -0.1), (90, 0, 0)),
        "face": ((0.1, -1.75, 0.75), (72, 0, -15)),
        "helmet": ((-0.45, -2.6, 0.95), (90, 0, 0)),
        "feet": ((-0.75, -2.6, -0.6), (90, 0, 0)),
    }
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    for name, (location, rotation) in views.items():
        camera.location = location
        camera.rotation_euler = [math.radians(angle) for angle in rotation]
        scene.render.filepath = os.path.join(PREVIEW_DIR, f"{name}.png")
        bpy.ops.render.render(write_still=True)
    camera.location, camera.rotation_euler = views["front"][0], (math.radians(90), 0, 0)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)

    mats = {name: material(name) for name in PALETTE}
    # The outline only shows its inside faces; that is what makes it a line.
    mats["outline"].use_backface_culling = True

    root = bpy.data.objects.new("Hero", None)
    bpy.context.collection.objects.link(root)

    groups = [
        build_moon(mats, root),
        build_astronaut(mats, root),
        build_helmet(mats, root),
        build_sky(mats, root),
    ]

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

    # For the website each group becomes a single mesh (far fewer objects
    # to draw), and the outlined groups get their dark line.
    joined, outlines = [], []
    for owner in groups:
        mesh = joined_copy(f"{owner.name} mesh", parts_of(owner), root)
        joined.append(mesh)
        print(f"{mesh.name}: {len(mesh.data.vertices)} vertices")
        if owner.name in OUTLINE:
            outlined = joined_copy("Outlined", parts_of(owner, outline=True), root)
            outlines.append(outline_of(f"{owner.name} outline", outlined, OUTLINE[owner.name], mats["outline"], root))
            bpy.data.objects.remove(outlined)

    for obj in [obj for obj in bpy.data.objects if obj.get("outline_only")]:
        bpy.data.objects.remove(obj)

    if PREVIEW_DIR:
        originals = [part for owner in groups for part in parts_of(owner)]
        for part in originals:
            part.hide_render = True
        render_previews(camera)
        for part in originals:
            part.hide_render = False

    os.makedirs(os.path.dirname(GLB_PATH), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in [root] + joined + outlines:
        obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=GLB_PATH,
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True,
        export_texcoords=False,
        # Draco shrinks the file several times over; the website loads the
        # matching decoder (see moon-scene.ts).
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
        export_draco_position_quantization=14,
        export_draco_normal_quantization=10,
    )

    # The .blend keeps the separate, named parts (and the outlines) instead.
    for mesh in joined:
        bpy.data.objects.remove(mesh)
    os.makedirs(os.path.dirname(BLEND_PATH), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)

    print(f"Saved {BLEND_PATH}")
    print(f"Exported {GLB_PATH} ({os.path.getsize(GLB_PATH) / 1024:.0f} kB)")


main()
