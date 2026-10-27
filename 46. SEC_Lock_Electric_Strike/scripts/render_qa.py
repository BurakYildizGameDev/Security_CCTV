"""
=============================================================================
Security CCTV Asset Production Suite - Asset 46
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
BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Lock_Electric_Strike.blend")
os.makedirs(QA_DIR, exist_ok=True)

FLAT_RES_X = 600
FLAT_RES_Y = 1200
FLAT_ORTHO = 0.185

HERO_RES = 1024
HERO_LENS = 75.0
HERO_DIST = 0.35
HERO_TARGET = Vector((0.0, -0.015, 0.0))

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

def setup_world(scene, strength=0.8, color=(0.85, 0.88, 0.92)):
    world = scene.world or bpy.data.worlds.new("QA_World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
        bg.inputs[1].default_value = strength

def render_flat(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = FLAT_RES_X
    scene.render.resolution_y = FLAT_RES_Y
    scene.render.resolution_percentage = 100

    shading = scene.display.shading
    shading.light = 'FLAT'
    shading.color_type = 'TEXTURE'

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for idx, mat in enumerate(obj.data.materials):
                if mat and 'Atlas' in mat.name:
                    obj.active_material_index = idx

    cam = make_camera(
        "Cam_Flat",
        location=(0.0, 0.30, 0.0),
        rotation=(math.radians(90), 0.0, math.radians(180))
    )
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = FLAT_ORTHO
    scene.camera = cam

    out_path = os.path.join(QA_DIR, "front_flat.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"Flat front render saved: {out_path}")
    bpy.data.objects.remove(cam, do_unlink=True)

def render_hero(scene):
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = HERO_RES
    scene.render.resolution_y = HERO_RES
    scene.render.resolution_percentage = 100

    setup_world(scene, strength=0.6)

    # 3-point light setup
    key = bpy.data.objects.new("Key_Light", bpy.data.lights.new("Key_Light", 'POINT'))
    key.location = Vector((0.25, 0.25, 0.25))
    key.data.energy = 40.0
    bpy.context.collection.objects.link(key)

    fill = bpy.data.objects.new("Fill_Light", bpy.data.lights.new("Fill_Light", 'POINT'))
    fill.location = Vector((-0.25, 0.20, 0.10))
    fill.data.energy = 20.0
    bpy.context.collection.objects.link(fill)

    rim = bpy.data.objects.new("Rim_Light", bpy.data.lights.new("Rim_Light", 'POINT'))
    rim.location = Vector((0.0, -0.30, -0.15))
    rim.data.energy = 35.0
    bpy.context.collection.objects.link(rim)

    # Hero camera
    cam_pos = HERO_TARGET + Vector((0.18, 0.24, 0.15))
    cam = make_camera("Cam_Hero", location=cam_pos, target=HERO_TARGET)
    cam.data.type = 'PERSP'
    cam.data.lens = HERO_LENS
    scene.camera = cam

    out_path = os.path.join(QA_DIR, "hero_34.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"Hero 3/4 render saved: {out_path}")

    # Side view showing mortise & spec plate
    cam_side_pos = HERO_TARGET + Vector((0.30, -0.015, 0.0))
    cam.location = cam_side_pos
    direction = HERO_TARGET - cam_side_pos
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    out_side = os.path.join(QA_DIR, "side_spec.png")
    scene.render.filepath = out_side
    bpy.ops.render.render(write_still=True)
    print(f"Side spec render saved: {out_side}")

    for obj in [cam, key, fill, rim]:
        bpy.data.objects.remove(obj, do_unlink=True)

def main():
    scene = open_asset()
    render_flat(scene)
    render_hero(scene)
    print("QA renders complete!")

if __name__ == "__main__":
    main()
