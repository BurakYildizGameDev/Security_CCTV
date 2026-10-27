"""
=============================================================================
Security CCTV Asset Production Suite - Asset 46
Asset Name: SEC_Lock_Electric_Strike (Elektrikli Kapi Karsiligi)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Electric_Strike.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Electric_Strike.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Lock_Electric_Strike"
MAX_TRIS = 300

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

def build_strike_housing(mat_metal, mat_atlas):
    """
    High-fidelity industrial faceplate (25 x 160 x 3 mm) with 45° chamfered ends,
    2 physical countersunk mounting screw holes (top and bottom),
    central latch cavity, and chamfered mortise solenoid box.
    """
    mesh = bpy.data.meshes.new("Strike_Housing_Mesh")
    obj = bpy.data.objects.new("Strike_Housing", mesh)
    bpy.context.collection.objects.link(obj)

    # Append materials first
    mesh.materials.append(mat_metal)   # Slot 0: M_Metal
    mesh.materials.append(mat_atlas)   # Slot 1: M_Security_Atlas

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hw_p = 0.0125       # 25 mm width -> X: [-0.0125, +0.0125]
    hh_p = 0.0800       # 160 mm height -> Z: [-0.0800, +0.0800]
    th_p = 0.0030       # 3 mm thickness -> Y: [-0.0030, 0.0]
    ch_p = 0.0035       # 3.5 mm 45° corner chamfer

    hw_c = 0.0080       # 16 mm width latch cutout
    hh_c = 0.0220       # 44 mm height latch cutout
    d_cav = 0.0200      # 20 mm cavity depth behind cutout

    hw_b = 0.0105       # 21 mm width mortise box
    hh_b = 0.0380       # 76 mm height mortise box
    d_b  = 0.0270       # 27 mm mortise box depth

    # Screw landmarks
    z_ts = 0.0708       # Top screw center
    z_bs = -0.0708      # Bottom screw center
    r_out = 0.0028      # 5.6 mm outer countersunk bevel
    r_in = 0.0016       # 3.2 mm inner screw head
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

    # Inner hex bottom face (screw drive face)
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

    # Intermediate top panel
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

    # 5. Internal latch cavity walls
    v_cav_tl = bm.verts.new((-hw_c, -d_cav,  hh_c))
    v_cav_tr = bm.verts.new(( hw_c, -d_cav,  hh_c))
    v_cav_bl = bm.verts.new((-hw_c, -d_cav, -hh_c))
    v_cav_br = bm.verts.new(( hw_c, -d_cav, -hh_c))

    bm.faces.new([v_c_tl, v_c_tr, v_cav_tr, v_cav_tl])      # Top cavity wall
    bm.faces.new([v_c_bl, v_cav_bl, v_cav_br, v_c_br])      # Bottom cavity wall
    bm.faces.new([v_c_tl, v_cav_tl, v_cav_bl, v_c_bl])      # Left cavity wall
    bm.faces.new([v_cav_tl, v_cav_tr, v_cav_br, v_cav_bl])  # Back cavity wall

    # 6. Mortise housing box behind plate with chamfered rear edges
    ch_b = 0.0030
    v_box = [
        bm.verts.new((-hw_b, -th_p, -hh_b)),
        bm.verts.new(( hw_b, -th_p, -hh_b)),
        bm.verts.new(( hw_b, -th_p,  hh_b)),
        bm.verts.new((-hw_b, -th_p,  hh_b)),
        # Rear 8 verts
        bm.verts.new((-hw_b, -d_b + ch_b, -hh_b)),
        bm.verts.new((-hw_b + ch_b, -d_b, -hh_b)),
        bm.verts.new(( hw_b - ch_b, -d_b, -hh_b)),
        bm.verts.new(( hw_b, -d_b + ch_b, -hh_b)),
        bm.verts.new(( hw_b, -d_b + ch_b,  hh_b)),
        bm.verts.new(( hw_b - ch_b, -d_b,  hh_b)),
        bm.verts.new((-hw_b + ch_b, -d_b,  hh_b)),
        bm.verts.new((-hw_b, -d_b + ch_b,  hh_b)),
    ]
    bm.faces.new([v_box[5], v_box[6], v_box[9], v_box[10]])  # Rear wall
    bm.faces.new([v_box[4], v_box[5], v_box[10], v_box[11]]) # Rear chamfer left
    bm.faces.new([v_box[6], v_box[7], v_box[8], v_box[9]])   # Rear chamfer right
    f_box_left  = bm.faces.new([v_box[0], v_box[3], v_box[11], v_box[4]])  # Left
    f_box_right = bm.faces.new([v_box[1], v_box[7], v_box[8], v_box[2]])   # Right (Spec Label)
    bm.faces.new([v_box[3], v_box[2], v_box[8], v_box[9], v_box[10], v_box[11]]) # Top
    bm.faces.new([v_box[0], v_box[4], v_box[5], v_box[6], v_box[7], v_box[1]])   # Bot

    # 7. Back face of plate
    v_bp_tl = bm.verts.new((-hw_p, -th_p,  hh_b))
    v_bp_tr = bm.verts.new(( hw_p, -th_p,  hh_b))
    v_bp_bl = bm.verts.new((-hw_p, -th_p, -hh_b))
    v_bp_br = bm.verts.new(( hw_p, -th_p, -hh_b))

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

    # Front-facing faces map to REGION_FACEPLATE
    for f in bm.faces:
        if f.normal.y > 0.4:
            f.material_index = 1  # M_Security_Atlas
            for loop in f.loops:
                p = loop.vert.co
                u_norm = (p.x - (-hw_p)) / (2.0 * hw_p)
                u = u_max - u_norm * (u_max - u_min)
                v_norm = (p.z - (-hh_p)) / (2.0 * hh_p)
                v = (1.0 - v_max) + v_norm * (v_max - v_min)
                loop[uv_layer].uv = (u, v)

    # Right side of mortise box maps to REGION_HOUSING_SIDE
    hu_min, hu_max = 520.0 / 2048.0, 1320.0 / 2048.0
    hv_min, hv_max = 64.0 / 2048.0, 964.0 / 2048.0
    f_box_right.material_index = 1
    for loop in f_box_right.loops:
        p = loop.vert.co
        u_norm = (p.y - (-th_p)) / ((-d_b) - (-th_p))
        u = hu_min + u_norm * (hu_max - hu_min)
        v_norm = (p.z - (-hh_b)) / (2.0 * hh_b)
        v = (1.0 - hv_max) + v_norm * (hv_max - hv_min)
        loop[uv_layer].uv = (u, v)

    # Swatch fill for all other faces (cut edges, cavity, bevels)
    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (1750.0 / 2048.0)
    for f in bm.faces:
        if f.material_index != 1:
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_keeper_plate(mat_metal, mat_atlas):
    """
    Sculpted mechanical keeper jaw inside the cutout opening.
    Features curved door latch strike ramp, locking lip, and top/bottom hinge pivot lugs.
    """
    mesh = bpy.data.meshes.new("Keeper_Plate_Mesh")
    obj = bpy.data.objects.new("Keeper_Plate", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0: M_Metal
    mesh.materials.append(mat_atlas)   # Slot 1: M_Security_Atlas

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    kw_l = -0.0075
    kw_ramp = 0.0010
    kw_r = 0.0070

    y_f = -0.0025
    y_ramp = -0.0120
    y_b = -0.0180

    kh = 0.0200

    prof = [
        (kw_l, y_f),
        (kw_ramp, y_f),
        (kw_r, y_ramp),
        (kw_r, y_b),
        (kw_l, y_b),
    ]

    rings = [
        [bm.verts.new((p[0], p[1], zz)) for p in prof]
        for zz in (-kh, kh)
    ]

    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[1])

    f_front = bm.faces.new([rings[0][0], rings[0][1], rings[1][1], rings[1][0]])
    f_ramp  = bm.faces.new([rings[0][1], rings[0][2], rings[1][2], rings[1][1]])
    f_right = bm.faces.new([rings[0][2], rings[0][3], rings[1][3], rings[1][2]])
    f_back  = bm.faces.new([rings[0][3], rings[0][4], rings[1][4], rings[1][3]])
    f_left  = bm.faces.new([rings[0][4], rings[0][0], rings[1][0], rings[1][4]])

    # Top & bottom cylindrical hinge pivot lugs
    lug_r = 0.0018
    lug_cx = -0.0040
    lug_cy = -0.0100
    lug_h = 0.0018

    for sign in (1, -1):
        z_base = sign * kh
        z_top = sign * (kh + lug_h)
        base_v = []
        top_v = []
        for i in range(6):
            ang = i * math.pi / 3.0
            x = lug_cx + lug_r * math.cos(ang)
            y = lug_cy + lug_r * math.sin(ang)
            base_v.append(bm.verts.new((x, y, z_base)))
            top_v.append(bm.verts.new((x, y, z_top)))
        if sign == 1:
            bm.faces.new(top_v)
            for i in range(6):
                j = (i + 1) % 6
                bm.faces.new([base_v[i], base_v[j], top_v[j], top_v[i]])
        else:
            bm.faces.new(list(reversed(top_v)))
            for i in range(6):
                j = (i + 1) % 6
                bm.faces.new([base_v[j], base_v[i], top_v[i], top_v[j]])

    # UV Mapping
    ku_min, ku_max = 520.0 / 2048.0, 1020.0 / 2048.0
    kv_min, kv_max = 1024.0 / 2048.0, 1984.0 / 2048.0

    for f in (f_front, f_ramp):
        f.material_index = 1
        for loop in f.loops:
            p = loop.vert.co
            u_norm = (p.x - kw_l) / (kw_r - kw_l)
            u = ku_min + u_norm * (ku_max - ku_min)
            v_norm = (p.z - (-kh)) / (2.0 * kh)
            v = (1.0 - kv_max) + v_norm * (kv_max - kv_min)
            loop[uv_layer].uv = (u, v)

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (1750.0 / 2048.0)
    for f in bm.faces:
        if f not in (f_front, f_ramp):
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_terminal_cover(mat_metal, mat_atlas):
    """
    Connection block on top rear of mortise box with 2 clamping terminals.
    """
    mesh = bpy.data.meshes.new("Terminal_Cover_Mesh")
    obj = bpy.data.objects.new("Terminal_Cover", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.materials.append(mat_metal)   # Slot 0: M_Metal
    mesh.materials.append(mat_atlas)   # Slot 1: M_Security_Atlas

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    tw = 0.0080
    th_bot = 0.0380
    th_top = 0.0540
    y_f = -0.0230
    y_b = -0.0290

    v = [
        bm.verts.new((-tw, y_f, th_bot)),
        bm.verts.new(( tw, y_f, th_bot)),
        bm.verts.new(( tw, y_f, th_top)),
        bm.verts.new((-tw, y_f, th_top)),
        bm.verts.new((-tw, y_b, th_bot)),
        bm.verts.new(( tw, y_b, th_bot)),
        bm.verts.new(( tw, y_b, th_top)),
        bm.verts.new((-tw, y_b, th_top)),
    ]
    bm.faces.new([v[0], v[1], v[2], v[3]]) # front
    f_back  = bm.faces.new([v[5], v[4], v[7], v[6]]) # back
    bm.faces.new([v[4], v[0], v[3], v[7]]) # left
    bm.faces.new([v[1], v[5], v[6], v[2]]) # right
    bm.faces.new([v[3], v[2], v[6], v[7]]) # top
    bm.faces.new([v[0], v[4], v[5], v[1]]) # bot

    # UV Mapping
    tu_min, tu_max = 1080.0 / 2048.0, 1580.0 / 2048.0
    tv_min, tv_max = 1024.0 / 2048.0, 1524.0 / 2048.0

    f_back.material_index = 1
    for loop in f_back.loops:
        p = loop.vert.co
        u_norm = (p.x - (-tw)) / (2.0 * tw)
        u = tu_min + u_norm * (tu_max - tu_min)
        v_norm = (p.z - th_bot) / (th_top - th_bot)
        v = (1.0 - tv_max) + v_norm * (tv_max - tv_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 1850.0 / 2048.0
    swatch_v = 1.0 - (1850.0 / 2048.0)
    for f in bm.faces:
        if f != f_back:
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

    root_obj = bpy.data.objects.new(ASSET_NAME, None)
    root_obj.empty_display_type = 'ARROWS'
    root_obj.empty_display_size = 0.05
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_obj)

    housing = build_strike_housing(mat_metal, mat_atlas)
    housing.parent = root_obj

    keeper = build_keeper_plate(mat_metal, mat_atlas)
    keeper.parent = root_obj

    terminal = build_terminal_cover(mat_metal, mat_atlas)
    terminal.parent = root_obj

    for obj in [housing, keeper, terminal]:
        obj.location = Vector((0.0, 0.0, 0.0))
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)

    bpy.context.view_layer.update()

    t_housing = count_triangles(housing)
    t_keeper = count_triangles(keeper)
    t_terminal = count_triangles(terminal)
    total_tris = t_housing + t_keeper + t_terminal

    print(f"\n[POLYCOUNT] Strike_Housing: {t_housing} tris")
    print(f"[POLYCOUNT] Keeper_Plate: {t_keeper} tris")
    print(f"[POLYCOUNT] Terminal_Cover: {t_terminal} tris")
    print(f"[POLYCOUNT] TOTAL: {total_tris} tris (Budget: <= {MAX_TRIS})")
    assert total_tris <= MAX_TRIS, f"Total tris {total_tris} exceeds budget {MAX_TRIS}!"

    # Save .blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"[OK] Saved .blend to {BLEND_PATH}")

    # Export FBX
    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    for child in root_obj.children:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    bpy.ops.export_scene.fbx(
        filepath=FBX_PATH,
        use_selection=True,
        object_types={'EMPTY', 'MESH'},
        mesh_smooth_type='FACE',
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=False
    )
    print(f"[OK] Exported FBX to {FBX_PATH}")

    # Re-import verification
    print("\n--- RUNNING HEADLESS FBX VERIFICATION ---")
    reset_scene()
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)

    re_root = bpy.data.objects.get(ASSET_NAME)
    assert re_root is not None, f"Root {ASSET_NAME} missing from imported FBX!"
    assert re_root.type == 'EMPTY', f"Root is not an EMPTY!"

    meshes = [c for c in re_root.children if c.type == 'MESH']
    assert len(meshes) == 3, f"Expected 3 meshes, got {len(meshes)}"

    re_total_tris = 0
    for m in meshes:
        bm = bmesh.new()
        bm.from_mesh(m.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        t = len(bm.faces)
        re_total_tris += t
        bm.free()
        assert len(m.data.uv_layers) > 0, f"Mesh {m.name} is missing UVMap!"
        print(f"       -> {m.name}: {t} tris")

    print(f"[QA] FBX Total Triangles: {re_total_tris} (budget <= {MAX_TRIS})")
    assert re_total_tris <= MAX_TRIS, "FBX triangle count exceeds budget!"

    manifest = {
        "asset_name": ASSET_NAME,
        "category": "Electronic Hardware / Access Control Locks",
        "description": "ANSI standard heavy-duty electric door strike with countersunk mounting screw pockets, latch guide ramp, and mortise casing",
        "target_tris": MAX_TRIS,
        "actual_tris": re_total_tris,
        "meshes": [m.name for m in meshes],
        "materials": ["M_Metal", "M_Security_Atlas"],
        "export_fbx": "exports/SEC_Lock_Electric_Strike.fbx",
        "export_blend": "exports/SEC_Lock_Electric_Strike.blend",
        "qa_status": "PASSED"
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print(f"[OK] Updated manifest: {MANIFEST_PATH}")

    # Cleanup .blend1
    blend1_path = BLEND_PATH + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[CLEAN] Removed {blend1_path}")

    print("\n[SUCCESS] Asset 46 generation & verification completed successfully!")

if __name__ == "__main__":
    generate_asset()
