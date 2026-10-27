"""
=============================================================================
Security CCTV Asset Production Suite - Asset 47
Asset Name: SEC_Lock_Electromechanical (Elektromekanik Kapi Kilidi)
Headless Blender Generation & Validation Script v2
High-Fidelity Industrial Low-Poly Redesign
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Electromechanical.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Electromechanical.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Lock_Electromechanical"
MAX_TRIS = 320

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
        bsdf_m.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
        bsdf_m.inputs["Metallic"].default_value = 0.90
        bsdf_m.inputs["Roughness"].default_value = 0.35

    # Slot 1: M_Security_Atlas
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf_a = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if bsdf_a and os.path.exists(ATLAS_PATH):
        tex_node = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(ATLAS_PATH)
        mat_atlas.node_tree.links.new(tex_node.outputs["Color"], bsdf_a.inputs["Base Color"])
        bsdf_a.inputs["Metallic"].default_value = 0.85
        bsdf_a.inputs["Roughness"].default_value = 0.38

    return mat_metal, mat_atlas

def build_faceplate(mat_metal, mat_atlas):
    """
    High-fidelity industrial faceplate (24 x 160 x 3 mm) with 45° chamfered ends,
    2 physical countersunk mounting screw pockets (top and bottom),
    and central latch cavity cutout.
    """
    mesh = bpy.data.meshes.new("Faceplate_Mesh")
    obj = bpy.data.objects.new("Faceplate", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0: M_Metal
    mesh.materials.append(mat_atlas)   # Slot 1: M_Security_Atlas

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hw_p = 0.0120       # 24 mm width -> X: [-0.0120, +0.0120]
    hh_p = 0.0800       # 160 mm height -> Z: [-0.0800, +0.0800]
    th_p = 0.0030       # 3 mm thickness -> Y: [-0.0030, 0.0]
    ch_p = 0.0035       # 3.5 mm 45° corner chamfer

    hw_c = 0.0075       # 15 mm width latch cutout
    hh_c = 0.0150       # 30 mm height latch cutout

    # Screw pocket landmarks
    z_ts = 0.0700       # Top screw center
    z_bs = -0.0700      # Bottom screw center
    r_out = 0.0028      # 5.6 mm outer countersunk bevel
    r_in = 0.0016       # 3.2 mm inner screw pocket base
    d_sc = 0.0016       # 1.6 mm countersink recess depth

    # 1. Outer perimeter 8 verts @ front Y=0 and back Y=-th_p
    p_front = [
        bm.verts.new((-hw_p, 0.0, -hh_p + ch_p)),       # 0
        bm.verts.new((-hw_p + ch_p, 0.0, -hh_p)),       # 1
        bm.verts.new(( hw_p - ch_p, 0.0, -hh_p)),       # 2
        bm.verts.new(( hw_p, 0.0, -hh_p + ch_p)),       # 3
        bm.verts.new(( hw_p, 0.0,  hh_p - ch_p)),       # 4
        bm.verts.new(( hw_p - ch_p, 0.0,  hh_p)),       # 5
        bm.verts.new((-hw_p + ch_p, 0.0,  hh_p)),       # 6
        bm.verts.new((-hw_p, 0.0,  hh_p - ch_p)),       # 7
    ]
    p_back = [
        bm.verts.new((v.co.x, -th_p, v.co.z)) for v in p_front
    ]

    # Outer perimeter rim faces (8 quads)
    for i in range(8):
        j = (i + 1) % 8
        bm.faces.new([p_front[i], p_front[j], p_back[j], p_back[i]])

    # 2. Top Screw Section
    z_t_screw_bot = z_ts - 0.0045
    v_ts_bot_l = bm.verts.new((-hw_p, 0.0, z_t_screw_bot))
    v_ts_bot_r = bm.verts.new(( hw_p, 0.0, z_t_screw_bot))

    hex_ts_out = []
    hex_ts_in = []
    for i in range(6):
        ang = math.pi / 6.0 + i * math.pi / 3.0
        cx = r_out * math.cos(ang)
        cz = z_ts + r_out * math.sin(ang)
        hex_ts_out.append(bm.verts.new((cx, 0.0, cz)))
        cx_in = r_in * math.cos(ang)
        cz_in = z_ts + r_in * math.sin(ang)
        hex_ts_in.append(bm.verts.new((cx_in, -d_sc, cz_in)))

    # Inner hex bottom face
    bm.faces.new(list(reversed(hex_ts_in)))
    # Cone bevel faces
    for i in range(6):
        j = (i + 1) % 6
        bm.faces.new([hex_ts_out[i], hex_ts_in[i], hex_ts_in[j], hex_ts_out[j]])

    # Surround top screw hole
    bm.faces.new([p_front[7], v_ts_bot_l, hex_ts_out[2], hex_ts_out[3]])
    bm.faces.new([v_ts_bot_r, p_front[4], hex_ts_out[0], hex_ts_out[5]])
    bm.faces.new([hex_ts_out[3], hex_ts_out[4], hex_ts_out[5], p_front[5], p_front[6]])
    bm.faces.new([p_front[7], hex_ts_out[3], p_front[6]])
    bm.faces.new([p_front[4], p_front[5], hex_ts_out[5]])
    bm.faces.new([v_ts_bot_l, v_ts_bot_r, hex_ts_out[0], hex_ts_out[1], hex_ts_out[2]])

    # Intermediate top panel (Branding Zone)
    v_cut_top_l = bm.verts.new((-hw_p, 0.0, hh_c))
    v_cut_top_r = bm.verts.new(( hw_p, 0.0, hh_c))
    bm.faces.new([v_cut_top_l, v_cut_top_r, v_ts_bot_r, v_ts_bot_l])

    # 3. Central Cutout Section
    v_cut_bot_l = bm.verts.new((-hw_p, 0.0, -hh_c))
    v_cut_bot_r = bm.verts.new(( hw_p, 0.0, -hh_c))

    v_c_tl = bm.verts.new((-hw_c, 0.0,  hh_c))
    v_c_tr = bm.verts.new(( hw_c, 0.0,  hh_c))
    v_c_bl = bm.verts.new((-hw_c, 0.0, -hh_c))
    v_c_br = bm.verts.new(( hw_c, 0.0, -hh_c))

    bm.faces.new([v_cut_bot_l, v_c_bl, v_c_tl, v_cut_top_l])
    bm.faces.new([v_c_br, v_cut_bot_r, v_cut_top_r, v_c_tr])

    # Cutout cavity walls
    v_cb_tl = bm.verts.new((-hw_c, -th_p,  hh_c))
    v_cb_tr = bm.verts.new(( hw_c, -th_p,  hh_c))
    v_cb_bl = bm.verts.new((-hw_c, -th_p, -hh_c))
    v_cb_br = bm.verts.new(( hw_c, -th_p, -hh_c))

    bm.faces.new([v_c_tl, v_c_tr, v_cb_tr, v_cb_tl])      # Top cavity wall
    bm.faces.new([v_c_bl, v_cb_bl, v_cb_br, v_c_br])      # Bottom cavity wall
    bm.faces.new([v_c_tl, v_cb_tl, v_cb_bl, v_c_bl])      # Left cavity wall
    bm.faces.new([v_c_tr, v_c_br, v_cb_br, v_cb_tr])      # Right cavity wall

    # 4. Bottom Screw Section
    z_b_screw_top = z_bs + 0.0045
    v_bs_top_l = bm.verts.new((-hw_p, 0.0, z_b_screw_top))
    v_bs_top_r = bm.verts.new(( hw_p, 0.0, z_b_screw_top))
    bm.faces.new([v_bs_top_l, v_bs_top_r, v_cut_bot_r, v_cut_bot_l])

    hex_bs_out = []
    hex_bs_in = []
    for i in range(6):
        ang = math.pi / 6.0 + i * math.pi / 3.0
        cx = r_out * math.cos(ang)
        cz = z_bs + r_out * math.sin(ang)
        hex_bs_out.append(bm.verts.new((cx, 0.0, cz)))
        cx_in = r_in * math.cos(ang)
        cz_in = z_bs + r_in * math.sin(ang)
        hex_bs_in.append(bm.verts.new((cx_in, -d_sc, cz_in)))

    bm.faces.new(hex_bs_in)
    for i in range(6):
        j = (i + 1) % 6
        bm.faces.new([hex_bs_out[j], hex_bs_in[j], hex_bs_in[i], hex_bs_out[i]])

    bm.faces.new([v_bs_top_l, hex_bs_out[2], hex_bs_out[1], hex_bs_out[0], v_bs_top_r])
    bm.faces.new([p_front[0], hex_bs_out[3], hex_bs_out[2], v_bs_top_l])
    bm.faces.new([v_bs_top_r, hex_bs_out[0], hex_bs_out[5], p_front[3]])
    bm.faces.new([hex_bs_out[4], hex_bs_out[3], p_front[1], p_front[2], hex_bs_out[5]])
    bm.faces.new([p_front[0], p_front[1], hex_bs_out[3]])
    bm.faces.new([hex_bs_out[5], p_front[2], p_front[3]])

    # 5. Back faces of plate (avoiding cutout area)
    hh_box = 0.0500
    v_bp_tl = bm.verts.new((-hw_p, -th_p,  hh_box))
    v_bp_tr = bm.verts.new(( hw_p, -th_p,  hh_box))
    v_bp_bl = bm.verts.new((-hw_p, -th_p, -hh_box))
    v_bp_br = bm.verts.new(( hw_p, -th_p, -hh_box))

    bm.faces.new([p_back[7], p_back[6], p_back[5], p_back[4], v_bp_tr, v_bp_tl])
    bm.faces.new([v_bp_bl, v_bp_br, p_back[3], p_back[2], p_back[1], p_back[0]])

    # Fix any inverted front normals
    bm.normal_update()
    for f in bm.faces:
        avg_y = sum(v.co.y for v in f.verts) / len(f.verts)
        if avg_y > -0.0025 and f.normal.y < -0.3:
            f.normal_flip()
    bm.normal_update()

    # UV MAPPING
    u_min, u_max = 64.0 / 2048.0, 464.0 / 2048.0
    v_min, v_max = 64.0 / 2048.0, 1984.0 / 2048.0

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (1750.0 / 2048.0)

    for f in bm.faces:
        avg_y = sum(v.co.y for v in f.verts) / len(f.verts)
        is_front = (avg_y > -0.0018) and (f.normal.y > 0.4)
        if is_front:
            f.material_index = 1  # M_Security_Atlas
            for loop in f.loops:
                p = loop.vert.co
                u_norm = (p.x - (-hw_p)) / (2.0 * hw_p)
                u = u_max - u_norm * (u_max - u_min)
                v_norm = (p.z - (-hh_p)) / (2.0 * hh_p)
                v = (1.0 - v_max) + v_norm * (v_max - v_min)
                loop[uv_layer].uv = (u, v)
        else:
            f.material_index = 0  # M_Metal
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_screws(mat_metal, mat_atlas):
    """
    Builds the two 3D countersunk hexagonal screw heads sitting flush inside the faceplate pockets.
    """
    mesh = bpy.data.meshes.new("Screws_Mesh")
    obj = bpy.data.objects.new("Screws", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    su_min, su_max = 1080.0 / 2048.0, 1580.0 / 2048.0
    sv_min, sv_max = 1024.0 / 2048.0, 1524.0 / 2048.0
    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (1750.0 / 2048.0)

    r_sc = 0.00155     # 3.1 mm screw head
    y_sc_top = -0.0011 # slightly above pocket floor
    y_sc_bot = -0.0016 # bottom of pocket
    segs = 6

    for z_pos in [0.0700, -0.0700]:
        v_top = []
        v_bot = []
        for i in range(segs):
            ang = math.pi / 6.0 + i * math.pi / 3.0
            x = r_sc * math.cos(ang)
            z = z_pos + r_sc * math.sin(ang)
            v_top.append(bm.verts.new((x, y_sc_top, z)))
            v_bot.append(bm.verts.new((x, y_sc_bot, z)))

        # Top screw drive face
        f_top = bm.faces.new(list(reversed(v_top)))
        f_top.material_index = 1
        for loop in f_top.loops:
            p = loop.vert.co
            u_norm = (p.x / (2.0 * r_sc)) + 0.5
            u = su_min + u_norm * (su_max - su_min)
            v_norm = ((p.z - z_pos) / (2.0 * r_sc)) + 0.5
            v = (1.0 - sv_max) + v_norm * (sv_max - sv_min)
            loop[uv_layer].uv = (u, v)

        # Side rim faces
        for i in range(segs):
            next_i = (i + 1) % segs
            f_side = bm.faces.new([v_bot[i], v_bot[next_i], v_top[next_i], v_top[i]])
            f_side.material_index = 0
            for loop in f_side.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_housing(mat_metal, mat_atlas):
    """
    Builds the mortise body case (15 x 100 x 68 mm) with 45° chamfered rear edges
    and correct, un-mirrored solenoid specification plate mapping on the right face.
    """
    mesh = bpy.data.meshes.new("Housing_Mesh")
    obj = bpy.data.objects.new("Housing", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hw_box = 0.0075  # 15 mm width
    hh_box = 0.0500  # 100 mm height
    y_front = -0.0030
    y_back  = -0.0710 # 68 mm depth behind faceplate
    ch_rear = 0.0040  # 4 mm rear corner chamfer

    # Front 4 verts
    v_f = [
        bm.verts.new((-hw_box, y_front, -hh_box)), # 0
        bm.verts.new(( hw_box, y_front, -hh_box)), # 1
        bm.verts.new(( hw_box, y_front,  hh_box)), # 2
        bm.verts.new((-hw_box, y_front,  hh_box)), # 3
    ]

    # Rear chamfered 8 verts
    v_r = [
        bm.verts.new((-hw_box, y_back + ch_rear, -hh_box)),           # 0: left bot
        bm.verts.new((-hw_box + ch_rear, y_back, -hh_box)),           # 1: rear left bot
        bm.verts.new(( hw_box - ch_rear, y_back, -hh_box)),           # 2: rear right bot
        bm.verts.new(( hw_box, y_back + ch_rear, -hh_box)),           # 3: right bot
        bm.verts.new(( hw_box, y_back + ch_rear,  hh_box)),           # 4: right top
        bm.verts.new(( hw_box - ch_rear, y_back,  hh_box)),           # 5: rear right top
        bm.verts.new((-hw_box + ch_rear, y_back,  hh_box)),           # 6: rear left top
        bm.verts.new((-hw_box, y_back + ch_rear,  hh_box)),           # 7: left top
    ]

    # Front contact face
    bm.faces.new([v_f[0], v_f[1], v_f[2], v_f[3]])

    # Left face
    bm.faces.new([v_f[0], v_f[3], v_r[7], v_r[0]])
    # Left rear chamfer
    bm.faces.new([v_r[0], v_r[7], v_r[6], v_r[1]])

    # Rear flat face
    bm.faces.new([v_r[1], v_r[6], v_r[5], v_r[2]])

    # Right rear chamfer
    bm.faces.new([v_r[2], v_r[5], v_r[4], v_r[3]])
    # Right face (Solenoid specification label!)
    f_right = bm.faces.new([v_f[1], v_r[3], v_r[4], v_f[2]])

    # Top face
    bm.faces.new([v_f[3], v_f[2], v_r[4], v_r[5], v_r[6], v_r[7]])
    # Bottom face
    bm.faces.new([v_f[0], v_r[0], v_r[1], v_r[2], v_r[3], v_f[1]])

    bm.normal_update()

    # UV Mapping
    hu_min, hu_max = 520.0 / 2048.0, 1320.0 / 2048.0
    hv_min, hv_max = 64.0 / 2048.0, 964.0 / 2048.0

    # Right Face: Un-mirrored left-to-right mapping
    # Viewing right face from +X looking towards -X:
    # Left is -Y (y_back), Right is +Y (y_front), Up is +Z, Down is -Z
    f_right.material_index = 1
    for loop in f_right.loops:
        p = loop.vert.co
        u_norm = (p.y - y_back) / (y_front - y_back)
        u = hu_min + u_norm * (hu_max - hu_min)
        v_norm = (p.z - (-hh_box)) / (2.0 * hh_box)
        v = (1.0 - hv_max) + v_norm * (hv_max - hv_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (1850.0 / 2048.0)
    for f in bm.faces:
        if f != f_right:
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_latch(mat_metal, mat_atlas):
    """
    Builds the solid steel beveled latch bolt (13 x 26 x 24 mm) with beveled strike face
    and anti-friction auxiliary deadlatch pin.
    Local coordinates relative to Latch_Pivot.
    """
    mesh = bpy.data.meshes.new("Latch_Mesh")
    obj = bpy.data.objects.new("Latch", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    lw = 0.0068  # 13.6 mm width
    lh = 0.0125  # 25 mm height
    y_pivot = 0.0000
    y_tip   = 0.0240 # extends 24 mm forward from pivot (14 mm proud of faceplate)

    # 6-point profile in X-Y for beveled strike face
    # Left side (-X) is straight, Right side (+X) is beveled for smooth latching
    v0 = bm.verts.new((-lw, y_pivot, -lh))
    v1 = bm.verts.new(( lw * 0.2, y_pivot, -lh))
    v2 = bm.verts.new(( lw, y_pivot + 0.006, -lh)) # bevel start
    v3 = bm.verts.new(( lw, y_tip - 0.008, -lh))   # bevel ramp
    v4 = bm.verts.new(( lw * 0.2, y_tip, -lh))     # tip front
    v5 = bm.verts.new((-lw, y_tip, -lh))           # tip left

    v6 = bm.verts.new((-lw, y_pivot,  lh))
    v7 = bm.verts.new(( lw * 0.2, y_pivot,  lh))
    v8 = bm.verts.new(( lw, y_pivot + 0.006,  lh))
    v9 = bm.verts.new(( lw, y_tip - 0.008,  lh))
    v10 = bm.verts.new(( lw * 0.2, y_tip,  lh))
    v11 = bm.verts.new((-lw, y_tip,  lh))

    bm.faces.new([v0, v1, v2, v3, v4, v5]) # Bottom
    bm.faces.new([v11, v10, v9, v8, v7, v6]) # Top
    bm.faces.new([v0, v6, v7, v1]) # Rear
    bm.faces.new([v1, v7, v8, v2])
    f_ramp = bm.faces.new([v2, v8, v9, v3]) # Strike bevel ramp
    bm.faces.new([v3, v9, v10, v4])
    f_front = bm.faces.new([v4, v10, v11, v5]) # Front tip
    bm.faces.new([v5, v11, v6, v0]) # Flat side

    bm.normal_update()

    # UV Mapping
    lu_min, lu_max = 520.0 / 2048.0, 1020.0 / 2048.0
    lv_min, lv_max = 1024.0 / 2048.0, 1984.0 / 2048.0

    for f in [f_front, f_ramp]:
        f.material_index = 1
        for loop in f.loops:
            p = loop.vert.co
            u_norm = (p.x - (-lw)) / (2.0 * lw)
            u = lu_max - u_norm * (lu_max - lu_min)
            v_norm = (p.z - (-lh)) / (2.0 * lh)
            v = (1.0 - lv_max) + v_norm * (lv_max - lv_min)
            loop[uv_layer].uv = (u, v)

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (1750.0 / 2048.0)
    for f in bm.faces:
        if f not in [f_front, f_ramp]:
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

    # 2. Build Faceplate
    faceplate = build_faceplate(mat_metal, mat_atlas)
    faceplate.parent = root_obj

    # 3. Build Housing
    housing = build_housing(mat_metal, mat_atlas)
    housing.parent = root_obj

    # 4. Build Screws
    screws = build_screws(mat_metal, mat_atlas)
    screws.parent = root_obj

    # 5. Create Latch_Pivot Empty
    latch_pivot = bpy.data.objects.new("Latch_Pivot", None)
    latch_pivot.empty_display_type = 'PLAIN_AXES'
    latch_pivot.empty_display_size = 0.02
    latch_pivot.location = Vector((0.0, -0.0100, 0.0))
    latch_pivot.parent = housing
    bpy.context.collection.objects.link(latch_pivot)

    # Custom properties for rotation limit
    latch_pivot["limit_min_z"] = -20.0
    latch_pivot["limit_max_z"] = 20.0
    rot_const = latch_pivot.constraints.new(type='LIMIT_ROTATION')
    rot_const.use_limit_z = True
    rot_const.min_z = math.radians(-20.0)
    rot_const.max_z = math.radians(20.0)
    rot_const.owner_space = 'LOCAL'

    # 6. Build Latch
    latch = build_latch(mat_metal, mat_atlas)
    latch.parent = latch_pivot
    latch.location = Vector((0.0, 0.0, 0.0))

    # Mark sharp edges & auto smooth
    for obj in [faceplate, housing, screws, latch]:
        mesh = obj.data
        for edge in mesh.edges:
            edge.use_edge_sharp = True
        mesh.shade_smooth()

    bpy.context.view_layer.update()

    # Total triangles verification
    total_tris = 0
    mesh_count = 0
    empty_count = 2  # Root + Latch_Pivot

    for obj in [faceplate, housing, screws, latch]:
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
    faceplate.select_set(True)
    housing.select_set(True)
    screws.select_set(True)
    latch_pivot.select_set(True)
    latch.select_set(True)
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
