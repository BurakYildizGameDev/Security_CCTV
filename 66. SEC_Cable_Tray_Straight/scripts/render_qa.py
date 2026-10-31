import bpy
import math
import os

def render_qa(blend_path, qa_dir):
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    os.makedirs(qa_dir, exist_ok=True)
    
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.film_transparent = False
    
    # World background
    world = scene.world or bpy.data.worlds.new("QA_World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0

    # Lighting
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)
        
    def add_sun(name, rot, strength):
        l_data = bpy.data.lights.new(name=name, type='SUN')
        l_data.energy = strength
        l_obj = bpy.data.objects.new(name=name, object_data=l_data)
        l_obj.rotation_euler = rot
        scene.collection.objects.link(l_obj)
        return l_obj

    add_sun("Key_Sun", (math.radians(50), math.radians(20), math.radians(-30)), 3.5)
    add_sun("Fill_Sun", (math.radians(60), math.radians(-40), math.radians(140)), 1.5)
    add_sun("Rim_Sun", (math.radians(-30), 0, math.radians(180)), 2.0)

    # Camera
    cam_data = bpy.data.cameras.new("QA_Cam")
    cam_obj = bpy.data.objects.new("QA_Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 1. Hero 3/4 Perspective View
    cam_data.type = 'PERSP'
    cam_data.lens = 50
    cam_obj.location = (0.75, -0.45, 0.70)
    # Point at (0.0, 0.5, 0.025)
    target = (0.0, 0.5, 0.025)
    dx = target[0] - cam_obj.location[0]
    dy = target[1] - cam_obj.location[1]
    dz = target[2] - cam_obj.location[2]
    dist_xy = math.hypot(dx, dy)
    cam_obj.rotation_euler = (
        math.pi / 2 - math.atan2(dz, dist_xy),
        0,
        math.atan2(dx, -dy)
    )
    
    scene.render.filepath = os.path.join(qa_dir, "hero_34.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered hero_34.png")

    # 2. Top-Down Ortho View (showing length, base perforation pattern and side walls)
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 1.25
    cam_obj.location = (0.0, 0.50, 1.5)
    cam_obj.rotation_euler = (0, 0, 0)
    scene.render.filepath = os.path.join(qa_dir, "top_ortho.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered top_ortho.png")

    # 3. Front End Flat Profile View (mating cross-section at Y=0)
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 0.35
    cam_obj.location = (0.0, -0.80, 0.025)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    scene.render.filepath = os.path.join(qa_dir, "front_flat.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered front_flat.png")

if __name__ == "__main__":
    blend_file = os.path.abspath(r"66. SEC_Cable_Tray_Straight\exports\SEC_Cable_Tray_Straight.blend")
    qa_path = os.path.abspath(r"66. SEC_Cable_Tray_Straight\qa")
    render_qa(blend_file, qa_path)
