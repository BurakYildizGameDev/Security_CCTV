"""
=============================================================================
Security CCTV Asset Production Suite - Asset 57
QA Render Script for Visual Validation
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
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Network_Router_Industrial.blend")
os.makedirs(QA_DIR, exist_ok=True)

FLAT_RES_X = 1200
FLAT_RES_Y = 1000
FLAT_ORTHO = 0.220

HERO_RES = 1024
HERO_LENS = 50.0
HERO_TARGET = Vector((0.0, 0.02, 0.02))

def open_asset():
    if not os.path.exists(BLEND_PATH):
        raise FileNotFoundError(f"Source blend missing: {BLEND_PATH}")
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

def render_flat(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = FLAT_RES_X
    scene.render.resolution_y = FLAT_RES_Y
    scene.render.resolution_percentage = 100

    shading = scene.display.shading
    shading.light = 'FLAT'
    shading.color_type = 'TEXTURE'

    # Camera looking directly at front face (+Y looking towards -Y)
    cam = make_camera(
        "Cam_Flat",
        location=(0.0, -0.40, 0.02),
        rotation=(math.radians(90), 0.0, 0.0)
    )
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = FLAT_ORTHO
    scene.camera = cam

    out_path = os.path.join(QA_DIR, "front_flat.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"[QA Render] Flat front ortho saved: {out_path}")
    bpy.data.objects.remove(cam, do_unlink=True)

def render_hero(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = HERO_RES
    scene.render.resolution_y = HERO_RES
    scene.render.resolution_percentage = 100

    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.color_type = 'TEXTURE'

    # 3/4 perspective looking down at front-left
    eye = Vector((-0.20, -0.25, 0.15))
    cam = make_camera("Cam_Hero", location=eye, target=HERO_TARGET)
    cam.data.type = 'PERSP'
    cam.data.lens = HERO_LENS
    scene.camera = cam

    out_path = os.path.join(QA_DIR, "hero_34.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"[QA Render] Hero 3/4 perspective saved: {out_path}")
    bpy.data.objects.remove(cam, do_unlink=True)

def main():
    scene = open_asset()
    render_flat(scene)
    render_hero(scene)
    print("[QA Render] All renders completed successfully.")

if __name__ == "__main__":
    main()
