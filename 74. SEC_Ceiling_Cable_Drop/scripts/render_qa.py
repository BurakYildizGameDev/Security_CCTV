import os
import math
import bpy

def render_qa(export_dir, qa_dir):
    blend_path = os.path.join(export_dir, "SEC_Ceiling_Cable_Drop.blend")
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
        bg.inputs['Color'].default_value = (0.24, 0.26, 0.28, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    cam_data = bpy.data.cameras.new("QACam")
    cam_obj = bpy.data.objects.new("QACam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Studio Lights
    light_data = bpy.data.lights.new(name="KeyLight", type='SUN')
    light_data.energy = 18.0
    light_obj = bpy.data.objects.new(name="KeyLight", object_data=light_data)
    light_obj.rotation_euler = (math.radians(50), math.radians(25), math.radians(45))
    scene.collection.objects.link(light_obj)

    fill_data = bpy.data.lights.new(name="FillLight", type='SUN')
    fill_data.energy = 10.0
    fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(-35), math.radians(-30), math.radians(140))
    scene.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new(name="RimLight", type='SUN')
    rim_data.energy = 8.0
    rim_obj = bpy.data.objects.new(name="RimLight", object_data=rim_data)
    rim_obj.rotation_euler = (math.radians(70), math.radians(-60), math.radians(-40))
    scene.collection.objects.link(rim_obj)

    # Track target at midpoint of cable drop (0.0, 0.0, -0.22)
    target_empty = bpy.data.objects.new("TargetEmpty", None)
    target_empty.location = (0.0, 0.0, -0.22)
    scene.collection.objects.link(target_empty)

    track_con = cam_obj.constraints.new(type='TRACK_TO')
    track_con.target = target_empty
    track_con.track_axis = 'TRACK_NEGATIVE_Z'
    track_con.up_axis = 'UP_Y'

    os.makedirs(qa_dir, exist_ok=True)

    # 1. Hero 3/4 View
    cam_obj.location = (0.45, -0.45, -0.10)
    bpy.context.view_layer.update()
    scene.render.filepath = os.path.join(qa_dir, "hero_34.png")
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered: {scene.render.filepath}")

    # 2. Front View
    cam_obj.location = (0.0, -0.65, -0.22)
    bpy.context.view_layer.update()
    scene.render.filepath = os.path.join(qa_dir, "front_flat.png")
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered: {scene.render.filepath}")

    # 3. Bottom Angled View (showing ceiling rosette mounting screws & cable exit)
    cam_obj.location = (0.28, -0.28, -0.48)
    bpy.context.view_layer.update()
    scene.render.filepath = os.path.join(qa_dir, "bottom_ortho.png")
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Rendered: {scene.render.filepath}")

    print("[QA] All 3 QA renders completed successfully.")

if __name__ == "__main__":
    exp_dir = r"C:\Users\Burak\Desktop\Security_CCTV\74. SEC_Ceiling_Cable_Drop\exports"
    q_dir = r"C:\Users\Burak\Desktop\Security_CCTV\74. SEC_Ceiling_Cable_Drop\qa"
    render_qa(exp_dir, q_dir)
