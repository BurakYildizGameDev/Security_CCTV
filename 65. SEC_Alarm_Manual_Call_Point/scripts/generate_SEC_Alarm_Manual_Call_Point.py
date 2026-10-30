"""
Security CCTV Asset Production Suite - Asset 65
Asset Name: SEC_Alarm_Manual_Call_Point (Manual Fire Alarm Break-Glass Call Point)
Generator Script for Blender CLI
"""

import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Euler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Manual_Call_Point.blend")
FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Manual_Call_Point.fbx")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")

MAX_TRIS = 300

def create_materials():
    materials = {}

    # 1. M_Security_Atlas (Slot 0)
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if os.path.exists(ATLAS_PATH):
        tex_node = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        img = bpy.data.images.load(ATLAS_PATH)
        tex_node.image = img
        mat_atlas.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.35
    mat_atlas.diffuse_color = (0.78, 0.10, 0.12, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. M_Transparent (Slot 1)
    mat_trans = bpy.data.materials.new(name="M_Transparent")
    mat_trans.use_nodes = True
    bsdf_tr = mat_trans.node_tree.nodes.get("Principled BSDF")
    if os.path.exists(ATLAS_PATH):
        tex_tr = mat_trans.node_tree.nodes.new("ShaderNodeTexImage")
        tex_tr.image = bpy.data.images.get(os.path.basename(ATLAS_PATH)) or bpy.data.images.load(ATLAS_PATH)
        mat_trans.node_tree.links.new(tex_tr.outputs["Color"], bsdf_tr.inputs["Base Color"])
    else:
        bsdf_tr.inputs["Base Color"].default_value = (0.92, 0.95, 1.0, 1.0)
    bsdf_tr.inputs["Roughness"].default_value = 0.05
    if "Transmission Weight" in bsdf_tr.inputs:
        bsdf_tr.inputs["Transmission Weight"].default_value = 0.85
    if "Alpha" in bsdf_tr.inputs:
        bsdf_tr.inputs["Alpha"].default_value = 0.40
    if "IOR" in bsdf_tr.inputs:
        bsdf_tr.inputs["IOR"].default_value = 1.49
    mat_trans.blend_method = 'BLEND'
    mat_trans.diffuse_color = (0.85, 0.90, 0.98, 0.40)
    materials["M_Transparent"] = mat_trans

    # 3. M_Emission (Slot 2)
    mat_emit = bpy.data.materials.new(name="M_Emission")
    mat_emit.use_nodes = True
    bsdf_emit = mat_emit.node_tree.nodes.get("Principled BSDF")
    bsdf_emit.inputs["Base Color"].default_value = (1.0, 0.15, 0.15, 1.0)
    bsdf_emit.inputs["Emission Color"].default_value = (1.0, 0.15, 0.15, 1.0)
    bsdf_emit.inputs["Emission Strength"].default_value = 8.0
    mat_emit.diffuse_color = (1.0, 0.15, 0.15, 1.0)
    materials["M_Emission"] = mat_emit

    return materials

def assign_material_slots(obj, mat_dict):
    slot_order = ["M_Security_Atlas", "M_Transparent", "M_Emission"]
    for mat_name in slot_order:
        obj.data.materials.append(mat_dict[mat_name])

def set_face_uv_rect(bm, face, uv_rect):
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv_rect
    xs = [l.vert.co.x for l in face.loops]
    zs = [l.vert.co.z for l in face.loops]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    dx = max_x - min_x if max_x > min_x else 1e-5
    dz = max_z - min_z if max_z > min_z else 1e-5
    for l in face.loops:
        # Looking from +Y (front), +X is screen-left, -X is screen-right.
        # Texture u increases from left to right, so tx must be inverted:
        tx = (max_x - l.vert.co.x) / dx
        tz = (l.vert.co.z - min_z) / dz
        l[uv_layer].uv = (u0 + tx * (u1 - u0), v0 + tz * (v1 - v0))

def set_face_uv_constant(bm, face, uv_point):
    uv_layer = bm.loops.layers.uv.verify()
    for l in face.loops:
        l[uv_layer].uv = uv_point

def mark_sharp_edges(bm):
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            ang = edge.calc_face_angle()
            if ang > math.radians(35.0):
                edge.smooth = False
            else:
                edge.smooth = True
        else:
            edge.smooth = False

def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    materials = create_materials()

    # Root Empty: SEC_Alarm_Manual_Call_Point at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Alarm_Manual_Call_Point", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.10
    bpy.context.collection.objects.link(root)

    uv_swatch_red    = (250 / 2048.0, 1.0 - 1850 / 2048.0)
    uv_swatch_white  = (750 / 2048.0, 1.0 - 1850 / 2048.0)
    uv_swatch_yellow = (1250 / 2048.0, 1.0 - 1850 / 2048.0)
    uv_swatch_pocket = (1750 / 2048.0, 1.0 - 1850 / 2048.0)

    # -------------------------------------------------------------------------
    # 1. HOUSING (Mesh - Child of Root)
    # 88mm x 88mm casing with recessed pocket:
    # Outer box: X: -0.044 to 0.044, Z: -0.044 to 0.044, Y: 0.000 to 0.032
    # Recessed pocket: X: -0.030 to 0.030, Z: -0.024 to 0.020, Y: 0.022 to 0.032
    # -------------------------------------------------------------------------
    h_me = bpy.data.meshes.new("Housing")
    h_bm = bmesh.new()

    hx0, hx1 = -0.044, 0.044
    hz0, hz1 = -0.044, 0.044
    hy_back = 0.000
    hy_front = 0.032

    # Outer box vertices
    vb0 = h_bm.verts.new((hx0, hy_back, hz0))
    vb1 = h_bm.verts.new((hx1, hy_back, hz0))
    vb2 = h_bm.verts.new((hx1, hy_back, hz1))
    vb3 = h_bm.verts.new((hx0, hy_back, hz1))

    vf0 = h_bm.verts.new((hx0, hy_front, hz0))
    vf1 = h_bm.verts.new((hx1, hy_front, hz0))
    vf2 = h_bm.verts.new((hx1, hy_front, hz1))
    vf3 = h_bm.verts.new((hx0, hy_front, hz1))

    # Back face (M_Security_Atlas - Rear spec label)
    f_back = h_bm.faces.new([vb0, vb1, vb2, vb3])
    f_back.material_index = 0
    uv_casing_back = (700 / 2048.0, 1.0 - 1650 / 2048.0, 1950 / 2048.0, 1.0 - 1120 / 2048.0)
    set_face_uv_rect(h_bm, f_back, uv_casing_back)

    # Outer side walls (Left, Right, Bottom, Top)
    f_left  = h_bm.faces.new([vf0, vb0, vb3, vf3])
    f_right = h_bm.faces.new([vb1, vf1, vf2, vb2])
    f_bot   = h_bm.faces.new([vb0, vf0, vf1, vb1])
    f_top   = h_bm.faces.new([vb3, vb2, vf2, vf3])
    for f in [f_left, f_right, f_bot, f_top]:
        f.material_index = 0
        set_face_uv_constant(h_bm, f, uv_swatch_red)

    # Front Face Frame with Recessed Pocket Cavity
    # Pocket inner dimensions:
    px0, px1 = -0.030, 0.030
    pz0, pz1 = -0.024, 0.020
    py_rec   = 0.022 # 10mm pocket depth

    # Front inner frame vertices at hy_front (0.032)
    vi0 = h_bm.verts.new((px0, hy_front, pz0)) # bottom-left
    vi1 = h_bm.verts.new((px1, hy_front, pz0)) # bottom-right
    vi2 = h_bm.verts.new((px1, hy_front, pz1)) # top-right
    vi3 = h_bm.verts.new((px0, hy_front, pz1)) # top-left

    # Front frame faces:
    # 1. Top banner: vf3, vf2, vi2, vi3 (Z: 0.020 to 0.044)
    f_f_top = h_bm.faces.new([vi3, vi2, vf2, vf3])
    f_f_top.material_index = 0
    uv_top_banner = (50 / 2048.0, 1.0 - 200 / 2048.0, 1050 / 2048.0, 1.0 - 50 / 2048.0)
    set_face_uv_rect(h_bm, f_f_top, uv_top_banner)

    # 2. Bottom instructions bar: vf0, vi0, vi1, vf1 (Z: -0.044 to -0.024)
    f_f_bot = h_bm.faces.new([vf0, vf1, vi1, vi0])
    f_f_bot.material_index = 0
    uv_bot_bar = (50 / 2048.0, 1.0 - 1050 / 2048.0, 1050 / 2048.0, 1.0 - 850 / 2048.0)
    set_face_uv_rect(h_bm, f_f_bot, uv_bot_bar)

    # 3. Left side border: vf0, vi0, vi3, vf3
    f_f_l = h_bm.faces.new([vf0, vi0, vi3, vf3])
    f_f_l.material_index = 0
    set_face_uv_constant(h_bm, f_f_l, uv_swatch_red)

    # 4. Right side border: vi1, vf1, vf2, vi2
    f_f_r = h_bm.faces.new([vi1, vf1, vf2, vi2])
    f_f_r.material_index = 0
    set_face_uv_constant(h_bm, f_f_r, uv_swatch_red)

    # Recessed Cavity Inner Walls & Floor
    vr0 = h_bm.verts.new((px0, py_rec, pz0))
    vr1 = h_bm.verts.new((px1, py_rec, pz0))
    vr2 = h_bm.verts.new((px1, py_rec, pz1))
    vr3 = h_bm.verts.new((px0, py_rec, pz1))

    # Cavity Floor (-Y back of pocket)
    f_p_floor = h_bm.faces.new([vr0, vr1, vr2, vr3])
    f_p_floor.material_index = 0
    set_face_uv_constant(h_bm, f_p_floor, uv_swatch_pocket)

    # Cavity Inner Walls
    f_pw_bot = h_bm.faces.new([vi0, vi1, vr1, vr0])
    f_pw_top = h_bm.faces.new([vr3, vr2, vi2, vi3])
    f_pw_l   = h_bm.faces.new([vi3, vi0, vr0, vr3])
    f_pw_r   = h_bm.faces.new([vi1, vi2, vr2, vr1])
    for f in [f_pw_bot, f_pw_top, f_pw_l, f_pw_r]:
        f.material_index = 0
        set_face_uv_constant(h_bm, f, uv_swatch_pocket)

    # Integrated Alarm LED on Top Right of Banner (M_Emission)
    led_x = -0.0334
    led_z = 0.0272
    r_led = 0.0032
    v_led_b = []
    v_led_t = []
    for s in range(8):
        ang = s * (2.0 * math.pi / 8)
        vx = led_x + r_led * math.cos(ang)
        vz = led_z + r_led * math.sin(ang)
        v_led_b.append(h_bm.verts.new((vx, hy_front, vz)))
        v_led_t.append(h_bm.verts.new((vx, hy_front + 0.002, vz)))

    f_led_cap = h_bm.faces.new(v_led_t)
    f_led_cap.material_index = 2 # M_Emission
    set_face_uv_constant(h_bm, f_led_cap, uv_swatch_red)
    for s in range(8):
        s_next = (s + 1) % 8
        f_led_s = h_bm.faces.new([v_led_b[s], v_led_b[s_next], v_led_t[s_next], v_led_t[s]])
        f_led_s.material_index = 2
        set_face_uv_constant(h_bm, f_led_s, uv_swatch_red)

    mark_sharp_edges(h_bm)
    h_bm.to_mesh(h_me)
    h_bm.free()

    h_obj = bpy.data.objects.new("Housing", h_me)
    bpy.context.collection.objects.link(h_obj)
    h_obj.parent = root
    assign_material_slots(h_obj, materials)

    # -------------------------------------------------------------------------
    # 2. PRESS_PIVOT (Empty - Child of Housing)
    # Centered at operating element surface: (0.000, 0.025, -0.002)
    # Linear movement along local Y: 0.000m to 0.003m inward into unit
    # -------------------------------------------------------------------------
    press_pivot = bpy.data.objects.new("Press_Pivot", None)
    press_pivot.empty_display_type = 'SINGLE_ARROW'
    press_pivot.empty_display_size = 0.04
    press_pivot.location = (0.000, 0.025, -0.002)
    bpy.context.collection.objects.link(press_pivot)
    press_pivot.parent = h_obj

    press_pivot["min_move_y"] = 0.0
    press_pivot["max_move_y"] = 0.003
    press_pivot["move_axis"] = "Y"
    press_pivot["rest_y_m"] = 0.025
    press_pivot["local_y_min"] = 0.022
    press_pivot["local_y_max"] = 0.025

    con_press = press_pivot.constraints.new(type='LIMIT_LOCATION')
    con_press.owner_space = 'LOCAL'
    con_press.use_min_x = True
    con_press.use_max_x = True
    con_press.min_x = 0.0
    con_press.max_x = 0.0
    con_press.use_min_y = True
    con_press.use_max_y = True
    con_press.min_y = 0.022
    con_press.max_y = 0.025
    con_press.use_min_z = True
    con_press.use_max_z = True
    con_press.min_z = -0.002
    con_press.max_z = -0.002

    # -------------------------------------------------------------------------
    # 3. PRESS_AREA (Mesh - Child of Press_Pivot)
    # White operating target plate with inward arrows:
    # Local X: -0.028 to 0.028, Z: -0.019 to 0.017, Y: -0.001 to 0.001
    # -------------------------------------------------------------------------
    pa_me = bpy.data.meshes.new("Press_Area")
    pa_bm = bmesh.new()

    pax0, pax1 = -0.028, 0.028
    paz0, paz1 = -0.019, 0.017
    pay0, pay1 = -0.001, 0.001

    v_pa = [
        pa_bm.verts.new((pax0, pay0, paz0)), # 0
        pa_bm.verts.new((pax1, pay0, paz0)), # 1
        pa_bm.verts.new((pax1, pay0, paz1)), # 2
        pa_bm.verts.new((pax0, pay0, paz1)), # 3
        pa_bm.verts.new((pax0, pay1, paz0)), # 4
        pa_bm.verts.new((pax1, pay1, paz0)), # 5
        pa_bm.verts.new((pax1, pay1, paz1)), # 6
        pa_bm.verts.new((pax0, pay1, paz1)), # 7
    ]
    f_pa_front = pa_bm.faces.new([v_pa[4], v_pa[5], v_pa[6], v_pa[7]])
    f_pa_front.material_index = 0 # M_Security_Atlas
    uv_target_plate = (1120 / 2048.0, 1.0 - 750 / 2048.0, 1950 / 2048.0, 1.0 - 50 / 2048.0)
    set_face_uv_rect(pa_bm, f_pa_front, uv_target_plate)

    f_pa_back  = pa_bm.faces.new([v_pa[0], v_pa[3], v_pa[2], v_pa[1]])
    f_pa_bot   = pa_bm.faces.new([v_pa[0], v_pa[1], v_pa[5], v_pa[4]])
    f_pa_top   = pa_bm.faces.new([v_pa[3], v_pa[7], v_pa[6], v_pa[2]])
    f_pa_left  = pa_bm.faces.new([v_pa[0], v_pa[4], v_pa[7], v_pa[3]])
    f_pa_right = pa_bm.faces.new([v_pa[1], v_pa[2], v_pa[6], v_pa[5]])
    for f in [f_pa_back, f_pa_bot, f_pa_top, f_pa_left, f_pa_right]:
        f.material_index = 0
        set_face_uv_constant(pa_bm, f, uv_swatch_white)

    mark_sharp_edges(pa_bm)
    pa_bm.to_mesh(pa_me)
    pa_bm.free()

    pa_obj = bpy.data.objects.new("Press_Area", pa_me)
    bpy.context.collection.objects.link(pa_obj)
    pa_obj.parent = press_pivot
    assign_material_slots(pa_obj, materials)

    # -------------------------------------------------------------------------
    # 4. BREAKABLE_WINDOW (Mesh - Child of Housing)
    # Transparent protective flip cover hinged at top: origin (0.000, 0.034, 0.021)
    # Local coords: X: -0.031 to 0.031, Z: -0.046 to 0.000, Y: -0.002 to 0.000
    # Bottom yellow lift tab: Z: -0.046 to -0.052, Y: 0.000 to 0.003
    # -------------------------------------------------------------------------
    bw_me = bpy.data.meshes.new("Breakable_Window")
    bw_bm = bmesh.new()

    bwx0, bwx1 = -0.031, 0.031
    bwz0, bwz1 = -0.046, 0.000
    bwy0, bwy1 = -0.002, 0.000

    # Main clear acrylic window plate
    v_bw = [
        bw_bm.verts.new((bwx0, bwy0, bwz0)), # 0
        bw_bm.verts.new((bwx1, bwy0, bwz0)), # 1
        bw_bm.verts.new((bwx1, bwy0, bwz1)), # 2
        bw_bm.verts.new((bwx0, bwy0, bwz1)), # 3
        bw_bm.verts.new((bwx0, bwy1, bwz0)), # 4
        bw_bm.verts.new((bwx1, bwy1, bwz0)), # 5
        bw_bm.verts.new((bwx1, bwy1, bwz1)), # 6
        bw_bm.verts.new((bwx0, bwy1, bwz1)), # 7
    ]
    f_bw_front = bw_bm.faces.new([v_bw[4], v_bw[5], v_bw[6], v_bw[7]])
    f_bw_front.material_index = 1 # M_Transparent
    uv_window_pane = (1120 / 2048.0, 1.0 - 1050 / 2048.0, 1950 / 2048.0, 1.0 - 800 / 2048.0)
    set_face_uv_rect(bw_bm, f_bw_front, uv_window_pane)

    f_bw_back  = bw_bm.faces.new([v_bw[0], v_bw[3], v_bw[2], v_bw[1]])
    f_bw_left  = bw_bm.faces.new([v_bw[0], v_bw[4], v_bw[7], v_bw[3]])
    f_bw_right = bw_bm.faces.new([v_bw[1], v_bw[2], v_bw[6], v_bw[5]])
    f_bw_top   = bw_bm.faces.new([v_bw[3], v_bw[7], v_bw[6], v_bw[2]])
    for f in [f_bw_back, f_bw_left, f_bw_right, f_bw_top]:
        f.material_index = 1
        set_face_uv_rect(bw_bm, f, uv_window_pane)

    # Bottom Yellow Finger Tab (Grip lip)
    tab_x0, tab_x1 = -0.018, 0.018
    tab_z0, tab_z1 = -0.052, -0.046
    tab_y0, tab_y1 = -0.002, 0.003

    v_tab = [
        bw_bm.verts.new((tab_x0, tab_y0, tab_z0)), # 0
        bw_bm.verts.new((tab_x1, tab_y0, tab_z0)), # 1
        bw_bm.verts.new((tab_x1, tab_y0, tab_z1)), # 2
        bw_bm.verts.new((tab_x0, tab_y0, tab_z1)), # 3
        bw_bm.verts.new((tab_x0, tab_y1, tab_z0)), # 4
        bw_bm.verts.new((tab_x1, tab_y1, tab_z0)), # 5
        bw_bm.verts.new((tab_x1, tab_y1, tab_z1)), # 6
        bw_bm.verts.new((tab_x0, tab_y1, tab_z1)), # 7
    ]
    f_tab_front = bw_bm.faces.new([v_tab[4], v_tab[5], v_tab[6], v_tab[7]])
    f_tab_front.material_index = 0 # M_Security_Atlas
    uv_tab = (1120 / 2048.0, 1.0 - 1150 / 2048.0, 1950 / 2048.0, 1.0 - 1050 / 2048.0)
    set_face_uv_rect(bw_bm, f_tab_front, uv_tab)

    f_tab_bot   = bw_bm.faces.new([v_tab[0], v_tab[1], v_tab[5], v_tab[4]])
    f_tab_back  = bw_bm.faces.new([v_tab[0], v_tab[3], v_tab[2], v_tab[1]])
    f_tab_left  = bw_bm.faces.new([v_tab[0], v_tab[4], v_tab[7], v_tab[3]])
    f_tab_right = bw_bm.faces.new([v_tab[1], v_tab[2], v_tab[6], v_tab[5]])
    for f in [f_tab_bot, f_tab_back, f_tab_left, f_tab_right]:
        f.material_index = 0
        set_face_uv_constant(bw_bm, f, uv_swatch_yellow)

    # Top Hinge Pivot Lugs (Left and Right)
    for hx in [-0.026, 0.026]:
        v_h = [
            bw_bm.verts.new((hx - 0.003, -0.004, -0.004)),
            bw_bm.verts.new((hx + 0.003, -0.004, -0.004)),
            bw_bm.verts.new((hx + 0.003, -0.004,  0.003)),
            bw_bm.verts.new((hx - 0.003, -0.004,  0.003)),
            bw_bm.verts.new((hx - 0.003,  0.001, -0.004)),
            bw_bm.verts.new((hx + 0.003,  0.001, -0.004)),
            bw_bm.verts.new((hx + 0.003,  0.001,  0.003)),
            bw_bm.verts.new((hx - 0.003,  0.001,  0.003)),
        ]
        f_hl = bw_bm.faces.new([v_h[4], v_h[5], v_h[6], v_h[7]])
        f_hl.material_index = 1
        set_face_uv_rect(bw_bm, f_hl, uv_window_pane)

    mark_sharp_edges(bw_bm)
    bw_bm.to_mesh(bw_me)
    bw_bm.free()

    bw_obj = bpy.data.objects.new("Breakable_Window", bw_me)
    bw_obj.location = (0.000, 0.034, 0.021)
    bpy.context.collection.objects.link(bw_obj)
    bw_obj.parent = h_obj
    assign_material_slots(bw_obj, materials)

    bw_obj["min_rot_x"] = 0.0
    bw_obj["max_rot_x"] = 85.0
    bw_obj["rot_axis"] = "X"

    con_bw = bw_obj.constraints.new(type='LIMIT_ROTATION')
    con_bw.owner_space = 'LOCAL'
    con_bw.use_limit_x = True
    con_bw.min_x = math.radians(0.0)
    con_bw.max_x = math.radians(85.0)
    con_bw.use_limit_y = True
    con_bw.min_y = 0.0
    con_bw.max_y = 0.0
    con_bw.use_limit_z = True
    con_bw.min_z = 0.0
    con_bw.max_z = 0.0

    # -------------------------------------------------------------------------
    # 5. RESET_COVER (Mesh - Child of Housing)
    # Bottom test key release cover:
    # X: -0.016 to 0.016, Z: -0.042 to -0.030, Y: 0.032 to 0.035
    # -------------------------------------------------------------------------
    rc_me = bpy.data.meshes.new("Reset_Cover")
    rc_bm = bmesh.new()

    rcx0, rcx1 = -0.016, 0.016
    rcz0, rcz1 = -0.042, -0.030
    rcy0, rcy1 = 0.032, 0.0355

    v_rc = [
        rc_bm.verts.new((rcx0, rcy0, rcz0)), # 0
        rc_bm.verts.new((rcx1, rcy0, rcz0)), # 1
        rc_bm.verts.new((rcx1, rcy0, rcz1)), # 2
        rc_bm.verts.new((rcx0, rcy0, rcz1)), # 3
        rc_bm.verts.new((rcx0, rcy1, rcz0)), # 4
        rc_bm.verts.new((rcx1, rcy1, rcz0)), # 5
        rc_bm.verts.new((rcx1, rcy1, rcz1)), # 6
        rc_bm.verts.new((rcx0, rcy1, rcz1)), # 7
    ]
    f_rc_front = rc_bm.faces.new([v_rc[4], v_rc[5], v_rc[6], v_rc[7]])
    f_rc_front.material_index = 0 # M_Security_Atlas
    uv_reset_key = (50 / 2048.0, 1.0 - 1400 / 2048.0, 650 / 2048.0, 1.0 - 1120 / 2048.0)
    set_face_uv_rect(rc_bm, f_rc_front, uv_reset_key)

    f_rc_bot   = rc_bm.faces.new([v_rc[0], v_rc[1], v_rc[5], v_rc[4]])
    f_rc_top   = rc_bm.faces.new([v_rc[3], v_rc[7], v_rc[6], v_rc[2]])
    f_rc_left  = rc_bm.faces.new([v_rc[0], v_rc[4], v_rc[7], v_rc[3]])
    f_rc_right = rc_bm.faces.new([v_rc[1], v_rc[2], v_rc[6], v_rc[5]])
    for f in [f_rc_bot, f_rc_top, f_rc_left, f_rc_right]:
        f.material_index = 0
        set_face_uv_constant(rc_bm, f, uv_swatch_red)

    mark_sharp_edges(rc_bm)
    rc_bm.to_mesh(rc_me)
    rc_bm.free()

    rc_obj = bpy.data.objects.new("Reset_Cover", rc_me)
    bpy.context.collection.objects.link(rc_obj)
    rc_obj.parent = h_obj
    assign_material_slots(rc_obj, materials)

    # -------------------------------------------------------------------------
    # QA Check & Triangulation
    # -------------------------------------------------------------------------
    total_tris = 0
    meshes = [h_obj, pa_obj, bw_obj, rc_obj]
    for obj in meshes:
        me = obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        tris = len(bm.faces)
        total_tris += tris
        bm.free()
        obj.to_mesh_clear()

    print(f"[Geometry] Total meshes: {len(meshes)}, Total tris: {total_tris} (limit: {MAX_TRIS})")
    assert total_tris <= MAX_TRIS, f"Tris limit exceeded: {total_tris} > {MAX_TRIS}"

    # Viewport shading mode to MATERIAL
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

    # Save Blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"[Export] Saved blend: {BLEND_PATH}")

    # Export FBX
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root

    bpy.ops.export_scene.fbx(
        filepath=FBX_PATH,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        bake_space_transform=False,
        object_types={'EMPTY', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        use_armature_deform_only=False,
        bake_anim=False
    )
    print(f"[Export] Saved FBX: {FBX_PATH}")

    # Verify FBX Reimport
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)

    reimp_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    reimp_tris = 0
    for o in reimp_meshes:
        m = o.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(m)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        reimp_tris += len(bm.faces)
        bm.free()
        o.to_mesh_clear()

    print(f"[QA Reimport] Meshes: {len(reimp_meshes)}, Tris: {reimp_tris}")
    assert len(reimp_meshes) == 4, f"Mesh count mismatch: {len(reimp_meshes)} != 4"
    assert reimp_tris <= MAX_TRIS, f"Re-imported tris exceed budget: {reimp_tris} > {MAX_TRIS}"

    # Manifest update
    manifest = {
        "SEC_Alarm_Manual_Call_Point": {
            "status": "SUCCESS",
            "fbx_path": FBX_PATH,
            "blend_path": BLEND_PATH,
            "total_tris": total_tris,
            "max_tris": MAX_TRIS,
            "mesh_count": len(meshes),
            "empty_count": 2,
            "materials": ["M_Security_Atlas", "M_Transparent", "M_Emission"]
        }
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print(f"[Manifest] Updated {MANIFEST_PATH} with status SUCCESS")

if __name__ == "__main__":
    build_scene()
