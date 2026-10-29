import bpy
import bmesh
import math
import os
import json

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def setup_units():
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.scene.unit_settings.length_unit = 'METERS'

def get_or_create_materials(atlas_path):
    # Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.get("M_Security_Atlas")
    if not mat_atlas:
        mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
        mat_atlas.use_nodes = True
        mat_atlas.diffuse_color = (0.15, 0.17, 0.22, 1.0)
        nodes = mat_atlas.node_tree.nodes
        links = mat_atlas.node_tree.links
        nodes.clear()
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        tex_node = nodes.new(type='ShaderNodeTexImage')
        
        if os.path.exists(atlas_path):
            img = bpy.data.images.load(atlas_path)
            tex_node.image = img
            
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = 0.35
        bsdf.inputs['Metallic'].default_value = 0.65
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    # Slot 1: M_Metal
    mat_metal = bpy.data.materials.get("M_Metal")
    if not mat_metal:
        mat_metal = bpy.data.materials.new(name="M_Metal")
        mat_metal.use_nodes = True
        mat_metal.diffuse_color = (0.65, 0.70, 0.75, 1.0)
        nodes = mat_metal.node_tree.nodes
        links = mat_metal.node_tree.links
        nodes.clear()
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        tex_node = nodes.new(type='ShaderNodeTexImage')
        if os.path.exists(atlas_path):
            img = bpy.data.images.load(atlas_path)
            tex_node.image = img
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        bsdf.inputs['Metallic'].default_value = 0.90
        bsdf.inputs['Roughness'].default_value = 0.25
        links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return [mat_atlas, mat_metal]

def assign_material_slots(obj, materials, primary_slot=0):
    obj.data.materials.clear()
    for mat in materials:
        obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = primary_slot

def build_housing_mesh():
    mesh = bpy.data.meshes.new("Housing")
    bm = bmesh.new()
    
    # 2U rack battery body:
    # Body width: 0.44m (X: -0.22 to 0.22)
    # Rack ear extension width: 0.4826m (X: -0.2413 to 0.2413)
    # Height: 0.088m (Z: -0.044 to 0.044)
    # Depth: 0.42m (Y: -0.21 to 0.21)
    
    bx, by, bz = 0.22, 0.21, 0.044
    ex = 0.2413
    
    # Main enclosure body verts
    # 0..7
    c = [
        bm.verts.new((-bx, -by, -bz)), # 0: Front-Left-Bottom
        bm.verts.new(( bx, -by, -bz)), # 1: Front-Right-Bottom
        bm.verts.new(( bx,  by, -bz)), # 2: Back-Right-Bottom
        bm.verts.new((-bx,  by, -bz)), # 3: Back-Left-Bottom
        bm.verts.new((-bx, -by,  bz)), # 4: Front-Left-Top
        bm.verts.new(( bx, -by,  bz)), # 5: Front-Right-Top
        bm.verts.new(( bx,  by,  bz)), # 6: Back-Right-Top
        bm.verts.new((-bx,  by,  bz)), # 7: Back-Left-Top
    ]
    
    # Faces of main body
    bm.faces.new((c[0], c[1], c[5], c[4])) # Front (-Y)
    bm.faces.new((c[2], c[3], c[7], c[6])) # Back (+Y)
    bm.faces.new((c[0], c[4], c[7], c[3])) # Left (-X)
    bm.faces.new((c[1], c[2], c[6], c[5])) # Right (+X)
    bm.faces.new((c[4], c[5], c[6], c[7])) # Top (+Z)
    bm.faces.new((c[0], c[3], c[2], c[1])) # Bottom (-Z)
    
    # Left rack ear (-X)
    ear_t = 0.003
    le0 = bm.verts.new((-ex, -by, -bz))
    le1 = bm.verts.new((-bx, -by, -bz))
    le2 = bm.verts.new((-bx, -by + ear_t, -bz))
    le3 = bm.verts.new((-ex, -by + ear_t, -bz))
    le4 = bm.verts.new((-ex, -by,  bz))
    le5 = bm.verts.new((-bx, -by,  bz))
    le6 = bm.verts.new((-bx, -by + ear_t,  bz))
    le7 = bm.verts.new((-ex, -by + ear_t,  bz))
    
    bm.faces.new((le0, le1, le5, le4)) # Front
    bm.faces.new((le2, le3, le7, le6)) # Back
    bm.faces.new((le0, le4, le7, le3)) # Outer left
    bm.faces.new((le4, le5, le6, le7)) # Top
    bm.faces.new((le0, le3, le2, le1)) # Bottom
    
    # Right rack ear (+X)
    re0 = bm.verts.new(( bx, -by, -bz))
    re1 = bm.verts.new(( ex, -by, -bz))
    re2 = bm.verts.new(( ex, -by + ear_t, -bz))
    re3 = bm.verts.new(( bx, -by + ear_t, -bz))
    re4 = bm.verts.new(( bx, -by,  bz))
    re5 = bm.verts.new(( ex, -by,  bz))
    re6 = bm.verts.new(( ex, -by + ear_t,  bz))
    re7 = bm.verts.new(( bx, -by + ear_t,  bz))
    
    bm.faces.new((re0, re1, re5, re4)) # Front
    bm.faces.new((re2, re3, re7, re6)) # Back
    bm.faces.new((re1, re2, re6, re5)) # Outer right
    bm.faces.new((re4, re5, re6, re7)) # Top
    bm.faces.new((re0, re3, re2, re1)) # Bottom

    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def uv_unwrap_battery_housing(obj):
    me = obj.data
    uv_layer = me.uv_layers.new(name="UVMap")
    
    ex = 0.2413
    total_w = 2.0 * ex
    h = 0.088
    
    for poly in me.polygons:
        normal = poly.normal
        if normal.y < -0.7:
            # Front face (-Y)
            poly.material_index = 0
            for loop_idx in poly.loop_indices:
                v = me.vertices[me.loops[loop_idx].vertex_index].co
                u = 0.0195 + ((v.x + ex) / total_w) * (0.9570 - 0.0195)
                vv = 0.7949 + ((v.z + 0.044) / h) * (0.9805 - 0.7949)
                uv_layer.data[loop_idx].uv = (u, vv)
        elif normal.z > 0.7:
            # Top face (+Z) with big warning labels
            poly.material_index = 0
            for loop_idx in poly.loop_indices:
                v = me.vertices[me.loops[loop_idx].vertex_index].co
                u = 0.02 + ((v.x + 0.22) / 0.44) * 0.94
                vv = 0.27 + ((v.y + 0.21) / 0.42) * 0.26
                uv_layer.data[loop_idx].uv = (u, vv)
        else:
            # Sides, Back, Bottom
            poly.material_index = 1
            for loop_idx in poly.loop_indices:
                v = me.vertices[me.loops[loop_idx].vertex_index].co
                u = 0.05 + ((v.x + 0.22) / 0.44) * 0.8
                vv = 0.02 + ((v.y + 0.21) / 0.42) * 0.20
                uv_layer.data[loop_idx].uv = (u, vv)

def build_pull_handle():
    # U-shaped handle bar
    # Pivot is at (0, 0, 0)
    mesh = bpy.data.meshes.new("Pull_Handle")
    bm = bmesh.new()
    
    hw = 0.070 # Half-width = 70mm -> total 140mm width
    arm_len = 0.028 # Distance protruding forward from front face
    bar_thick = 0.006 # Thickness of bar
    
    # Left arm, Right arm, Crossbar in local coords
    # Pivot at front face Y=0. Handle extends forward (-Y)
    
    # Left arm: X: -hw to -hw + bar_thick, Y: 0 to -arm_len, Z: -bar_thick to bar_thick
    # Right arm: X: hw - bar_thick to hw, Y: 0 to -arm_len, Z: -bar_thick to bar_thick
    # Front crossbar: X: -hw to hw, Y: -arm_len to -arm_len - bar_thick, Z: -bar_thick to bar_thick
    
    # We can create a simple 12-vert U profile extruded in Z
    # Profile points in X-Y plane:
    bt = bar_thick
    p_outer = [
        (-hw, 0.0),
        (-hw, -arm_len - bt),
        ( hw, -arm_len - bt),
        ( hw, 0.0),
        ( hw - bt, 0.0),
        ( hw - bt, -arm_len),
        (-hw + bt, -arm_len),
        (-hw + bt, 0.0),
    ]
    
    bottom_verts = []
    top_verts = []
    for px, py in p_outer:
        bottom_verts.append(bm.verts.new((px, py, -bt)))
        top_verts.append(bm.verts.new((px, py, bt)))
        
    n = len(p_outer)
    for i in range(n):
        i_next = (i + 1) % n
        bm.faces.new((bottom_verts[i], bottom_verts[i_next], top_verts[i_next], top_verts[i]))
        
    bm.faces.new(bottom_verts) # Bottom cap
    bm.faces.new(reversed(top_verts)) # Top cap
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Pull_Handle", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_terminal_mesh(name):
    # Hex nut base + central contact post
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    r_base = 0.010
    d_base = 0.006
    # 6-sided base nut
    segs = 6
    b_base = []
    f_base = []
    for i in range(segs):
        ang = (2 * math.pi * i) / segs
        x = r_base * math.cos(ang)
        z = r_base * math.sin(ang)
        b_base.append(bm.verts.new((x, 0.0, z)))
        f_base.append(bm.verts.new((x, -d_base, z)))
        
    for i in range(segs):
        i_next = (i + 1) % segs
        bm.faces.new((b_base[i], b_base[i_next], f_base[i_next], f_base[i]))
    bm.faces.new(reversed(f_base))
    bm.faces.new(b_base)
    
    # Central terminal stud
    r_stud = 0.005
    d_stud = 0.012
    b_stud = []
    f_stud = []
    for i in range(segs):
        ang = (2 * math.pi * i) / segs
        x = r_stud * math.cos(ang)
        z = r_stud * math.sin(ang)
        b_stud.append(bm.verts.new((x, -d_base, z)))
        f_stud.append(bm.verts.new((x, -d_stud, z)))
        
    for i in range(segs):
        i_next = (i + 1) % segs
        bm.faces.new((b_stud[i], b_stud[i_next], f_stud[i_next], f_stud[i]))
    bm.faces.new(reversed(f_stud))
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def uv_unwrap_handle(obj):
    me = obj.data
    uv_layer = me.uv_layers.new(name="UVMap")
    # Region: u in [0.03, 0.38], v in [0.58, 0.75]
    u_min, u_max = 0.03, 0.38
    v_min, v_max = 0.58, 0.75
    hw = 0.070
    for poly in me.polygons:
        poly.material_index = 0
        for loop_idx in poly.loop_indices:
            v = me.vertices[me.loops[loop_idx].vertex_index].co
            u = u_min + ((v.x + hw) / (2.0 * hw)) * (u_max - u_min)
            vv = v_min + ((v.z + 0.01) / 0.02) * (v_max - v_min)
            uv_layer.data[loop_idx].uv = (max(u_min, min(u_max, u)), max(v_min, min(v_max, vv)))

def uv_unwrap_terminal(obj, u_min, u_max, v_min, v_max):
    me = obj.data
    uv_layer = me.uv_layers.new(name="UVMap")
    r = 0.010
    for poly in me.polygons:
        poly.material_index = 0
        for loop_idx in poly.loop_indices:
            v = me.vertices[me.loops[loop_idx].vertex_index].co
            u = u_min + ((v.x + r) / (2.0 * r)) * (u_max - u_min)
            vv = v_min + ((v.z + r) / (2.0 * r)) * (v_max - v_min)
            uv_layer.data[loop_idx].uv = (max(u_min, min(u_max, u)), max(v_min, min(v_max, vv)))

def generate_asset():
    clear_scene()
    setup_units()
    
    base_dir = os.path.abspath(r"C:\Users\Burak\Desktop\Security_CCTV\60. SEC_Battery_Module")
    exports_dir = os.path.join(base_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")
    
    materials = get_or_create_materials(atlas_path)
    
    # 1. Root Empty: SEC_Battery_Module at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Battery_Module", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.15
    bpy.context.collection.objects.link(root)
    root.location = (0.0, 0.0, 0.0)
    
    # 2. Housing Mesh (child of Root)
    housing = build_housing_mesh()
    assign_material_slots(housing, materials, primary_slot=0)
    uv_unwrap_battery_housing(housing)
    housing.parent = root
    housing.location = (0.0, 0.0, 0.0)
    
    # 3. Pull_Handle_Pivot Empty (child of Housing)
    # Placed on front face: Y = -0.21, centered at X = 0.0, Z = 0.0
    handle_pivot = bpy.data.objects.new("Pull_Handle_Pivot", None)
    handle_pivot.empty_display_type = 'ARROWS'
    handle_pivot.empty_display_size = 0.05
    bpy.context.collection.objects.link(handle_pivot)
    handle_pivot.parent = housing
    handle_pivot.location = (0.0, -0.21, 0.0)
    
    # Limit rotation on Pull_Handle_Pivot (Local X ±20°)
    rot_limit = handle_pivot.constraints.new(type='LIMIT_ROTATION')
    rot_limit.use_limit_x = True
    rot_limit.min_x = math.radians(-20.0)
    rot_limit.max_x = math.radians(20.0)
    rot_limit.use_limit_y = True
    rot_limit.min_y = 0.0
    rot_limit.max_y = 0.0
    rot_limit.use_limit_z = True
    rot_limit.min_z = 0.0
    rot_limit.max_z = 0.0
    rot_limit.owner_space = 'LOCAL'
    
    handle_pivot["tilt_axis"] = "X"
    handle_pivot["tilt_min_deg"] = -20.0
    handle_pivot["tilt_max_deg"] = 20.0
    
    # 4. Pull_Handle Mesh (child of Pull_Handle_Pivot)
    handle_obj = build_pull_handle()
    assign_material_slots(handle_obj, materials, primary_slot=0)
    uv_unwrap_handle(handle_obj)
    handle_obj.parent = handle_pivot
    handle_obj.location = (0.0, 0.0, 0.0)
    
    # 5. Terminal_Positive Mesh (child of Housing)
    term_pos = build_terminal_mesh("Terminal_Positive")
    assign_material_slots(term_pos, materials, primary_slot=0)
    uv_unwrap_terminal(term_pos, 0.43, 0.60, 0.58, 0.75)
    term_pos.parent = housing
    term_pos.location = (0.116, -0.21, 0.016)
    
    # 6. Terminal_Negative Mesh (child of Housing)
    term_neg = build_terminal_mesh("Terminal_Negative")
    assign_material_slots(term_neg, materials, primary_slot=0)
    uv_unwrap_terminal(term_neg, 0.65, 0.82, 0.58, 0.75)
    term_neg.parent = housing
    term_neg.location = (0.116, -0.21, -0.016)
    
    bpy.context.view_layer.update()
    
    # Triangle count
    all_meshes = [housing, handle_obj, term_pos, term_neg]
    total_tris = 0
    for m in all_meshes:
        me = m.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        total_tris += len(bm.faces)
        bm.free()
        
    print(f"[Geometry] Total meshes: {len(all_meshes)}, Total tris: {total_tris} (limit: 360)")
    assert total_tris <= 360, f"Triangle count {total_tris} exceeds limit 360!"

    # Set viewport shading to MATERIAL and color_type to TEXTURE
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'

    # Pack all images into .blend
    bpy.ops.file.pack_all()

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Battery_Module.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Battery_Module.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    housing.select_set(True)
    handle_pivot.select_set(True)
    handle_obj.select_set(True)
    term_pos.select_set(True)
    term_neg.select_set(True)
    
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        object_types={'MESH', 'EMPTY'},
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,
        bake_space_transform=False,
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode='AUTO'
    )
    print(f"[Export] Saved FBX: {fbx_path}")
    
    # Clean verification
    clear_scene()
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    imported_objs = bpy.context.scene.objects
    imp_meshes = [o for o in imported_objs if o.type == 'MESH']
    imp_empties = [o for o in imported_objs if o.type == 'EMPTY']
    
    reimport_tris = 0
    for m in imp_meshes:
        bm = bmesh.new()
        bm.from_mesh(m.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        reimport_tris += len(bm.faces)
        bm.free()
        
    print(f"[QA Reimport] Meshes: {len(imp_meshes)}, Empties: {len(imp_empties)}, Tris: {reimport_tris}")
    
    imp_root = bpy.data.objects.get("SEC_Battery_Module")
    imp_housing = bpy.data.objects.get("Housing")
    imp_pivot = bpy.data.objects.get("Pull_Handle_Pivot")
    imp_handle = bpy.data.objects.get("Pull_Handle")
    imp_pos = bpy.data.objects.get("Terminal_Positive")
    imp_neg = bpy.data.objects.get("Terminal_Negative")
    
    status = "SUCCESS"
    if not imp_root or not imp_housing or not imp_pivot or not imp_handle or not imp_pos or not imp_neg:
        status = "FAILED"
    if len(imp_meshes) != 4 or len(imp_empties) != 2:
        status = "FAILED"
    if reimport_tris > 360:
        status = "FAILED"
        
    # Update manifest
    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}
            
    manifest_data["SEC_Battery_Module"] = {
        "asset_name": "SEC_Battery_Module",
        "fbx_path": fbx_path,
        "tris_count": reimport_tris,
        "mesh_count": len(imp_meshes),
        "empty_count": len(imp_empties),
        "materials": ["M_Security_Atlas", "M_Metal"],
        "status": status
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=4)
        
    print(f"[Manifest] Updated {manifest_path} with status {status}")
    
    blend1 = blend_path + "1"
    if os.path.exists(blend1):
        os.remove(blend1)
        
    if status != "SUCCESS":
        raise RuntimeError("QA verification failed for SEC_Battery_Module")

if __name__ == "__main__":
    generate_asset()
