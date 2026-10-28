"""
=============================================================================
Security CCTV Asset Production Suite - Asset 55
Asset Name: SEC_DVR_Port_Expansion (CCTV Port Genisletme Modulu)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_DVR_Port_Expansion.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_DVR_Port_Expansion.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_DVR_Port_Expansion"
MAX_TRIS = 420

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
        bsdf_m.inputs["Metallic"].default_value = 0.90
        bsdf_m.inputs["Roughness"].default_value = 0.25

    # Slot 2: M_Emission
    mat_emit = bpy.data.materials.new(name="M_Emission")
    mat_emit.use_nodes = True
    bsdf_e = mat_emit.node_tree.nodes.get("Principled BSDF")
    if bsdf_e:
        bsdf_e.inputs["Base Color"].default_value = (0.15, 0.90, 0.30, 1.0)
        bsdf_e.inputs["Emission Color"].default_value = (0.15, 0.90, 0.30, 1.0)
        bsdf_e.inputs["Emission Strength"].default_value = 3.50

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

def build_chassis(mat_atlas, mat_metal, mat_emit):
    me = bpy.data.meshes.new("Chassis")
    bm = bmesh.new()

    uv_front   = (20/2048, 1.0 - 240/2048, 1960/2048, 1.0 - 20/2048)
    uv_rear    = (20/2048, 1.0 - 740/2048, 1960/2048, 1.0 - 500/2048)
    uv_chassis = (50/2048, 1.0 - 1900/2048, 450/2048, 1.0 - 1500/2048)

    # 1U Chassis Dimensions:
    # W = 0.440m (X: -0.220 to +0.220)
    # D = 0.220m (Y: 0.000 to +0.220)
    # H = 0.044m (Z: -0.022 to +0.022)
    box = add_box(bm, -0.220, 0.220, 0.000, 0.220, -0.022, 0.022)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            if k == 'front':
                set_planar_uv(bm, face, uv_front, plane='XZ', flip_u=False)
            elif k == 'rear':
                set_planar_uv(bm, face, uv_rear, plane='XZ', flip_u=True)
            else:
                set_planar_uv(bm, face, uv_chassis, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Chassis", me)
    return obj

def build_rack_ears(mat_atlas, mat_metal, mat_emit):
    me = bpy.data.meshes.new("Rack_Ears")
    bm = bmesh.new()

    uv_metal = (1020/2048, 1.0 - 1100/2048, 1480/2048, 1.0 - 800/2048)

    # 19" 1U Mounting Ears: Left & Right Flanges
    # Thickness: 3mm (Y: -0.003 to 0.000)
    # Left Ear: X: -0.241 to -0.220, Z: -0.022 to +0.022
    box_l = add_box(bm, -0.241, -0.220, -0.003, 0.000, -0.022, 0.022)
    for face in box_l.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    # Right Ear: X: 0.220 to 0.241, Z: -0.022 to +0.022
    box_r = add_box(bm, 0.220, 0.241, -0.003, 0.000, -0.022, 0.022)
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

def build_front_led_array(mat_atlas, mat_metal, mat_emit):
    """Front panel status indicator LED plate sitting proud of the fascia."""
    me = bpy.data.meshes.new("Front_LED_Array")
    bm = bmesh.new()

    # Positioned on front panel right side:
    # X: -0.020 to +0.198 (W = 0.218m)
    # Y: -0.0018 to 0.0000 (1.8mm proud)
    # Z: -0.015 to +0.015 (H = 0.030m)
    box = add_box(bm, -0.020, 0.198, -0.0018, 0.0000, -0.015, 0.015)
    uv_led_face = (20/2048, 1.0 - 460/2048, 1960/2048, 1.0 - 260/2048)
    uv_dark     = (550/2048, 1.0 - 1900/2048, 950/2048, 1.0 - 1500/2048)

    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front':
                face.material_index = 0 # Slot 0: M_Security_Atlas
                set_planar_uv(bm, face, uv_led_face, plane='XZ', flip_u=False)
            else:
                face.material_index = 0
                set_planar_uv(bm, face, uv_dark, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Front_LED_Array", me)
    return obj

def build_rear_port_array(mat_atlas, mat_metal, mat_emit):
    """Rear 16-channel BNC ports and Host Bus connectors extruding from rear panel."""
    me = bpy.data.meshes.new("Rear_Port_Array")
    bm = bmesh.new()

    uv_metal = (1020/2048, 1.0 - 1100/2048, 1480/2048, 1.0 - 800/2048)
    uv_dark  = (1520/2048, 1.0 - 1440/2048, 1980/2048, 1.0 - 1140/2048)

    # 1. BNC Connector Cluster:
    # 2 rows of 8 cylindrical/hex barrels simplified to low-poly boxes
    # Spans X: -0.205 to -0.025, Y: 0.220 to 0.228, Z: -0.015 to +0.015
    for r in range(2):
        z_c = 0.007 if r == 0 else -0.007
        for c in range(8):
            x_c = -0.200 + c * 0.022
            box_bnc = add_box(bm, x_c - 0.005, x_c + 0.005, 0.220, 0.228, z_c - 0.005, z_c + 0.005)
            for face in box_bnc.values():
                if isinstance(face, bmesh.types.BMFace):
                    face.material_index = 1 # Slot 1: M_Metal
                    set_planar_uv(bm, face, uv_metal, plane='XZ')

    # 2. Host Expansion Bus (High-density DB / SCSI connector):
    # Centered at X: 0.010 to 0.070, Y: 0.220 to 0.227, Z: -0.012 to +0.012
    box_bus = add_box(bm, 0.010, 0.070, 0.220, 0.227, -0.012, 0.012)
    for face in box_bus.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    # 3. RS-485 Green Terminal Block:
    # X: 0.085 to 0.145, Y: 0.220 to 0.229, Z: -0.010 to +0.010
    box_term = add_box(bm, 0.085, 0.145, 0.220, 0.229, -0.010, 0.010)
    for face in box_term.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            set_planar_uv(bm, face, uv_dark, plane='XZ')

    # 4. DC Power Jack:
    # X: 0.165 to 0.195, Y: 0.220 to 0.227, Z: -0.008 to +0.008
    box_pwr = add_box(bm, 0.165, 0.195, 0.220, 0.227, -0.008, 0.008)
    for face in box_pwr.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_metal, mat_emit)
    obj = bpy.data.objects.new("Rear_Port_Array", me)
    return obj

def main():
    print("=" * 70)
    print(f"Generating {ASSET_NAME}...")
    print("=" * 70)

    reset_scene()
    mat_atlas, mat_metal, mat_emit = create_materials()

    # 1. Root Empty: SEC_DVR_Port_Expansion at (0, 0, 0)
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

    # 4. Front_LED_Array parented to Chassis
    leds = build_front_led_array(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(leds)
    leds.parent = chassis

    # 5. Rear_Port_Array parented to Chassis
    ports = build_rear_port_array(mat_atlas, mat_metal, mat_emit)
    bpy.context.scene.collection.objects.link(ports)
    ports.parent = chassis

    # Metadata custom properties on Root
    root["asset_id"] = "SEC_55"
    root["form_factor"] = "19_INCH_1U_RACKMOUNT"
    root["expansion_type"] = "16_CHANNEL_BNC_MULTIPLEXER"
    root["bus_standard"] = "PCIE_EXP_BUS"
    root["power_input"] = "12V_DC_5A"

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, chassis, ears, leds, ports]
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

    # Export FBX
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

    # QA Validation in clean scene
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
    print(f"  Mesh Count: {mesh_count}")
    print(f"  Empty Count: {empty_count}")
    print(f"  Materials: {sorted(list(materials_found))}")

    status = "SUCCESS" if (total_tris <= MAX_TRIS and mesh_count == 4 and empty_count == 1) else "FAILED"
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
        raise RuntimeError(f"QA Validation FAILED: tris={total_tris} > {MAX_TRIS} or mesh_count={mesh_count} != 4")

if __name__ == "__main__":
    main()
