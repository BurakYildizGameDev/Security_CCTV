"""
=============================================================================
Security CCTV Asset Production Suite - Asset 57
Asset Name: SEC_Network_Router_Industrial (Endustriyel Guvenlik Routeri)
Blender Python Generation & QA Script
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Network_Router_Industrial.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Network_Router_Industrial.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Network_Router_Industrial"
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
        bsdf_a.inputs["Metallic"].default_value = 0.25
        bsdf_a.inputs["Roughness"].default_value = 0.45

    # Slot 1: M_Metal
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    bsdf_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    if bsdf_m and os.path.exists(ATLAS_PATH):
        tex_m = mat_metal.node_tree.nodes.new("ShaderNodeTexImage")
        tex_m.image = bpy.data.images.load(ATLAS_PATH)
        mat_metal.node_tree.links.new(tex_m.outputs["Color"], bsdf_m.inputs["Base Color"])
        bsdf_m.inputs["Metallic"].default_value = 0.92
        bsdf_m.inputs["Roughness"].default_value = 0.22

    # Slot 2: M_Emission
    mat_emit = bpy.data.materials.new(name="M_Emission")
    mat_emit.use_nodes = True
    bsdf_e = mat_emit.node_tree.nodes.get("Principled BSDF")
    if bsdf_e:
        bsdf_e.inputs["Base Color"].default_value = (0.15, 0.92, 0.35, 1.0)
        bsdf_e.inputs["Emission Color"].default_value = (0.15, 0.92, 0.35, 1.0)
        bsdf_e.inputs["Emission Strength"].default_value = 5.00

    return mat_atlas, mat_metal, mat_emit

def setup_slots(mesh, mat_atlas, mat_metal, mat_emit):
    mesh.materials.append(mat_atlas) # Slot 0
    mesh.materials.append(mat_metal) # Slot 1
    mesh.materials.append(mat_emit)  # Slot 2

def set_planar_uv(bm, face, rect, plane='XZ', flip_u=False, flip_v=False):
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = rect
    if flip_u:
        u0, u1 = u1, u0
    if flip_v:
        v0, v1 = v1, v0

    if plane == 'XZ':
        xs = [l.vert.co.x for l in face.loops]
        zs = [l.vert.co.z for l in face.loops]
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        dx = max_x - min_x if max_x > min_x else 1.0
        dz = max_z - min_z if max_z > min_z else 1.0
        for l in face.loops:
            tx = (l.vert.co.x - min_x) / dx
            tz = (l.vert.co.z - min_z) / dz
            l[uv_layer].uv = (u0 + tx * (u1 - u0), v0 + tz * (v1 - v0))
    elif plane == 'XY':
        xs = [l.vert.co.x for l in face.loops]
        ys = [l.vert.co.y for l in face.loops]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        dx = max_x - min_x if max_x > min_x else 1.0
        dy = max_y - min_y if max_y > min_y else 1.0
        for l in face.loops:
            tx = (l.vert.co.x - min_x) / dx
            ty = (l.vert.co.y - min_y) / dy
            l[uv_layer].uv = (u0 + tx * (u1 - u0), v0 + ty * (v1 - v0))
    else: # YZ
        ys = [l.vert.co.y for l in face.loops]
        zs = [l.vert.co.z for l in face.loops]
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        dy = max_y - min_y if max_y > min_y else 1.0
        dz = max_z - min_z if max_z > min_z else 1.0
        for l in face.loops:
            ty = (l.vert.co.y - min_y) / dy
            tz = (l.vert.co.z - min_z) / dz
            l[uv_layer].uv = (u0 + ty * (u1 - u0), v0 + tz * (v1 - v0))

def add_box(bm, x0, x1, y0, y1, z0, z1):
    v = [
        bm.verts.new((x0, y0, z0)), # 0
        bm.verts.new((x1, y0, z0)), # 1
        bm.verts.new((x1, y0, z1)), # 2
        bm.verts.new((x0, y0, z1)), # 3
        bm.verts.new((x0, y1, z0)), # 4
        bm.verts.new((x1, y1, z0)), # 5
        bm.verts.new((x1, y1, z1)), # 6
        bm.verts.new((x0, y1, z1)), # 7
    ]
    f_front = bm.faces.new([v[0], v[1], v[2], v[3]]) # -Y (looks toward viewer)
    f_rear  = bm.faces.new([v[5], v[4], v[7], v[6]]) # +Y (rear)
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]]) # -Z
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]]) # +Z
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]]) # -X
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]]) # +X
    bm.normal_update()
    return {
        'front': f_front, 'rear': f_rear, 'bot': f_bot,
        'top': f_top, 'left': f_left, 'right': f_right, 'verts': v
    }

def mark_sharp_edges_by_angle(bm, threshold_deg=35.0):
    thresh = math.radians(threshold_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            angle = edge.calc_face_angle()
            if angle > thresh:
                edge.smooth = False
        elif len(edge.link_faces) == 1:
            edge.smooth = False

def build_housing(mat_atlas, mat_metal, mat_emit):
    me = bpy.data.meshes.new("Housing")
    bm = bmesh.new()

    uv_front = (80/2048, 1.0 - 960/2048, 1280/2048, 1.0 - 60/2048)
    uv_rear  = (80/2048, 1.0 - 1400/2048, 1280/2048, 1.0 - 1000/2048)
    uv_fins  = (1320/2048, 1.0 - 1500/2048, 2020/2048, 1.0 - 1000/2048)
    uv_dark  = (80/2048, 1.0 - 2000/2048, 500/2048, 1.0 - 1550/2048)
    uv_metal = (540/2048, 1.0 - 2000/2048, 960/2048, 1.0 - 1550/2048)

    # 1. Main Router Housing Block:
    # W = 0.120m (X: -0.060 to +0.060)
    # D = 0.040m (Y: 0.000 to +0.040)
    # H = 0.090m (Z: -0.045 to +0.045)
    box = add_box(bm, -0.060, 0.060, 0.000, 0.040, -0.045, 0.045)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            if k == 'front':
                set_planar_uv(bm, face, uv_front, plane='XZ', flip_u=False)
            elif k == 'rear':
                set_planar_uv(bm, face, uv_rear, plane='XZ', flip_u=True)
            elif k in ('left', 'right'):
                set_planar_uv(bm, face, uv_fins, plane='YZ')
            else:
                set_planar_uv(bm, face, uv_dark, plane='XY')

    # 2. Rear DIN-Rail Mounting Clip (TS-35 industrial bracket)
    # W = 0.040m (X: -0.020 to +0.020), Y: 0.040 to 0.046, Z: -0.025 to +0.025
    box_din = add_box(bm, -0.020, 0.020, 0.040, 0.046, -0.025, 0.025)
    for face in box_din.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Housing", me)
    return obj

def build_antenna(name, mat_atlas, mat_metal, mat_emit):
    """
    Builds a dipole rubber duck antenna with knurled brass SMA base.
    Origin at antenna base (0, 0, 0) locally.
    Points in local +Z direction.
    """
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Dedicated texture regions from upgraded atlas:
    uv_brass   = (1720/2048, 1.0 - 300/2048, 2020/2048, 1.0 - 50/2048)
    uv_antenna = (1720/2048, 1.0 - 960/2048, 2020/2048, 1.0 - 320/2048)
    uv_metal   = (540/2048, 1.0 - 2000/2048, 960/2048, 1.0 - 1550/2048)

    # 1. Knurled SMA Connector Base Nut (6-sided cylinder)
    # Radius = 0.0045m, Height = 0.007m (Z: 0.000 to 0.007)
    segments = 6
    verts_nut_bot = []
    verts_nut_top = []
    r_nut = 0.0045
    h_nut = 0.007

    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        vx = r_nut * math.cos(ang)
        vy = r_nut * math.sin(ang)
        verts_nut_bot.append(bm.verts.new((vx, vy, 0.000)))
        verts_nut_top.append(bm.verts.new((vx, vy, h_nut)))

    f_nut_bot = bm.faces.new(verts_nut_bot)
    for i in range(segments):
        i_next = (i + 1) % segments
        f_side = bm.faces.new([
            verts_nut_bot[i], verts_nut_bot[i_next],
            verts_nut_top[i_next], verts_nut_top[i]
        ])
        f_side.material_index = 0 # Slot 0: M_Security_Atlas (Brass knurl)
        set_planar_uv(bm, f_side, uv_brass, plane='XZ')
    f_nut_bot.material_index = 0
    set_planar_uv(bm, f_nut_bot, uv_brass, plane='XY')

    # 2. Articulated Swivel Knuckle (Box: 6mm x 6mm x 8mm)
    # Z: 0.007 to 0.015
    box_k = add_box(bm, -0.003, 0.003, -0.003, 0.003, 0.007, 0.015)
    for face in box_k.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            set_planar_uv(bm, face, uv_antenna, plane='XZ')

    # 3. Main Antenna Stalk (Tapered 6-sided cylinder)
    # Z: 0.015 to 0.080 (Total height 80mm)
    # Base radius = 0.0035m, Top radius = 0.0022m
    r_stalk_bot = 0.0035
    r_stalk_top = 0.0022
    z_stalk_bot = 0.015
    z_stalk_top = 0.080

    v_stk_bot = []
    v_stk_top = []
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        v_stk_bot.append(bm.verts.new((r_stalk_bot * math.cos(ang), r_stalk_bot * math.sin(ang), z_stalk_bot)))
        v_stk_top.append(bm.verts.new((r_stalk_top * math.cos(ang), r_stalk_top * math.sin(ang), z_stalk_top)))

    f_stk_top = bm.faces.new(v_stk_top)
    for i in range(segments):
        i_next = (i + 1) % segments
        f_side = bm.faces.new([
            v_stk_bot[i], v_stk_bot[i_next],
            v_stk_top[i_next], v_stk_top[i]
        ])
        f_side.material_index = 0 # Slot 0: M_Security_Atlas (Ribbed rubber)
        set_planar_uv(bm, f_side, uv_antenna, plane='XZ')
    f_stk_top.material_index = 0
    set_planar_uv(bm, f_stk_top, uv_antenna, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new(name, me)
    return obj

def build_port_array(mat_atlas, mat_metal, mat_emit):
    """
    Builds the 3D socket cluster:
    1x WAN RJ-45 + 4x LAN RJ-45 sockets + USB port.
    Sitting proud on front panel: Y: -0.0025 to 0.0000.
    Exact Z coordinates matching texture: Z = -0.018m to +0.002m.
    """
    me = bpy.data.meshes.new("Port_Array")
    bm = bmesh.new()

    uv_metal = (540/2048, 1.0 - 2000/2048, 960/2048, 1.0 - 1550/2048)
    uv_rj45  = (1320/2048, 1.0 - 450/2048, 1680/2048, 1.0 - 50/2048)
    uv_usb   = (1320/2048, 1.0 - 620/2048, 1680/2048, 1.0 - 480/2048)

    # 1. WAN Port Socket:
    # Centered at X = -0.0445m, Z = -0.008m
    # Width = 0.015m (-0.052 to -0.037), Height = 0.020m (-0.018 to +0.002)
    box_wan = add_box(bm, -0.052, -0.037, -0.0025, 0.0000, -0.018, 0.002)
    for k, face in box_wan.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front':
                face.material_index = 0
                set_planar_uv(bm, face, uv_rj45, plane='XZ')
            else:
                face.material_index = 1
                set_planar_uv(bm, face, uv_metal, plane='XZ')

    # 2. LAN Ports 1 to 4:
    # Spaced at X = -0.020, -0.0005, +0.019, +0.0385m, Z = -0.008m
    lan_x_centers = [-0.020, -0.0005, 0.019, 0.0385]
    for lx in lan_x_centers:
        box_lan = add_box(bm, lx - 0.0075, lx + 0.0075, -0.0025, 0.0000, -0.018, 0.002)
        for k, face in box_lan.items():
            if isinstance(face, bmesh.types.BMFace):
                if k == 'front':
                    face.material_index = 0
                    set_planar_uv(bm, face, uv_rj45, plane='XZ')
                else:
                    face.material_index = 1
                    set_planar_uv(bm, face, uv_metal, plane='XZ')

    # 3. USB 3.0 Diagnostic Port:
    # Centered at X = -0.0445m, Z = -0.030m
    box_usb = add_box(bm, -0.050, -0.039, -0.0020, 0.0000, -0.033, -0.027)
    for k, face in box_usb.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front':
                face.material_index = 0
                set_planar_uv(bm, face, uv_usb, plane='XZ')
            else:
                face.material_index = 1
                set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Port_Array", me)
    return obj

def build_status_led_array(mat_atlas, mat_metal, mat_emit):
    """
    Builds the 10 status LED indicator beads sitting proud of front panel:
    Y: -0.0008 to 0.0000.
    Z = +0.0210 to +0.0240 (matching texture y = 285 px).
    """
    me = bpy.data.meshes.new("Status_LED_Array")
    bm = bmesh.new()

    # Dedicated jewel lens coordinates:
    uv_green = (1320/2048, 1.0 - 800/2048, 1490/2048, 1.0 - 650/2048)
    uv_amber = (1510/2048, 1.0 - 800/2048, 1680/2048, 1.0 - 650/2048)
    uv_blue  = (1320/2048, 1.0 - 960/2048, 1490/2048, 1.0 - 810/2048)
    uv_cyan  = (1510/2048, 1.0 - 960/2048, 1680/2048, 1.0 - 810/2048)

    led_uv_map = [
        uv_green, # PWR
        uv_green, # SYS
        uv_blue,  # WAN
        uv_green, # LAN 1
        uv_green, # LAN 2
        uv_green, # LAN 3
        uv_cyan,  # 2.4G
        uv_blue,  # 5.0G
        uv_amber, # SIM
        uv_green  # VPN
    ]

    # 10 LEDs along upper strip:
    for i in range(10):
        lx = -0.0486 + i * 0.0108
        box_led = add_box(bm, lx - 0.0015, lx + 0.0015, -0.0008, 0.0000, 0.0210, 0.0240)
        target_uv = led_uv_map[i]
        for k, face in box_led.items():
            if isinstance(face, bmesh.types.BMFace):
                face.material_index = 0 # Slot 0: M_Security_Atlas
                set_planar_uv(bm, face, target_uv, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Status_LED_Array", me)
    return obj

def main():
    print("=" * 70)
    print(f"Generating {ASSET_NAME}...")
    print("=" * 70)

    reset_scene()
    mat_atlas, mat_metal, mat_emit = create_materials()

    # 1. Root Empty: SEC_Network_Router_Industrial at (0, 0, 0)
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.15
    root.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root)

    # 2. Housing parented to Root
    housing = build_housing(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(housing)
    housing.parent = root

    # 3. Port_Array parented to Housing
    ports = build_port_array(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(ports)
    ports.parent = housing

    # 4. Status_LED_Array parented to Housing
    leds = build_status_led_array(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(leds)
    leds.parent = housing

    # 5. 4 Antennas with individual Empty Pivots
    # Symmetrically positioned on top of housing: Z = +0.045, Y = 0.020
    # X locations: -0.045, -0.015, +0.015, +0.045
    antenna_x_locs = [-0.045, -0.015, 0.015, 0.045]
    antenna_objects = []
    pivot_objects = []

    for i in range(4):
        num = i + 1
        pivot_name = f"Antenna_Pivot_{num:02d}"
        antenna_name = f"Antenna_{num:02d}"
        px = antenna_x_locs[i]
        py = 0.020
        pz = 0.045

        # Empty Pivot at antenna base
        pivot = bpy.data.objects.new(pivot_name, None)
        pivot.empty_display_type = 'SINGLE_ARROW'
        pivot.empty_display_size = 0.03
        pivot.location = (px, py, pz)
        bpy.context.scene.collection.objects.link(pivot)
        pivot.parent = housing

        # Limit Rotation constraint on local X (+/- 45 deg)
        con = pivot.constraints.new('LIMIT_ROTATION')
        con.owner_space = 'LOCAL'
        con.use_limit_x = True
        con.min_x = math.radians(-45.0)
        con.max_x = math.radians(45.0)
        con.use_limit_y = True
        con.min_y = 0.0
        con.max_y = 0.0
        con.use_limit_z = True
        con.min_z = 0.0
        con.max_z = 0.0

        # Custom properties
        pivot["tilt_axis"] = "X"
        pivot["tilt_min_deg"] = -45.0
        pivot["tilt_max_deg"] = 45.0
        pivot["antenna_band"] = "DUAL_BAND_LTE_WIFI"
        pivot_objects.append(pivot)

        # Antenna Mesh (Origin at base (0,0,0) locally, parented to pivot)
        ant_obj = build_antenna(antenna_name, mat_atlas, mat_metal, mat_emit)
        bpy.context.scene.collection.objects.link(ant_obj)
        ant_obj.location = (0.0, 0.0, 0.0) # Local position relative to pivot is 0!
        ant_obj.parent = pivot
        antenna_objects.append(ant_obj)

    # Metadata custom properties on Root
    root["asset_id"] = "SEC_57"
    root["category"] = "INDUSTRIAL_NETWORK_ROUTER"
    root["mount_type"] = "DIN_RAIL_TS35"
    root["cellular_modem"] = "4G_5G_LTE_CAT12"
    root["ports"] = "1x_WAN_4x_LAN_1x_USB"
    root["poe_capability"] = "802.3AT_PSE_OUT"

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, housing, ports, leds] + pivot_objects + antenna_objects
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root

    # Set viewport shading to MATERIAL for nice user preview
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'

    # Pack all images into .blend
    bpy.ops.file.pack_all()

    # Save .blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"[Blend] Saved: {BLEND_PATH}")

    # Remove automatic .blend1 backup
    blend1_path = BLEND_PATH + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)

    # Export FBX with standard Unity parameters
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
    print(f"[FBX] Exported: {FBX_PATH}")

    # QA Validation in clean test scene (Reverse Import Verification)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)

    total_tris = 0
    mesh_count = 0
    empty_count = 0
    materials_found = set()

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            mesh_count += 1
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            total_tris += len(bm.faces)
            bm.free()

            for slot in obj.material_slots:
                if slot.material:
                    materials_found.add(slot.material.name)
        elif obj.type == 'EMPTY':
            empty_count += 1

    print("-" * 50)
    print(f"QA Results for {ASSET_NAME}:")
    print(f"  Total Tris: {total_tris} (Max: {MAX_TRIS})")
    print(f"  Mesh Count: {mesh_count} (Expected: 7)")
    print(f"  Empty Count: {empty_count} (Expected: 5)")
    print(f"  Materials: {sorted(list(materials_found))}")

    is_tris_ok = (total_tris <= MAX_TRIS)
    is_mesh_ok = (mesh_count == 7)
    is_empty_ok = (empty_count == 5)

    status = "SUCCESS" if (is_tris_ok and is_mesh_ok and is_empty_ok) else "FAILED"
    print(f"  Validation Status: {status}")
    print("-" * 50)

    # Manifest update
    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data[ASSET_NAME] = {
        "status": status,
        "fbx_path": FBX_PATH,
        "blend_path": BLEND_PATH,
        "total_tris": total_tris,
        "max_tris": MAX_TRIS,
        "mesh_count": mesh_count,
        "empty_count": empty_count,
        "materials": sorted(list(materials_found))
    }

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest_data, f, indent=4)
    print(f"[Manifest] Updated: {MANIFEST_PATH}")

    if status != "SUCCESS":
        raise RuntimeError(f"QA Validation FAILED: tris={total_tris} (max {MAX_TRIS}), mesh_count={mesh_count} (exp 7), empty_count={empty_count} (exp 5)")

if __name__ == "__main__":
    main()
