"""
Security CCTV Asset Production Suite - Asset 61
Asset Name: SEC_Alarm_Control_Panel (Fire & Security Alarm Control Panel)
Generator Script for Blender CLI
"""

import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Euler, Matrix

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Control_Panel.blend")
FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Control_Panel.fbx")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")

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
    bsdf.inputs["Roughness"].default_value = 0.45
    mat_atlas.diffuse_color = (0.68, 0.12, 0.15, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. M_Screen (Slot 1)
    mat_screen = bpy.data.materials.new(name="M_Screen")
    mat_screen.use_nodes = True
    bsdf_scr = mat_screen.node_tree.nodes.get("Principled BSDF")
    if os.path.exists(ATLAS_PATH):
        tex_scr = mat_screen.node_tree.nodes.new("ShaderNodeTexImage")
        tex_scr.image = bpy.data.images.get(os.path.basename(ATLAS_PATH)) or bpy.data.images.load(ATLAS_PATH)
        mat_screen.node_tree.links.new(tex_scr.outputs["Color"], bsdf_scr.inputs["Base Color"])
        mat_screen.node_tree.links.new(tex_scr.outputs["Color"], bsdf_scr.inputs["Emission Color"])
        bsdf_scr.inputs["Emission Strength"].default_value = 1.8
    else:
        bsdf_scr.inputs["Base Color"].default_value = (0.05, 0.18, 0.10, 1.0)
        bsdf_scr.inputs["Emission Color"].default_value = (0.2, 0.9, 0.4, 1.0)
        bsdf_scr.inputs["Emission Strength"].default_value = 1.8
    bsdf_scr.inputs["Roughness"].default_value = 0.15
    mat_screen.diffuse_color = (0.1, 0.6, 0.3, 1.0)
    materials["M_Screen"] = mat_screen

    # 3. M_Emission (Slot 2)
    mat_emit = bpy.data.materials.new(name="M_Emission")
    mat_emit.use_nodes = True
    bsdf_emit = mat_emit.node_tree.nodes.get("Principled BSDF")
    bsdf_emit.inputs["Base Color"].default_value = (0.2, 0.95, 0.3, 1.0)
    bsdf_emit.inputs["Emission Color"].default_value = (0.2, 0.95, 0.3, 1.0)
    bsdf_emit.inputs["Emission Strength"].default_value = 8.0
    mat_emit.diffuse_color = (0.2, 0.95, 0.3, 1.0)
    materials["M_Emission"] = mat_emit

    # 4. M_Metal (Slot 3)
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    bsdf_met = mat_metal.node_tree.nodes.get("Principled BSDF")
    bsdf_met.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    bsdf_met.inputs["Metallic"].default_value = 0.95
    bsdf_met.inputs["Roughness"].default_value = 0.20
    mat_metal.diffuse_color = (0.75, 0.78, 0.82, 1.0)
    materials["M_Metal"] = mat_metal

    return materials

def assign_material_slots(obj, mat_dict):
    slot_order = ["M_Security_Atlas", "M_Screen", "M_Emission", "M_Metal"]
    for mat_name in slot_order:
        obj.data.materials.append(mat_dict[mat_name])

def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv_rect
    xs = [l.vert.co.x for l in face.loops]
    zs = [l.vert.co.z for l in face.loops]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    dx = max_x - min_x if max_x > min_x else 1e-5
    dz = max_z - min_z if max_z > min_z else 1e-5
    for l in face.loops:
        tx = (l.vert.co.x - min_x) / dx
        tz = (l.vert.co.z - min_z) / dz
        if flip_u:
            tx = 1.0 - tx
        if flip_v:
            tz = 1.0 - tz
        l[uv_layer].uv = (u0 + tx * (u1 - u0), v0 + tz * (v1 - v0))

def set_face_uv_constant(bm, face, uv_point):
    uv_layer = bm.loops.layers.uv.verify()
    for l in face.loops:
        l[uv_layer].uv = uv_point

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
    f_front = bm.faces.new([v[0], v[1], v[2], v[3]]) # -Y (toward wall if Y=0)
    f_rear  = bm.faces.new([v[5], v[4], v[7], v[6]]) # +Y (front face facing room!)
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]]) # -Z
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]]) # +Z
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]]) # -X
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]]) # +X
    bm.normal_update()
    return {
        'back': f_front, 'front': f_rear, 'bot': f_bot,
        'top': f_top, 'left': f_left, 'right': f_right, 'verts': v
    }

def mark_sharp_edges(bm, angle_deg=35.0):
    thresh = math.radians(angle_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            if edge.calc_face_angle() > thresh:
                edge.smooth = False
        else:
            edge.smooth = False

def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    materials = create_materials()

    # Root Empty: SEC_Alarm_Control_Panel at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Alarm_Control_Panel", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.25
    bpy.context.collection.objects.link(root)

    # Coordinates:
    # Width X: -0.190 to +0.190 (380mm)
    # Depth Y: 0.000 (wall) to 0.115m (front chassis)
    # Height Z: -0.230 to +0.230 (460mm)

    # -------------------------------------------------------------------------
    # 1. CABINET (Mesh) - Wall mount cabinet body
    # -------------------------------------------------------------------------
    cab_me = bpy.data.meshes.new("Cabinet")
    cab_bm = bmesh.new()

    box = add_box(cab_bm, -0.190, 0.190, 0.000, 0.115, -0.230, 0.230)
    uv_cab_front = (1020/2048, 1.0 - 1150/2048, 1980/2048, 1.0 - 50/2048)
    uv_cab_side  = (50/2048, 1.0 - 1650/2048, 1980/2048, 1.0 - 1200/2048)
    uv_swatch_dark = ((540 + 200)/2048, 1.0 - 1850/2048)

    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front': # +Y face (operator interface)
                face.material_index = 0 # M_Security_Atlas
                set_face_uv_rect(cab_bm, face, uv_cab_front, flip_u=True)
            elif k in ['left', 'right', 'top', 'bot']:
                face.material_index = 0
                set_face_uv_rect(cab_bm, face, uv_cab_side)
            else:
                face.material_index = 0
                set_face_uv_constant(cab_bm, face, uv_swatch_dark)

    mark_sharp_edges(cab_bm)
    cab_bm.to_mesh(cab_me)
    cab_bm.free()

    cab_obj = bpy.data.objects.new("Cabinet", cab_me)
    bpy.context.collection.objects.link(cab_obj)
    cab_obj.parent = root
    assign_material_slots(cab_obj, materials)

    # -------------------------------------------------------------------------
    # 2. DISPLAY (Mesh) - LCD text/graphical screen (Child of Cabinet)
    # -------------------------------------------------------------------------
    disp_me = bpy.data.meshes.new("Display")
    disp_bm = bmesh.new()

    # Screen placed at Z: +0.065 to +0.155, X: -0.125 to +0.125, Y: 0.115 to 0.118
    dbox = add_box(disp_bm, -0.125, 0.125, 0.115, 0.118, 0.065, 0.155)
    uv_scr = (1060/2048, 1.0 - 390/2048, 1940/2048, 1.0 - 90/2048)
    uv_bezel = ((1040+200)/2048, 1.0 - 1850/2048)

    for k, face in dbox.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front': # +Y facing room
                face.material_index = 1 # M_Screen
                set_face_uv_rect(disp_bm, face, uv_scr, flip_u=True)
            else:
                face.material_index = 0 # M_Security_Atlas
                set_face_uv_constant(disp_bm, face, uv_bezel)

    mark_sharp_edges(disp_bm)
    disp_bm.to_mesh(disp_me)
    disp_bm.free()

    disp_obj = bpy.data.objects.new("Display", disp_me)
    bpy.context.collection.objects.link(disp_obj)
    disp_obj.parent = cab_obj
    assign_material_slots(disp_obj, materials)

    # -------------------------------------------------------------------------
    # 3. LED_ARRAY (Mesh) - Status LED indicators (Child of Cabinet)
    # -------------------------------------------------------------------------
    led_me = bpy.data.meshes.new("LED_Array")
    led_bm = bmesh.new()

    # LED Bezel base strip
    lbox = add_box(led_bm, -0.130, 0.130, 0.115, 0.117, 0.030, 0.055)
    uv_led_strip = (1060/2048, 1.0 - 510/2048, 1940/2048, 1.0 - 420/2048)
    for k, face in lbox.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if k == 'front':
                set_face_uv_rect(led_bm, face, uv_led_strip, flip_u=True)
            else:
                set_face_uv_constant(led_bm, face, uv_swatch_dark)

    # 8 individual 6-sided raised LED lenses
    for i in range(8):
        lx = -0.105 + i * 0.030
        lz = 0.042
        r_led = 0.0035
        # 6-sided cylinder
        verts_bot = []
        verts_top = []
        for s in range(6):
            ang = s * (2.0 * math.pi / 6)
            vx = lx + r_led * math.cos(ang)
            vz = lz + r_led * math.sin(ang)
            verts_bot.append(led_bm.verts.new((vx, 0.117, vz)))
            verts_top.append(led_bm.verts.new((vx, 0.119, vz)))
        # cap
        f_cap = led_bm.faces.new(verts_top)
        f_cap.material_index = 2 # M_Emission
        set_face_uv_constant(led_bm, f_cap, ((1000)/2048, 1.0 - 1500/2048))
        # sides
        for s in range(6):
            s_next = (s + 1) % 6
            f_side = led_bm.faces.new([verts_bot[s], verts_bot[s_next], verts_top[s_next], verts_top[s]])
            f_side.material_index = 2
            set_face_uv_constant(led_bm, f_side, ((1000)/2048, 1.0 - 1500/2048))

    mark_sharp_edges(led_bm)
    led_bm.to_mesh(led_me)
    led_bm.free()

    led_obj = bpy.data.objects.new("LED_Array", led_me)
    bpy.context.collection.objects.link(led_obj)
    led_obj.parent = cab_obj
    assign_material_slots(led_obj, materials)

    # -------------------------------------------------------------------------
    # 4. KEYPAD (Mesh) - Control button pad (Child of Cabinet)
    # -------------------------------------------------------------------------
    key_me = bpy.data.meshes.new("Keypad")
    key_bm = bmesh.new()

    # Raised keypad mounting island: X: -0.135 to 0.135, Z: -0.210 to 0.020, Y: 0.115 to 0.117
    kbox = add_box(key_bm, -0.135, 0.135, 0.115, 0.117, -0.210, 0.020)
    uv_kpad = (1060/2048, 1.0 - 1100/2048, 1940/2048, 1.0 - 540/2048)
    for k, face in kbox.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if k == 'front':
                set_face_uv_rect(key_bm, face, uv_kpad, flip_u=True)
            else:
                set_face_uv_constant(key_bm, face, uv_swatch_dark)

    # 6 function button raised blocks
    btn_defs = [
        (-0.080, -0.005, 0, 0), (0.000, -0.005, 0, 1), (0.080, -0.005, 0, 2),
        (-0.080, -0.035, 1, 0), (0.000, -0.035, 1, 1), (0.080, -0.035, 1, 2)
    ]
    for bx_c, bz_c, row, col in btn_defs:
        fb = add_box(key_bm, bx_c - 0.032, bx_c + 0.032, 0.117, 0.120, bz_c - 0.010, bz_c + 0.010)
        # Atlas button bounds:
        ab_x = 1020 + 50 + col * 295
        ab_y = 50 + 540 + row * 85
        uv_btn = (ab_x / 2048, 1.0 - (ab_y + 65) / 2048, (ab_x + 270) / 2048, 1.0 - ab_y / 2048)
        for k, face in fb.items():
            if isinstance(face, bmesh.types.BMFace):
                face.material_index = 0
                if k == 'front':
                    set_face_uv_rect(key_bm, face, uv_btn, flip_u=True)
                else:
                    set_face_uv_constant(key_bm, face, uv_swatch_dark)

    # 12 numeric key blocks (3 columns x 4 rows)
    for r in range(4):
        for c in range(3):
            nx_c = 0.045 - c * 0.045 # Left to right from viewer's perspective
            nz_c = -0.075 - r * 0.030
            nb = add_box(key_bm, nx_c - 0.016, nx_c + 0.016, 0.117, 0.120, nz_c - 0.010, nz_c + 0.010)
            ak_x = 1020 + 260 + 15 + c * 130
            ak_y = 50 + 720 + 35 + r * 70
            uv_key = (ak_x / 2048, 1.0 - (ak_y + 55) / 2048, (ak_x + 110) / 2048, 1.0 - ak_y / 2048)
            for k, face in nb.items():
                if isinstance(face, bmesh.types.BMFace):
                    face.material_index = 0
                    if k == 'front':
                        set_face_uv_rect(key_bm, face, uv_key, flip_u=True)
                    else:
                        set_face_uv_constant(key_bm, face, uv_swatch_dark)

    mark_sharp_edges(key_bm)
    key_bm.to_mesh(key_me)
    key_bm.free()

    key_obj = bpy.data.objects.new("Keypad", key_me)
    bpy.context.collection.objects.link(key_obj)
    key_obj.parent = cab_obj
    assign_material_slots(key_obj, materials)

    # -------------------------------------------------------------------------
    # 5. DOOR HINGE PIVOT (Empty at door hinge on screen left: +X = +0.190m)
    # -------------------------------------------------------------------------
    hinge_pivot = bpy.data.objects.new("Door_Hinge_Pivot", None)
    hinge_pivot.empty_display_type = 'SINGLE_ARROW'
    hinge_pivot.empty_display_size = 0.15
    hinge_pivot.location = (0.190, 0.115, 0.000)
    # Invert local Y & Z so positive rotation 0°..100° around local Z swings door forward into +Y
    hinge_pivot.rotation_euler = (math.pi, 0, 0)
    bpy.context.collection.objects.link(hinge_pivot)
    hinge_pivot.parent = root

    # Custom properties for game engine rotation limits
    hinge_pivot["min_rot_z"] = 0.0
    hinge_pivot["max_rot_z"] = 100.0
    hinge_pivot["rot_axis"] = "Z"

    # Add Limit Rotation constraint in Blender
    con = hinge_pivot.constraints.new(type='LIMIT_ROTATION')
    con.owner_space = 'LOCAL'
    con.use_limit_x = True
    con.use_limit_y = True
    con.use_limit_z = True
    con.min_x = 0.0
    con.max_x = 0.0
    con.min_y = 0.0
    con.max_y = 0.0
    con.min_z = math.radians(0.0)
    con.max_z = math.radians(100.0)

    # -------------------------------------------------------------------------
    # 6. FRONT_DOOR (Mesh) - Child of Door_Hinge_Pivot
    # -------------------------------------------------------------------------
    door_me = bpy.data.meshes.new("Front_Door")
    door_bm = bmesh.new()

    # Modeled in local space of Door_Hinge_Pivot!
    # Hinge is at local (0, 0, 0).
    # Door spans local X: -0.380 to 0.000 (covers world X: -0.190 to +0.190)
    door_box = add_box(door_bm, -0.380, 0.000, 0.000, 0.012, -0.230, 0.230)
    uv_door_front = (50/2048, 1.0 - 1150/2048, 950/2048, 1.0 - 50/2048)
    uv_swatch_red = ((50 + 200)/2048, 1.0 - 1850/2048)

    for k, face in door_box.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front': # Outer facing room
                face.material_index = 0 # M_Security_Atlas
                set_face_uv_rect(door_bm, face, uv_door_front, flip_u=True)
            else:
                face.material_index = 0
                set_face_uv_constant(door_bm, face, uv_swatch_red)

    # Lock cylinder at swinging edge: mathematically concentric with lock decal at (kx=850, ky=770)
    # lx = -0.380 + (1.0 - 800/900) * 0.380 = -0.33778m
    # lz = -0.230 + (380/1100) * 0.460 = -0.07109m
    r_lock = 0.010
    lx = -0.33778
    lz = -0.07109
    lock_verts_bot = []
    lock_verts_top = []
    for s in range(12):
        ang = s * (2.0 * math.pi / 12)
        vx = lx + r_lock * math.cos(ang)
        vz = lz + r_lock * math.sin(ang)
        lock_verts_bot.append(door_bm.verts.new((vx, 0.012, vz)))
        lock_verts_top.append(door_bm.verts.new((vx, 0.015, vz)))
    f_lock_cap = door_bm.faces.new(lock_verts_top)
    f_lock_cap.material_index = 0 # M_Security_Atlas (renders keyhole decal)
    # Map cap directly to keyhole decal center:
    kx, ky = 850, 770
    uv_lock_cap = ((kx - 24)/2048, 1.0 - (ky + 24)/2048, (kx + 24)/2048, 1.0 - (ky - 24)/2048)
    set_face_uv_rect(door_bm, f_lock_cap, uv_lock_cap, flip_u=True)
    for s in range(12):
        s_next = (s + 1) % 12
        f_lside = door_bm.faces.new([lock_verts_bot[s], lock_verts_bot[s_next], lock_verts_top[s_next], lock_verts_top[s]])
        f_lside.material_index = 3 # M_Metal chamfer side rim
        set_face_uv_constant(door_bm, f_lside, ((1040+200)/2048, 1.0 - 1850/2048))

    mark_sharp_edges(door_bm)
    door_bm.to_mesh(door_me)
    door_bm.free()

    door_obj = bpy.data.objects.new("Front_Door", door_me)
    bpy.context.collection.objects.link(door_obj)
    door_obj.parent = hinge_pivot
    assign_material_slots(door_obj, materials)

    # -------------------------------------------------------------------------
    # QA Check & Triangulation
    # -------------------------------------------------------------------------
    total_tris = 0
    meshes = [cab_obj, disp_obj, led_obj, key_obj, door_obj]
    for obj in meshes:
        me = obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        tris = len(bm.faces)
        total_tris += tris
        bm.free()
        obj.to_mesh_clear()

    print(f"[Geometry] Total meshes: {len(meshes)}, Total tris: {total_tris} (limit: 600)")
    assert total_tris <= 600, f"Tris limit exceeded: {total_tris} > 600"

    # Viewport shading mode to MATERIAL
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'

    # Pack textures into .blend
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"[Export] Saved blend: {BLEND_PATH}")

    # Remove any .blend1 backup files
    blend1 = BLEND_PATH + "1"
    if os.path.exists(blend1):
        try:
            os.remove(blend1)
        except Exception:
            pass

    # Select all hierarchy for FBX export
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for child in [cab_obj, disp_obj, led_obj, key_obj, hinge_pivot, door_obj]:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root

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
        path_mode='AUTO',
        use_custom_props=True
    )
    print(f"[Export] Saved FBX: {FBX_PATH}")

    # QA Re-import test in clean scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)
    imported_objs = bpy.context.selected_objects
    imp_meshes = [o for o in imported_objs if o.type == 'MESH']
    imp_empties = [o for o in imported_objs if o.type == 'EMPTY']
    imp_tris = 0
    for o in imp_meshes:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        imp_tris += len(bm.faces)
        bm.free()

    print(f"[QA Reimport] Meshes: {len(imp_meshes)}, Empties: {len(imp_empties)}, Tris: {imp_tris}")

    # Clean export folder of .blend1 again
    if os.path.exists(blend1):
        try:
            os.remove(blend1)
        except Exception:
            pass

    # Update manifest
    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            pass

    manifest_data["SEC_Alarm_Control_Panel"] = {
        "status": "SUCCESS",
        "fbx_path": FBX_PATH,
        "blend_path": BLEND_PATH,
        "total_tris": imp_tris,
        "max_tris": 600,
        "mesh_count": len(imp_meshes),
        "empty_count": len(imp_empties),
        "materials": ["M_Security_Atlas", "M_Screen", "M_Emission", "M_Metal"]
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)
    print(f"[Manifest] Updated {MANIFEST_PATH} with status SUCCESS")

if __name__ == "__main__":
    build_scene()
