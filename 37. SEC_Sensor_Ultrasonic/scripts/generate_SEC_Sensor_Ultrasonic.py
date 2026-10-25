"""
=============================================================================
Security CCTV Asset Production Suite - Asset 37
Asset Name: SEC_Sensor_Ultrasonic  (Ultrasonik Hareket Sensoru)
Triangle Budget: <= 260 tris      (hedef: 176 tris)
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Emission

ASSET (Master Prompt 37):
    - Duvara monte ultrasonik hareket sensoru: kademeli kasa, iki dairesel
      transducer acikligi (TX / RX), on cerceve ve durum LED gostergesi.

Hierarchy (Master Prompt):
    SEC_Sensor_Ultrasonic (Root Empty @ 0,0,0)
     └── Housing            (Mesh - pahli duvar kasasi 58 x 43 x 30 mm, on yuz 50 x 35 mm)
          ├── Transducer_Left  (Mesh - sol piezo transducer puck, 8 kenar)
          ├── Transducer_Right (Mesh - sag piezo transducer puck, 8 kenar)
          └── Status_LED       (Mesh, Slot 1 M_Emission - gomme durum lensi)
    Sabit pivot (hareketli parca yok) -> yalnizca Root Empty.

Calistirma:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python scripts/generate_SEC_Sensor_Ultrasonic.py
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Sensor_Ultrasonic"
TRIS_BUDGET = 260

# ---------------------------------------------------------------- Geometri (m)
# Kademeli kasa: duvar plakasi -> govde -> on cerceve dudagi -> on yuz
H_BACK_HX, H_BACK_HZ, H_BACK_C = 0.0290, 0.0215, 0.0045
H_MID_HX, H_MID_HZ, H_MID_C = 0.0275, 0.0200, 0.0040
H_LIP_HX, H_LIP_HZ, H_LIP_C = 0.0262, 0.0188, 0.0038
H_FACE_HX, H_FACE_HZ, H_FACE_C = 0.0250, 0.0175, 0.0035

H_Y_BACK, H_Y_MID, H_Y_LIP, H_Y_FACE = 0.0, 0.0160, 0.0268, 0.0300

# On yuz = etiket bandi: 50.0 x 35.0 mm
COVER_HALF_X, COVER_HALF_Z = H_FACE_HX, H_FACE_HZ

TRANSDUCER_X, TRANSDUCER_Z, TRANSDUCER_R = 0.0128, 0.0075, 0.0076
TRANSDUCER_TOP_Y = 0.0342
LED_X, LED_Z, LED_R = 0.0, 0.0075, 0.0026
LED_TOP_Y = 0.0303
EMBED = 0.0002          # on yuze gomme miktari (bosluk birakmaz)

# ---------------------------------------------------------------- Doku atlasi
ATLAS_W, ATLAS_H = 2048, 2048
# generate_textures.py ile bire bir ayni piksel dikdortgenleri (2048x2048)
UV_RECT_COVER = (32, 32, 1982, 1397)          # 1950 x 1365 px -> 50 x 35 mm
UV_RECT_TRANSDUCER = (32, 1430, 332, 1730)    # 300 x 300 px -> piezo membran
UV_RECT_LED = (360, 1430, 560, 1630)          # 200 x 200 px -> LED lensi
PIX_FLAT_BODY = (770, 1600)                   # duz govde rengi
PIX_FLAT_SIDE = (1120, 1600)                  # pah / yan yuzey ara tonu
PIX_FLAT_DARK = (1470, 1600)                  # koyu slate (transducer govdesi)


def pix_to_uv(px, py):
    """Atlas piksel koordinatini Blender UV noktasina cevirir."""
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_FLAT_BODY)
FLAT_UV_SIDE = pix_to_uv(*PIX_FLAT_SIDE)
FLAT_UV_DARK = pix_to_uv(*PIX_FLAT_DARK)


def uv_rect_from_pixels(x0, y0, x1, y1):
    """Piksel dikdortgenini (u0, v0, u1, v1) araligina cevirir."""
    return (x0 / ATLAS_W, 1.0 - (y1 / ATLAS_H), x1 / ATLAS_W, 1.0 - (y0 / ATLAS_H))


def set_face_uv_rect(face, uv_layer, rect, flip_u=False, extent=None):
    """
    Yuzey noktalarini verilen UV dikdortgenine oransal olarak haritalar.
    extent: (minx, maxx, minz, maxz) gercek yuz sinirlari. Pah kirpilmis
    koselerde sinir kutusu kullanmak dokuyu sikistirir; extent bunu onler.
    """
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
    """Tek renk doku noktasina haritalar (govde yanlari, arka yuzler)."""
    uv = point if point else FLAT_UV_BODY
    for loop in face.loops:
        loop[uv_layer].uv = uv


def mark_sharp_edges_by_angle(bm, threshold_deg=35.0):
    """35 derece uzerindeki kirilma kenarlarini sert isaretler."""
    threshold = math.radians(threshold_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            edge.smooth = edge.calc_face_angle(0.0) < threshold


def finish_mesh(bm, name, mats):
    """BMesh'i mesh datablokuna cevirip sahneye baglar."""
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
    """Slot 0: M_Security_Atlas (doku atlasi), Slot 1: M_Emission (Asset 34 dili)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    tex_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes = mat_atlas.node_tree.nodes
    links = mat_atlas.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if os.path.exists(tex_path):
        tex = nodes.new("ShaderNodeTexImage")
        img = bpy.data.images.load(tex_path)
        try:
            img.pack()
        except Exception:
            pass
        tex.image = img
        tex.image.colorspace_settings.name = 'sRGB'
        tex.interpolation = 'Linear'
        tex.location = (-420, 220)
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.34
    bsdf.inputs["Metallic"].default_value = 0.08
    mat_atlas.diffuse_color = (0.86, 0.88, 0.92, 1.0)

    # Slot 1: M_Emission - gosterge lensi. Doku da baglanir: Workbench
    # (color_type='TEXTURE') render'inda lens yesil okunur, EEVEE'de isik verir.
    mat_emission = bpy.data.materials.new("M_Emission")
    mat_emission.use_nodes = True
    nodes_em = mat_emission.node_tree.nodes
    links_em = mat_emission.node_tree.links
    bsdf_em = nodes_em.get("Principled BSDF")
    em_col = (0.14, 0.90, 0.42, 1.0)
    if os.path.exists(tex_path):
        tex_em = nodes_em.new("ShaderNodeTexImage")
        tex_em.image = bpy.data.images.load(tex_path)
        try:
            tex_em.image.pack()
        except Exception:
            pass
        tex_em.image.colorspace_settings.name = 'sRGB'
        tex_em.location = (-420, -120)
        links_em.new(tex_em.outputs["Color"], bsdf_em.inputs["Base Color"])
        if "Emission Color" in bsdf_em.inputs:
            links_em.new(tex_em.outputs["Color"], bsdf_em.inputs["Emission Color"])
        elif "Emission" in bsdf_em.inputs:
            links_em.new(tex_em.outputs["Color"], bsdf_em.inputs["Emission"])
    if "Emission Color" in bsdf_em.inputs:
        bsdf_em.inputs["Emission Color"].default_value = em_col
    elif "Emission" in bsdf_em.inputs:
        bsdf_em.inputs["Emission"].default_value = em_col
    if "Emission Strength" in bsdf_em.inputs:
        bsdf_em.inputs["Emission Strength"].default_value = 6.0
    bsdf_em.inputs["Roughness"].default_value = 0.18
    mat_emission.diffuse_color = em_col

    return [mat_atlas, mat_emission]


def build_stepped_bar(name, profiles, mats, front_rect=None, front_extent=None,
                      front_mat=0):
    """
    Ardisik pahlanmis profiller arasinda kademeli govde uretir.
    profiles: [(profile_points, y), ...] arkadan one dogru.
    On yuz (+Y) front_rect ile kaplanir (flip_u=True), yan/pah yuzeyleri
    FLAT_UV_SIDE tonuna, arka yuz FLAT_UV_BODY tonuna haritalanir.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    rings = []
    for pts, y in profiles:
        rings.append([bm.verts.new(Vector((p[0], y, p[1]))) for p in pts])

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[-1])
    f_front.smooth = False
    f_front.material_index = front_mat
    if front_rect:
        set_face_uv_rect(f_front, uv_layer, front_rect, flip_u=True,
                         extent=front_extent)
    else:
        set_flat_uv(f_front, uv_layer, FLAT_UV_BODY)

    n = len(rings[0])
    for r in range(len(rings) - 1):
        a_ring, b_ring = rings[r], rings[r + 1]
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = 0
            set_flat_uv(f, uv_layer, FLAT_UV_SIDE)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, name, mats)


def build_cylinder(name, rings, segments, axis, mats, mat_index=0, uv_rect=None,
                   side_flat_uv=None, phase=0.0):
    """
    Kapali silindir / koni uretir (transducer puck, LED lensi).
    rings: [(merkez_x, merkez_y, merkez_z, rx, rz)] arkadan one dogru.
    axis : 'Y', 'X' veya 'Z'
    side_flat_uv: yan yuzeylerin duz UV noktasi
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    loop_rings = []
    for (cx, cy, cz, rx, rz) in rings:
        ring = []
        for i in range(segments):
            ang = phase + i * (2.0 * math.pi / segments)
            ca, sa = math.cos(ang), math.sin(ang)
            if axis == 'Y':
                co = Vector((cx + ca * rx, cy, cz + sa * rz))
            elif axis == 'X':
                co = Vector((cx, cy + ca * rx, cz + sa * rz))
            else:  # 'Z'
                co = Vector((cx + ca * rx, cy + sa * rz, cz))
            ring.append(bm.verts.new(co))
        loop_rings.append(ring)

    for r in range(len(loop_rings) - 1):
        a_ring, b_ring = loop_rings[r], loop_rings[r + 1]
        for i in range(segments):
            j = (i + 1) % segments
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = mat_index
            set_flat_uv(f, uv_layer, side_flat_uv if side_flat_uv else FLAT_UV_SIDE)

    for ring, rev in ((loop_rings[0], True), (loop_rings[-1], False)):
        f = bm.faces.new(list(reversed(ring)) if rev else ring)
        f.smooth = False
        f.material_index = mat_index
        if uv_rect:
            set_face_uv_rect(f, uv_layer, uv_rect, flip_u=True)
        else:
            set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, name, mats)


def world_aabb(obj):
    """Objenin dunya uzayindaki eksen hizali sinir kutusu (min/max)."""
    pts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return (
        Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))),
    )


def parts_in_contact(a_obj, b_obj, tol=0.0002):
    """Iki parcanin her eksende temas ettigini (veya bindigini) dogrular."""
    a_min, a_max = world_aabb(a_obj)
    b_min, b_max = world_aabb(b_obj)
    for i in range(3):
        gap = max(a_min[i], b_min[i]) - min(a_max[i], b_max[i])
        if gap > tol:
            return False
    return True


def aa_ratio(pixels, size_mm):
    """Piksel dikdortgeni orani ile metre yuzey orani karsilastirmasi."""
    x0, y0, x1, y1 = pixels
    px_ratio = (x1 - x0) / float(y1 - y0)
    mm_ratio = size_mm[0] / float(size_mm[1])
    return px_ratio / mm_ratio


def build_all(mats):
    """Tum parcalari kurar ve hiyerarsiyi gercek parent baglantilariyla olusturur."""
    rect_cover = uv_rect_from_pixels(*UV_RECT_COVER)
    rect_transducer = uv_rect_from_pixels(*UV_RECT_TRANSDUCER)
    rect_led = uv_rect_from_pixels(*UV_RECT_LED)

    # ------------------------------------------------------------ Root Empty
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    # ------------------------------------------------------------ Kademeli kasa
    # Duvar plakasi -> govde -> on cerceve dudagi -> on yuz (etiket yuzeyi)
    housing = build_stepped_bar(
        "Housing",
        [
            (chamfer_profile(H_BACK_HX, H_BACK_HZ, H_BACK_C), H_Y_BACK),
            (chamfer_profile(H_MID_HX, H_MID_HZ, H_MID_C), H_Y_MID),
            (chamfer_profile(H_LIP_HX, H_LIP_HZ, H_LIP_C), H_Y_LIP),
            (chamfer_profile(H_FACE_HX, H_FACE_HZ, H_FACE_C), H_Y_FACE),
        ],
        mats,
        front_rect=rect_cover,
        front_extent=(-H_FACE_HX, H_FACE_HX, -H_FACE_HZ, H_FACE_HZ),
    )
    housing.parent = root

    # ------------------------------------------------------------ Transducer puck'lari
    # 8 kenar; on yuzde 0.2 mm gomulu (bosluk yok), ust yuzde piezo membran dokusu.
    # Dunya +X izleyicinin soludur -> Transducer_Left = -X (Asset 36 civata dili).
    for name, sx in (("Transducer_Left", -TRANSDUCER_X),
                     ("Transducer_Right", TRANSDUCER_X)):
        puck = build_cylinder(
            name,
            [(0.0, 0.0, 0.0, TRANSDUCER_R, TRANSDUCER_R),
             (0.0, 0.0028, 0.0, TRANSDUCER_R * 0.96, TRANSDUCER_R * 0.96),
             (0.0, TRANSDUCER_TOP_Y - (H_Y_FACE - EMBED), 0.0,
              TRANSDUCER_R * 0.80, TRANSDUCER_R * 0.80)],
            8, 'Y', mats, mat_index=0,
            uv_rect=rect_transducer, side_flat_uv=FLAT_UV_DARK,
            phase=math.pi / 8.0,
        )
        puck.location = Vector((sx, H_Y_FACE - EMBED, TRANSDUCER_Z))
        puck.parent = housing

    # ------------------------------------------------------------ Durum LED lensi
    led = build_cylinder(
        "Status_LED",
        [(0.0, 0.0, 0.0, LED_R, LED_R),
         (0.0, LED_TOP_Y - (H_Y_FACE - EMBED), 0.0, LED_R * 0.92, LED_R * 0.92)],
        8, 'Y', mats, mat_index=1,
        uv_rect=rect_led, side_flat_uv=FLAT_UV_DARK,
        phase=math.pi / 8.0,
    )
    led.location = Vector((LED_X, H_Y_FACE - EMBED, LED_Z))
    led.parent = housing

    bpy.context.view_layer.update()
    return root


def clean_scene():
    """Sahneyi bosaltir ve metrik birimleri ayarlar."""
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

    # --------------------------------------------------------------- Transform hijyeni
    bpy.context.view_layer.update()
    for obj in bpy.data.objects:
        obj.scale = (1.0, 1.0, 1.0)
        if obj.type == 'EMPTY':
            obj.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()

    boxes = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            boxes.append(world_aabb(obj))
    gmin = Vector((min(b[0].x for b in boxes), min(b[0].y for b in boxes),
                   min(b[0].z for b in boxes)))
    gmax = Vector((max(b[1].x for b in boxes), max(b[1].y for b in boxes),
                   max(b[1].z for b in boxes)))
    print(f"[INFO] Overall size: {(gmax.x - gmin.x) * 1000:.1f} x "
          f"{(gmax.y - gmin.y) * 1000:.1f} x {(gmax.z - gmin.z) * 1000:.1f} mm")

    # --------------------------------------------------------------- Kaydet + FBX
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

    bpy.ops.export_scene.fbx(
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
    print(f"[OK] Exported FBX: {fbx_path}")

    # --------------------------------------------------------------- Re-Import QA
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 37) ---")
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
    assert total_tris <= TRIS_BUDGET, \
        f"FAIL: Total triangles {total_tris} exceeds {TRIS_BUDGET} budget!"
    print(f"[PASS] Triangle count verified strictly (<= {TRIS_BUDGET})!")
    assert not uv_missing, f"FAIL: Missing/empty UV layer on: {uv_missing}"
    print("[PASS] UV layers present on all meshes!")
    assert empty_names == [ASSET_NAME], \
        f"FAIL: Fixed-pivot asset must contain exactly one empty, found {empty_names}"
    print("[PASS] Single root empty (no moving pivots) verified!")

    # --------------------------------------------------------------- Hiyerarsi
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    expected_parents = {
        "Housing": ASSET_NAME,
        "Transducer_Left": "Housing",
        "Transducer_Right": "Housing",
        "Status_LED": "Housing",
    }
    for child_name, parent_name in expected_parents.items():
        child = objs.get(child_name)
        assert child is not None, f"FAIL: {child_name} missing in FBX hierarchy"
        assert child.parent is not None and child.parent.name == parent_name, \
            f"FAIL: {child_name} parent mismatch (expected {parent_name})"
    print(f"[PASS] Full parent-child hierarchy verified ({len(expected_parents)} relations)!")

    # --------------------------------------------------------------- Materyal slotlari
    expected_mats = ["M_Security_Atlas", "M_Emission"]
    for name in ("Housing", "Transducer_Left", "Transducer_Right", "Status_LED"):
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:2] == expected_mats, \
            f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0: M_Security_Atlas, Slot 1: M_Emission)!")

    # --------------------------------------------------------------- Emisyon QA
    # Emisyon yalnizca gosterge lensinde kullanilmali (Master Prompt kurali).
    for name in ("Housing", "Transducer_Left", "Transducer_Right"):
        idxs = {p.material_index for p in objs[name].data.polygons}
        assert 1 not in idxs, f"FAIL: Emission material used on non-indicator part {name}"
    led_polys = objs["Status_LED"].data.polygons
    led_emissive = [p for p in led_polys if p.material_index == 1]
    assert len(led_emissive) == len(led_polys) and led_emissive, \
        "FAIL: Status_LED is not fully assigned to M_Emission"
    em_mat = bpy.data.materials.get("M_Emission")
    strength = None
    for node in em_mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            key = "Emission Strength" if "Emission Strength" in node.inputs else None
            strength = node.inputs[key].default_value if key else None
    assert strength is not None and strength >= 1.0, \
        f"FAIL: M_Emission strength too low ({strength})"
    print(f"[PASS] Emission confined to Status_LED ({len(led_polys)} faces, "
          f"strength {strength:.1f})!")

    # --------------------------------------------------------------- Bosluk / temas QA
    contact_pairs = [
        ("Transducer_Left", "Housing"),
        ("Transducer_Right", "Housing"),
        ("Status_LED", "Housing"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), \
            f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} contact pairs)!")

    wall_y = world_aabb(objs["Housing"])[0].y * 1000.0
    print(f"[QA] Duvar yuzeyi offseti: {wall_y:.2f} mm (0.00 olmali)")
    assert abs(wall_y) < 0.05, "FAIL: Housing does not sit on the wall plane"

    face = world_aabb(objs["Housing"])
    os_x = (face[1].x - face[0].x) * 1000.0
    os_z = (face[1].z - face[0].z) * 1000.0
    os_y = (face[1].y - face[0].y) * 1000.0
    print(f"[QA] Kasa dis olcusu: {os_x:.1f} x {os_y:.1f} x {os_z:.1f} mm (G x D x Y)")
    assert abs(os_x - 58.0) < 0.3 and abs(os_z - 43.0) < 0.3 and abs(os_y - 30.0) < 0.3, \
        "FAIL: Housing outer size does not match 58 x 43 x 30 mm"

    # On yuz, on cerceve dudaginin 50 x 35 mm olculu duz alanidir.
    front_polys = [p for p in objs["Housing"].data.polygons if p.normal.y > 0.9]
    front_poly = max(front_polys, key=lambda p: p.area)
    fx = [objs["Housing"].matrix_world @ objs["Housing"].data.vertices[v].co
          for v in front_poly.vertices]
    fx_w = (max(v.x for v in fx) - min(v.x for v in fx)) * 1000.0
    fx_h = (max(v.z for v in fx) - min(v.z for v in fx)) * 1000.0
    print(f"[QA] Etiket yuzeyi: {fx_w:.1f} x {fx_h:.1f} mm")
    assert abs(fx_w - 50.0) < 0.3 and abs(fx_h - 35.0) < 0.3, \
        "FAIL: Cover face size does not match the 50 x 35 mm texture band"

    # --------------------------------------------------------------- Simetri QA
    l_min, l_max = world_aabb(objs["Transducer_Left"])
    r_min, r_max = world_aabb(objs["Transducer_Right"])
    dx = abs(abs(l_min.x) - abs(r_max.x)) * 1000.0
    dz = abs((0.5 * (l_min.z + l_max.z)) - (0.5 * (r_min.z + r_max.z))) * 1000.0
    dd = abs((l_max.y - l_min.y) - (r_max.y - r_min.y)) * 1000.0
    print(f"[QA] Transducer simetrisi: dx={dx:.2f} mm, dz={dz:.2f} mm, derinlik farki={dd:.2f} mm")
    assert dx < 0.05 and dz < 0.05 and dd < 0.05, \
        "FAIL: Transducer pair is not mirror-symmetric"
    print("[PASS] Mirrored transducer pair verified!")

    # --------------------------------------------------------------- UV oran QA
    ratios = [
        ("Cover front", UV_RECT_COVER, (50.0, 35.0)),
        ("Transducer membrane", UV_RECT_TRANSDUCER, (15.2, 15.2)),
        ("LED lens", UV_RECT_LED, (5.2, 5.2)),
    ]
    for label, rect, size_mm in ratios:
        err = abs(aa_ratio(rect, size_mm) - 1.0) * 100.0
        print(f"[QA] UV aspect {label:20s}: {size_mm[0]:.1f} x {size_mm[1]:.1f} mm -> sapma {err:.2f}%")
        assert err < 1.0, f"FAIL: UV stretch {err:.2f}% on {label}"
    print(f"[QA] Etiket doku yogunlugu: {(UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 50.0:.1f} px/mm")
    print("[PASS] UV rectangles locked to face aspect ratios (no texture sliding)!")

    # ------------------------------------------- Doku yogunlugu (gercek, pah kirpilmis yuz)
    # set_face_uv_rect yuzun sinir kutusunu kullanirsa pah kirpilmis koseler
    # dokuyu sikistirir. Bu olcum bunu yakalar: u ve v yogunlugu esit olmali
    # ve bant tasarim yogunluguna esit cikmali.
    cov = objs["Housing"]
    cme, cuv = cov.data, cov.data.uv_layers[0]
    mw = cov.matrix_world
    samples = []
    for li in front_poly.loop_indices:
        co = mw @ cme.vertices[cme.loops[li].vertex_index].co
        uv = cuv.data[li].uv
        samples.append((co.x, co.z, uv.x, uv.y))
    xa = max(samples, key=lambda s: s[0])
    xb = min(samples, key=lambda s: s[0])
    slope_u = (xa[2] - xb[2]) / (xa[0] - xb[0])
    u_edge = xa[2] + slope_u * (COVER_HALF_X - xa[0])
    dx_span = max(s[0] for s in samples) - min(s[0] for s in samples)
    dz_span = max(s[1] for s in samples) - min(s[1] for s in samples)
    du_span = max(s[2] for s in samples) - min(s[2] for s in samples)
    dv_span = max(s[3] for s in samples) - min(s[3] for s in samples)
    dens_u = du_span * ATLAS_W / (dx_span * 1000.0)
    dens_v = dv_span * ATLAS_W / (dz_span * 1000.0)
    design = (UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 50.0
    print(f"[QA] Kapak doku yogunlugu: u={dens_u:.2f} px/mm, v={dens_v:.2f} px/mm "
          f"(tasarim {design:.2f})")
    assert abs(dens_u / dens_v - 1.0) < 0.02, \
        f"FAIL: Cover texture squeezed (u/v density {dens_u:.2f} vs {dens_v:.2f})"
    assert abs(dens_u / design - 1.0) < 0.03, \
        f"FAIL: Cover texture scale off design ({dens_u:.2f} vs {design:.2f} px/mm)"
    px_at_cover_edge = u_edge * ATLAS_W
    print(f"[QA] Kapak sol kenari (X=+{COVER_HALF_X*1000:.1f} mm) atlas px: "
          f"{px_at_cover_edge:.1f} (beklenen {UV_RECT_COVER[0]:.1f})")
    assert abs(px_at_cover_edge - UV_RECT_COVER[0]) < 2.0, \
        "FAIL: Cover label is not aligned to the texture band edge (text offset)"
    print("[PASS] Cover label mapped 1:1 (density + alignment verified)!")

    # --------------------------------------------------------------- Topoloji sagligi
    loose, non_manifold = 0, 0
    for name in mesh_names:
        bm = bmesh.new()
        bm.from_mesh(objs[name].data)
        for v in bm.verts:
            if not v.link_faces:
                loose += 1
        for e in bm.edges:
            if len(e.link_faces) != 2:
                non_manifold += 1
        bm.free()
    print(f"[QA] Topoloji: loose vertex = {loose}, non-manifold edge = {non_manifold}")
    assert loose == 0 and non_manifold == 0, "FAIL: Topology health check failed"
    print("[PASS] Manifold topology verified (0 loose verts, 0 non-manifold edges)!")

    # --------------------------------------------------------------- Manifest
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
        "status": "SUCCESS",
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[OK] Updated manifest: {manifest_path}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")

    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[CLEAN] Removed backup: {blend1_path}")


if __name__ == "__main__":
    main()







