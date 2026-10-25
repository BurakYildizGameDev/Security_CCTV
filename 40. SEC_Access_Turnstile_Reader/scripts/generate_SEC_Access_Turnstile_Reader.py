"""
=============================================================================
Security CCTV Asset Production Suite - Asset 40
Asset Name: SEC_Access_Turnstile_Reader (Turnike Kart Okuyucu)
Triangle Budget: <= 300 tris      (hedef: 264 tris)
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Emission , Slot 2 -> M_Metal

ASSET (Master Prompt 40):
    - Egimli terminal govdesi, RFID yuzeyi, kucuk LED halkasi ve metal direk
      montaj kelepcesi.

Hierarchy (Master Prompt):
    SEC_Access_Turnstile_Reader (Root Empty @ 0,0,0)
     ├── Pole_Clamp     (Mesh, Slot 2 M_Metal - kelepce halkasi + boyun + civata)
     └── Reader_Housing (Mesh - 28 derece EGIMLI terminal govdesi; on yuz 58 x 74 mm)
          ├── RFID_Area  (Mesh, Slot 0 M_Security_Atlas - 42 x 34 mm RFID plakasi)
          └── LED_Ring   (Mesh, Slot 1 M_Emission - Ø14/Ø10.4 mm halka)
    Sabit pivot (hareketli parca yok) -> yalnizca Root Empty.

EGIM STRATEJISI (kritik):
    Govde geometrisi ve UV'ler ONCE egimsiz yerel uzayda kurulur, sonra tum
    vertex'ler X ekseni cevresinde 28 derece dondurulur. Boylece UV'ler
    "acilmis" yuzey olarak dogru kalir ve obje transform'u temiz (identity)
    olur - uygulanmamis rotation kalmaz.

Calistirma:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python scripts/generate_SEC_Access_Turnstile_Reader.py
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import math
import os
import json

ASSET_NAME = "SEC_Access_Turnstile_Reader"
TRIS_BUDGET = 300

# ---------------------------------------------------------------- Geometri (m)
TILT = math.radians(28.0)                 # govde egimi
ROT = Matrix.Rotation(TILT, 3, 'X')       # +Y -> (0, cos, sin): yuz yukari bakar
ROT_T = ROT.transposed()

# Direk kelepcesi (dikey direk, Z ekseni)
POLE_R_IN, POLE_R_OUT = 0.0300, 0.0360    # Ø60 / Ø72 mm
CLAMP_HZ = 0.0100                         # 20 mm yukseklik
CLAMP_SEG = 12
SCREW_R, SCREW_H = 0.0040, 0.0026         # M8 sikma civatasi
BOSS_HX, BOSS_HZ = 0.0140, 0.0260
BOSS_Y0, BOSS_Y1 = 0.0260, 0.0480
BOSS_Z0, BOSS_Z1 = 0.0000, 0.0520

# Egimli terminal govdesi (yerel uzay: +Y derinlik, yuz y=D'de)
D = 0.0240                                # 24 mm derinlik
H_BACK_HX, H_BACK_HZ, H_BACK_C = 0.0230, 0.0310, 0.0035
H_MID_HX, H_MID_HZ, H_MID_C = 0.0270, 0.0350, 0.0040
H_FACE_HX, H_FACE_HZ, H_FACE_C = 0.0290, 0.0370, 0.0040
ORIGIN = Vector((0.0, 0.0420, 0.0450))    # arka yuz merkezinin dunya konumu

COVER_HALF_X, COVER_HALF_Z = H_FACE_HX, H_FACE_HZ      # 58 x 74 mm

# RFID plakasi (yuz yerel uzay)
RFID_X, RFID_Z = 0.0, -0.0140
RFID_HX, RFID_HZ, RFID_C = 0.0210, 0.0170, 0.0030
RFID_PROUD = 0.0004

# LED halkasi (yuz yerel uzay)
LED_X, LED_Z = 0.0160, 0.0160
LED_R_OUT, LED_R_IN = 0.0070, 0.0052
LED_PROUD = 0.0003
LED_SEG = 8

# ---------------------------------------------------------------- Doku atlasi
ATLAS_W, ATLAS_H = 2048, 2048
UV_RECT_COVER = (32, 32, 1308, 1660)      # 1276 x 1628 px -> 58 x 74 mm
UV_RECT_RFID = (1330, 32, 2030, 599)      # 700 x 567 px  -> RFID plaka
UV_RECT_LED = (1330, 630, 1630, 930)      # 300 x 300 px  -> LED halkasi
PIX_FLAT_BODY = (1700, 700)
PIX_FLAT_SIDE = (1900, 700)
PIX_FLAT_DARK = (1700, 950)
PIX_FLAT_METAL = (1900, 950)


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


def set_radial_uv(face, uv_layer, rect, cx, cz, r_out):
    """Daire sekilli yuzu radyal haritalar (LED halkasi emission dokusu)."""
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


def tilt_apply(bm):
    """Yerel uzaydaki govdeyi 28 derece egip dunya konumuna tasir."""
    for v in bm.verts:
        v.co = ORIGIN + ROT @ v.co


def setup_materials():
    """Slot 0: M_Security_Atlas, Slot 1: M_Emission, Slot 2: M_Metal."""
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

    # Slot 1: M_Emission - LED halkasi
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
        tex_e.location = (-420, -140)
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
    bsdf_e.inputs["Roughness"].default_value = 0.20
    mat_em.diffuse_color = em_col

    # Slot 2: M_Metal (asset 33/36/38 aile standardi)
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    mbsdf = mat_metal.node_tree.nodes.get("Principled BSDF")
    mbsdf.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    mbsdf.inputs["Metallic"].default_value = 0.95
    mbsdf.inputs["Roughness"].default_value = 0.22
    mat_metal.diffuse_color = (0.75, 0.78, 0.82, 1.0)

    return [mat_atlas, mat_em, mat_metal]


def build_clamp(mats):
    """Direk kelepcesi: 12 kenarli halka + boyun blogu + 6 kenar sikma civatasi."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    rings = {}
    for z in (-CLAMP_HZ, CLAMP_HZ):
        for r in (POLE_R_OUT, POLE_R_IN):
            ring = []
            for i in range(CLAMP_SEG):
                # faz 0: bir kose X eksenine oturur -> gercek dis cap 72 mm olur
                ang = i * (2.0 * math.pi / CLAMP_SEG)
                ring.append(bm.verts.new(Vector((math.cos(ang) * r,
                                                 math.sin(ang) * r, z))))
            rings[(z, r)] = ring

    for i in range(CLAMP_SEG):
        j = (i + 1) % CLAMP_SEG
        for (za, ra, zb, rb) in ((-CLAMP_HZ, POLE_R_OUT, CLAMP_HZ, POLE_R_OUT),
                                 (-CLAMP_HZ, POLE_R_IN, CLAMP_HZ, POLE_R_IN),
                                 (CLAMP_HZ, POLE_R_IN, CLAMP_HZ, POLE_R_OUT),
                                 (-CLAMP_HZ, POLE_R_OUT, -CLAMP_HZ, POLE_R_IN)):
            a = rings[(za, ra)]
            b = rings[(zb, rb)]
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            f.smooth = True
            f.material_index = 2
            set_flat_uv(f, uv_layer, FLAT_UV_METAL)

    # --- Boyun blogu (kelepceden govdeye) ----------------------------------
    v = {}
    for sx in (-BOSS_HX, BOSS_HX):
        for sy in (BOSS_Y0, BOSS_Y1):
            for sz in (BOSS_Z0, BOSS_Z1):
                v[(sx, sy, sz)] = bm.verts.new(Vector((sx, sy, sz)))
    quads = (
        ((-BOSS_HX, BOSS_Y0, BOSS_Z0), (BOSS_HX, BOSS_Y0, BOSS_Z0),
         (BOSS_HX, BOSS_Y0, BOSS_Z1), (-BOSS_HX, BOSS_Y0, BOSS_Z1)),
        ((-BOSS_HX, BOSS_Y1, BOSS_Z0), (-BOSS_HX, BOSS_Y1, BOSS_Z1),
         (BOSS_HX, BOSS_Y1, BOSS_Z1), (BOSS_HX, BOSS_Y1, BOSS_Z0)),
        ((-BOSS_HX, BOSS_Y0, BOSS_Z0), (-BOSS_HX, BOSS_Y1, BOSS_Z0),
         (-BOSS_HX, BOSS_Y1, BOSS_Z1), (-BOSS_HX, BOSS_Y0, BOSS_Z1)),
        ((BOSS_HX, BOSS_Y0, BOSS_Z0), (BOSS_HX, BOSS_Y0, BOSS_Z1),
         (BOSS_HX, BOSS_Y1, BOSS_Z1), (BOSS_HX, BOSS_Y1, BOSS_Z0)),
        ((-BOSS_HX, BOSS_Y0, BOSS_Z0), (BOSS_HX, BOSS_Y0, BOSS_Z0),
         (BOSS_HX, BOSS_Y1, BOSS_Z0), (-BOSS_HX, BOSS_Y1, BOSS_Z0)),
        ((-BOSS_HX, BOSS_Y0, BOSS_Z1), (-BOSS_HX, BOSS_Y1, BOSS_Z1),
         (BOSS_HX, BOSS_Y1, BOSS_Z1), (BOSS_HX, BOSS_Y0, BOSS_Z1)),
    )
    for quad in quads:
        f = bm.faces.new([v[k] for k in quad])
        f.smooth = False
        f.material_index = 2
        set_flat_uv(f, uv_layer, FLAT_UV_METAL)

    # --- 6 kenarli sikma civatasi (boynun on yuzunde) ----------------------
    head_y0 = BOSS_Y1 - 0.0002
    hex_rings = []
    for yy, rr in ((head_y0, SCREW_R), (head_y0 + SCREW_H, SCREW_R * 0.84)):
        ring = []
        for i in range(6):
            ang = math.pi / 6.0 + i * (2.0 * math.pi / 6.0)
            ring.append(bm.verts.new(Vector((math.cos(ang) * rr, yy,
                                             0.0260 + math.sin(ang) * rr))))
        hex_rings.append(ring)
    for i in range(6):
        j = (i + 1) % 6
        f = bm.faces.new((hex_rings[0][i], hex_rings[0][j],
                          hex_rings[1][j], hex_rings[1][i]))
        f.smooth = True
        f.material_index = 2
        set_flat_uv(f, uv_layer, FLAT_UV_METAL)
    for ring, rev in ((hex_rings[0], True), (hex_rings[1], False)):
        f = bm.faces.new(list(reversed(ring)) if rev else ring)
        f.smooth = False
        f.material_index = 2
        set_flat_uv(f, uv_layer, FLAT_UV_METAL)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Pole_Clamp", mats)


def build_housing(mats):
    """28 derece egimli terminal govdesi: egimsiz kurulur, sonra dondurulur."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    profiles = [
        (chamfer_profile(H_BACK_HX, H_BACK_HZ, H_BACK_C), 0.0),
        (chamfer_profile(H_MID_HX, H_MID_HZ, H_MID_C), D - 0.0040),
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

    tilt_apply(bm)          # UV'ler sakli; simdi egimi ve konumu uygula
    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "Reader_Housing", mats)


def build_rfid_plate(mats):
    """RFID yuzeyi: yuzden 0.4 mm kabarik ince plaka (paralaks siniri icinde)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    prof = chamfer_profile(RFID_HX, RFID_HZ, RFID_C)
    rings = [[bm.verts.new(Vector((RFID_X + p[0], yy, RFID_Z + p[1]))) for p in prof]
             for yy in (D - 0.0008, D + RFID_PROUD)]

    f_back = bm.faces.new(list(reversed(rings[0])))
    f_back.smooth = False
    f_back.material_index = 0
    set_flat_uv(f_back, uv_layer, FLAT_UV_DARK)

    f_front = bm.faces.new(rings[1])
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, uv_rect_from_pixels(*UV_RECT_RFID),
                     flip_u=True,
                     extent=(RFID_X - RFID_HX, RFID_X + RFID_HX,
                             RFID_Z - RFID_HZ, RFID_Z + RFID_HZ))

    n = len(prof)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((rings[0][i], rings[0][j], rings[1][j], rings[1][i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    tilt_apply(bm)
    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "RFID_Area", mats)


def build_led_ring(mats):
    """Durum LED halkasi: annulus, yuzden 0.3 mm kabarik, radyal emission UV."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    rings = {}
    for yy in (D - 0.0005, D + LED_PROUD):
        for rr in (LED_R_OUT, LED_R_IN):
            ring = []
            for i in range(LED_SEG):
                ang = math.pi / LED_SEG + i * (2.0 * math.pi / LED_SEG)
                ring.append(bm.verts.new(Vector((LED_X + math.cos(ang) * rr,
                                                 yy,
                                                 LED_Z + math.sin(ang) * rr))))
            rings[(yy, rr)] = ring

    led_rect = uv_rect_from_pixels(*UV_RECT_LED)
    for i in range(LED_SEG):
        j = (i + 1) % LED_SEG
        for (ya, ra, yb, rb) in ((D - 0.0005, LED_R_OUT, D + LED_PROUD, LED_R_OUT),
                                 (D - 0.0005, LED_R_IN, D + LED_PROUD, LED_R_IN)):
            a, b = rings[(ya, ra)], rings[(yb, rb)]
            f = bm.faces.new((a[i], a[j], b[j], b[i]))
            f.smooth = True
            f.material_index = 1
            set_flat_uv(f, uv_layer, FLAT_UV_DARK)
        for yy in (D + LED_PROUD, D - 0.0005):
            a_out = rings[(yy, LED_R_OUT)]
            a_in = rings[(yy, LED_R_IN)]
            f = bm.faces.new((a_in[i], a_in[j], a_out[j], a_out[i]))
            f.smooth = False
            f.material_index = 1
            set_radial_uv(f, uv_layer, led_rect, LED_X, LED_Z, LED_R_OUT)

    tilt_apply(bm)
    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, "LED_Ring", mats)


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


def front_face_normal():
    """Egimli on yuzun beklenen dunya normali."""
    return ROT @ Vector((0.0, 1.0, 0.0))


def build_all(mats):
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    clamp = build_clamp(mats)
    clamp.parent = root

    housing = build_housing(mats)
    housing.parent = root

    rfid = build_rfid_plate(mats)
    rfid.parent = housing

    led = build_led_ring(mats)
    led.parent = housing

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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 40) ---")
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
        "Pole_Clamp": ASSET_NAME,
        "Reader_Housing": ASSET_NAME,
        "RFID_Area": "Reader_Housing",
        "LED_Ring": "Reader_Housing",
    }
    for child_name, parent_name in expected_parents.items():
        child = objs.get(child_name)
        assert child is not None, f"FAIL: {child_name} missing in FBX hierarchy"
        assert child.parent is not None and child.parent.name == parent_name, \
            f"FAIL: {child_name} parent mismatch (expected {parent_name})"
    print(f"[PASS] Full parent-child hierarchy verified ({len(expected_parents)} relations)!")

    # --------------------------------------------------------------- Materyal slotlari
    expected_mats = ["M_Security_Atlas", "M_Emission", "M_Metal"]
    for name in expected_parents:
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:3] == expected_mats, \
            f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0 Atlas, 1 Emission, 2 Metal)!")

    # --------------------------------------------------------------- Slot kullanimi
    for name in ("Pole_Clamp",):
        idxs = {p.material_index for p in objs[name].data.polygons}
        assert idxs == {2}, f"FAIL: {name} must be fully M_Metal (found {idxs})"
    for name in ("Reader_Housing", "RFID_Area"):
        idxs = {p.material_index for p in objs[name].data.polygons}
        assert idxs == {0}, f"FAIL: {name} must be fully M_Security_Atlas (found {idxs})"
    led_polys = objs["LED_Ring"].data.polygons
    assert all(p.material_index == 1 for p in led_polys) and led_polys, \
        "FAIL: LED_Ring is not fully assigned to M_Emission"
    print(f"[PASS] Slot usage verified (kelepce metal, govde/RFID atlas, "
          f"LED halkasi emisyon - {len(led_polys)} yuz)!")

    # --------------------------------------------------------------- Bosluk / olcu QA
    contact_pairs = [
        ("Pole_Clamp", "Reader_Housing"),
        ("RFID_Area", "Reader_Housing"),
        ("LED_Ring", "Reader_Housing"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), \
            f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} contact pairs)!")

    clamp_box = world_aabb(objs["Pole_Clamp"])
    clamp_w = (clamp_box[1].x - clamp_box[0].x) * 1000.0
    clamp_h = (clamp_box[1].z - clamp_box[0].z) * 1000.0
    print(f"[QA] Kelepce: X ayak izi {clamp_w:.1f} mm, Z yuksekligi {clamp_h:.1f} mm")
    assert abs(clamp_w - POLE_R_OUT * 2000.0) < 0.5, \
        "FAIL: clamp outer diameter must be 72 mm"
    assert abs(clamp_h - (BOSS_Z1 + CLAMP_HZ) * 1000.0) < 0.5, \
        "FAIL: clamp + boss height wrong"
    pole_axis_offset = abs(0.5 * (clamp_box[0].x + clamp_box[1].x)) * 1000.0
    assert pole_axis_offset < 0.05, "FAIL: clamp is not centred on the pole axis (X=0)"

    # --------------------------------------------------------------- Egim QA
    n_exp = front_face_normal()
    front_polys = []
    for p in objs["Reader_Housing"].data.polygons:
        n = (objs["Reader_Housing"].matrix_world.to_3x3() @ p.normal).normalized()
        if n.dot(n_exp) > 0.999:
            front_polys.append(p)
    assert front_polys, "FAIL: tilted front face not found (tilt not applied?)"
    front_poly = max(front_polys, key=lambda p: p.area)
    nrm = front_poly.normal.normalized()
    print(f"[QA] On yuz normali: ({nrm.x:+.3f}, {nrm.y:+.3f}, {nrm.z:+.3f}) "
          f"- beklenen ({n_exp.x:+.3f}, {n_exp.y:+.3f}, {n_exp.z:+.3f})")
    assert abs(nrm.z - math.sin(TILT)) < 0.01 and abs(nrm.y - math.cos(TILT)) < 0.01, \
        "FAIL: front face tilt angle wrong"

    fverts = [objs["Reader_Housing"].matrix_world
              @ objs["Reader_Housing"].data.vertices[v].co for v in front_poly.vertices]
    fx_w = (max(v.x for v in fverts) - min(v.x for v in fverts)) * 1000.0
    # Egitimli duzlemde gercek yukseklik yerel uzaya donusturulerek olculur
    fz = [(-(v.y - ORIGIN.y) * math.sin(TILT) + (v.z - ORIGIN.z) * math.cos(TILT))
          for v in fverts]
    fx_h = (max(fz) - min(fz)) * 1000.0
    print(f"[QA] Etiket yuzeyi (yerel): {fx_w:.1f} x {fx_h:.1f} mm")
    assert abs(fx_w - 58.0) < 0.3 and abs(fx_h - 74.0) < 0.3, \
        "FAIL: Cover face size does not match the 58 x 74 mm texture band"

    face_center = ORIGIN + ROT @ Vector((0.0, D, 0.0))
    print(f"[QA] On yuz merkezi: ({face_center.x * 1000:.1f}, "
          f"{face_center.y * 1000:.1f}, {face_center.z * 1000:.1f}) mm")
    assert face_center.y > 0.040, "FAIL: reading face is not in front of the pole"

    # LED/RFID cikintilari paralaks kuralina uymali (<= 0.5 mm)
    # NOT: bound_box egimli mesh'te eksen hizali kutudur ve kose noktalari
    # gercek geometriden cok disarida kalir; bu yuzden VERTEX'ler kullanilir.
    for name, limit in (("RFID_Area", 0.0005), ("LED_Ring", 0.0004)):
        obj = objs[name]
        ws = [obj.matrix_world @ v.co for v in obj.data.vertices]
        dmax = max((n_exp.dot(v) - n_exp.dot(face_center)) for v in ws)
        print(f"[QA] {name} yuzden cikinti: {dmax * 1000:.2f} mm "
              f"(limit {limit * 1000:.1f} mm)")
        assert 0.0 <= dmax <= limit, \
            f"FAIL: {name} protrudes {dmax * 1000:.2f} mm (paralaks kurali)"
    print("[PASS] RFID plakasi ve LED halkasi yuzeye yakin (paralaks kurali)!")

    # --------------------------------------------------------------- UV oran QA
    ratios = [
        ("Cover front", UV_RECT_COVER, (58.0, 74.0)),
        ("RFID plate", UV_RECT_RFID, (RFID_HX * 2000.0, RFID_HZ * 2000.0)),
        ("LED ring", UV_RECT_LED, (1.0, 1.0)),
    ]
    for label, rect, size_mm in ratios:
        err = abs(aa_ratio(rect, size_mm) - 1.0) * 100.0
        print(f"[QA] UV aspect {label:12s}: {size_mm[0]:.1f} x {size_mm[1]:.1f} mm "
              f"-> sapma {err:.2f}%")
        assert err < 1.0, f"FAIL: UV stretch {err:.2f}% on {label}"
    print(f"[QA] Etiket doku yogunlugu: "
          f"{(UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 58.0:.1f} px/mm")
    print("[PASS] UV rectangles locked to face aspect ratios (no texture sliding)!")

    # ------------------------------------------- Doku yogunlugu (egimli yuz, yerel uzay)
    hou = objs["Reader_Housing"]
    hme, huv = hou.data, hou.data.uv_layers[0]
    mw = hou.matrix_world
    samples = []
    for li in front_poly.loop_indices:
        wco = mw @ hme.vertices[hme.loops[li].vertex_index].co
        loc = ROT_T @ (wco - ORIGIN)          # egimi geri al -> yuz yerel uzayi
        uv = huv.data[li].uv
        samples.append((loc.x, loc.z, uv.x, uv.y))
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
    design = (UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 58.0
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
    print("[PASS] Egimli yuz etiketi 1:1 eslendi (density + alignment)!")

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







