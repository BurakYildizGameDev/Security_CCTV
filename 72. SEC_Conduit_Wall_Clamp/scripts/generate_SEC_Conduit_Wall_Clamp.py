import os
import sys
import math
import mathutils
import bpy
import bmesh

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.textures: bpy.data.textures.remove(block)
    for block in bpy.data.images: bpy.data.images.remove(block)

def setup_units():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

def create_metal_material(export_dir):
    mat = bpy.data.materials.new("M_Metal")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new('ShaderNodeOutputMaterial')
    node_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    node_bsdf.inputs['Metallic'].default_value = 0.92
    node_bsdf.inputs['Roughness'].default_value = 0.24
    
    tex_path = os.path.join(export_dir, "T_Security_Atlas.png")
    if os.path.exists(tex_path):
        node_tex = nodes.new('ShaderNodeTexImage')
        img = bpy.data.images.load(tex_path)
        node_tex.image = img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
    else:
        node_bsdf.inputs['Base Color'].default_value = (0.78, 0.81, 0.84, 1.0)
        
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # 100% OPAQUE - NO ALPHA GLITCH
    if hasattr(mat, 'blend_method'):
        mat.blend_method = 'OPAQUE'
    if hasattr(mat, 'shadow_method'):
        mat.shadow_method = 'OPAQUE'
        
    return mat

def add_box(bm, x_min, x_max, y_min, y_max, z_min, z_max, uv_coord=(0.25, 0.75)):
    v = [
        bm.verts.new((x_min, y_min, z_min)),
        bm.verts.new((x_max, y_min, z_min)),
        bm.verts.new((x_max, y_max, z_min)),
        bm.verts.new((x_min, y_max, z_min)),
        bm.verts.new((x_min, y_min, z_max)),
        bm.verts.new((x_max, y_min, z_max)),
        bm.verts.new((x_max, y_max, z_max)),
        bm.verts.new((x_min, y_max, z_max)),
    ]
    face_idx = [
        (0, 1, 2, 3), # Bottom
        (4, 7, 6, 5), # Top
        (0, 4, 5, 1), # Front (-Y)
        (2, 6, 7, 3), # Back (+Y)
        (0, 3, 7, 4), # Left (-X)
        (1, 5, 6, 2)  # Right (+X)
    ]
    faces = []
    uv_layer = bm.loops.layers.uv.verify()
    for f_idx in face_idx:
        f = bm.faces.new([v[i] for i in f_idx])
        f.material_index = 0
        for l in f.loops: l[uv_layer].uv = uv_coord
        faces.append(f)
    return faces

def add_cylinder(bm, p1, p2, radius, segments=16, uv_coord=(0.25, 0.75), add_caps=True):
    p1 = mathutils.Vector(p1)
    p2 = mathutils.Vector(p2)
    axis = p2 - p1
    length = axis.length
    if length < 1e-6: return []
    dir_v = axis.normalized()
    
    up = mathutils.Vector((0, 0, 1)) if abs(dir_v.z) < 0.9 else mathutils.Vector((1, 0, 0))
    right = dir_v.cross(up).normalized()
    up = right.cross(dir_v).normalized()
    
    vb, vt = [], []
    uv_layer = bm.loops.layers.uv.verify()
    for s in range(segments):
        ang = s * (2.0 * math.pi / segments)
        offset = radius * (math.cos(ang) * right + math.sin(ang) * up)
        vb.append(bm.verts.new(p1 + offset))
        vt.append(bm.verts.new(p2 + offset))
        
    faces = []
    for s in range(segments):
        sn = (s + 1) % segments
        f = bm.faces.new((vb[s], vb[sn], vt[sn], vt[s]))
        f.material_index = 0
        for l in f.loops: l[uv_layer].uv = uv_coord
        faces.append(f)
    if add_caps:
        fb = bm.faces.new(reversed(vb))
        fb.material_index = 0
        for l in fb.loops: l[uv_layer].uv = uv_coord
        ft = bm.faces.new(vt)
        ft.material_index = 0
        for l in ft.loops: l[uv_layer].uv = uv_coord
    return faces

def add_detailed_hex_bolt(bm, center_xy, z_base, z_top, radius, uv_coord=(0.75, 0.75)):
    # Flanged hex head with chamfer and washer
    cx, cy = center_xy
    uv_layer = bm.loops.layers.uv.verify()
    
    # 1. Washer flange base
    r_flange = radius * 1.35
    h_flange = (z_top - z_base) * 0.25
    add_cylinder(bm, (cx, cy, z_base), (cx, cy, z_base + h_flange), radius=r_flange, segments=12, uv_coord=uv_coord, add_caps=True)
    
    # 2. 6-sided hex head
    vb, vt = [], []
    for s in range(6):
        ang = s * (2.0 * math.pi / 6.0)
        vb.append(bm.verts.new((cx + radius * math.cos(ang), cy + radius * math.sin(ang), z_base + h_flange)))
        vt.append(bm.verts.new((cx + radius * math.cos(ang), cy + radius * math.sin(ang), z_top)))
    for s in range(6):
        sn = (s + 1) % 6
        f = bm.faces.new((vb[s], vb[sn], vt[sn], vt[s]))
        f.material_index = 0
        for l in f.loops: l[uv_layer].uv = uv_coord
    ft = bm.faces.new(vt)
    ft.material_index = 0
    for l in ft.loops: l[uv_layer].uv = uv_coord

def build_high_detail_clamp(export_dir):
    clear_scene()
    setup_units()
    
    mat_metal = create_metal_material(export_dir)
    
    coll = bpy.data.collections.new("SEC_Conduit_Wall_Clamp_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    # Root Empty at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Conduit_Wall_Clamp", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    UV_METAL = (0.25, 0.75)       # Clean seamless galvanized sheet steel
    UV_DARK_ZINC = (0.75, 0.75)   # Darkened hardware bolt steel
    
    # -------------------------------------------------------------
    # 1. Backplate (High-Detail Baseplate with Rounded Chamfered Corners)
    # -------------------------------------------------------------
    mesh_bp = bpy.data.meshes.new("Backplate")
    bm_bp = bmesh.new()
    uv_bp = bm_bp.loops.layers.uv.new("UVMap")
    
    # Rounded rectangle perimeter in X-Y plane at Z=0.0 and Z=0.003
    # Dimensions: X in [-0.013, +0.013], Y in [-0.044, +0.044], Z in [0.0, 0.003]
    # Corner radius = 0.004m
    r_c = 0.004
    x_in = 0.013 - r_c
    y_in = 0.044 - r_c
    corner_centers = [
        ( x_in,  y_in, 0.0),             # Q1
        (-x_in,  y_in, math.pi * 0.5),   # Q2
        (-x_in, -y_in, math.pi),         # Q3
        ( x_in, -y_in, math.pi * 1.5)    # Q4
    ]
    
    poly_pts = []
    for ccx, ccy, start_ang in corner_centers:
        for s in range(5):
            ang = start_ang + s * (math.pi * 0.5 / 4.0)
            poly_pts.append((ccx + r_c * math.cos(ang), ccy + r_c * math.sin(ang)))
            
    n_pts = len(poly_pts)
    vb_bp = [bm_bp.verts.new((px, py, 0.0)) for px, py in poly_pts]
    vt_bp = [bm_bp.verts.new((px, py, 0.003)) for px, py in poly_pts]
    
    # Side quads
    for s in range(n_pts):
        sn = (s + 1) % n_pts
        f = bm_bp.faces.new((vb_bp[s], vb_bp[sn], vt_bp[sn], vt_bp[s]))
        f.material_index = 0
        for l in f.loops: l[uv_bp].uv = UV_METAL
        
    # Top and bottom faces
    fb = bm_bp.faces.new(reversed(vb_bp))
    fb.material_index = 0
    for l in fb.loops: l[uv_bp].uv = UV_METAL
    ft = bm_bp.faces.new(vt_bp)
    ft.material_index = 0
    for l in ft.loops: l[uv_bp].uv = UV_METAL
    
    # Screw clearance recess bevel rings at Y = +-0.033
    for sy in [-0.033, 0.033]:
        add_cylinder(bm_bp, (0.0, sy, 0.0028), (0.0, sy, 0.0032), radius=0.0055, segments=12, uv_coord=UV_METAL, add_caps=True)
        
    bm_bp.to_mesh(mesh_bp)
    bm_bp.free()
    obj_bp = bpy.data.objects.new("Backplate", mesh_bp)
    obj_bp.data.materials.append(mat_metal)
    obj_bp.parent = root
    coll.objects.link(obj_bp)
    
    # -------------------------------------------------------------
    # 2. Clamp_Lower (High-Detail Semicircular Cradle & Mounting Tabs)
    # Conduit pipe axis: along X at Y = 0.0, Z = 0.0155 (R = 0.0125m)
    # 24 segments on semicircle!
    # -------------------------------------------------------------
    mesh_cl = bpy.data.meshes.new("Clamp_Lower")
    bm_cl = bmesh.new()
    uv_cl = bm_cl.loops.layers.uv.new("UVMap")
    
    R_in = 0.0125
    R_out = 0.0145
    Z_pipe = 0.0155
    x_w = 0.011 # width along X
    segs = 24
    
    v_in_f, v_in_b = [], []
    v_out_f, v_out_b = [], []
    
    for s in range(segs + 1):
        ang = -math.pi + s * (math.pi / segs)
        cy = R_in * math.cos(ang)
        cz = Z_pipe + R_in * math.sin(ang)
        cy_o = R_out * math.cos(ang)
        cz_o = Z_pipe + R_out * math.sin(ang)
        
        v_in_f.append(bm_cl.verts.new((-x_w, cy, cz)))
        v_in_b.append(bm_cl.verts.new((x_w, cy, cz)))
        v_out_f.append(bm_cl.verts.new((-x_w, cy_o, cz_o)))
        v_out_b.append(bm_cl.verts.new((x_w, cy_o, cz_o)))
        
    for s in range(segs):
        f1 = bm_cl.faces.new((v_in_f[s], v_in_f[s+1], v_in_b[s+1], v_in_b[s]))
        f1.material_index = 0
        for l in f1.loops: l[uv_cl].uv = UV_METAL
        f2 = bm_cl.faces.new((v_out_f[s], v_out_b[s], v_out_b[s+1], v_out_f[s+1]))
        f2.material_index = 0
        for l in f2.loops: l[uv_cl].uv = UV_METAL
        f3 = bm_cl.faces.new((v_in_f[s], v_out_f[s], v_out_f[s+1], v_in_f[s+1]))
        f3.material_index = 0
        for l in f3.loops: l[uv_cl].uv = UV_METAL
        f4 = bm_cl.faces.new((v_in_b[s], v_in_b[s+1], v_out_b[s+1], v_out_b[s]))
        f4.material_index = 0
        for l in f4.loops: l[uv_cl].uv = UV_METAL
        
    # Lower Hinge Barrel on -Y side (Y: -0.0125 to -0.0185)
    add_box(bm_cl, -x_w, x_w, -0.0185, -0.0125, Z_pipe - 0.002, Z_pipe, uv_coord=UV_METAL)
    # Hinge barrel roll along X:
    add_cylinder(bm_cl, (-x_w, -0.0155, Z_pipe - 0.001), (x_w, -0.0155, Z_pipe - 0.001), radius=0.0025, segments=12, uv_coord=UV_METAL, add_caps=True)
    
    # Lower Clamping Tab on +Y side (Y: +0.0125 to +0.026)
    add_box(bm_cl, -x_w, x_w, 0.0125, 0.026, Z_pipe - 0.002, Z_pipe, uv_coord=UV_METAL)
    # Clamping tab bolt boss
    add_cylinder(bm_cl, (0.0, 0.0195, Z_pipe - 0.003), (0.0, 0.0195, Z_pipe - 0.002), radius=0.0045, segments=12, uv_coord=UV_METAL, add_caps=True)
    
    bm_cl.to_mesh(mesh_cl)
    bm_cl.free()
    obj_cl = bpy.data.objects.new("Clamp_Lower", mesh_cl)
    obj_cl.data.materials.append(mat_metal)
    obj_cl.parent = root
    coll.objects.link(obj_cl)
    
    # -------------------------------------------------------------
    # 3. Clamp_Upper_Pivot Empty (At hinge center axis)
    # Hinge axis: (0.0, -0.0155, Z_pipe)
    # -------------------------------------------------------------
    hinge_y = -0.0155
    hinge_z = Z_pipe
    pivot = bpy.data.objects.new("Clamp_Upper_Pivot", None)
    pivot.empty_display_type = 'SINGLE_ARROW'
    pivot.empty_display_size = 0.025
    pivot.location = (0.0, hinge_y, hinge_z)
    pivot["rotation_axis"] = "X"
    pivot["limit_min"] = 0.0
    pivot["limit_max"] = 90.0
    pivot.parent = root
    coll.objects.link(pivot)
    
    # -------------------------------------------------------------
    # 4. Clamp_Upper (High-Detail Upper Arch with Stiffening Bead)
    # Parented to Clamp_Upper_Pivot
    # 24 segments on semicircle!
    # -------------------------------------------------------------
    mesh_cu = bpy.data.meshes.new("Clamp_Upper")
    bm_cu = bmesh.new()
    uv_cu = bm_cu.loops.layers.uv.new("UVMap")
    
    v_u_in_f, v_u_in_b = [], []
    v_u_out_f, v_u_out_b = [], []
    
    for s in range(segs + 1):
        ang = s * (math.pi / segs)
        w_y = R_in * math.cos(ang)
        w_z = Z_pipe + R_in * math.sin(ang)
        w_yo = R_out * math.cos(ang)
        w_zo = Z_pipe + R_out * math.sin(ang)
        
        loc_y = w_y - hinge_y
        loc_z = w_z - hinge_z
        loc_yo = w_yo - hinge_y
        loc_zo = w_zo - hinge_z
        
        v_u_in_f.append(bm_cu.verts.new((-x_w, loc_y, loc_z)))
        v_u_in_b.append(bm_cu.verts.new((x_w, loc_y, loc_z)))
        v_u_out_f.append(bm_cu.verts.new((-x_w, loc_yo, loc_zo)))
        v_u_out_b.append(bm_cu.verts.new((x_w, loc_yo, loc_zo)))
        
    for s in range(segs):
        f1 = bm_cu.faces.new((v_u_in_f[s], v_u_in_b[s], v_u_in_b[s+1], v_u_in_f[s+1]))
        f1.material_index = 0
        for l in f1.loops: l[uv_cu].uv = UV_METAL
        f2 = bm_cu.faces.new((v_u_out_f[s], v_u_out_f[s+1], v_u_out_b[s+1], v_u_out_b[s]))
        f2.material_index = 0
        for l in f2.loops: l[uv_cu].uv = UV_METAL
        f3 = bm_cu.faces.new((v_u_in_f[s], v_u_in_f[s+1], v_u_out_f[s+1], v_u_out_f[s]))
        f3.material_index = 0
        for l in f3.loops: l[uv_cu].uv = UV_METAL
        f4 = bm_cu.faces.new((v_u_in_b[s], v_u_out_b[s], v_u_out_b[s+1], v_u_in_b[s+1]))
        f4.material_index = 0
        for l in f4.loops: l[uv_cu].uv = UV_METAL
        
    # Central Stamped Stiffener Ridge on outer crown (continuous smooth bead along circumference)
    for s in range(segs):
        ang1 = s * (math.pi / segs)
        ang2 = (s + 1) * (math.pi / segs)
        p1 = (0.0, (R_out + 0.0006) * math.cos(ang1) - hinge_y, (Z_pipe + (R_out + 0.0006) * math.sin(ang1)) - hinge_z)
        p2 = (0.0, (R_out + 0.0006) * math.cos(ang2) - hinge_y, (Z_pipe + (R_out + 0.0006) * math.sin(ang2)) - hinge_z)
        add_cylinder(bm_cu, p1, p2, radius=0.0012, segments=8, uv_coord=UV_METAL, add_caps=False)
        
    # Upper Hinge Knuckle at -Y side
    add_box(bm_cu, -x_w, x_w, -0.0185 - hinge_y, -0.0125 - hinge_y, 0.0, 0.002, uv_coord=UV_METAL)
    # Upper hinge barrel roll:
    add_cylinder(bm_cu, (-x_w, -0.0155 - hinge_y, 0.001), (x_w, -0.0155 - hinge_y, 0.001), radius=0.0025, segments=12, uv_coord=UV_METAL, add_caps=True)
    
    # Upper Clamping Ear at +Y side
    add_box(bm_cu, -x_w, x_w, 0.0125 - hinge_y, 0.026 - hinge_y, 0.0, 0.002, uv_coord=UV_METAL)
    add_cylinder(bm_cu, (0.0, 0.0195 - hinge_y, 0.002), (0.0, 0.0195 - hinge_y, 0.003), radius=0.0045, segments=12, uv_coord=UV_METAL, add_caps=True)
    
    bm_cu.to_mesh(mesh_cu)
    bm_cu.free()
    obj_cu = bpy.data.objects.new("Clamp_Upper", mesh_cu)
    obj_cu.data.materials.append(mat_metal)
    obj_cu.parent = pivot
    coll.objects.link(obj_cu)
    
    # -------------------------------------------------------------
    # 5. Screws & Hardware (High-Detail Fasteners, Washers & Hinge Pin)
    # -------------------------------------------------------------
    mesh_sc = bpy.data.meshes.new("Screws")
    bm_sc = bmesh.new()
    bm_sc.loops.layers.uv.new("UVMap")
    
    # A. 2 Wall Mounting Flanged Screws with Socket Drive Cavity at Y = +-0.033
    for sy in [-0.033, 0.033]:
        add_detailed_hex_bolt(bm_sc, (0.0, sy), z_base=0.003, z_top=0.0075, radius=0.0034, uv_coord=UV_DARK_ZINC)
        # Socket recess on bolt head
        add_cylinder(bm_sc, (0.0, sy, 0.0072), (0.0, sy, 0.0076), radius=0.0016, segments=6, uv_coord=UV_DARK_ZINC, add_caps=True)
        
    # B. Clamping Bolt, Nut & Washers at Y = +0.0195
    # Hex bolt head on top:
    add_detailed_hex_bolt(bm_sc, (0.0, 0.0195), z_base=Z_pipe + 0.003, z_top=Z_pipe + 0.0075, radius=0.0030, uv_coord=UV_DARK_ZINC)
    # Threaded shank passing through tabs:
    add_cylinder(bm_sc, (0.0, 0.0195, Z_pipe - 0.007), (0.0, 0.0195, Z_pipe + 0.003), radius=0.0020, segments=10, uv_coord=UV_DARK_ZINC, add_caps=False)
    # Hex nut on bottom:
    add_detailed_hex_bolt(bm_sc, (0.0, 0.0195), z_base=Z_pipe - 0.007, z_top=Z_pipe - 0.003, radius=0.0030, uv_coord=UV_DARK_ZINC)
    
    # C. Mechanical Hinge Pin passing through the hinge barrel at Y = -0.0155, Z = Z_pipe
    add_cylinder(bm_sc, (-x_w - 0.0025, hinge_y, hinge_z), (x_w + 0.0025, hinge_y, hinge_z), radius=0.0014, segments=12, uv_coord=UV_DARK_ZINC, add_caps=True)
    # Rivet heads on hinge pin ends
    add_cylinder(bm_sc, (-x_w - 0.0035, hinge_y, hinge_z), (-x_w - 0.0025, hinge_y, hinge_z), radius=0.0024, segments=12, uv_coord=UV_DARK_ZINC, add_caps=True)
    add_cylinder(bm_sc, ( x_w + 0.0025, hinge_y, hinge_z), ( x_w + 0.0035, hinge_y, hinge_z), radius=0.0024, segments=12, uv_coord=UV_DARK_ZINC, add_caps=True)
    
    bm_sc.to_mesh(mesh_sc)
    bm_sc.free()
    obj_sc = bpy.data.objects.new("Screws", mesh_sc)
    obj_sc.data.materials.append(mat_metal)
    obj_sc.parent = root
    coll.objects.link(obj_sc)
    
    # Apply smooth shading and edge split modifier
    all_meshes = [obj_bp, obj_cl, obj_cu, obj_sc]
    for child in all_meshes:
        for p in child.data.polygons:
            p.use_smooth = True
        mod = child.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
        mod.split_angle = math.radians(35)
        
    # Calculate triangles
    total_tris = 0
    for child in all_meshes:
        child_bm = bmesh.new()
        child_bm.from_mesh(child.data)
        bmesh.ops.triangulate(child_bm, faces=child_bm.faces)
        total_tris += len(child_bm.faces)
        child_bm.free()
        
    print(f"High-Detail SEC_Conduit_Wall_Clamp Triangles: {total_tris}")
    
    # Set Material Preview on 3D view
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'
                        space.region_3d.view_distance = 0.20
                        space.region_3d.view_location = (0.0, 0.0, 0.015)
                        
    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Conduit_Wall_Clamp.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Conduit_Wall_Clamp.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    pivot.select_set(True)
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
                if mat: materials_found.add(mat.name)
        elif obj.type == 'EMPTY':
            reimported_empties += 1
            
    print(f"Re-import check: Meshes={reimported_meshes}, Empties={reimported_empties}, Tris={reimported_tris}")
    status = "SUCCESS" if (reimported_meshes == 4 and reimported_empties == 2 and reimported_tris == original_tris) else "FAILED"
    
    manifest = {
        "asset_name": "SEC_Conduit_Wall_Clamp",
        "fbx_path": "exports/SEC_Conduit_Wall_Clamp.fbx",
        "triangles": reimported_tris,
        "mesh_count": reimported_meshes,
        "empty_count": reimported_empties,
        "materials": sorted(list(materials_found)),
        "status": status
    }
    
    manifest_path = os.path.join(export_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        import json
        json.dump(manifest, f, indent=2)
    print(f"Manifest written to: {manifest_path} with status {status}")

if __name__ == "__main__":
    export_directory = r"C:\Users\Burak\Desktop\Security_CCTV\72. SEC_Conduit_Wall_Clamp\exports"
    build_high_detail_clamp(export_directory)
