"""
=============================================================================
Security CCTV Asset Production Suite - Asset 38
QA Render Script (tekrarlanabilir gorsel dogrulama)

Calistirma:
    & "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b \
        --python scripts/render_qa.py

Uretilenler (qa/):
    front_flat.png  : on yuzun 1:1 (isiksiz, dokulu) dik izdusumu
                      -> scripts/check_uv_render.py bunu atlas ile koreler
    hero_34.png     : 3/4 perspektif, EEVEE, doku + form kontrolu

NOT: QA kamerasi ve isiklari kaydedilen .blend dosyasina YAZILMAZ; teslimat
     sahnesi temiz kalir (kamera/light eklenmez).
=============================================================================
"""

import bpy
import math
import os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(HERE)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
QA_DIR = os.path.join(ASSET_DIR, "qa")     # teslimat disi: exports/ temiz kalir
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Sensor_Gas.blend")

# check_uv_render.py ile bire bir ayni kadraj parametreleri
FLAT_RES = 900
FLAT_ORTHO = 0.105          # m
FLAT_CAM_Z = 0.0            # m (on yuz merkezi hizasi)

HERO_RES = 1100
HERO_LENS = 85.0
HERO_DIST = 0.30
HERO_TARGET = Vector((0.0, 0.0190, 0.0))
# Isik siddeti kalibrasyon carpani (gerekirse QA_LIGHT_SCALE ile ayarlanir)
LIGHT_SCALE = float(os.environ.get("QA_LIGHT_SCALE", "1.0"))


def open_asset():
    if not os.path.exists(BLEND_PATH):
        raise FileNotFoundError(f"Kaynak sahne yok: {BLEND_PATH}")
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    return scene


def make_camera(name, location, rotation=None, target=None):
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    if target is not None:
        direction = target - Vector(location)
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    elif rotation is not None:
        cam.rotation_euler = rotation
    return cam


def assert_in_frame(scene, cam, label, margin=0.03):
    """Tum mesh koselerinin kadraj icinde (kenar payiyla) kaldigini dogrular."""
    from bpy_extras.object_utils import world_to_camera_view

    bpy.context.view_layer.update()   # kamera/nesne matrix_world tazelenmeli

    worst = 0.0
    offender = None
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        for corner in obj.bound_box:
            co = world_to_camera_view(scene, cam, obj.matrix_world @ Vector(corner))
            d = max(margin - co.x, co.x - (1.0 - margin),
                    margin - co.y, co.y - (1.0 - margin))
            if d > worst:
                worst, offender = d, obj.name
    assert worst <= 0.0, (f"FAIL: {label} kadraj disina tasiyor "
                          f"({offender}, {worst:.3f} NDC)")
    print(f"[PASS] {label}: tum parcalar kadraj icinde (kenar payi >= %{margin*100:.0f})")


def assert_exposure(path, label, white_max=0.04, mean_range=(60.0, 210.0)):
    """Render patlamamis mi? Beyaz kirpilma ve ortalama parlaklik siniri."""
    import numpy as np

    img = bpy.data.images.load(path)
    try:
        img.colorspace_settings.name = 'Non-Color'  # dosyadaki sRGB degerleri okunur
        px = np.array(img.pixels[:], dtype=np.float32).reshape(-1, img.channels)
        rgb = px[:, :3] * 255.0
    finally:
        bpy.data.images.remove(img)

    white = float((rgb.min(axis=1) > 250.0).mean())
    mean = float(rgb.mean())
    assert white <= white_max, (f"FAIL: {label} asiri pozlama - beyaz kirpilma "
                                f"%{white*100:.2f} (limit %{white_max*100:.0f})")
    assert mean_range[0] <= mean <= mean_range[1], (
        f"FAIL: {label} parlaklik dengesi bozuk - ortalama {mean:.1f} "
        f"(beklenen {mean_range[0]:.0f}..{mean_range[1]:.0f})")
    print(f"[PASS] {label}: pozlama dengeli (beyaz %{white*100:.2f}, ortalama {mean:.1f})")


def setup_world(scene, strength=0.65, color=(0.72, 0.75, 0.80)):
    world = scene.world or bpy.data.worlds.new("QA_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
        bg.inputs[1].default_value = strength


def render_flat(scene):
    """Isiksiz, dokulu dik izdusum: doku ile render bire bir karsilastirilabilsin."""
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = FLAT_RES
    scene.render.resolution_y = FLAT_RES
    scene.render.resolution_percentage = 100

    shading = scene.display.shading
    shading.light = 'FLAT'
    shading.color_type = 'TEXTURE'
    shading.show_shadows = False
    shading.show_cavity = False
    shading.show_specular_highlight = False
    shading.show_object_outline = False
    shading.background_type = 'VIEWPORT'
    shading.background_color = (0.84, 0.86, 0.89)
    scene.display.render_aa = '8'

    cam = make_camera(
        "QA_Cam_Flat",
        (0.0, 0.35, FLAT_CAM_Z),
        rotation=(math.radians(90.0), 0.0, math.radians(180.0)),
    )
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = FLAT_ORTHO
    cam.data.clip_start = 0.01
    cam.data.clip_end = 1.0
    scene.camera = cam
    assert_in_frame(scene, cam, "duz izdusum kadraji", margin=0.01)

    path = os.path.join(QA_DIR, "front_flat.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[OK] QA flat render: {path}")


def render_hero(scene):
    """3/4 perspektif, EEVEE, uc nokta isik: doku + form + golge kontrolu."""
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = HERO_RES
    scene.render.resolution_y = HERO_RES
    scene.render.resolution_percentage = 100
    try:
        scene.eevee.taa_render_samples = 64
    except AttributeError:
        pass

    setup_world(scene, 0.35, (0.70, 0.73, 0.78))

    eye = HERO_TARGET + Vector((0.85, 1.15, 0.62)).normalized() * HERO_DIST
    cam = make_camera("QA_Cam_34", eye, target=HERO_TARGET)
    cam.data.lens = HERO_LENS
    cam.data.sensor_width = 36.0
    cam.data.clip_start = 0.01
    cam.data.clip_end = 2.0
    scene.camera = cam

    lights = (
        ("QA_Key", (0.16, 0.26, 0.20), 0.55, 0.22),
        ("QA_Fill", (-0.22, 0.16, 0.05), 0.22, 0.30),
        ("QA_Rim", (-0.06, -0.16, 0.14), 0.32, 0.20),
    )
    for name, loc, power, size in lights:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy = power * LIGHT_SCALE
        data.size = size
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        obj.location = loc
        obj.rotation_euler = (HERO_TARGET - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        obj.visible_camera = False

    path = os.path.join(QA_DIR, "hero_34.png")
    scene.render.filepath = path
    assert_in_frame(scene, cam, "3/4 kadraji", margin=0.03)
    bpy.ops.render.render(write_still=True)
    assert_exposure(path, "3/4 render pozu")
    print(f"[OK] QA hero render: {path}")


def main():
    os.makedirs(QA_DIR, exist_ok=True)
    scene = open_asset()
    render_flat(scene)
    render_hero(scene)
    print("[DONE] QA render tamamlandi (sahne dosyasi degistirilmedi)")


if __name__ == "__main__":
    main()

