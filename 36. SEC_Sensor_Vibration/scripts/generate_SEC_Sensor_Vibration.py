"""
=============================================================================
Security CCTV Asset Production Suite - Asset 36
Asset Name: SEC_Sensor_Vibration  (Titresim Sensoru / Vibration Sensor)
Triangle Budget: <= 220 tris      (hedef: 216 tris)
Materials: Slot 0 -> M_Security_Atlas , Slot 1 -> M_Metal

ASSET (Master Prompt 36):
    - Kompakt metal sensor kasasi, montaj delikleri (civata baslari),
      kapak ve kucuk baglanti klemensi.

Hierarchy (Master Prompt):
    SEC_Sensor_Vibration (Root Empty @ 0,0,0)
     ├── Mount_Flange        (Mesh - duvara oturan montaj flansi 69 x 48 x 4 mm)
     │    ├── Mount_Bolt_L   (Mesh, M_Metal, 6 kenar civata basi)
     │    └── Mount_Bolt_R   (Mesh, M_Metal, 6 kenar civata basi)
     ├── Housing             (Mesh - pahli metal sensor kasasi)
     │    ├── Cover_Plate    (Mesh - on kapak, tam sartname etiketi)
     │    │    └── Status_LED (Mesh - gomme durum LED lensi)
     │    └── Terminal_Block (Mesh - kucuk baglanti klemensi)
     │         ├── Clamp_Screw_L (Mesh, M_Metal)
     │         ├── Clamp_Screw_R (Mesh, M_Metal)
     │         └── Cable_Gland   (Mesh, M_Metal, 6 kenar kablo rakoru)
    Sabit pivot (hareketli parca yok) -> yalnizca Root Empty.

Calistirma:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b --python scripts/generate_SEC_Sensor_Vibration.py
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector
import math
import os
import json

ASSET_NAME = "SEC_Sensor_Vibration"
TRIS_BUDGET = 220

# ---------------------------------------------------------------- Geometri (m)
FLANGE_HALF_X, FLANGE_HALF_Z, FLANGE_DEPTH = 0.0345, 0.0240, 0.0040
FLANGE_CHAMFER = 0.0026

HOUSING_BACK_HALF_X, HOUSING_BACK_HALF_Z = 0.0250, 0.0195
HOUSING_FRONT_HALF_X, HOUSING_FRONT_HALF_Z = 0.0235, 0.0180
HOUSING_FRONT_Y = 0.0290
HOUSING_CHAMFER = 0.0030

COVER_HALF_X, COVER_HALF_Z = 0.0215, 0.0150
COVER_BACK_Y, COVER_FRONT_Y = 0.0288, 0.0330
COVER_CHAMFER = 0.0022

BOLT_X, BOLT_R = 0.0288, 0.0020
LED_X, LED_Z, LED_R = 0.0135, -0.0085, 0.0024

TERM_HALF_X = 0.0110
TERM_Y0, TERM_Y1 = 0.0100, 0.0340
TERM_Z0, TERM_Z1 = -0.0305, -0.0185

CLAMP_X, CLAMP_R = 0.0055, 0.0020
CLAMP_Z = 0.5 * (TERM_Z0 + TERM_Z1)

GLAND_R, GLAND_LEN = 0.0040, 0.0080

# ---------------------------------------------------------------- Doku atlasi
ATLAS_W, ATLAS_H = 2048, 2048
# generate_textures.py ile bire bir ayni piksel dikdortgenleri (2048x2048)
UV_RECT_COVER = (32, 32, 2016, 1416)      # 43.0 x 30.0 mm
UV_RECT_TERMINAL = (32, 1490, 632, 1817)  # 22.0 x 12.0 mm
UV_RECT_LED = (700, 1478, 880, 1658)      # LED lensi
PIX_FLAT_BODY = (840, 1835)               # duz govde rengi
PIX_FLAT_SIDE = (1170, 1835)              # pah / yan yuzey ara tonu
PIX_LED_RIM = (708, 1560)                 # lens kenari (koyu kirmizi)


def pix_to_uv(px, py):
    """Atlas piksel koordinatini Blender UV noktasina cevirir."""
    return (px / ATLAS_W, 1.0 - py / ATLAS_H)


FLAT_UV_BODY = pix_to_uv(*PIX_FLAT_BODY)
FLAT_UV_SIDE = pix_to_uv(*PIX_FLAT_SIDE)
LED_SIDE_UV = pix_to_uv(*PIX_LED_RIM)


def uv_rect_from_pixels(x0, y0, x1, y1):
    """Piksel dikdortgenini (u0, v0, u1, v1) araligina cevirir."""
    return (x0 / ATLAS_W, 1.0 - (y1 / ATLAS_H), x1 / ATLAS_W, 1.0 - (y0 / ATLAS_H))


def set_face_uv_rect(face, uv_layer, rect, flip_u=False, extent=None):
    """
    Yuzeyi verilen UV dikdortgenine oransal haritalar (doku sunmesi yok).
    flip_u: +Y normaline bakan yuzlerde True (SOP 2-C kurali).
    extent: (minx, maxx, minz, maxz) - pahlanmis yuzlerde gercek profil olcusu.
            Verilmezse yuzun kendi sinir kutusu kullanilir; pah kirpilmis
            koseler sinir kutusunu kucultup dokuyu sikistirir.
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
    bsdf.inputs["Roughness"].default_value = 0.38
    bsdf.inputs["Metallic"].default_value = 0.15

    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    mbsdf = mat_metal.node_tree.nodes.get("Principled BSDF")
    mbsdf.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    mbsdf.inputs["Metallic"].default_value = 0.95
    mbsdf.inputs["Roughness"].default_value = 0.22

    return [mat_atlas, mat_metal]


def build_beveled_bar(name, p_back, y_back, p_front, y_front, mats,
                      front_rect=None, back_rect=None, front_mat=0, back_mat=0,
                      front_extent=None):
    """
    Iki pahlanmis profil arasinda govde uretir (arka ve on halka).
    front_rect: +Y yuzune uygulanacak UV dikdortgeni (flip_u=True)
    back_rect : -Y yuzune uygulanacak UV dikdortgeni (flip_u=False)
    front_extent: on yuz UV'sinin referans aldigi gercek profil sinirlari
                  (minx, maxx, minz, maxz). Pah kirpilmis koselerde doku
                  sikismasini onler.
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
        set_face_uv_rect(f_front, uv_layer, front_rect, flip_u=True,
                         extent=front_extent)
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
    Eksen hizali kapali kutu (12 tris).
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
    rect_cover = uv_rect_from_pixels(*UV_RECT_COVER)
    rect_terminal = uv_rect_from_pixels(*UV_RECT_TERMINAL)
    rect_led = uv_rect_from_pixels(*UV_RECT_LED)

    # ------------------------------------------------------------ Root Empty
    root = bpy.data.objects.new(ASSET_NAME, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.03
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    # ------------------------------------------------------------ Montaj flansi
    flange = build_beveled_bar(
        "Mount_Flange",
        chamfer_profile(FLANGE_HALF_X, FLANGE_HALF_Z, FLANGE_CHAMFER), 0.0,
        chamfer_profile(FLANGE_HALF_X - 0.0004, FLANGE_HALF_Z - 0.0003,
                        FLANGE_CHAMFER - 0.0002), FLANGE_DEPTH,
        mats, front_rect=None,
    )
    flange.parent = root

    # 6 kenar civata baslari (flansin on yuzune 0.2 mm gomulu -> bosluk yok)
    for name, sx in (("Mount_Bolt_L", -BOLT_X), ("Mount_Bolt_R", BOLT_X)):
        bolt = build_cylinder(
            name,
            [(0.0, 0.0, 0.0, BOLT_R, BOLT_R),
             (0.0, 0.0020, 0.0, BOLT_R * 0.80, BOLT_R * 0.80)],
            6, 'Y', mats, mat_index=1, phase=math.pi / 6.0,
        )
        bolt.location = Vector((sx, FLANGE_DEPTH - 0.0002, 0.0))
        bolt.parent = flange

    # ------------------------------------------------------------ Sensor kasasi
    housing = build_beveled_bar(
        "Housing",
        chamfer_profile(HOUSING_BACK_HALF_X, HOUSING_BACK_HALF_Z, HOUSING_CHAMFER),
        FLANGE_DEPTH,
        chamfer_profile(HOUSING_FRONT_HALF_X, HOUSING_FRONT_HALF_Z,
                        HOUSING_CHAMFER - 0.0004), HOUSING_FRONT_Y,
        mats, front_rect=None,
    )
    housing.parent = root

    # ------------------------------------------------------------ On kapak
    cover = build_beveled_bar(
        "Cover_Plate",
        chamfer_profile(COVER_HALF_X, COVER_HALF_Z, COVER_CHAMFER + 0.0002),
        COVER_BACK_Y,
        chamfer_profile(COVER_HALF_X - 0.0004, COVER_HALF_Z - 0.0004, COVER_CHAMFER),
        COVER_FRONT_Y,
        mats, front_rect=rect_cover,
        front_extent=(-COVER_HALF_X, COVER_HALF_X, -COVER_HALF_Z, COVER_HALF_Z),
    )
    cover.parent = housing

    # Gomme durum LED lensi (kapak on yuzune gomulu)
    led = build_cylinder(
        "Status_LED",
        [(0.0, 0.0, 0.0, LED_R, LED_R),
         (0.0, 0.0005, 0.0, LED_R * 0.85, LED_R * 0.85)],
        6, 'Y', mats, mat_index=0, uv_rect=rect_led, side_flat_uv=LED_SIDE_UV,
        phase=math.pi / 6.0,
    )
    led.location = Vector((LED_X, COVER_FRONT_Y - 0.0002, LED_Z))
    led.parent = cover

    # ------------------------------------------------------------ Klemens blogu
    terminal = build_box(
        "Terminal_Block",
        -TERM_HALF_X, TERM_HALF_X, TERM_Y0, TERM_Y1, TERM_Z0, TERM_Z1,
        mats, front_rect=rect_terminal,
    )
    terminal.parent = housing

    # Sikistirma vidalari (klemens on yuzune gomulu)
    for name, sx in (("Clamp_Screw_L", -CLAMP_X), ("Clamp_Screw_R", CLAMP_X)):
        screw = build_cylinder(
            name,
            [(0.0, 0.0, 0.0, CLAMP_R, CLAMP_R),
             (0.0, 0.0018, 0.0, CLAMP_R * 0.78, CLAMP_R * 0.78)],
            6, 'Y', mats, mat_index=1, phase=math.pi / 6.0,
        )
        screw.location = Vector((sx, TERM_Y1 - 0.0002, CLAMP_Z))
        screw.parent = terminal

    # Kablo rakoru (-Z yonunde, klemens tabanindan cikar)
    gland = build_cylinder(
        "Cable_Gland",
        [(0.0, 0.0, 0.0, GLAND_R, GLAND_R),
         (0.0, 0.0, -GLAND_LEN, GLAND_R * 0.86, GLAND_R * 0.86)],
        6, 'Z', mats, mat_index=1, phase=math.pi / 6.0,
        side_flat_uv=FLAT_UV_SIDE,
    )
    gland.location = Vector((0.0, 0.5 * (TERM_Y0 + TERM_Y1), TERM_Z0))
    gland.parent = terminal

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

    total_size = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        mn, mx = world_aabb(obj)
        total_size.append((mn, mx))
    gmin = Vector((min(v[0].x for v in total_size), min(v[0].y for v in total_size),
                   min(v[0].z for v in total_size)))
    gmax = Vector((max(v[1].x for v in total_size), max(v[1].y for v in total_size),
                   max(v[1].z for v in total_size)))
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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 36) ---")
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
        "Mount_Flange": ASSET_NAME,
        "Mount_Bolt_L": "Mount_Flange",
        "Mount_Bolt_R": "Mount_Flange",
        "Housing": ASSET_NAME,
        "Cover_Plate": "Housing",
        "Status_LED": "Cover_Plate",
        "Terminal_Block": "Housing",
        "Clamp_Screw_L": "Terminal_Block",
        "Clamp_Screw_R": "Terminal_Block",
        "Cable_Gland": "Terminal_Block",
    }
    for child_name, parent_name in expected_parents.items():
        child = objs.get(child_name)
        assert child is not None, f"FAIL: {child_name} missing in FBX hierarchy"
        assert child.parent is not None and child.parent.name == parent_name, \
            f"FAIL: {child_name} parent mismatch (expected {parent_name})"
    print(f"[PASS] Full parent-child hierarchy verified ({len(expected_parents)} relations)!")



    # --------------------------------------------------------------- Materyal slotlari
    expected_mats = ["M_Security_Atlas", "M_Metal"]
    for name in ("Mount_Flange", "Mount_Bolt_L", "Mount_Bolt_R", "Housing",
                 "Cover_Plate", "Status_LED", "Terminal_Block",
                 "Clamp_Screw_L", "Clamp_Screw_R", "Cable_Gland"):
        slots = [s.material.name.split('.')[0] for s in objs[name].material_slots if s.material]
        assert slots[:2] == expected_mats, \
            f"FAIL: {name} material slot order wrong: {slots}"
    print("[PASS] Material slots verified (Slot 0: M_Security_Atlas, Slot 1: M_Metal)!")

    # --------------------------------------------------------------- Bosluk / temas QA
    contact_pairs = [
        ("Mount_Flange", "Housing"),
        ("Mount_Bolt_L", "Mount_Flange"),
        ("Mount_Bolt_R", "Mount_Flange"),
        ("Cover_Plate", "Housing"),
        ("Status_LED", "Cover_Plate"),
        ("Terminal_Block", "Housing"),
        ("Clamp_Screw_L", "Terminal_Block"),
        ("Clamp_Screw_R", "Terminal_Block"),
        ("Cable_Gland", "Terminal_Block"),
    ]
    for a_name, b_name in contact_pairs:
        assert parts_in_contact(objs[a_name], objs[b_name]), \
            f"FAIL: visible gap between {a_name} and {b_name}"
    print(f"[PASS] Zero-gap assembly verified ({len(contact_pairs)} contact pairs)!")

    wall_y = world_aabb(objs["Mount_Flange"])[0].y * 1000.0
    print(f"[QA] Montaj yuzeyi offseti: {wall_y:.2f} mm (0.00 olmali)")
    assert abs(wall_y) < 0.05, "FAIL: Mounting flange does not sit on the wall plane"

    cover_face = world_aabb(objs["Cover_Plate"])
    os_x = (cover_face[1].x - cover_face[0].x) * 1000.0
    os_z = (cover_face[1].z - cover_face[0].z) * 1000.0
    print(f"[QA] Kapak on yuzu: {os_x:.1f} x {os_z:.1f} mm")
    assert abs(os_x - 43.0) < 0.3 and abs(os_z - 30.0) < 0.3, \
        "FAIL: Cover face size does not match the 43 x 30 mm texture band"

    # --------------------------------------------------------------- UV oran QA
    ratios = [
        ("Cover front", UV_RECT_COVER, (43.0, 30.0)),
        ("Terminal front", UV_RECT_TERMINAL, (22.0, 12.0)),
    ]
    for label, rect, size_mm in ratios:
        err = abs(aa_ratio(rect, size_mm) - 1.0) * 100.0
        print(f"[QA] UV aspect {label:16s}: {size_mm[0]:.1f} x {size_mm[1]:.1f} mm -> sapma {err:.2f}%")
        assert err < 1.0, f"FAIL: UV stretch {err:.2f}% on {label}"
    print(f"[QA] Etiket doku yogunlugu: {(UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 43.0:.1f} px/mm")
    print("[PASS] UV rectangles locked to face aspect ratios (no texture sliding)!")

    # ------------------------------------------- Doku yogunlugu (gercek, pah kirpilmis yuz)
    # set_face_uv_rect yuzun sinir kutusunu kullanirsa pah kirpilmis koseler
    # dokuyu sikistirir. Bu olcum bunu yakalar: u ve v yogunlugu esit olmali
    # ve bant tasarim yogunluguna esit cikmali.
    cov = objs["Cover_Plate"]
    cme, cuv = cov.data, cov.data.uv_layers[0]
    mw = cov.matrix_world
    nrm = mw.to_3x3()
    cpoly = max((p for p in cme.polygons if (nrm @ p.normal).normalized().y > 0.9),
                key=lambda p: p.area)
    samples = []
    for li in cpoly.loop_indices:
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
    design = (UV_RECT_COVER[2] - UV_RECT_COVER[0]) / 43.0
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
        "FAIL: Cover label is not aligned to the texture band edge (LED/text offset)"
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

