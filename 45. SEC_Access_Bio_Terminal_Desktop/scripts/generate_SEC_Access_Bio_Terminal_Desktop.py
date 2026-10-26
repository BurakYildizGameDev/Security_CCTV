"""
=============================================================================
Security CCTV Asset Production Suite - Asset 45
Asset Name: SEC_Access_Bio_Terminal_Desktop (Masaustu Biyometrik Terminal)
Triangle Budget: <= 400 tris
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Screen , Slot 2 -> M_Emission

HIYERARSI:
    SEC_Access_Bio_Terminal_Desktop (Root Empty @ 0,0,0 - masa duzlemi)
     └── Stand_Base                 (Mesh, Slot 0 - 76 x 84 x 10 mm ayak + boyun)
          └── Tilt_Pivot            (Empty @ ekran arkasi boyun mafsali; yerel X ±15°)
               └── Terminal_Housing (Mesh, Slot 0 - 68 x 100 x 24 mm acili baslik)
                    ├── Display     (Mesh, Slot 1 M_Screen - 48 x 32 mm LCD ekran)
                    └── Fingerprint_Pad (Mesh, Slot 2 M_Emission - 22 x 26 mm optik prizma)
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import math
import os
import json

ASSET_NAME = "SEC_Access_Bio_Terminal_Desktop"
TRIS_BUDGET = 400
TILT_LIMIT_DEG = 15.0

# Boyutlar (metre)
BASE_W, BASE_L, BASE_H = 0.0760, 0.0840, 0.0100
PIVOT_POS = Vector((0.0, -0.0060, 0.0620))

HEAD_W, HEAD_H, HEAD_D = 0.0680, 0.1000, 0.0240
HEAD_CHAMFER = 0.0040
HEAD_TILT_DEG = 25.0                          # Ergonomik masaustu gorus acisi

SCR_W, SCR_H = 0.0480, 0.0320
SCR_POS_Z = 0.0180                            # Baslik yerel duzleminde ekran konumu

FING_W, FING_H = 0.0220, 0.0260
FING_POS_Z = -0.0230

PROUD = 0.0003                                # 0.30 mm cikinti (SOP kurali)

ATLAS_W, ATLAS_H = 2048, 2048
UV_RECT_HOUSING = (32, 32, 1032, 1500)
UV_RECT_SCREEN = (1100, 32, 1800, 500)
UV_RECT_PRISM = (1100, 540, 1600, 1040)

PIX_BODY_GRAY = (1250, 1200)
PIX_DARK_BEZEL = (1500, 1200)
PIX_RUBBER = (1500, 1500)


def pix_to_uv(px, py):
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_BODY_GRAY)
FLAT_UV_BEZEL = pix_to_uv(*PIX_DARK_BEZEL)
FLAT_UV_RUBBER = pix_to_uv(*PIX_RUBBER)


def uv_rect_from_pixels(x0, y0, x1, y1):
    return (x0 / ATLAS_W, 1.0 - (y1 / ATLAS_H), x1 / ATLAS_W, 1.0 - (y0 / ATLAS_H))


def set_face_uv_rect(face, uv_layer, rect, flip_u=False, extent=None):
    u0, v0, u1, v1 = rect
    if extent is not None:
        minx, maxx, minz, maxz = extent
    else:
        xs = [loop.vert.co.x for loop in face.loops]
        zs = [loop.vert.co.z for loop in face.loops]
        minx, maxx = min(xs), max(xs)
        minz, maxz = min(zs), max(zs)

    dx = (maxx - minx) if (maxx - minx) > 1e-9 else 1.0
    dz = (maxz - minz) if (maxz - minz) > 1e-9 else 1.0

    for loop in face.loops:
        nx = (loop.vert.co.x - minx) / dx
        nz = (loop.vert.co.z - minz) / dz
        u = (u1 - nx * (u1 - u0)) if flip_u else (u0 + nx * (u1 - u0))
        v = v0 + nz * (v1 - v0)
        loop[uv_layer].uv = (u, v)


def set_flat_uv(face, uv_layer, point=None):
    uv = point if point else FLAT_UV_BODY
    for loop in face.loops:
        loop[uv_layer].uv = uv


def mark_sharp_edges_by_angle(bm, threshold_deg=35.0):
    threshold = math.radians(threshold_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            edge.smooth = edge.calc_face_angle(0.0) < threshold


def finish_mesh(bm, name, mats):
    bm.normal_update()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def chamfer_profile(hx, hz, c):
    return [
        (-hx + c, -hz), (hx - c, -hz), (hx, -hz + c), (hx, hz - c),
        (hx - c, hz), (-hx + c, hz), (-hx, hz - c), (-hx, -hz + c),
    ]


def setup_materials():
    """Slot 0 -> M_Security_Atlas, Slot 1 -> M_Screen, Slot 2 -> M_Emission."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    tex_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    def add_tex(nodes, links, bsdf, loc):
        if not os.path.exists(tex_path):
            return None
        tex = nodes.new("ShaderNodeTexImage")
        img = bpy.data.images.load(tex_path)
        try:
            img.pack()
        except Exception:
            pass
        tex.image = img
        tex.image.colorspace_settings.name = 'sRGB'
        tex.interpolation = 'Linear'
        tex.location = loc
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        return tex

    # Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    n_a = mat_atlas.node_tree.nodes
    l_a = mat_atlas.node_tree.links
    b_a = n_a.get("Principled BSDF")
    add_tex(n_a, l_a, b_a, (-420, 200))
    b_a.inputs["Roughness"].default_value = 0.35
    b_a.inputs["Metallic"].default_value = 0.15
    mat_atlas.diffuse_color = (0.22, 0.26, 0.30, 1.0)

    # Slot 1: M_Screen
    mat_screen = bpy.data.materials.new("M_Screen")
    mat_screen.use_nodes = True
    n_s = mat_screen.node_tree.nodes
    l_s = mat_screen.node_tree.links
    b_s = n_s.get("Principled BSDF")
    tex_s = add_tex(n_s, l_s, b_s, (-420, 120))
    scr_col = (0.12, 0.40, 0.55, 1.0)
    if tex_s is not None:
        for key in ("Emission Color", "Emission"):
            if key in b_s.inputs:
                l_s.new(tex_s.outputs["Color"], b_s.inputs[key])
                break
    for key in ("Emission Color", "Emission"):
        if key in b_s.inputs:
            b_s.inputs[key].default_value = scr_col
            break
    if "Emission Strength" in b_s.inputs:
        b_s.inputs["Emission Strength"].default_value = 1.40
    mat_screen.diffuse_color = scr_col

    # Slot 2: M_Emission (optik biyometrik prizma parlamasi)
    mat_em = bpy.data.materials.new("M_Emission")
    mat_em.use_nodes = True
    n_e = mat_em.node_tree.nodes
    l_e = mat_em.node_tree.links
    b_e = n_e.get("Principled BSDF")
    tex_e = add_tex(n_e, l_e, b_e, (-420, -100))
    em_col = (0.20, 0.95, 0.45, 1.0)
    if tex_e is not None:
        for key in ("Emission Color", "Emission"):
            if key in b_e.inputs:
                l_e.new(tex_e.outputs["Color"], b_e.inputs[key])
                break
    for key in ("Emission Color", "Emission"):
        if key in b_e.inputs:
            b_e.inputs[key].default_value = em_col
            break
    if "Emission Strength" in b_e.inputs:
        b_e.inputs["Emission Strength"].default_value = 5.0
    mat_em.diffuse_color = em_col

    return [mat_atlas, mat_screen, mat_em]


def build_stand_base(mats):
    """Masa ayagi ve boyun geometrisi: taban 76 x 84 x 10 mm + boyun dikmesi."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx, hy = BASE_W / 2.0, BASE_L / 2.0
    prof = chamfer_profile(hx, hy, 0.0060)

    # Z ekseninde taban ekstruzyonu (0.0 -> BASE_H)
    rings = [[bm.verts.new(Vector((p[0], p[1], zz))) for p in prof]
             for zz in (0.0, BASE_H)]

    f_bot = bm.faces.new(list(reversed(rings[0])))
    f_bot.smooth = False
    f_bot.material_index = 0
    set_flat_uv(f_bot, uv_layer, FLAT_UV_RUBBER)

    f_top = bm.faces.new(rings[1])
    f_top.smooth = False
    f_top.material_index = 0
    set_flat_uv(f_top, uv_layer, FLAT_UV_BODY)

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BEZEL)

    # Boyun dikmesi (mafsala yukselen kompakt kule)
    neck_prof = [
        (-0.014, -0.020), (0.014, -0.020), (0.014, 0.004), (-0.014, 0.004)
    ]
    neck_rings = [[bm.verts.new(Vector((p[0], p[1], zz))) for p in neck_prof]
                  for zz in (BASE_H - 0.001, PIVOT_POS.z + 0.004)]

    for i in range(4):
        j = (i + 1) % 4
        f = bm.faces.new((neck_rings[0][i], neck_rings[0][j], neck_rings[1][j], neck_rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BODY)

    f_neck_top = bm.faces.new(neck_rings[1])
    f_neck_top.smooth = False
    f_neck_top.material_index = 0
    set_flat_uv(f_neck_top, uv_layer, FLAT_UV_BEZEL)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Stand_Base", mats)


def build_terminal_housing(mats):
    """Mafsaldan yukselen egimli baslik kasasi: 68 x 100 x 24 mm."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx, hz = HEAD_W / 2.0, HEAD_H / 2.0
    prof = chamfer_profile(hx, hz, HEAD_CHAMFER)

    # Baslik yerel uzayinda: Y ekseni bakis derinligi, X genislik, Z yukseklik
    y_back = -HEAD_D / 2.0
    y_front = HEAD_D / 2.0

    rings = [[bm.verts.new(Vector((p[0], yy, p[1]))) for p in prof]
             for yy in (y_back, y_front)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_HOUSING),
                     flip_u=True, extent=(-hx, hx, -hz, hz))

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BEZEL)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Terminal_Housing", mats)


def build_display(mats):
    """LCD ekran cami: 48 x 32 mm, 0.30 mm cikinti."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx, hz = SCR_W / 2.0, SCR_H / 2.0
    prof = chamfer_profile(hx, hz, 0.0020)

    y_front = HEAD_D / 2.0
    y_base = y_front - 0.0010
    y_top = y_front + PROUD

    rings = [[bm.verts.new(Vector((p[0], yy, SCR_POS_Z + p[1]))) for p in prof]
             for yy in (y_base, y_top)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 1
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 1
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_SCREEN),
                     flip_u=True, extent=(-hx, hx, SCR_POS_Z - hz, SCR_POS_Z + hz))

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 1
        set_flat_uv(f, uv_layer, FLAT_UV_BEZEL)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Display", mats)


def build_fingerprint_pad(mats):
    """Optik biyometrik prizma: 22 x 26 mm, 0.30 mm cikinti."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx, hz = FING_W / 2.0, FING_H / 2.0
    prof = chamfer_profile(hx, hz, 0.0025)

    y_front = HEAD_D / 2.0
    y_base = y_front - 0.0010
    y_top = y_front + PROUD

    rings = [[bm.verts.new(Vector((p[0], yy, FING_POS_Z + p[1]))) for p in prof]
             for yy in (y_base, y_top)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 2
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 2
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_PRISM),
                     flip_u=True, extent=(-hx, hx, FING_POS_Z - hz, FING_POS_Z + hz))

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 2
        set_flat_uv(f, uv_layer, FLAT_UV_BEZEL)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Fingerprint_Pad", mats)


def parent_keep(child, parent):
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def world_aabb(obj):
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return (
        Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )


def parts_in_contact(a_obj, b_obj, tol=0.0002):
    a_min, a_max = world_aabb(a_obj)
    b_min, b_max = world_aabb(b_obj)
    for i in range(3):
        gap = max(a_min[i], b_min[i]) - min(a_max[i], b_max[i])
        if gap > tol:
            return False
    return True


def build_all(mats):
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    stand = build_stand_base(mats)
    parent_keep(stand, root)

    # Tilt_Pivot Empty @ ekran arkasi boyun mafsali
    pivot = bpy.data.objects.new("Tilt_Pivot", None)
    pivot.empty_display_type = 'ARROWS'
    pivot.empty_display_size = 0.02
    pivot.location = PIVOT_POS
    pivot.rotation_euler = (math.radians(HEAD_TILT_DEG), 0.0, 0.0)
    bpy.context.collection.objects.link(pivot)
    bpy.context.view_layer.update()
    parent_keep(pivot, stand)

    con = pivot.constraints.new('LIMIT_ROTATION')
    con.owner_space = 'LOCAL'
    con.use_limit_x = True
    con.min_x = -math.radians(TILT_LIMIT_DEG)
    con.max_x = math.radians(TILT_LIMIT_DEG)
    con.use_limit_y = con.use_limit_z = True
    con.min_y = con.max_y = con.min_z = con.max_z = 0.0

    pivot["rot_min_deg"] = -TILT_LIMIT_DEG
    pivot["rot_max_deg"] = TILT_LIMIT_DEG
    pivot["rot_axis"] = "X"
    pivot["rest_tilt_deg"] = HEAD_TILT_DEG

    # Baslik govdesi (pivot uzayinda orantili yerlesim)
    housing = build_terminal_housing(mats)
    housing.parent = pivot
    housing.matrix_parent_inverse.identity()
    housing.location = Vector((0.0, 0.010, 0.0))

    # Ekran ve Parmak Izi
    display = build_display(mats)
    display.parent = housing
    display.matrix_parent_inverse.identity()
    display.location = Vector((0.0, 0.0, 0.0))

    fpad = build_fingerprint_pad(mats)
    fpad.parent = housing
    fpad.matrix_parent_inverse.identity()
    fpad.location = Vector((0.0, 0.0, 0.0))

    bpy.context.view_layer.update()
    return root


def clean_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'


def qa_pivot(pivot):
    assert pivot.type == 'EMPTY', "FAIL: Tilt_Pivot must be an Empty"
    loc = pivot.location
    print(f"[QA] Tilt_Pivot konumu: ({loc.x*1000:.2f}, {loc.y*1000:.2f}, {loc.z*1000:.2f}) mm")
    assert abs(loc.x) < 1e-6, "FAIL: Pivot must be centered on X"

    lo = pivot.get("rot_min_deg")
    hi = pivot.get("rot_max_deg")
    ax = pivot.get("rot_axis")
    print(f"[QA] Pivot limit custom properties: {lo}° .. {hi}°, axis={ax}")
    assert lo == -TILT_LIMIT_DEG and hi == TILT_LIMIT_DEG and ax == "X", \
        "FAIL: custom properties mismatch"


def main():
    clean_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    mats = setup_materials()
    root = build_all(mats)

    pivot = bpy.data.objects.get("Tilt_Pivot")
    qa_pivot(pivot)

    bpy.context.view_layer.update()
    for obj in bpy.data.objects:
        obj.scale = (1.0, 1.0, 1.0)
    bpy.context.view_layer.update()

    boxes = [world_aabb(o) for o in bpy.data.objects if o.type == 'MESH']
    gmin = Vector((min(b[0].x for b in boxes), min(b[0].y for b in boxes), min(b[0].z for b in boxes)))
    gmax = Vector((max(b[1].x for b in boxes), max(b[1].y for b in boxes), max(b[1].z for b in boxes)))
    print(f"[INFO] Overall size: {(gmax.x - gmin.x) * 1000:.1f} x {(gmax.y - gmin.y) * 1000:.1f} x {(gmax.z - gmin.z) * 1000:.1f} mm")

    blend_path = os.path.join(exports_dir, ASSET_NAME + ".blend")
    fbx_path = os.path.join(exports_dir, ASSET_NAME + ".fbx")

    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root

    fbx_kwargs = dict(
        filepath=fbx_path,
        use_selection=True,
        object_types={'MESH', 'EMPTY'},
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,
        bake_space_transform=False,
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode='AUTO',
    )
    try:
        bpy.ops.export_scene.fbx(use_custom_props=True, **fbx_kwargs)
    except TypeError:
        bpy.ops.export_scene.fbx(**fbx_kwargs)
    print(f"[OK] Exported FBX: {fbx_path}")

    # Re-import QA
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 45) ---")
    clean_scene()
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    re_root = bpy.data.objects.get(ASSET_NAME)
    assert re_root is not None, f"FAIL: Root {ASSET_NAME} missing in FBX"
    assert re_root.type == 'EMPTY', "FAIL: Root must be an Empty"
    print(f"[PASS] Root empty found: {re_root.name}")

    total_tris = 0
    mesh_names, empty_names, uv_missing = [], [], []
    for obj in [re_root] + re_root.children_recursive:
        if obj.type == 'MESH':
            mesh_names.append(obj.name)
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            tris = len(bm.faces)
            bm.free()
            total_tris += tris
            print(f"       -> {obj.name}: {tris} tris")
            if not obj.data.uv_layers or len(obj.data.uv_layers[0].data) == 0:
                uv_missing.append(obj.name)
        elif obj.type == 'EMPTY':
            empty_names.append(obj.name)

    print(f"[QA] Total Triangles: {total_tris} (butce {TRIS_BUDGET})")
    assert total_tris <= TRIS_BUDGET, f"FAIL: Total triangles {total_tris} exceeds {TRIS_BUDGET} budget!"
    print(f"[PASS] Triangle count verified strictly (<= {TRIS_BUDGET})!")
    assert not uv_missing, f"FAIL: Missing/empty UV layer on: {uv_missing}"
    print("[PASS] UV layers present on all meshes!")

    assert sorted(empty_names) == sorted([ASSET_NAME, "Tilt_Pivot"]), \
        f"FAIL: expected exactly root + Tilt_Pivot, found {empty_names}"
    print("[PASS] Exactly one moving pivot empty verified!")

    # Hierarchy verification
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    assert objs["Stand_Base"].parent == re_root, "FAIL: Stand_Base must be child of Root"
    assert objs["Tilt_Pivot"].parent == objs["Stand_Base"], "FAIL: Pivot must be child of Stand_Base"
    assert objs["Terminal_Housing"].parent == objs["Tilt_Pivot"], "FAIL: Housing must be child of Pivot"
    assert objs["Display"].parent == objs["Terminal_Housing"], "FAIL: Display must be child of Housing"
    assert objs["Fingerprint_Pad"].parent == objs["Terminal_Housing"], "FAIL: Fingerprint_Pad must be child of Housing"
    print("[PASS] Parent-child hierarchy verified (4 meshes + 1 pivot)!")

    # Material slots verification
    expected_mats = ["M_Security_Atlas", "M_Screen", "M_Emission"]
    for name in ("Stand_Base", "Terminal_Housing", "Display", "Fingerprint_Pad"):
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:3] == expected_mats, f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0 Atlas, Slot 1 Screen, Slot 2 Emission)!")

    # Contact QA
    contact_pairs = [
        ("Terminal_Housing", "Stand_Base"),
        ("Display", "Terminal_Housing"),
        ("Fingerprint_Pad", "Terminal_Housing"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} pairs)!")

    # Update manifest
    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    manifest[ASSET_NAME] = {
        "asset_name": ASSET_NAME,
        "fbx_path": f"exports/{ASSET_NAME}.fbx",
        "blend_path": f"exports/{ASSET_NAME}.blend",
        "tris_count": total_tris,
        "mesh_count": len(mesh_names),
        "empty_count": len(empty_names),
        "materials": expected_mats,
        "moving_pivots": ["Tilt_Pivot"],
        "status": "SUCCESS"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Updated manifest: {manifest_path}")

    # Remove .blend1 backup
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[CLEAN] Removed backup: {blend1_path}")

    print("[ALL QA CHECKS PASSED SUCCESSFULLY]")


if __name__ == "__main__":
    main()
