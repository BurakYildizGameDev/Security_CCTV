"""
=============================================================================
Security CCTV Asset Production Suite - Asset 44
Asset Name: SEC_Access_Card_Reader_Rugged (Endustriyel RFID Okuyucu)
Triangle Budget: <= 340 tris
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Emission , Slot 2 -> M_Metal

HIYERARSI:
    SEC_Access_Card_Reader_Rugged (Root Empty @ 0,0,0)
     └── Backplate               (Mesh, Slot 0 - 60 x 120 x 4 mm montaj plakasi)
          └── Reader_Housing     (Mesh, Slot 0 - 56 x 116 x 18 mm antrasit dis kasa)
               ├── Card_Area     (Mesh, Slot 0 - 46 x 52 mm yukseltilmis RFID hedefi)
               ├── LED_Green     (Mesh, Slot 1 M_Emission - Ø5.6 mm durum LED'i)
               └── LED_Red       (Mesh, Slot 1 M_Emission - Ø5.6 mm erisim LED'i)
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Access_Card_Reader_Rugged"
TRIS_BUDGET = 340

# Boyutlar (metre)
BP_W, BP_H, BP_D = 0.0600, 0.1200, 0.0040     # Backplate: 60 x 120 x 4 mm
BP_C = 0.0040

H_W, H_H = 0.0560, 0.1160                     # Housing: 56 x 116 mm
H_FRONT_Y = 0.0220                            # On yuz Y konumu (22 mm derinlik)
H_C = 0.0045

CARD_W, CARD_H = 0.0460, 0.0520               # Kart alani: 46 x 52 mm
CARD_Z = -0.0060
CARD_PROUD = 0.0003                           # 0.30 mm cikinti (SOP kurali)
CARD_C = 0.0030

LED_R = 0.0028                                # Ø5.6 mm
LED_Z = 0.0380
LED_X = 0.0130
LED_SEG = 8

ATLAS_W, ATLAS_H = 2048, 2048
UV_RECT_HOUSING = (32, 32, 1032, 2016)
UV_RECT_CARD = (1100, 32, 1700, 712)

PIX_BODY_DARK = (1250, 950)
PIX_BUMPER = (1500, 950)
PIX_METAL = (1250, 1250)


def pix_to_uv(px, py):
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_BODY_DARK)
FLAT_UV_BUMPER = pix_to_uv(*PIX_BUMPER)
FLAT_UV_METAL = pix_to_uv(*PIX_METAL)


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
    """8 noktali pahlanmis dikdortgen profili."""
    return [
        (-hx + c, -hz), (hx - c, -hz), (hx, -hz + c), (hx, hz - c),
        (hx - c, hz), (-hx + c, hz), (-hx, hz - c), (-hx, -hz + c),
    ]


def setup_materials():
    """Slot 0 -> M_Security_Atlas, Slot 1 -> M_Emission, Slot 2 -> M_Metal."""
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
    b_a.inputs["Roughness"].default_value = 0.40
    b_a.inputs["Metallic"].default_value = 0.10
    mat_atlas.diffuse_color = (0.20, 0.24, 0.28, 1.0)

    # Slot 1: M_Emission
    mat_em = bpy.data.materials.new("M_Emission")
    mat_em.use_nodes = True
    n_e = mat_em.node_tree.nodes
    b_e = n_e.get("Principled BSDF")
    for key in ("Emission Color", "Emission"):
        if key in b_e.inputs:
            b_e.inputs[key].default_value = (0.15, 0.90, 0.35, 1.0)
            break
    if "Emission Strength" in b_e.inputs:
        b_e.inputs["Emission Strength"].default_value = 6.0
    mat_em.diffuse_color = (0.15, 0.90, 0.35, 1.0)

    # Slot 2: M_Metal
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    n_m = mat_metal.node_tree.nodes
    b_m = n_m.get("Principled BSDF")
    b_m.inputs["Roughness"].default_value = 0.20
    b_m.inputs["Metallic"].default_value = 0.90
    mat_metal.diffuse_color = (0.85, 0.88, 0.92, 1.0)

    return [mat_atlas, mat_em, mat_metal]


def build_backplate(mats):
    """Duvar montaj plakasi: 60 x 120 x 4 mm."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx, hz = BP_W / 2.0, BP_H / 2.0
    prof = chamfer_profile(hx, hz, BP_C)

    rings = [[bm.verts.new(Vector((p[0], yy, p[1]))) for p in prof]
             for yy in (0.0, BP_D)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BUMPER)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 0
    set_flat_uv(f_front, uv_layer, FLAT_UV_BUMPER)

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BUMPER)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Backplate", mats)


def build_housing(mats):
    """Dayanikli on kasa: 56 x 116 x 18 mm (pahli kademeli siluet)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx_base, hz_base = H_W / 2.0, H_H / 2.0
    hx_face, hz_face = (H_W - 0.003) / 2.0, (H_H - 0.003) / 2.0

    prof_base = chamfer_profile(hx_base, hz_base, H_C)
    prof_face = chamfer_profile(hx_face, hz_face, H_C - 0.001)

    rings = [
        [bm.verts.new(Vector((p[0], BP_D, p[1]))) for p in prof_base],
        [bm.verts.new(Vector((p[0], H_FRONT_Y, p[1]))) for p in prof_face],
    ]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_HOUSING),
                     flip_u=True, extent=(-hx_face, hx_face, -hz_face, hz_face))

    n = len(prof_base)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BUMPER)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Reader_Housing", mats)


def build_card_area(mats):
    """Yukseltilmis RFID kart alani: 46 x 52 mm, 0.30 mm cikinti."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    hx, hz = CARD_W / 2.0, CARD_H / 2.0
    prof = chamfer_profile(hx, hz, CARD_C)

    y_base = H_FRONT_Y - 0.0010
    y_top = H_FRONT_Y + CARD_PROUD

    rings = [[bm.verts.new(Vector((p[0], yy, CARD_Z + p[1]))) for p in prof]
             for yy in (y_base, y_top)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_CARD),
                     flip_u=True, extent=(-hx, hx, CARD_Z - hz, CARD_Z + hz))

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BUMPER)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Card_Area", mats)


def build_led(name, cx, cz, mats, is_green=True):
    """Durum gosterge LED lensi (Ø5.6 mm, 0.30 mm cikinti)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    y_base = H_FRONT_Y - 0.0008
    y_top = H_FRONT_Y + CARD_PROUD

    rings = []
    for yy, rr in ((y_base, LED_R), (y_top, LED_R * 0.85)):
        ring = []
        for i in range(LED_SEG):
            ang = i * (2.0 * math.pi / LED_SEG)
            ring.append(bm.verts.new(Vector((cx + math.cos(ang) * rr, yy,
                                             cz + math.sin(ang) * rr))))
        rings.append(ring)

    f_base = bm.faces.new(list(reversed(rings[0])))
    f_base.smooth = False
    f_base.material_index = 1
    set_flat_uv(f_base, uv_layer, FLAT_UV_DARK if 'FLAT_UV_DARK' in globals() else FLAT_UV_BODY)

    f_top = bm.faces.new(rings[1])
    f_top.smooth = False
    f_top.material_index = 1
    set_flat_uv(f_top, uv_layer, FLAT_UV_BODY)

    for i in range(LED_SEG):
        j = (i + 1) % LED_SEG
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = True
        f.material_index = 1
        set_flat_uv(f, uv_layer, FLAT_UV_BODY)

    mark_sharp_edges_by_angle(bm, 35.0)
    obj = finish_mesh(bm, name, mats)

    # Kendi rengine gore emisyon ayari
    mat_copy = mats[1].copy()
    mat_copy.name = "M_Emission"
    col = (0.15, 0.95, 0.35, 1.0) if is_green else (0.95, 0.18, 0.15, 1.0)
    b_e = mat_copy.node_tree.nodes.get("Principled BSDF")
    for key in ("Emission Color", "Emission"):
        if key in b_e.inputs:
            b_e.inputs[key].default_value = col
            break
    mat_copy.diffuse_color = col
    obj.data.materials[1] = mat_copy

    return obj


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

    backplate = build_backplate(mats)
    parent_keep(backplate, root)

    housing = build_housing(mats)
    parent_keep(housing, backplate)

    card_area = build_card_area(mats)
    parent_keep(card_area, housing)

    led_green = build_led("LED_Green", -LED_X, LED_Z, mats, is_green=True)
    parent_keep(led_green, housing)

    led_red = build_led("LED_Red", LED_X, LED_Z, mats, is_green=False)
    parent_keep(led_red, housing)

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


def main():
    clean_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    mats = setup_materials()
    root = build_all(mats)

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
    bpy.ops.export_scene.fbx(**fbx_kwargs)
    print(f"[OK] Exported FBX: {fbx_path}")

    # Re-import QA
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 44) ---")
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

    # Hierarchy
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    assert objs["Backplate"].parent == re_root, "FAIL: Backplate must be child of Root"
    assert objs["Reader_Housing"].parent == objs["Backplate"], "FAIL: Housing must be child of Backplate"
    assert objs["Card_Area"].parent == objs["Reader_Housing"], "FAIL: Card_Area must be child of Housing"
    assert objs["LED_Green"].parent == objs["Reader_Housing"], "FAIL: LED_Green must be child of Housing"
    assert objs["LED_Red"].parent == objs["Reader_Housing"], "FAIL: LED_Red must be child of Housing"
    print("[PASS] Parent-child hierarchy verified (5 meshes)!")

    # Materials
    expected_mats = ["M_Security_Atlas", "M_Emission", "M_Metal"]
    for name in ("Backplate", "Reader_Housing", "Card_Area", "LED_Green", "LED_Red"):
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:3] == expected_mats, f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0 Atlas, Slot 1 Emission, Slot 2 Metal)!")

    # Contact QA
    contact_pairs = [
        ("Reader_Housing", "Backplate"),
        ("Card_Area", "Reader_Housing"),
        ("LED_Green", "Reader_Housing"),
        ("LED_Red", "Reader_Housing"),
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
        "moving_pivots": [],
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
