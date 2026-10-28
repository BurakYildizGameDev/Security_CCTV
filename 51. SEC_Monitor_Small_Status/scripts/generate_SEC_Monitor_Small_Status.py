"""
=============================================================================
Security CCTV Asset Production Suite - Asset 51
Asset Name: SEC_Monitor_Small_Status (Kucuk Durum Monitoru)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Monitor_Small_Status.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Monitor_Small_Status.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
SCREEN_PATH = os.path.join(EXPORTS_DIR, "T_Screen.png")

ASSET_NAME = "SEC_Monitor_Small_Status"
MAX_TRIS = 280

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
        bsdf_s.inputs["Emission Strength"].default_value = 1.35
        bsdf_s.inputs["Roughness"].default_value = 0.15

    return mat_atlas, mat_screen

def setup_slots(mesh, mat_atlas, mat_screen):
    mesh.materials.append(mat_atlas)   # Slot 0
    mesh.materials.append(mat_screen)  # Slot 1

def set_planar_uv(bm, face, rect, plane='XZ', flip_u=False, flip_v=False):
    """Maps quad UV accurately based on vertex coordinate bounds in the given plane."""
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = rect
    if flip_u:
        u0, u1 = u1, u0
    if flip_v:
        v0, v1 = v1, v0

    if plane == 'XZ':
        xs = [loop.vert.co.x for loop in face.loops]
        zs = [loop.vert.co.z for loop in face.loops]
        min_x, max_x = min(xs), max(xs)
        min_z, max_z = min(zs), max(zs)
        dx = max_x - min_x if max_x > min_x else 1.0
        dz = max_z - min_z if max_z > min_z else 1.0

        for loop in face.loops:
            tx = (loop.vert.co.x - min_x) / dx
            tz = (loop.vert.co.z - min_z) / dz
            loop[uv_layer].uv = (u0 + tx * (u1 - u0), v0 + tz * (v1 - v0))
    elif plane == 'XY':
        xs = [loop.vert.co.x for loop in face.loops]
        ys = [loop.vert.co.y for loop in face.loops]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        dx = max_x - min_x if max_x > min_x else 1.0
        dy = max_y - min_y if max_y > min_y else 1.0

        for loop in face.loops:
            tx = (loop.vert.co.x - min_x) / dx
            ty = (loop.vert.co.y - min_y) / dy
            loop[uv_layer].uv = (u0 + tx * (u1 - u0), v0 + ty * (v1 - v0))
    else: # YZ
        ys = [loop.vert.co.y for loop in face.loops]
        zs = [loop.vert.co.z for loop in face.loops]
        min_y, max_y = min(ys), max(ys)
        min_z, max_z = min(zs), max(zs)
        dy = max_y - min_y if max_y > min_y else 1.0
        dz = max_z - min_z if max_z > min_z else 1.0

        for loop in face.loops:
            ty = (loop.vert.co.y - min_y) / dy
            tz = (loop.vert.co.z - min_z) / dz
            loop[uv_layer].uv = (u0 + ty * (u1 - u0), v0 + tz * (v1 - v0))

def add_box(bm, x0, x1, y0, y1, z0, z1):
    """Builds a solid 6-sided cuboid with correct outward normals."""
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
    # Outward windings:
    f_rear  = bm.faces.new([v[0], v[1], v[2], v[3]]) # facing -Y
    f_front = bm.faces.new([v[5], v[4], v[7], v[6]]) # facing +Y
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]]) # facing -Z
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]]) # facing +Z
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]]) # facing -X
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]]) # facing +X
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

def build_mount_bracket(mat_atlas, mat_screen):
    me = bpy.data.meshes.new("Mount_Bracket")
    bm = bmesh.new()

    # UV Atlas Regions
    uv_bracket = (630/1024, 1.0 - 992/1024, 850/1024, 1.0 - 560/1024)
    uv_steel   = (880/1024, 1.0 - 880/1024, 1024/1024, 1.0 - 800/1024)

    # 1. Base Wall / Desk Plate: X: -0.045 to 0.045, Y: 0.000 to 0.008, Z: -0.045 to 0.045
    box_base = add_box(bm, -0.045, 0.045, 0.0, 0.008, -0.045, 0.045)
    for face in box_base.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == box_base['rear']:
                set_planar_uv(bm, face, uv_bracket, plane='XZ', flip_u=False)
            else:
                set_planar_uv(bm, face, uv_steel, plane='XZ')

    # 2. Hinge Stand Arm: X: -0.015 to 0.015, Y: 0.008 to 0.030, Z: -0.022 to 0.022
    box_arm = add_box(bm, -0.015, 0.015, 0.008, 0.030, -0.022, 0.022)
    for face in box_arm.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            set_planar_uv(bm, face, uv_steel, plane='XZ')

    # 3. Swivel Pivot Collar: X: -0.025 to 0.025, Y: 0.026 to 0.035, Z: -0.012 to 0.012
    box_swivel = add_box(bm, -0.025, 0.025, 0.026, 0.035, -0.012, 0.012)
    for face in box_swivel.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            set_planar_uv(bm, face, uv_steel, plane='XZ')

    # 4. Left Thumb-Screw Lock: X: -0.033 to -0.025, Y: 0.028 to 0.033, Z: -0.008 to 0.008
    box_tl = add_box(bm, -0.033, -0.025, 0.028, 0.033, -0.008, 0.008)
    for face in box_tl.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            set_planar_uv(bm, face, uv_bracket, plane='YZ')

    # 5. Right Thumb-Screw Lock: X: 0.025 to 0.033, Y: 0.028 to 0.033, Z: -0.008 to 0.008
    box_tr = add_box(bm, 0.025, 0.033, 0.028, 0.033, -0.008, 0.008)
    for face in box_tr.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            set_planar_uv(bm, face, uv_bracket, plane='YZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen)
    obj = bpy.data.objects.new("Mount_Bracket", me)
    return obj

def build_housing(mat_atlas, mat_screen):
    me = bpy.data.meshes.new("Housing")
    bm = bmesh.new()

    # Texture UV Coordinates
    # Front Bezel (32, 32, 992, 480)
    # Bezel total spans X: -0.090 to 0.090 (width 0.180m), Z: -0.065 to 0.065 (height 0.130m)
    # Atlas UV coordinates:
    # U: 32/1024 .. 992/1024
    # V: (1024-480)/1024 .. (1024-32)/1024 -> 544/1024 .. 992/1024
    u_f0, v_f0 = 32/1024, 544/1024
    u_f1, v_f1 = 992/1024, 992/1024

    # Rear Housing UV: (32, 512, 600, 992)
    u_r0, v_r0 = 32/1024, 1.0 - 992/1024
    u_r1, v_r1 = 600/1024, 1.0 - 512/1024

    # Chassis Dark Swatch (for sides/cavity): (880, 560, 1024, 640)
    u_dark = (880/1024, 1.0 - 640/1024, 1024/1024, 1.0 - 560/1024)

    # Inner Recess Swatch (pitch black behind screen): (880, 960, 1024, 1024)
    u_recess = (880/1024, 1.0 - 1024/1024, 1024/1024, 1.0 - 960/1024)

    # 1. Rear Electronic Inset / Louver Collar: X: -0.065 to 0.065, Y: 0.025 to 0.035, Z: -0.045 to 0.045
    box_rear = add_box(bm, -0.065, 0.065, 0.025, 0.035, -0.045, 0.045)
    for face in box_rear.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == box_rear['rear']:
                set_planar_uv(bm, face, (u_r0, v_r0, u_r1, v_r1), plane='XZ', flip_u=False)
            else:
                set_planar_uv(bm, face, u_dark, plane='XZ')

    # 2. Main Housing Chassis Body: X: -0.090 to 0.090, Y: 0.035 to 0.054, Z: -0.065 to 0.065
    box_body = add_box(bm, -0.090, 0.090, 0.035, 0.054, -0.065, 0.065)
    for face in box_body.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == box_body['front']:
                # The front face is at Y=0.054, which sits 2mm behind the screen (Y=0.056)
                # Map this face to pure black INNER_RECESS so zero text or light ever bleeds
                set_planar_uv(bm, face, u_recess, plane='XZ')
            else:
                set_planar_uv(bm, face, u_dark, plane='XZ')

    # 3. Outer Front Bezel Rim (Surrounds the screen, extends forward from Y=0.054 to Y=0.058)
    # Overall Bezel Bounds: X: -0.090 to 0.090, Z: -0.065 to 0.065
    # Screen Opening Cutout: X: -0.070 to 0.070, Z: -0.025 to 0.050
    # Function to map a sub-rectangle of the front bezel proportionally
    def map_bezel_quad(f_quad, x_min, x_max, z_min, z_max):
        # Calculate sub-UV in bezel region
        tx0 = (x_min - (-0.090)) / 0.180
        tx1 = (x_max - (-0.090)) / 0.180
        tz0 = (z_min - (-0.065)) / 0.130
        tz1 = (z_max - (-0.065)) / 0.130

        sub_u0 = u_f0 + tx0 * (u_f1 - u_f0)
        sub_u1 = u_f0 + tx1 * (u_f1 - u_f0)
        sub_v0 = v_f0 + tz0 * (v_f1 - v_f0)
        sub_v1 = v_f0 + tz1 * (v_f1 - v_f0)

        set_planar_uv(bm, f_quad, (sub_u0, sub_v0, sub_u1, sub_v1), plane='XZ', flip_u=True)

    # 3a. Top Bezel (Contains SEC-MON 07S & LED Status Indicators)
    # X: -0.090 to 0.090, Y: 0.054 to 0.058, Z: 0.050 to 0.065
    b_top = add_box(bm, -0.090, 0.090, 0.054, 0.058, 0.050, 0.065)
    for face in b_top.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == b_top['front']:
                map_bezel_quad(face, -0.090, 0.090, 0.050, 0.065)
            else:
                set_planar_uv(bm, face, u_dark, plane='XZ')

    # 3b. Bottom Bezel (Contains SEC-TELEMETRY SYSTEMS branding & Button Sockets)
    # X: -0.090 to 0.090, Y: 0.054 to 0.058, Z: -0.065 to -0.040
    b_bot = add_box(bm, -0.090, 0.090, 0.054, 0.058, -0.065, -0.040)
    for face in b_bot.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == b_bot['front']:
                map_bezel_quad(face, -0.090, 0.090, -0.065, -0.040)
            else:
                set_planar_uv(bm, face, u_dark, plane='XZ')

    # 3c. Left Bezel (Flank)
    # X: -0.090 to -0.070, Y: 0.054 to 0.058, Z: -0.040 to 0.050
    b_left = add_box(bm, -0.090, -0.070, 0.054, 0.058, -0.040, 0.050)
    for face in b_left.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == b_left['front']:
                map_bezel_quad(face, -0.090, -0.070, -0.040, 0.050)
            else:
                set_planar_uv(bm, face, u_dark, plane='XZ')

    # 3d. Right Bezel (Flank)
    # X: 0.070 to 0.090, Y: 0.054 to 0.058, Z: -0.040 to 0.050
    b_right = add_box(bm, 0.070, 0.090, 0.054, 0.058, -0.040, 0.050)
    for face in b_right.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == b_right['front']:
                map_bezel_quad(face, 0.070, 0.090, -0.040, 0.050)
            else:
                set_planar_uv(bm, face, u_dark, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen)
    obj = bpy.data.objects.new("Housing", me)
    return obj

def build_screen_surface(mat_atlas, mat_screen):
    """
    Screen surface is a recessed quad placed at Y=0.056.
    The outer bezel rim sits at Y=0.058 (2mm forward).
    The backing housing wall sits at Y=0.054 (2mm behind).
    This completely eliminates any possibility of Z-fighting while creating realistic depth.
    """
    me = bpy.data.meshes.new("Screen_Surface")
    bm = bmesh.new()

    y_pos = 0.056
    v0 = bm.verts.new((-0.070, y_pos, -0.040))
    v1 = bm.verts.new(( 0.070, y_pos, -0.040))
    v2 = bm.verts.new(( 0.070, y_pos,  0.050))
    v3 = bm.verts.new((-0.070, y_pos,  0.050))

    # Face facing +Y
    face = bm.faces.new([v1, v0, v3, v2])
    bm.normal_update()
    face.material_index = 1 # Slot 1: M_Screen

    # Full screen UV unwrap: 0..1, flip_u=True for +Y normal
    set_planar_uv(bm, face, (0.0, 0.0, 1.0, 1.0), plane='XZ', flip_u=True)

    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen)
    obj = bpy.data.objects.new("Screen_Surface", me)
    return obj

def build_button_cap(name, mat_atlas, mat_screen, x0, x1, z0, z1, uv_rect):
    """Builds a raised 3D tactile button cap positioned on the bottom bezel strip."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    # Sits on the bezel face at Y=0.058, protruding to Y=0.0605 (2.5mm travel cap)
    box = add_box(bm, x0, x1, 0.0575, 0.0605, z0, z1)
    u_dark = (880/1024, 1.0 - 640/1024, 1024/1024, 1.0 - 560/1024)

    for face in box.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if face == box['front']:
                # Front face facing +Y: flip_u=True corrects mirror effect so text reads normally
                set_planar_uv(bm, face, uv_rect, plane='XZ', flip_u=True)
            else:
                set_planar_uv(bm, face, u_dark, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_atlas, mat_screen)
    obj = bpy.data.objects.new(name, me)
    return obj

def main():
    print("=" * 70)
    print("Generating SEC_Monitor_Small_Status...")
    print("=" * 70)

    reset_scene()
    mat_atlas, mat_screen = create_materials()

    # 1. Root Empty: SEC_Monitor_Small_Status at (0, 0, 0)
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.10
    root.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root)

    # 2. Mount_Bracket mesh
    mount = build_mount_bracket(mat_atlas, mat_screen)
    bpy.context.scene.collection.objects.link(mount)
    mount.parent = root

    # 3. Housing mesh
    housing = build_housing(mat_atlas, mat_screen)
    bpy.context.scene.collection.objects.link(housing)
    housing.parent = root

    # 4. Screen_Surface mesh
    screen = build_screen_surface(mat_atlas, mat_screen)
    bpy.context.scene.collection.objects.link(screen)
    screen.parent = housing

    # 5. Buttons:
    # On Bezel, Menu Socket is at Atlas: x in [680, 768] -> relative x bounds: -0.048 to -0.032
    # Enter Socket is at Atlas: x in [800, 888] -> relative x bounds: -0.070 to -0.054
    # Height: z: -0.059 to -0.046
    # Atlas UV for Menu Button: (672, 490, 766, 538)
    uv_menu = (672/1024, 1.0 - 538/1024, 766/1024, 1.0 - 490/1024)
    # Atlas UV for Enter Button: (792, 490, 886, 538)
    uv_enter = (792/1024, 1.0 - 538/1024, 886/1024, 1.0 - 490/1024)

    btn_menu = build_button_cap("Control_Button_Left", mat_atlas, mat_screen,
                                -0.048, -0.032, -0.059, -0.046, uv_menu)
    bpy.context.scene.collection.objects.link(btn_menu)
    btn_menu.parent = housing

    btn_enter = build_button_cap("Control_Button_Right", mat_atlas, mat_screen,
                                 -0.070, -0.054, -0.059, -0.046, uv_enter)
    bpy.context.scene.collection.objects.link(btn_enter)
    btn_enter.parent = housing

    # Custom Properties for Interactive Elements
    housing["tilt_angle_min"] = -30.0
    housing["tilt_angle_max"] = 30.0
    housing["pan_angle_min"] = -45.0
    housing["pan_angle_max"] = 45.0
    btn_menu["button_role"] = "MENU / NAVIGATION"
    btn_enter["button_role"] = "ENTER / SELECT"

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, mount, housing, screen, btn_menu, btn_enter]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root

    # Set 3D Viewport to MATERIAL preview
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

    # Pack all textures directly into blend
    try:
        bpy.ops.file.pack_all()
    except Exception:
        pass

    # Save .blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"[Blend] Saved: {BLEND_PATH}")

    # Export FBX with standard parameters
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
            # Triangulate to get exact tris
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

    status = "SUCCESS" if (total_tris <= MAX_TRIS and mesh_count >= 5) else "FAILED"
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
        raise RuntimeError(f"QA Validation FAILED: tris={total_tris} > {MAX_TRIS} or mesh_count={mesh_count} < 5")

if __name__ == "__main__":
    main()
