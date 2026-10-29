"""
=============================================================================
Security CCTV Asset Production Suite - Asset 58
Asset Name: SEC_Network_Fiber_Patch_Panel (Fiber Optik Patch Panel)
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

FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Network_Fiber_Patch_Panel.fbx")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Network_Fiber_Patch_Panel.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

ASSET_NAME = "SEC_Network_Fiber_Patch_Panel"
MAX_TRIS = 480

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
        bsdf_m.inputs["Metallic"].default_value = 0.92
        bsdf_m.inputs["Roughness"].default_value = 0.22

    # Slot 1: M_Security_Atlas
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf_a = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if bsdf_a and os.path.exists(ATLAS_PATH):
        tex_node = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(ATLAS_PATH)
        mat_atlas.node_tree.links.new(tex_node.outputs["Color"], bsdf_a.inputs["Base Color"])
        bsdf_a.inputs["Metallic"].default_value = 0.25
        bsdf_a.inputs["Roughness"].default_value = 0.45

    return mat_metal, mat_atlas

def setup_slots(mesh, mat_metal, mat_atlas):
    mesh.materials.append(mat_metal) # Slot 0: M_Metal
    mesh.materials.append(mat_atlas) # Slot 1: M_Security_Atlas

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

def build_panel_body(mat_metal, mat_atlas):
    me = bpy.data.meshes.new("Panel_Body")
    bm = bmesh.new()

    uv_front  = (74/2048, 1.0 - 220/2048, 1974/2048, 1.0 - 30/2048)
    uv_rear   = (74/2048, 1.0 - 1100/2048, 1974/2048, 1.0 - 600/2048)
    uv_top_cover = (74/2048, 1.0 - 1100/2048, 1974/2048, 1.0 - 600/2048)
    uv_chassis = (74/2048, 1.0 - 2000/2048, 500/2048, 1.0 - 1500/2048)
    uv_metal  = (540/2048, 1.0 - 2000/2048, 960/2048, 1.0 - 1500/2048)

    # 1. Main 1U Panel Chassis:
    # W = 0.440m (X: -0.220 to +0.220)
    # D = 0.140m (Y: 0.000 to +0.140)
    # H = 0.044m (Z: -0.022 to +0.022)
    box = add_box(bm, -0.220, 0.220, 0.000, 0.140, -0.022, 0.022)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front':
                face.material_index = 1 # Slot 1: M_Security_Atlas
                set_planar_uv(bm, face, uv_front, plane='XZ', flip_u=False)
            elif k == 'top':
                face.material_index = 1 # Slot 1: M_Security_Atlas (Warning & Spec decal)
                set_planar_uv(bm, face, uv_top_cover, plane='XY')
            elif k == 'rear':
                face.material_index = 1 # Slot 1: M_Security_Atlas
                set_planar_uv(bm, face, uv_rear, plane='XZ', flip_u=True)
            else:
                face.material_index = 0 # Slot 0: M_Metal
                set_planar_uv(bm, face, uv_chassis, plane='XY')

    # 2. Left & Right 19" Rack Mounting Ears
    # Left Ear: X: -0.2415 to -0.220, Y: -0.003 to 0.000, Z: -0.022 to +0.022
    box_l = add_box(bm, -0.2415, -0.220, -0.003, 0.000, -0.022, 0.022)
    for face in box_l.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    # Right Ear: X: 0.220 to 0.2415, Y: -0.003 to 0.000, Z: -0.022 to +0.022
    box_r = add_box(bm, 0.220, 0.2415, -0.003, 0.000, -0.022, 0.022)
    for face in box_r.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 0 # Slot 0: M_Metal
            set_planar_uv(bm, face, uv_metal, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_metal, mat_atlas)
    obj = bpy.data.objects.new("Panel_Body", me)
    return obj

def build_adapter(name, cx, mat_metal, mat_atlas):
    """
    Builds a single duplex LC fiber optic coupler adapter (5 faces = 10 tris).
    Protrudes 4.5mm proud of front panel: Y = -0.0045 to 0.000.
    Width = 15mm, Height = 11mm, Center Z = 0.000m.
    """
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()

    hw = 0.015 / 2.0
    hh = 0.011 / 2.0
    cz = 0.000
    x0, x1 = cx - hw, cx + hw
    y0, y1 = -0.0045, 0.000
    z0, z1 = cz - hh, cz + hh

    uv_adapter = (74/2048, 1.0 - 550/2048, 600/2048, 1.0 - 250/2048)
    uv_aqua    = (1000/2048, 1.0 - 2000/2048, 1480/2048, 1.0 - 1500/2048)

    box = add_box(bm, x0, x1, y0, y1, z0, z1)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            if k == 'front':
                face.material_index = 1 # Slot 1: M_Security_Atlas
                set_planar_uv(bm, face, uv_adapter, plane='XZ')
            else:
                face.material_index = 1 # Slot 1: M_Security_Atlas
                set_planar_uv(bm, face, uv_aqua, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_metal, mat_atlas)
    obj = bpy.data.objects.new(name, me)
    center_local = Vector((cx, (y0 + y1) / 2.0, cz))
    me.transform(Matrix.Translation(-center_local))
    obj.location = center_local
    return obj

def build_label_strip(mat_metal, mat_atlas):
    """
    Builds the acrylic / paper label strip running below adapters:
    Width: 340mm (X: -0.170 to +0.170)
    Height: 11mm (Z: -0.020 to -0.009)
    Thickness: 1.5mm (Y: -0.0015 to 0.000)
    """
    me = bpy.data.meshes.new("Label_Strip")
    bm = bmesh.new()

    # Exact UV mapping matching texture Zone C:
    # X_px from 290 to 1758, Y_px from 160 to 210
    uv_label = (290/2048, 1.0 - 210/2048, 1758/2048, 1.0 - 160/2048)
    uv_paper = (74/2048, 1.0 - 2000/2048, 500/2048, 1.0 - 1500/2048)

    box = add_box(bm, -0.170, 0.170, -0.0015, 0.000, -0.020, -0.009)
    for k, face in box.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Security_Atlas
            if k == 'front':
                set_planar_uv(bm, face, uv_label, plane='XZ', flip_u=False)
            else:
                face.material_index = 0 # Slot 0: M_Metal
                set_planar_uv(bm, face, uv_paper, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_metal, mat_atlas)
    obj = bpy.data.objects.new("Label_Strip", me)
    return obj

def build_cable_manager(mat_metal, mat_atlas):
    """
    Builds the front cable management trough bar with 4 curved wire D-rings:
    Extends 25mm forward (Y: -0.025 to 0.000).
    """
    me = bpy.data.meshes.new("Cable_Manager")
    bm = bmesh.new()

    uv_manager = (650/2048, 1.0 - 550/2048, 1974/2048, 1.0 - 250/2048)

    # 1. Main horizontal support bar:
    # W = 0.400m (X: -0.200 to +0.200), Y: -0.022 to -0.018, Z: -0.021 to -0.017
    box_bar = add_box(bm, -0.200, 0.200, -0.022, -0.018, -0.021, -0.017)
    for face in box_bar.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # Slot 1: M_Security_Atlas
            set_planar_uv(bm, face, uv_manager, plane='XZ')

    # 2. Two mounting brackets connecting to front panel:
    # Left bracket: X: -0.200 to -0.196, Y: -0.020 to 0.000, Z: -0.021 to -0.017
    box_bl = add_box(bm, -0.200, -0.196, -0.020, 0.000, -0.021, -0.017)
    for face in box_bl.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1
            set_planar_uv(bm, face, uv_manager, plane='XZ')

    # Right bracket: X: 0.196 to 0.200, Y: -0.020 to 0.000, Z: -0.021 to -0.017
    box_br = add_box(bm, 0.196, 0.200, -0.020, 0.000, -0.021, -0.017)
    for face in box_br.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1
            set_planar_uv(bm, face, uv_manager, plane='XZ')

    # 3. Four cable routing D-rings along the bar:
    # Located at X = -0.140, -0.050, +0.050, +0.140
    for rx in [-0.140, -0.050, 0.050, 0.140]:
        # Left upright of D-ring
        b_up1 = add_box(bm, rx - 0.010, rx - 0.008, -0.025, -0.015, -0.019, 0.012)
        for f in b_up1.values():
            if isinstance(f, bmesh.types.BMFace):
                f.material_index = 1
                set_planar_uv(bm, f, uv_manager, plane='XZ')

        # Right upright of D-ring
        b_up2 = add_box(bm, rx + 0.008, rx + 0.010, -0.025, -0.015, -0.019, 0.012)
        for f in b_up2.values():
            if isinstance(f, bmesh.types.BMFace):
                f.material_index = 1
                set_planar_uv(bm, f, uv_manager, plane='XZ')

        # Top bridge of D-ring
        b_top = add_box(bm, rx - 0.010, rx + 0.010, -0.025, -0.023, 0.010, 0.012)
        for f in b_top.values():
            if isinstance(f, bmesh.types.BMFace):
                f.material_index = 1
                set_planar_uv(bm, f, uv_manager, plane='XZ')

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(me)
    bm.free()

    setup_slots(me, mat_metal, mat_atlas)
    obj = bpy.data.objects.new("Cable_Manager", me)
    return obj

def main():
    print("=" * 70)
    print(f"Generating {ASSET_NAME}...")
    print("=" * 70)

    reset_scene()
    mat_metal, mat_atlas = create_materials()

    # 1. Root Empty: SEC_Network_Fiber_Patch_Panel at (0, 0, 0)
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.20
    root.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root)

    # 2. Panel_Body parented to Root
    body = build_panel_body(mat_metal, mat_atlas)
    bpy.context.scene.collection.objects.link(body)
    body.parent = root

    # 3. Label_Strip parented to Panel_Body
    label_strip = build_label_strip(mat_metal, mat_atlas)
    bpy.context.scene.collection.objects.link(label_strip)
    label_strip.parent = body

    # 4. Cable_Manager parented to Panel_Body
    cable_mgr = build_cable_manager(mat_metal, mat_atlas)
    bpy.context.scene.collection.objects.link(cable_mgr)
    cable_mgr.parent = body

    # 5. 12 Fiber Coupler Adapters (Adapter_01 .. Adapter_12) parented to Panel_Body
    # Exactly aligned: cx(i) = -0.154 + i * 0.028m
    adapters = []
    for i in range(12):
        num = i + 1
        name = f"Adapter_{num:02d}"
        cx = -0.154 + i * 0.028
        ad_obj = build_adapter(name, cx, mat_metal, mat_atlas)
        bpy.context.scene.collection.objects.link(ad_obj)
        ad_obj.parent = body
        adapters.append(ad_obj)

    # Metadata custom properties on Root
    root["asset_id"] = "SEC_58"
    root["form_factor"] = "19_INCH_1U_RACKMOUNT"
    root["fiber_coupler_type"] = "DUPLEX_LC_UPC"
    root["port_capacity"] = 12
    root["fiber_count"] = 24
    root["insertion_loss_db"] = 0.20

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root, body, label_strip, cable_mgr] + adapters
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
    print(f"  Mesh Count: {mesh_count} (Expected: 15)")
    print(f"  Empty Count: {empty_count} (Expected: 1)")
    print(f"  Materials: {sorted(list(materials_found))}")

    is_tris_ok = (total_tris <= MAX_TRIS)
    is_mesh_ok = (mesh_count == 15)
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
        raise RuntimeError(f"QA Validation FAILED: tris={total_tris} (max {MAX_TRIS}), mesh_count={mesh_count} (exp 15), empty_count={empty_count} (exp 1)")

if __name__ == "__main__":
    main()
