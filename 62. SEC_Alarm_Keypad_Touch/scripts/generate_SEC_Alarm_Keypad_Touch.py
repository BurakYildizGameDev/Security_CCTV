"""
Security CCTV Asset Production Suite - Asset 62
Asset Name: SEC_Alarm_Keypad_Touch (Touchscreen Security Alarm Keypad)
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

BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Keypad_Touch.blend")
FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Keypad_Touch.fbx")
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
    bsdf.inputs["Roughness"].default_value = 0.35
    mat_atlas.diffuse_color = (0.20, 0.22, 0.26, 1.0)
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
        bsdf_scr.inputs["Emission Strength"].default_value = 1.4
    else:
        bsdf_scr.inputs["Base Color"].default_value = (0.05, 0.08, 0.12, 1.0)
        bsdf_scr.inputs["Emission Color"].default_value = (0.1, 0.3, 0.6, 1.0)
        bsdf_scr.inputs["Emission Strength"].default_value = 1.4
    bsdf_scr.inputs["Roughness"].default_value = 0.08
    mat_screen.diffuse_color = (0.05, 0.08, 0.12, 1.0)
    materials["M_Screen"] = mat_screen

    # 3. M_Emission (Slot 2)
    mat_emit = bpy.data.materials.new(name="M_Emission")
    mat_emit.use_nodes = True
    bsdf_emit = mat_emit.node_tree.nodes.get("Principled BSDF")
    if os.path.exists(ATLAS_PATH):
        tex_emit = mat_emit.node_tree.nodes.new("ShaderNodeTexImage")
        tex_emit.image = bpy.data.images.get(os.path.basename(ATLAS_PATH)) or bpy.data.images.load(ATLAS_PATH)
        mat_emit.node_tree.links.new(tex_emit.outputs["Color"], bsdf_emit.inputs["Base Color"])
        mat_emit.node_tree.links.new(tex_emit.outputs["Color"], bsdf_emit.inputs["Emission Color"])
        bsdf_emit.inputs["Emission Strength"].default_value = 2.5
    else:
        bsdf_emit.inputs["Base Color"].default_value = (0.2, 0.95, 0.45, 1.0)
        bsdf_emit.inputs["Emission Color"].default_value = (0.2, 0.95, 0.45, 1.0)
        bsdf_emit.inputs["Emission Strength"].default_value = 2.5
    bsdf_emit.inputs["Roughness"].default_value = 0.2
    mat_emit.diffuse_color = (0.15, 0.85, 0.45, 1.0)
    materials["M_Emission"] = mat_emit

    return materials

def assign_material_slots(obj, mat_dict):
    slot_order = ["M_Security_Atlas", "M_Screen", "M_Emission"]
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
    f_back  = bm.faces.new([v[0], v[1], v[2], v[3]]) # -Y (wall)
    f_front = bm.faces.new([v[5], v[4], v[7], v[6]]) # +Y (room)
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]]) # -Z
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]]) # +Z
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]]) # -X
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]]) # +X
    bm.normal_update()
    return {
        'back': f_back, 'front': f_front, 'bot': f_bot,
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

    # Root Empty: SEC_Alarm_Keypad_Touch at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Alarm_Keypad_Touch", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.15
    bpy.context.collection.objects.link(root)

    uv_swatch_frame = ((1500 + 100)/2048, 1.0 - 1450/2048)
    uv_swatch_mount = ((1750 + 100)/2048, 1.0 - 1450/2048)

    # -------------------------------------------------------------------------
    # 1. MOUNT_PLATE (Mesh - Child of Root)
    # Wall plate at Y: 0.000 to 0.003, X: -0.086 to +0.086, Z: -0.058 to +0.058
    # -------------------------------------------------------------------------
    mp_me = bpy.data.meshes.new("Mount_Plate")
    mp_bm = bmesh.new()

    mp_box = add_box(mp_bm, -0.086, 0.086, 0.000, 0.003, -0.058, 0.058)
    uv_mount_back = (50/2048, 1.0 - 1650/2048, 1450/2048, 1.0 - 1020/2048)
    for k, face in mp_box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if k == 'back':
                set_face_uv_rect(mp_bm, face, uv_mount_back, flip_u=False)
            else:
                set_face_uv_constant(mp_bm, face, uv_swatch_mount)

    mark_sharp_edges(mp_bm)
    mp_bm.to_mesh(mp_me)
    mp_bm.free()

    mp_obj = bpy.data.objects.new("Mount_Plate", mp_me)
    bpy.context.collection.objects.link(mp_obj)
    mp_obj.parent = root
    assign_material_slots(mp_obj, materials)

    # -------------------------------------------------------------------------
    # 2. HOUSING (Mesh - Child of Root)
    # Slim console bezel at Y: 0.003 to 0.018, X: -0.090 to +0.090, Z: -0.0625 to +0.0625
    # -------------------------------------------------------------------------
    h_me = bpy.data.meshes.new("Housing")
    h_bm = bmesh.new()

    h_box = add_box(h_bm, -0.090, 0.090, 0.003, 0.018, -0.0625, 0.0625)
    uv_bezel = (1500/2048, 1.0 - 950/2048, 2000/2048, 1.0 - 50/2048)
    for k, face in h_box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0
            if k == 'front':
                set_face_uv_rect(h_bm, face, uv_bezel, flip_u=True)
            else:
                set_face_uv_constant(h_bm, face, uv_swatch_frame)

    mark_sharp_edges(h_bm)
    h_bm.to_mesh(h_me)
    h_bm.free()

    h_obj = bpy.data.objects.new("Housing", h_me)
    bpy.context.collection.objects.link(h_obj)
    h_obj.parent = root
    assign_material_slots(h_obj, materials)

    # -------------------------------------------------------------------------
    # 3. SCREEN_SURFACE (Mesh - Child of Housing)
    # 7-inch glass touch display at Y: 0.0185, X: -0.080 to +0.080, Z: -0.046 to +0.054
    # -------------------------------------------------------------------------
    scr_me = bpy.data.meshes.new("Screen_Surface")
    scr_bm = bmesh.new()

    s_box = add_box(scr_bm, -0.080, 0.080, 0.018, 0.0185, -0.046, 0.054)
    uv_touch_ui = (50/2048, 1.0 - 950/2048, 1450/2048, 1.0 - 50/2048)
    for k, face in s_box.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front':
                face.material_index = 1 # M_Screen
                set_face_uv_rect(scr_bm, face, uv_touch_ui, flip_u=True)
            else:
                face.material_index = 0 # M_Security_Atlas
                set_face_uv_constant(scr_bm, face, uv_swatch_frame)

    mark_sharp_edges(scr_bm)
    scr_bm.to_mesh(scr_me)
    scr_bm.free()

    scr_obj = bpy.data.objects.new("Screen_Surface", scr_me)
    bpy.context.collection.objects.link(scr_obj)
    scr_obj.parent = h_obj
    assign_material_slots(scr_obj, materials)

    # -------------------------------------------------------------------------
    # 4. STATUS_LED (Mesh - Child of Housing)
    # Glowing light bar at bottom: Y: 0.018 to 0.0188, X: -0.055 to +0.055, Z: -0.0565 to -0.0535 (sleek 3mm diffused blade)
    # -------------------------------------------------------------------------
    led_me = bpy.data.meshes.new("Status_LED")
    led_bm = bmesh.new()

    l_box = add_box(led_bm, -0.055, 0.055, 0.018, 0.0188, -0.0565, -0.0535)
    uv_led_strip = (1500/2048, 1.0 - 1200/2048, 2000/2048, 1.0 - 1020/2048)
    for k, face in l_box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 2 # M_Emission
            if k == 'front':
                set_face_uv_rect(led_bm, face, uv_led_strip, flip_u=True)
            else:
                set_face_uv_constant(led_bm, face, ((1750+100)/2048, 1.0 - 1800/2048))

    mark_sharp_edges(led_bm)
    led_bm.to_mesh(led_me)
    led_bm.free()

    led_obj = bpy.data.objects.new("Status_LED", led_me)
    bpy.context.collection.objects.link(led_obj)
    led_obj.parent = h_obj
    assign_material_slots(led_obj, materials)

    # -------------------------------------------------------------------------
    # QA Check & Triangulation
    # -------------------------------------------------------------------------
    total_tris = 0
    meshes = [mp_obj, h_obj, scr_obj, led_obj]
    for obj in meshes:
        me = obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        tris = len(bm.faces)
        total_tris += tris
        bm.free()
        obj.to_mesh_clear()

    print(f"[Geometry] Total meshes: {len(meshes)}, Total tris: {total_tris} (limit: 300)")
    assert total_tris <= 300, f"Tris limit exceeded: {total_tris} > 300"

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
    for child in [mp_obj, h_obj, scr_obj, led_obj]:
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

    manifest_data["SEC_Alarm_Keypad_Touch"] = {
        "status": "SUCCESS",
        "fbx_path": FBX_PATH,
        "blend_path": BLEND_PATH,
        "total_tris": imp_tris,
        "max_tris": 300,
        "mesh_count": len(imp_meshes),
        "empty_count": len(imp_empties),
        "materials": ["M_Security_Atlas", "M_Screen", "M_Emission"]
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=4)
    print(f"[Manifest] Updated {MANIFEST_PATH} with status SUCCESS")

if __name__ == "__main__":
    build_scene()
