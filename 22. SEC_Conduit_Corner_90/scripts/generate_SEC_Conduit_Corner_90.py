"""
=============================================================================
Security CCTV Asset Production Suite - Asset 22 (High Detail Refinement)
Asset Name: SEC_Conduit_Corner_90
Production Script (Blender 4.x / 5.x Python API)
Description: High-fidelity 90-degree industrial metal conduit elbow (25mm OD, 21mm ID)
             with 20-radial smooth bore, straight tangent ends, sealed collars,
             and authentic 3D radial set-screws.
Hierarchy:
    SEC_Conduit_Corner_90 (Root Empty at 0, 0, 0 - theoretical axes intersection)
     ├── Elbow_Pipe (Mesh, 90-deg sweep from Y-axis to X-axis)
     ├── End_Collar_A (Mesh, at Y-end compression coupler)
     └── End_Collar_B (Mesh, at X-end compression coupler)
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
FBX_OUT = os.path.join(EXPORTS_DIR, "SEC_Conduit_Corner_90.fbx")
BLEND_OUT = os.path.join(EXPORTS_DIR, "SEC_Conduit_Corner_90.blend")
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

    node_bsdf.inputs['Metallic'].default_value = 0.90
    node_bsdf.inputs['Roughness'].default_value = 0.35

    if os.path.exists(texture_path):
        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.location = (-400, 0)
        img = bpy.data.images.load(texture_path)
        node_tex.image = img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    else:
        node_bsdf.inputs['Base Color'].default_value = (0.75, 0.76, 0.78, 1.0)

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat


def build_elbow_pipe_mesh(mat):
    """
    Construct high-fidelity 90-degree hollow conduit elbow.
    Sweep from Y-axis to X-axis with radius R = 0.080 m.
    Includes straight tangent extensions of 0.025 m at both ends.
    Total length along each axis: R + 0.025 = 0.105 m.
    OD = 0.025 m (radius 0.0125 m), ID = 0.021 m (radius 0.0105 m, 2mm wall).
    20 radial segments x 12 longitudinal segments.
    """
    R_bend = 0.080
    L_tangent = 0.025
    r_out = 0.0125
    r_in = 0.0105
    n_radial = 20
    n_curve = 10

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    outer_rings = []
    inner_rings = []

    center_frames = []

    # 1. Straight X extension tip
    center_frames.append({
        'center': Vector((R_bend + L_tangent, 0.0, 0.0)),
        'norm': Vector((0.0, -1.0, 0.0)),
        'binorm': Vector((0.0, 0.0, 1.0))
    })

    # 2. Curve rings (0 to n_curve)
    for i in range(n_curve + 1):
        t = i / float(n_curve)
        theta = 1.5 * math.pi - 0.5 * math.pi * t
        cx = R_bend * (1.0 + math.cos(theta))
        cy = R_bend * (1.0 + math.sin(theta))
        center_frames.append({
            'center': Vector((cx, cy, 0.0)),
            'norm': Vector((math.cos(theta), math.sin(theta), 0.0)),
            'binorm': Vector((0.0, 0.0, 1.0))
        })

    # 3. Straight Y extension tip
    center_frames.append({
        'center': Vector((0.0, R_bend + L_tangent, 0.0)),
        'norm': Vector((-1.0, 0.0, 0.0)),
        'binorm': Vector((0.0, 0.0, 1.0))
    })

    n_rings = len(center_frames)

    for i, frame in enumerate(center_frames):
        cen = frame['center']
        norm = frame['norm']
        binorm = frame['binorm']

        out_ring = []
        in_ring = []

        for j in range(n_radial):
            psi = j * (2.0 * math.pi / n_radial)
            offset = norm * math.cos(psi) + binorm * math.sin(psi)
            v_out = bm.verts.new(cen + offset * r_out)
            v_in = bm.verts.new(cen + offset * r_in)
            out_ring.append(v_out)
            in_ring.append(v_in)

        outer_rings.append(out_ring)
        inner_rings.append(in_ring)

    bm.verts.ensure_lookup_table()

    # Outer surface quads
    for i in range(n_rings - 1):
        t0 = i / float(n_rings - 1)
        t1 = (i + 1) / float(n_rings - 1)
        v0 = 0.55 + 0.40 * t0
        v1 = 0.55 + 0.40 * t1

        for j in range(n_radial):
            j_next = (j + 1) % n_radial
            va = outer_rings[i][j]
            vb = outer_rings[i][j_next]
            vc = outer_rings[i + 1][j_next]
            vd = outer_rings[i + 1][j]

            f = bm.faces.new((va, vb, vc, vd))
            f.smooth = True

            u0 = j / float(n_radial)
            u1 = (j + 1) / float(n_radial)
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    # Inner surface quads (facing inward)
    for i in range(n_rings - 1):
        t0 = i / float(n_rings - 1)
        t1 = (i + 1) / float(n_rings - 1)
        v0 = 0.35 + 0.15 * t0
        v1 = 0.35 + 0.15 * t1

        for j in range(n_radial):
            j_next = (j + 1) % n_radial
            va = inner_rings[i][j]
            vb = inner_rings[i][j_next]
            vc = inner_rings[i + 1][j_next]
            vd = inner_rings[i + 1][j]

            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True

            u0 = j / float(n_radial)
            u1 = (j + 1) / float(n_radial)
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    # End Rim 0: at i = 0 (X-end, facing +X)
    for j in range(n_radial):
        j_next = (j + 1) % n_radial
        v_out_a = outer_rings[0][j]
        v_out_b = outer_rings[0][j_next]
        v_in_b = inner_rings[0][j_next]
        v_in_a = inner_rings[0][j]

        f = bm.faces.new((v_out_a, v_in_a, v_in_b, v_out_b))
        f.smooth = False

        ang0 = j * (2.0 * math.pi / n_radial)
        ang1 = (j + 1) * (2.0 * math.pi / n_radial)
        cx_uv, cy_uv = 0.85, 0.40
        r_uv_out = 0.04
        r_uv_in = 0.03
        for loop in f.loops:
            if loop.vert == v_out_a: loop[uv_layer].uv = (cx_uv + r_uv_out * math.cos(ang0), cy_uv + r_uv_out * math.sin(ang0))
            elif loop.vert == v_in_a: loop[uv_layer].uv = (cx_uv + r_uv_in * math.cos(ang0), cy_uv + r_uv_in * math.sin(ang0))
            elif loop.vert == v_in_b: loop[uv_layer].uv = (cx_uv + r_uv_in * math.cos(ang1), cy_uv + r_uv_in * math.sin(ang1))
            elif loop.vert == v_out_b: loop[uv_layer].uv = (cx_uv + r_uv_out * math.cos(ang1), cy_uv + r_uv_out * math.sin(ang1))

    # End Rim 1: at i = n_rings - 1 (Y-end, facing +Y)
    last_i = n_rings - 1
    for j in range(n_radial):
        j_next = (j + 1) % n_radial
        v_out_a = outer_rings[last_i][j]
        v_out_b = outer_rings[last_i][j_next]
        v_in_b = inner_rings[last_i][j_next]
        v_in_a = inner_rings[last_i][j]

        f = bm.faces.new((v_out_a, v_out_b, v_in_b, v_in_a))
        f.smooth = False

        ang0 = j * (2.0 * math.pi / n_radial)
        ang1 = (j + 1) * (2.0 * math.pi / n_radial)
        cx_uv, cy_uv = 0.92, 0.40
        r_uv_out = 0.04
        r_uv_in = 0.03
        for loop in f.loops:
            if loop.vert == v_out_a: loop[uv_layer].uv = (cx_uv + r_uv_out * math.cos(ang0), cy_uv + r_uv_out * math.sin(ang0))
            elif loop.vert == v_out_b: loop[uv_layer].uv = (cx_uv + r_uv_out * math.cos(ang1), cy_uv + r_uv_out * math.sin(ang1))
            elif loop.vert == v_in_b: loop[uv_layer].uv = (cx_uv + r_uv_in * math.cos(ang1), cy_uv + r_uv_in * math.sin(ang1))
            elif loop.vert == v_in_a: loop[uv_layer].uv = (cx_uv + r_uv_in * math.cos(ang0), cy_uv + r_uv_in * math.sin(ang0))

    bm.normal_update()

    mesh = bpy.data.meshes.new("Elbow_Pipe")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Elbow_Pipe", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_detailed_collar(name, axis, pos, length, r_pipe, r_base, r_knurl, mat):
    """
    Build high-detail industrial EMT set-screw compression coupling collar.
    Fully sealed against pipe (no hollow gap).
    Includes realistic 3D radial threaded boss and 3D slotted set-screw.
    """
    bm = bmesh.new()
    n_radial = 20
    uv_layer = bm.loops.layers.uv.new("UVMap")

    l_half = length * 0.5
    # Profile along length:
    # 0: rear contact with pipe (r_pipe = 0.0125 m)
    # 1: rear bevel up to collar body (r_base = 0.0142 m)
    # 2: center knurled ring (r_knurl = 0.0155 m)
    # 3: front threaded sleeve (r_base = 0.0142 m)
    # 4: front stop lip down to pipe (r_pipe = 0.0125 m)
    sections = [
        (-l_half, r_pipe),
        (-l_half + length * 0.15, r_base),
        (-l_half + length * 0.45, r_knurl),
        (-l_half + length * 0.85, r_knurl),
        (l_half, r_base),
        (l_half, r_pipe)
    ]

    rings = []
    for sec_pos, sec_r in sections:
        ring = []
        for j in range(n_radial):
            ang = j * (2.0 * math.pi / n_radial)
            ca = math.cos(ang) * sec_r
            sa = math.sin(ang) * sec_r

            if axis == 'Y':
                pt = pos + Vector((ca, sec_pos, sa))
            else: # 'X'
                pt = pos + Vector((sec_pos, ca, sa))
            ring.append(bm.verts.new(pt))
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    # Cylindrical/bevel section quads
    for s in range(len(sections) - 1):
        v_start = 0.05 + 0.23 * (s / float(len(sections) - 1))
        v_end = 0.05 + 0.23 * ((s + 1) / float(len(sections) - 1))

        for j in range(n_radial):
            j_next = (j + 1) % n_radial
            va = rings[s][j]
            vb = rings[s][j_next]
            vc = rings[s + 1][j_next]
            vd = rings[s + 1][j]

            if axis == 'Y':
                f = bm.faces.new((va, vb, vc, vd))
            else:
                f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True

            u0 = j / float(n_radial)
            u1 = (j + 1) / float(n_radial)
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v_start)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v_start)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v_end)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v_end)

    # 3D Radial Set-Screw & Boss on the collar:
    # Sits radially outward at the top (+Z):
    # Boss center in XY depends on axis:
    # For axis == 'Y': pos.y is collar center, screw is at Z = r_knurl, oriented along +Z.
    # For axis == 'X': pos.x is collar center, screw is at Z = r_knurl, oriented along +Z.
    boss_cen = Vector((pos.x, pos.y, r_knurl))
    r_boss = 0.0040
    h_boss = 0.0020
    r_screw = 0.0028
    h_screw = 0.0015

    # 1. 8-sided cylindrical Boss (along +Z)
    v_boss_bot = []
    v_boss_top = []
    n_sc = 8
    for k in range(n_sc):
        sang = k * (2.0 * math.pi / n_sc)
        bx = boss_cen.x + r_boss * math.cos(sang)
        by = boss_cen.y + r_boss * math.sin(sang)
        v_boss_bot.append(bm.verts.new(Vector((bx, by, boss_cen.z))))
        v_boss_top.append(bm.verts.new(Vector((bx, by, boss_cen.z + h_boss))))

    # 2. 8-sided cylindrical Set-Screw head (along +Z)
    v_sc_bot = []
    v_sc_top = []
    for k in range(n_sc):
        sang = k * (2.0 * math.pi / n_sc)
        sx = boss_cen.x + r_screw * math.cos(sang)
        sy = boss_cen.y + r_screw * math.sin(sang)
        v_sc_bot.append(bm.verts.new(Vector((sx, sy, boss_cen.z + h_boss))))
        v_sc_top.append(bm.verts.new(Vector((sx, sy, boss_cen.z + h_boss + h_screw))))

    bm.verts.ensure_lookup_table()

    # Boss side faces
    for k in range(n_sc):
        k_next = (k + 1) % n_sc
        f = bm.faces.new((v_boss_bot[k], v_boss_bot[k_next], v_boss_top[k_next], v_boss_top[k]))
        f.smooth = True
        for loop in f.loops: loop[uv_layer].uv = (0.28, 0.90)

    # Boss top rim (annular ring from r_boss down to r_screw)
    for k in range(n_sc):
        k_next = (k + 1) % n_sc
        f = bm.faces.new((v_boss_top[k], v_boss_top[k_next], v_sc_bot[k_next], v_sc_bot[k]))
        f.smooth = False
        for loop in f.loops: loop[uv_layer].uv = (0.28, 0.92)

    # Screw side faces
    for k in range(n_sc):
        k_next = (k + 1) % n_sc
        f = bm.faces.new((v_sc_bot[k], v_sc_bot[k_next], v_sc_top[k_next], v_sc_top[k]))
        f.smooth = False
        for loop in f.loops: loop[uv_layer].uv = (0.29, 0.95)

    # Screw top cap (facing +Z, mapped to slotted screw head texture)
    f_sc_top = bm.faces.new(v_sc_top)
    f_sc_top.smooth = False
    for loop in f_sc_top.loops:
        # Texture coordinates around (0.293, 0.031)
        # Pillow X: 600 -> U: 0.293, Pillow Y: 992 -> V: 1.0 - 992/1024 = 0.031
        u_sc = 0.293 + ((loop.vert.co.x - boss_cen.x) / r_screw) * 0.015
        v_sc = 0.031 + ((loop.vert.co.y - boss_cen.y) / r_screw) * 0.015
        loop[uv_layer].uv = (u_sc, v_sc)

    bm.normal_update()

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def build_asset():
    """Create the full SEC_Conduit_Corner_90 asset hierarchy."""
    reset_scene()

    mat_metal = create_material("M_Metal", TEXTURE_PATH)

    # Root Empty at theoretical intersection of axes (0, 0, 0)
    root = bpy.data.objects.new("SEC_Conduit_Corner_90", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 1. Elbow Pipe (with straight extensions, R=0.080, reach 0.105 m along Y and X)
    elbow = build_elbow_pipe_mesh(mat_metal)
    elbow.parent = root

    # 2. End Collar A (at Y-end, centered at Y = 0.105 - 0.012 = 0.093 m, length 0.024 m)
    collar_a = build_detailed_collar("End_Collar_A", 'Y', Vector((0.0, 0.093, 0.0)), 0.024, 0.0125, 0.0142, 0.0155, mat_metal)
    collar_a.parent = root

    # 3. End Collar B (at X-end, centered at X = 0.105 - 0.012 = 0.093 m, length 0.024 m)
    collar_b = build_detailed_collar("End_Collar_B", 'X', Vector((0.093, 0.0, 0.0)), 0.024, 0.0125, 0.0142, 0.0155, mat_metal)
    collar_b.parent = root

    # Select all hierarchy objects
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    elbow.select_set(True)
    collar_a.select_set(True)
    collar_b.select_set(True)
    bpy.context.view_layer.objects.active = root

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[OK] Saved .blend: {BLEND_OUT}")

    return root, [elbow, collar_a, collar_b]


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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 22 High Detail Refined) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=FBX_OUT)

    root = bpy.data.objects.get("SEC_Conduit_Corner_90")
    assert root is not None, "FAIL: Root object 'SEC_Conduit_Corner_90' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    empty_objs = [obj for obj in bpy.data.objects if obj.type == 'EMPTY']

    print(f"[INFO] Imported Meshes: {[m.name for m in mesh_objs]}")
    print(f"[INFO] Imported Empties: {[e.name for e in empty_objs]}")

    assert len(mesh_objs) == 3, f"FAIL: Expected 3 meshes, got {len(mesh_objs)}"

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

    pipe = bpy.data.objects.get("Elbow_Pipe")
    col_a = bpy.data.objects.get("End_Collar_A")
    col_b = bpy.data.objects.get("End_Collar_B")
    assert pipe and pipe.parent == root, "FAIL: Elbow_Pipe parent != root!"
    assert col_a and col_a.parent == root, "FAIL: Collar A parent != root!"
    assert col_b and col_b.parent == root, "FAIL: Collar B parent != root!"
    print("[PASS] Hierarchy relationships strictly verified!")

    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Conduit_Corner_90"] = {
        "asset_name": "SEC_Conduit_Corner_90",
        "fbx_path": "exports/SEC_Conduit_Corner_90.fbx",
        "blend_path": "exports/SEC_Conduit_Corner_90.blend",
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
