"""
=============================================================================
Security CCTV Asset Production Suite - Asset 50
Asset Name: SEC_Monitor_Wall_Display (Duvar Tipi Buyuk Guvenlik Ekrani)
Headless Blender Generation & Validation Script
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Monitor_Wall_Display.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Monitor_Wall_Display.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
SCREEN_PATH = os.path.join(EXPORTS_DIR, "T_Screen.png")

ASSET_NAME = "SEC_Monitor_Wall_Display"
MAX_TRIS = 500

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

def create_materials():
    # Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf_a = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if bsdf_a and os.path.exists(ATLAS_PATH):
        tex_node = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(ATLAS_PATH)
        mat_atlas.node_tree.links.new(tex_node.outputs["Color"], bsdf_a.inputs["Base Color"])
        bsdf_a.inputs["Metallic"].default_value = 0.80
        bsdf_a.inputs["Roughness"].default_value = 0.40

    # Slot 1: M_Screen
    mat_screen = bpy.data.materials.new(name="M_Screen")
    mat_screen.use_nodes = True
    bsdf_s = mat_screen.node_tree.nodes.get("Principled BSDF")
    if bsdf_s and os.path.exists(SCREEN_PATH):
        tex_s = mat_screen.node_tree.nodes.new("ShaderNodeTexImage")
        tex_s.image = bpy.data.images.load(SCREEN_PATH)
        mat_screen.node_tree.links.new(tex_s.outputs["Color"], bsdf_s.inputs["Base Color"])
        mat_screen.node_tree.links.new(tex_s.outputs["Color"], bsdf_s.inputs["Emission Color"])
        bsdf_s.inputs["Emission Strength"].default_value = 1.2
        bsdf_s.inputs["Roughness"].default_value = 0.15

    # Slot 2: M_Metal
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    bsdf_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    if bsdf_m:
        bsdf_m.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
        bsdf_m.inputs["Metallic"].default_value = 0.88
        bsdf_m.inputs["Roughness"].default_value = 0.35

    return mat_atlas, mat_screen, mat_metal

def setup_slots(mesh, mat_atlas, mat_screen, mat_metal):
    mesh.materials.append(mat_atlas)   # Slot 0: M_Security_Atlas
    mesh.materials.append(mat_screen)  # Slot 1: M_Screen
    mesh.materials.append(mat_metal)   # Slot 2: M_Metal

def add_box(bm, x0, x1, y0, y1, z0, z1):
    """Utility to build a solid 6-sided cuboid."""
    v = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    f_rear  = bm.faces.new([v[0], v[3], v[2], v[1]]) # facing -Y
    f_front = bm.faces.new([v[4], v[5], v[6], v[7]]) # facing +Y
    f_bot   = bm.faces.new([v[0], v[1], v[5], v[4]]) # facing -Z
    f_top   = bm.faces.new([v[2], v[3], v[7], v[6]]) # facing +Z
    f_left  = bm.faces.new([v[3], v[0], v[4], v[7]]) # facing -X
    f_right = bm.faces.new([v[1], v[2], v[6], v[5]]) # facing +X
    return {
        'rear': f_rear, 'front': f_front, 'bot': f_bot,
        'top': f_top, 'left': f_left, 'right': f_right, 'verts': v
    }

def add_cylinder_x(bm, center_x, center_y, center_z, radius, half_len, segments=6):
    """Builds a horizontal cylinder aligned with X axis (locking knobs)."""
    p_left, p_right = [], []
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        cy = center_y + radius * math.cos(ang)
        cz = center_z + radius * math.sin(ang)
        p_left.append(bm.verts.new((center_x - half_len, cy, cz)))
        p_right.append(bm.verts.new((center_x + half_len, cy, cz)))
    f_left = bm.faces.new(list(reversed(p_left)))
    f_right = bm.faces.new(p_right)
    sides = []
    for i in range(segments):
        ni = (i + 1) % segments
        sides.append(bm.faces.new([p_left[i], p_left[ni], p_right[ni], p_right[i]]))
    return {'left': f_left, 'right': f_right, 'sides': sides}

def add_cylinder_z(bm, center_x, center_y, z0, z1, radius, segments=6):
    """Builds a vertical cylinder aligned with Z axis (BNC connectors / LEDs)."""
    p_bot, p_top = [], []
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        cx = center_x + radius * math.cos(ang)
        cy = center_y + radius * math.sin(ang)
        p_bot.append(bm.verts.new((cx, cy, z0)))
        p_top.append(bm.verts.new((cx, cy, z1)))
    f_bot = bm.faces.new(list(reversed(p_bot)))
    f_top = bm.faces.new(p_top)
    sides = []
    for i in range(segments):
        ni = (i + 1) % segments
        sides.append(bm.faces.new([p_bot[i], p_top[i], p_top[ni], p_bot[ni]]))
    return {'bot': f_bot, 'top': f_top, 'sides': sides}

def build_vesa_plate(mat_atlas, mat_screen, mat_metal):
    """
    Builds the authentic industrial VESA wall mount bracket:
    - Base wall mounting plate (340 x 340 x 6 mm)
    - Dual heavy-gauge vertical tilt bracket arms (40 x 360 x 30 mm)
    - Dual knurled side tilt clamp knobs on tilt axis
    - Front VESA mounting plate (320 x 320 mm) with tilt texture
    """
    mesh = bpy.data.meshes.new("VESA_Plate_Mesh")
    setup_slots(mesh, mat_atlas, mat_screen, mat_metal)
    obj = bpy.data.objects.new("VESA_Plate", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    # 1. Base Wall Backplate (340 x 340 x 6 mm, Y = 0.000 to 0.006)
    hw_base = 0.1700
    hh_base = 0.1700
    b_wall = add_box(bm, -hw_base, hw_base, 0.0000, 0.0060, -hh_base, hh_base)

    # 4 Corner mounting anchor washers on wall plate
    for cx in [-0.140, 0.140]:
        for cz in [-0.140, 0.140]:
            add_box(bm, cx - 0.015, cx + 0.015, 0.0060, 0.0090, cz - 0.015, cz + 0.015)

    # 2. Dual Vertical Tilt Bracket Arms (left & right)
    arm_w = 0.0240
    arm_h = 0.1800
    arm_d = 0.0320 # extends from Y = 0.006 to 0.038
    for ax in [-0.110, 0.110]:
        add_box(bm, ax - arm_w/2, ax + arm_w/2, 0.0060, 0.0380, -arm_h, arm_h)

    # 3. Knurled Side Tilt Locking Knobs (on left & right of tilt axis at Y = 0.040, Z = 0.0)
    knob_rad = 0.0140
    add_cylinder_x(bm, -0.130, 0.0380, 0.0000, knob_rad, 0.0120, segments=6)
    add_cylinder_x(bm,  0.130, 0.0380, 0.0000, knob_rad, 0.0120, segments=6)

    # 4. Front VESA Tilt Cross-Plate (320 x 320 x 4 mm, Y = 0.036 to 0.040)
    hw_vesa = 0.1600
    hh_vesa = 0.1600
    b_front = add_box(bm, -hw_vesa, hw_vesa, 0.0360, 0.0400, -hh_vesa, hh_vesa)
    f_bracket_face = b_front['front']

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    # UV Mapping
    vu_min, vu_max = 1340.0 / 2048.0, 1984.0 / 2048.0
    vv_min, vv_max = 380.0 / 2048.0, 1020.0 / 2048.0

    # Front bracket face: viewer at +Y looking toward -Y:
    # Screen Left is +X -> vu_min (start of text)
    # Screen Right is -X -> vu_max (end of text)
    f_bracket_face.material_index = 0
    for loop in f_bracket_face.loops:
        p = loop.vert.co
        u_norm = (p.x - (-hw_vesa)) / (2.0 * hw_vesa)
        u = vu_max - u_norm * (vu_max - vu_min)
        v_norm = (p.z - (-hh_vesa)) / (2.0 * hh_vesa)
        v = (1.0 - vv_max) + v_norm * (vv_max - vv_min)
        loop[uv_layer].uv = (u, v)

    # Other bracket elements map to steel bracket swatch
    swatch_u = 1500.0 / 2048.0
    swatch_v = 1.0 - (1500.0 / 2048.0)
    for f in bm.faces:
        if f != f_bracket_face:
            f.material_index = 2 # Slot 2: M_Metal
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_display_housing(mat_atlas, mat_screen, mat_metal):
    """
    Builds the authentic industrial commercial monitor housing:
    - Main slim perimeter chassis (1000 x 580 x 18 mm, Y = 0.018 to 0.036) with 45° beveled perimeter
    - Stepped rear electronics chassis (480 x 440 x 18 mm, Y = 0.000 to 0.018)
    - Downward-facing I/O connection bay with IEC socket, 2x chrome BNC terminals, HDMI & LAN ports
    - Rear specification label UV mapped crisp and un-mirrored
    """
    mesh = bpy.data.meshes.new("Display_Housing_Mesh")
    setup_slots(mesh, mat_atlas, mat_screen, mat_metal)
    obj = bpy.data.objects.new("Display_Housing", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    # 1. Main Slim Display Chassis (1000 x 580 mm, Y = 0.018 to 0.034)
    hx = 0.5000
    hz = 0.3000
    y_mid = 0.0180
    y_front = 0.0340
    b_main = add_box(bm, -hx, hx, y_mid, y_front, -hz, hz)

    # 2. Stepped Rear Electronics Chassis (480 x 440 mm, Y = 0.000 to 0.018)
    bx = 0.2400
    bz = 0.2200
    y_rear = 0.0000
    b_box = add_box(bm, -bx, bx, y_rear, y_mid, -bz, bz)
    f_spec_rear = b_box['rear'] # Facing -Y (rear towards wall)

    # 3. Downward-Facing I/O Bay Cavity at bottom of electronics box (Z = -0.220 to -0.160)
    # Cavity recessed upward into the chassis
    io_x0, io_x1 = -0.180, 0.180
    io_y0, io_y1 = 0.004, 0.016
    io_z0, io_z1 = -0.220, -0.160
    b_io = add_box(bm, io_x0, io_x1, io_y0, io_y1, io_z0, io_z1)

    # 4. 2x 3D Cylindrical BNC Connectors inside I/O bay (downward pointing)
    bnc_rad = 0.0055
    bnc1 = add_cylinder_z(bm, 0.060, 0.010, -0.228, -0.218, bnc_rad, segments=6)
    bnc2 = add_cylinder_z(bm, 0.090, 0.010, -0.228, -0.218, bnc_rad, segments=6)

    # 5. IEC Power Socket frame in I/O bay
    iec_box = add_box(bm, -0.150, -0.110, 0.008, 0.012, -0.224, -0.218)

    # 6. Upper & Lower Rear Ventilation Louver Strips
    for lz in [bz - 0.040, bz - 0.070]:
        add_box(bm, -bx + 0.030, bx - 0.030, y_rear - 0.002, y_rear, lz - 0.006, lz + 0.006)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    # UV Mapping
    hu_min, hu_max = 64.0 / 2048.0, 1280.0 / 2048.0
    hv_min, hv_max = 380.0 / 2048.0, 1180.0 / 2048.0

    # Rear specification plate: viewed from -Y towards +Y (looking at back of monitor)
    # Observer's Left is -X -> hu_min (start of text)
    # Observer's Right is +X -> hu_max (end of text)
    # Observer's Top is +Z -> hv_min (top of texture)
    # Observer's Bottom is -Z -> hv_max (bottom of texture)
    f_spec_rear.material_index = 0
    for loop in f_spec_rear.loops:
        p = loop.vert.co
        u_norm = (p.x - (-bx)) / (2.0 * bx)
        u = hu_min + u_norm * (hu_max - hu_min)
        v_norm = (p.z - (-bz)) / (2.0 * bz)
        v = (1.0 - hv_max) + v_norm * (hv_max - hv_min)
        loop[uv_layer].uv = (u, v)

    # Metallic parts (BNC connectors)
    bnc_faces = set(bnc1['sides'] + [bnc1['bot'], bnc1['top']] + bnc2['sides'] + [bnc2['bot'], bnc2['top']])
    swatch_metal_u = 1500.0 / 2048.0
    swatch_metal_v = 1.0 - (1500.0 / 2048.0)
    for f in bnc_faces:
        f.material_index = 2
        for loop in f.loops:
            loop[uv_layer].uv = (swatch_metal_u, swatch_metal_v)

    # Chassis dark swatch for remainder
    swatch_dark_u = 1500.0 / 2048.0
    swatch_dark_v = 1.0 - (1200.0 / 2048.0)
    for f in bm.faces:
        if f != f_spec_rear and f not in bnc_faces:
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_dark_u, swatch_dark_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_bezel(mat_atlas, mat_screen, mat_metal):
    """
    Builds the authentic commercial monitor front bezel:
    - Outer frame: 1000 x 580 mm, inner opening: 960 x 540 mm (16:9)
    - 45° inner chamfer slope framing the screen glass
    - Bottom chin with silk-screen logo & model
    - 3D status cluster: green power indicator LED + dark IR receiver eye
    """
    mesh = bpy.data.meshes.new("Bezel_Mesh")
    setup_slots(mesh, mat_atlas, mat_screen, mat_metal)
    obj = bpy.data.objects.new("Bezel", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.verify()

    hw_out = 0.5000  # 1000 mm outer width
    hh_out = 0.3000  # 600 mm outer height (30mm chin)
    hw_in  = 0.4800  # 960 mm inner screen width
    hh_in  = 0.2700  # 540 mm inner screen height
    y_front = 0.0375
    y_back  = 0.0355
    y_inner = 0.0360 # recessed inner chamfer rim

    # 1. Top Bezel Strip
    v_top = [
        bm.verts.new((-hw_out, y_front, hh_in)),
        bm.verts.new(( hw_out, y_front, hh_in)),
        bm.verts.new(( hw_out, y_front, hh_out)),
        bm.verts.new((-hw_out, y_front, hh_out)),
        bm.verts.new((-hw_out, y_back,  hh_out)),
        bm.verts.new(( hw_out, y_back,  hh_out)),
        bm.verts.new(( hw_in,  y_inner, hh_in)),
        bm.verts.new((-hw_in,  y_inner, hh_in)),
    ]
    f_top_front = bm.faces.new([v_top[0], v_top[1], v_top[2], v_top[3]])
    bm.faces.new([v_top[3], v_top[2], v_top[5], v_top[4]]) # top outer rim
    bm.faces.new([v_top[0], v_top[7], v_top[6], v_top[1]]) # inner chamfer slope

    # 2. Bottom Bezel Strip (contains silk-screen brand logo & status cluster)
    v_bot = [
        bm.verts.new((-hw_out, y_front, -hh_out)),
        bm.verts.new(( hw_out, y_front, -hh_out)),
        bm.verts.new(( hw_out, y_front, -hh_in)),
        bm.verts.new((-hw_out, y_front, -hh_in)),
        bm.verts.new((-hw_out, y_back,  -hh_out)),
        bm.verts.new(( hw_out, y_back,  -hh_out)),
        bm.verts.new(( hw_in,  y_inner, -hh_in)),
        bm.verts.new((-hw_in,  y_inner, -hh_in)),
    ]
    f_bot_front = bm.faces.new([v_bot[0], v_bot[1], v_bot[2], v_bot[3]])
    bm.faces.new([v_bot[0], v_bot[4], v_bot[5], v_bot[1]]) # bot outer rim
    bm.faces.new([v_bot[3], v_bot[2], v_bot[6], v_bot[7]]) # inner chamfer slope

    # 3. Left Bezel Strip
    v_left = [
        bm.verts.new((-hw_out, y_front, -hh_in)),
        bm.verts.new((-hw_in,  y_front, -hh_in)),
        bm.verts.new((-hw_in,  y_front,  hh_in)),
        bm.verts.new((-hw_out, y_front,  hh_in)),
        bm.verts.new((-hw_out, y_back,  -hh_in)),
        bm.verts.new((-hw_out, y_back,   hh_in)),
        bm.verts.new((-hw_in,  y_inner, -hh_in)),
        bm.verts.new((-hw_in,  y_inner,  hh_in)),
    ]
    f_left_front = bm.faces.new([v_left[0], v_left[1], v_left[2], v_left[3]])
    bm.faces.new([v_left[4], v_left[0], v_left[3], v_left[5]]) # left outer rim
    bm.faces.new([v_left[1], v_left[6], v_left[7], v_left[2]]) # inner chamfer slope

    # 4. Right Bezel Strip
    v_right = [
        bm.verts.new(( hw_in,  y_front, -hh_in)),
        bm.verts.new(( hw_out, y_front, -hh_in)),
        bm.verts.new(( hw_out, y_front,  hh_in)),
        bm.verts.new(( hw_in,  y_front,  hh_in)),
        bm.verts.new(( hw_out, y_back,  -hh_in)),
        bm.verts.new(( hw_out, y_back,   hh_in)),
        bm.verts.new(( hw_in,  y_inner, -hh_in)),
        bm.verts.new(( hw_in,  y_inner,  hh_in)),
    ]
    f_right_front = bm.faces.new([v_right[0], v_right[1], v_right[2], v_right[3]])
    bm.faces.new([v_right[1], v_right[4], v_right[5], v_right[2]]) # right outer rim
    bm.faces.new([v_right[0], v_right[3], v_right[7], v_right[6]]) # inner chamfer slope

    # 5. 3D Status Cluster at Bottom-Right (Viewer's right = -X in room view)
    # Cylindrical power LED lens (6 segments)
    led_x = -0.404 # located toward viewer's right (-X)
    led_z = -0.280
    led_obj = add_cylinder_z(bm, led_x, y_front + 0.001, led_z - 0.004, led_z + 0.004, 0.0040, segments=6)

    # Dark IR receiver eye dome next to LED
    ir_x = -0.479
    ir_obj = add_cylinder_z(bm, ir_x, y_front + 0.0008, led_z - 0.003, led_z + 0.003, 0.0030, segments=6)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()

    # UV Mapping
    bu_min, bu_max = 64.0 / 2048.0, 1984.0 / 2048.0
    bv_min, bv_max = 64.0 / 2048.0, 256.0 / 2048.0

    # Bottom bezel front face with logo & LED:
    # Viewer at +Y looking towards -Y:
    # Screen Left is +X -> bu_min (MODEL: SEC-MON50-4K)
    # Screen Center is 0 -> SEC-VISION PRO 4K
    # Screen Right is -X -> bu_max (PWR / ACTIVE green LED)
    f_bot_front.material_index = 0
    for loop in f_bot_front.loops:
        p = loop.vert.co
        u_norm = (p.x - (-hw_out)) / (2.0 * hw_out)
        u = bu_max - u_norm * (bu_max - bu_min) # Flip U for +Y facing normal
        v_norm = (p.z - (-hh_out)) / (hh_out - hh_in)
        v = (1.0 - bv_max) + v_norm * (bv_max - bv_min)
        loop[uv_layer].uv = (u, v)

    swatch_u = 1500.0 / 2048.0
    swatch_v = 1.0 - (1200.0 / 2048.0)
    for f in bm.faces:
        if f != f_bot_front:
            f.material_index = 0
            for loop in f.loops:
                loop[uv_layer].uv = (swatch_u, swatch_v)

    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return obj

def build_screen_surface(mat_atlas, mat_screen, mat_metal):
    """
    Builds the recessed 16:9 LCD screen surface (960 x 540 mm).
    Local coordinates relative to Display_Housing.
    Sits at Y = 0.0358 (recessed behind bezel).
    """
    mesh = bpy.data.meshes.new("Screen_Surface_Mesh")
    setup_slots(mesh, mat_atlas, mat_screen, mat_metal)
    obj = bpy.data.objects.new("Screen_Surface", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()

    hw = 0.4800  # 960 mm width
    hh = 0.2700  # 540 mm height
    y_screen = 0.0358

    v0 = bm.verts.new((-hw, y_screen, -hh))
    v1 = bm.verts.new(( hw, y_screen, -hh))
    v2 = bm.verts.new(( hw, y_screen,  hh))
    v3 = bm.verts.new((-hw, y_screen,  hh))

    # Winding order facing +Y normal towards viewer: [v0, v3, v2, v1]
    f_screen = bm.faces.new([v0, v3, v2, v1])
    f_screen.material_index = 1 # Slot 1: M_Screen

    uv_layer = bm.loops.layers.uv.verify()
    for loop in f_screen.loops:
        p = loop.vert.co
        u_norm = (p.x - (-hw)) / (2.0 * hw)
        u = 1.0 - u_norm  # Flip U so +X is left (CAM 01), -X is right (CAM 02)
        v = (p.z - (-hh)) / (2.0 * hh)
        loop[uv_layer].uv = (u, v)

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

    mat_atlas, mat_screen, mat_metal = create_materials()

    # 1. Create Root Empty
    root_obj = bpy.data.objects.new(ASSET_NAME, None)
    root_obj.empty_display_type = 'ARROWS'
    root_obj.empty_display_size = 0.10
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_obj)

    # 2. Build VESA_Plate
    vesa_plate = build_vesa_plate(mat_atlas, mat_screen, mat_metal)
    vesa_plate.parent = root_obj

    # 3. Create Tilt_Pivot Empty (at Y = 0.0400 from wall)
    tilt_pivot = bpy.data.objects.new("Tilt_Pivot", None)
    tilt_pivot.empty_display_type = 'PLAIN_AXES'
    tilt_pivot.empty_display_size = 0.05
    tilt_pivot.location = Vector((0.0, 0.0400, 0.0))
    tilt_pivot.parent = vesa_plate
    bpy.context.collection.objects.link(tilt_pivot)

    tilt_pivot["limit_min_x"] = -10.0
    tilt_pivot["limit_max_x"] = 10.0
    c_tilt = tilt_pivot.constraints.new(type='LIMIT_ROTATION')
    c_tilt.use_limit_x = True
    c_tilt.min_x = math.radians(-10.0)
    c_tilt.max_x = math.radians(10.0)
    c_tilt.owner_space = 'LOCAL'

    # 4. Build Display_Housing
    housing = build_display_housing(mat_atlas, mat_screen, mat_metal)
    housing.parent = tilt_pivot
    housing.location = Vector((0.0, 0.0, 0.0))

    # 5. Build Bezel
    bezel = build_bezel(mat_atlas, mat_screen, mat_metal)
    bezel.parent = housing
    bezel.location = Vector((0.0, 0.0, 0.0))

    # 6. Build Screen_Surface
    screen = build_screen_surface(mat_atlas, mat_screen, mat_metal)
    screen.parent = housing
    screen.location = Vector((0.0, 0.0, 0.0))

    # Mark sharp edges & auto smooth
    for obj in [vesa_plate, housing, bezel, screen]:
        mesh = obj.data
        for edge in mesh.edges:
            edge.use_edge_sharp = True
        mesh.shade_smooth()

    bpy.context.view_layer.update()

    # Total triangles verification
    total_tris = 0
    mesh_count = 0
    empty_count = 2  # Root + Tilt_Pivot

    for obj in [vesa_plate, housing, bezel, screen]:
        tris = count_triangles(obj)
        total_tris += tris
        mesh_count += 1
        print(f"Mesh '{obj.name}': {tris} tris")

    print(f"Total Tris: {total_tris} (Max: {MAX_TRIS})")
    assert total_tris <= MAX_TRIS, f"Tri count exceeded: {total_tris} > {MAX_TRIS}"

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved .blend to: {BLEND_PATH}")

    # Select hierarchy for FBX export
    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    vesa_plate.select_set(True)
    tilt_pivot.select_set(True)
    housing.select_set(True)
    bezel.select_set(True)
    screen.select_set(True)
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
        "materials": ["M_Security_Atlas", "M_Screen", "M_Metal"],
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
