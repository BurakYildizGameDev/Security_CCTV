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
        bsdf.inputs['Metallic'].default_value = 0.70
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

    # Slot 2: M_Emission
    mat_emission = bpy.data.materials.get("M_Emission")
    if not mat_emission:
        mat_emission = bpy.data.materials.new(name="M_Emission")
        mat_emission.use_nodes = True
        mat_emission.diffuse_color = (0.2, 1.0, 0.3, 1.0)
        nodes = mat_emission.node_tree.nodes
        links = mat_emission.node_tree.links
        nodes.clear()
        
        output = nodes.new(type='ShaderNodeOutputMaterial')
        emit_node = nodes.new(type='ShaderNodeEmission')
        emit_node.inputs['Color'].default_value = (0.2, 1.0, 0.3, 1.0)
        emit_node.inputs['Strength'].default_value = 5.0
        links.new(emit_node.outputs['Emission'], output.inputs['Surface'])

    return [mat_atlas, mat_metal, mat_emission]

def assign_material_slots(obj, materials, primary_slot=0):
    obj.data.materials.clear()
    for mat in materials:
        obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = primary_slot

def create_box_mesh(name, size, origin_offset=(0,0,0)):
    # Returns mesh object centered or offset
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    # size is (dx, dy, dz)
    dx, dy, dz = size[0]*0.5, size[1]*0.5, size[2]*0.5
    ox, oy, oz = origin_offset
    
    verts = [
        bm.verts.new((ox - dx, oy - dy, oz - dz)),
        bm.verts.new((ox + dx, oy - dy, oz - dz)),
        bm.verts.new((ox + dx, oy + dy, oz - dz)),
        bm.verts.new((ox - dx, oy + dy, oz - dz)),
        bm.verts.new((ox - dx, oy - dy, oz + dz)),
        bm.verts.new((ox + dx, oy - dy, oz + dz)),
        bm.verts.new((ox + dx, oy + dy, oz + dz)),
        bm.verts.new((ox - dx, oy + dy, oz + dz)),
    ]
    
    # Faces: Bottom, Top, Front(-Y), Back(+Y), Left(-X), Right(+X)
    faces = [
        (verts[0], verts[3], verts[2], verts[1]), # Bottom -Z
        (verts[4], verts[5], verts[6], verts[7]), # Top +Z
        (verts[0], verts[1], verts[5], verts[4]), # Front -Y
        (verts[2], verts[3], verts[7], verts[6]), # Back +Y
        (verts[0], verts[4], verts[7], verts[3]), # Left -X
        (verts[1], verts[2], verts[6], verts[5]), # Right +X
    ]
    for f in faces:
        bm.faces.new(f)
        
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def uv_unwrap_pdu_housing(obj):
    me = obj.data
    uv_layer = me.uv_layers.new(name="UVMap")
    
    # Atlas UV Regions:
    # Front strip: u [0.01, 0.24], v [0.01, 0.99]
    # Metal sides/back: u [0.55, 0.95], v [0.55, 0.95]
    # Brackets: u [0.55, 0.95], v [0.05, 0.45]
    
    for poly in me.polygons:
        normal = poly.normal
        # Check if front face (-Y normal)
        if normal.y < -0.7:
            # Front face
            poly.material_index = 0
            for loop_idx in poly.loop_indices:
                v = me.vertices[me.loops[loop_idx].vertex_index].co
                # v.x in [-0.024, 0.024], v.z in [-0.30, 0.30]
                u = 0.01 + ((v.x + 0.024) / 0.048) * (0.24 - 0.01)
                vv = 0.01 + ((v.z + 0.30) / 0.60) * (0.99 - 0.01)
                uv_layer.data[loop_idx].uv = (u, vv)
        elif abs(normal.z) > 0.8:
            # Top/bottom brackets or ends
            poly.material_index = 1
            for loop_idx in poly.loop_indices:
                v = me.vertices[me.loops[loop_idx].vertex_index].co
                u = 0.55 + ((v.x + 0.024) / 0.048) * 0.4
                vv = 0.05 + ((v.y + 0.0225) / 0.045) * 0.4
                uv_layer.data[loop_idx].uv = (u, vv)
        else:
            # Left, Right, Rear (+Y)
            poly.material_index = 1
            for loop_idx in poly.loop_indices:
                v = me.vertices[me.loops[loop_idx].vertex_index].co
                u = 0.55 + ((v.x + 0.024) / 0.048) * 0.4
                vv = 0.55 + ((v.z + 0.30) / 0.60) * 0.4
                uv_layer.data[loop_idx].uv = (u, vv)

def uv_unwrap_box_region(obj, u_min, u_max, v_min, v_max, mat_idx=0):
    me = obj.data
    uv_layer = me.uv_layers.new(name="UVMap")
    # Find bounding box in X and Z
    xs = [v.co.x for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)
    span_x = max(0.0001, max_x - min_x)
    span_z = max(0.0001, max_z - min_z)
    
    for poly in me.polygons:
        poly.material_index = mat_idx
        for loop_idx in poly.loop_indices:
            v = me.vertices[me.loops[loop_idx].vertex_index].co
            u = u_min + ((v.x - min_x) / span_x) * (u_max - u_min)
            vv = v_min + ((v.z - min_z) / span_z) * (v_max - v_min)
            uv_layer.data[loop_idx].uv = (max(u_min, min(u_max, u)), max(v_min, min(v_max, vv)))

def build_pdu_housing():
    mesh = bpy.data.meshes.new("PDU_Housing")
    bm = bmesh.new()
    
    # Main extrusion: W=0.048 (X: -0.024 to 0.024), D=0.045 (Y: -0.0225 to 0.0225), H=0.60 (Z: -0.30 to 0.30)
    dx, dy, dz = 0.024, 0.0225, 0.30
    
    # 8 corners of main chassis
    c = [
        bm.verts.new((-dx, -dy, -dz)),
        bm.verts.new(( dx, -dy, -dz)),
        bm.verts.new(( dx,  dy, -dz)),
        bm.verts.new((-dx,  dy, -dz)),
        bm.verts.new((-dx, -dy,  dz)),
        bm.verts.new(( dx, -dy,  dz)),
        bm.verts.new(( dx,  dy,  dz)),
        bm.verts.new((-dx,  dy,  dz)),
    ]
    
    # Main faces
    bm.faces.new((c[0], c[1], c[5], c[4])) # Front (-Y)
    bm.faces.new((c[2], c[3], c[7], c[6])) # Back (+Y)
    bm.faces.new((c[0], c[4], c[7], c[3])) # Left (-X)
    bm.faces.new((c[1], c[2], c[6], c[5])) # Right (+X)
    
    # Top flange (+Z)
    flange_h = 0.025
    flange_t = 0.003
    t1 = bm.verts.new((-dx, dy - flange_t, dz))
    t2 = bm.verts.new(( dx, dy - flange_t, dz))
    t3 = bm.verts.new(( dx, dy, dz + flange_h))
    t4 = bm.verts.new((-dx, dy, dz + flange_h))
    bm.faces.new((c[4], c[5], c[6], c[7])) # Chassis top cap
    bm.faces.new((t1, t2, t3, t4)) # Flange front
    
    # Bottom flange (-Z)
    b1 = bm.verts.new((-dx, dy - flange_t, -dz))
    b2 = bm.verts.new(( dx, dy - flange_t, -dz))
    b3 = bm.verts.new(( dx, dy, -dz - flange_h))
    b4 = bm.verts.new((-dx, dy, -dz - flange_h))
    bm.faces.new((c[0], c[3], c[2], c[1])) # Chassis bottom cap
    bm.faces.new((b1, b2, b3, b4)) # Flange front
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("PDU_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_socket_mesh(name):
    # Low-poly socket cup: W=0.038, H=0.038, D=0.006 recessed/beveled frame
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    sx, sz = 0.018, 0.018
    # Outer bezel on front surface (Y=0.0)
    v0 = bm.verts.new((-sx, 0.0, -sz))
    v1 = bm.verts.new(( sx, 0.0, -sz))
    v2 = bm.verts.new(( sx, 0.0,  sz))
    v3 = bm.verts.new((-sx, 0.0,  sz))
    
    # Inner cup recessed slightly forward/backward (Y=-0.004)
    ix, iz = 0.014, 0.014
    v4 = bm.verts.new((-ix, -0.004, -iz))
    v5 = bm.verts.new(( ix, -0.004, -iz))
    v6 = bm.verts.new(( ix, -0.004,  iz))
    v7 = bm.verts.new((-ix, -0.004,  iz))
    
    # Bevel border faces
    bm.faces.new((v0, v1, v5, v4))
    bm.faces.new((v1, v2, v6, v5))
    bm.faces.new((v2, v3, v7, v6))
    bm.faces.new((v3, v0, v4, v7))
    # Bottom plate of socket
    bm.faces.new((v4, v5, v6, v7))
    
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_switch_mesh(name):
    # Rocker switch button
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    w, h, d = 0.010, 0.016, 0.006
    # 2-faceted rocker switch
    # Pivot is at (0, 0, 0). Switch tilts around X axis.
    v_top_l = bm.verts.new((-w, -d*0.6,  h))
    v_top_r = bm.verts.new(( w, -d*0.6,  h))
    v_mid_l = bm.verts.new((-w, -d,      0.0))
    v_mid_r = bm.verts.new(( w, -d,      0.0))
    v_bot_l = bm.verts.new((-w, -d*0.6, -h))
    v_bot_r = bm.verts.new(( w, -d*0.6, -h))
    
    # Base verts
    b_top_l = bm.verts.new((-w, 0.0,  h))
    b_top_r = bm.verts.new(( w, 0.0,  h))
    b_bot_l = bm.verts.new((-w, 0.0, -h))
    b_bot_r = bm.verts.new(( w, 0.0, -h))
    
    # Front angled faces
    bm.faces.new((v_mid_l, v_mid_r, v_top_r, v_top_l))
    bm.faces.new((v_bot_l, v_bot_r, v_mid_r, v_mid_l))
    # Side faces
    bm.faces.new((b_top_l, v_top_l, v_mid_l, v_bot_l, b_bot_l))
    bm.faces.new((v_top_r, b_top_r, b_bot_r, v_bot_r, v_mid_r))
    # Top & bottom caps
    bm.faces.new((b_top_r, v_top_r, v_top_l, b_top_l))
    bm.faces.new((b_bot_l, v_bot_l, v_bot_r, b_bot_r))
    
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_led_mesh(name):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    r = 0.004
    d = 0.003
    # 8-sided cylinder/dome for LED
    segs = 8
    front_verts = []
    base_verts = []
    for i in range(segs):
        ang = (2 * math.pi * i) / segs
        x = r * math.cos(ang)
        z = r * math.sin(ang)
        front_verts.append(bm.verts.new((x, -d, z)))
        base_verts.append(bm.verts.new((x, 0.0, z)))
        
    for i in range(segs):
        i_next = (i + 1) % segs
        bm.faces.new((base_verts[i], base_verts[i_next], front_verts[i_next], front_verts[i]))
        
    bm.faces.new(reversed(front_verts))
    bm.faces.new(base_verts)
    
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def generate_asset():
    clear_scene()
    setup_units()
    
    base_dir = os.path.abspath(r"C:\Users\Burak\Desktop\Security_CCTV\59. SEC_Power_Distribution_Unit")
    exports_dir = os.path.join(base_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")
    
    materials = get_or_create_materials(atlas_path)
    
    # 1. Root Empty: SEC_Power_Distribution_Unit
    root = bpy.data.objects.new("SEC_Power_Distribution_Unit", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.1
    bpy.context.collection.objects.link(root)
    root.location = (0.0, 0.0, 0.0)
    
    # 2. PDU_Housing Mesh
    housing = build_pdu_housing()
    assign_material_slots(housing, materials, primary_slot=0)
    uv_unwrap_pdu_housing(housing)
    housing.parent = root
    housing.location = (0.0, 0.0, 0.0)
    
    # 3. Main_Switch_Pivot Empty (child of Housing)
    # Front face is at Y = -0.0225. Rocker switch located at Z = 0.22.
    switch_pivot = bpy.data.objects.new("Main_Switch_Pivot", None)
    switch_pivot.empty_display_type = 'ARROWS'
    switch_pivot.empty_display_size = 0.025
    bpy.context.collection.objects.link(switch_pivot)
    switch_pivot.parent = housing
    switch_pivot.location = (0.0, -0.0225, 0.22)
    
    # Limit rotation on switch_pivot (Local X ±25°)
    rot_limit = switch_pivot.constraints.new(type='LIMIT_ROTATION')
    rot_limit.use_limit_x = True
    rot_limit.min_x = math.radians(-25.0)
    rot_limit.max_x = math.radians(25.0)
    rot_limit.use_limit_y = True
    rot_limit.min_y = 0.0
    rot_limit.max_y = 0.0
    rot_limit.use_limit_z = True
    rot_limit.min_z = 0.0
    rot_limit.max_z = 0.0
    rot_limit.owner_space = 'LOCAL'
    
    switch_pivot["tilt_axis"] = "X"
    switch_pivot["tilt_min_deg"] = -25.0
    switch_pivot["tilt_max_deg"] = 25.0
    
    # 4. Main_Switch Mesh (child of Main_Switch_Pivot)
    switch_mesh = build_switch_mesh("Main_Switch")
    assign_material_slots(switch_mesh, materials, primary_slot=0)
    # UV map to switch rocker region: u [0.2686, 0.5127], v [0.4629, 0.7070]
    uv_unwrap_box_region(switch_mesh, 0.27, 0.51, 0.46, 0.70, mat_idx=0)
    switch_mesh.parent = switch_pivot
    switch_mesh.location = (0.0, 0.0, 0.0)
    
    # 5. Status_LED Mesh (child of Housing)
    # Located at Z = 0.17 on front face
    led_obj = build_led_mesh("Status_LED")
    assign_material_slots(led_obj, materials, primary_slot=2) # Slot 2 M_Emission
    uv_unwrap_box_region(led_obj, 0.27, 0.51, 0.29, 0.44, mat_idx=2)
    led_obj.parent = housing
    led_obj.location = (0.0, -0.0225, 0.17)
    
    # 6. Sockets 01..08 (children of Housing)
    # Distributed along Z from 0.10 down to -0.27
    socket_z_start = 0.10
    socket_step = 0.052
    
    sockets = []
    for i in range(8):
        s_name = f"Socket_{i+1:02d}"
        s_obj = build_socket_mesh(s_name)
        assign_material_slots(s_obj, materials, primary_slot=0)
        # UV map to socket detailed region: u [0.27, 0.51], v [0.73, 0.98]
        uv_unwrap_box_region(s_obj, 0.27, 0.51, 0.73, 0.98, mat_idx=0)
        s_obj.parent = housing
        s_obj.location = (0.0, -0.0225, socket_z_start - i * socket_step)
        sockets.append(s_obj)
        
    bpy.context.view_layer.update()
    
    # Calculate triangle count
    all_meshes = [housing, switch_mesh, led_obj] + sockets
    total_tris = 0
    for m in all_meshes:
        me = m.data
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        total_tris += len(bm.faces)
        bm.free()
        
    print(f"[Geometry] Total meshes: {len(all_meshes)}, Total tris: {total_tris} (limit: 430)")
    assert total_tris <= 430, f"Triangle count {total_tris} exceeds limit 430!"

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
    blend_path = os.path.join(exports_dir, "SEC_Power_Distribution_Unit.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Power_Distribution_Unit.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    housing.select_set(True)
    switch_pivot.select_set(True)
    switch_mesh.select_set(True)
    led_obj.select_set(True)
    for s in sockets:
        s.select_set(True)
        
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
    
    # Verify in clean test scene
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
    
    # Check hierarchy
    imp_root = bpy.data.objects.get("SEC_Power_Distribution_Unit")
    imp_housing = bpy.data.objects.get("PDU_Housing")
    imp_switch_pivot = bpy.data.objects.get("Main_Switch_Pivot")
    imp_switch = bpy.data.objects.get("Main_Switch")
    imp_led = bpy.data.objects.get("Status_LED")
    
    status = "SUCCESS"
    if not imp_root or not imp_housing or not imp_switch_pivot or not imp_switch or not imp_led:
        status = "FAILED"
    if len(imp_meshes) != 11 or len(imp_empties) != 2:
        status = "FAILED"
    if reimport_tris > 430:
        status = "FAILED"
        
    # Manifest update
    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}
            
    manifest_data["SEC_Power_Distribution_Unit"] = {
        "asset_name": "SEC_Power_Distribution_Unit",
        "fbx_path": fbx_path,
        "tris_count": reimport_tris,
        "mesh_count": len(imp_meshes),
        "empty_count": len(imp_empties),
        "materials": ["M_Security_Atlas", "M_Metal", "M_Emission"],
        "status": status
    }
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=4)
        
    print(f"[Manifest] Updated {manifest_path} with status {status}")
    
    # Clean up .blend1
    blend1 = blend_path + "1"
    if os.path.exists(blend1):
        os.remove(blend1)
        
    if status != "SUCCESS":
        raise RuntimeError("QA verification failed for SEC_Power_Distribution_Unit")

if __name__ == "__main__":
    generate_asset()
