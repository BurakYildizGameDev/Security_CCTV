import os
import math
import bpy

def render_qa(export_dir, qa_dir):
    blend_path = os.path.join(export_dir, "SEC_Conduit_Wall_Clamp.blend")
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.film_transparent = False
    
    world = scene.world or bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.22, 0.24, 0.26, 1.0)
        bg.inputs['Strength'].default_value = 0.8
        
    cam_data = bpy.data.cameras.new("QACam")
    cam_obj = bpy.data.objects.new("QACam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    light_data = bpy.data.lights.new(name="KeyLight", type='SUN')
    light_data.energy = 3.5
    light_obj = bpy.data.objects.new(name="KeyLight", object_data=light_data)
    light_obj.rotation_euler = (math.radians(45), math.radians(25), math.radians(45))
    scene.collection.objects.link(light_obj)
    
    fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_data.energy = 2.0
    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-40), math.radians(-30), math.radians(140))
    scene.collection.objects.link(fill_obj)
    
    # 1. Hero 3/4 View
    cam_obj.location = (0.07, -0.08, 0.07)
    cam_obj.rotation_euler = (math.radians(60), 0, math.radians(42))
    scene.render.filepath = os.path.join(qa_dir, "hero_34.png")
    bpy.ops.render.render(write_still=True)
    
    # 2. Front View (Looking along X into the clamp opening)
    cam_obj.location = (0.12, 0.0, 0.02)
    cam_obj.rotation_euler = (math.radians(85), 0, math.radians(90))
    scene.render.filepath = os.path.join(qa_dir, "front_flat.png")
    bpy.ops.render.render(write_still=True)
    
    # 3. Top View
    cam_obj.location = (0.0, 0.0, 0.15)
    cam_obj.rotation_euler = (0, 0, 0)
    scene.render.filepath = os.path.join(qa_dir, "top_ortho.png")
    bpy.ops.render.render(write_still=True)
    
    print("Asset 72 QA renders completed.")

if __name__ == "__main__":
    export_dir = r"C:\Users\Burak\Desktop\Security_CCTV\72. SEC_Conduit_Wall_Clamp\exports"
    qa_dir = r"C:\Users\Burak\Desktop\Security_CCTV\72. SEC_Conduit_Wall_Clamp\qa"
    render_qa(export_dir, qa_dir)
