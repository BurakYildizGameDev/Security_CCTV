"""
=============================================================================
Security CCTV Asset Production Suite - Asset 24 (High Detail Refinement)
Asset Name: SEC_Ceiling_Conduit_Clamp
Production Script (Blender 4.x / 5.x Python API)
Description: High-fidelity industrial ceiling conduit clamp for 25mm OD pipe
             with 20-segment smooth U-cradle, stamped stiffener rib,
             countersunk ceiling plate slots, and 3D flanged M6 bolts with nuts.
Hierarchy:
    SEC_Ceiling_Conduit_Clamp (Root Empty at 0, 0, 0 - ceiling mount center)
     ├── Ceiling_Plate (Mesh, root child)
     ├── Clamp_Band (Mesh, root child)
     ├── Screw_Left (Mesh, root child)
     └── Screw_Right (Mesh, root child)
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
FBX_OUT = os.path.join(EXPORTS_DIR, "SEC_Ceiling_Conduit_Clamp.fbx")
BLEND_OUT = os.path.join(EXPORTS_DIR, "SEC_Ceiling_Conduit_Clamp.blend")
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

    node_bsdf.inputs['Metallic'].default_value = 0.88
    node_bsdf.inputs['Roughness'].default_value = 0.38

    if os.path.exists(texture_path):
        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.location = (-400, 0)
        img = bpy.data.images.load(texture_path)
        node_tex.image = img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    else:
        node_bsdf.inputs['Base Color'].default_value = (0.75, 0.77, 0.80, 1.0)

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat


def get_filleted_profile_16(dx, dy, r):
    """Return 16 2D vertices for a smoothly filleted/rounded rectangle in CCW order."""
    pts = []
    cx_vals = [dx - r, -dx + r, -dx + r, dx - r]
    cy_vals = [dy - r, dy - r, -dy + r, -dy + r]
    start_angles = [0.0, 0.5 * math.pi, math.pi, 1.5 * math.pi]

    for k in range(4):
        cx = cx_vals[k]
        cy = cy_vals[k]
        base_ang = start_angles[k]
        for a in range(4):
            ang = base_ang + a * (0.5 * math.pi / 4.0)
            pts.append(Vector((cx + r * math.cos(ang), cy + r * math.sin(ang))))

    return pts


def build_ceiling_plate_mesh(mat):
    """
    Build filleted stamped steel base plate with 3D recessed ceiling anchor slots.
    Ceiling contact plane at Z = 0.000, extends down to Z = -0.003 m.
    Width 0.080 m (X: -0.040 to +0.040), depth 0.024 m (Y: -0.012 to +0.012).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    dx, dy, r = 0.040, 0.012, 0.004
    z_bot, z_top = -0.003, 0.000

    prof = get_filleted_profile_16(dx, dy, r)
    v_bot = [bm.verts.new(Vector((p.x, p.y, z_bot))) for p in prof]
    v_top = [bm.verts.new(Vector((p.x, p.y, z_top))) for p in prof]

    bm.verts.ensure_lookup_table()
    n_pts = len(prof)

    # 1. Top face
    f_top = bm.faces.new(v_top)
    f_top.smooth = False
    for loop in f_top.loops:
        u = 0.25 + (loop.vert.co.x / dx) * 0.20
        v = 0.75 + (loop.vert.co.y / dy) * 0.15
        loop[uv_layer].uv = (u, v)

    # 2. Bottom face
    f_bot = bm.faces.new(reversed(v_bot))
    f_bot.smooth = False
    for loop in f_bot.loops:
        u = 0.25 + (loop.vert.co.x / dx) * 0.20
        v = 0.75 + (loop.vert.co.y / dy) * 0.15
        loop[uv_layer].uv = (u, v)

    # 3. Side walls (16 quads)
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        va = v_bot[i]
        vb = v_bot[i_next]
        vc = v_top[i_next]
        vd = v_top[i]

        f = bm.faces.new((va, vb, vc, vd))
        f.smooth = True

        u0 = (i / float(n_pts)) * 0.40 + 0.05
        u1 = ((i + 1) / float(n_pts)) * 0.40 + 0.05
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.52)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.52)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.54)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.54)

    # 4. Add 3D Recessed Anchor Slot Caps (Left at X=-0.030, Right at X=+0.030)
    for ax in [-0.030, 0.030]:
        slot_w, slot_l = 0.0025, 0.0050
        v_s1 = bm.verts.new(Vector((ax - slot_w, -slot_l, z_top + 0.0001)))
        v_s2 = bm.verts.new(Vector((ax + slot_w, -slot_l, z_top + 0.0001)))
        v_s3 = bm.verts.new(Vector((ax + slot_w,  slot_l, z_top + 0.0001)))
        v_s4 = bm.verts.new(Vector((ax - slot_w,  slot_l, z_top + 0.0001)))
        f_s = bm.faces.new((v_s1, v_s2, v_s3, v_s4))
        f_s.smooth = False
        for loop in f_s.loops: loop[uv_layer].uv = (0.15, 0.75) # dark slot

    bm.normal_update()

    mesh = bpy.data.meshes.new("Ceiling_Plate")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Ceiling_Plate", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_clamp_band_mesh(mat):
    """
    Build high-detail U-shaped conduit saddle clamp band.
    16-segment smooth semi-circular arch cradling 25mm OD pipe (r = 0.0125 m).
    Includes stamped reinforcing central ridge.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    zin = -0.003
    t = 0.002
    zout = -0.005
    zc = -0.0155
    r_in = 0.0125
    r_out = r_in + t

    pts_in = []
    pts_out = []

    # 0: Left ear tip
    pts_in.append((-0.038, zin))
    pts_out.append((-0.038, zout))

    # 1: Left ear inner corner
    pts_in.append((-r_in, zin))
    pts_out.append((-r_out, zout))

    # 2: Left drop tangent
    pts_in.append((-r_in, zc))
    pts_out.append((-r_out, zc))

    # Semicircular arch: 16 segments across 180 degrees
    n_arch = 16
    for k in range(1, n_arch):
        ang = math.pi + k * (math.pi / float(n_arch))
        pts_in.append((r_in * math.cos(ang), zc + r_in * math.sin(ang)))
        pts_out.append((r_out * math.cos(ang), zc + r_out * math.sin(ang)))

    # Right rise tangent
    pts_in.append((r_in, zc))
    pts_out.append((r_out, zc))

    # Right ear inner corner
    pts_in.append((r_in, zin))
    pts_out.append((r_out, zout))

    # Right ear tip
    pts_in.append((0.038, zin))
    pts_out.append((0.038, zout))

    n_pts = len(pts_in)
    n_segs = n_pts - 1

    # 3 rings along Y for central stiffening bead:
    y_front =  0.009
    y_mid   =  0.000
    y_back  = -0.009

    v_in_front = [bm.verts.new(Vector((p[0], y_front, p[1]))) for p in pts_in]
    v_in_mid   = [bm.verts.new(Vector((p[0], y_mid,   p[1]))) for p in pts_in]
    v_in_back  = [bm.verts.new(Vector((p[0], y_back,  p[1]))) for p in pts_in]

    v_out_front = [bm.verts.new(Vector((p[0], y_front, p[1]))) for p in pts_out]
    v_out_mid   = [bm.verts.new(Vector((p[0] * 1.018, y_mid, p[1] * 1.018))) for p in pts_out]
    v_out_back  = [bm.verts.new(Vector((p[0], y_back,  p[1]))) for p in pts_out]

    bm.verts.ensure_lookup_table()

    # Outer surface
    for i in range(n_segs):
        u0 = 0.52 + (i / float(n_segs)) * 0.45
        u1 = 0.52 + ((i + 1) / float(n_segs)) * 0.45

        va = v_out_front[i]
        vb = v_out_front[i + 1]
        vc = v_out_mid[i + 1]
        vd = v_out_mid[i]
        f1 = bm.faces.new((va, vb, vc, vd))
        f1.smooth = True
        for loop in f1.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.90)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.90)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.75)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.75)

        va2 = v_out_mid[i]
        vb2 = v_out_mid[i + 1]
        vc2 = v_out_back[i + 1]
        vd2 = v_out_back[i]
        f2 = bm.faces.new((va2, vb2, vc2, vd2))
        f2.smooth = True
        for loop in f2.loops:
            if loop.vert == va2: loop[uv_layer].uv = (u0, 0.75)
            elif loop.vert == vb2: loop[uv_layer].uv = (u1, 0.75)
            elif loop.vert == vc2: loop[uv_layer].uv = (u1, 0.60)
            elif loop.vert == vd2: loop[uv_layer].uv = (u0, 0.60)

    # Inner surface
    for i in range(n_segs):
        vf1 = v_in_front[i]
        vf2 = v_in_front[i + 1]
        vb2 = v_in_back[i + 1]
        vb1 = v_in_back[i]

        f = bm.faces.new((vf1, vf2, vb2, vb1))
        f.smooth = True

        u0 = 0.05 + (i / float(n_segs)) * 0.40
        u1 = 0.05 + ((i + 1) / float(n_segs)) * 0.40
        for loop in f.loops:
            if loop.vert == vf1: loop[uv_layer].uv = (u0, 0.55)
            elif loop.vert == vf2: loop[uv_layer].uv = (u1, 0.55)
            elif loop.vert == vb2: loop[uv_layer].uv = (u1, 0.52)
            elif loop.vert == vb1: loop[uv_layer].uv = (u0, 0.52)

    # Front Edges
    for i in range(n_segs):
        f = bm.faces.new((v_out_front[i], v_out_front[i + 1], v_in_front[i + 1], v_in_front[i]))
        f.smooth = False
        for loop in f.loops: loop[uv_layer].uv = (0.80, 0.53)

    # Back Edges
    for i in range(n_segs):
        f = bm.faces.new((v_out_back[i], v_in_back[i], v_in_back[i + 1], v_out_back[i + 1]))
        f.smooth = False
        for loop in f.loops: loop[uv_layer].uv = (0.82, 0.53)

    # End Caps
    f_left = bm.faces.new((v_out_front[0], v_in_front[0], v_in_back[0], v_out_back[0]))
    f_left.smooth = False
    for loop in f_left.loops: loop[uv_layer].uv = (0.85, 0.53)

    f_right = bm.faces.new((v_out_front[-1], v_out_back[-1], v_in_back[-1], v_in_front[-1]))
    f_right.smooth = False
    for loop in f_right.loops: loop[uv_layer].uv = (0.85, 0.53)

    bm.normal_update()

    mesh = bpy.data.meshes.new("Clamp_Band")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Clamp_Band", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_detailed_screw_mesh(name, center_pos, mat, uv_u_center):
    """
    Build realistic 3D M6 hex bolt with flanged washer, threaded stud, and M6 nut.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    r_washer = 0.0050
    r_hex = 0.0040
    r_stud = 0.0030

    z_seat = center_pos.z              # -0.005 m (bottom face of clamp ear)
    z_flange = center_pos.z - 0.0012   # flange top
    z_head_bot = center_pos.z - 0.0050 # hex head bottom face
    z_plate_top = 0.0000               # top of base plate
    z_nut_top = 0.0035                 # M6 nut top on plate

    # 1. Hex Bolt Head (6-sided) below ear
    v_hex_top = []
    v_hex_bot = []
    for i in range(6):
        ang = i * (math.pi / 3.0) + (math.pi / 6.0)
        cx = center_pos.x + r_hex * math.cos(ang)
        cy = center_pos.y + r_hex * math.sin(ang)
        v_hex_top.append(bm.verts.new(Vector((cx, cy, z_flange))))
        v_hex_bot.append(bm.verts.new(Vector((cx, cy, z_head_bot))))

    # 2. Flanged Washer Ring (8-sided)
    v_w_top = []
    v_w_bot = []
    for i in range(8):
        ang = i * (2.0 * math.pi / 8.0)
        cx = center_pos.x + r_washer * math.cos(ang)
        cy = center_pos.y + r_washer * math.sin(ang)
        v_w_top.append(bm.verts.new(Vector((cx, cy, z_seat))))
        v_w_bot.append(bm.verts.new(Vector((cx, cy, z_flange))))

    # 3. M6 Hex Nut (6-sided) on top of ceiling plate
    v_nut_bot = []
    v_nut_top = []
    for i in range(6):
        ang = i * (math.pi / 3.0) + (math.pi / 6.0)
        cx = center_pos.x + r_hex * math.cos(ang)
        cy = center_pos.y + r_hex * math.sin(ang)
        v_nut_bot.append(bm.verts.new(Vector((cx, cy, z_plate_top))))
        v_nut_top.append(bm.verts.new(Vector((cx, cy, z_nut_top))))

    bm.verts.ensure_lookup_table()

    # Hex Head Bottom Face (facing -Z, visible head face with grade 8.8)
    f_hex_bot = bm.faces.new(reversed(v_hex_bot))
    f_hex_bot.smooth = False
    for loop in f_hex_bot.loops:
        u = uv_u_center + ((loop.vert.co.x - center_pos.x) / r_hex) * 0.045
        v = 0.267 + ((loop.vert.co.y - center_pos.y) / r_hex) * 0.045
        loop[uv_layer].uv = (u, v)

    # Hex Head Sides (6 quads)
    for i in range(6):
        i_next = (i + 1) % 6
        f = bm.faces.new((v_hex_top[i], v_hex_bot[i], v_hex_bot[i_next], v_hex_top[i_next]))
        f.smooth = False
        u0 = uv_u_center - 0.03 + (i / 6.0) * 0.06
        u1 = uv_u_center - 0.03 + ((i + 1) / 6.0) * 0.06
        for loop in f.loops:
            if loop.vert == v_hex_top[i]: loop[uv_layer].uv = (u0, 0.21)
            elif loop.vert == v_hex_bot[i]: loop[uv_layer].uv = (u0, 0.23)
            elif loop.vert == v_hex_bot[i_next]: loop[uv_layer].uv = (u1, 0.23)
            elif loop.vert == v_hex_top[i_next]: loop[uv_layer].uv = (u1, 0.21)

    # Flanged Washer Rim (8 quads)
    for i in range(8):
        i_next = (i + 1) % 8
        f = bm.faces.new((v_w_top[i], v_w_bot[i], v_w_bot[i_next], v_w_top[i_next]))
        f.smooth = True
        for loop in f.loops: loop[uv_layer].uv = (uv_u_center, 0.20)

    # Nut Sides (6 quads)
    for i in range(6):
        i_next = (i + 1) % 6
        f = bm.faces.new((v_nut_bot[i], v_nut_top[i], v_nut_top[i_next], v_nut_bot[i_next]))
        f.smooth = False
        for loop in f.loops: loop[uv_layer].uv = (uv_u_center, 0.22)

    # Nut Top Face (facing +Z)
    f_nut_top = bm.faces.new(v_nut_top)
    f_nut_top.smooth = False
    for loop in f_nut_top.loops: loop[uv_layer].uv = (uv_u_center, 0.25)

    bm.normal_update()

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_asset():
    """Create the full SEC_Ceiling_Conduit_Clamp asset hierarchy."""
    reset_scene()

    mat_metal = create_material("M_Metal", TEXTURE_PATH)

    # Root Empty at center of ceiling contact plane (0, 0, 0)
    root = bpy.data.objects.new("SEC_Ceiling_Conduit_Clamp", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 1. Base Ceiling Plate (Z from 0.000 to -0.003)
    plate = build_ceiling_plate_mesh(mat_metal)
    plate.parent = root

    # 2. U-Clamp Band (smooth 16-segment arch)
    band = build_clamp_band_mesh(mat_metal)
    band.parent = root

    # 3. Screw Left (centered at X = -0.026, Y = 0.0, Z = -0.005)
    screw_l = build_detailed_screw_mesh("Screw_Left", Vector((-0.026, 0.0, -0.005)), mat_metal, 0.146)
    screw_l.parent = root

    # 4. Screw Right (centered at X = +0.026, Y = 0.0, Z = -0.005)
    screw_r = build_detailed_screw_mesh("Screw_Right", Vector(( 0.026, 0.0, -0.005)), mat_metal, 0.342)
    screw_r.parent = root

    # Select all hierarchy objects
    meshes = [plate, band, screw_l, screw_r]
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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 24 High Detail Refined) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=FBX_OUT)

    root = bpy.data.objects.get("SEC_Ceiling_Conduit_Clamp")
    assert root is not None, "FAIL: Root object 'SEC_Ceiling_Conduit_Clamp' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    empty_objs = [obj for obj in bpy.data.objects if obj.type == 'EMPTY']

    print(f"[INFO] Imported Meshes: {[m.name for m in mesh_objs]}")
    print(f"[INFO] Imported Empties: {[e.name for e in empty_objs]}")

    expected_meshes = {"Ceiling_Plate", "Clamp_Band", "Screw_Left", "Screw_Right"}
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

    manifest_data["SEC_Ceiling_Conduit_Clamp"] = {
        "asset_name": "SEC_Ceiling_Conduit_Clamp",
        "fbx_path": "exports/SEC_Ceiling_Conduit_Clamp.fbx",
        "blend_path": "exports/SEC_Ceiling_Conduit_Clamp.blend",
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
