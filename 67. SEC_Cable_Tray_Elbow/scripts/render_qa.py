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
    
    world = scene.world or bpy.data.worlds.new("QA_World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0

    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)
        
    def add_sun(name, rot, strength):
        l_data = bpy.data.lights.new(name=name, type='SUN')
        l_data.energy = strength
        l_obj = bpy.data.objects.new(name=name, object_data=l_data)
        l_obj.rotation_euler = rot
        scene.collection.objects.link(l_obj)
        return l_obj

    add_sun("Key_Sun", (math.radians(55), math.radians(25), math.radians(-35)), 3.5)
    add_sun("Fill_Sun", (math.radians(65), math.radians(-40), math.radians(145)), 1.5)
    add_sun("Rim_Sun", (math.radians(-30), 0, math.radians(180)), 2.0)

    cam_data = bpy.data.cameras.new("QA_Cam")
    cam_obj = bpy.data.objects.new("QA_Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # 1. Hero 3/4 Perspective View
    # Center of elbow is around (0.22, 0.22, 0.025)
    cam_data.type = 'PERSP'
    cam_data.lens = 50
    cam_obj.location = (0.75, 0.75, 0.65)
    target = (0.22, 0.22, 0.025)
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

    # 2. Top-Down Ortho View (showing the 90 degree sweep and perforated floor)
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 0.65
    cam_obj.location = (0.20, 0.20, 1.2)
    cam_obj.rotation_euler = (0, 0, 0)
    scene.render.filepath = os.path.join(qa_dir, "top_ortho.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered top_ortho.png")

    # 3. Port Profile View (looking into the Y entrance)
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 0.35
    cam_obj.location = (0.0, 0.60, 0.025)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180))
    scene.render.filepath = os.path.join(qa_dir, "front_flat.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered front_flat.png")

if __name__ == "__main__":
    blend_file = os.path.abspath(r"67. SEC_Cable_Tray_Elbow\exports\SEC_Cable_Tray_Elbow.blend")
    qa_path = os.path.abspath(r"67. SEC_Cable_Tray_Elbow\qa")
    render_qa(blend_file, qa_path)
