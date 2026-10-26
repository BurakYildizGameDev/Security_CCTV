"""
=============================================================================
Security CCTV Asset Production Suite - Asset 42
Asset Name: SEC_Access_Exit_Button (Kapi Cikis Butonu)
Triangle Budget: <= 180 tris      (hedef: 172 tris)
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Metal , Slot 2 -> M_Emission

ASSET (Master Prompt 42):
    - Duvar plakasi, genis basmali dugme, ince cerceve ve iki vida basi.

Hierarchy (Master Prompt):
    SEC_Access_Exit_Button (Root Empty @ 0,0,0)
     ├── Backplate        (Mesh, Slot 0 - 86 x 86 x 6 mm pahli duvar plakasi)
     │    └── Frame_Ring  (Mesh, Slot 1 M_Metal - Ø49.2 mm ince 3D cerceve)
     ├── Screw_L          (Mesh, Slot 1 M_Metal - 6 kenar vida basi, -X)  [root child]
     ├── Screw_R          (Mesh, Slot 1 M_Metal - 6 kenar vida basi, +X)  [root child]
     └── Button_Pivot     (Empty @ panel yuzeyi; yerel Y 4 mm basma)
          └── Push_Button (Mesh, Slot 0 govde + Slot 2 Emission ust yuz - Ø44)

SARTNAME NOTU: "Screws root child'lari" dendigi icin vidalar Backplate'e DEGIL,
dogrudan root'a baglanir. Cerceve hiyerarside sayilmadigi icin plaka grubunun
(Backplate) altina alindi.

BASMA MEKANIZMASI: LIMIT_LOCATION (owner_space LOCAL). LIMIT_LOCATION mutlak
yerel konumu kirptigi icin limitler DINLENME konumu etrafinda tanimlanir
(varlik 41 dersi): min_y = D - 0.004, max_y = D.

PARALAKS: dugme +4.2 mm kabarik oldugu icin cerceve tepesi de AYNI duzlemde
(+4.2 mm) modellendi; egik bakista ikisi birlikte kayar, "kayma" gorunmez.

Calistirma:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python scripts/generate_SEC_Access_Exit_Button.py
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Access_Exit_Button"
TRIS_BUDGET = 180
PRESS_TRAVEL = 0.004            # 4 mm basma stroku (sartname)

# ---------------------------------------------------------------- Geometri (m)
D = 0.0060                      # plaka derinligi
BP_HX, BP_HZ, BP_C = 0.0430, 0.0430, 0.0050     # 86 x 86 mm, 5 mm pah

# Genis basmali dugme (Ø44)
BTN_R, BTN_TOP_R, BTN_SKIRT_R = 0.0220, 0.0212, 0.0217
BTN_PROUD = 0.0042              # on yuzden cikinti = strok + 0.2 mm
BTN_SKIRT = 0.0030              # plaka icine giren etek
BTN_SEG = 10

# Ince cerceve (Frame_Ring): ucgen kesitli kapali halka (8 kenar)
FR_R_IN, FR_R_CREST, FR_R_OUT = 0.0224, 0.0234, 0.0246
FR_Y_BASE, FR_Y_CREST = D + 0.0002, D + BTN_PROUD
FR_SEG = 10

# Iki vida basi (root child)
SCREW_X, SCREW_R, SCREW_H = 0.0320, 0.0040, 0.0024
SCREW_SEG = 6

# ---------------------------------------------------------------- Doku atlasi
ATLAS_W, ATLAS_H = 2048, 2048
UV_RECT_COVER = (32, 32, 1760, 1760)         # 1728 x 1728 px -> 86 x 86 mm
UV_RECT_BUTTON = (1790, 32, 2016, 258)       # 226 x 226 px -> dugme ust yuzu
PIX_FLAT_BODY = (1890, 385)
PIX_FLAT_SIDE = (1890, 580)
PIX_FLAT_DARK = (1890, 775)
PIX_FLAT_METAL = (1890, 970)


def pix_to_uv(px, py):
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_FLAT_BODY)
FLAT_UV_SIDE = pix_to_uv(*PIX_FLAT_SIDE)
FLAT_UV_DARK = pix_to_uv(*PIX_FLAT_DARK)
FLAT_UV_METAL = pix_to_uv(*PIX_FLAT_METAL)


def uv_rect_from_pixels(x0, y0, x1, y1):
    return (x0 / ATLAS_W, 1.0 - (y1 / ATLAS_H), x1 / ATLAS_W, 1.0 - (y0 / ATLAS_H))


def set_face_uv_rect(face, uv_layer, rect, flip_u=False, extent=None):
    """Yuzey noktalarini verilen UV dikdortgenine oransal olarak haritalar."""
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


def set_radial_uv(face, uv_layer, rect, cx, cz, r_out, flip_u=True):
    """Daire sekilli yuzu radyal (aslinda duzlemsel) haritalar.

    flip_u=True (varsayilan): +Y normaline bakan on yuzler icin ZORUNLUDUR.
    Kamera +Y'den -Y'ye bakarken dunya +X ekranin SOLUNA duser; U'yu +X ile
    birlikte artirmak dokuyu yatay aynalar ve uzerindeki yaziyi ters gosterir
    ("EXIT" -> "TIXE"). Bu yuzden U, set_face_uv_rect(flip_u=True) ile ayni
    sekilde ters cevrilir.
    """
    u0, v0, u1, v1 = rect
    for loop in face.loops:
        nx = (loop.vert.co.x - cx) / r_out
        nz = (loop.vert.co.z - cz) / r_out
        t = 0.5 + 0.5 * nx
        u = (u1 - t * (u1 - u0)) if flip_u else (u0 + t * (u1 - u0))
        v = v0 + (0.5 + 0.5 * nz) * (v1 - v0)
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
    """X-Z duzleminde 8 noktali pahlanmis dikdortgen profili (CCW)."""
    return [
        (-hx + c, -hz), (hx - c, -hz), (hx, -hz + c), (hx, hz - c),
        (hx - c, hz), (-hx + c, hz), (-hx, hz - c), (-hx, -hz + c),
    ]


def setup_materials():
    """Slot 0: M_Security_Atlas, Slot 1: M_Metal, Slot 2: M_Emission."""
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
        tex.location = (-420, 240)
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.34
    bsdf.inputs["Metallic"].default_value = 0.08
    mat_atlas.diffuse_color = (0.86, 0.88, 0.92, 1.0)

    # Slot 1: M_Metal (aile standardi)
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    mbsdf = mat_metal.node_tree.nodes.get("Principled BSDF")
    mbsdf.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    mbsdf.inputs["Metallic"].default_value = 0.95
    mbsdf.inputs["Roughness"].default_value = 0.22
    mat_metal.diffuse_color = (0.75, 0.78, 0.82, 1.0)

    # Slot 2: M_Emission (aydinlatmali basma yuzu)
    mat_em = bpy.data.materials.new("M_Emission")
    mat_em.use_nodes = True
    nodes_e = mat_em.node_tree.nodes
    links_e = mat_em.node_tree.links
    bsdf_e = nodes_e.get("Principled BSDF")
    em_col = (0.16, 0.90, 0.44, 1.0)
    if os.path.exists(tex_path):
        tex_e = nodes_e.new("ShaderNodeTexImage")
        tex_e.image = bpy.data.images.load(tex_path)
        try:
            tex_e.image.pack()
        except Exception:
            pass
        tex_e.image.colorspace_settings.name = 'sRGB'
        tex_e.location = (-420, -140)
        links_e.new(tex_e.outputs["Color"], bsdf_e.inputs["Base Color"])
        for key in ("Emission Color", "Emission"):
            if key in bsdf_e.inputs:
                links_e.new(tex_e.outputs["Color"], bsdf_e.inputs[key])
                break
    for key in ("Emission Color", "Emission"):
        if key in bsdf_e.inputs:
            bsdf_e.inputs[key].default_value = em_col
            break
    if "Emission Strength" in bsdf_e.inputs:
        bsdf_e.inputs["Emission Strength"].default_value = 7.0
    bsdf_e.inputs["Roughness"].default_value = 0.20
    mat_em.diffuse_color = em_col

    return [mat_atlas, mat_metal, mat_em]


def build_backplate(mats):
    """86 x 86 x 6 mm pahli duvar plakasi (8 kenar x 2 profil = 28 tris)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    back = chamfer_profile(BP_HX, BP_HZ, BP_C)
    # On profil ayni ayak izinde (86 mm) tutulur; yalnizca kose pahi biraz
    # kucultulur, boylece etiket yuzeyi doku bandiyla birebir 86 x 86 mm kalir.
    front = chamfer_profile(BP_HX, BP_HZ, BP_C - 0.0006)
    v_back = [bm.verts.new(Vector((p[0], 0.0, p[1]))) for p in back]
    v_front = [bm.verts.new(Vector((p[0], D, p[1]))) for p in front]

    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(v_front)
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_COVER),
                     flip_u=True, extent=(-BP_HX, BP_HX, -BP_HZ, BP_HZ))

    n = len(back)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((v_back[i], v_back[j], v_front[j], v_front[i]))
        f.smooth = True
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_SIDE)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Backplate", mats)


def build_frame_ring(mats):
    """Ince cerceve: ucgen kesitli kapali halka (8 kenar x 3 quad = 48 tris).

    Tepesi dugme tepesiyle AYNI duzlemde (+4.2 mm) -> paylasilan paralaks.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    prof = ((FR_R_OUT, FR_Y_BASE), (FR_R_CREST, FR_Y_CREST), (FR_R_IN, FR_Y_BASE))
    rings = []
    for (rr, yy) in prof:
        ring = []
        for i in range(FR_SEG):
            ang = i * (2.0 * math.pi / FR_SEG)
            ring.append(bm.verts.new(Vector((math.cos(ang) * rr, yy,
                                             math.sin(ang) * rr))))
        rings.append(ring)

    for r in range(3):
        a_ring, b_ring = rings[r], rings[(r + 1) % 3]
        for i in range(FR_SEG):
            j = (i + 1) % FR_SEG
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = 1
            set_flat_uv(f, uv_layer, FLAT_UV_METAL)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Frame_Ring", mats)


def build_push_button(mats):
    """Genis basmali dugme: 10 kenar x 3 halka + 2 kapak = 56 tris.

    Yerel origin dugme merkezinde (pivot ile ayni). Yerel +Y disari.
    Ust kapak aydinlatmali (Slot 2), govde/etek atlas (Slot 0).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    rings_def = ((-BTN_SKIRT, BTN_R), (BTN_PROUD, BTN_TOP_R))
    loop_rings = []
    for (yy, rr) in rings_def:
        ring = []
        for i in range(BTN_SEG):
            ang = i * (2.0 * math.pi / BTN_SEG)
            ring.append(bm.verts.new(Vector((math.cos(ang) * rr, yy,
                                             math.sin(ang) * rr))))
        loop_rings.append(ring)

    for r in range(len(loop_rings) - 1):
        a_ring, b_ring = loop_rings[r], loop_rings[r + 1]
        for i in range(BTN_SEG):
            j = (i + 1) % BTN_SEG
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = 0
            set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    f_bot = bm.faces.new(list(reversed(loop_rings[0])))
    f_bot.smooth = False
    f_bot.material_index = 0
    set_flat_uv(f_bot, uv_layer, FLAT_UV_DARK)

    f_top = bm.faces.new(loop_rings[-1])
    f_top.smooth = False
    f_top.material_index = 2
    set_radial_uv(f_top, uv_layer, uv_rect_from_pixels(*UV_RECT_BUTTON),
                  0.0, 0.0, BTN_TOP_R)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Push_Button", mats)


def build_screw(name, mats, sx):
    """6 kenarli vida basi (20 tris). Yerel origin taban merkezinde."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    loop_rings = []
    for (yy, rr) in ((0.0, SCREW_R), (SCREW_H, SCREW_R * 0.84)):
        ring = []
        for i in range(SCREW_SEG):
            ang = i * (2.0 * math.pi / SCREW_SEG)
            ring.append(bm.verts.new(Vector((math.cos(ang) * rr, yy,
                                             math.sin(ang) * rr))))
        loop_rings.append(ring)

    for i in range(SCREW_SEG):
        j = (i + 1) % SCREW_SEG
        f = bm.faces.new((loop_rings[0][i], loop_rings[0][j],
                          loop_rings[1][j], loop_rings[1][i]))
        f.smooth = True
        f.material_index = 1
        set_flat_uv(f, uv_layer, FLAT_UV_METAL)

    for ring, rev in ((loop_rings[0], True), (loop_rings[1], False)):
        f = bm.faces.new(list(reversed(ring)) if rev else ring)
        f.smooth = False
        f.material_index = 1
        set_flat_uv(f, uv_layer, FLAT_UV_METAL)

    mark_sharp_edges_by_angle(bm, 35.0)
    obj = finish_mesh(bm, name, mats)
    obj.location = Vector((sx, D - 0.0002, 0.0))
    return obj


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


def aa_ratio(pixels, size_mm):
    x0, y0, x1, y1 = pixels
    return ((x1 - x0) / float(y1 - y0)) / (size_mm[0] / float(size_mm[1]))


def build_all(mats):
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    plate = build_backplate(mats)
    plate.parent = root

    ring = build_frame_ring(mats)
    ring.parent = plate

    # Vidalar SARTNAME geregi root'un dogrudan cocugu
    for name, sx in (("Screw_L", -SCREW_X), ("Screw_R", SCREW_X)):
        sc = build_screw(name, mats, sx)
        sc.parent = root

    # ------------------------------------------------------------ Basma pivotu
    # Pivot PANEL YUZEYINDE (0, D, 0); dugme geometrisi pivot yerel uzayinda.
    pivot = bpy.data.objects.new("Button_Pivot", None)
    pivot.empty_display_type = 'ARROWS'
    pivot.empty_display_size = 0.01
    pivot.location = Vector((0.0, D, 0.0))
    bpy.context.collection.objects.link(pivot)
    bpy.context.view_layer.update()
    pivot.parent = plate
    pivot.matrix_parent_inverse.identity()

    con = pivot.constraints.new('LIMIT_LOCATION')
    con.owner_space = 'LOCAL'
    # LIMIT_LOCATION MUTLAK yerel konumu kirpar -> limitler dinlenme konumu
    # etrafinda (varlik 41 dersi), aksi halde pivot baslangica cakilir.
    con.use_min_x = con.use_max_x = True
    con.min_x = con.max_x = 0.0
    con.use_min_y = True
    con.min_y = D - PRESS_TRAVEL
    con.use_max_y = True
    con.max_y = D
    con.use_min_z = con.use_max_z = True
    con.min_z = con.max_z = 0.0
    pivot["press_min_m"] = -PRESS_TRAVEL
    pivot["press_max_m"] = 0.0
    pivot["press_axis"] = "Y"
    pivot["rest_y_m"] = D
    pivot["local_y_min"] = D - PRESS_TRAVEL
    pivot["local_y_max"] = D

    button = build_push_button(mats)
    button.parent = pivot
    button.matrix_parent_inverse.identity()
    button.location = Vector((0.0, 0.0, 0.0))

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


def qa_press(objs):
    """Basma pivotu: konum, limitler, custom property ve 4 mm strok testi."""
    pivot = objs["Button_Pivot"]
    button = objs["Push_Button"]
    plate = objs["Backplate"]
    assert pivot.type == 'EMPTY', "FAIL: Button_Pivot must be an Empty"
    pl = pivot.matrix_world.translation
    print(f"[QA] Button_Pivot konumu: ({pl.x * 1000:.2f}, {pl.y * 1000:.2f}, "
          f"{pl.z * 1000:.2f}) mm (panel yuzeyi {D * 1000:.1f} mm)")
    assert abs(pl.x) < 1e-6 and abs(pl.z) < 1e-6, \
        "FAIL: Button_Pivot is not centred on the plate"
    assert abs(pl.y - D) < 1e-6, "FAIL: Button_Pivot is not on the panel surface"

    lo, hi = pivot.get("press_min_m"), pivot.get("press_max_m")
    axis = pivot.get("press_axis")
    assert lo is not None and hi is not None and axis == "Y", \
        "FAIL: press limits missing/incorrect as custom properties"
    assert abs(lo + PRESS_TRAVEL) < 1e-6 and abs(hi) < 1e-6, \
        f"FAIL: press range wrong ({lo}..{hi})"
    print(f"[QA] Limit custom properties: press_min_m={lo}, press_max_m={hi}, axis={axis}")

    cons = [c for c in pivot.constraints if c.type == 'LIMIT_LOCATION']
    assert cons, "FAIL: Button_Pivot has no LIMIT_LOCATION constraint"
    con = cons[0]
    assert con.owner_space == 'LOCAL', "FAIL: constraint space must be LOCAL"
    assert abs(con.min_y - (D - PRESS_TRAVEL)) < 1e-6, "FAIL: LIMIT_LOCATION min_y wrong"
    assert abs(con.max_y - D) < 1e-6, "FAIL: LIMIT_LOCATION max_y wrong"
    assert abs(con.min_x) < 1e-6 and abs(con.max_x) < 1e-6, \
        "FAIL: LIMIT_LOCATION X must be pinned to the button centre"
    assert abs(con.min_z) < 1e-6 and abs(con.max_z) < 1e-6, \
        "FAIL: LIMIT_LOCATION Z must be pinned to the button centre"
    print(f"[PASS] LIMIT_LOCATION (LOCAL, Y {con.min_y*1000:.1f}..{con.max_y*1000:.1f} mm "
          f"= {(con.max_y - con.min_y)*1000:.0f} mm strok, X/Z kilitli)")

    # --- Strok testi -------------------------------------------------------
    rest_top = max((button.matrix_world @ v.co).y for v in button.data.vertices)
    proud = (rest_top - D) * 1000.0
    print(f"[QA] Dinlenme: dugme tepe Y={rest_top * 1000:.2f} mm, cikinti {proud:.2f} mm")
    assert abs(proud - BTN_PROUD * 1000.0) < 0.01, \
        f"FAIL: rest protrusion {proud:.2f} mm != {BTN_PROUD*1000:.1f} mm"

    pivot.location.y = D - PRESS_TRAVEL
    bpy.context.view_layer.update()
    pressed_top = max((button.matrix_world @ v.co).y for v in button.data.vertices)
    travel = (rest_top - pressed_top) * 1000.0
    remain = (pressed_top - D) * 1000.0
    print(f"[QA] Basili:   dugme tepe Y={pressed_top * 1000:.2f} mm -> strok {travel:.2f} mm, "
          f"kalan cikinti {remain:.2f} mm")
    assert abs(travel - PRESS_TRAVEL * 1000.0) < 1e-3, \
        f"FAIL: press travel {travel:.3f} mm != {PRESS_TRAVEL*1000:.1f} mm"
    assert remain >= 0.1, f"FAIL: button sinks {abs(remain):.2f} mm into the plate"
    pivot.location.y = D
    bpy.context.view_layer.update()
    print("[PASS] Basma stroku 4.00 mm, basili halde 0.20 mm cikinti kaliyor")


def main():
    clean_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    mats = setup_materials()
    root = build_all(mats)

    objs_src = {o.name: o for o in [root] + root.children_recursive}
    qa_press(objs_src)

    bpy.context.view_layer.update()
    for obj in bpy.data.objects:
        obj.scale = (1.0, 1.0, 1.0)
        if obj.type == 'EMPTY':
            obj.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()

    boxes = [world_aabb(o) for o in bpy.data.objects if o.type == 'MESH']
    gmin = Vector((min(b[0].x for b in boxes), min(b[0].y for b in boxes),
                   min(b[0].z for b in boxes)))
    gmax = Vector((max(b[1].x for b in boxes), max(b[1].y for b in boxes),
                   max(b[1].z for b in boxes)))
    print(f"[INFO] Overall size: {(gmax.x - gmin.x) * 1000:.1f} x "
          f"{(gmax.y - gmin.y) * 1000:.1f} x {(gmax.z - gmin.z) * 1000:.1f} mm")

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
        print("[WARN] use_custom_props desteklenmiyor, ozelliksiz aktariliyor")
        bpy.ops.export_scene.fbx(**fbx_kwargs)
    print(f"[OK] Exported FBX: {fbx_path}")

    # --------------------------------------------------------------- Re-Import QA
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 42) ---")
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
    assert sorted(empty_names) == sorted([ASSET_NAME, "Button_Pivot"]), \
        f"FAIL: expected root + Button_Pivot empties, found {empty_names}"
    print("[PASS] Exactly one moving pivot empty (Button_Pivot) verified!")

    # --------------------------------------------------------------- Hiyerarsi
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    expected_parents = {
        "Backplate": ASSET_NAME,
        "Frame_Ring": "Backplate",
        "Screw_L": ASSET_NAME,
        "Screw_R": ASSET_NAME,
        "Button_Pivot": "Backplate",
        "Push_Button": "Button_Pivot",
    }
    for child_name, parent_name in expected_parents.items():
        child = objs.get(child_name)
        assert child is not None, f"FAIL: {child_name} missing in FBX hierarchy"
        assert child.parent is not None and child.parent.name == parent_name, \
            f"FAIL: {child_name} parent mismatch (expected {parent_name})"
    print(f"[PASS] Full parent-child hierarchy verified ({len(expected_parents)} relations)!")
    print("[PASS] Screws are direct children of the root (spec requirement)!")

    # --------------------------------------------------------------- Materyal slotlari
    expected_mats = ["M_Security_Atlas", "M_Metal", "M_Emission"]
    for name in expected_parents:
        if objs[name].type != 'MESH':
            continue
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:3] == expected_mats, \
            f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0 Atlas, 1 Metal, 2 Emission)!")

    # --------------------------------------------------------------- Slot kullanimi
    assert {p.material_index for p in objs["Backplate"].data.polygons} == {0}, \
        "FAIL: Backplate must be M_Security_Atlas"
    for name in ("Frame_Ring", "Screw_L", "Screw_R"):
        idxs = {p.material_index for p in objs[name].data.polygons}
        assert idxs == {1}, f"FAIL: {name} must be M_Metal (found {idxs})"
    btn = objs["Push_Button"].data.polygons
    emis = [p for p in btn if p.material_index == 2]
    assert emis and all(p.material_index in (0, 2) for p in btn), \
        "FAIL: Push_Button must use only Atlas + Emission"
    assert len(emis) == 1, \
        f"FAIL: emission must be only the illuminated top face (found {len(emis)} faces)"
    print(f"[PASS] Emisyon yalniz dugme ust yuzunde "
          f"({len(emis)}/{len(btn)} yuz), metal yalniz cerceve+vidalarda!")

    # --------------------------------------------------------------- Bosluk / olcu QA
    contact_pairs = [
        ("Frame_Ring", "Backplate"),
        ("Screw_L", "Backplate"),
        ("Screw_R", "Backplate"),
        ("Push_Button", "Backplate"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), \
            f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} contact pairs)!")

    wall_y = world_aabb(objs["Backplate"])[0].y * 1000.0
    print(f"[QA] Duvar yuzeyi offseti: {wall_y:.2f} mm (0.00 olmali)")
    assert abs(wall_y) < 0.05, "FAIL: Backplate does not sit on the wall plane"

    bp = world_aabb(objs["Backplate"])
    bp_w = (bp[1].x - bp[0].x) * 1000.0
    bp_h = (bp[1].z - bp[0].z) * 1000.0
    bp_d = (bp[1].y - bp[0].y) * 1000.0
    print(f"[QA] Plaka: {bp_w:.1f} x {bp_d:.1f} x {bp_h:.1f} mm (G x D x Y)")
    assert abs(bp_w - 86.0) < 0.3 and abs(bp_h - 86.0) < 0.3 and abs(bp_d - 6.0) < 0.3, \
        "FAIL: Backplate must be 86 x 86 x 6 mm"

    front_polys = [p for p in objs["Backplate"].data.polygons if p.normal.y > 0.9]
    front_poly = max(front_polys, key=lambda p: p.area)
    fverts = [objs["Backplate"].matrix_world
              @ objs["Backplate"].data.vertices[v].co for v in front_poly.vertices]
    fx_w = (max(v.x for v in fverts) - min(v.x for v in fverts)) * 1000.0
    fx_h = (max(v.z for v in fverts) - min(v.z for v in fverts)) * 1000.0
    print(f"[QA] Etiket yuzeyi: {fx_w:.1f} x {fx_h:.1f} mm")
    assert abs(fx_w - 86.0) < 0.3 and abs(fx_h - 86.0) < 0.3, \
        "FAIL: Cover face must match the 86 x 86 mm texture band"

    # --- Cerceve / dugme: paylasilan paralaks sarti -----------------------
    ring_box = world_aabb(objs["Frame_Ring"])
    ring_w = (ring_box[1].x - ring_box[0].x) * 1000.0
    ring_crest = (ring_box[1].y - D) * 1000.0
    btn_box = world_aabb(objs["Push_Button"])
    btn_w = (btn_box[1].x - btn_box[0].x) * 1000.0
    btn_top = (btn_box[1].y - D) * 1000.0
    print(f"[QA] Cerceve Ø{ring_w:.1f} mm tepe {ring_crest:+.2f} mm | "
          f"dugme Ø{btn_w:.1f} mm tepe {btn_top:+.2f} mm")
    assert abs(ring_w - FR_R_OUT * 2000.0) < 0.3, "FAIL: frame outer diameter wrong"
    assert abs(btn_w - BTN_R * 2000.0) < 0.3, "FAIL: button diameter must be Ø44 mm"
    assert FR_R_IN > BTN_R + 0.0002, "FAIL: frame inner radius must clear the button"
    assert abs(ring_crest - btn_top) < 0.05, \
        (f"FAIL: frame crest ({ring_crest:.2f} mm) must equal button top "
         f"({btn_top:.2f} mm) so both share the same parallax")
    print("[PASS] Cerceve ve dugme ayni duzlemde (paylasilan paralaks - kayma yok)!")

    # --------------------------------------------------------------- UV oran QA
    ratios = [
        ("Cover front", UV_RECT_COVER, (86.0, 86.0)),
        ("Button face", UV_RECT_BUTTON, (1.0, 1.0)),
    ]
    for label, rect, size_mm in ratios:
        err = abs(aa_ratio(rect, size_mm) - 1.0) * 100.0
        print(f"[QA] UV aspect {label:12s}: {size_mm[0]:.1f} x {size_mm[1]:.1f} mm "
              f"-> sapma {err:.2f}%")
        assert err < 1.0, f"FAIL: UV stretch {err:.2f}% on {label}"
    print(f"[QA] Etiket doku yogunlugu: "
          f"{(UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 86.0:.1f} px/mm")
    print("[PASS] UV rectangles locked to face aspect ratios (no texture sliding)!")

    # ------------------------------------------- Doku yogunlugu (gercek, pah kirpilmis yuz)
    cov = objs["Backplate"]
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
    u_edge = xa[2] + slope_u * (BP_HX - xa[0])
    dx_span = max(s[0] for s in samples) - min(s[0] for s in samples)
    dz_span = max(s[1] for s in samples) - min(s[1] for s in samples)
    du_span = max(s[2] for s in samples) - min(s[2] for s in samples)
    dv_span = max(s[3] for s in samples) - min(s[3] for s in samples)
    dens_u = du_span * ATLAS_W / (dx_span * 1000.0)
    dens_v = dv_span * ATLAS_W / (dz_span * 1000.0)
    design = (UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 86.0
    print(f"[QA] Kapak doku yogunlugu: u={dens_u:.2f} px/mm, v={dens_v:.2f} px/mm "
          f"(tasarim {design:.2f})")
    assert abs(dens_u / dens_v - 1.0) < 0.02, \
        f"FAIL: Cover texture squeezed (u/v {dens_u:.2f} vs {dens_v:.2f})"
    assert abs(dens_u / design - 1.0) < 0.03, \
        f"FAIL: Cover texture scale off design ({dens_u:.2f} vs {design:.2f} px/mm)"
    px_at_cover_edge = u_edge * ATLAS_W
    print(f"[QA] Kapak sol kenari (X=+{BP_HX*1000:.1f} mm) atlas px: "
          f"{px_at_cover_edge:.1f} (beklenen {UV_RECT_COVER[0]:.1f})")
    assert abs(px_at_cover_edge - UV_RECT_COVER[0]) < 2.0, \
        "FAIL: Cover label is not aligned to the texture band edge"
    print("[PASS] Cover label mapped 1:1 (density + alignment verified)!")

    # --------------------------------------------------------------- Pivot (FBX sonrasi)
    re_pivot = objs["Button_Pivot"]
    rp = re_pivot.matrix_world.translation
    print(f"[QA] FBX'te Button_Pivot dunya konumu: ({rp.x * 1000:.2f}, "
          f"{rp.y * 1000:.2f}, {rp.z * 1000:.2f}) mm")
    assert abs(rp.y - D) < 1e-4, "FAIL: Button_Pivot lost its panel-surface position"
    pmin, pmax = re_pivot.get("press_min_m"), re_pivot.get("press_max_m")
    if pmin is None or pmax is None:
        print("[WARN] press custom properties FBX'ten gelmedi (kaynak .blend'de dogrulandi)")
    else:
        assert abs(pmin + PRESS_TRAVEL) < 1e-4 and abs(pmax) < 1e-4, \
            f"FAIL: press limits corrupted in FBX ({pmin}..{pmax})"
        print(f"[PASS] press_min_m / press_max_m FBX ile tasindi ({pmin}..{pmax})")

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
        "moving_pivots": ["Button_Pivot"],
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








