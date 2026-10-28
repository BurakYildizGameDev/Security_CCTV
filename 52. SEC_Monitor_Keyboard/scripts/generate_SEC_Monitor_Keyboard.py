"""
=============================================================================
Security CCTV Asset Production Suite - Asset 52
Asset Name: SEC_Monitor_Keyboard (CCTV Operator Klavyesi)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Monitor_Keyboard.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Monitor_Keyboard.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Monitor_Keyboard"
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
        bsdf_a.inputs["Metallic"].default_value = 0.20
        bsdf_a.inputs["Roughness"].default_value = 0.50

    # Slot 1: M_Rubber
    mat_rubber = bpy.data.materials.new(name="M_Rubber")
    mat_rubber.use_nodes = True
    bsdf_r = mat_rubber.node_tree.nodes.get("Principled BSDF")
    if bsdf_r and os.path.exists(ATLAS_PATH):
        tex_r = mat_rubber.node_tree.nodes.new("ShaderNodeTexImage")
        tex_r.image = bpy.data.images.load(ATLAS_PATH)
        mat_rubber.node_tree.links.new(tex_r.outputs["Color"], bsdf_r.inputs["Base Color"])
        bsdf_r.inputs["Metallic"].default_value = 0.05
        bsdf_r.inputs["Roughness"].default_value = 0.85

    return mat_atlas, mat_rubber

def setup_slots(mesh, mat_atlas, mat_rubber):
    mesh.materials.append(mat_atlas)   # Slot 0
    mesh.materials.append(mat_rubber)  # Slot 1

def set_planar_uv(bm, face, rect, plane='XY', flip_u=False, flip_v=False):
    """Accurately projects vertex coordinates onto UV rectangle."""
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

def build_keyboard_base(mat_atlas, mat_rubber):
    me = bpy.data.meshes.new("Keyboard_Base")
    bm = bmesh.new()

    # Swatch UVs
    u_chassis_top = (20/2048, 1.0 - 580/2048, 1420/2048, 1.0 - 20/2048)
    u_bottom_spec = (20/2048, 1.0 - 1980/2048, 1420/2048, 1.0 - 1440/2048)
    u_rubber      = (1500/2048, 1.0 - 1340/2048, 2000/2048, 1.0 - 1140/2048)
    u_dark_side   = (1500/2048, 1.0 - 240/2048, 2000/2048, 1.0 - 40/2048)

    # 1. Main Wedge Chassis Body:
    # W = 0.360m (X: -0.180 to +0.180)
    # D = 0.150m (Y: -0.075 to +0.075)
    # Ergonomic tilt: Front Z=0.0 to 0.010m; Rear Z=0.0 to 0.020m (4° angle)
    # Create 8 vertices for the sloped chassis
    v_base = [
        bm.verts.new((-0.180, -0.075, 0.000)), # 0: Front-Left Bottom
        bm.verts.new(( 0.180, -0.075, 0.000)), # 1: Front-Right Bottom
        bm.verts.new(( 0.180,  0.075, 0.000)), # 2: Rear-Right Bottom
        bm.verts.new((-0.180,  0.075, 0.000)), # 3: Rear-Left Bottom
        bm.verts.new((-0.180, -0.075, 0.010)), # 4: Front-Left Top
        bm.verts.new(( 0.180, -0.075, 0.010)), # 5: Front-Right Top
        bm.verts.new(( 0.180,  0.075, 0.020)), # 6: Rear-Right Top
        bm.verts.new((-0.180,  0.075, 0.020)), # 7: Rear-Left Top
    ]
    f_bottom = bm.faces.new([v_base[0], v_base[1], v_base[2], v_base[3]]) # -Z
    f_top    = bm.faces.new([v_base[4], v_base[7], v_base[6], v_base[5]]) # Sloped Top +Z
    f_front  = bm.faces.new([v_base[0], v_base[4], v_base[5], v_base[1]]) # Front -Y
    f_rear   = bm.faces.new([v_base[2], v_base[6], v_base[7], v_base[3]]) # Rear +Y
    f_left   = bm.faces.new([v_base[3], v_base[7], v_base[4], v_base[0]]) # Left -X
    f_right  = bm.faces.new([v_base[1], v_base[5], v_base[6], v_base[2]]) # Right +X

    bm.normal_update()

    # Materials and UV mapping for Chassis
    f_top.material_index = 0
    set_planar_uv(bm, f_top, u_chassis_top, plane='XY', flip_u=False, flip_v=False)

    f_bottom.material_index = 0
    set_planar_uv(bm, f_bottom, u_bottom_spec, plane='XY', flip_u=False, flip_v=False)

    for f_side in [f_front, f_rear, f_left, f_right]:
        f_side.material_index = 0
        set_planar_uv(bm, f_side, u_dark_side, plane='XZ')

    # 2. Four Non-Slip Rubber Feet on Bottom (Slot 1: M_Rubber)
    # Positioned at 4 corners under the bottom plate (Z: -0.002 to 0.000)
    feet_coords = [
        (-0.160, -0.135, -0.060, -0.045), # Front Left
        ( 0.135,  0.160, -0.060, -0.045), # Front Right
        (-0.160, -0.135,  0.045,  0.060), # Rear Left
        ( 0.135,  0.160,  0.045,  0.060)  # Rear Right
    ]
    for x0, x1, y0, y1 in feet_coords:
        box_foot = add_box(bm, x0, x1, y0, y1, -0.002, 0.000)
        for f in box_foot.values():
            if isinstance(f, bmesh.types.BMFace):
                f.material_index = 1 # Slot 1: M_Rubber
                set_planar_uv(bm, f, u_rubber, plane='XY')

    # 3. Rear Cable Strain Relief Boot (USB / RS-485 connection at center rear)
    # Centered at X: -0.010 to 0.010, Y: 0.075 to 0.088, Z: 0.008 to 0.016
    box_cable = add_box(bm, -0.010, 0.010, 0.075, 0.088, 0.008, 0.016)
    for f in box_cable.values():
        if isinstance(f, bmesh.types.BMFace):
            f.material_index = 1 # M_Rubber
            set_planar_uv(bm, f, u_rubber, plane='XY')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_rubber)
    obj = bpy.data.objects.new("Keyboard_Base", me)
    return obj

def build_key_row(name, mat_atlas, mat_rubber, d_depth, h_height, uv_rect):
    """
    Builds a key row mesh centered at local (0, 0, 0).
    The parent Pivot Empty handles the world positioning and travel animation.
    """
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    u_sides = (1500/2048, 1.0 - 2000/2048, 2000/2048, 1.0 - 1800/2048)

    # Key row span: X: -0.160 to +0.160 (width 0.320m)
    # Local depth centered around Y=0: -d_depth/2 to +d_depth/2
    # Local height: 0 to h_height (sits on base and raises upwards)
    x0, x1 = -0.160, 0.160
    hy = d_depth / 2.0
    box_row = add_box(bm, x0, x1, -hy, hy, 0.0, h_height)

    for face in box_row.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == box_row['top']:
                set_planar_uv(bm, face, uv_rect, plane='XY', flip_u=False, flip_v=False)
            else:
                set_planar_uv(bm, face, u_sides, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_rubber)
    obj = bpy.data.objects.new(name, me)
    return obj

def main():
    print("=" * 70)
    print("Generating SEC_Monitor_Keyboard...")
    print("=" * 70)

    reset_scene()
    mat_atlas, mat_rubber = create_materials()

    # 1. Root Empty: SEC_Monitor_Keyboard at (0, 0, 0)
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.20
    root.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root)

    # 2. Keyboard_Base mesh parented to root
    base = build_keyboard_base(mat_atlas, mat_rubber)
    bpy.context.scene.collection.objects.link(base)
    base.parent = root

    # 3. Key Rows (Key_Row_01 .. Key_Row_05)
    # Dedicated atlas regions for each row:
    # ROW_01 (Function & CCTV Navigation): (20, 620, 1420, 760)
    uv_r1 = (20/2048, 1.0 - 760/2048, 1420/2048, 1.0 - 620/2048)
    # ROW_02 (Numbers & Presets): (20, 780, 1420, 920)
    uv_r2 = (20/2048, 1.0 - 920/2048, 1420/2048, 1.0 - 780/2048)
    # ROW_03 (QWERTY & Zoom): (20, 940, 1420, 1080)
    uv_r3 = (20/2048, 1.0 - 1080/2048, 1420/2048, 1.0 - 940/2048)
    # ROW_04 (ASDFGH & Iris/Focus): (20, 1100, 1420, 1240)
    uv_r4 = (20/2048, 1.0 - 1240/2048, 1420/2048, 1.0 - 1100/2048)
    # ROW_05 (Space & PTZ Pan/Tilt): (20, 1260, 1420, 1400)
    uv_r5 = (20/2048, 1.0 - 1400/2048, 1420/2048, 1.0 - 1260/2048)

    # Sloped heights: Chassis surface slopes from Z=0.010 at front (Y=-0.075) to Z=0.020 at rear (Y=0.075)
    # Z_surface(Y) = 0.015 + (Y / 0.150) * 0.010
    # Recessed well is Y = -0.068 to +0.059 (127mm span)
    # 5 rows: row depth = 17mm
    # Row 1: Function keys (6mm gap to Row 2)
    # Rows 2-5: Main alphanumeric & control cluster (3mm gap)
    rows_data = [
        ("Key_Row_01",  0.0390, uv_r1),
        ("Key_Row_02",  0.0160, uv_r2),
        ("Key_Row_03", -0.0040, uv_r3),
        ("Key_Row_04", -0.0240, uv_r4),
        ("Key_Row_05", -0.0440, uv_r5)
    ]

    key_objects = []
    row_depth = 0.017   # 17mm
    row_height = 0.0035 # 3.5mm raised keys

    for name, y_mid, uv_rect in rows_data:
        z_surf = 0.015 + (y_mid / 0.150) * 0.010

        # Empty pivot for key travel animation (Z stroke: 0.002m)
        pivot = bpy.data.objects.new(f"{name}_Pivot", None)
        pivot.empty_display_type = 'ARROWS'
        pivot.empty_display_size = 0.03
        pivot.location = (0.0, y_mid, z_surf)
        bpy.context.scene.collection.objects.link(pivot)
        pivot.parent = base

        # Custom Properties for Key Stroke & Interactive Action
        pivot["key_travel_mm"] = 2.0
        pivot["stroke_axis"] = "Z"
        pivot["role"] = f"OPERATOR {name.upper()}"

        key_mesh = build_key_row(name, mat_atlas, mat_rubber, row_depth, row_height, uv_rect)
        bpy.context.scene.collection.objects.link(key_mesh)
        key_mesh.parent = pivot
        key_mesh.location = (0.0, 0.0, 0.0) # Local identity transform
        key_objects.append((pivot, key_mesh))

    # Product Metadata Custom Properties on Root
    root["asset_id"] = "SEC_52"
    root["product_model"] = "SEC-KB-884-PRO"
    root["key_switch_type"] = "MEMBRANE_SCISSOR"
    root["interface"] = "USB_2.0_RS485"

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, base]
    for piv, mesh_obj in key_objects:
        export_objects.extend([piv, mesh_obj])

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

    status = "SUCCESS" if (total_tris <= MAX_TRIS and mesh_count >= 6 and empty_count >= 6) else "FAILED"
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
