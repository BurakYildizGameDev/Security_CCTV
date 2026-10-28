"""
=============================================================================
Security CCTV Asset Production Suite - Asset 54
Asset Name: SEC_DVR_NVR_16Channel (16 Kanalli NVR Kayit Cihazi)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_DVR_NVR_16Channel.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_DVR_NVR_16Channel.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
SCREEN_PATH = os.path.join(EXPORTS_DIR, "T_Screen.png")

ASSET_NAME = "SEC_DVR_NVR_16Channel"
MAX_TRIS = 580

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

    # Slot 1: M_Screen
    mat_screen = bpy.data.materials.new(name="M_Screen")
    mat_screen.use_nodes = True
    bsdf_s = mat_screen.node_tree.nodes.get("Principled BSDF")
    if bsdf_s and os.path.exists(SCREEN_PATH):
        tex_s = mat_screen.node_tree.nodes.new("ShaderNodeTexImage")
        tex_s.image = bpy.data.images.load(SCREEN_PATH)
        mat_screen.node_tree.links.new(tex_s.outputs["Color"], bsdf_s.inputs["Base Color"])
        mat_screen.node_tree.links.new(tex_s.outputs["Color"], bsdf_s.inputs["Emission Color"])
        bsdf_s.inputs["Emission Strength"].default_value = 1.80
        bsdf_s.inputs["Roughness"].default_value = 0.15

    # Slot 2: M_Emission
    mat_emit = bpy.data.materials.new(name="M_Emission")
    mat_emit.use_nodes = True
    bsdf_e = mat_emit.node_tree.nodes.get("Principled BSDF")
    if bsdf_e:
        bsdf_e.inputs["Base Color"].default_value = (0.15, 0.90, 0.30, 1.0)
        bsdf_e.inputs["Emission Color"].default_value = (0.15, 0.90, 0.30, 1.0)
        bsdf_e.inputs["Emission Strength"].default_value = 3.50

    # Slot 3: M_Metal
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    bsdf_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    if bsdf_m and os.path.exists(ATLAS_PATH):
        tex_m = mat_metal.node_tree.nodes.new("ShaderNodeTexImage")
        tex_m.image = bpy.data.images.load(ATLAS_PATH)
        mat_metal.node_tree.links.new(tex_m.outputs["Color"], bsdf_m.inputs["Base Color"])
        bsdf_m.inputs["Metallic"].default_value = 0.92
        bsdf_m.inputs["Roughness"].default_value = 0.22

    return mat_atlas, mat_screen, mat_emit, mat_metal

def setup_slots(mesh, mat_atlas, mat_screen, mat_emit, mat_metal):
    mesh.materials.append(mat_atlas)   # Slot 0
    mesh.materials.append(mat_screen)  # Slot 1
    mesh.materials.append(mat_emit)    # Slot 2
    mesh.materials.append(mat_metal)   # Slot 3

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
    f_rear  = bm.faces.new([v[0], v[1], v[2], v[3]]) # -Y (Front towards viewer in standard camera)
    f_front = bm.faces.new([v[5], v[4], v[7], v[6]]) # +Y (Rear)
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]]) # -Z
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]]) # +Z
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]]) # -X
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]]) # +X
    bm.normal_update()
    return {
        'rear': f_rear, 'front': f_front, 'bot': f_bot,
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

def build_chassis(mat_atlas, mat_screen, mat_emit, mat_metal):
    me = bpy.data.meshes.new("Chassis")
    bm = bmesh.new()

    uv_rear_io = (20/2048, 1.0 - 1000/2048, 1960/2048, 1.0 - 600/2048)
    # Clean black area without swatch text labels
    uv_dark    = (1550/2048, 1.0 - 1300/2048, 1980/2048, 1.0 - 1160/2048)
    uv_metal   = (1020/2048, 1.0 - 1300/2048, 1480/2048, 1.0 - 1060/2048)

    # 1. Main 2U Chassis Enclosure:
    # W = 0.440m (X: -0.220 to +0.220)
    # D = 0.400m (Y: 0.000 to +0.400)
    # H = 0.088m (Z: -0.044 to +0.044)
    box_main = add_box(bm, -0.220, 0.220, 0.000, 0.400, -0.044, 0.044)
    for face in box_main.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == box_main['front']: # +Y: Rear I/O Panel
                set_planar_uv(bm, face, uv_rear_io, plane='XZ', flip_u=True)
            else:
                set_planar_uv(bm, face, uv_dark, plane='XY')

    # 2. Left & Right 19" Rack Mounting Ears (Flanges with screw slots)
    # Left Ear: X: -0.241 to -0.220, Y: -0.004 to 0.000, Z: -0.044 to 0.044
    box_el = add_box(bm, -0.241, -0.220, -0.004, 0.000, -0.044, 0.044)
    for face in box_el.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 3 # Slot 3: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    # Right Ear: X: 0.220 to 0.241, Y: -0.004 to 0.000, Z: -0.044 to 0.044
    box_er = add_box(bm, 0.220, 0.241, -0.004, 0.000, -0.044, 0.044)
    for face in box_er.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 3 # Slot 3: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen, mat_emit, mat_metal)
    obj = bpy.data.objects.new("Chassis", me)
    return obj

def build_front_panel(mat_atlas, mat_screen, mat_emit, mat_metal):
    me = bpy.data.meshes.new("Front_Panel")
    bm = bmesh.new()

    uv_fascia = (20/2048, 1.0 - 360/2048, 1960/2048, 1.0 - 20/2048)
    uv_dark   = (20/2048, 1.0 - 1300/2048, 480/2048, 1.0 - 1060/2048)
    uv_recess = (1520/2048, 1.0 - 1300/2048, 1980/2048, 1.0 - 1060/2048)

    # Front Panel Fascia Block:
    # W = 0.440m (X: -0.220 to +0.220)
    # D = 0.010m (Y: -0.010 to 0.000)
    # H = 0.088m (Z: -0.044 to +0.044)
    box_fp = add_box(bm, -0.220, 0.220, -0.010, 0.000, -0.044, 0.044)
    for face in box_fp.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            if face == box_fp['rear']: # -Y face looks toward front viewer
                set_planar_uv(bm, face, uv_fascia, plane='XZ', flip_u=False)
            else:
                set_planar_uv(bm, face, uv_dark, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen, mat_emit, mat_metal)
    obj = bpy.data.objects.new("Front_Panel", me)
    return obj

def build_display(mat_atlas, mat_screen, mat_emit, mat_metal):
    """3D VFD/LCD telemetry display surface sitting centered in front panel cutout."""
    me = bpy.data.meshes.new("Display")
    bm = bmesh.new()

    # Screen Quad: W = 0.104m (X: -0.052 to +0.052), H = 0.046m (Z: -0.018 to +0.028)
    # Positioned at Y = -0.0108 (0.8mm proud of fascia, eliminating any Z-fighting)
    y_pos = -0.0108
    v0 = bm.verts.new((-0.052, y_pos, -0.018))
    v1 = bm.verts.new(( 0.052, y_pos, -0.018))
    v2 = bm.verts.new(( 0.052, y_pos,  0.028))
    v3 = bm.verts.new((-0.052, y_pos,  0.028))

    # Face looking towards -Y (outward towards viewer)
    face = bm.faces.new([v0, v1, v2, v3])
    bm.normal_update()
    face.material_index = 1 # Slot 1: M_Screen

    # UV mapping 0..1 for T_Screen.png
    set_planar_uv(bm, face, (0.0, 0.0, 1.0, 1.0), plane='XZ', flip_u=False)

    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen, mat_emit, mat_metal)
    obj = bpy.data.objects.new("Display", me)
    return obj

def build_channel_led_array(mat_atlas, mat_screen, mat_emit, mat_metal):
    """16 Channel Status Indicator LED bar situated to the right of the display."""
    me = bpy.data.meshes.new("Channel_LED_Array")
    bm = bmesh.new()

    # LED Array Box: X: 0.061 to 0.166 (W = 0.105m), Z: -0.023 to +0.034 (H = 0.057m)
    # Y: -0.0112 to -0.0100 (1.2mm proud of panel)
    box_led = add_box(bm, 0.061, 0.166, -0.0112, -0.0100, -0.023, 0.034)
    uv_led = (1260/2048, 1.0 - 280/2048, 1720/2048, 1.0 - 60/2048)
    uv_dark = (1550/2048, 1.0 - 1300/2048, 1980/2048, 1.0 - 1160/2048)

    for face in box_led.values():
        if isinstance(face, bmesh.types.BMFace):
            if face == box_led['rear']:
                face.material_index = 0 # Slot 0: M_Security_Atlas (displays 16 LEDs & text numbers)
                set_planar_uv(bm, face, uv_led, plane='XZ', flip_u=False)
            else:
                face.material_index = 0
                set_planar_uv(bm, face, uv_dark, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen, mat_emit, mat_metal)
    obj = bpy.data.objects.new("Channel_LED_Array", me)
    return obj

def build_usb_ports(mat_atlas, mat_screen, mat_emit, mat_metal):
    """Dual USB 3.0 ports on bottom right of front panel."""
    me = bpy.data.meshes.new("USB_Port_Array")
    bm = bmesh.new()

    uv_metal = (1020/2048, 1.0 - 1300/2048, 1480/2048, 1.0 - 1060/2048)

    # Port 1 (Top): X: 0.178 to 0.200, Y: -0.0125 to -0.0100, Z: 0.006 to 0.015
    box_u1 = add_box(bm, 0.178, 0.200, -0.0125, -0.0100, 0.006, 0.015)
    for face in box_u1.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 3 # Slot 3: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    # Port 2 (Bottom): X: 0.178 to 0.200, Y: -0.0125 to -0.0100, Z: -0.015 to -0.006
    box_u2 = add_box(bm, 0.178, 0.200, -0.0125, -0.0100, -0.015, -0.006)
    for face in box_u2.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 3 # Slot 3: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen, mat_emit, mat_metal)
    obj = bpy.data.objects.new("USB_Port_Array", me)
    return obj

def build_power_button(mat_atlas, mat_screen, mat_emit, mat_metal):
    """Raised 3D tactile power switch cap on left side of front panel."""
    me = bpy.data.meshes.new("Power_Button")
    bm = bmesh.new()

    uv_btn = (120/2048, 1.0 - 540/2048, 280/2048, 1.0 - 420/2048)
    uv_dark = (20/2048, 1.0 - 1300/2048, 480/2048, 1.0 - 1060/2048)

    # Power button centered at local (0, 0, 0)
    # Radius = 0.009m (18mm button), depth = 0.0035m
    hb = 0.009
    box = add_box(bm, -hb, hb, -0.0035, 0.0, -hb, hb)
    for face in box.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Security_Atlas
            if face == box['rear']:
                set_planar_uv(bm, face, uv_btn, plane='XZ', flip_u=False)
            else:
                set_planar_uv(bm, face, uv_dark, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen, mat_emit, mat_metal)
    obj = bpy.data.objects.new("Power_Button", me)
    return obj

def main():
    print("=" * 70)
    print("Generating SEC_DVR_NVR_16Channel...")
    print("=" * 70)

    reset_scene()
    mat_atlas, mat_screen, mat_emit, mat_metal = create_materials()

    # 1. Root Empty: SEC_DVR_NVR_16Channel at (0, 0, 0)
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.25
    root.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root)

    # 2. Chassis mesh parented to root
    chassis = build_chassis(mat_atlas, mat_screen, mat_emit, mat_metal)
    bpy.context.scene.collection.objects.link(chassis)
    chassis.parent = root

    # 3. Front_Panel mesh parented to chassis
    front = build_front_panel(mat_atlas, mat_screen, mat_emit, mat_metal)
    bpy.context.scene.collection.objects.link(front)
    front.parent = chassis

    # 4. Display mesh parented to front panel
    disp = build_display(mat_atlas, mat_screen, mat_emit, mat_metal)
    bpy.context.scene.collection.objects.link(disp)
    disp.parent = front

    # 5. Channel_LED_Array parented to front panel
    leds = build_channel_led_array(mat_atlas, mat_screen, mat_emit, mat_metal)
    bpy.context.scene.collection.objects.link(leds)
    leds.parent = front

    # 6. USB_Port_Array parented to front panel
    usb = build_usb_ports(mat_atlas, mat_screen, mat_emit, mat_metal)
    bpy.context.scene.collection.objects.link(usb)
    usb.parent = front

    # 7. Button_Pivot & Power_Button
    # Button location: Left fascia at X = -0.163, Y = -0.010, Z = -0.020
    btn_piv = bpy.data.objects.new("Button_Pivot", None)
    btn_piv.empty_display_type = 'ARROWS'
    btn_piv.empty_display_size = 0.02
    btn_piv.location = (-0.163, -0.010, -0.020)
    bpy.context.scene.collection.objects.link(btn_piv)
    btn_piv.parent = front
    btn_piv["button_role"] = "SYSTEM_POWER_STANDBY"
    btn_piv["stroke_mm"] = 2.0
    btn_piv["stroke_axis"] = "Y"

    btn = build_power_button(mat_atlas, mat_screen, mat_emit, mat_metal)
    bpy.context.scene.collection.objects.link(btn)
    btn.parent = btn_piv
    btn.location = (0.0, 0.0, 0.0)

    # Metadata custom properties on Root
    root["asset_id"] = "SEC_54"
    root["form_factor"] = "19_INCH_2U_RACKMOUNT"
    root["channels"] = 16
    root["max_storage_tb"] = 64
    root["raid_support"] = "RAID_0_1_5_6_10"

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, chassis, front, disp, leds, usb, btn_piv, btn]
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

    status = "SUCCESS" if (total_tris <= MAX_TRIS and mesh_count >= 6 and empty_count >= 2) else "FAILED"
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
        raise RuntimeError(f"QA Validation FAILED: tris={total_tris} > {MAX_TRIS} or mesh_count={mesh_count} < 6")

if __name__ == "__main__":
    main()
