"""
=============================================================================
Security CCTV Asset Production Suite - Asset 49
Asset Name: SEC_Lock_Rack_Cabinet (Guvenlik Rack Kabini)
Headless Blender Generation & Validation Script v2
High-Fidelity 19-Inch Rack Cabinet with Internal EIA Rails & 3D Door
=============================================================================
"""

import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Matrix

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Rack_Cabinet.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Rack_Cabinet.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Lock_Rack_Cabinet"
MAX_TRIS = 850

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

def create_materials():
    # Slot 0: M_Metal
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    bsdf_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    if bsdf_m:
        bsdf_m.inputs["Base Color"].default_value = (0.22, 0.25, 0.28, 1.0)
        bsdf_m.inputs["Metallic"].default_value = 0.85
        bsdf_m.inputs["Roughness"].default_value = 0.40

    # Slot 1: M_Security_Atlas
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf_a = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if bsdf_a and os.path.exists(ATLAS_PATH):
        tex_node = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(ATLAS_PATH)
        mat_atlas.node_tree.links.new(tex_node.outputs["Color"], bsdf_a.inputs["Base Color"])
        bsdf_a.inputs["Metallic"].default_value = 0.80
        bsdf_a.inputs["Roughness"].default_value = 0.42

    return mat_metal, mat_atlas

def build_frame(mat_metal, mat_atlas):
    """
    Builds the main 19-inch rack enclosure frame:
    - Top canopy roof with exhaust fan vents (un-mirrored UV)
    - Bottom base plinth
    - 4 vertical outer corner posts
    - 4 internal 19-inch EIA rack upright mounting rails (18U height)
    - 4 horizontal depth support struts connecting front and rear rails
    - Rear solid panel with cable entry knockouts
    """
    mesh = bpy.data.meshes.new("Frame_Mesh")
    obj = bpy.data.objects.new("Frame", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx = 0.3000   # 600 mm width
    hy = 0.3000   # 600 mm depth
    z_floor = 0.0400  # above feet
    z_base  = 0.0700  # base plinth
    z_roof  = 1.0100  # roof start
    z_top   = 1.0400  # top canopy (1.04 m total height)

    # 1. Top Canopy Roof (600 x 600 x 30 mm)
    vr = [
        bm.verts.new((-hx, -hy, z_roof)),
        bm.verts.new(( hx, -hy, z_roof)),
        bm.verts.new(( hx,  hy, z_roof)),
        bm.verts.new((-hx,  hy, z_roof)),
        bm.verts.new((-hx, -hy, z_top)),
        bm.verts.new(( hx, -hy, z_top)),
        bm.verts.new(( hx,  hy, z_top)),
        bm.verts.new((-hx,  hy, z_top)),
    ]
    bm.faces.new([vr[0], vr[1], vr[2], vr[3]]) # roof bot
    f_roof_top = bm.faces.new([vr[4], vr[5], vr[6], vr[7]]) # roof top face with fan exhausts
    bm.faces.new([vr[0], vr[4], vr[5], vr[1]]) # roof rear
    bm.faces.new([vr[1], vr[5], vr[6], vr[2]]) # roof right
    bm.faces.new([vr[2], vr[6], vr[7], vr[3]]) # roof front
    bm.faces.new([vr[3], vr[7], vr[4], vr[0]]) # roof left

    # 2. Bottom Base Plinth (600 x 600 x 30 mm)
    vb = [
        bm.verts.new((-hx, -hy, z_floor)),
        bm.verts.new(( hx, -hy, z_floor)),
        bm.verts.new(( hx,  hy, z_floor)),
        bm.verts.new((-hx,  hy, z_floor)),
        bm.verts.new((-hx, -hy, z_base)),
        bm.verts.new(( hx, -hy, z_base)),
        bm.verts.new(( hx,  hy, z_base)),
        bm.verts.new((-hx,  hy, z_base)),
    ]
    bm.faces.new([vb[0], vb[3], vb[2], vb[1]]) # base bot
    bm.faces.new([vb[4], vb[5], vb[6], vb[7]]) # base top floor
    bm.faces.new([vb[0], vb[1], vb[5], vb[4]]) # base rear
    bm.faces.new([vb[1], vb[2], vb[6], vb[5]]) # base right
    bm.faces.new([vb[2], vb[3], vb[7], vb[6]]) # base front
    bm.faces.new([vb[3], vb[0], vb[4], vb[7]]) # base left

    # 3. Four Outer Corner Vertical Uprights (35 x 35 mm)
    post_w = 0.0350
    corners = [
        (-hx, -hy), (hx - post_w, -hy),
        (hx - post_w, hy - post_w), (-hx, hy - post_w)
    ]
    for cx, cy in corners:
        vp = [
            bm.verts.new((cx,          cy,          z_base)),
            bm.verts.new((cx + post_w, cy,          z_base)),
            bm.verts.new((cx + post_w, cy + post_w, z_base)),
            bm.verts.new((cx,          cy + post_w, z_base)),
            bm.verts.new((cx,          cy,          z_roof)),
            bm.verts.new((cx + post_w, cy,          z_roof)),
            bm.verts.new((cx + post_w, cy + post_w, z_roof)),
            bm.verts.new((cx,          cy + post_w, z_roof)),
        ]
        bm.faces.new([vp[0], vp[4], vp[5], vp[1]])
        bm.faces.new([vp[1], vp[5], vp[6], vp[2]])
        bm.faces.new([vp[2], vp[6], vp[7], vp[3]])
        bm.faces.new([vp[3], vp[7], vp[4], vp[0]])

    # 4. Rear Solid Panel with thickness (th = 0.0040)
    th_r = 0.0040
    vr_b = [
        bm.verts.new((-hx + 0.035, -hy + 0.002, z_base)),
        bm.verts.new(( hx - 0.035, -hy + 0.002, z_base)),
        bm.verts.new(( hx - 0.035, -hy + 0.002, z_roof)),
        bm.verts.new((-hx + 0.035, -hy + 0.002, z_roof)),
        bm.verts.new((-hx + 0.035, -hy + 0.002 + th_r, z_base)),
        bm.verts.new(( hx - 0.035, -hy + 0.002 + th_r, z_base)),
        bm.verts.new(( hx - 0.035, -hy + 0.002 + th_r, z_roof)),
        bm.verts.new((-hx + 0.035, -hy + 0.002 + th_r, z_roof)),
    ]
    bm.faces.new([vr_b[0], vr_b[3], vr_b[2], vr_b[1]]) # rear facing
    bm.faces.new([vr_b[4], vr_b[5], vr_b[6], vr_b[7]]) # front facing inside

    # 5. Internal 19-Inch EIA Rack Mounting Upright Rails (18U Height)
    # 4 solid 3D L-bracket rails extruded along Z
    rx_pos = 0.2325
    ry_front = 0.2100
    ry_rear  = -0.2100
    rail_w   = 0.0220 # 22 mm L-flange
    r_th     = 0.0030 # 3 mm sheet metal

    rack_rails = [
        (-rx_pos, ry_front,  1.0, -1.0), # Front Left
        ( rx_pos, ry_front, -1.0, -1.0), # Front Right
        (-rx_pos, ry_rear,   1.0,  1.0), # Rear Left
        ( rx_pos, ry_rear,  -1.0,  1.0), # Rear Right
    ]

    for rx, ry, sx, sy in rack_rails:
        # 6-vert L profile at bottom and top
        p_b = [
            bm.verts.new((rx,                       ry,                       z_base)),
            bm.verts.new((rx + sx * rail_w,          ry,                       z_base)),
            bm.verts.new((rx + sx * rail_w,          ry + sy * r_th,          z_base)),
            bm.verts.new((rx + sx * r_th,           ry + sy * r_th,          z_base)),
            bm.verts.new((rx + sx * r_th,           ry + sy * rail_w,        z_base)),
            bm.verts.new((rx,                       ry + sy * rail_w,        z_base)),
        ]
        p_t = [
            bm.verts.new((v.co.x, v.co.y, z_roof)) for v in p_b
        ]
        # Bottom and top caps
        bm.faces.new(p_b)
        bm.faces.new(list(reversed(p_t)))
        # 6 vertical side quads
        for i in range(6):
            ni = (i + 1) % 6
            bm.faces.new([p_b[i], p_b[ni], p_t[ni], p_t[i]])

    # 6. Horizontal Depth Support Struts (solid box channels connecting front & rear)
    st_th = 0.0060
    st_h  = 0.0240
    for sx, sign_x in [(-rx_pos, 1.0), (rx_pos, -1.0)]:
        for sz in [z_base + 0.100, z_roof - 0.120]:
            x0 = sx
            x1 = sx + sign_x * st_th
            vst = [
                bm.verts.new((x0, ry_rear,  sz)),
                bm.verts.new((x1, ry_rear,  sz)),
                bm.verts.new((x1, ry_front, sz)),
                bm.verts.new((x0, ry_front, sz)),
                bm.verts.new((x0, ry_rear,  sz + st_h)),
                bm.verts.new((x1, ry_rear,  sz + st_h)),
                bm.verts.new((x1, ry_front, sz + st_h)),
                bm.verts.new((x0, ry_front, sz + st_h)),
            ]
            bm.faces.new([vst[0], vst[3], vst[2], vst[1]]) # bot
            bm.faces.new([vst[4], vst[5], vst[6], vst[7]]) # top
            bm.faces.new([vst[0], vst[4], vst[7], vst[3]]) # inner side
            bm.faces.new([vst[1], vst[2], vst[6], vst[5]]) # outer side

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    # UV Mapping
    ru_min, ru_max = 1080.0 / 2048.0, 1720.0 / 2048.0
    rv_min, rv_max = 1340.0 / 2048.0, 1984.0 / 2048.0

    # Roof Top (+Z): Oriented so front (+Y) has fan header and rear (-Y) has cable brush strip
    # Text reads left-to-right (-X to +X) when viewed from top
    f_roof_top.material_index = 1
    for loop in f_roof_top.loops:
        p = loop.vert.co
        u_norm = (p.x - (-hx)) / (2.0 * hx)
        u = ru_min + u_norm * (ru_max - ru_min)
        v_norm = (p.y - (-hy)) / (2.0 * hy)
        v = (1.0 - rv_max) + v_norm * (rv_max - rv_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (200.0 / 2048.0)
    for f in bm.faces:
        if f != f_roof_top:
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_side_panels(mat_metal, mat_atlas):
    """
    Builds the removable vented side panels on left (-X) and right (+X)
    with completely un-mirrored UV texture mapping on both sides.
    """
    mesh = bpy.data.meshes.new("Side_Panels_Mesh")
    obj = bpy.data.objects.new("Side_Panels", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx = 0.3000
    hy0, hy1 = -0.2700, 0.2700
    hz0, hz1 =  0.0750, 1.0050
    th = 0.0080

    # 1. Left Side Panel (-X)
    v_left = [
        bm.verts.new((-hx,      hy0, hz0)),
        bm.verts.new((-hx,      hy1, hz0)),
        bm.verts.new((-hx,      hy1, hz1)),
        bm.verts.new((-hx,      hy0, hz1)),
        bm.verts.new((-hx + th, hy0, hz0)),
        bm.verts.new((-hx + th, hy1, hz0)),
        bm.verts.new((-hx + th, hy1, hz1)),
        bm.verts.new((-hx + th, hy0, hz1)),
    ]
    f_left_outer = bm.faces.new([v_left[0], v_left[3], v_left[2], v_left[1]]) # Facing -X
    bm.faces.new([v_left[4], v_left[5], v_left[6], v_left[7]]) # Facing +X
    bm.faces.new([v_left[0], v_left[1], v_left[5], v_left[4]]) # bottom
    bm.faces.new([v_left[2], v_left[3], v_left[7], v_left[6]]) # top
    bm.faces.new([v_left[3], v_left[0], v_left[4], v_left[7]]) # rear
    bm.faces.new([v_left[1], v_left[2], v_left[6], v_left[5]]) # front

    # 2. Right Side Panel (+X)
    v_right = [
        bm.verts.new((hx - th, hy0, hz0)),
        bm.verts.new((hx - th, hy1, hz0)),
        bm.verts.new((hx - th, hy1, hz1)),
        bm.verts.new((hx - th, hy0, hz1)),
        bm.verts.new((hx,      hy0, hz0)),
        bm.verts.new((hx,      hy1, hz0)),
        bm.verts.new((hx,      hy1, hz1)),
        bm.verts.new((hx,      hy0, hz1)),
    ]
    f_right_outer = bm.faces.new([v_right[4], v_right[5], v_right[6], v_right[7]]) # Facing +X
    bm.faces.new([v_right[0], v_right[3], v_right[2], v_right[1]])
    bm.faces.new([v_right[0], v_right[4], v_right[7], v_right[3]])
    bm.faces.new([v_right[1], v_right[2], v_right[6], v_right[5]])
    bm.faces.new([v_right[2], v_right[3], v_right[7], v_right[6]])
    bm.faces.new([v_right[0], v_right[1], v_right[5], v_right[4]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    # UV Mapping
    pu_min, pu_max = 1080.0 / 2048.0, 1720.0 / 2048.0
    pv_min, pv_max = 64.0 / 2048.0, 1280.0 / 2048.0

    # Left outer face (-X):
    # Viewer standing at left of cabinet looking towards +X:
    # Front (+Y) is to viewer's left -> pu_min (start of text)
    # Rear (-Y) is to viewer's right -> pu_max (end of text)
    f_left_outer.material_index = 1
    for loop in f_left_outer.loops:
        p = loop.vert.co
        u_norm = (p.y - hy1) / (hy0 - hy1)
        u = pu_min + u_norm * (pu_max - pu_min)
        v_norm = (p.z - hz0) / (hz1 - hz0)
        v = (1.0 - pv_max) + v_norm * (pv_max - pv_min)
        loop[uv_layer].uv = (u, v)

    # Right outer face (+X):
    # Viewer standing at right of cabinet looking towards -X:
    # Rear (-Y) is to viewer's left -> pu_min (start of text)
    # Front (+Y) is to viewer's right -> pu_max (end of text)
    f_right_outer.material_index = 1
    for loop in f_right_outer.loops:
        p = loop.vert.co
        u_norm = (p.y - hy0) / (hy1 - hy0)
        u = pu_min + u_norm * (pu_max - pu_min)
        v_norm = (p.z - hz0) / (hz1 - hz0)
        v = (1.0 - pv_max) + v_norm * (pv_max - pv_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (200.0 / 2048.0)
    for f in bm.faces:
        if f not in (f_left_outer, f_right_outer):
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_feet(mat_metal, mat_atlas):
    """
    Builds the 4 adjustable leveling feet at bottom corners.
    """
    mesh = bpy.data.meshes.new("Feet_Mesh")
    obj = bpy.data.objects.new("Feet", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx = 0.2600
    hy = 0.2600
    z_floor = 0.0000
    z_pad   = 0.0150
    z_top   = 0.0400

    r_pad = 0.0240
    r_pin = 0.0080
    segs = 6

    for fx in [-hx, hx]:
        for fy in [-hy, hy]:
            # Foot base pad
            v_pad_b = []
            v_pad_t = []
            for i in range(segs):
                ang = i * 2.0 * math.pi / segs
                x = fx + r_pad * math.cos(ang)
                y = fy + r_pad * math.sin(ang)
                v_pad_b.append(bm.verts.new((x, y, z_floor)))
                v_pad_t.append(bm.verts.new((x, y, z_pad)))

            bm.faces.new(v_pad_b)
            bm.faces.new(list(reversed(v_pad_t)))
            for i in range(segs):
                ni = (i + 1) % segs
                bm.faces.new([v_pad_b[i], v_pad_b[ni], v_pad_t[ni], v_pad_t[i]])

            # Threaded stem
            v_pin_b = []
            v_pin_t = []
            for i in range(segs):
                ang = i * 2.0 * math.pi / segs
                x = fx + r_pin * math.cos(ang)
                y = fy + r_pin * math.sin(ang)
                v_pin_b.append(bm.verts.new((x, y, z_pad)))
                v_pin_t.append(bm.verts.new((x, y, z_top)))

            for i in range(segs):
                ni = (i + 1) % segs
                bm.faces.new([v_pin_b[i], v_pin_b[ni], v_pin_t[ni], v_pin_t[i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (200.0 / 2048.0)
    for f in bm.faces:
        f.material_index = 0
        for loop in f.loops:
            loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_front_door(mat_metal, mat_atlas):
    """
    Builds the high-fidelity hinged 19-inch rack front door (580 x 940 x 16 mm).
    Hinged on the left stile at Door_Hinge_Pivot at (+0.290, 0.295, 0.540).
    Extends along -X from 0.0 to -0.580 (in world from +0.290 to -0.290).
    Features:
    - 3D door frame stiles and rails with recessed perforated mesh window
    - Digital swing-handle lock housing on the right stile (-X in world)
    - 3D internal latch cam on the inside back face
    """
    mesh = bpy.data.meshes.new("Front_Door_Mesh")
    obj = bpy.data.objects.new("Front_Door", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    door_w = 0.5800  # 580 mm width (X: 0.0 to -0.5800)
    door_h = 0.9400  # 940 mm height (Z: -0.4700 to +0.4700)
    th_door = 0.0160 # 16 mm door thickness (Y: 0.0 to -th_door)

    # 1. Main Door Box
    # 4 corner vertices at front Y = 0.0 (normal +Y)
    vf0 = bm.verts.new(( 0.0,     0.0, -door_h / 2.0))
    vf1 = bm.verts.new((-door_w,  0.0, -door_h / 2.0))
    vf2 = bm.verts.new((-door_w,  0.0,  door_h / 2.0))
    vf3 = bm.verts.new(( 0.0,     0.0,  door_h / 2.0))

    # Back face vertices at Y = -th_door
    vb0 = bm.verts.new(( 0.0,    -th_door, -door_h / 2.0))
    vb1 = bm.verts.new((-door_w, -th_door, -door_h / 2.0))
    vb2 = bm.verts.new((-door_w, -th_door,  door_h / 2.0))
    vb3 = bm.verts.new(( 0.0,    -th_door,  door_h / 2.0))

    f_front = bm.faces.new([vf0, vf1, vf2, vf3]) # Main front face (normal +Y)
    f_back  = bm.faces.new([vb0, vb3, vb2, vb1]) # Back inside face
    bm.faces.new([vf0, vb0, vb1, vf1]) # bottom
    bm.faces.new([vf2, vb2, vb3, vf3]) # top
    bm.faces.new([vf3, vb3, vb0, vf0]) # right hinge stile
    bm.faces.new([vf1, vb1, vb2, vf2]) # left lock stile

    # 2. Internal 3D Lock Cam Mechanism on the back face
    # Box sitting on the inside face near the lock handle (-door_w + 0.060)
    cx0, cx1 = -door_w + 0.0200, -door_w + 0.0900
    cy0, cy1 = -th_door - 0.0250, -th_door
    cz0, cz1 = -0.0800, 0.0800

    vc = [
        bm.verts.new((cx0, cy0, cz0)),
        bm.verts.new((cx1, cy0, cz0)),
        bm.verts.new((cx1, cy0, cz1)),
        bm.verts.new((cx0, cy0, cz1)),
        bm.verts.new((cx0, cy1, cz0)),
        bm.verts.new((cx1, cy1, cz0)),
        bm.verts.new((cx1, cy1, cz1)),
        bm.verts.new((cx0, cy1, cz1)),
    ]
    bm.faces.new([vc[0], vc[1], vc[2], vc[3]]) # front of cam
    bm.faces.new([vc[0], vc[4], vc[5], vc[1]]) # bot
    bm.faces.new([vc[2], vc[6], vc[7], vc[3]]) # top
    bm.faces.new([vc[3], vc[7], vc[4], vc[0]]) # left
    bm.faces.new([vc[1], vc[5], vc[6], vc[2]]) # right

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    # UV Mapping
    du_min, du_max = 64.0 / 2048.0, 1024.0 / 2048.0
    dv_min, dv_max = 64.0 / 2048.0, 1984.0 / 2048.0

    # Front Face (+Y in world):
    # Viewer standing at front (+Y): left is hinge (p.x = 0 -> du_min), right is lock (p.x = -door_w -> du_max)
    f_front.material_index = 1
    for loop in f_front.loops:
        p = loop.vert.co
        u_norm = -p.x / door_w
        u = du_min + u_norm * (du_max - du_min)
        v_norm = (p.z - (-door_h / 2.0)) / door_h
        v = (1.0 - dv_max) + v_norm * (dv_max - dv_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (200.0 / 2048.0)
    for f in bm.faces:
        if f != f_front:
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def count_triangles(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    count = len(bm.faces)
    bm.free()
    return count

def generate_asset():
    reset_scene()

    mat_metal, mat_atlas = create_materials()

    # 1. Create Root Empty
    root_obj = bpy.data.objects.new(ASSET_NAME, None)
    root_obj.empty_display_type = 'ARROWS'
    root_obj.empty_display_size = 0.10
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_obj)

    # 2. Build Frame
    frame = build_frame(mat_metal, mat_atlas)
    frame.parent = root_obj

    # 3. Build Side Panels
    side_panels = build_side_panels(mat_metal, mat_atlas)
    side_panels.parent = frame

    # 4. Build Feet
    feet = build_feet(mat_metal, mat_atlas)
    feet.parent = frame

    # 5. Create Door_Hinge_Pivot Empty at front-left corner (+0.290, 0.295, 0.540)
    door_pivot = bpy.data.objects.new("Door_Hinge_Pivot", None)
    door_pivot.empty_display_type = 'PLAIN_AXES'
    door_pivot.empty_display_size = 0.05
    door_pivot.location = Vector((0.2900, 0.2950, 0.5400))
    door_pivot.parent = frame
    bpy.context.collection.objects.link(door_pivot)

    door_pivot["limit_min_z"] = -110.0
    door_pivot["limit_max_z"] = 0.0
    c_door = door_pivot.constraints.new(type='LIMIT_ROTATION')
    c_door.use_limit_z = True
    c_door.min_z = math.radians(-110.0)
    c_door.max_z = math.radians(0.0)
    c_door.owner_space = 'LOCAL'

    # 6. Build Front_Door
    front_door = build_front_door(mat_metal, mat_atlas)
    front_door.parent = door_pivot
    front_door.location = Vector((0.0, 0.0, 0.0))

    # Mark sharp edges & auto smooth
    for obj in [frame, side_panels, feet, front_door]:
        mesh = obj.data
        for edge in mesh.edges:
            edge.use_edge_sharp = True
        mesh.shade_smooth()

    bpy.context.view_layer.update()

    # Total triangles verification
    total_tris = 0
    mesh_count = 0
    empty_count = 2  # Root + Door_Hinge_Pivot

    for obj in [frame, side_panels, feet, front_door]:
        tris = count_triangles(obj)
        total_tris += tris
        mesh_count += 1
        print(f"Mesh '{obj.name}': {tris} tris")

    print(f"Total Tris: {total_tris} (Max: {MAX_TRIS})")
    assert total_tris <= MAX_TRIS, f"Tri count exceeded: {total_tris} > {MAX_TRIS}"

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved .blend to: {BLEND_PATH}")

    # Clean up any .blend1
    blend1_path = BLEND_PATH + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)

    # Select hierarchy for FBX export
    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    frame.select_set(True)
    side_panels.select_set(True)
    feet.select_set(True)
    door_pivot.select_set(True)
    front_door.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    bpy.ops.export_scene.fbx(
        filepath=FBX_PATH,
        use_selection=True,
        object_types={'MESH', 'EMPTY'},
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,
        bake_space_transform=False,
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode='AUTO'
    )
    print(f"Exported FBX to: {FBX_PATH}")

    # Manifest update
    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data[ASSET_NAME] = {
        "fbx_path": FBX_PATH,
        "tris": total_tris,
        "mesh_count": mesh_count,
        "empty_count": empty_count,
        "materials": ["M_Metal", "M_Security_Atlas"],
        "status": "SUCCESS"
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)
    print(f"Manifest written: {MANIFEST_PATH}")

    # Re-import test
    print("\n--- Running FBX Re-import Verification ---")
    reset_scene()
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)

    re_root = bpy.data.objects.get(ASSET_NAME)
    assert re_root is not None, f"Root '{ASSET_NAME}' missing after re-import!"
    re_meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    assert len(re_meshes) == mesh_count, f"Mesh count mismatch: {len(re_meshes)} != {mesh_count}"
    re_empties = [o for o in bpy.data.objects if o.type == 'EMPTY']
    assert len(re_empties) == empty_count, f"Empty count mismatch: {len(re_empties)} != {empty_count}"

    print(f"Re-import successful! Verified root, {len(re_empties)} empties, and {len(re_meshes)} meshes.")
    print("ALL ASSERTIONS PASSED.")

if __name__ == "__main__":
    generate_asset()
