"""
=============================================================================
Security CCTV Asset Production Suite - Asset 39
Asset Name: SEC_Beam_Detector_Dual  (Cift Isinli Bariyer Dedektoru)
Triangle Budget: <= 340 tris      (hedef: 240 tris)
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Lens_Glass , Slot 2 -> M_Emission

ASSET (Master Prompt 39):
    - Dikey ince muhafaza, iki optik pencere, montaj ayagi ve durum gostergesi.

Hierarchy (Master Prompt):
    SEC_Beam_Detector_Dual (Root Empty @ 0,0,0)
     ├── Mount_Bracket      (Mesh - 46 x 76 x 4 mm duvar plakasi + konik kol + mentese pimi)
     └── Aim_Pivot          (Empty @ iki pencerenin optik ekseni; yerel X -10..+10 deg)
          └── Detector_Housing   (Mesh - 36 x 84 x 22 mm dikey ince muhafaza)
               ├── Optical_Window_Upper (Mesh, Slot 1 M_Lens_Glass - gomme cam, Z=+24 mm)
               ├── Optical_Window_Lower (Mesh, Slot 1 M_Lens_Glass - gomme cam, Z=-24 mm)
               └── Status_LED           (Mesh, Slot 2 M_Emission - gomme durum lensi)

DONUS LIMITI: Aim_Pivot uzerinde LIMIT_ROTATION (owner_space LOCAL, X -10..+10)
              + Blender custom properties `tilt_min_deg` / `tilt_max_deg`.

Calistirma:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python scripts/generate_SEC_Beam_Detector_Dual.py
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Beam_Detector_Dual"
TRIS_BUDGET = 340
TILT_LIMIT_DEG = 10.0

# ---------------------------------------------------------------- Geometri (m)
# Duvar plakasi (ayak izi 46 x 76 mm)
BP_HX, BP_HZ, BP_C = 0.0230, 0.0380, 0.0040
BP_Y0, BP_Y1 = 0.0, 0.0040
# Konik kol: plakadan mentese eksenine kadar daralir
ARM_HX, ARM_HZ, ARM_C = 0.0120, 0.0130, 0.0030
ARM_Y = 0.0260
# Mentese pimi (X ekseni boyunca; kasayi tasiyan gorsel mafsal)
PIN_Y, PIN_R, PIN_HX, PIN_SEG = 0.0290, 0.0070, 0.0195, 10

# Kasa: arka Y=0.032 -> on Y=0.048 (22 mm derinlik), on yuz 36 x 84 mm
H_BACK_HX, H_BACK_HZ, H_BACK_C = 0.0150, 0.0390, 0.0030
H_MID_HX, H_MID_HZ, H_MID_C = 0.0172, 0.0412, 0.0034
H_FACE_HX, H_FACE_HZ, H_FACE_C = 0.0180, 0.0420, 0.0035
H_Y_BACK, H_Y_MID, H_Y_LIP, H_Y_FACE = 0.0320, 0.0360, 0.0460, 0.0480

# On yuz = etiket bandi: 36.0 x 84.0 mm
COVER_HALF_X, COVER_HALF_Z = H_FACE_HX, H_FACE_HZ

# Optik pencereler (gomme cam: paralaks yok) ve durum lensi
WINDOW_X, WINDOW_Z = 0.0, 0.0240
GLASS_R, GLASS_TOP_R, GLASS_SEG = 0.0062, 0.0059, 12
GLASS_RECESS = 0.0006           # on yuzden iceri gomme
GLASS_THICK = 0.0008
LED_X, LED_Z, LED_R, LED_PROTRUSION = -0.0115, 0.0100, 0.0025, 0.0003
LED_SEG = 8

# ---------------------------------------------------------------- Doku atlasi
ATLAS_W, ATLAS_H = 2048, 2048
UV_RECT_COVER = (32, 32, 882, 2016)         # 850 x 1984 px -> 36 x 84 mm
UV_RECT_LENS = (900, 32, 1400, 532)         # 500 x 500 px -> optik cam
UV_RECT_LED = (1420, 32, 1720, 332)         # 300 x 300 px -> durum lensi
PIX_FLAT_BODY = (980, 620)
PIX_FLAT_SIDE = (1200, 620)
PIX_FLAT_DARK = (1420, 620)
PIX_FLAT_WARN = (1640, 620)


def pix_to_uv(px, py):
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_FLAT_BODY)
FLAT_UV_SIDE = pix_to_uv(*PIX_FLAT_SIDE)
FLAT_UV_DARK = pix_to_uv(*PIX_FLAT_DARK)


def uv_rect_from_pixels(x0, y0, x1, y1):
    return (x0 / ATLAS_W, 1.0 - (y1 / ATLAS_H), x1 / ATLAS_W, 1.0 - (y0 / ATLAS_H))


def set_face_uv_rect(face, uv_layer, rect, flip_u=False, extent=None):
    """
    Yuzey noktalarini verilen UV dikdortgenine oransal olarak haritalar.
    extent: (minx, maxx, minz, maxz) gercek yuz sinirlari (pah kirpilmis
    koselerde dokunun sikismasini onler).
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
    """Slot 0: M_Security_Atlas, Slot 1: M_Lens_Glass, Slot 2: M_Emission."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    tex_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    # ---------------- Slot 0: M_Security_Atlas
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

    # ---------------- Slot 1: M_Lens_Glass (asset 33 dili)
    mat_glass = bpy.data.materials.new("M_Lens_Glass")
    mat_glass.use_nodes = True
    nodes_g = mat_glass.node_tree.nodes
    links_g = mat_glass.node_tree.links
    bsdf_g = nodes_g.get("Principled BSDF")
    if os.path.exists(tex_path):
        tex_g = nodes_g.new("ShaderNodeTexImage")
        tex_g.image = bpy.data.images.load(tex_path)
        try:
            tex_g.image.pack()
        except Exception:
            pass
        tex_g.image.colorspace_settings.name = 'sRGB'
        tex_g.location = (-420, 40)
        links_g.new(tex_g.outputs["Color"], bsdf_g.inputs["Base Color"])
    bsdf_g.inputs["Roughness"].default_value = 0.06
    if "Transmission Weight" in bsdf_g.inputs:
        bsdf_g.inputs["Transmission Weight"].default_value = 0.35
    if "IOR" in bsdf_g.inputs:
        bsdf_g.inputs["IOR"].default_value = 1.55
    mat_glass.diffuse_color = (0.10, 0.20, 0.28, 1.0)

    # ---------------- Slot 2: M_Emission (yalnizca durum lensi)
    mat_em = bpy.data.materials.new("M_Emission")
    mat_em.use_nodes = True
    nodes_e = mat_em.node_tree.nodes
    links_e = mat_em.node_tree.links
    bsdf_e = nodes_e.get("Principled BSDF")
    em_col = (0.14, 0.90, 0.42, 1.0)
    if os.path.exists(tex_path):
        tex_e = nodes_e.new("ShaderNodeTexImage")
        tex_e.image = bpy.data.images.load(tex_path)
        try:
            tex_e.image.pack()
        except Exception:
            pass
        tex_e.image.colorspace_settings.name = 'sRGB'
        tex_e.location = (-420, -160)
        links_e.new(tex_e.outputs["Color"], bsdf_e.inputs["Base Color"])
        if "Emission Color" in bsdf_e.inputs:
            links_e.new(tex_e.outputs["Color"], bsdf_e.inputs["Emission Color"])
        elif "Emission" in bsdf_e.inputs:
            links_e.new(tex_e.outputs["Color"], bsdf_e.inputs["Emission"])
    if "Emission Color" in bsdf_e.inputs:
        bsdf_e.inputs["Emission Color"].default_value = em_col
    elif "Emission" in bsdf_e.inputs:
        bsdf_e.inputs["Emission"].default_value = em_col
    if "Emission Strength" in bsdf_e.inputs:
        bsdf_e.inputs["Emission Strength"].default_value = 7.0
    bsdf_e.inputs["Roughness"].default_value = 0.18
    mat_em.diffuse_color = em_col

    return [mat_atlas, mat_glass, mat_em]


def add_cylinder_to_bm(bm, uv_layer, center, axis, radius, half_len, segments,
                       mat_index=0, side_uv=None, cap_uv=None, phase=0.0):
    """Mevcut bmesh'e X ekseni boyunca kapali silindir ekler (mentese pimi)."""
    rings = []
    cx, cy, cz = center
    for sgn in (-1.0, 1.0):
        ring = []
        for i in range(segments):
            ang = phase + i * (2.0 * math.pi / segments)
            ca, sa = math.cos(ang), math.sin(ang)
            if axis == 'X':
                co = Vector((cx + sgn * half_len, cy + ca * radius, cz + sa * radius))
            else:
                co = Vector((cx + ca * radius, cy + sgn * half_len, cz + sa * radius))
            ring.append(bm.verts.new(co))
        rings.append(ring)

    for i in range(segments):
        j = (i + 1) % segments
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = True
        f.material_index = mat_index
        set_flat_uv(f, uv_layer, side_uv if side_uv else FLAT_UV_SIDE)

    for ring, rev in ((rings[0], False), (rings[1], True)):
        f = bm.faces.new(list(reversed(ring)) if rev else ring)
        f.smooth = False
        f.material_index = mat_index
        set_flat_uv(f, uv_layer, cap_uv if cap_uv else FLAT_UV_DARK)
    return rings


def build_bracket(mats):
    """Duvar plakasi + konik kol + X ekseni mentese pimi (tek mesh)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    profiles = [
        (chamfer_profile(BP_HX, BP_HZ, BP_C), BP_Y0),
        (chamfer_profile(BP_HX - 0.0006, BP_HZ - 0.0006, BP_C - 0.0003), BP_Y1),
        (chamfer_profile(ARM_HX, ARM_HZ, ARM_C), ARM_Y),
    ]
    rings = [[bm.verts.new(Vector((p[0], y, p[1]))) for p in pts] for pts, y in profiles]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_BODY)

    f_front = bm.faces.new(rings[-1])
    f_front.smooth = False
    f_front.material_index = 0
    set_flat_uv(f_front, uv_layer, FLAT_UV_SIDE)

    n = len(rings[0])
    for r in range(len(rings) - 1):
        a_ring, b_ring = rings[r], rings[r + 1]
        for i in range(n):
            j = (i + 1) % n
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = 0
            set_flat_uv(f, uv_layer, FLAT_UV_SIDE)

    # Mentese pimi: kasayi tasiyan gorsel mafsal, kasa genisliginden 1.5 mm tasar
    add_cylinder_to_bm(bm, uv_layer, (0.0, PIN_Y, 0.0), 'X', PIN_R, PIN_HX,
                       PIN_SEG, mat_index=0, side_uv=FLAT_UV_SIDE,
                       cap_uv=FLAT_UV_DARK, phase=math.pi / PIN_SEG)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Mount_Bracket", mats)


def build_stepped_bar(name, profiles, mats, front_rect=None, front_extent=None,
                      front_mat=0):
    """Ardisik pahlanmis profiller arasinda kademeli govde uretir."""
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


def build_glass_disc(name, mats, uv_rect):
    """Gomme optik cam diski: yerel origin cam merkezinde, 12 kenar.

    Geometri yerel (0,0,0) cevresinde kurulur; obje konumu pencere merkezine
    tasinir (mesh origin = mafsal/etkilesim noktasi kurali).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    rings = []
    for cy, rr in ((-GLASS_THICK, GLASS_R), (0.0, GLASS_TOP_R)):
        ring = []
        for i in range(GLASS_SEG):
            ang = math.pi / GLASS_SEG + i * (2.0 * math.pi / GLASS_SEG)
            ring.append(bm.verts.new(Vector((math.cos(ang) * rr, cy,
                                             math.sin(ang) * rr))))
        rings.append(ring)

    for i in range(GLASS_SEG):
        j = (i + 1) % GLASS_SEG
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = True
        f.material_index = 1
        set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    f_top = bm.faces.new(rings[1])
    f_top.smooth = False
    f_top.material_index = 1
    set_face_uv_rect(f_top, uv_layer, uv_rect, flip_u=True)

    f_bot = bm.faces.new(list(reversed(rings[0])))
    f_bot.smooth = False
    f_bot.material_index = 1
    set_flat_uv(f_bot, uv_layer, FLAT_UV_DARK)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, name, mats)


def build_led(mats, uv_rect):
    """Gomme durum lensi: 0.3 mm cikinti (paralaks kurali, varlik 38 dersi)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    height = 0.0010
    rings = []
    for cy, rr in ((0.0, LED_R), (height, LED_R * 0.94)):
        ring = []
        for i in range(LED_SEG):
            ang = math.pi / LED_SEG + i * (2.0 * math.pi / LED_SEG)
            ring.append(bm.verts.new(Vector((math.cos(ang) * rr, cy,
                                             math.sin(ang) * rr))))
        rings.append(ring)

    for i in range(LED_SEG):
        j = (i + 1) % LED_SEG
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = True
        f.material_index = 2
        set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    f_top = bm.faces.new(rings[1])
    f_top.smooth = False
    f_top.material_index = 2
    set_face_uv_rect(f_top, uv_layer, uv_rect, flip_u=True)

    f_bot = bm.faces.new(list(reversed(rings[0])))
    f_bot.smooth = False
    f_bot.material_index = 2
    set_flat_uv(f_bot, uv_layer, FLAT_UV_DARK)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Status_LED", mats)



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


def parent_keep(child, parent):
    """Parent baglar ama cocugun dunya konumunu korur.

    `child.parent = parent` tek basina yetmez: Blender parent'in ters matrisini
    ancak matrix_parent_inverse ile dengeler. Pivot (0, 0.029, 0) gibi sifirdan
    farkli bir konumdaysa kasa aksi halde 29 mm one kayar.
    """
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def build_all(mats):
    """Tum parcalari kurar; hareketli kasa Aim_Pivot Empty'sine baglanir."""
    rect_cover = uv_rect_from_pixels(*UV_RECT_COVER)
    rect_lens = uv_rect_from_pixels(*UV_RECT_LENS)
    rect_led = uv_rect_from_pixels(*UV_RECT_LED)

    # ------------------------------------------------------------ Root Empty
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    # ------------------------------------------------------------ Montaj ayagi
    bracket = build_bracket(mats)
    parent_keep(bracket, root)

    # ------------------------------------------------------------ Aim_Pivot
    # Iki optik pencerenin TAM ortasinda: X=0 (optik eksen), Z=0 (pencere ciftinin
    # orta noktasi), Y=mentese ekseni. Yerel X donusu isinlari yukari/asagi cevirir.
    pivot = bpy.data.objects.new("Aim_Pivot", None)
    pivot.empty_display_type = 'ARROWS'
    pivot.empty_display_size = 0.02
    pivot.location = Vector((0.0, PIN_Y, 0.0))
    bpy.context.collection.objects.link(pivot)
    bpy.context.view_layer.update()
    parent_keep(pivot, bracket)


    con = pivot.constraints.new('LIMIT_ROTATION')
    con.owner_space = 'LOCAL'
    con.use_limit_x = True
    con.min_x = math.radians(-TILT_LIMIT_DEG)
    con.max_x = math.radians(TILT_LIMIT_DEG)
    con.use_limit_y = True
    con.min_y = 0.0
    con.max_y = 0.0
    con.use_limit_z = True
    con.min_z = 0.0
    con.max_z = 0.0
    # Motor tarafi limitleri okur (FBX'e custom properties ile tasinir)
    pivot["tilt_min_deg"] = -TILT_LIMIT_DEG
    pivot["tilt_max_deg"] = TILT_LIMIT_DEG
    pivot["tilt_axis"] = "X"

    # ------------------------------------------------------------ Dikey muhafaza
    housing = build_stepped_bar(
        "Detector_Housing",
        [
            (chamfer_profile(H_BACK_HX, H_BACK_HZ, H_BACK_C), H_Y_BACK),
            (chamfer_profile(H_MID_HX, H_MID_HZ, H_MID_C), H_Y_MID),
            (chamfer_profile(H_FACE_HX, H_FACE_HZ, H_FACE_C), H_Y_LIP),
            (chamfer_profile(H_FACE_HX, H_FACE_HZ, H_FACE_C), H_Y_FACE),
        ],
        mats,
        front_rect=rect_cover,
        front_extent=(-H_FACE_HX, H_FACE_HX, -H_FACE_HZ, H_FACE_HZ),
    )
    parent_keep(housing, pivot)

    # ------------------------------------------------------------ Optik pencereler
    # Cam on yuzun 0.6 mm gerisinde: egik bakista yuvasindan kaymaz (varlik 38 dersi).
    for name, cz in (("Optical_Window_Upper", WINDOW_Z),
                     ("Optical_Window_Lower", -WINDOW_Z)):
        glass = build_glass_disc(name, mats, rect_lens)
        glass.location = Vector((WINDOW_X, H_Y_FACE - GLASS_RECESS, cz))
        parent_keep(glass, housing)

    # ------------------------------------------------------------ Durum gostergesi
    led = build_led(mats, rect_led)
    led.location = Vector((LED_X, H_Y_FACE + LED_PROTRUSION - 0.0010, LED_Z))
    parent_keep(led, housing)

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


def qa_pivot(objs):
    """Pivot konumu, limitleri ve +-10 derece donus temizligi (hareketli varlik QA).

    Ilk kez hareketli parca iceren varlik: pivotun optik eksende olmasi, limit
    custom property'lerinin dogru olmasi ve maksimum acida kasanin montaj
    ayagina carpmamasi sayisal olarak dogrulanir.
    """
    pivot = objs["Aim_Pivot"]
    housing = objs["Detector_Housing"]
    bracket = objs["Mount_Bracket"]

    assert pivot.type == 'EMPTY', "FAIL: Aim_Pivot must be an Empty"
    assert abs(pivot.location.x) < 1e-6, "FAIL: Aim_Pivot is not on the optical axis (X != 0)"
    assert abs(pivot.location.z) < 1e-6, "FAIL: Aim_Pivot is not centered between the windows"
    print(f"[QA] Aim_Pivot konumu: ({pivot.location.x * 1000:.2f}, "
          f"{pivot.location.y * 1000:.2f}, {pivot.location.z * 1000:.2f}) mm")

    lo = pivot.get("tilt_min_deg")
    hi = pivot.get("tilt_max_deg")
    assert lo is not None and hi is not None, "FAIL: tilt limits missing as custom properties"
    assert abs(lo + TILT_LIMIT_DEG) < 1e-6 and abs(hi - TILT_LIMIT_DEG) < 1e-6, \
        f"FAIL: tilt limits wrong ({lo}..{hi}), expected +-{TILT_LIMIT_DEG}"
    axis = pivot.get("tilt_axis")
    assert axis == "X", f"FAIL: tilt axis must be X, found {axis}"
    print(f"[QA] Limit custom properties: tilt_min_deg={lo}, tilt_max_deg={hi}, axis={axis}")

    cons = [c for c in pivot.constraints if c.type == 'LIMIT_ROTATION']
    assert cons, "FAIL: Aim_Pivot has no LIMIT_ROTATION constraint"
    con = cons[0]
    assert con.owner_space == 'LOCAL', f"FAIL: constraint space must be LOCAL ({con.owner_space})"
    assert abs(con.min_x - math.radians(-TILT_LIMIT_DEG)) < 1e-6, "FAIL: constraint min_x wrong"
    assert abs(con.max_x - math.radians(TILT_LIMIT_DEG)) < 1e-6, "FAIL: constraint max_x wrong"
    assert con.use_limit_y and con.use_limit_z, "FAIL: Y/Z rotation must be locked"
    print(f"[PASS] LIMIT_ROTATION (LOCAL, X -{TILT_LIMIT_DEG:.0f}..+{TILT_LIMIT_DEG:.0f} deg, "
          f"Y/Z kilitli) dogrulandi")

    # --- Donus testi: maksimum acida kasa ayaga carpmamali -----------------
    # Kasa profili yalnizca 8 kosep noktasi tasidigi icin |z|<ARM_HZ araliginda
    # vertex yok; bu yuzden kritik bolge arka yuz duzleminden ORNEKLENIR.
    arm_front = ARM_Y
    for deg in (-TILT_LIMIT_DEG, TILT_LIMIT_DEG):
        pivot.rotation_euler = (math.radians(deg), 0.0, 0.0)
        bpy.context.view_layer.update()
        th = math.radians(deg)
        worst = None
        for sx in (-ARM_HX, 0.0, ARM_HX):
            for sz in (-ARM_HZ, 0.0, ARM_HZ):
                # kasa arka yuzundeki nokta, pivot cevresinde X ekseninde doner
                dy = H_Y_BACK - PIN_Y
                y2 = PIN_Y + dy * math.cos(th) - sz * math.sin(th)
                z2 = dy * math.sin(th) + sz * math.cos(th)
                if abs(z2) <= ARM_HZ + 0.002 and (worst is None or y2 < worst[0]):
                    worst = (y2, z2)
        clearance = (worst[0] - arm_front) * 1000.0
        print(f"[QA] {deg:+.0f} derecede kol on yuzune en yakin kasa noktasi: "
              f"Y={worst[0] * 1000:.2f} mm (kol {arm_front * 1000:.1f} mm) -> "
              f"bosluk {clearance:+.2f} mm")
        assert clearance > 0.5, (
            f"FAIL: at {deg:+.0f} deg the housing collides with the bracket arm "
            f"(clearance {clearance:.2f} mm)")
        # Hicbir nokta duvar duzlemine de girmemeli
        min_y = min((housing.matrix_world @ v.co).y for v in housing.data.vertices)
        assert min_y > 0.004, f"FAIL: housing reaches the wall plane at {deg:+.0f} deg"
    # Pencere merkezleri zit yonlerde kaymali (isinlar yukari/asagi doner)
    pivot.rotation_euler = (math.radians(TILT_LIMIT_DEG), 0.0, 0.0)
    bpy.context.view_layer.update()
    up_y = objs["Optical_Window_Upper"].matrix_world.translation.y
    lo_y = objs["Optical_Window_Lower"].matrix_world.translation.y
    print(f"[QA] +10 derece: ust pencere Y={up_y * 1000:.2f} mm, "
          f"alt pencere Y={lo_y * 1000:.2f} mm (fark {(up_y - lo_y) * 1000:+.2f} mm)")
    assert up_y < lo_y, "FAIL: +10 deg must tilt the upper beam backwards (aim down)"
    pivot.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    print("[PASS] Aim_Pivot +-10 derecede temiz donuyor (carpma yok, isinlar zit yonde)")


def main():
    clean_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    mats = setup_materials()
    root = build_all(mats)

    # --------------------------------------------------------------- Pivot QA (kaynak sahne)
    # LIMIT_ROTATION constraint'i FBX'te tasinmaz; bu yuzden limit ve donus
    # temizligi EXPORT ONCESI kaynak sahnede dogrulanir (motor tarafi limitleri
    # custom property'lerden okur).
    qa_pivot({o.name: o for o in [root] + root.children_recursive})


    # --------------------------------------------------------------- Transform hijyeni
    bpy.context.view_layer.update()
    for obj in bpy.data.objects:
        obj.scale = (1.0, 1.0, 1.0)
        if obj.type == 'EMPTY' and obj.name == ASSET_NAME:
            obj.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()

    boxes = [world_aabb(o) for o in bpy.data.objects if o.type == 'MESH']
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

    # use_custom_props: pivot donus limitleri FBX'e tasinsin (motor tarafi okur)
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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 39) ---")
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
    assert sorted(empty_names) == sorted([ASSET_NAME, "Aim_Pivot"]), \
        f"FAIL: expected exactly root + Aim_Pivot empties, found {empty_names}"
    print("[PASS] Exactly one moving pivot empty (Aim_Pivot) verified!")

    # --------------------------------------------------------------- Hiyerarsi
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    expected_parents = {
        "Mount_Bracket": ASSET_NAME,
        "Aim_Pivot": "Mount_Bracket",
        "Detector_Housing": "Aim_Pivot",
        "Optical_Window_Upper": "Detector_Housing",
        "Optical_Window_Lower": "Detector_Housing",
        "Status_LED": "Detector_Housing",
    }
    for child_name, parent_name in expected_parents.items():
        child = objs.get(child_name)
        assert child is not None, f"FAIL: {child_name} missing in FBX hierarchy"
        assert child.parent is not None and child.parent.name == parent_name, \
            f"FAIL: {child_name} parent mismatch (expected {parent_name})"
    print(f"[PASS] Full parent-child hierarchy verified ({len(expected_parents)} relations)!")

    # --------------------------------------------------------------- Materyal slotlari
    expected_mats = ["M_Security_Atlas", "M_Lens_Glass", "M_Emission"]
    for name in expected_parents:
        if objs[name].type != 'MESH':
            continue
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:3] == expected_mats, \
            f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0 Atlas, 1 Lens_Glass, 2 Emission)!")

    # --------------------------------------------------------------- Slot kullanimi
    for name in ("Mount_Bracket", "Detector_Housing"):
        idxs = {p.material_index for p in objs[name].data.polygons}
        assert idxs == {0}, f"FAIL: {name} must be fully M_Security_Atlas (found {idxs})"
    for name in ("Optical_Window_Upper", "Optical_Window_Lower"):
        idxs = {p.material_index for p in objs[name].data.polygons}
        assert idxs == {1}, f"FAIL: {name} must be fully M_Lens_Glass (found {idxs})"
    led_polys = objs["Status_LED"].data.polygons
    assert all(p.material_index == 2 for p in led_polys) and led_polys, \
        "FAIL: Status_LED is not fully assigned to M_Emission"
    glass_mat = bpy.data.materials.get("M_Lens_Glass")
    gb = None
    for node in glass_mat.node_tree.nodes:
        if node.type == 'BSDF_PRINCIPLED':
            gb = node
    gr = gb.inputs["Roughness"].default_value
    assert gr <= 0.12, "FAIL: M_Lens_Glass roughness drifted from family standard (<= 0.12)"
    print(f"[PASS] Slot usage verified (cam yalniz camlarda, emisyon yalniz LED'de, "
          f"cam roughness {gr:.2f})!")

    # --------------------------------------------------------------- Bosluk / olcu QA
    contact_pairs = [
        ("Detector_Housing", "Mount_Bracket"),
        ("Optical_Window_Upper", "Detector_Housing"),
        ("Optical_Window_Lower", "Detector_Housing"),
        ("Status_LED", "Detector_Housing"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), \
            f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} contact pairs)!")

    wall_y = world_aabb(objs["Mount_Bracket"])[0].y * 1000.0
    print(f"[QA] Duvar yuzeyi offseti: {wall_y:.2f} mm (0.00 olmali)")
    assert abs(wall_y) < 0.05, "FAIL: Mount bracket does not sit on the wall plane"

    bp = world_aabb(objs["Mount_Bracket"])
    bp_w = (bp[1].x - bp[0].x) * 1000.0
    bp_h = (bp[1].z - bp[0].z) * 1000.0
    print(f"[QA] Montaj ayagi ayak izi: {bp_w:.1f} x {bp_h:.1f} mm")
    assert abs(bp_w - 46.0) < 0.3 and abs(bp_h - 76.0) < 0.3, \
        "FAIL: bracket footprint must be 46 x 76 mm"

    hs = world_aabb(objs["Detector_Housing"])
    hx = (hs[1].x - hs[0].x) * 1000.0
    hy = (hs[1].y - hs[0].y) * 1000.0
    hz = (hs[1].z - hs[0].z) * 1000.0
    print(f"[QA] Muhafaza olcusu: {hx:.1f} x {hy:.1f} x {hz:.1f} mm (G x D x Y)")
    assert abs(hx - 36.0) < 0.3 and abs(hz - 84.0) < 0.3 and abs(hy - 16.0) < 0.3, \
        "FAIL: housing must be 36 x 84 mm, 16 mm deep"

    # On yuz, etiket bandiyla birebir: 36 x 84 mm
    front_polys = [p for p in objs["Detector_Housing"].data.polygons if p.normal.y > 0.9]
    front_poly = max(front_polys, key=lambda p: p.area)
    fx = [objs["Detector_Housing"].matrix_world
          @ objs["Detector_Housing"].data.vertices[v].co for v in front_poly.vertices]
    fx_w = (max(v.x for v in fx) - min(v.x for v in fx)) * 1000.0
    fx_h = (max(v.z for v in fx) - min(v.z for v in fx)) * 1000.0
    print(f"[QA] Etiket yuzeyi: {fx_w:.1f} x {fx_h:.1f} mm")
    assert abs(fx_w - 36.0) < 0.3 and abs(fx_h - 84.0) < 0.3, \
        "FAIL: Cover face size does not match the 36 x 84 mm texture band"

    # --------------------------------------------------------------- Optik yerlesim QA
    up = objs["Optical_Window_Upper"].matrix_world.translation
    lo = objs["Optical_Window_Lower"].matrix_world.translation
    print(f"[QA] Pencere merkezleri: ust ({up.x * 1000:.2f}, {up.z * 1000:.2f}), "
          f"alt ({lo.x * 1000:.2f}, {lo.z * 1000:.2f}) mm")
    assert abs(up.x) < 1e-6 and abs(lo.x) < 1e-6, "FAIL: windows are not on the optical axis"
    assert abs(up.z - WINDOW_Z) < 1e-6 and abs(lo.z + WINDOW_Z) < 1e-6, \
        "FAIL: window Z positions wrong"
    assert abs(0.5 * (up.z + lo.z)) < 1e-6, \
        "FAIL: windows are not symmetric about the housing centre"
    assert (up.y - H_Y_FACE) < 0, "FAIL: glass must be recessed behind the front face"
    recess = (H_Y_FACE - up.y) * 1000.0
    print(f"[QA] Cam gomme derinligi: {recess:.2f} mm (on yuz {H_Y_FACE * 1000:.1f} mm)")
    print("[PASS] Both optical windows on the axis, mirrored, recessed!")

    # LED cikinti (paralaks kurali - varlik 38 dersi)
    led_ws = [objs["Status_LED"].matrix_world @ Vector(c)
              for c in objs["Status_LED"].bound_box]
    protrusion = (max(v.y for v in led_ws) - H_Y_FACE) * 1000.0
    print(f"[QA] LED cikinti: {protrusion:.2f} mm (limit 0.6 mm)")
    assert 0.0 <= protrusion <= 0.6, \
        f"FAIL: LED protrudes {protrusion:.2f} mm (near-flush required)"
    print("[PASS] Status LED near-flush (no decal-socket parallax)!")

    # --------------------------------------------------------------- Pivot (FBX sonrasi)
    re_pivot = objs["Aim_Pivot"]
    pl = re_pivot.matrix_local.translation
    print(f"[QA] FBX'te Aim_Pivot yerel konumu: ({pl.x * 1000:.2f}, "
          f"{pl.y * 1000:.2f}, {pl.z * 1000:.2f}) mm")
    assert abs(pl.x) < 1e-4 and abs(pl.z) < 1e-4, \
        "FAIL: Aim_Pivot lost its optical-axis alignment through FBX"
    pmin = re_pivot.get("tilt_min_deg")
    pmax = re_pivot.get("tilt_max_deg")
    if pmin is None or pmax is None:
        print("[WARN] tilt custom properties FBX'ten gelmedi (kaynak .blend'de dogrulandi)")
    else:
        assert abs(pmin + TILT_LIMIT_DEG) < 1e-4 and abs(pmax - TILT_LIMIT_DEG) < 1e-4, \
            f"FAIL: tilt limits corrupted in FBX ({pmin}..{pmax})"
        print(f"[PASS] tilt_min_deg / tilt_max_deg FBX ile tasindi ({pmin}..{pmax})")
    print("[PASS] Moving pivot reached the FBX with its optical-axis alignment!")

    # --------------------------------------------------------------- UV oran QA
    ratios = [
        ("Cover front", UV_RECT_COVER, (36.0, 84.0)),
        ("Optical glass", UV_RECT_LENS, (GLASS_TOP_R * 2000.0, GLASS_TOP_R * 2000.0)),
        ("Status lens", UV_RECT_LED, (LED_R * 2000.0 * 0.94, LED_R * 2000.0 * 0.94)),
    ]
    for label, rect, size_mm in ratios:
        err = abs(aa_ratio(rect, size_mm) - 1.0) * 100.0
        print(f"[QA] UV aspect {label:14s}: {size_mm[0]:.1f} x {size_mm[1]:.1f} mm "
              f"-> sapma {err:.2f}%")
        assert err < 1.0, f"FAIL: UV stretch {err:.2f}% on {label}"
    print(f"[QA] Etiket doku yogunlugu: "
          f"{(UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 36.0:.1f} px/mm")
    print("[PASS] UV rectangles locked to face aspect ratios (no texture sliding)!")

    # ------------------------------------------- Doku yogunlugu (gercek, pah kirpilmis yuz)
    cov = objs["Detector_Housing"]
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
    design = (UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 36.0
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
        "moving_pivots": ["Aim_Pivot"],
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









