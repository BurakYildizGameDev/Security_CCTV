import bpy
import bmesh
import math
import os
import json

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for img in list(bpy.data.images):
        bpy.data.images.remove(img)

def setup_units():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

def create_materials(export_dir):
    atlas_path = os.path.join(export_dir, "T_Security_Atlas.png")
    
    # Slot 0: M_Metal
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    nodes_m = mat_metal.node_tree.nodes
    links_m = mat_metal.node_tree.links
    nodes_m.clear()
    
    out_m = nodes_m.new(type='ShaderNodeOutputMaterial')
    out_m.location = (400, 0)
    bsdf_m = nodes_m.new(type='ShaderNodeBsdfPrincipled')
    bsdf_m.location = (0, 0)
    bsdf_m.inputs['Metallic'].default_value = 0.88
    bsdf_m.inputs['Roughness'].default_value = 0.28
    
    if os.path.exists(atlas_path):
        tex_m = nodes_m.new(type='ShaderNodeTexImage')
        tex_m.location = (-400, 0)
        img = bpy.data.images.load(atlas_path)
        img.name = "T_Security_Atlas.png"
        tex_m.image = img
        links_m.new(tex_m.outputs['Color'], bsdf_m.inputs['Base Color'])
        nodes_m.active = tex_m
        
    links_m.new(bsdf_m.outputs['BSDF'], out_m.inputs['Surface'])
    mat_metal.diffuse_color = (0.88, 0.90, 0.92, 1.0)
    
    # Strictly OPAQUE
    if hasattr(mat_metal, 'blend_method'):
        mat_metal.blend_method = 'OPAQUE'
    if hasattr(mat_metal, 'shadow_method'):
        mat_metal.shadow_method = 'OPAQUE'
    
    # Slot 1: M_Rubber
    mat_rubber = bpy.data.materials.new(name="M_Rubber")
    mat_rubber.use_nodes = True
    nodes_r = mat_rubber.node_tree.nodes
    links_r = mat_rubber.node_tree.links
    nodes_r.clear()
    
    out_r = nodes_r.new(type='ShaderNodeOutputMaterial')
    out_r.location = (400, 0)
    bsdf_r = nodes_r.new(type='ShaderNodeBsdfPrincipled')
    bsdf_r.location = (0, 0)
    bsdf_r.inputs['Base Color'].default_value = (0.10, 0.11, 0.12, 1.0)
    bsdf_r.inputs['Metallic'].default_value = 0.0
    bsdf_r.inputs['Roughness'].default_value = 0.75
    links_r.new(bsdf_r.outputs['BSDF'], out_r.inputs['Surface'])
    mat_rubber.diffuse_color = (0.10, 0.11, 0.12, 1.0)
    
    if hasattr(mat_rubber, 'blend_method'):
        mat_rubber.blend_method = 'OPAQUE'
    if hasattr(mat_rubber, 'shadow_method'):
        mat_rubber.shadow_method = 'OPAQUE'
    
    return mat_metal, mat_rubber

def add_tube_segment(bm, p0, p1, radius=0.009, segments=10, mat_idx=0, uv_coord=(0.25, 0.75)):
    dx, dy, dz = p1[0]-p0[0], p1[1]-p0[1], p1[2]-p0[2]
    L = math.sqrt(dx*dx + dy*dy + dz*dz)
    if L < 1e-5:
        return []
    ux, uy, uz = dx/L, dy/L, dz/L
    if abs(uz) < 0.9:
        vx, vy, vz = -uy, ux, 0.0
    else:
        vx, vy, vz = 0.0, -uz, uy
    vL = math.sqrt(vx*vx + vy*vy + vz*vz)
    vx, vy, vz = vx/vL, vy/vL, vz/vL
    wx, wy, wz = uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx
    
    vb, vt = [], []
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        offset = (radius * (cos_a * vx + sin_a * wx),
                  radius * (cos_a * vy + sin_a * wy),
                  radius * (cos_a * vz + sin_a * wz))
        vb.append(bm.verts.new((p0[0] + offset[0], p0[1] + offset[1], p0[2] + offset[2])))
        vt.append(bm.verts.new((p1[0] + offset[0], p1[1] + offset[1], p1[2] + offset[2])))
        
    faces = []
    uv_layer = bm.loops.layers.uv.verify()
    for s in range(segments):
        sn = (s + 1) % segments
        f = bm.faces.new((vb[s], vb[sn], vt[sn], vt[s]))
        f.material_index = mat_idx
        for l in f.loops: l[uv_layer].uv = uv_coord
        faces.append(f)
    fb = bm.faces.new(reversed(vb))
    fb.material_index = mat_idx
    for l in fb.loops: l[uv_layer].uv = uv_coord
    ft = bm.faces.new(vt)
    ft.material_index = mat_idx
    for l in ft.loops: l[uv_layer].uv = uv_coord
    return faces

def add_cylinder_y(bm, center_xz, radius, y_min, y_max, segments=24, mat_idx=0, uv_coord=(0.25, 0.75), add_caps=True):
    cx, cz = center_xz
    vb, vt = [], []
    uv_layer = bm.loops.layers.uv.verify()
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        vb.append(bm.verts.new((cx + radius * math.cos(ang), y_min, cz + radius * math.sin(ang))))
        vt.append(bm.verts.new((cx + radius * math.cos(ang), y_max, cz + radius * math.sin(ang))))
        
    faces = []
    for s in range(segments):
        sn = (s + 1) % segments
        f = bm.faces.new((vb[s], vb[sn], vt[sn], vt[s]))
        f.material_index = mat_idx
        for l in f.loops: l[uv_layer].uv = uv_coord
        faces.append(f)
    if add_caps:
        fb = bm.faces.new(reversed(vb))
        fb.material_index = mat_idx
        for l in fb.loops: l[uv_layer].uv = uv_coord
        ft = bm.faces.new(vt)
        ft.material_index = mat_idx
        for l in ft.loops: l[uv_layer].uv = uv_coord
    return vb, vt, faces

def build_sec_cable_reel(export_dir):
    clear_scene()
    setup_units()
    
    mat_metal, mat_rubber = create_materials(export_dir)
    
    coll = bpy.data.collections.new("SEC_Cable_Reel_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    root = bpy.data.objects.new("SEC_Cable_Reel", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.25
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    Z_AXIS = 0.220
    UV_METAL = (0.25, 0.75)   # Clean seamless powder-coated steel
    UV_RUBBER = (0.75, 0.75)  # Clean matte black rubber
    UV_RESET_BTN = (0.12, 0.32) # Red button swatch
    
    # =========================================================================
    # 1. Frame_Stand (Tubular Steel A-frame, Feet, Handle Grip)
    # =========================================================================
    mesh_frame = bpy.data.meshes.new("Frame_Stand")
    bm_f = bmesh.new()
    bm_f.loops.layers.uv.new("UVMap")
    
    r_pipe = 0.009 # Ø18mm steel tube
    
    # Floor skids
    add_tube_segment(bm_f, (-0.145, -0.115, 0.010), (0.145, -0.115, 0.010), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    add_tube_segment(bm_f, (-0.145,  0.115, 0.010), (0.145,  0.115, 0.010), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    # Floor crossbars
    add_tube_segment(bm_f, (-0.135, -0.115, 0.010), (-0.135, 0.115, 0.010), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    add_tube_segment(bm_f, ( 0.135, -0.115, 0.010), ( 0.135, 0.115, 0.010), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    
    # 4 Corner Rubber Feet (M_Rubber)
    for fx in [-0.140, 0.140]:
        for fy in [-0.115, 0.115]:
            add_tube_segment(bm_f, (fx, fy, 0.001), (fx, fy, 0.016), radius=0.014, segments=10, mat_idx=1, uv_coord=UV_RUBBER)
            
    # A-Frame Legs (Left side Y = -0.115)
    add_tube_segment(bm_f, (-0.125, -0.115, 0.010), (0.0, -0.115, Z_AXIS), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    add_tube_segment(bm_f, ( 0.125, -0.115, 0.010), (0.0, -0.115, Z_AXIS), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    
    # A-Frame Legs (Right side Y = +0.115)
    add_tube_segment(bm_f, (-0.125,  0.115, 0.010), (0.0,  0.115, Z_AXIS), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    add_tube_segment(bm_f, ( 0.125,  0.115, 0.010), (0.0,  0.115, Z_AXIS), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    
    # Axle Bearing Blocks
    add_tube_segment(bm_f, (0.0, -0.125, Z_AXIS), (0.0, -0.095, Z_AXIS), radius=0.016, segments=12, mat_idx=0, uv_coord=UV_METAL)
    add_tube_segment(bm_f, (0.0,  0.095, Z_AXIS), (0.0,  0.125, Z_AXIS), radius=0.016, segments=12, mat_idx=0, uv_coord=UV_METAL)
    
    # Top Carry Handle Arch
    add_tube_segment(bm_f, (0.0, -0.115, Z_AXIS), (0.0, -0.065, 0.400), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    add_tube_segment(bm_f, (0.0,  0.115, Z_AXIS), (0.0,  0.065, 0.400), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    add_tube_segment(bm_f, (0.0, -0.065, 0.400), (0.0,  0.065, 0.400), radius=r_pipe, segments=10, mat_idx=0, uv_coord=UV_METAL)
    
    # Molded Ergonomic Rubber Grip (M_Rubber)
    add_tube_segment(bm_f, (0.0, -0.055, 0.400), (0.0, 0.055, 0.400), radius=0.016, segments=12, mat_idx=1, uv_coord=UV_RUBBER)
    for gy in [-0.035, -0.012, 0.012, 0.035]:
        add_tube_segment(bm_f, (0.0, gy - 0.003, 0.400), (0.0, gy + 0.003, 0.400), radius=0.0185, segments=12, mat_idx=1, uv_coord=UV_RUBBER)
        
    bm_f.to_mesh(mesh_frame)
    bm_f.free()
    obj_frame = bpy.data.objects.new("Frame_Stand", mesh_frame)
    obj_frame.data.materials.append(mat_metal)
    obj_frame.data.materials.append(mat_rubber)
    obj_frame.parent = root
    coll.objects.link(obj_frame)
    
    # =========================================================================
    # 2. Spindle_Pivot Empty (Rotates 360 deg on Y axis at Z=0.220)
    # =========================================================================
    spindle = bpy.data.objects.new("Spindle_Pivot", None)
    spindle.empty_display_type = 'CIRCLE'
    spindle.empty_display_size = 0.18
    spindle.location = (0.0, 0.0, Z_AXIS)
    spindle["rotation_axis"] = "Y"
    spindle["limit_min"] = -360.0
    spindle["limit_max"] = 360.0
    spindle.parent = root
    coll.objects.link(spindle)
    
    # =========================================================================
    # 3. Drum (Hollow cylinder between flanges: Y = -0.076 to +0.076, NO COPLANAR CAPS!)
    # =========================================================================
    mesh_drum = bpy.data.meshes.new("Drum")
    bm_d = bmesh.new()
    bm_d.loops.layers.uv.new("UVMap")
    # Open ends (add_caps=False) so ZERO z-fighting with flanges!
    add_cylinder_y(bm_d, (0.0, 0.0), radius=0.070, y_min=-0.076, y_max=0.076, segments=24, mat_idx=0, uv_coord=UV_METAL, add_caps=False)
    # Cable clamp bracket on drum surface
    add_tube_segment(bm_d, (0.068, -0.035, 0.010), (0.068, 0.035, 0.010), radius=0.005, segments=8, mat_idx=0, uv_coord=UV_METAL)
    
    bm_d.to_mesh(mesh_drum)
    bm_d.free()
    obj_drum = bpy.data.objects.new("Drum", mesh_drum)
    obj_drum.data.materials.append(mat_metal)
    obj_drum.data.materials.append(mat_rubber)
    obj_drum.parent = spindle
    coll.objects.link(obj_drum)
    
    # =========================================================================
    # 4. Flange_Left (Left Disc: Y = -0.078)
    # =========================================================================
    mesh_flange_l = bpy.data.meshes.new("Flange_Left")
    bm_fl = bmesh.new()
    uv_fl = bm_fl.loops.layers.uv.new("UVMap")
    
    R_flange = 0.155
    segments_fl = 32
    v_fl_outer = []
    v_fl_rim = []
    v_fl_hub = []
    for s in range(segments_fl):
        ang = s * (2.0 * math.pi / segments_fl)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_fl_outer.append(bm_fl.verts.new((R_flange * cos_a, -0.082, R_flange * sin_a)))
        v_fl_rim.append(bm_fl.verts.new(((R_flange - 0.006) * cos_a, -0.078, (R_flange - 0.006) * sin_a)))
        v_fl_hub.append(bm_fl.verts.new((0.045 * cos_a, -0.082, 0.045 * sin_a)))
        
    for s in range(segments_fl):
        sn = (s + 1) % segments_fl
        f_rim = bm_fl.faces.new((v_fl_outer[s], v_fl_outer[sn], v_fl_rim[sn], v_fl_rim[s]))
        f_rim.material_index = 0
        for l in f_rim.loops: l[uv_fl].uv = UV_METAL
        f_main = bm_fl.faces.new((v_fl_rim[s], v_fl_rim[sn], v_fl_hub[sn], v_fl_hub[s]))
        f_main.material_index = 0
        for l in f_main.loops: l[uv_fl].uv = UV_METAL
        
    f_hub_l = bm_fl.faces.new(reversed(v_fl_hub))
    f_hub_l.material_index = 0
    for l in f_hub_l.loops: l[uv_fl].uv = UV_METAL
    
    bm_fl.to_mesh(mesh_flange_l)
    bm_fl.free()
    obj_flange_l = bpy.data.objects.new("Flange_Left", mesh_flange_l)
    obj_flange_l.data.materials.append(mat_metal)
    obj_flange_l.data.materials.append(mat_rubber)
    obj_flange_l.parent = spindle
    coll.objects.link(obj_flange_l)
    
    # =========================================================================
    # 5. Flange_Right (Right Disc with Stepped Center Hub: Y = +0.078 to +0.084)
    # ZERO GLITCHING, NO UNWANTED MIDDLE TEXTURE!
    # =========================================================================
    mesh_flange_r = bpy.data.meshes.new("Flange_Right")
    bm_fr = bmesh.new()
    uv_fr = bm_fr.loops.layers.uv.new("UVMap")
    
    v_fr_outer = []
    v_fr_rim = []
    v_fr_hub_rim = []
    v_fr_hub_out = []
    
    for s in range(segments_fl):
        ang = s * (2.0 * math.pi / segments_fl)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_fr_outer.append(bm_fr.verts.new((R_flange * cos_a, 0.082, R_flange * sin_a)))
        v_fr_rim.append(bm_fr.verts.new(((R_flange - 0.006) * cos_a, 0.078, (R_flange - 0.006) * sin_a)))
        v_fr_hub_rim.append(bm_fr.verts.new((0.048 * cos_a, 0.078, 0.048 * sin_a)))
        v_fr_hub_out.append(bm_fr.verts.new((0.048 * cos_a, 0.084, 0.048 * sin_a)))
        
    for s in range(segments_fl):
        sn = (s + 1) % segments_fl
        f_rim = bm_fr.faces.new((v_fr_rim[s], v_fr_rim[sn], v_fr_outer[sn], v_fr_outer[s]))
        f_rim.material_index = 0
        for l in f_rim.loops: l[uv_fr].uv = UV_METAL
        f_main = bm_fr.faces.new((v_fr_hub_rim[s], v_fr_hub_rim[sn], v_fr_rim[sn], v_fr_rim[s]))
        f_main.material_index = 0
        for l in f_main.loops: l[uv_fr].uv = UV_METAL
        f_step = bm_fr.faces.new((v_fr_hub_rim[s], v_fr_hub_out[s], v_fr_hub_out[sn], v_fr_hub_rim[sn]))
        f_step.material_index = 0
        for l in f_step.loops: l[uv_fr].uv = UV_METAL
        
    f_hub_cap = bm_fr.faces.new(v_fr_hub_out)
    f_hub_cap.material_index = 0
    for l in f_hub_cap.loops: l[uv_fr].uv = UV_METAL
    
    # 3D Red Thermal Overload Reset Button on hub face
    add_cylinder_y(bm_fr, (-0.020, 0.015), radius=0.010, y_min=0.084, y_max=0.089, segments=16, mat_idx=0, uv_coord=UV_RESET_BTN, add_caps=True)
    
    bm_fr.to_mesh(mesh_flange_r)
    bm_fr.free()
    obj_flange_r = bpy.data.objects.new("Flange_Right", mesh_flange_r)
    obj_flange_r.data.materials.append(mat_metal)
    obj_flange_r.data.materials.append(mat_rubber)
    obj_flange_r.parent = spindle
    coll.objects.link(obj_flange_r)
    
    # =========================================================================
    # 6. Cable_Coil (Wound heavy-duty security cable mass, M_Rubber)
    # =========================================================================
    mesh_cable = bpy.data.meshes.new("Cable_Coil")
    bm_c = bmesh.new()
    bm_c.loops.layers.uv.new("UVMap")
    
    radii_layers = [0.088, 0.104, 0.120, 0.136]
    for r_c in radii_layers:
        for wrap_y in [-0.055, -0.035, -0.015, 0.005, 0.025, 0.045]:
            add_cylinder_y(bm_c, (0.0, 0.0), radius=r_c, y_min=wrap_y - 0.008, y_max=wrap_y + 0.008, segments=18, mat_idx=1, uv_coord=UV_RUBBER, add_caps=True)
            
    # Emerging cable tail clipped to flange
    add_tube_segment(bm_c, (0.136, 0.050, 0.0), (0.155, 0.078, 0.020), radius=0.005, segments=8, mat_idx=1, uv_coord=UV_RUBBER)
    
    bm_c.to_mesh(mesh_cable)
    bm_c.free()
    obj_cable = bpy.data.objects.new("Cable_Coil", mesh_cable)
    obj_cable.data.materials.append(mat_metal)
    obj_cable.data.materials.append(mat_rubber)
    obj_cable.parent = spindle
    coll.objects.link(obj_cable)
    
    # =========================================================================
    # 7. Crank_Handle (PROPER MECHANICAL WINDING CRANK!)
    # Attached solidly to the central axle, on the OUTSIDE of the frame!
    # Central axle shaft extends from drum through bearing to Y = 0.140.
    # Center crank hub collar sits firmly at (0.0, 0.0), Y = 0.128 to 0.140.
    # Crank arm extends from (0, 0) radially out to R = 0.095m at Y = 0.138.
    # Ergonomic revolving grip knob sits at the tip, pointing forward (Y = 0.140 to 0.172).
    # ZERO floating tubes, ZERO clipping, 100% mechanically correct!
    # =========================================================================
    mesh_crank = bpy.data.meshes.new("Crank_Handle")
    bm_crk = bmesh.new()
    bm_crk.loops.layers.uv.new("UVMap")
    
    # A. Central rotating axle shaft extending through the bearing to Y = 0.140
    add_cylinder_y(bm_crk, (0.0, 0.0), radius=0.011, y_min=0.078, y_max=0.140, segments=16, mat_idx=0, uv_coord=UV_METAL, add_caps=True)
    
    # B. Central Crank Hub Collar at (0.0, 0.0), Y = 0.128 to 0.140
    add_cylinder_y(bm_crk, (0.0, 0.0), radius=0.018, y_min=0.128, y_max=0.140, segments=16, mat_idx=0, uv_coord=UV_METAL, add_caps=True)
    
    # C. Solid Crank Arm extending from (0.0, 0.0) radially to R = 0.095m
    crank_len = 0.095
    add_tube_segment(bm_crk, (0.0, 0.138, 0.0), (crank_len, 0.138, 0.0), radius=0.007, segments=10, mat_idx=0, uv_coord=UV_METAL)
    
    # D. Tip Pivot Pin at (crank_len, 0.0), extending forward Y = 0.134 to 0.175
    add_cylinder_y(bm_crk, (crank_len, 0.0), radius=0.0045, y_min=0.134, y_max=0.175, segments=12, mat_idx=0, uv_coord=UV_METAL, add_caps=True)
    
    # E. Revolving Contoured Rubber Winding Knob (M_Rubber) at tip, Y = 0.140 to 0.172
    add_cylinder_y(bm_crk, (crank_len, 0.0), radius=0.0135, y_min=0.140, y_max=0.172, segments=16, mat_idx=1, uv_coord=UV_RUBBER, add_caps=True)
    # Center tactile ridge on knob
    add_cylinder_y(bm_crk, (crank_len, 0.0), radius=0.0155, y_min=0.152, y_max=0.160, segments=16, mat_idx=1, uv_coord=UV_RUBBER, add_caps=True)
    
    bm_crk.to_mesh(mesh_crank)
    bm_crk.free()
    obj_crank = bpy.data.objects.new("Crank_Handle", mesh_crank)
    obj_crank.data.materials.append(mat_metal)
    obj_crank.data.materials.append(mat_rubber)
    obj_crank.parent = spindle
    coll.objects.link(obj_crank)
    
    # Apply smooth shading and edge split modifier to all meshes
    all_meshes = [obj_frame, obj_flange_l, obj_flange_r, obj_drum, obj_cable, obj_crank]
    for child in all_meshes:
        for poly in child.data.polygons:
            poly.use_smooth = True
        mod = child.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
        mod.split_angle = math.radians(30)
        
    # Calculate triangles
    total_tris = 0
    for child in all_meshes:
        child_bm = bmesh.new()
        child_bm.from_mesh(child.data)
        bmesh.ops.triangulate(child_bm, faces=child_bm.faces)
        total_tris += len(child_bm.faces)
        child_bm.free()
        
    print(f"Perfect Mechanical SEC_Cable_Reel: Total Triangles = {total_tris}")
    
    # Configure Material Preview shading across all screens
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'
                        r3d = space.region_3d
                        r3d.view_distance = 0.85
                        r3d.view_location = (0.0, 0.0, 0.220)
                        
    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Cable_Reel.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Cable_Reel.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    spindle.select_set(True)
    for m in all_meshes:
        m.select_set(True)
    
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
    print(f"Exported FBX: {fbx_path}")
    
    test_reimport(fbx_path, total_tris, export_dir)

def test_reimport(fbx_path, original_tris, export_dir):
    clear_scene()
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    
    reimported_tris = 0
    reimported_meshes = 0
    reimported_empties = 0
    materials_found = set()
    
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            reimported_meshes += 1
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            reimported_tris += len(bm.faces)
            bm.free()
            for mat in obj.data.materials:
                if mat:
                    materials_found.add(mat.name)
        elif obj.type == 'EMPTY':
            reimported_empties += 1
            
    print(f"Re-import check: Meshes={reimported_meshes}, Empties={reimported_empties}, Tris={reimported_tris}")
    status = "SUCCESS" if (reimported_meshes == 6 and reimported_empties == 2 and reimported_tris == original_tris) else "FAILED"
    
    manifest = {
        "asset_name": "SEC_Cable_Reel",
        "fbx_path": "exports/SEC_Cable_Reel.fbx",
        "triangles": reimported_tris,
        "mesh_count": reimported_meshes,
        "empty_count": reimported_empties,
        "materials": sorted(list(materials_found)),
        "status": status
    }
    
    manifest_path = os.path.join(export_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    export_directory = r"C:\Users\Burak\Desktop\Security_CCTV\70. SEC_Cable_Reel\exports"
    build_sec_cable_reel(export_directory)
