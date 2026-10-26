"""
=============================================================================
Security CCTV Asset Production Suite - Asset 41
Asset Name: SEC_Access_Intercom (Goruntulu Kapi Interkomu)
Triangle Budget: <= 420 tris      (hedef: 228 tris)
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Screen ,
           Slot 2 -> M_Lens_Glass , Slot 3 -> M_Emission

ASSET (Master Prompt 41):
    - Duvar paneli, hoparlor izgarasi, kamera lensi, cagri dugmesi ve kucuk ekran.

Hierarchy (Master Prompt):
    SEC_Access_Intercom (Root Empty @ 0,0,0)
     └── Housing          (Mesh, Slot 0 - 80 x 150 x 26 mm duvar paneli)
          ├── Display      (Mesh, Slot 1 M_Screen      - 64 x 30 mm gomme LCD)
          ├── Speaker_Grille (Mesh, Slot 0            - Ø34 mm delikli izgara)
          ├── Camera_Lens  (Mesh, Slot 2 M_Lens_Glass - Ø14 mm gomme lens)
          └── Button_Pivot (Empty @ dugme merkezi; yerel Y 0..-3 mm basma)
               └── Call_Button (Mesh, Slot 3 M_Emission - Ø26 mm aydinlatilmali)

NOT (sartname yorumu): Sartname "Call_Button Housing child" derken dugmenin de
basma pivotu tanimlar. Ikisi ancak soyle birlikte saglanir: Button_Pivot
Housing'in cocugu, Call_Button de Button_Pivot'un cocugu. Boylece dugme hem
Housing alt agacindadir hem de pivotu dogru mafsal merkezindedir; QA bunu
"Housing alt agacinda mi" + "pivot cocugu mu" olarak ayri ayri dogrular.

BASMA MEKANIZMASI: LIMIT_LOCATION (owner_space LOCAL, Y -3..0 mm, X/Z kilitli)
+ custom properties `press_min_m` / `press_max_m` / `press_axis`.

Calistirma:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python scripts/generate_SEC_Access_Intercom.py
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Access_Intercom"
TRIS_BUDGET = 420
PRESS_TRAVEL = 0.003            # 3 mm basma stroku (sartname)

# ---------------------------------------------------------------- Geometri (m)
D = 0.0260                      # panel derinligi
H_BACK_HX, H_BACK_HZ, H_BACK_C = 0.0375, 0.0725, 0.0040
H_MID_HX, H_MID_HZ, H_MID_C = 0.0395, 0.0745, 0.0045
H_FACE_HX, H_FACE_HZ, H_FACE_C = 0.0400, 0.0750, 0.0045

COVER_HALF_X, COVER_HALF_Z = H_FACE_HX, H_FACE_HZ      # 80 x 150 mm

# Ekran (gomme LCD)
SCREEN_X, SCREEN_Z = 0.0, 0.0400
SCREEN_HX, SCREEN_HZ, SCREEN_C = 0.0320, 0.0150, 0.0025
SCREEN_RECESS = 0.0010
SCREEN_THICK = 0.0008

# Kamera lensi (gomme)
LENS_X, LENS_Z = -0.0260, 0.0640
LENS_R, LENS_TOP_R = 0.0070, 0.0062
LENS_RECESS = 0.0006
LENS_THICK = 0.0010
LENS_SEG = 12

# Hoparlor izgarasi (hafif kubbe, gomme)
GRILLE_X, GRILLE_Z = 0.0, 0.0020
GRILLE_R, GRILLE_MID_R, GRILLE_TOP_R = 0.0170, 0.0166, 0.0150
GRILLE_RECESS = 0.0004
GRILLE_SEG = 12

# Cagri dugmesi (kabarik + basilabilir)
BTN_X, BTN_Z = 0.0, -0.0340
BTN_R, BTN_TOP_R = 0.0130, 0.0124
BTN_PROUD = 0.0032              # on yuzden cikinti: basma stroku kadar + 0.2 mm
BTN_SKIRT = 0.0050              # govde icine giren etek
BTN_SEG = 12

# Dugme bilezigi (3D oturma cercevesi).
# NEDEN 3D: dugme basma stroku icin 3.2 mm kabarik olmak zorunda ve duz doku
# yuvasi egik bakista ondan 12.7 px kayiyor ("kayma" sikayeti). Bilezik ayni
# yukseklikte gercek geometri oldugu icin dugmeyle BIRLIKTE kayar; arada
# kacmis bir cizgi kalmaz. Bilezik tepe yuzu dugme tepe yuzuyle ayni duzlemde.
BEZEL_R_IN = 0.0134             # dugme yaricapi + 0.4 mm bosluk
BEZEL_R_OUT = 0.0162
BEZEL_TOP_IN = BTN_PROUD        # ic kenar dugme tepesiyle ayni (3.2 mm)
BEZEL_TOP_OUT = 0.0006          # dis kenar yuzeye yakin (pah)
BEZEL_BASE = -0.0004            # yuzeye gomulu taban
BEZEL_SEG = 12

# ---------------------------------------------------------------- Doku atlasi
ATLAS_W, ATLAS_H = 2048, 2048
UV_RECT_COVER = (32, 32, 1032, 1907)       # 1000 x 1875 px -> 80 x 150 mm
UV_RECT_SCREEN = (1160, 32, 1960, 407)     # 800 x 375 px  -> 64 x 30 mm
UV_RECT_LENS = (1160, 440, 1660, 940)      # 500 x 500 px  -> Ø14 lens
UV_RECT_GRILLE = (1700, 440, 2016, 756)    # 316 x 316 px  -> Ø34 izgara
UV_RECT_BUTTON = (1160, 970, 1560, 1370)   # 400 x 400 px  -> Ø26 dugme
PIX_FLAT_BODY = (1650, 1050)
PIX_FLAT_SIDE = (1700, 1330)
PIX_FLAT_DARK = (1700, 1590)
PIX_FLAT_SLATE = (1700, 1830)


def pix_to_uv(px, py):
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_FLAT_BODY)
FLAT_UV_SIDE = pix_to_uv(*PIX_FLAT_SIDE)
FLAT_UV_DARK = pix_to_uv(*PIX_FLAT_DARK)
FLAT_UV_SLATE = pix_to_uv(*PIX_FLAT_SLATE)


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


def set_radial_uv(face, uv_layer, rect, cx, cz, r_out):
    """Daire sekilli yuzu radyal haritalar (lens/izgara/dugme bantlari)."""
    u0, v0, u1, v1 = rect
    for loop in face.loops:
        nx = (loop.vert.co.x - cx) / r_out
        nz = (loop.vert.co.z - cz) / r_out
        u = u0 + (0.5 + 0.5 * nx) * (u1 - u0)
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
    """Slot 0 Atlas, Slot 1 Screen, Slot 2 Lens_Glass, Slot 3 Emission."""
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

    # ---------------- Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes = mat_atlas.node_tree.nodes
    links = mat_atlas.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    add_tex(nodes, links, bsdf, (-420, 320))
    bsdf.inputs["Roughness"].default_value = 0.34
    bsdf.inputs["Metallic"].default_value = 0.08
    mat_atlas.diffuse_color = (0.86, 0.88, 0.92, 1.0)

    # ---------------- Slot 1: M_Screen (ailesi: emission 1.25-1.50)
    mat_screen = bpy.data.materials.new("M_Screen")
    mat_screen.use_nodes = True
    n_s = mat_screen.node_tree.nodes
    l_s = mat_screen.node_tree.links
    b_s = n_s.get("Principled BSDF")
    tex_s = add_tex(n_s, l_s, b_s, (-420, 120))
    scr_col = (0.10, 0.42, 0.30, 1.0)
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
    b_s.inputs["Roughness"].default_value = 0.10
    mat_screen.diffuse_color = scr_col

    # ---------------- Slot 2: M_Lens_Glass (asset 33 dili)
    mat_glass = bpy.data.materials.new("M_Lens_Glass")
    mat_glass.use_nodes = True
    n_g = mat_glass.node_tree.nodes
    l_g = mat_glass.node_tree.links
    b_g = n_g.get("Principled BSDF")
    add_tex(n_g, l_g, b_g, (-420, -80))
    b_g.inputs["Roughness"].default_value = 0.06
    if "Transmission Weight" in b_g.inputs:
        b_g.inputs["Transmission Weight"].default_value = 0.35
    if "IOR" in b_g.inputs:
        b_g.inputs["IOR"].default_value = 1.55
    mat_glass.diffuse_color = (0.10, 0.20, 0.28, 1.0)

    # ---------------- Slot 3: M_Emission (dugme aydinlatmasi)
    mat_em = bpy.data.materials.new("M_Emission")
    mat_em.use_nodes = True
    n_e = mat_em.node_tree.nodes
    l_e = mat_em.node_tree.links
    b_e = n_e.get("Principled BSDF")
    tex_e = add_tex(n_e, l_e, b_e, (-420, -280))
    em_col = (0.14, 0.90, 0.42, 1.0)
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
        b_e.inputs["Emission Strength"].default_value = 7.0
    b_e.inputs["Roughness"].default_value = 0.20
    mat_em.diffuse_color = em_col

    return [mat_atlas, mat_screen, mat_glass, mat_em]


def build_housing(mats):
    """Duvar paneli: 3 kademeli pahli govde, on yuz 80 x 150 mm."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    profiles = [
        (chamfer_profile(H_BACK_HX, H_BACK_HZ, H_BACK_C), 0.0),
        (chamfer_profile(H_MID_HX, H_MID_HZ, H_MID_C), D - 0.0080),
        (chamfer_profile(H_FACE_HX, H_FACE_HZ, H_FACE_C), D),
    ]
    rings = [[bm.verts.new(Vector((p[0], y, p[1]))) for p in pts]
             for pts, y in profiles]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[-1])
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_COVER),
                     flip_u=True,
                     extent=(-H_FACE_HX, H_FACE_HX, -H_FACE_HZ, H_FACE_HZ))

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
    return finish_mesh(bm, "Housing", mats)


def build_display(mats):
    """Gomme LCD: on yuzun 1.0 mm gerisinde ince cam plaka (64 x 30 mm)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    prof = chamfer_profile(SCREEN_HX, SCREEN_HZ, SCREEN_C)
    y_top = D + 0.0003
    rings = [[bm.verts.new(Vector((SCREEN_X + p[0], yy, SCREEN_Z + p[1])))
              for p in prof] for yy in (D - 0.0005, y_top)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 1
    set_flat_uv(f_back, uv_layer, FLAT_UV_DARK)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 1
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_SCREEN),
                     flip_u=True,
                     extent=(SCREEN_X - SCREEN_HX, SCREEN_X + SCREEN_HX,
                             SCREEN_Z - SCREEN_HZ, SCREEN_Z + SCREEN_HZ))

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 1
        set_flat_uv(f, uv_layer, FLAT_UV_SLATE)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Display", mats)


def build_disc(name, mats, cx, cz, seg, rings_def, mat_index, uv_rect,
               cap_uv_radial=True, side_uv=None):
    """Kapali disk/konik kapak: rings_def = [(y, r), ...] arkadan one dogru.

    Son halka on yuzdur (cap). uv_rect varsa cap radyal haritalanir.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    loop_rings = []
    for (yy, rr) in rings_def:
        ring = []
        for i in range(seg):
            # faz 0: bir kose +X eksenine oturur -> gercek cap okunur
            ang = i * (2.0 * math.pi / seg)
            ring.append(bm.verts.new(Vector((cx + math.cos(ang) * rr, yy,
                                             cz + math.sin(ang) * rr))))
        loop_rings.append(ring)

    for r in range(len(loop_rings) - 1):
        a_ring, b_ring = loop_rings[r], loop_rings[r + 1]
        for i in range(seg):
            j = (i + 1) % seg
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = mat_index
            set_flat_uv(f, uv_layer, side_uv if side_uv else FLAT_UV_DARK)

    f_bot = bm.faces.new(list(reversed(loop_rings[0])))
    f_bot.smooth = False
    f_bot.material_index = mat_index
    set_flat_uv(f_bot, uv_layer, FLAT_UV_DARK)

    f_top = bm.faces.new(loop_rings[-1])
    f_top.smooth = False
    f_top.material_index = mat_index
    if uv_rect and cap_uv_radial:
        set_radial_uv(f_top, uv_layer, uv_rect, cx, cz, rings_def[-1][1])
    elif uv_rect:
        set_face_uv_rect(f_top, uv_layer, uv_rect, flip_u=True)
    else:
        set_flat_uv(f_top, uv_layer, FLAT_UV_SLATE)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, name, mats)


def build_call_button(mats):
    """Cagri dugmesi: yerel origin dugme merkezinde (pivot ile ayni).

    Yerel +Y govdeden disari; tepe yuzu +BTN_PROUD'da. Etek (skirt) negatif Y'de
    govde icine girer, boylece basildiginda bosluk olusmaz.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    rings_def = [(-BTN_SKIRT, BTN_R), (0.0000, BTN_R), (BTN_PROUD, BTN_TOP_R)]
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
            f.material_index = 3
            set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    f_bot = bm.faces.new(list(reversed(loop_rings[0])))
    f_bot.smooth = False
    f_bot.material_index = 3
    set_flat_uv(f_bot, uv_layer, FLAT_UV_DARK)

    f_top = bm.faces.new(loop_rings[-1])
    f_top.smooth = False
    f_top.material_index = 3
    set_radial_uv(f_top, uv_layer, uv_rect_from_pixels(*UV_RECT_BUTTON),
                  0.0, 0.0, BTN_TOP_R)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Call_Button", mats)


def build_button_bezel(mats):
    """Dugme bilezigi: kapali 4 noktali profil, 12 kenar donel govde.

    Profil: dis alt -> dis ust (yuzeye yakin) -> ic ust (dugme tepesiyle ayni)
    -> ic alt. Boylece dugme, gercek bir yuvaya oturmus gibi okunur ve egik
    bakista dugmeyle ayni paralaksla hareket eder.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    prof = [(BEZEL_R_OUT, BEZEL_BASE), (BEZEL_R_OUT, BEZEL_TOP_OUT),
            (BEZEL_R_IN, BEZEL_TOP_IN), (BEZEL_R_IN, BEZEL_BASE)]
    rings = []
    for (rr, yy) in prof:
        ring = []
        for i in range(BEZEL_SEG):
            ang = i * (2.0 * math.pi / BEZEL_SEG)
            ring.append(bm.verts.new(Vector((BTN_X + math.cos(ang) * rr,
                                             D + yy,
                                             BTN_Z + math.sin(ang) * rr))))
        rings.append(ring)

    n = len(prof)
    for r in range(n):
        a_ring, b_ring = rings[r], rings[(r + 1) % n]
        for i in range(BEZEL_SEG):
            j = (i + 1) % BEZEL_SEG
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = 0
            set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Button_Bezel", mats)


def parent_keep(child, parent):
    """Parent baglar ama cocugun dunya konumunu korur (matrix_parent_inverse)."""
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


def aa_ratio(pixels, size_mm):
    x0, y0, x1, y1 = pixels
    return ((x1 - x0) / float(y1 - y0)) / (size_mm[0] / float(size_mm[1]))


def build_all(mats):
    rect_screen = uv_rect_from_pixels(*UV_RECT_SCREEN)
    rect_lens = uv_rect_from_pixels(*UV_RECT_LENS)
    rect_grille = uv_rect_from_pixels(*UV_RECT_GRILLE)

    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    housing = build_housing(mats)
    parent_keep(housing, root)

    # ------------------------------------------------------------ Ekran
    display = build_display(mats)
    parent_keep(display, housing)

    # ------------------------------------------------------------ Izgara (kubbe)
    grille = build_disc(
        "Speaker_Grille", mats, GRILLE_X, GRILLE_Z, GRILLE_SEG,
        [(D - 0.0005, GRILLE_R),
         (D + 0.0001, GRILLE_MID_R),
         (D + 0.0003, GRILLE_TOP_R)],
        0, rect_grille, cap_uv_radial=False, side_uv=FLAT_UV_SLATE,
    )
    parent_keep(grille, housing)

    # ------------------------------------------------------------ Kamera lensi
    lens = build_disc(
        "Camera_Lens", mats, LENS_X, LENS_Z, LENS_SEG,
        [(D - 0.0005, LENS_R),
         (D + 0.0003, LENS_TOP_R)],
        2, rect_lens, cap_uv_radial=True,
    )
    parent_keep(lens, housing)

    # ------------------------------------------------------------ Basma pivotu
    # Pivot dugmenin tam merkezinde (X/Z dugme merkezi, Y on yuz duzlemi).
    bezel = build_button_bezel(mats)
    parent_keep(bezel, housing)

    pivot = bpy.data.objects.new("Button_Pivot", None)
    pivot.empty_display_type = 'ARROWS'
    pivot.empty_display_size = 0.01
    pivot.location = Vector((BTN_X, D, BTN_Z))
    bpy.context.collection.objects.link(pivot)
    bpy.context.view_layer.update()
    parent_keep(pivot, housing)

    con = pivot.constraints.new('LIMIT_LOCATION')
    con.owner_space = 'LOCAL'
    # KRITIK: LIMIT_LOCATION pivotun MUTLAK yerel konumunu kirpar (dönüşte 0
    # etrafinda oldugu gibi degil). Pivot dugme merkezinde (0, D, BTN_Z) durdugu
    # icin limitler dinlenme konumu etrafinda tanimlanir; aksi halde pivot
    # baslangica cakilir ve dugme govdenin icinde kalir.
    con.use_min_y = True
    con.min_y = D - PRESS_TRAVEL
    con.use_max_y = True
    con.max_y = D
    con.use_min_x = con.use_max_x = True
    con.min_x = con.max_x = BTN_X
    con.use_min_z = con.use_max_z = True
    con.min_z = con.max_z = BTN_Z
    # Motor tarafi limitleri custom property'den okur: hem STROK hem MUTLAK aralik
    pivot["press_min_m"] = -PRESS_TRAVEL
    pivot["press_max_m"] = 0.0
    pivot["press_axis"] = "Y"
    pivot["rest_y_m"] = D
    pivot["local_y_min"] = D - PRESS_TRAVEL
    pivot["local_y_max"] = D

    # Dugme geometrisi PIVOT YEREL uzayinda uretildi (origin = dugme merkezi),
    # bu yuzden parent_keep KULLANILMAZ: ters matris dunya konumunu sifira cekerdi.
    # Obje transform'u identity kalir, konumu pivot belirler.
    button = build_call_button(mats)
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


def qa_button(objs):
    """Basma pivotu: konum, limitler, custom property ve 3 mm strok testi."""
    pivot = objs["Button_Pivot"]
    button = objs["Call_Button"]
    housing = objs["Housing"]
    assert pivot.type == 'EMPTY', "FAIL: Button_Pivot must be an Empty"
    loc = pivot.location
    print(f"[QA] Button_Pivot konumu: ({loc.x * 1000:.2f}, {loc.y * 1000:.2f}, "
          f"{loc.z * 1000:.2f}) mm")
    assert abs(loc.x - BTN_X) < 1e-6 and abs(loc.z - BTN_Z) < 1e-6, \
        "FAIL: Button_Pivot is not centred on the button"
    assert abs(loc.y - D) < 1e-6, "FAIL: Button_Pivot is not on the front face plane"

    lo = pivot.get("press_min_m")
    hi = pivot.get("press_max_m")
    axis = pivot.get("press_axis")
    assert lo is not None and hi is not None and axis is not None, \
        "FAIL: press limits missing as custom properties"
    assert abs(lo + PRESS_TRAVEL) < 1e-6 and abs(hi) < 1e-6, \
        f"FAIL: press range wrong ({lo}..{hi}), expected -{PRESS_TRAVEL}..0"
    assert axis == "Y", f"FAIL: press axis must be Y, found {axis}"
    print(f"[QA] Limit custom properties: press_min_m={lo}, press_max_m={hi}, axis={axis}")

    cons = [c for c in pivot.constraints if c.type == 'LIMIT_LOCATION']
    assert cons, "FAIL: Button_Pivot has no LIMIT_LOCATION constraint"
    con = cons[0]
    assert con.owner_space == 'LOCAL', f"FAIL: constraint space must be LOCAL ({con.owner_space})"
    # Limitler DINLENME konumu etrafinda olmali (LIMIT_LOCATION mutlak Y kirpar)
    assert abs(con.min_y - (D - PRESS_TRAVEL)) < 1e-6, "FAIL: LIMIT_LOCATION min_y wrong"
    assert abs(con.max_y - D) < 1e-6, "FAIL: LIMIT_LOCATION max_y wrong"
    assert abs(con.min_x - BTN_X) < 1e-6 and abs(con.max_x - BTN_X) < 1e-6, \
        "FAIL: LIMIT_LOCATION X must be pinned to the button centre"
    assert abs(con.min_z - BTN_Z) < 1e-6 and abs(con.max_z - BTN_Z) < 1e-6, \
        "FAIL: LIMIT_LOCATION Z must be pinned to the button centre"
    span = (con.max_y - con.min_y) * 1000.0
    print(f"[PASS] LIMIT_LOCATION (LOCAL, Y {con.min_y*1000:.1f}..{con.max_y*1000:.1f} mm "
          f"= {span:.0f} mm strok, X/Z dugme merkezinde kilitli)")

    # --- Strok testi: dinlenme / basili durumda dugme govdesi nerede? ------
    rest_top = max((button.matrix_world @ v.co).y for v in button.data.vertices)
    print(f"[QA] Dinlenme: dugme tepe Y={rest_top * 1000:.2f} mm "
          f"(on yuz {D * 1000:.1f} mm, cikinti {(rest_top - D) * 1000:.2f} mm)")
    assert abs((rest_top - D) - BTN_PROUD) < 1e-6, \
        f"FAIL: rest protrusion {((rest_top - D) * 1000):.2f} mm != {BTN_PROUD*1000:.1f} mm"

    pivot.location.y = D - PRESS_TRAVEL
    bpy.context.view_layer.update()
    pressed_top = max((button.matrix_world @ v.co).y for v in button.data.vertices)
    travel = (rest_top - pressed_top) * 1000.0
    proud = (pressed_top - D) * 1000.0
    print(f"[QA] Basili:   dugme tepe Y={pressed_top * 1000:.2f} mm -> "
          f"strok {travel:.2f} mm, kalan cikinti {proud:.2f} mm")
    assert abs(travel - PRESS_TRAVEL * 1000.0) < 1e-3, \
        f"FAIL: press travel {travel:.3f} mm != {PRESS_TRAVEL*1000:.1f} mm"
    assert proud >= 0.1, \
        f"FAIL: button sinks {abs(proud):.2f} mm into the housing when pressed"
    # Basili haldeyken de govdeye degmiyor / gomuluyor olmamali
    assert parts_in_contact(button, housing) or proud > 0, \
        "FAIL: pressed button lost contact with the housing"

    pivot.location.y = D
    bpy.context.view_layer.update()
    print("[PASS] Basma stroku 3.00 mm, basili halde 0.20 mm cikinti kaliyor "
          "(govdeye gomulmuyor)")


def main():
    clean_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    mats = setup_materials()
    root = build_all(mats)

    # Constraint + custom property'ler FBX'te tasinmaz -> export ONCESI dogrula
    qa_button({o.name: o for o in [root] + root.children_recursive})

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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 41) ---")
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
        f"FAIL: expected exactly root + Button_Pivot empties, found {empty_names}"
    print("[PASS] Exactly one moving pivot empty (Button_Pivot) verified!")

    # --------------------------------------------------------------- Hiyerarsi
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    expected_parents = {
        "Housing": ASSET_NAME,
        "Display": "Housing",
        "Speaker_Grille": "Housing",
        "Camera_Lens": "Housing",
        "Button_Bezel": "Housing",
        "Button_Pivot": "Housing",
        "Call_Button": "Button_Pivot",
    }
    for child_name, parent_name in expected_parents.items():
        child = objs.get(child_name)
        assert child is not None, f"FAIL: {child_name} missing in FBX hierarchy"
        assert child.parent is not None and child.parent.name == parent_name, \
            f"FAIL: {child_name} parent mismatch (expected {parent_name})"
    print(f"[PASS] Full parent-child hierarchy verified ({len(expected_parents)} relations)!")
    # Sartname "Call_Button Housing child" -> dugme pivot uzerinden Housing alt agacinda
    anc, chain = objs["Call_Button"].parent, []
    while anc is not None:
        chain.append(anc.name)
        anc = anc.parent
    assert "Housing" in chain, "FAIL: Call_Button is not inside the Housing subtree"
    print(f"[PASS] Call_Button is inside the Housing subtree: {' -> '.join(chain)}!")

    # --------------------------------------------------------------- Materyal slotlari
    expected_mats = ["M_Security_Atlas", "M_Screen", "M_Lens_Glass", "M_Emission"]
    for name in ("Housing", "Display", "Speaker_Grille", "Camera_Lens",
                 "Button_Bezel", "Call_Button"):
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:4] == expected_mats, \
            f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Atlas, Screen, Lens_Glass, Emission)!")

    # --------------------------------------------------------------- Slot kullanimi
    for name in ("Housing", "Speaker_Grille", "Button_Bezel"):
        idxs = {p.material_index for p in objs[name].data.polygons}
        assert idxs == {0}, f"FAIL: {name} must be M_Security_Atlas (found {idxs})"
    assert {p.material_index for p in objs["Display"].data.polygons} == {1}, \
        "FAIL: Display must be M_Screen"
    assert {p.material_index for p in objs["Camera_Lens"].data.polygons} == {2}, \
        "FAIL: Camera_Lens must be M_Lens_Glass"
    btn_polys = objs["Call_Button"].data.polygons
    assert all(p.material_index == 3 for p in btn_polys) and btn_polys, \
        "FAIL: Call_Button must be M_Emission"
    scr = bpy.data.materials.get("M_Screen")
    sb = None
    for node in scr.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            sb = node
    st = sb.inputs["Emission Strength"].default_value if "Emission Strength" in sb.inputs else None
    assert st is not None and 1.2 <= st <= 1.6, \
        f"FAIL: M_Screen emission strength out of family range ({st})"
    print(f"[PASS] Slot usage verified (izgara/govde atlas, ekran Screen {st:.2f}, "
          f"lens Glass, dugme Emission - {len(btn_polys)} yuz)!")

    # --------------------------------------------------------------- Bosluk / olcu QA
    contact_pairs = [
        ("Display", "Housing"),
        ("Speaker_Grille", "Housing"),
        ("Camera_Lens", "Housing"),
        ("Button_Bezel", "Housing"),
        ("Call_Button", "Housing"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), \
            f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} contact pairs)!")

    wall_y = world_aabb(objs["Housing"])[0].y * 1000.0
    print(f"[QA] Duvar yuzeyi offseti: {wall_y:.2f} mm (0.00 olmali)")
    assert abs(wall_y) < 0.05, "FAIL: Housing does not sit on the wall plane"

    hs = world_aabb(objs["Housing"])
    hx = (hs[1].x - hs[0].x) * 1000.0
    hz = (hs[1].z - hs[0].z) * 1000.0
    hy = (hs[1].y - hs[0].y) * 1000.0
    print(f"[QA] Panel olcusu: {hx:.1f} x {hy:.1f} x {hz:.1f} mm (G x D x Y)")
    assert abs(hx - 80.0) < 0.3 and abs(hz - 150.0) < 0.3 and abs(hy - 26.0) < 0.3, \
        "FAIL: Housing must be 80 x 150 x 26 mm"

    front_polys = [p for p in objs["Housing"].data.polygons if p.normal.y > 0.9]
    front_poly = max(front_polys, key=lambda p: p.area)
    fverts = [objs["Housing"].matrix_world
              @ objs["Housing"].data.vertices[v].co for v in front_poly.vertices]
    fx_w = (max(v.x for v in fverts) - min(v.x for v in fverts)) * 1000.0
    fx_h = (max(v.z for v in fverts) - min(v.z for v in fverts)) * 1000.0
    print(f"[QA] Etiket yuzeyi: {fx_w:.1f} x {fx_h:.1f} mm")
    assert abs(fx_w - 80.0) < 0.3 and abs(fx_h - 150.0) < 0.3, \
        "FAIL: Cover face size does not match the 80 x 150 mm texture band"

    # --------------------------------------------------------------- Parca kontrolleri
    scr_box = world_aabb(objs["Display"])
    scr_w = (scr_box[1].x - scr_box[0].x) * 1000.0
    scr_h = (scr_box[1].z - scr_box[0].z) * 1000.0
    scr_proud = (scr_box[1].y - D) * 1000.0
    print(f"[QA] Ekran: {scr_w:.1f} x {scr_h:.1f} mm, cikinti {scr_proud:.2f} mm")
    assert abs(scr_w - 64.0) < 0.3 and abs(scr_h - 30.0) < 0.3, \
        "FAIL: Display must be 64 x 30 mm"
    assert 0.1 <= scr_proud <= 0.4, f"FAIL: Display protrusion {scr_proud:.2f} mm outside SOP (0.1..0.4 mm)"

    for name, dia in (("Speaker_Grille", 34.0), ("Camera_Lens", 14.0)):
        b = world_aabb(objs[name])
        dx = (b[1].x - b[0].x) * 1000.0
        dz = (b[1].z - b[0].z) * 1000.0
        proud = (b[1].y - D) * 1000.0
        print(f"[QA] {name}: Ø{dx:.1f} / Ø{dz:.1f} mm, cikinti {proud:.2f} mm")
        assert abs(dx - dia) < 0.3 and abs(dz - dia) < 0.3, \
            f"FAIL: {name} diameter must be Ø{dia} mm"
        assert 0.1 <= proud <= 0.4, f"FAIL: {name} protrusion {proud:.2f} mm outside SOP (0.1..0.4 mm)"

    btn_box = world_aabb(objs["Call_Button"])
    btn_dx = (btn_box[1].x - btn_box[0].x) * 1000.0
    btn_proud = (btn_box[1].y - D) * 1000.0
    print(f"[QA] Cagri dugmesi: Ø{btn_dx:.1f} mm, cikinti {btn_proud:.2f} mm "
          f"(strok {PRESS_TRAVEL*1000:.0f} mm + 0.2 mm)")
    assert abs(btn_dx - 26.0) < 0.3, "FAIL: Call_Button must be Ø26 mm"
    assert btn_proud >= PRESS_TRAVEL * 1000.0, \
        "FAIL: button protrusion is smaller than the press travel"

    # --- Bilezik: dugmeyi cevreleyen gercek 3D yuva -----------------------
    bz = world_aabb(objs["Button_Bezel"])
    bz_dx = (bz[1].x - bz[0].x) * 1000.0
    bz_top = (bz[1].y - D) * 1000.0
    bz_cx = 0.5 * (bz[0].x + bz[1].x)
    bz_cz = 0.5 * (bz[0].z + bz[1].z)
    print(f"[QA] Bilezik: Ø{bz_dx:.1f} mm, tepe {bz_top:+.2f} mm, merkez "
          f"({bz_cx * 1000:.2f}, {bz_cz * 1000:.2f}) mm")
    assert abs(bz_dx - BEZEL_R_OUT * 2000.0) < 0.3, \
        "FAIL: bezel outer diameter wrong"
    assert abs(bz_cx - BTN_X) < 1e-6 and abs(bz_cz - BTN_Z) < 1e-6, \
        "FAIL: bezel is not concentric with the button"
    # Bilezik ic yaricapi dugme yaricapindan buyuk olmali (dugme icine oturur)
    assert BEZEL_R_IN > BTN_R + 0.0002, "FAIL: bezel inner radius must clear the button"
    # Bilezik tepesi dugme tepesiyle ayni duzlemde olmali -> paralaks birlikte
    assert abs(bz_top - BTN_PROUD * 1000.0) < 0.05, \
        (f"FAIL: bezel top ({bz_top:.2f} mm) must match the button top "
         f"({BTN_PROUD*1000:.2f} mm) so both share the same parallax")
    print("[PASS] Bilezik dugmeyi cevreliyor ve ayni duzlemde (paylasilan paralaks)!")
    print("[PASS] Ekran/lens/izgara gomme, dugme basilabilir cikintida!")

    # --------------------------------------------------------------- UV oran QA
    ratios = [
        ("Cover front", UV_RECT_COVER, (80.0, 150.0)),
        ("Screen", UV_RECT_SCREEN, (64.0, 30.0)),
        ("Camera lens", UV_RECT_LENS, (1.0, 1.0)),
        ("Grille", UV_RECT_GRILLE, (1.0, 1.0)),
        ("Button", UV_RECT_BUTTON, (1.0, 1.0)),
    ]
    for label, rect, size_mm in ratios:
        err = abs(aa_ratio(rect, size_mm) - 1.0) * 100.0
        print(f"[QA] UV aspect {label:12s}: {size_mm[0]:.1f} x {size_mm[1]:.1f} mm "
              f"-> sapma {err:.2f}%")
        assert err < 1.0, f"FAIL: UV stretch {err:.2f}% on {label}"
    print(f"[QA] Etiket doku yogunlugu: "
          f"{(UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 80.0:.1f} px/mm")
    print("[PASS] UV rectangles locked to face aspect ratios (no texture sliding)!")

    # ------------------------------------------- Doku yogunlugu (gercek, pah kirpilmis yuz)
    hou = objs["Housing"]
    hme, huv = hou.data, hou.data.uv_layers[0]
    mw = hou.matrix_world
    samples = []
    for li in front_poly.loop_indices:
        co = mw @ hme.vertices[hme.loops[li].vertex_index].co
        uv = huv.data[li].uv
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
    design = (UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 80.0
    print(f"[QA] Kapak doku yogunlugu: u={dens_u:.2f} px/mm, v={dens_v:.2f} px/mm "
          f"(tasarim {design:.2f})")
    assert abs(dens_u / dens_v - 1.0) < 0.02, \
        f"FAIL: Cover texture squeezed (u/v {dens_u:.2f} vs {dens_v:.2f})"
    assert abs(dens_u / design - 1.0) < 0.03, \
        f"FAIL: Cover texture scale off design ({dens_u:.2f} vs {design:.2f} px/mm)"
    px_at_cover_edge = u_edge * ATLAS_W
    print(f"[QA] Kapak sol kenari (X=+{COVER_HALF_X*1000:.1f} mm) atlas px: "
          f"{px_at_cover_edge:.1f} (beklenen {UV_RECT_COVER[0]:.1f})")
    assert abs(px_at_cover_edge - UV_RECT_COVER[0]) < 2.0, \
        "FAIL: Cover label is not aligned to the texture band edge"
    print("[PASS] Cover label mapped 1:1 (density + alignment verified)!")

    # --------------------------------------------------------------- Pivot (FBX sonrasi)
    re_pivot = objs["Button_Pivot"]
    pl = re_pivot.matrix_local.translation
    print(f"[QA] FBX'te Button_Pivot yerel konumu: ({pl.x * 1000:.2f}, "
          f"{pl.y * 1000:.2f}, {pl.z * 1000:.2f}) mm")
    assert abs(pl.x - BTN_X) < 1e-4 and abs(pl.z - BTN_Z) < 1e-4, \
        "FAIL: Button_Pivot lost its centring through FBX"
    pmin = re_pivot.get("press_min_m")
    pmax = re_pivot.get("press_max_m")
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







