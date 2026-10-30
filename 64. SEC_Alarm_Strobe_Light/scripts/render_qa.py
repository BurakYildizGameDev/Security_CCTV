"""
Security CCTV Asset Production Suite - Asset 64
QA Render Script for SEC_Alarm_Strobe_Light
"""

import bpy
import math
import os
from mathutils import Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
QA_DIR = os.path.join(ASSET_DIR, "qa")
os.makedirs(QA_DIR, exist_ok=True)

BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Strobe_Light.blend")
FRONT_RENDER = os.path.join(QA_DIR, "front_flat.png")
HERO_RENDER = os.path.join(QA_DIR, "hero_34.png")

def make_camera(name, location, target=None):
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    if target is not None:
        direction = target - Vector(location)
        cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    return cam

def render_qa():
    bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
    scene = bpy.context.scene

    scene.unit_settings.system = 'METRIC'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'

    # 1. Flat Front Ortho (looking along +Y into the lens dome)
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100

    shading = scene.display.shading
    shading.light = 'FLAT'
    shading.color_type = 'TEXTURE'

    cam_flat = make_camera("Cam_Flat", location=(0.0, 0.80, 0.0), target=Vector((0.0, 0.06, 0.0)))
    cam_flat.data.type = 'ORTHO'
    cam_flat.data.ortho_scale = 0.22
    scene.camera = cam_flat

    scene.render.filepath = FRONT_RENDER
    bpy.ops.render.render(write_still=True)
    print(f"[QA Render] Flat front ortho saved: {FRONT_RENDER}")
    bpy.data.objects.remove(cam_flat, do_unlink=True)

    # 2. Hero 3/4 Perspective
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    shading.light = 'STUDIO'
    shading.color_type = 'TEXTURE'

    cam_hero = make_camera("Cam_Hero", location=Vector((0.18, 0.28, 0.16)), target=Vector((0.0, 0.06, 0.0)))
    cam_hero.data.type = 'PERSP'
    cam_hero.data.lens = 45.0
    scene.camera = cam_hero

    scene.render.filepath = HERO_RENDER
    bpy.ops.render.render(write_still=True)
    print(f"[QA Render] Hero 3/4 perspective saved: {HERO_RENDER}")
    bpy.data.objects.remove(cam_hero, do_unlink=True)

if __name__ == "__main__":
    render_qa()
