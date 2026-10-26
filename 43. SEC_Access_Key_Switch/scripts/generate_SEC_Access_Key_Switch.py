"""
=============================================================================
Security CCTV Asset Production Suite - Asset 43
Asset Name: SEC_Access_Key_Switch (Anahtarli Guvenlik Salteri)
Triangle Budget: <= 240 tris
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Metal

HIYERARSI:
    SEC_Access_Key_Switch (Root Empty @ 0,0,0)
     └── Faceplate        (Mesh, 70 x 70 x 6 mm paslanmaz celik on plaka)
          └── Key_Rotation_Pivot (Empty @ silindir merkezi; yerel Y -45°..+45°)
               ├── Key_Cylinder  (Mesh, Ø22 mm doner kilit gobegini temsil eder)
               └── Key_Blade     (Mesh, takili kilit anahtari ve tutamagi)
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Access_Key_Switch"
TRIS_BUDGET = 240
ROT_LIMIT_DEG = 45.0

# Boyutlar (metre)
PLATE_W, PLATE_H = 0.0700, 0.0700             # 70 x 70 mm
PLATE_D = 0.0060                               # 6 mm kalinlik
PLATE_CHAMFER = 0.0035

CYL_R = 0.0110                                 # Ø22 mm
CYL_PROUD = 0.0050                             # on plakadan 5 mm cikinti
CYL_SEG = 12

KEY_W = 0.0140                                 # anahtar basi genisligi
KEY_H = 0.0240                                 # anahtar basi boyu
KEY_THICK = 0.0024                             # 2.4 mm et kalinligi
KEY_PROUD = 0.0180                             # kilit gobeginin disindaki boy

# Doku UV dikdortgenleri
ATLAS_W, ATLAS_H = 2048, 2048
UV_RECT_PLATE = (32, 32, 1432, 1432)
UV_RECT_CYLINDER = (1480, 32, 1980, 532)
UV_RECT_KEY = (1480, 580, 1980, 1080)

PIX_METAL_LIGHT = (1650, 1250)
PIX_METAL_MID = (1850, 1250)
PIX_METAL_DARK = (1650, 1550)
PIX_CHROME = (1850, 1550)


def pix_to_uv(px, py):
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_LIGHT = pix_to_uv(*PIX_METAL_LIGHT)
FLAT_UV_MID = pix_to_uv(*PIX_METAL_MID)
FLAT_UV_DARK = pix_to_uv(*PIX_METAL_DARK)
FLAT_UV_CHROME = pix_to_uv(*PIX_CHROME)


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


def set_radial_uv(face, uv_layer, rect, cx, cz, r_out):
    u0, v0, u1, v1 = rect
    for loop in face.loops:
        nx = (loop.vert.co.x - cx) / r_out
        nz = (loop.vert.co.z - cz) / r_out
        u = u0 + (0.5 + 0.5 * nx) * (u1 - u0)
        v = v0 + (0.5 + 0.5 * nz) * (v1 - v0)
        loop[uv_layer].uv = (u, v)


def set_flat_uv(face, uv_layer, point=None):
    uv = point if point else FLAT_UV_LIGHT
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
    """X-Z duzleminde 8 noktali pahlanmis dikdortgen profili (CCW)."""
    return [
        (-hx + c, -hz), (hx - c, -hz), (hx, -hz + c), (hx, hz - c),
        (hx - c, hz), (-hx + c, hz), (-hx, hz - c), (-hx, -hz + c),
    ]


def setup_materials():
    """Slot 0 -> M_Security_Atlas, Slot 1 -> M_Metal."""
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
    b_a.inputs["Roughness"].default_value = 0.28
    b_a.inputs["Metallic"].default_value = 0.65
    mat_atlas.diffuse_color = (0.85, 0.88, 0.92, 1.0)

    # Slot 1: M_Metal
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    n_m = mat_metal.node_tree.nodes
    l_m = mat_metal.node_tree.links
    b_m = n_m.get("Principled BSDF")
    add_tex(n_m, l_m, b_m, (-420, -100))
    b_m.inputs["Roughness"].default_value = 0.16
    b_m.inputs["Metallic"].default_value = 0.95
    mat_metal.diffuse_color = (0.92, 0.93, 0.95, 1.0)

    return [mat_atlas, mat_metal]


def build_faceplate(mats):
    """Paslanmaz celik on panel: 70 x 70 x 6 mm."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx, hz = PLATE_W / 2.0, PLATE_H / 2.0
    prof = chamfer_profile(hx, hz, PLATE_CHAMFER)

    rings = [[bm.verts.new(Vector((p[0], yy, p[1]))) for p in prof]
             for yy in (0.0, PLATE_D)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_MID)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_PLATE),
                     flip_u=True, extent=(-hx, hx, -hz, hz))

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_MID)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Faceplate", mats)


def build_cylinder(mats):
    """Silindirik kilit gobegini temsil eden donel parca."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    y_base = PLATE_D - 0.0015
    y_top = PLATE_D + CYL_PROUD

    rings = []
    for yy in (y_base, y_top):
        ring = []
        for i in range(CYL_SEG):
            ang = i * (2.0 * math.pi / CYL_SEG)
            ring.append(bm.verts.new(Vector((math.cos(ang) * CYL_R, yy,
                                             math.sin(ang) * CYL_R))))
        rings.append(ring)

    f_base = bm.faces.new(list(reversed(rings[0])))
    f_base.smooth = False
    f_base.material_index = 1
    set_flat_uv(f_base, uv_layer, FLAT_UV_DARK)

    f_top = bm.faces.new(rings[1])
    f_top.smooth = False
    f_top.material_index = 0
    set_radial_uv(f_top, uv_layer, uv_rect_from_pixels(*UV_RECT_CYLINDER),
                  0.0, 0.0, CYL_R)

    for i in range(CYL_SEG):
        j = (i + 1) % CYL_SEG
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = True
        f.material_index = 1
        set_flat_uv(f, uv_layer, FLAT_UV_CHROME)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Key_Cylinder", mats)


def build_key_blade(mats):
    """Silindir keyway'ine takili metal anahtar ve tutamak."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    y_start = PLATE_D + CYL_PROUD - 0.0010
    y_end = y_start + KEY_PROUD

    hx = KEY_W / 2.0
    hz = KEY_THICK / 2.0

    # Anahtar profili: X-Z ekseninde 6 noktali baslik
    prof = [
        (-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz),
    ]

    rings = [[bm.verts.new(Vector((p[0], yy, p[1]))) for p in prof]
             for yy in (y_start, y_end)]

    f_bottom = bm.faces.new(list(reversed(rings[0])))
    f_bottom.smooth = False
    f_bottom.material_index = 1
    set_flat_uv(f_bottom, uv_layer, FLAT_UV_DARK)

    f_top = bm.faces.new(rings[1])
    f_top.smooth = False
    f_top.material_index = 1
    set_flat_uv(f_top, uv_layer, FLAT_UV_CHROME)

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 1
        # Yan yuzeylerde anahtar basi atlas dokusu
        set_face_uv_rect(f, uv_layer, uv_rect_from_pixels(*UV_RECT_KEY))

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Key_Blade", mats)


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

    faceplate = build_faceplate(mats)
    parent_keep(faceplate, root)

    # Key_Rotation_Pivot Empty @ silindir merkezi
    pivot = bpy.data.objects.new("Key_Rotation_Pivot", None)
    pivot.empty_display_type = 'ARROWS'
    pivot.empty_display_size = 0.015
    pivot.location = Vector((0.0, PLATE_D, 0.0))
    bpy.context.collection.objects.link(pivot)
    bpy.context.view_layer.update()
    parent_keep(pivot, faceplate)

    # LIMIT_ROTATION mafsali (yerel Y ekseninde -45° .. +45°)
    con = pivot.constraints.new('LIMIT_ROTATION')
    con.owner_space = 'LOCAL'
    con.use_limit_y = True
    con.min_y = -math.radians(ROT_LIMIT_DEG)
    con.max_y = math.radians(ROT_LIMIT_DEG)
    con.use_limit_x = con.use_limit_z = True
    con.min_x = con.max_x = con.min_z = con.max_z = 0.0

    pivot["rot_min_deg"] = -ROT_LIMIT_DEG
    pivot["rot_max_deg"] = ROT_LIMIT_DEG
    pivot["rot_axis"] = "Y"
    pivot["rest_rot_deg"] = 0.0

    cylinder = build_cylinder(mats)
    parent_keep(cylinder, pivot)

    blade = build_key_blade(mats)
    parent_keep(blade, pivot)

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
    assert pivot.type == 'EMPTY', "FAIL: Key_Rotation_Pivot must be an Empty"
    loc = pivot.location
    print(f"[QA] Key_Rotation_Pivot konumu: ({loc.x*1000:.2f}, {loc.y*1000:.2f}, {loc.z*1000:.2f}) mm")
    assert abs(loc.x) < 1e-6 and abs(loc.z) < 1e-6, "FAIL: Pivot must be at X=0, Z=0"
    assert abs(loc.y - PLATE_D) < 1e-6, "FAIL: Pivot must be on front face plane"

    lo = pivot.get("rot_min_deg")
    hi = pivot.get("rot_max_deg")
    ax = pivot.get("rot_axis")
    print(f"[QA] Pivot limit custom properties: {lo}° .. {hi}°, axis={ax}")
    assert lo == -ROT_LIMIT_DEG and hi == ROT_LIMIT_DEG and ax == "Y", \
        "FAIL: custom properties mismatch"


def main():
    clean_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    mats = setup_materials()
    root = build_all(mats)

    pivot = bpy.data.objects.get("Key_Rotation_Pivot")
    qa_pivot(pivot)

    bpy.context.view_layer.update()
    for obj in bpy.data.objects:
        obj.scale = (1.0, 1.0, 1.0)
        if obj.type == 'EMPTY':
            obj.rotation_euler = (0.0, 0.0, 0.0)
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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 43) ---")
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

    assert sorted(empty_names) == sorted([ASSET_NAME, "Key_Rotation_Pivot"]), \
        f"FAIL: expected exactly root + Key_Rotation_Pivot, found {empty_names}"
    print("[PASS] Exactly one moving pivot empty verified!")

    # Hierarchy verification
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    assert objs["Faceplate"].parent == re_root, "FAIL: Faceplate must be child of Root"
    assert objs["Key_Rotation_Pivot"].parent == objs["Faceplate"], "FAIL: Pivot must be child of Faceplate"
    assert objs["Key_Cylinder"].parent == objs["Key_Rotation_Pivot"], "FAIL: Key_Cylinder must be child of Pivot"
    assert objs["Key_Blade"].parent == objs["Key_Rotation_Pivot"], "FAIL: Key_Blade must be child of Pivot"
    print("[PASS] Parent-child hierarchy verified!")

    # Material slots verification
    expected_mats = ["M_Security_Atlas", "M_Metal"]
    for name in ("Faceplate", "Key_Cylinder", "Key_Blade"):
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:2] == expected_mats, f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0 Atlas, Slot 1 Metal)!")

    # Contact QA
    contact_pairs = [
        ("Key_Cylinder", "Faceplate"),
        ("Key_Blade", "Key_Cylinder"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} pairs)!")

    # Dimensions
    hs = world_aabb(objs["Faceplate"])
    hx = (hs[1].x - hs[0].x) * 1000.0
    hz = (hs[1].z - hs[0].z) * 1000.0
    hy = (hs[1].y - hs[0].y) * 1000.0
    print(f"[QA] Faceplate olcusu: {hx:.1f} x {hy:.1f} x {hz:.1f} mm")
    assert abs(hx - 70.0) < 0.3 and abs(hz - 70.0) < 0.3 and abs(hy - 6.0) < 0.3, \
        "FAIL: Faceplate must be 70 x 70 x 6 mm"
    print("[PASS] Faceplate dimensions exact (70 x 70 x 6 mm)!")

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
        "moving_pivots": ["Key_Rotation_Pivot"],
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
