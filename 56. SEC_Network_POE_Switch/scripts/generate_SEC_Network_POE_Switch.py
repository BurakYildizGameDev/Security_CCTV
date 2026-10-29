"""
=============================================================================
Security CCTV Asset Production Suite - Asset 56
Asset Name: SEC_Network_POE_Switch (PoE Ag Anahtari)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Network_POE_Switch.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Network_POE_Switch.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Network_POE_Switch"
MAX_TRIS = 650

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
        bsdf_e.inputs["Emission Strength"].default_value = 6.00

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
    f_front = bm.faces.new([v[0], v[1], v[2], v[3]]) # -Y face (facing viewer)
    f_rear  = bm.faces.new([v[5], v[4], v[7], v[6]]) # +Y face (rear)
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]]) # -Z face
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]]) # +Z face
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]]) # -X face
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]]) # +X face
    bm.normal_update()
    return {
        'front': f_front, 'rear': f_rear, 'bot': f_bot,
        'top': f_top, 'left': f_left, 'right': f_right, 'verts': v
    }

def add_open_box_front(bm, x0, x1, y0, y1, z0, z1):
    """5-sided box open at the back (+Y), front face at y0 (-Y)."""
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
    f_front = bm.faces.new([v[0], v[1], v[2], v[3]]) # -Y (front)
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]]) # -Z
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]]) # +Z
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]]) # -X
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]]) # +X
    bm.normal_update()
    return {
        'front': f_front, 'bot': f_bot,
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

def build_chassis(mat_atlas, mat_metal, mat_emit):
    me = bpy.data.meshes.new("Chassis")
    bm = bmesh.new()

    uv_rear_panel = (74/2048, 1.0 - 670/2048, 1974/2048, 1.0 - 480/2048)
    uv_chassis_dark = (50/2048, 1.0 - 1900/2048, 450/2048, 1.0 - 1500/2048)

    # 1U Chassis Dimensions:
    # W = 0.440m (X: -0.220 to +0.220)
    # D = 0.260m (Y: 0.000 to +0.260)
    # H = 0.044m (Z: -0.022 to +0.022)
    box = add_box(bm, -0.220, 0.220, 0.000, 0.260, -0.022, 0.022)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            if k == 'rear':
                set_planar_uv(bm, face, uv_rear_panel, plane='XZ', flip_u=True)
            else:
                set_planar_uv(bm, face, uv_chassis_dark, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Chassis", me)
    return obj

def build_rack_ears(mat_atlas, mat_metal, mat_emit):
    me = bpy.data.meshes.new("Rack_Ears")
    bm = bmesh.new()

    uv_metal = (1050/2048, 1.0 - 1900/2048, 1450/2048, 1.0 - 1500/2048)

    # 19" Rack Mounting Ears:
    # Left Ear: X: -0.2415 to -0.220, Y: -0.003 to 0.000, Z: -0.022 to +0.022
    box_l = add_box(bm, -0.2415, -0.220, -0.003, 0.000, -0.022, 0.022)
    for face in box_l.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    # Right Ear: X: 0.220 to 0.2415, Y: -0.003 to 0.000, Z: -0.022 to +0.022
    box_r = add_box(bm, 0.220, 0.2415, -0.003, 0.000, -0.022, 0.022)
    for face in box_r.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Rack_Ears", me)
    return obj

def build_front_panel(mat_atlas, mat_metal, mat_emit):
    me = bpy.data.meshes.new("Front_Panel")
    bm = bmesh.new()

    # Front Fascia UV: exact 10:1 aspect ratio matching 440mm x 44mm front face
    uv_fascia = (74/2048, 1.0 - 220/2048, 1974/2048, 1.0 - 30/2048)
    uv_dark   = (50/2048, 1.0 - 1900/2048, 450/2048, 1.0 - 1500/2048)

    # Front Panel Block:
    # W = 0.440m (X: -0.220 to +0.220)
    # D = 0.008m (Y: -0.008 to 0.000)
    # H = 0.044m (Z: -0.022 to +0.022)
    box = add_box(bm, -0.220, 0.220, -0.008, 0.000, -0.022, 0.022)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            if k == 'front':
                set_planar_uv(bm, face, uv_fascia, plane='XZ', flip_u=False)
            else:
                set_planar_uv(bm, face, uv_dark, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Front_Panel", me)
    return obj

def build_ethernet_port(name, cx, cz, mat_atlas, mat_metal, mat_emit):
    """Builds a single RJ-45 shielded socket mesh (5 faces = 10 tris)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Port dimensions:
    # Width = 0.0135m (13.5mm), Height = 0.0115m (11.5mm)
    # Protrudes 1.5mm proud of front panel (Y: -0.0095 to -0.0080)
    hw = 0.0135 / 2.0
    hh = 0.0115 / 2.0
    x0, x1 = cx - hw, cx + hw
    y0, y1 = -0.0095, -0.0080
    z0, z1 = cz - hh, cz + hh

    uv_port_face = (120/2048, 1.0 - 430/2048, 420/2048, 1.0 - 300/2048)
    uv_metal     = (1050/2048, 1.0 - 1900/2048, 1450/2048, 1.0 - 1500/2048)

    box = add_open_box_front(bm, x0, x1, y0, y1, z0, z1)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front':
                face.material_index = 0 # Slot 0: M_Security_Atlas (Socket pin cavity texture)
                set_planar_uv(bm, face, uv_port_face, plane='XZ')
            else:
                face.material_index = 1 # Slot 1: M_Metal (Shielded collar sides)
                set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new(name, me)
    # Set mesh origin to geometric center of the port
    center_local = Vector((cx, (y0 + y1) / 2.0, cz))
    me.transform(Matrix.Translation(-center_local))
    obj.location = center_local
    return obj

def build_led_indicator(name, cx, cz, mat_atlas, mat_metal, mat_emit):
    """Builds a single 3D LED indicator lens bead (5 faces = 10 tris)."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # LED dimensions:
    # Width = 0.0030m (3.0mm), Height = 0.0018m (1.8mm)
    # Sitting 0.35mm proud of front panel (Y: -0.00835 to -0.0080)
    hw = 0.0030 / 2.0
    hh = 0.0018 / 2.0
    x0, x1 = cx - hw, cx + hw
    y0, y1 = -0.00835, -0.0080
    z0, z1 = cz - hh, cz + hh

    uv_emit = (74/2048, 1.0 - 1360/2048, 520/2048, 1.0 - 1060/2048)

    box = add_open_box_front(bm, x0, x1, y0, y1, z0, z1)
    for face in box.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 2 # Slot 2: M_Emission
            set_planar_uv(bm, face, uv_emit, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new(name, me)
    # Set mesh origin to geometric center of the LED
    center_local = Vector((cx, (y0 + y1) / 2.0, cz))
    me.transform(Matrix.Translation(-center_local))
    obj.location = center_local
    return obj

def main():
    print("=" * 70)
    print(f"Generating {ASSET_NAME}...")
    print("=" * 70)

    reset_scene()
    mat_atlas, mat_metal, mat_emit = create_materials()

    # 1. Root Empty: SEC_Network_POE_Switch at (0, 0, 0)
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.20
    root.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root)

    # 2. Chassis parented to root
    chassis = build_chassis(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(chassis)
    chassis.parent = root

    # 3. Rack_Ears parented to Chassis
    ears = build_rack_ears(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(ears)
    ears.parent = chassis

    # 4. Front_Panel parented to Chassis
    front_panel = build_front_panel(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(front_panel)
    front_panel.parent = chassis

    # 5. Build 24 Ethernet Ports and 24 Status LEDs
    # 12 Columns matching exact mathematical 1:1 texture mapping:
    # x_c(c) = -0.01275 + c * 0.0160 m
    # Top Row (Odd: 1, 3, ..., 23): z = +0.0068m, Top LED: z = +0.0165m
    # Bot Row (Even: 2, 4, ..., 24): z = -0.0068m, Bot LED: z = -0.0165m
    all_ports = []
    all_leds = []

    for col in range(12):
        cx = -0.01275 + col * 0.0160

        # --- Top Port (Odd: 01, 03, ..., 23) ---
        port_num_top = col * 2 + 1
        port_name_top = f"Ethernet_Port_{port_num_top:02d}"
        led_name_top = f"LED_{port_num_top:02d}"

        port_top = build_ethernet_port(port_name_top, cx, +0.0068, mat_atlas, mat_metal, mat_emit)
        bpy.context.scene.collection.objects.link(port_top)
        port_top.parent = front_panel
        all_ports.append(port_top)

        led_top = build_led_indicator(led_name_top, cx, +0.0165, mat_atlas, mat_metal, mat_emit)
        bpy.context.scene.collection.objects.link(led_top)
        led_top.parent = front_panel
        all_leds.append(led_top)

        # --- Bottom Port (Even: 02, 04, ..., 24) ---
        port_num_bot = col * 2 + 2
        port_name_bot = f"Ethernet_Port_{port_num_bot:02d}"
        led_name_bot = f"LED_{port_num_bot:02d}"

        port_bot = build_ethernet_port(port_name_bot, cx, -0.0068, mat_atlas, mat_metal, mat_emit)
        bpy.context.scene.collection.objects.link(port_bot)
        port_bot.parent = front_panel
        all_ports.append(port_bot)

        led_bot = build_led_indicator(led_name_bot, cx, -0.0165, mat_atlas, mat_metal, mat_emit)
        bpy.context.scene.collection.objects.link(led_bot)
        led_bot.parent = front_panel
        all_leds.append(led_bot)

    # Sort ports and leds cleanly by name
    all_ports.sort(key=lambda o: o.name)
    all_leds.sort(key=lambda o: o.name)

    # Metadata custom properties on Root
    root["asset_id"] = "SEC_56"
    root["form_factor"] = "19_INCH_1U_RACKMOUNT"
    root["port_count"] = 24
    root["uplink_count"] = 2
    root["poe_standard"] = "IEEE_802.3AT_AF"
    root["poe_budget_watts"] = 370
    root["switching_capacity"] = "52_GBPS"

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, chassis, ears, front_panel] + all_ports + all_leds
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
    print(f"  Mesh Count: {mesh_count} (Expected: 51)")
    print(f"  Empty Count: {empty_count} (Expected: 1)")
    print(f"  Materials: {sorted(list(materials_found))}")

    is_tris_ok = (total_tris <= MAX_TRIS)
    is_mesh_ok = (mesh_count == 51)
    is_empty_ok = (empty_count == 1)

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
        raise RuntimeError(f"QA Validation FAILED: tris={total_tris} (max {MAX_TRIS}), mesh_count={mesh_count} (exp 51), empty_count={empty_count} (exp 1)")

if __name__ == "__main__":
    main()
