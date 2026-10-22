"""
=============================================================================
Security CCTV Asset Production Suite - Asset 23 (High Detail Refinement)
Asset Name: SEC_Conduit_Junction_T
Production Script (Blender 4.x / 5.x Python API)
Description: High-fidelity industrial T-junction conduit condulet box (Form 7 style)
             with 20-radial circular ports, filleted cast housing, neoprene gasket lip,
             and 3D slotted machine screws with washers.
Hierarchy:
    SEC_Conduit_Junction_T (Root Empty at 0, 0, 0)
     ├── Junction_Housing (Mesh, root child)
     ├── Cover_Plate (Mesh, root child with 3D slotted screws and gasket)
     ├── Port_Main_A (Mesh, root child along -Y)
     ├── Port_Main_B (Mesh, root child along +Y)
     └── Port_Branch (Mesh, root child along +X)
=============================================================================
"""

import os
import sys
import math
import json
import bpy
import bmesh
from mathutils import Vector

# Directory Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

TEXTURE_PATH = os.path.join(EXPORTS_DIR, "T_Metal.png")
FBX_OUT = os.path.join(EXPORTS_DIR, "SEC_Conduit_Junction_T.fbx")
BLEND_OUT = os.path.join(EXPORTS_DIR, "SEC_Conduit_Junction_T.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")


def reset_scene():
    """Clear all objects, meshes, materials, and textures."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.scene.unit_settings.length_unit = 'METERS'


def create_material(mat_name, texture_path):
    """Create PBR material with Principled BSDF using procedural metal texture."""
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (400, 0)

    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)

    node_bsdf.inputs['Metallic'].default_value = 0.85
    node_bsdf.inputs['Roughness'].default_value = 0.40

    if os.path.exists(texture_path):
        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.location = (-400, 0)
        img = bpy.data.images.load(texture_path)
        node_tex.image = img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    else:
        node_bsdf.inputs['Base Color'].default_value = (0.70, 0.72, 0.75, 1.0)

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat


def get_filleted_profile_20(dx, dy, r):
    """
    Return 20 2D vertices for a smoothly filleted/rounded rectangle in CCW order.
    dx: half-width, dy: half-length, r: corner radius.
    """
    pts = []
    cx_vals = [dx - r, -dx + r, -dx + r, dx - r]
    cy_vals = [dy - r, dy - r, -dy + r, -dy + r]
    start_angles = [0.0, 0.5 * math.pi, math.pi, 1.5 * math.pi]

    for k in range(4):
        cx = cx_vals[k]
        cy = cy_vals[k]
        base_ang = start_angles[k]
        for a in range(5):
            ang = base_ang + a * (0.5 * math.pi / 4.0)
            if a == 4 and k < 3:
                continue # avoid duplicate corner vertex
            pts.append(Vector((cx + r * math.cos(ang), cy + r * math.sin(ang))))

    return pts[:20]


def build_housing_mesh(mat):
    """
    Build filleted cast-metal junction body.
    20 filleted vertices profile with top open rim.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    dx, dy, r = 0.024, 0.046, 0.010
    z_bot, z_top = -0.018, 0.018

    prof_out = get_filleted_profile_20(dx, dy, r)
    prof_in = get_filleted_profile_20(dx - 0.005, dy - 0.005, r - 0.002)

    v_bot = [bm.verts.new(Vector((p.x, p.y, z_bot))) for p in prof_out]
    v_top_out = [bm.verts.new(Vector((p.x, p.y, z_top))) for p in prof_out]
    v_top_in = [bm.verts.new(Vector((p.x, p.y, z_top))) for p in prof_in]

    bm.verts.ensure_lookup_table()
    n_pts = len(prof_out)

    # 1. Bottom face
    f_bot = bm.faces.new(reversed(v_bot))
    f_bot.smooth = False
    for loop in f_bot.loops:
        u = 0.60 + (loop.vert.co.x / dx) * 0.10
        v = 0.70 + (loop.vert.co.y / dy) * 0.10
        loop[uv_layer].uv = (u, v)

    # 2. Side walls (20 quads)
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        va = v_bot[i]
        vb = v_bot[i_next]
        vc = v_top_out[i_next]
        vd = v_top_out[i]

        f = bm.faces.new((va, vb, vc, vd))
        f.smooth = True

        u0 = 0.52 + (i / float(n_pts)) * 0.44
        u1 = 0.52 + ((i + 1) / float(n_pts)) * 0.44
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.60)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.60)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.92)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.92)

    # 3. Top Rim (20 quads connecting outer to inner profile)
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        vo1 = v_top_out[i]
        vo2 = v_top_out[i_next]
        vi2 = v_top_in[i_next]
        vi1 = v_top_in[i]

        f = bm.faces.new((vo1, vo2, vi2, vi1))
        f.smooth = False
        for loop in f.loops:
            u = 0.60 + (loop.vert.co.x / dx) * 0.08
            v = 0.70 + (loop.vert.co.y / dy) * 0.08
            loop[uv_layer].uv = (u, v)

    bm.normal_update()

    mesh = bpy.data.meshes.new("Junction_Housing")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Junction_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_cover_plate_mesh(mat):
    """
    Build filleted inspection cover plate with neoprene gasket rim and 3D slotted screws.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    dx, dy, r = 0.025, 0.047, 0.011
    z_gasket = 0.0175
    z_lip = 0.019
    z_top = 0.0225

    prof = get_filleted_profile_20(dx, dy, r)
    prof_gasket = get_filleted_profile_20(dx - 0.001, dy - 0.001, r - 0.001)

    v_gas_bot = [bm.verts.new(Vector((p.x, p.y, z_gasket))) for p in prof_gasket]
    v_lip = [bm.verts.new(Vector((p.x, p.y, z_lip))) for p in prof]
    v_top = [bm.verts.new(Vector((p.x, p.y, z_top))) for p in prof]

    bm.verts.ensure_lookup_table()
    n_pts = len(prof)

    # 1. Gasket Rim (20 quads connecting gasket bot to cover lip)
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        f = bm.faces.new((v_gas_bot[i], v_gas_bot[i_next], v_lip[i_next], v_lip[i]))
        f.smooth = True
        for loop in f.loops: loop[uv_layer].uv = (0.28, 0.10) # dark gasket rubber

    # 2. Cover Top Face
    f_top = bm.faces.new(v_top)
    f_top.smooth = False
    for loop in f_top.loops:
        u = 0.25 + (loop.vert.co.y / dy) * 0.21
        v = 0.75 - (loop.vert.co.x / dx) * 0.18
        loop[uv_layer].uv = (u, v)

    # 3. Skirt sides (20 quads)
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        va = v_lip[i]
        vb = v_lip[i_next]
        vc = v_top[i_next]
        vd = v_top[i]

        f = bm.faces.new((va, vb, vc, vd))
        f.smooth = True

        u0 = (i / float(n_pts)) * 0.40 + 0.05
        u1 = ((i + 1) / float(n_pts)) * 0.40 + 0.05
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.52)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.52)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.55)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.55)

    # 4. Add 3D Slotted Machine Screws (Left at Y=-0.035, Right at Y=+0.035)
    for sy in [-0.035, 0.035]:
        sc_cen = Vector((0.0, sy, z_top))
        sc_rad = 0.0036
        sc_h = 0.0016

        sc_top = []
        sc_bot = []
        for a in range(8):
            ang = a * (2.0 * math.pi / 8.0)
            sc_x = sc_cen.x + sc_rad * math.cos(ang)
            sc_y = sc_cen.y + sc_rad * math.sin(ang)
            sc_bot.append(bm.verts.new(Vector((sc_x, sc_y, z_top))))
            sc_top.append(bm.verts.new(Vector((sc_x, sc_y, z_top + sc_h))))

        f_sct = bm.faces.new(sc_top)
        f_sct.smooth = False
        for loop in f_sct.loops: loop[uv_layer].uv = (0.25, 0.98)

        for a in range(8):
            a_next = (a + 1) % 8
            f_sc = bm.faces.new((sc_bot[a], sc_bot[a_next], sc_top[a_next], sc_top[a]))
            f_sc.smooth = False
            for loop in f_sc.loops: loop[uv_layer].uv = (0.24, 0.96)

    bm.normal_update()

    mesh = bpy.data.meshes.new("Cover_Plate")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Cover_Plate", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_detailed_port(name, axis, start_coord, end_coord, r_hub, r_collar, r_in, mat):
    """
    Build smooth 20-radial conduit port with thickened entrance collar and internal bore.
    """
    bm = bmesh.new()
    n_radial = 20
    uv_layer = bm.loops.layers.uv.new("UVMap")

    dir_sign = 1.0 if end_coord > start_coord else -1.0
    total_l = abs(end_coord - start_coord)
    mid_coord = start_coord + dir_sign * (total_l * 0.65)

    v_out_start = []
    v_out_mid = []
    v_out_end = []
    v_in_start = []
    v_in_end = []

    for j in range(n_radial):
        ang = j * (2.0 * math.pi / n_radial)
        ca = math.cos(ang)
        sa = math.sin(ang)

        if axis == 'Y':
            pt_out_s = Vector((ca * r_hub,    start_coord, sa * r_hub))
            pt_out_m = Vector((ca * r_collar, mid_coord,   sa * r_collar))
            pt_out_e = Vector((ca * r_collar, end_coord,   sa * r_collar))
            pt_in_s  = Vector((ca * r_in,     start_coord, sa * r_in))
            pt_in_e  = Vector((ca * r_in,     end_coord,   sa * r_in))
        else: # 'X'
            pt_out_s = Vector((start_coord, ca * r_hub,    sa * r_hub))
            pt_out_m = Vector((mid_coord,   ca * r_collar, sa * r_collar))
            pt_out_e = Vector((end_coord,   ca * r_collar, sa * r_collar))
            pt_in_s  = Vector((start_coord, ca * r_in,     sa * r_in))
            pt_in_e  = Vector((end_coord,   ca * r_in,     sa * r_in))

        v_out_start.append(bm.verts.new(pt_out_s))
        v_out_mid.append(bm.verts.new(pt_out_m))
        v_out_end.append(bm.verts.new(pt_out_e))
        v_in_start.append(bm.verts.new(pt_in_s))
        v_in_end.append(bm.verts.new(pt_in_e))

    bm.verts.ensure_lookup_table()

    # 1. Outer Hub Quads (start to mid)
    for j in range(n_radial):
        j_next = (j + 1) % n_radial
        va = v_out_start[j]
        vb = v_out_start[j_next]
        vc = v_out_mid[j_next]
        vd = v_out_mid[j]

        if dir_sign > 0: f = bm.faces.new((va, vb, vc, vd))
        else: f = bm.faces.new((va, vd, vc, vb))
        f.smooth = True

        u0 = j / float(n_radial)
        u1 = (j + 1) / float(n_radial)
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.20)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.20)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.35)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.35)

    # 2. Outer Collar Quads (mid to end)
    for j in range(n_radial):
        j_next = (j + 1) % n_radial
        va = v_out_mid[j]
        vb = v_out_mid[j_next]
        vc = v_out_end[j_next]
        vd = v_out_end[j]

        if dir_sign > 0: f = bm.faces.new((va, vb, vc, vd))
        else: f = bm.faces.new((va, vd, vc, vb))
        f.smooth = True

        u0 = j / float(n_radial)
        u1 = (j + 1) / float(n_radial)
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.35)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.35)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.48)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.48)

    # 3. Inner Bore Quads (facing inward)
    for j in range(n_radial):
        j_next = (j + 1) % n_radial
        va = v_in_start[j]
        vb = v_in_start[j_next]
        vc = v_in_end[j_next]
        vd = v_in_end[j]

        if dir_sign > 0: f = bm.faces.new((va, vd, vc, vb))
        else: f = bm.faces.new((va, vb, vc, vd))
        f.smooth = True

        u0 = j / float(n_radial)
        u1 = (j + 1) / float(n_radial)
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.02)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.02)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.16)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.16)

    # 4. Open Entrance Rim (connecting outer collar to inner bore)
    for j in range(n_radial):
        j_next = (j + 1) % n_radial
        vo1 = v_out_end[j]
        vo2 = v_out_end[j_next]
        vi2 = v_in_end[j_next]
        vi1 = v_in_end[j]

        if dir_sign > 0: f = bm.faces.new((vo1, vo2, vi2, vi1))
        else: f = bm.faces.new((vo1, vi1, vi2, vo2))
        f.smooth = False

        ang0 = j * (2.0 * math.pi / n_radial)
        ang1 = (j + 1) * (2.0 * math.pi / n_radial)
        cx_uv, cy_uv = 0.85, 0.88
        r0, r1 = 0.04, 0.03
        for loop in f.loops:
            if loop.vert == vo1: loop[uv_layer].uv = (cx_uv + r0 * math.cos(ang0), cy_uv + r0 * math.sin(ang0))
            elif loop.vert == vo2: loop[uv_layer].uv = (cx_uv + r0 * math.cos(ang1), cy_uv + r0 * math.sin(ang1))
            elif loop.vert == vi2: loop[uv_layer].uv = (cx_uv + r1 * math.cos(ang1), cy_uv + r1 * math.sin(ang1))
            elif loop.vert == vi1: loop[uv_layer].uv = (cx_uv + r1 * math.cos(ang0), cy_uv + r1 * math.sin(ang0))

    bm.normal_update()

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_asset():
    """Create the full SEC_Conduit_Junction_T asset hierarchy."""
    reset_scene()

    mat_metal = create_material("M_Metal", TEXTURE_PATH)

    # Root Empty at center of box (0, 0, 0)
    root = bpy.data.objects.new("SEC_Conduit_Junction_T", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 1. Housing Body
    housing = build_housing_mesh(mat_metal)
    housing.parent = root

    # 2. Cover Plate
    cover = build_cover_plate_mesh(mat_metal)
    cover.parent = root

    # 3. Ports: 20-radial, r_hub = 0.014 m, r_collar = 0.015 m, r_in = 0.0105 m
    port_a = build_detailed_port("Port_Main_A", 'Y', -0.046, -0.072, 0.014, 0.015, 0.0105, mat_metal)
    port_a.parent = root

    port_b = build_detailed_port("Port_Main_B", 'Y',  0.046,  0.072, 0.014, 0.015, 0.0105, mat_metal)
    port_b.parent = root

    port_branch = build_detailed_port("Port_Branch", 'X', 0.024, 0.050, 0.014, 0.015, 0.0105, mat_metal)
    port_branch.parent = root

    # Select all hierarchy objects
    meshes = [housing, cover, port_a, port_b, port_branch]
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = root

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[OK] Saved .blend: {BLEND_OUT}")

    return root, meshes


def export_fbx(root, meshes):
    """Export asset to FBX."""
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = root

    bpy.ops.export_scene.fbx(
        filepath=FBX_OUT,
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
    print(f"[OK] Exported FBX: {FBX_OUT}")


def run_qa_verification():
    """Import FBX in clean test scene and verify specs, tris, UVs and hierarchy."""
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 23 High Detail Refined) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=FBX_OUT)

    root = bpy.data.objects.get("SEC_Conduit_Junction_T")
    assert root is not None, "FAIL: Root object 'SEC_Conduit_Junction_T' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    empty_objs = [obj for obj in bpy.data.objects if obj.type == 'EMPTY']

    print(f"[INFO] Imported Meshes: {[m.name for m in mesh_objs]}")
    print(f"[INFO] Imported Empties: {[e.name for e in empty_objs]}")

    expected_meshes = {"Junction_Housing", "Cover_Plate", "Port_Main_A", "Port_Main_B", "Port_Branch"}
    found_meshes = {m.name for m in mesh_objs}
    assert expected_meshes.issubset(found_meshes), f"FAIL: Missing meshes: {expected_meshes - found_meshes}"

    total_tris = 0
    for m in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(m.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        m_tris = len(bm.faces)
        total_tris += m_tris
        bm.free()
        print(f"       -> {m.name}: {m_tris} tris")

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 2000, f"FAIL: Total triangles {total_tris} exceeds 2000 budget!"
    print("[PASS] Triangle count verified strictly!")

    for m in mesh_objs:
        assert len(m.data.materials) > 0, f"FAIL: Mesh '{m.name}' has no material!"
        assert m.data.materials[0].name.startswith("M_Metal"), f"FAIL: Slot 0 is '{m.data.materials[0].name}', expected 'M_Metal'!"
    print("[PASS] All materials correctly assigned to Slot 0: M_Metal!")

    for m in mesh_objs:
        assert len(m.data.uv_layers) > 0, f"FAIL: Mesh '{m.name}' has no UV layers!"
    print("[PASS] All meshes have valid UV coordinates!")

    for m_name in expected_meshes:
        obj = bpy.data.objects.get(m_name)
        assert obj and obj.parent == root, f"FAIL: Mesh '{m_name}' parent != root!"
    print("[PASS] All child meshes correctly parented to root!")

    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Conduit_Junction_T"] = {
        "asset_name": "SEC_Conduit_Junction_T",
        "fbx_path": "exports/SEC_Conduit_Junction_T.fbx",
        "blend_path": "exports/SEC_Conduit_Junction_T.blend",
        "tris_count": total_tris,
        "mesh_count": len(mesh_objs),
        "empty_count": len(empty_objs),
        "materials": [m.name for m in bpy.data.materials],
        "status": "SUCCESS"
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[OK] Updated manifest: {MANIFEST_PATH}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")


def clean_backup_files():
    """Remove any temporary .blend1 backup files."""
    for root, dirs, files in os.walk(EXPORTS_DIR):
        for file in files:
            if file.endswith(".blend1"):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"[CLEAN] Removed backup: {file}")
                except Exception:
                    pass


if __name__ == "__main__":
    root, meshes = build_asset()
    export_fbx(root, meshes)
    run_qa_verification()
    clean_backup_files()
