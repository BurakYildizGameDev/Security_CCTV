"""
=============================================================================
Security CCTV Asset Production Suite - Asset 53
Asset Name: SEC_Console_Rack_Keyboard_Drawer (1U Rack Klavye Tepsisi)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Console_Rack_Keyboard_Drawer.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Console_Rack_Keyboard_Drawer.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Console_Rack_Keyboard_Drawer"
MAX_TRIS = 620

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
    if bsdf_m and os.path.exists(ATLAS_PATH):
        tex_m = mat_metal.node_tree.nodes.new("ShaderNodeTexImage")
        tex_m.image = bpy.data.images.load(ATLAS_PATH)
        mat_metal.node_tree.links.new(tex_m.outputs["Color"], bsdf_m.inputs["Base Color"])
        bsdf_m.inputs["Metallic"].default_value = 0.90
        bsdf_m.inputs["Roughness"].default_value = 0.28

    # Slot 1: M_Security_Atlas
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf_a = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if bsdf_a and os.path.exists(ATLAS_PATH):
        tex_a = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        tex_a.image = bpy.data.images.load(ATLAS_PATH)
        mat_atlas.node_tree.links.new(tex_a.outputs["Color"], bsdf_a.inputs["Base Color"])
        bsdf_a.inputs["Metallic"].default_value = 0.20
        bsdf_a.inputs["Roughness"].default_value = 0.45

    # Slot 2: M_Rubber
    mat_rubber = bpy.data.materials.new(name="M_Rubber")
    mat_rubber.use_nodes = True
    bsdf_r = mat_rubber.node_tree.nodes.get("Principled BSDF")
    if bsdf_r and os.path.exists(ATLAS_PATH):
        tex_r = mat_rubber.node_tree.nodes.new("ShaderNodeTexImage")
        tex_r.image = bpy.data.images.load(ATLAS_PATH)
        mat_rubber.node_tree.links.new(tex_r.outputs["Color"], bsdf_r.inputs["Base Color"])
        bsdf_r.inputs["Metallic"].default_value = 0.05
        bsdf_r.inputs["Roughness"].default_value = 0.85

    return mat_metal, mat_atlas, mat_rubber

def setup_slots(mesh, mat_metal, mat_atlas, mat_rubber):
    mesh.materials.append(mat_metal)   # Slot 0
    mesh.materials.append(mat_atlas)   # Slot 1
    mesh.materials.append(mat_rubber)  # Slot 2

def set_planar_uv(bm, face, rect, plane='XY', flip_u=False, flip_v=False):
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = rect
    if flip_u:
        u0, u1 = u1, u0
    if flip_v:
        v0, v1 = v1, v0

    if plane == 'XY':
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
    elif plane == 'XZ':
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
    f_rear  = bm.faces.new([v[0], v[1], v[2], v[3]]) # -Y
    f_front = bm.faces.new([v[5], v[4], v[7], v[6]]) # +Y
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

def build_side_rail(name, is_left, mat_metal, mat_atlas, mat_rubber):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    uv_rail = (20/2048, 1.0 - 1560/2048, 1100/2048, 1.0 - 1220/2048)
    uv_steel = (1140/2048, 1.0 - 1640/2048, 1560/2048, 1.0 - 1440/2048)

    # Rail channel: Outer rail mounted to rack posts (D = 0.450m, H = 0.038m, W = 0.012m)
    if is_left:
        rx0, rx1 = -0.235, -0.223
        fx0, fx1 = -0.241, -0.223
    else:
        rx0, rx1 =  0.223,  0.235
        fx0, fx1 =  0.223,  0.241

    # 1. Main Slide Channel
    box_ch = add_box(bm, rx0, rx1, 0.000, 0.450, 0.003, 0.041)
    for face in box_ch.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Metal
            if face in [box_ch['left'], box_ch['right']]:
                set_planar_uv(bm, face, uv_rail, plane='YZ')
            else:
                set_planar_uv(bm, face, uv_steel, plane='XY')

    # 2. Front Rack Mounting Flange / Ear
    box_fl = add_box(bm, fx0, fx1, -0.004, 0.000, 0.000, 0.044)
    for face in box_fl.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            set_planar_uv(bm, face, uv_steel, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_metal, mat_atlas, mat_rubber)
    obj = bpy.data.objects.new(name, me)
    return obj

def build_tray_body(mat_metal, mat_atlas, mat_rubber):
    me = bpy.data.meshes.new("Tray_Body")
    bm = bmesh.new()

    uv_fascia = (20/2048, 1.0 - 210/2048, 1960/2048, 1.0 - 20/2048)
    # Clean dark region without any text labels
    uv_dark   = (1750/2048, 1.0 - 2020/2048, 2020/2048, 1.0 - 1920/2048)
    uv_steel  = (1140/2048, 1.0 - 1640/2048, 1560/2048, 1.0 - 1440/2048)

    # 1. Front Fascia Panel (19" 1U rack panel: W=0.482m, H=0.044m, D=0.012m)
    # X: -0.241 to +0.241, Y: -0.012 to 0.000, Z: 0.000 to 0.044
    box_front = add_box(bm, -0.241, 0.241, -0.012, 0.000, 0.000, 0.044)
    for face in box_front.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Security_Atlas
            if face == box_front['rear']:
                # The face looking toward -Y (front viewer)
                set_planar_uv(bm, face, uv_fascia, plane='XZ', flip_u=False)
            else:
                set_planar_uv(bm, face, uv_dark, plane='XY')

    # 2. Front Pull Handle (Protruding forward at Y: -0.024 to -0.012, centered X: -0.080 to +0.080)
    box_handle = add_box(bm, -0.080, 0.080, -0.024, -0.012, 0.014, 0.030)
    for face in box_handle.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Metal
            set_planar_uv(bm, face, uv_steel, plane='XZ')

    # 3. Main Sheet-Metal Tray Floor & Side Walls:
    # Floor: X: -0.220 to +0.220, Y: 0.000 to 0.440, Z: 0.004 to 0.008
    box_floor = add_box(bm, -0.220, 0.220, 0.000, 0.440, 0.004, 0.008)
    for face in box_floor.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1
            set_planar_uv(bm, face, uv_dark, plane='XY')

    # Left Tray Wall
    box_lw = add_box(bm, -0.223, -0.219, 0.000, 0.440, 0.008, 0.038)
    for face in box_lw.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            set_planar_uv(bm, face, uv_steel, plane='YZ')

    # Right Tray Wall
    box_rw = add_box(bm, 0.219, 0.223, 0.000, 0.440, 0.008, 0.038)
    for face in box_rw.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            set_planar_uv(bm, face, uv_steel, plane='YZ')

    # Rear Tray Stop Flange
    box_back = add_box(bm, -0.220, 0.220, 0.436, 0.440, 0.008, 0.038)
    for face in box_back.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1
            set_planar_uv(bm, face, uv_dark, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_metal, mat_atlas, mat_rubber)
    obj = bpy.data.objects.new("Tray_Body", me)
    return obj

def build_keyboard_surface(mat_metal, mat_atlas, mat_rubber):
    me = bpy.data.meshes.new("Keyboard_Surface")
    bm = bmesh.new()

    uv_kbd = (20/2048, 1.0 - 1180/2048, 1960/2048, 1.0 - 240/2048)
    uv_dark = (1750/2048, 1.0 - 2020/2048, 2020/2048, 1.0 - 1920/2048)
    uv_rubber = (1580/2048, 1.0 - 1640/2048, 2000/2048, 1.0 - 1440/2048)

    # Keyboard & Touchpad Module:
    # W = 0.420m (X: -0.210 to +0.210)
    # D = 0.250m (Y: 0.020 to 0.270)
    # H = 0.012m (Z: 0.008 to 0.020)
    box_kbd = add_box(bm, -0.210, 0.210, 0.020, 0.270, 0.008, 0.020)
    for face in box_kbd.values():
        if isinstance(face, bmesh.types.BMFace):
            if face == box_kbd['top']:
                face.material_index = 1 # Slot 1: M_Security_Atlas
                # Looking from above (+Z): Y goes from 0.020 (front) to 0.270 (rear)
                set_planar_uv(bm, face, uv_kbd, plane='XY', flip_u=False, flip_v=False)
            else:
                face.material_index = 1
                set_planar_uv(bm, face, uv_dark, plane='XY')

    # Touchpad Left & Right Physical Click Buttons (Slot 2: M_Rubber)
    # Sits at right front: X: 0.105 to 0.195, Y: 0.025 to 0.055, Z: 0.020 to 0.022
    box_btns = add_box(bm, 0.105, 0.195, 0.025, 0.055, 0.020, 0.0225)
    for face in box_btns.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 2 # Slot 2: M_Rubber
            set_planar_uv(bm, face, uv_rubber, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_metal, mat_atlas, mat_rubber)
    obj = bpy.data.objects.new("Keyboard_Surface", me)
    return obj

def main():
    print("=" * 70)
    print("Generating SEC_Console_Rack_Keyboard_Drawer...")
    print("=" * 70)

    reset_scene()
    mat_metal, mat_atlas, mat_rubber = create_materials()

    # 1. Root Empty: SEC_Console_Rack_Keyboard_Drawer at (0, 0, 0)
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.25
    root.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root)

    # 2. Fixed Outer Rails parented directly to Root
    rail_l = build_side_rail("Left_Rail", True, mat_metal, mat_atlas, mat_rubber)
    bpy.context.scene.collection.objects.link(rail_l)
    rail_l.parent = root

    rail_r = build_side_rail("Right_Rail", False, mat_metal, mat_atlas, mat_rubber)
    bpy.context.scene.collection.objects.link(rail_r)
    rail_r.parent = root

    # 3. Slide Mechanism:
    # Master Drawer Slide Pivot at (0, 0, 0) parented to Root
    drawer_pivot = bpy.data.objects.new("Drawer_Slide_Pivot", None)
    drawer_pivot.empty_display_type = 'PLAIN_AXES'
    drawer_pivot.empty_display_size = 0.15
    drawer_pivot.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(drawer_pivot)
    drawer_pivot.parent = root
    drawer_pivot["slide_axis"] = "Y"
    drawer_pivot["slide_travel_min"] = 0.0
    drawer_pivot["slide_travel_max"] = 0.350

    # Subsidiary Ray Pivots (L and R along rail axes)
    pivot_l = bpy.data.objects.new("Slide_Pivot_L", None)
    pivot_l.empty_display_type = 'SINGLE_ARROW'
    pivot_l.empty_display_size = 0.06
    pivot_l.location = (-0.220, 0.0, 0.022)
    bpy.context.scene.collection.objects.link(pivot_l)
    pivot_l.parent = drawer_pivot
    pivot_l["slide_axis"] = "Y"
    pivot_l["slide_travel_min"] = 0.0
    pivot_l["slide_travel_max"] = 0.350

    pivot_r = bpy.data.objects.new("Slide_Pivot_R", None)
    pivot_r.empty_display_type = 'SINGLE_ARROW'
    pivot_r.empty_display_size = 0.06
    pivot_r.location = (0.220, 0.0, 0.022)
    bpy.context.scene.collection.objects.link(pivot_r)
    pivot_r.parent = drawer_pivot
    pivot_r["slide_axis"] = "Y"
    pivot_r["slide_travel_min"] = 0.0
    pivot_r["slide_travel_max"] = 0.350

    # 4. Tray_Body parented to drawer_pivot (Centered at X=0)
    tray = build_tray_body(mat_metal, mat_atlas, mat_rubber)
    bpy.context.scene.collection.objects.link(tray)
    tray.parent = drawer_pivot
    tray.location = (0.0, 0.0, 0.0)

    # 5. Keyboard_Surface parented to Tray_Body
    kbd = build_keyboard_surface(mat_metal, mat_atlas, mat_rubber)
    bpy.context.scene.collection.objects.link(kbd)
    kbd.parent = tray
    kbd.location = (0.0, 0.0, 0.0)

    # Root metadata
    root["asset_id"] = "SEC_53"
    root["form_factor"] = "19_INCH_1U_RACKMOUNT"
    root["drawer_depth_mm"] = 450.0
    root["slide_stroke_mm"] = 350.0

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, rail_l, rail_r, drawer_pivot, pivot_l, pivot_r, tray, kbd]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root

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

    # Re-import and QA Validation in clean scene
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

    status = "SUCCESS" if (total_tris <= MAX_TRIS and mesh_count >= 4 and empty_count >= 3) else "FAILED"
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
        raise RuntimeError(f"QA Validation FAILED: tris={total_tris} > {MAX_TRIS} or mesh_count={mesh_count} < 4")

if __name__ == "__main__":
    main()
