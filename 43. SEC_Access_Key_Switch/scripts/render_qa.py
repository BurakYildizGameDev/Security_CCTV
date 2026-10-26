"""
=============================================================================
Security CCTV Asset Production Suite - Asset 43
QA Render Script (tekrarlanabilir gorsel dogrulama)

Uretilenler (qa/):
    front_flat.png        : on yuzun 1:1 dik izdusumu (Workbench, dokulu)
    hero_34.png           : 3/4 perspektif, EEVEE, doku + form + golge
    key_turned_neg45.png  : anahtar -45° donuk halde (BYPASS konumu)
    key_turned_pos45.png  : anahtar +45° donuk halde (ON konumu)
=============================================================================
"""

import bpy
import math
import os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(HERE)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
QA_DIR = os.path.join(ASSET_DIR, "qa")
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Access_Key_Switch.blend")

FLAT_RES = 900
FLAT_ORTHO = 0.095          # 70 x 70 mm plaka icin kadraj
HERO_RES = 1100
HERO_LENS = 85.0
HERO_DIST = 0.32
HERO_TARGET = Vector((0.0, 0.006, 0.0))


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


def setup_world(scene, strength=0.7, color=(0.75, 0.78, 0.82)):
    world = scene.world or bpy.data.worlds.new("QA_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
        bg.inputs[1].default_value = strength


def render_flat(scene):
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
        (0.0, 0.25, 0.0),
        rotation=(math.radians(90.0), 0.0, math.radians(180.0)),
    )
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = FLAT_ORTHO
    cam.data.clip_start = 0.01
    cam.data.clip_end = 1.0
    scene.camera = cam

    path = os.path.join(QA_DIR, "front_flat.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[OK] QA flat render: {path}")


def render_hero(scene):
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = HERO_RES
    scene.render.resolution_y = HERO_RES
    setup_world(scene, strength=0.6)

    # 3 nokta isik
    lights = (
        ("QA_Key", (0.12, 0.18, 0.12), 0.55),
        ("QA_Fill", (-0.16, 0.12, 0.04), 0.25),
        ("QA_Rim", (-0.05, -0.12, 0.10), 0.35),
    )
    for name, pos, energy in lights:
        l_data = bpy.data.lights.new(name, 'POINT')
        l_data.energy = energy * 18.0
        l_data.shadow_soft_size = 0.02
        l_obj = bpy.data.objects.new(name, l_data)
        l_obj.location = pos
        bpy.context.collection.objects.link(l_obj)

    ang_h = math.radians(35.0)
    ang_v = math.radians(25.0)
    cam_pos = HERO_TARGET + Vector((
        HERO_DIST * math.cos(ang_v) * math.sin(ang_h),
        HERO_DIST * math.cos(ang_v) * math.cos(ang_h),
        HERO_DIST * math.sin(ang_v),
    ))
    cam = make_camera("QA_Cam_Hero", cam_pos, target=HERO_TARGET)
    cam.data.lens = HERO_LENS
    scene.camera = cam

    path = os.path.join(QA_DIR, "hero_34.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[OK] QA hero render: {path}")


def render_rotations(scene):
    pivot = bpy.data.objects.get("Key_Rotation_Pivot")
    if not pivot:
        return

    # -45 derece donuk render
    pivot.rotation_euler.y = -math.radians(45.0)
    bpy.context.view_layer.update()
    path_neg = os.path.join(QA_DIR, "key_turned_neg45.png")
    scene.render.filepath = path_neg
    bpy.ops.render.render(write_still=True)
    print(f"[OK] QA key neg45 render: {path_neg}")

    # +45 derece donuk render
    pivot.rotation_euler.y = math.radians(45.0)
    bpy.context.view_layer.update()
    path_pos = os.path.join(QA_DIR, "key_turned_pos45.png")
    scene.render.filepath = path_pos
    bpy.ops.render.render(write_still=True)
    print(f"[OK] QA key pos45 render: {path_pos}")

    # Sifirla
    pivot.rotation_euler.y = 0.0
    bpy.context.view_layer.update()


def main():
    scene = open_asset()
    render_flat(scene)
    render_hero(scene)
    render_rotations(scene)
    print("[DONE] QA render tamamlandi (Asset 43).")


if __name__ == "__main__":
    main()
