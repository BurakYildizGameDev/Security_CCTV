import bpy
import math
import os

blend_file = r"C:\Users\Burak\Desktop\Security_CCTV\75. SEC_Server_Rack_Fan\exports\SEC_Server_Rack_Fan.blend"
bpy.ops.wm.open_mainfile(filepath=blend_file)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.film_transparent = False

# World background
world = bpy.data.worlds.new("QA_World")
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
bg_node.inputs['Color'].default_value = (0.15, 0.16, 0.18, 1.0)
bg_node.inputs['Strength'].default_value = 0.85
scene.world = world

# Studio lighting
light_data1 = bpy.data.lights.new(name="KeyLight", type='SUN')
light_data1.energy = 2.8
light_data1.color = (1.0, 0.98, 0.95)
light1 = bpy.data.objects.new("KeyLight", light_data1)
light1.rotation_euler = (math.radians(50), math.radians(20), math.radians(45))
scene.collection.objects.link(light1)

light_data2 = bpy.data.lights.new(name="FillLight", type='SUN')
light_data2.energy = 1.4
light_data2.color = (0.85, 0.90, 1.0)
light2 = bpy.data.objects.new("FillLight", light_data2)
light2.rotation_euler = (math.radians(-40), math.radians(-30), math.radians(-135))
scene.collection.objects.link(light2)

# Camera (50mm lens at 0.28m distance for complete framing without edge clipping)
cam_data = bpy.data.cameras.new("QACam")
cam_data.lens = 50
cam = bpy.data.objects.new("QACam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam

out_dir = r"C:\Users\Burak\Desktop\Security_CCTV\75. SEC_Server_Rack_Fan\qa"
os.makedirs(out_dir, exist_ok=True)

# 1. Front view
cam.location = (0.0, -0.28, 0.0)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.render.filepath = os.path.join(out_dir, "front_flat.png")
bpy.ops.render.render(write_still=True)

# 2. Back view
cam.location = (0.0, 0.28, 0.0)
cam.rotation_euler = (math.radians(-90), math.radians(180), 0)
scene.render.filepath = os.path.join(out_dir, "back_flat.png")
bpy.ops.render.render(write_still=True)

# 3. Hero 3/4 view
cam.location = (0.18, -0.22, 0.16)
cam.rotation_euler = (math.radians(65), 0, math.radians(40))
scene.render.filepath = os.path.join(out_dir, "hero_34.png")
bpy.ops.render.render(write_still=True)

# 4. Solid View for direct geometry inspection
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.light = 'STUDIO'
scene.display.shading.color_type = 'MATERIAL'
cam.location = (0.0, -0.28, 0.0)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.render.filepath = os.path.join(out_dir, "front_solid.png")
bpy.ops.render.render(write_still=True)

print("[QA] All renders generated successfully.")
