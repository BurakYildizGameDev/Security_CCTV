import bpy
import os
import math

def render_qa(blend_path, qa_dir):
    os.makedirs(qa_dir, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.film_transparent = False
    
    world = scene.world or bpy.data.worlds.new("QA_World")
    scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get('Background')
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        bg_node.inputs['Strength'].default_value = 1.0
        
    cam_data = bpy.data.cameras.new("QA_Cam")
    cam_data.lens = 50
    cam_obj = bpy.data.objects.new("QA_Cam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    light_data = bpy.data.lights.new("QA_Key", type='SUN')
    light_data.energy = 4.0
    light_obj = bpy.data.objects.new("QA_Key", light_data)
    light_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(35))
    scene.collection.objects.link(light_obj)
    
    fill_data = bpy.data.lights.new("QA_Fill", type='SUN')
    fill_data.energy = 2.0
    fill_obj = bpy.data.objects.new("QA_Fill", fill_data)
    fill_obj.rotation_euler = (math.radians(60), math.radians(-40), math.radians(-120))
    scene.collection.objects.link(fill_obj)
    
    # 1. Hero 3/4
    cam_obj.location = (0.12, -0.14, 0.09)
    cam_obj.rotation_euler = (math.radians(62), 0, math.radians(40))
    scene.render.filepath = os.path.join(qa_dir, "hero_34.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered hero_34.png")
    
    # 2. Front Flat
    cam_obj.location = (0.0, -0.18, 0.015)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    scene.render.filepath = os.path.join(qa_dir, "front_flat.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered front_flat.png")
    
    # 3. Top Ortho
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 0.22
    cam_obj.location = (0.0, 0.0, 0.25)
    cam_obj.rotation_euler = (0, 0, 0)
    scene.render.filepath = os.path.join(qa_dir, "top_ortho.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered top_ortho.png")

if __name__ == "__main__":
    b_path = r"C:\Users\Burak\Desktop\Security_CCTV\69. SEC_Cable_Gland_Set\exports\SEC_Cable_Gland_Set.blend"
    q_dir = r"C:\Users\Burak\Desktop\Security_CCTV\69. SEC_Cable_Gland_Set\qa"
    render_qa(b_path, q_dir)
