"""
=============================================================================
Security CCTV Asset Production Suite - Asset 35  (REVIZYON v2)
Asset Name: SEC_Sensor_Door_Contact  (Manyetik Kapi Kontagi)
Triangle Budget: <= 180 tris      (v2 gerceklesen: 176 tris)
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Metal

v2'de giderilen sorunlar (kullanici geri bildirimi):
  1) "objeler arasi bosluk"  : Magnet_Block artik duvar duzleminden (Y=0)
     basliyor (once 3 mm havadaydi) ve sensor govdesiyle ayni derinlikte
     bitiyor. Kablo rakoru govde icine 3.4 mm gomuldu. Vida baslari
     plakaya gomuldu.
  2) "yazilar cok kotu"      : Atlas tek kolonlu 992 px bantlara cevrildi
     (22.5 px/mm, once 8.5 px/mm) ve en kucuk punto 17 px (once 9 px).
  3) "obje kaymasi"          : Etiket plakasi ve tum detaylar X=0'a gore
     simetrik; UV dikdortgen oranlari yuzey oranlariyla kilitli
     (max %0.3 sapma) -> doku kaymasi/gerilmesi yok.
  4) "daha detay"            : Yeni Label_Plate (kabartma etiket plakasi),
     konik alti kenar vida baslari, govdeye gomulu rakor, LED lens yuvasi,
     pah yuzeylerinde ayri ton (M_Security_Atlas icinde 2 duz renk).
  5) "referans 33"           : Asset 33'un endustriyel dili (koyu marka
     plakasi + amber aksan, gercek 3D civata baslari, barkod, teknik
     kunye, M_Metal 0.95 metallic / 0.22 roughness).

Hierarchy:
    SEC_Sensor_Door_Contact (Root Empty @ 0,0,0)
     ├── Backplate            (Mesh 68 x 14.7 x 3 mm, arka yuzu teknik etiket)
     │    ├── Screw_Boss_L    (Mesh, M_Metal, konik alti kenar vida)
     │    └── Screw_Boss_R    (Mesh, M_Metal, konik alti kenar vida)
     ├── Sensor_Body          (Mesh 60 x 12 mm taban -> 57.6 x 11 mm on yuz)
     │    ├── Label_Plate     (Mesh, kabartma etiket plakasi 44 x 8.4 x 0.45 mm)
     │    ├── Cable_Gland     (Mesh, M_Metal, -X ucunda alti kenar rakor)
     │    └── Status_LED      (Mesh, etiket plakasi uzerinde alcak lens)
     └── Magnet_Block_Root    (Empty - kapi acilma pivotu, Z ekseni)
          └── Magnet_Block    (Mesh 52 x 11 x 13.4 mm, duvar duzleminden baslar)

Calistirma:
    & "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --python scripts/generate_SEC_Sensor_Door_Contact.py
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Sensor_Door_Contact"
TRIS_BUDGET = 180

# ---------------------------------------------------------------- Geometri (m)
BP_HALF_X, BP_HALF_Z, BP_DEPTH = 0.0340, 0.00735, 0.0030
SENSOR_HALF_X, SENSOR_HALF_Z, SENSOR_FRONT_Y = 0.0300, 0.00600, 0.0138
SENSOR_FRONT_HALF_X, SENSOR_FRONT_HALF_Z = 0.0288, 0.00550
LABEL_HALF_X, LABEL_HALF_Z = 0.0220, 0.00420
LABEL_FRONT_Y = 0.01425
MAGNET_HALF_X, MAGNET_HALF_Z, MAGNET_DEPTH = 0.0260, 0.00550, 0.0134
MAGNET_FRONT_HALF_X, MAGNET_FRONT_HALF_Z = 0.0252, 0.00533
MAGNET_ROOT_X = 0.0620
SCREW_X, SCREW_R_BASE, SCREW_R_TOP = 0.0318, 0.0018, 0.00125

# ---------------------------------------------------------------- Doku atlasi
ATLAS_W, ATLAS_H = 2048, 2048
# generate_textures.py ile bire bir ayni piksel dikdortgenleri (2048x2048 v3)
UV_RECT_FRONT = (32, 32, 2016, 410)     # Label_Plate on yuzu  (44.0 x 8.4 mm)
UV_RECT_BACK = (32, 450, 2016, 878)     # Backplate arka yuzu  (68.0 x 14.7 mm)
UV_RECT_MAGNET = (32, 906, 2016, 1326)   # Magnet_Block on yuzu (50.4 x 10.66 mm)
UV_RECT_LED = (92, 1440, 260, 1608)     # DETAIL bandindaki kirmizi lens
PIX_FLAT_BODY = (1080, 1870)            # RAL 9003 duz govde rengi
PIX_FLAT_SIDE = (1360, 1870)            # pah/yan yuzey ara tonu
PIX_LED_RIM = (104, 1524)               # lens kenari (koyu kirmizi)


def pix_to_uv(px, py):
    """Atlas piksel koordinatini Blender UV noktasina cevirir."""
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_FLAT_BODY)
FLAT_UV_SIDE = pix_to_uv(*PIX_FLAT_SIDE)
LED_SIDE_UV = pix_to_uv(*PIX_LED_RIM)


def uv_rect_from_pixels(x0, y0, x1, y1):
    """Piksel dikdortgenini (u0, v0, u1, v1) araligina cevirir."""
    return (x0 / ATLAS_W, 1.0 - (y1 / ATLAS_H), x1 / ATLAS_W, 1.0 - (y0 / ATLAS_H))


def set_face_uv_rect(face, uv_layer, rect, flip_u=False):
    """
    Yuzeyi verilen UV dikdortgenine oransal haritalar (doku sunmesi yok).
    flip_u: +Y normaline bakan yuzlerde True (SOP 2-C kurali).
    """
    u0, v0, u1, v1 = rect
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
    """Slot 0: M_Security_Atlas (doku atlasli), Slot 1: M_Metal (Asset 33 dili)."""
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
    bsdf.inputs["Roughness"].default_value = 0.40
    bsdf.inputs["Metallic"].default_value = 0.05

    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    mbsdf = mat_metal.node_tree.nodes.get("Principled BSDF")
    mbsdf.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    mbsdf.inputs["Metallic"].default_value = 0.95
    mbsdf.inputs["Roughness"].default_value = 0.22

    return [mat_atlas, mat_metal]


def build_beveled_bar(name, p_back, y_back, p_front, y_front, mats,
                      front_rect=None, back_rect=None, front_mat=0, back_mat=0):
    """
    Iki pahlanmis profil arasinda govde uretir (arka ve on halka).
    front_rect: +Y yuzune uygulanacak UV dikdortgeni (flip_u=True)
    back_rect : -Y yuzune uygulanacak UV dikdortgeni (flip_u=False)
    Pah/yan yuzeyler FLAT_UV_SIDE tonuna haritalanir.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    v_back = [bm.verts.new(Vector((p[0], y_back, p[1]))) for p in p_back]
    v_front = [bm.verts.new(Vector((p[0], y_front, p[1]))) for p in p_front]

    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.smooth = False
    f_back.material_index = back_mat
    if back_rect:
        set_face_uv_rect(f_back, uv_layer, back_rect, flip_u=False)
    else:
        set_flat_uv(f_back, uv_layer)

    f_front = bm.faces.new(v_front)
    f_front.smooth = False
    f_front.material_index = front_mat
    if front_rect:
        set_face_uv_rect(f_front, uv_layer, front_rect, flip_u=True)
    else:
        set_flat_uv(f_front, uv_layer)

    n = len(p_back)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((v_back[i], v_back[j], v_front[j], v_front[i]))
        f.smooth = True
        f.material_index = front_mat
        set_flat_uv(f, uv_layer, FLAT_UV_SIDE)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, name, mats)


def build_box(name, x0, x1, y0, y1, z0, z1, mats, front_rect=None, mat_index=0):
    """
    Eksen hizali kapali kutu (12 tris). Kabartma etiket plakasi icin kullanilir.
    On yuz (+Y) front_rect ile kaplanir, diger yuzler duz renk alir.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    v000 = bm.verts.new(Vector((x0, y0, z0)))
    v100 = bm.verts.new(Vector((x1, y0, z0)))
    v110 = bm.verts.new(Vector((x1, y0, z1)))
    v010 = bm.verts.new(Vector((x0, y0, z1)))
    v001 = bm.verts.new(Vector((x0, y1, z0)))
    v101 = bm.verts.new(Vector((x1, y1, z0)))
    v111 = bm.verts.new(Vector((x1, y1, z1)))
    v011 = bm.verts.new(Vector((x0, y1, z1)))

    faces = [
        (bm.faces.new((v000, v100, v110, v010)), FLAT_UV_SIDE),   # -Y
        (bm.faces.new((v001, v011, v111, v101)), None),           # +Y (etiket)
        (bm.faces.new((v000, v010, v011, v001)), FLAT_UV_SIDE),   # -X
        (bm.faces.new((v100, v101, v111, v110)), FLAT_UV_SIDE),   # +X
        (bm.faces.new((v000, v001, v101, v100)), FLAT_UV_SIDE),   # -Z
        (bm.faces.new((v010, v110, v111, v011)), FLAT_UV_SIDE),   # +Z
    ]
    for f, flat in faces:
        f.smooth = False
        f.material_index = mat_index
        if flat is None and front_rect:
            set_face_uv_rect(f, uv_layer, front_rect, flip_u=True)
        else:
            set_flat_uv(f, uv_layer, flat if flat else FLAT_UV_SIDE)

    mark_sharp_edges_by_angle(bm, 35.0)
    return finish_mesh(bm, name, mats)


def build_cylinder(name, rings, segments, axis, mats, mat_index=1, uv_rect=None,
                   phase=0.0, side_flat_uv=None):
    """
    Kapali silindir / koni uretir (vida basi, rakor, LED lensi).
    rings: [(merkez_x, merkez_y, merkez_z, rx, rz)]
    axis : 'Y' veya 'X'
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
            else:
                co = Vector((cx, cy + ca * rx, cz + sa * rz))
            ring.append(bm.verts.new(co))
        loop_rings.append(ring)

    for r in range(len(loop_rings) - 1):
        a_ring, b_ring = loop_rings[r], loop_rings[r + 1]
        for i in range(segments):
            j = (i + 1) % segments
            f = bm.faces.new((a_ring[i], a_ring[j], b_ring[j], b_ring[i]))
            f.smooth = True
            f.material_index = mat_index
            if side_flat_uv:
                for loop in f.loops:
                    loop[uv_layer].uv = side_flat_uv
            elif uv_rect:
                set_face_uv_rect(f, uv_layer, uv_rect, flip_u=True)
            else:
                set_flat_uv(f, uv_layer, FLAT_UV_SIDE)

    f_cap_a = bm.faces.new(list(reversed(loop_rings[0])))
    f_cap_a.smooth = False
    f_cap_a.material_index = mat_index
    if uv_rect:
        set_face_uv_rect(f_cap_a, uv_layer, uv_rect, flip_u=True)
    else:
        set_flat_uv(f_cap_a, uv_layer)

    f_cap_b = bm.faces.new(loop_rings[-1])
    f_cap_b.smooth = False
    f_cap_b.material_index = mat_index
    if uv_rect:
        set_face_uv_rect(f_cap_b, uv_layer, uv_rect, flip_u=True)
    else:
        set_flat_uv(f_cap_b, uv_layer)

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
    rect_front = uv_rect_from_pixels(*UV_RECT_FRONT)
    rect_back = uv_rect_from_pixels(*UV_RECT_BACK)
    rect_magnet = uv_rect_from_pixels(*UV_RECT_MAGNET)
    rect_led = uv_rect_from_pixels(*UV_RECT_LED)

    # ------------------------------------------------------------ Root Empty
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    # ------------------------------------------------------------ Backplate
    backplate = build_beveled_bar(
        "Backplate",
        chamfer_profile(BP_HALF_X, BP_HALF_Z, 0.0028), 0.0,
        chamfer_profile(BP_HALF_X - 0.0005, BP_HALF_Z - 0.00025, 0.0026), BP_DEPTH,
        mats, front_rect=None, back_rect=rect_back,
    )
    backplate.parent = root

    # Konik alti kenar vida baslari (plakaya 0.1 mm gomulu - bosluk yok)
    # Origin: vida basi taban merkezi (kendi ekseninde dondurulebilir)
    for name, sx in (("Screw_Boss_L", -SCREW_X), ("Screw_Boss_R", SCREW_X)):
        screw = build_cylinder(
            name,
            [(0.0, 0.0, 0.0, SCREW_R_BASE, SCREW_R_BASE),
             (0.0, 0.00140, 0.0, SCREW_R_TOP, SCREW_R_TOP)],
            6, 'Y', mats, mat_index=1, phase=math.pi / 6.0,
        )
        screw.location = Vector((sx, 0.00290, 0.0))
        screw.parent = backplate

    # ------------------------------------------------------------ Sensor_Body
    sensor_body = build_beveled_bar(
        "Sensor_Body",
        chamfer_profile(SENSOR_HALF_X, SENSOR_HALF_Z, 0.0025), BP_DEPTH,
        chamfer_profile(SENSOR_FRONT_HALF_X, SENSOR_FRONT_HALF_Z, 0.0022), SENSOR_FRONT_Y,
        mats, front_rect=None,
    )
    sensor_body.parent = root

    # Kabartma etiket plakasi (X=0'a gore simetrik -> kayma yok)
    # Origin: plaka alt orta noktasi (govde on yuzu)
    label_plate = build_box(
        "Label_Plate",
        -LABEL_HALF_X, LABEL_HALF_X, 0.0, LABEL_FRONT_Y - SENSOR_FRONT_Y,
        -LABEL_HALF_Z, LABEL_HALF_Z, mats, front_rect=rect_front,
    )
    label_plate.location = Vector((0.0, SENSOR_FRONT_Y, 0.0))
    label_plate.parent = sensor_body

    # -X ucundan cikan rakor (govde icine 3.4 mm gomulu -> bosluk yok)
    # Origin: govde yuzeyindeki rakor tabani
    cable_gland = build_cylinder(
        "Cable_Gland",
        [(0.0, 0.0, 0.0, 0.0029, 0.0029),
         (-0.0102, 0.0, 0.0, 0.0026, 0.0026)],
        6, 'X', mats, mat_index=1, phase=math.pi / 6.0,
    )
    cable_gland.location = Vector((-0.0260, 0.0084, 0.0))
    cable_gland.parent = sensor_body

    # Etiket plakasi uzerindeki alcak durum LED lensi
    # Origin: lens taban merkezi
    status_led = build_cylinder(
        "Status_LED",
        [(0.0, 0.0, 0.0, 0.0026, 0.0026),
         (0.0, 0.00060, 0.0, 0.0022, 0.0022)],
        6, 'Y', mats, mat_index=0, uv_rect=rect_led, side_flat_uv=LED_SIDE_UV,
        phase=math.pi / 6.0,
    )
    status_led.location = Vector((0.0150, LABEL_FRONT_Y, 0.0))
    status_led.parent = sensor_body

    # ------------------------------------------------------------ Magnet
    magnet_root = bpy.data.objects.new("Magnet_Block_Root", None)
    magnet_root.empty_display_type = 'PLAIN_AXES'
    magnet_root.empty_display_size = 0.02
    magnet_root.location = Vector((MAGNET_ROOT_X, 0.0, 0.0))
    bpy.context.collection.objects.link(magnet_root)
    magnet_root.parent = root

    magnet_root["pivot_axis"] = "Z"
    magnet_root["rotation_min_deg"] = -95.0
    magnet_root["rotation_max_deg"] = 0.0
    magnet_root["door_swing_direction"] = "+Z ekseni (kapi acilma yonu)"
    magnet_root["nominal_gap_mm"] = 6.0
    magnet_root["max_operating_gap_mm"] = 12.0

    door_limit = magnet_root.constraints.new('LIMIT_ROTATION')
    door_limit.name = "Door_Swing_Limit"
    door_limit.use_limit_z = True
    door_limit.min_z = math.radians(-95.0)
    door_limit.max_z = math.radians(0.0)
    door_limit.owner_space = 'LOCAL'

    # Duvar duzleminden (Y=0) baslayan, govdeyle ayni derinlikte biten blok
    magnet_block = build_beveled_bar(
        "Magnet_Block",
        chamfer_profile(MAGNET_HALF_X, MAGNET_HALF_Z, 0.0024), 0.0,
        chamfer_profile(MAGNET_FRONT_HALF_X, MAGNET_FRONT_HALF_Z, 0.0022), MAGNET_DEPTH,
        mats, front_rect=rect_magnet,
    )
    magnet_block.parent = magnet_root

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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 35 v2) ---")
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

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= TRIS_BUDGET, \
        f"FAIL: Total triangles {total_tris} exceeds {TRIS_BUDGET} budget!"
    print(f"[PASS] Triangle count verified strictly (<= {TRIS_BUDGET})!")
    assert not uv_missing, f"FAIL: Missing/empty UV layer on: {uv_missing}"
    print("[PASS] UV layers present on all meshes!")

    # --------------------------------------------------------------- Hiyerarsi
    objs = {o.name: o for o in [re_root] + re_root.children_recursive}
    expected_parents = {
        "Backplate": ASSET_NAME,
        "Sensor_Body": ASSET_NAME,
        "Magnet_Block_Root": ASSET_NAME,
        "Magnet_Block": "Magnet_Block_Root",
        "Label_Plate": "Sensor_Body",
        "Cable_Gland": "Sensor_Body",
        "Status_LED": "Sensor_Body",
        "Screw_Boss_L": "Backplate",
        "Screw_Boss_R": "Backplate",
    }
    for child_name, parent_name in expected_parents.items():
        child = objs.get(child_name)
        assert child is not None, f"FAIL: {child_name} missing in FBX hierarchy"
        assert child.parent is not None and child.parent.name == parent_name, \
            f"FAIL: {child_name} parent mismatch (expected {parent_name})"
    print("[PASS] Full parent-child hierarchy verified (9 relations)!")

    # --------------------------------------------------------------- Materyal slotlari
    expected_mats = ["M_Security_Atlas", "M_Metal"]
    for name in ("Backplate", "Sensor_Body", "Magnet_Block", "Label_Plate",
                 "Cable_Gland", "Status_LED", "Screw_Boss_L", "Screw_Boss_R"):
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:2] == expected_mats, \
            f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0: M_Security_Atlas, Slot 1: M_Metal)!")

    # --------------------------------------------------------------- Bosluk / temas QA
    gap_mm = (world_aabb(objs["Magnet_Block"])[0].x
              - world_aabb(objs["Sensor_Body"])[1].x) * 1000.0
    clearance_mm = (world_aabb(objs["Magnet_Block"])[0].x
                    - world_aabb(objs["Backplate"])[1].x) * 1000.0
    magnet_y0 = world_aabb(objs["Magnet_Block"])[0].y * 1000.0
    print(f"[QA] Sensor -> magnet gap: {gap_mm:.2f} mm | montaj plakasi -> magnet boslugu: {clearance_mm:.2f} mm")
    print(f"[QA] Magnet montaj yuzeyi offseti: {magnet_y0:.2f} mm (0.00 olmali)")
    assert 2.0 < gap_mm < 12.0, f"FAIL: Magnet gap {gap_mm:.2f} mm out of spec"
    assert clearance_mm > 0.5, "FAIL: Magnet block intersects the wall backplate"
    assert abs(magnet_y0) < 0.05, "FAIL: Magnet block floats off the mounting plane"

    contact_pairs = [
        ("Sensor_Body", "Backplate"),
        ("Screw_Boss_L", "Backplate"),
        ("Screw_Boss_R", "Backplate"),
        ("Label_Plate", "Sensor_Body"),
        ("Status_LED", "Label_Plate"),
        ("Cable_Gland", "Sensor_Body"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), \
            f"FAIL: visible gap between {a_name} and {b_name}"
    print("[PASS] Zero-gap assembly verified (6 contact pairs, no floating parts)!")

    # --------------------------------------------------------------- UV oran QA
    ratios = [
        ("Label_Plate front", UV_RECT_FRONT, (44.0, 8.4)),
        ("Backplate rear", UV_RECT_BACK, (68.0, 14.7)),
        ("Magnet front", UV_RECT_MAGNET, (50.4, 10.66)),
    ]
    for label, rect, size_mm in ratios:
        err = abs(aa_ratio(rect, size_mm) - 1.0) * 100.0
        print(f"[QA] UV aspect {label:18s}: {size_mm[0]:.1f} x {size_mm[1]:.2f} mm -> sapma {err:.2f}%")
        assert err < 1.0, f"FAIL: UV stretch {err:.2f}% on {label}"
    print(f"[QA] Etiket doku yogunlugu: {(UV_RECT_FRONT[2] - UV_RECT_FRONT[0]) / 44.0:.1f} px/mm")
    print("[PASS] UV rectangles locked to face aspect ratios (no texture sliding)!")

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

