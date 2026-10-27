"""
=============================================================================
Security CCTV Asset Production Suite - Asset 48
Asset Name: SEC_Lock_Door_Closer (Kapi Kapatici Mekanizma)
Headless Blender Generation & Validation Script v2
High-Fidelity Industrial Hydraulic Closer & Kinematic Scissor Arm
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Door_Closer.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Door_Closer.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Lock_Door_Closer"
MAX_TRIS = 420

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
        bsdf_m.inputs["Base Color"].default_value = (0.78, 0.81, 0.85, 1.0)
        bsdf_m.inputs["Metallic"].default_value = 0.85
        bsdf_m.inputs["Roughness"].default_value = 0.35

    # Slot 1: M_Security_Atlas
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf_a = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if bsdf_a and os.path.exists(ATLAS_PATH):
        tex_node = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(ATLAS_PATH)
        mat_atlas.node_tree.links.new(tex_node.outputs["Color"], bsdf_a.inputs["Base Color"])
        bsdf_a.inputs["Metallic"].default_value = 0.80
        bsdf_a.inputs["Roughness"].default_value = 0.38

    return mat_metal, mat_atlas

def build_body(mat_metal, mat_atlas):
    """
    Builds the high-fidelity cast aluminum hydraulic door closer body (220 x 50 x 52 mm)
    with 45° longitudinal chamfers, stepped hydraulic end caps, mounting flanges,
    and un-mirrored UV mapping.
    """
    mesh = bpy.data.meshes.new("Body_Mesh")
    obj = bpy.data.objects.new("Body", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx_body = 0.1000  # 200 mm main cylinder body (X: -0.100 to +0.100)
    hz_body = 0.0250  # 50 mm height (Z: -0.025 to +0.025)
    y_back  = 0.0000  # Back mounting plane (door face)
    y_front = 0.0520  # Front face
    ch_long = 0.0050  # 5 mm longitudinal chamfer on front edges

    hx_flange = 0.1250 # Flanges extend to +/- 0.1250 (250 mm total)
    th_flange = 0.0060 # 6 mm flange thickness

    # 1. Main Cast Body: 6-sided cross section in Y-Z extruded along X
    # Vertices profile at X = -hx_body (0..5) and X = +hx_body (6..11)
    # Profile:
    # 0: (y_back, -hz_body) - back bottom
    # 1: (y_front - ch_long, -hz_body) - front bottom before chamfer
    # 2: (y_front, -hz_body + ch_long) - front bottom after chamfer
    # 3: (y_front, hz_body - ch_long)  - front top before chamfer
    # 4: (y_front - ch_long, hz_body)  - front top after chamfer
    # 5: (y_back, hz_body)  - back top

    v_left = [
        bm.verts.new((-hx_body, y_back, -hz_body)),
        bm.verts.new((-hx_body, y_front - ch_long, -hz_body)),
        bm.verts.new((-hx_body, y_front, -hz_body + ch_long)),
        bm.verts.new((-hx_body, y_front,  hz_body - ch_long)),
        bm.verts.new((-hx_body, y_front - ch_long,  hz_body)),
        bm.verts.new((-hx_body, y_back,  hz_body)),
    ]

    v_right = [
        bm.verts.new((hx_body, y_back, -hz_body)),
        bm.verts.new((hx_body, y_front - ch_long, -hz_body)),
        bm.verts.new((hx_body, y_front, -hz_body + ch_long)),
        bm.verts.new((hx_body, y_front,  hz_body - ch_long)),
        bm.verts.new((hx_body, y_front - ch_long,  hz_body)),
        bm.verts.new((hx_body, y_back,  hz_body)),
    ]

    # Extruded faces
    f_bot   = bm.faces.new([v_left[0], v_right[0], v_right[1], v_left[1]])
    f_ch_b  = bm.faces.new([v_left[1], v_right[1], v_right[2], v_left[2]]) # bottom chamfer
    f_front = bm.faces.new([v_left[2], v_right[2], v_right[3], v_left[3]]) # vertical front face (valves & brand)
    f_ch_t  = bm.faces.new([v_left[3], v_right[3], v_right[4], v_left[4]]) # top chamfer
    f_top   = bm.faces.new([v_left[4], v_right[4], v_right[5], v_left[5]]) # top face (pinion & caution)
    f_back  = bm.faces.new([v_left[5], v_right[5], v_right[0], v_left[0]]) # back mounting surface

    # 2. Hydraulic Cylinder End Caps (Left: -hx_body, Right: +hx_body)
    # 6-sided end cap caps
    bm.faces.new(list(reversed(v_left)))
    bm.faces.new(v_right)

    # 3. Stepped hydraulic cylinder end plugs projecting 3mm
    plug_r = 0.0160
    plug_len = 0.0035
    plug_y = 0.0260 # cylinder center axis
    segs = 6

    for sign, x_base in [(-1, -hx_body), (1, hx_body)]:
        v_plug_base = []
        v_plug_tip = []
        x_tip = x_base + sign * plug_len
        for i in range(segs):
            ang = i * 2.0 * math.pi / segs
            py = plug_y + plug_r * math.cos(ang)
            pz = plug_r * math.sin(ang)
            v_plug_base.append(bm.verts.new((x_base, py, pz)))
            v_plug_tip.append(bm.verts.new((x_tip, py, pz)))

        # Tip face
        if sign > 0:
            bm.faces.new(v_plug_tip)
        else:
            bm.faces.new(list(reversed(v_plug_tip)))

        # Side rim
        for i in range(segs):
            ni = (i + 1) % segs
            if sign > 0:
                bm.faces.new([v_plug_base[i], v_plug_tip[i], v_plug_tip[ni], v_plug_base[ni]])
            else:
                bm.faces.new([v_plug_base[i], v_plug_base[ni], v_plug_tip[ni], v_plug_tip[i]])

    # 4. Left Mounting Flange: X: -hx_flange .. -hx_body, Y: 0.0 .. th_flange, Z: -hz_body .. +hz_body
    v_fl_l = [
        bm.verts.new((-hx_flange, 0.0, -hz_body)),
        bm.verts.new((-hx_body,   0.0, -hz_body)),
        bm.verts.new((-hx_body,   0.0,  hz_body)),
        bm.verts.new((-hx_flange, 0.0,  hz_body)),
        bm.verts.new((-hx_flange, th_flange, -hz_body)),
        bm.verts.new((-hx_body,   th_flange, -hz_body)),
        bm.verts.new((-hx_body,   th_flange,  hz_body)),
        bm.verts.new((-hx_flange, th_flange,  hz_body)),
    ]
    bm.faces.new([v_fl_l[4], v_fl_l[5], v_fl_l[6], v_fl_l[7]]) # front
    bm.faces.new([v_fl_l[0], v_fl_l[4], v_fl_l[7], v_fl_l[3]]) # outer left
    bm.faces.new([v_fl_l[3], v_fl_l[7], v_fl_l[6], v_fl_l[2]]) # top
    bm.faces.new([v_fl_l[0], v_fl_l[1], v_fl_l[5], v_fl_l[4]]) # bot

    # 5. Right Mounting Flange: X: hx_body .. hx_flange, Y: 0.0 .. th_flange, Z: -hz_body .. +hz_body
    v_fl_r = [
        bm.verts.new((hx_body,   0.0, -hz_body)),
        bm.verts.new((hx_flange, 0.0, -hz_body)),
        bm.verts.new((hx_flange, 0.0,  hz_body)),
        bm.verts.new((hx_body,   0.0,  hz_body)),
        bm.verts.new((hx_body,   th_flange, -hz_body)),
        bm.verts.new((hx_flange, th_flange, -hz_body)),
        bm.verts.new((hx_flange, th_flange,  hz_body)),
        bm.verts.new((hx_body,   th_flange,  hz_body)),
    ]
    bm.faces.new([v_fl_r[4], v_fl_r[5], v_fl_r[6], v_fl_r[7]]) # front
    bm.faces.new([v_fl_r[1], v_fl_r[5], v_fl_r[6], v_fl_r[2]]) # outer right
    bm.faces.new([v_fl_r[3], v_fl_r[2], v_fl_r[6], v_fl_r[7]]) # top
    bm.faces.new([v_fl_r[0], v_fl_r[4], v_fl_r[5], v_fl_r[1]]) # bot

    # 6. Spindle Collar on top at (0.060, 0.032, 0.025 .. 0.032)
    scx, scy = 0.0600, 0.0320
    sr = 0.0125
    z_sp_top = 0.0320
    segs = 8
    v_sp_bot = []
    v_sp_top = []
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        x = scx + sr * math.cos(ang)
        y = scy + sr * math.sin(ang)
        v_sp_bot.append(bm.verts.new((x, y, hz_body)))
        v_sp_top.append(bm.verts.new((x, y, z_sp_top)))

    bm.faces.new(v_sp_top)
    for i in range(segs):
        ni = (i + 1) % segs
        bm.faces.new([v_sp_bot[i], v_sp_bot[ni], v_sp_top[ni], v_sp_top[i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    # UV MAPPING
    fu_min, fu_max = 64.0 / 2048.0, 1984.0 / 2048.0
    fv_min, fv_max = 64.0 / 2048.0, 564.0 / 2048.0

    tu_min, tu_max = 64.0 / 2048.0, 1984.0 / 2048.0
    tv_min, tv_max = 620.0 / 2048.0, 1020.0 / 2048.0

    swatch_u = 200.0 / 2048.0
    swatch_v = 1.0 - (1800.0 / 2048.0)

    # Front face (+Y): SEC-LOK branding & speed valves
    # Looking towards -Y: +X is right, -X is left, +Z is up, -Z is down
    f_front.material_index = 1
    for loop in f_front.loops:
        p = loop.vert.co
        u_norm = (p.x - (-hx_body)) / (2.0 * hx_body)
        u = fu_max - u_norm * (fu_max - fu_min)
        v_norm = (p.z - (-hz_body)) / (2.0 * hz_body)
        v = (1.0 - fv_max) + v_norm * (fv_max - fv_min)
        loop[uv_layer].uv = (u, v)

    # Top face (+Z): Pinion hub and CAUTION text (UN-MIRRORED and upright from front)
    f_top.material_index = 1
    for loop in f_top.loops:
        p = loop.vert.co
        u_norm = (p.x - (-hx_body)) / (2.0 * hx_body)
        u = tu_max - u_norm * (tu_max - tu_min)
        v_norm = (p.y - y_front) / (y_back - y_front)
        v = (1.0 - tv_max) + v_norm * (tv_max - tv_min)
        loop[uv_layer].uv = (u, v)

    # Other faces: metal swatch
    for f in bm.faces:
        if f not in (f_front, f_top):
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_main_arm(mat_metal, mat_atlas):
    """
    Builds the main articulated arm (forged steel beam connecting pinion spindle to elbow joint).
    Local coordinates relative to Arm_Pivot_A.
    Extends from (0, 0, 0) towards elbow at (-0.075, 0.105, 0.004).
    """
    mesh = bpy.data.meshes.new("Main_Arm_Mesh")
    obj = bpy.data.objects.new("Main_Arm", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # Spindle collar at (0, 0)
    segs = 8
    cr = 0.0135
    h_col = 0.0080
    v_col_bot = []
    v_col_top = []
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        x = cr * math.cos(ang)
        y = cr * math.sin(ang)
        v_col_bot.append(bm.verts.new((x, y, 0.0)))
        v_col_top.append(bm.verts.new((x, y, h_col)))

    bm.faces.new(v_col_top)
    for i in range(segs):
        ni = (i + 1) % segs
        bm.faces.new([v_col_bot[i], v_col_bot[ni], v_col_top[ni], v_col_top[i]])

    # Elbow joint at (-0.075, 0.105, 0.004)
    ex, ey, ez = -0.0750, 0.1050, 0.0040
    er = 0.0110
    v_elb_bot = []
    v_elb_top = []
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        x = ex + er * math.cos(ang)
        y = ey + er * math.sin(ang)
        v_elb_bot.append(bm.verts.new((x, y, ez)))
        v_elb_top.append(bm.verts.new((x, y, ez + h_col)))

    bm.faces.new(v_elb_top)
    for i in range(segs):
        ni = (i + 1) % segs
        bm.faces.new([v_elb_bot[i], v_elb_bot[ni], v_elb_top[ni], v_elb_top[i]])

    # Tapered arm blade connecting Spindle to Elbow
    # Normal to direction:
    dx = ex - 0.0
    dy = ey - 0.0
    dist = math.sqrt(dx * dx + dy * dy)
    nx = -dy / dist
    ny =  dx / dist

    w_start = 0.0090 # 18 mm at spindle
    w_end   = 0.0070 # 14 mm at elbow
    z0 = 0.0010
    z1 = 0.0070

    v_blade = [
        bm.verts.new(( 0.0 - nx * w_start,  0.0 - ny * w_start, z0)),
        bm.verts.new((  ex - nx * w_end,    ey - ny * w_end,   ez + z0)),
        bm.verts.new((  ex + nx * w_end,    ey + ny * w_end,   ez + z0)),
        bm.verts.new(( 0.0 + nx * w_start,  0.0 + ny * w_start, z0)),

        bm.verts.new(( 0.0 - nx * w_start,  0.0 - ny * w_start, z1)),
        bm.verts.new((  ex - nx * w_end,    ey - ny * w_end,   ez + z1)),
        bm.verts.new((  ex + nx * w_end,    ey + ny * w_end,   ez + z1)),
        bm.verts.new(( 0.0 + nx * w_start,  0.0 + ny * w_start, z1)),
    ]

    bm.faces.new([v_blade[0], v_blade[1], v_blade[2], v_blade[3]]) # bottom
    f_blade_top = bm.faces.new([v_blade[4], v_blade[7], v_blade[6], v_blade[5]]) # top
    bm.faces.new([v_blade[0], v_blade[4], v_blade[5], v_blade[1]]) # side 1
    bm.faces.new([v_blade[2], v_blade[6], v_blade[7], v_blade[3]]) # side 2

    bm.normal_update()

    # UV Mapping
    au_min, au_max = 64.0 / 2048.0, 1080.0 / 2048.0
    av_min, av_max = 1080.0 / 2048.0, 1580.0 / 2048.0

    f_blade_top.material_index = 1
    for loop in f_blade_top.loops:
        p = loop.vert.co
        proj = (p.x * dx + p.y * dy) / (dist * dist)
        u = au_min + max(0.0, min(1.0, proj)) * (au_max - au_min)
        v = (1.0 - av_max) + 0.5 * (av_max - av_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 200.0 / 2048.0
    swatch_v = 1.0 - (1800.0 / 2048.0)
    for f in bm.faces:
        if f != f_blade_top:
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_link_arm(mat_metal, mat_atlas):
    """
    Builds the secondary link arm and frame shoe bracket.
    Local coordinates relative to Arm_Pivot_B (elbow joint).
    Extends from (0, 0, 0) to frame shoe at (-0.050, -0.127, 0.003).
    """
    mesh = bpy.data.meshes.new("Link_Arm_Mesh")
    obj = bpy.data.objects.new("Link_Arm", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # Elbow knuckle boss at (0, 0, 0)
    segs = 8
    er = 0.0100
    h_knuck = 0.0060
    v_kn_bot = []
    v_kn_top = []
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        x = er * math.cos(ang)
        y = er * math.sin(ang)
        v_kn_bot.append(bm.verts.new((x, y, 0.0)))
        v_kn_top.append(bm.verts.new((x, y, h_knuck)))

    bm.faces.new(v_kn_top)
    for i in range(segs):
        ni = (i + 1) % segs
        bm.faces.new([v_kn_bot[i], v_kn_bot[ni], v_kn_top[ni], v_kn_top[i]])

    # Link rod connecting elbow to frame shoe
    sx, sy, sz = -0.0500, -0.1270, 0.0030
    dx = sx - 0.0
    dy = sy - 0.0
    dist = math.sqrt(dx * dx + dy * dy)
    nx = -dy / dist
    ny =  dx / dist

    w_rod = 0.0060 # 12 mm width
    z0 = 0.0005
    z1 = 0.0055

    v_rod = [
        bm.verts.new(( 0.0 - nx * w_rod,  0.0 - ny * w_rod, z0)),
        bm.verts.new((  sx - nx * w_rod,   sy - ny * w_rod,  sz + z0)),
        bm.verts.new((  sx + nx * w_rod,   sy + ny * w_rod,  sz + z0)),
        bm.verts.new(( 0.0 + nx * w_rod,  0.0 + ny * w_rod, z0)),

        bm.verts.new(( 0.0 - nx * w_rod,  0.0 - ny * w_rod, z1)),
        bm.verts.new((  sx - nx * w_rod,   sy - ny * w_rod,  sz + z1)),
        bm.verts.new((  sx + nx * w_rod,   sy + ny * w_rod,  sz + z1)),
        bm.verts.new(( 0.0 + nx * w_rod,  0.0 + ny * w_rod, z1)),
    ]

    bm.faces.new([v_rod[0], v_rod[1], v_rod[2], v_rod[3]]) # bottom
    f_rod_top = bm.faces.new([v_rod[4], v_rod[7], v_rod[6], v_rod[5]]) # top
    bm.faces.new([v_rod[0], v_rod[4], v_rod[5], v_rod[1]])
    bm.faces.new([v_rod[2], v_rod[6], v_rod[7], v_rod[3]])

    # Frame Shoe Mounting Bracket at (sx, sy, sz)
    # 46 mm length along X, 24 mm width along Y, 6 mm thickness
    hw_shoe = 0.0230 # 46 mm length
    hd_shoe = 0.0120 # 24 mm width
    h_shoe  = 0.0060

    v_shoe = [
        bm.verts.new((sx - hw_shoe, sy - hd_shoe, sz + 0.0010)),
        bm.verts.new((sx + hw_shoe, sy - hd_shoe, sz + 0.0010)),
        bm.verts.new((sx + hw_shoe, sy + hd_shoe, sz + 0.0010)),
        bm.verts.new((sx - hw_shoe, sy + hd_shoe, sz + 0.0010)),
        bm.verts.new((sx - hw_shoe, sy - hd_shoe, sz + 0.0010 + h_shoe)),
        bm.verts.new((sx + hw_shoe, sy - hd_shoe, sz + 0.0010 + h_shoe)),
        bm.verts.new((sx + hw_shoe, sy + hd_shoe, sz + 0.0010 + h_shoe)),
        bm.verts.new((sx - hw_shoe, sy + hd_shoe, sz + 0.0010 + h_shoe)),
    ]

    bm.faces.new([v_shoe[0], v_shoe[1], v_shoe[2], v_shoe[3]]) # bot
    f_shoe_top = bm.faces.new([v_shoe[4], v_shoe[7], v_shoe[6], v_shoe[5]]) # top
    bm.faces.new([v_shoe[0], v_shoe[4], v_shoe[5], v_shoe[1]])
    bm.faces.new([v_shoe[1], v_shoe[5], v_shoe[6], v_shoe[2]])
    bm.faces.new([v_shoe[2], v_shoe[6], v_shoe[7], v_shoe[3]])
    bm.faces.new([v_shoe[3], v_shoe[7], v_shoe[4], v_shoe[0]])

    bm.normal_update()

    # UV Mapping
    au_min, au_max = 64.0 / 2048.0, 1080.0 / 2048.0
    av_min, av_max = 1080.0 / 2048.0, 1580.0 / 2048.0

    ku_min, ku_max = 1140.0 / 2048.0, 1640.0 / 2048.0
    kv_min, kv_max = 1080.0 / 2048.0, 1580.0 / 2048.0

    f_rod_top.material_index = 1
    for loop in f_rod_top.loops:
        p = loop.vert.co
        proj = (p.x * dx + p.y * dy) / (dist * dist)
        u = au_min + max(0.0, min(1.0, proj)) * (au_max - au_min)
        v = (1.0 - av_max) + 0.5 * (av_max - av_min)
        loop[uv_layer].uv = (u, v)

    f_shoe_top.material_index = 1
    for loop in f_shoe_top.loops:
        p = loop.vert.co
        u_norm = (p.x - (sx - hw_shoe)) / (2.0 * hw_shoe)
        u = ku_max - u_norm * (ku_max - ku_min)
        v_norm = (p.y - (sy + hd_shoe)) / (-2.0 * hd_shoe)
        v = (1.0 - kv_max) + v_norm * (kv_max - kv_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 200.0 / 2048.0
    swatch_v = 1.0 - (1800.0 / 2048.0)
    for f in bm.faces:
        if f not in (f_rod_top, f_shoe_top):
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
    root_obj.empty_display_size = 0.05
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_obj)

    # 2. Build Body
    body = build_body(mat_metal, mat_atlas)
    body.parent = root_obj

    # 3. Create Arm_Pivot_A Empty (spindle axis: (0.060, 0.032, 0.032))
    arm_pivot_a = bpy.data.objects.new("Arm_Pivot_A", None)
    arm_pivot_a.empty_display_type = 'PLAIN_AXES'
    arm_pivot_a.empty_display_size = 0.025
    arm_pivot_a.location = Vector((0.0600, 0.0320, 0.0320))
    arm_pivot_a.parent = body
    bpy.context.collection.objects.link(arm_pivot_a)

    arm_pivot_a["limit_min_z"] = -60.0
    arm_pivot_a["limit_max_z"] = 60.0
    c_a = arm_pivot_a.constraints.new(type='LIMIT_ROTATION')
    c_a.use_limit_z = True
    c_a.min_z = math.radians(-60.0)
    c_a.max_z = math.radians(60.0)
    c_a.owner_space = 'LOCAL'

    # 4. Build Main_Arm
    main_arm = build_main_arm(mat_metal, mat_atlas)
    main_arm.parent = arm_pivot_a
    main_arm.location = Vector((0.0, 0.0, 0.0))

    # 5. Create Arm_Pivot_B Empty (elbow axis at (-0.075, 0.105, 0.004) in Main_Arm space)
    arm_pivot_b = bpy.data.objects.new("Arm_Pivot_B", None)
    arm_pivot_b.empty_display_type = 'PLAIN_AXES'
    arm_pivot_b.empty_display_size = 0.020
    arm_pivot_b.location = Vector((-0.0750, 0.1050, 0.0040))
    arm_pivot_b.parent = main_arm
    bpy.context.collection.objects.link(arm_pivot_b)

    arm_pivot_b["limit_min_z"] = -90.0
    arm_pivot_b["limit_max_z"] = 90.0
    c_b = arm_pivot_b.constraints.new(type='LIMIT_ROTATION')
    c_b.use_limit_z = True
    c_b.min_z = math.radians(-90.0)
    c_b.max_z = math.radians(90.0)
    c_b.owner_space = 'LOCAL'

    # 6. Build Link_Arm
    link_arm = build_link_arm(mat_metal, mat_atlas)
    link_arm.parent = arm_pivot_b
    link_arm.location = Vector((0.0, 0.0, 0.0))

    # Mark sharp edges & auto smooth
    for obj in [body, main_arm, link_arm]:
        mesh = obj.data
        for edge in mesh.edges:
            edge.use_edge_sharp = True
        mesh.shade_smooth()

    bpy.context.view_layer.update()

    # Total triangles verification
    total_tris = 0
    mesh_count = 0
    empty_count = 3  # Root, Arm_Pivot_A, Arm_Pivot_B

    for obj in [body, main_arm, link_arm]:
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
    body.select_set(True)
    arm_pivot_a.select_set(True)
    main_arm.select_set(True)
    arm_pivot_b.select_set(True)
    link_arm.select_set(True)
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
