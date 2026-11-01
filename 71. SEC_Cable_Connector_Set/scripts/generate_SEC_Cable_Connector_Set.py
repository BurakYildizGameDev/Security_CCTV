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
    
    # Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes_a = mat_atlas.node_tree.nodes
    links_a = mat_atlas.node_tree.links
    nodes_a.clear()
    
    out_a = nodes_a.new(type='ShaderNodeOutputMaterial')
    out_a.location = (400, 0)
    bsdf_a = nodes_a.new(type='ShaderNodeBsdfPrincipled')
    bsdf_a.location = (0, 0)
    bsdf_a.inputs['Metallic'].default_value = 0.10
    bsdf_a.inputs['Roughness'].default_value = 0.35
    
    if os.path.exists(atlas_path):
        tex_a = nodes_a.new(type='ShaderNodeTexImage')
        tex_a.location = (-400, 0)
        img = bpy.data.images.load(atlas_path)
        img.name = "T_Security_Atlas.png"
        tex_a.image = img
        links_a.new(tex_a.outputs['Color'], bsdf_a.inputs['Base Color'])
        nodes_a.active = tex_a
        
    links_a.new(bsdf_a.outputs['BSDF'], out_a.inputs['Surface'])
    mat_atlas.diffuse_color = (0.85, 0.88, 0.90, 1.0)
    
    # Strictly OPAQUE
    if hasattr(mat_atlas, 'blend_method'):
        mat_atlas.blend_method = 'OPAQUE'
    if hasattr(mat_atlas, 'shadow_method'):
        mat_atlas.shadow_method = 'OPAQUE'
        
    # Slot 1: M_Metal
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    nodes_m = mat_metal.node_tree.nodes
    links_m = mat_metal.node_tree.links
    nodes_m.clear()
    out_m = nodes_m.new(type='ShaderNodeOutputMaterial')
    out_m.location = (400, 0)
    bsdf_m = nodes_m.new(type='ShaderNodeBsdfPrincipled')
    bsdf_m.location = (0, 0)
    bsdf_m.inputs['Base Color'].default_value = (0.90, 0.92, 0.94, 1.0)
    bsdf_m.inputs['Metallic'].default_value = 0.90
    bsdf_m.inputs['Roughness'].default_value = 0.25
    links_m.new(bsdf_m.outputs['BSDF'], out_m.inputs['Surface'])
    mat_metal.diffuse_color = (0.90, 0.92, 0.94, 1.0)
    
    if hasattr(mat_metal, 'blend_method'):
        mat_metal.blend_method = 'OPAQUE'
    if hasattr(mat_metal, 'shadow_method'):
        mat_metal.shadow_method = 'OPAQUE'
        
    # Slot 2: M_Rubber
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
        
    return mat_atlas, mat_metal, mat_rubber

def add_cylinder(bm, center, radius, h_bottom, h_top, segments=16, mat_idx=0, uv_coord=(0.12, 0.88)):
    cx, cy = center
    vb, vt = [], []
    uv_layer = bm.loops.layers.uv.verify()
    for i in range(segments):
        ang = i * (2.0 * math.pi / segments)
        vb.append(bm.verts.new((cx + radius * math.cos(ang), cy + radius * math.sin(ang), h_bottom)))
        vt.append(bm.verts.new((cx + radius * math.cos(ang), cy + radius * math.sin(ang), h_top)))
    faces = []
    for i in range(segments):
        inxt = (i + 1) % segments
        f = bm.faces.new((vb[i], vb[inxt], vt[inxt], vt[i]))
        f.material_index = mat_idx
        for l in f.loops: l[uv_layer].uv = uv_coord
        faces.append(f)
    fb = bm.faces.new(reversed(vb))
    fb.material_index = mat_idx
    for l in fb.loops: l[uv_layer].uv = uv_coord
    ft = bm.faces.new(vt)
    ft.material_index = mat_idx
    for l in ft.loops: l[uv_layer].uv = uv_coord
    return vb, vt, faces

def add_box(bm, center, size, mat_idx=0, uv_coord=(0.12, 0.88)):
    cx, cy, cz = center
    sx, sy, sz = size[0]/2.0, size[1]/2.0, size[2]/2.0
    corners = [
        (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
        (-sx, -sy,  sz), (sx, -sy,  sz), (sx, sy,  sz), (-sx, sy,  sz),
    ]
    verts = [bm.verts.new((cx + c[0], cy + c[1], cz + c[2])) for c in corners]
    face_indices = [
        (0, 1, 2, 3), # Bottom
        (4, 7, 6, 5), # Top
        (0, 4, 5, 1), # Front (-Y)
        (2, 6, 7, 3), # Back (+Y)
        (0, 3, 7, 4), # Left (-X)
        (1, 5, 6, 2), # Right (+X)
    ]
    faces = []
    uv_layer = bm.loops.layers.uv.verify()
    for idxs in face_indices:
        f = bm.faces.new([verts[i] for i in idxs])
        f.material_index = mat_idx
        for l in f.loops: l[uv_layer].uv = uv_coord
        faces.append(f)
    return verts, faces

def build_sec_cable_connector_set(export_dir):
    clear_scene()
    setup_units()
    
    mat_atlas, mat_metal, mat_rubber = create_materials(export_dir)
    
    coll = bpy.data.collections.new("SEC_Cable_Connector_Set_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    root = bpy.data.objects.new("SEC_Cable_Connector_Set", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.10
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    UV_METAL = (0.12, 0.88)
    UV_RUBBER = (0.12, 0.62)
    UV_KNURL = (0.12, 0.38)
    UV_CLEAR_POLY = (0.12, 0.12)
    
    # =========================================================================
    # 1. Detailed Connector_BNC (centered at X = -0.060)
    # =========================================================================
    mesh_bnc = bpy.data.meshes.new("Connector_BNC")
    bm_b = bmesh.new()
    uv_b = bm_b.loops.layers.uv.new("UVMap")
    cx_b = -0.060
    
    # A. Rotating Bayonet Knurled Outer Sleeve (Z = 0.006 to 0.017, R = 0.00725)
    r_bnc_sleeve = 0.00725
    segments_bnc = 16
    vb_s, vt_s = [], []
    for s in range(segments_bnc):
        ang = -math.pi/2.0 - math.pi/segments_bnc + s * (2.0 * math.pi / segments_bnc)
        vb_s.append(bm_b.verts.new((cx_b + r_bnc_sleeve * math.cos(ang), r_bnc_sleeve * math.sin(ang), 0.006)))
        vt_s.append(bm_b.verts.new((cx_b + r_bnc_sleeve * math.cos(ang), r_bnc_sleeve * math.sin(ang), 0.017)))
        
    for s in range(segments_bnc):
        sn = (s + 1) % segments_bnc
        f = bm_b.faces.new((vb_s[s], vb_s[sn], vt_s[sn], vt_s[s]))
        f.material_index = 0
        if s == 0:
            # Front flat: BNC Technical Badge (Y: 100..280 -> V: 0.863..0.951, X: 550..1950 -> U: 0.27..0.95)
            f.loops[0][uv_b].uv = (0.28, 0.865)
            f.loops[1][uv_b].uv = (0.95, 0.865)
            f.loops[2][uv_b].uv = (0.95, 0.950)
            f.loops[3][uv_b].uv = (0.28, 0.950)
        else:
            for l in f.loops: l[uv_b].uv = UV_KNURL
            
    # Beveled lips on sleeve
    add_cylinder(bm_b, (cx_b, 0.0), radius=r_bnc_sleeve * 0.94, h_bottom=0.0045, h_top=0.006, segments=16, mat_idx=1, uv_coord=UV_METAL)
    add_cylinder(bm_b, (cx_b, 0.0), radius=r_bnc_sleeve * 0.94, h_bottom=0.017, h_top=0.0185, segments=16, mat_idx=1, uv_coord=UV_METAL)
    
    # 2 Opposing J-Slot Bayonet Lugs
    add_cylinder(bm_b, (cx_b - r_bnc_sleeve, 0.0), radius=0.0008, h_bottom=0.010, h_top=0.014, segments=8, mat_idx=1, uv_coord=UV_METAL)
    add_cylinder(bm_b, (cx_b + r_bnc_sleeve, 0.0), radius=0.0008, h_bottom=0.010, h_top=0.014, segments=8, mat_idx=1, uv_coord=UV_METAL)
    
    # B. Front Inner Steel Coupling Sleeve (Z = 0.0185 to 0.0245, R = 0.0055)
    add_cylinder(bm_b, (cx_b, 0.0), radius=0.0055, h_bottom=0.0185, h_top=0.0245, segments=16, mat_idx=1, uv_coord=UV_METAL)
    # Teflon Insulator Disc & Gold Pin
    add_cylinder(bm_b, (cx_b, 0.0), radius=0.0030, h_bottom=0.0185, h_top=0.0235, segments=12, mat_idx=0, uv_coord=UV_CLEAR_POLY)
    add_cylinder(bm_b, (cx_b, 0.0), radius=0.0007, h_bottom=0.0185, h_top=0.0260, segments=8, mat_idx=1, uv_coord=(0.88, 0.91)) # gold badge sample
    
    # C. Hex Crimp Ferrule behind collar (Z = -0.005 to 0.0045)
    v_crimp_b, v_crimp_t = [], []
    for i in range(6):
        ang = i * (math.pi / 3.0) + (math.pi / 6.0)
        v_crimp_b.append(bm_b.verts.new((cx_b + 0.0052 * math.cos(ang), 0.0052 * math.sin(ang), -0.005)))
        v_crimp_t.append(bm_b.verts.new((cx_b + 0.0052 * math.cos(ang), 0.0052 * math.sin(ang), 0.0045)))
    for i in range(6):
        inxt = (i + 1) % 6
        f = bm_b.faces.new((v_crimp_b[i], v_crimp_b[inxt], v_crimp_t[inxt], v_crimp_t[i]))
        f.material_index = 1
        for l in f.loops: l[uv_b].uv = UV_METAL
        
    # D. Compact Sleek Accordion Rubber Boot (Z = -0.023 to -0.005, 4 tapered rings)
    r_boot = [0.0056, 0.0051, 0.0046, 0.0040, 0.0036]
    z_boot = [-0.005, -0.0095, -0.0140, -0.0185, -0.0230]
    for bi in range(len(r_boot) - 1):
        add_cylinder(bm_b, (cx_b, 0.0), radius=r_boot[bi], h_bottom=z_boot[bi+1], h_top=z_boot[bi], segments=12, mat_idx=2, uv_coord=UV_RUBBER)
        
    # E. RG59 Coax Cable Stub (Z = -0.043 to -0.023, R = 0.0033)
    add_cylinder(bm_b, (cx_b, 0.0), radius=0.0033, h_bottom=-0.043, h_top=-0.023, segments=12, mat_idx=2, uv_coord=UV_RUBBER)
    
    bm_b.to_mesh(mesh_bnc)
    bm_b.free()
    obj_bnc = bpy.data.objects.new("Connector_BNC", mesh_bnc)
    obj_bnc.data.materials.append(mat_atlas)
    obj_bnc.data.materials.append(mat_metal)
    obj_bnc.data.materials.append(mat_rubber)
    obj_bnc.parent = root
    coll.objects.link(obj_bnc)

    # =========================================================================
    # 2. Detailed Connector_RJ45 (centered at X = 0.000)
    # Standard dimensions: 11.7mm wide, 8.0mm high, 21.5mm long
    # =========================================================================
    mesh_rj = bpy.data.meshes.new("Connector_RJ45")
    bm_r = bmesh.new()
    uv_r = bm_r.loops.layers.uv.new("UVMap")
    
    # A. Clear Polycarbonate Main Housing (Z = 0.002 to 0.0235)
    # Top face is mapped to T568B Color Diagram badge!
    # Box: size = (0.0117, 0.0080, 0.0215)
    w_rj = 0.0117
    h_rj = 0.0080
    z_min_rj = 0.002
    z_max_rj = 0.0235
    
    corners = [
        (-w_rj/2, -h_rj/2, z_min_rj), (w_rj/2, -h_rj/2, z_min_rj), (w_rj/2, h_rj/2, z_min_rj), (-w_rj/2, h_rj/2, z_min_rj),
        (-w_rj/2, -h_rj/2, z_max_rj), (w_rj/2, -h_rj/2, z_max_rj), (w_rj/2, h_rj/2, z_max_rj), (-w_rj/2, h_rj/2, z_max_rj),
    ]
    v_box = [bm_r.verts.new(c) for c in corners]
    face_map = [
        (0, 1, 2, 3, UV_CLEAR_POLY), # Bottom
        (4, 7, 6, 5, "TOP_DECAL"),   # Top face: T568B Pinout Decal!
        (0, 4, 5, 1, UV_CLEAR_POLY), # Front (-Y)
        (2, 6, 7, 3, UV_CLEAR_POLY), # Back (+Y)
        (0, 3, 7, 4, UV_CLEAR_POLY), # Left (-X)
        (1, 5, 6, 2, UV_CLEAR_POLY), # Right (+X)
    ]
    for f_def in face_map:
        f = bm_r.faces.new([v_box[f_def[0]], v_box[f_def[1]], v_box[f_def[2]], v_box[f_def[3]]])
        f.material_index = 0
        if f_def[4] == "TOP_DECAL":
            # Decal Region: Y: 340..560 -> V: 0.726..0.834, X: 550..1950 -> U: 0.27..0.95
            f.loops[0][uv_r].uv = (0.28, 0.730)
            f.loops[1][uv_r].uv = (0.28, 0.830)
            f.loops[2][uv_r].uv = (0.95, 0.830)
            f.loops[3][uv_r].uv = (0.95, 0.730)
        else:
            for l in f.loops: l[uv_r].uv = f_def[4]
            
    # Stepped front nose guide
    add_box(bm_r, (0.0, -0.0010, z_max_rj + 0.0025), (0.0112, 0.0060, 0.0050), mat_idx=0, uv_coord=UV_CLEAR_POLY)
    
    # 8 Physical Gold Contact Blades at front edge (Pitch = 1.02mm)
    for p in range(8):
        px = -0.0042 + p * (0.0084 / 7.0)
        # Gold blade
        add_box(bm_r, (px, -0.0035, z_max_rj + 0.0035), (0.00065, 0.0014, 0.0040), mat_idx=1, uv_coord=(0.88, 0.91))
        
    # 3D Flexible Snap Latch Lever
    # Hinge at front-bottom/top extending backwards
    add_box(bm_r, (0.0, 0.0048, 0.008), (0.0040, 0.0015, 0.004), mat_idx=0, uv_coord=UV_CLEAR_POLY)
    # Angled lever
    add_box(bm_r, (0.0, 0.0068, 0.016), (0.0042, 0.0016, 0.014), mat_idx=0, uv_coord=UV_CLEAR_POLY)
    # Thumb press pad with ridges
    add_box(bm_r, (0.0, 0.0075, 0.024), (0.0050, 0.0020, 0.004), mat_idx=0, uv_coord=UV_CLEAR_POLY)
    # Locking ear barbs
    add_box(bm_r, (-0.0036, 0.0068, 0.021), (0.0028, 0.0016, 0.003), mat_idx=0, uv_coord=UV_CLEAR_POLY)
    add_box(bm_r, ( 0.0036, 0.0068, 0.021), (0.0028, 0.0016, 0.003), mat_idx=0, uv_coord=UV_CLEAR_POLY)
    
    # Molded Snagless Rubber Boot (Z = -0.008 to 0.003)
    add_box(bm_r, (0.0, 0.0010, -0.002), (0.0132, 0.0098, 0.010), mat_idx=2, uv_coord=UV_RUBBER)
    # Arch hood over latch hinge
    add_box(bm_r, (0.0, 0.0078, 0.005), (0.0072, 0.0030, 0.008), mat_idx=2, uv_coord=UV_RUBBER)
    
    # Compact Tapered Boot Tail (Z = -0.023 to -0.008)
    r_rj_boot = [0.0052, 0.0047, 0.0042, 0.0036]
    z_rj_boot = [-0.008, -0.013, -0.018, -0.023]
    for bi in range(len(r_rj_boot) - 1):
        add_cylinder(bm_r, (0.0, 0.0), radius=r_rj_boot[bi], h_bottom=z_rj_boot[bi+1], h_top=z_rj_boot[bi], segments=12, mat_idx=2, uv_coord=UV_RUBBER)
        
    # Cat6 Cable Stub (Z = -0.043 to -0.023, R = 0.0033)
    add_cylinder(bm_r, (0.0, 0.0), radius=0.0033, h_bottom=-0.043, h_top=-0.023, segments=12, mat_idx=2, uv_coord=UV_RUBBER)
    
    bm_r.to_mesh(mesh_rj)
    bm_r.free()
    obj_rj = bpy.data.objects.new("Connector_RJ45", mesh_rj)
    obj_rj.data.materials.append(mat_atlas)
    obj_rj.data.materials.append(mat_metal)
    obj_rj.data.materials.append(mat_rubber)
    obj_rj.parent = root
    coll.objects.link(obj_rj)

    # =========================================================================
    # 3. Detailed Connector_Power (centered at X = +0.060)
    # Standard 5.5 x 2.1mm CCTV power jack
    # =========================================================================
    mesh_pwr = bpy.data.meshes.new("Connector_Power")
    bm_p = bmesh.new()
    uv_p = bm_p.loops.layers.uv.new("UVMap")
    cx_p = 0.060
    
    # A. Nickel Barrel Sleeve (OD = 5.5mm, R = 0.00275, Length = 9.5mm, Z = 0.012 to 0.0215)
    add_cylinder(bm_p, (cx_p, 0.0), radius=0.00275, h_bottom=0.012, h_top=0.0215, segments=16, mat_idx=1, uv_coord=UV_METAL)
    # Black tip insulator ring
    add_cylinder(bm_p, (cx_p, 0.0), radius=0.00275, h_bottom=0.0210, h_top=0.0220, segments=16, mat_idx=2, uv_coord=UV_RUBBER)
    # Inner 2.1mm center spring hole
    add_cylinder(bm_p, (cx_p, 0.0), radius=0.00105, h_bottom=0.014, h_top=0.0225, segments=10, mat_idx=1, uv_coord=UV_METAL)
    
    # B. Front Molded Collar (Z = 0.008 to 0.012, R = 0.0045)
    add_cylinder(bm_p, (cx_p, 0.0), radius=0.0045, h_bottom=0.008, h_top=0.012, segments=16, mat_idx=0, uv_coord=UV_RUBBER)
    
    # C. Molded PVC Grip Body (Z = -0.008 to 0.008, R = 0.0050)
    # Front flat face is mapped to DC 12V Polarity Badge!
    vb_pw, vt_pw = [], []
    segments_pw = 12
    r_pw_body = 0.0050
    for s in range(segments_pw):
        ang = -math.pi/2.0 - math.pi/segments_pw + s * (2.0 * math.pi / segments_pw)
        vb_pw.append(bm_p.verts.new((cx_p + r_pw_body * math.cos(ang), r_pw_body * math.sin(ang), -0.008)))
        vt_pw.append(bm_p.verts.new((cx_p + r_pw_body * math.cos(ang), r_pw_body * math.sin(ang), 0.008)))
        
    for s in range(segments_pw):
        sn = (s + 1) % segments_pw
        f = bm_p.faces.new((vb_pw[s], vb_pw[sn], vt_pw[sn], vt_pw[s]))
        f.material_index = 0
        if s == 0:
            # Front face: Polarity Badge!
            # Region 6: Y: 620..800 -> V: 0.609..0.697, X: 550..1950 -> U: 0.27..0.95
            f.loops[0][uv_p].uv = (0.28, 0.612)
            f.loops[1][uv_p].uv = (0.95, 0.612)
            f.loops[2][uv_p].uv = (0.95, 0.695)
            f.loops[3][uv_p].uv = (0.28, 0.695)
        else:
            for l in f.loops: l[uv_p].uv = UV_RUBBER
            
    # 4 Anti-slip Grip Ribs on body sides
    for rib_i in range(4):
        rib_ang = rib_i * (math.pi / 2.0) + (math.pi / 4.0)
        rx = cx_p + (r_pw_body * 0.98) * math.cos(rib_ang)
        ry = (r_pw_body * 0.98) * math.sin(rib_ang)
        add_cylinder(bm_p, (rx, ry), radius=0.0007, h_bottom=-0.006, h_top=0.006, segments=6, mat_idx=0, uv_coord=UV_RUBBER)
        
    # D. Compact Strain Relief Boot (Z = -0.023 to -0.008)
    r_pwr_boot = [0.0046, 0.0041, 0.0036, 0.0031]
    z_pwr_boot = [-0.008, -0.013, -0.018, -0.023]
    for bi in range(len(r_pwr_boot) - 1):
        add_cylinder(bm_p, (cx_p, 0.0), radius=r_pwr_boot[bi], h_bottom=z_pwr_boot[bi+1], h_top=z_pwr_boot[bi], segments=12, mat_idx=2, uv_coord=UV_RUBBER)
        
    # E. Two-Conductor Figure-8 Zip Cord (Z = -0.043 to -0.023)
    add_cylinder(bm_p, (cx_p - 0.0016, 0.0), radius=0.0016, h_bottom=-0.043, h_top=-0.023, segments=10, mat_idx=2, uv_coord=UV_RUBBER)
    add_cylinder(bm_p, (cx_p + 0.0016, 0.0), radius=0.0016, h_bottom=-0.043, h_top=-0.023, segments=10, mat_idx=2, uv_coord=UV_RUBBER)
    add_box(bm_p, (cx_p, 0.0, -0.033), (0.0018, 0.0010, 0.020), mat_idx=2, uv_coord=UV_RUBBER)
    
    bm_p.to_mesh(mesh_pwr)
    bm_p.free()
    obj_pwr = bpy.data.objects.new("Connector_Power", mesh_pwr)
    obj_pwr.data.materials.append(mat_atlas)
    obj_pwr.data.materials.append(mat_metal)
    obj_pwr.data.materials.append(mat_rubber)
    obj_pwr.parent = root
    coll.objects.link(obj_pwr)
    
    # Calculate triangles
    total_tris = 0
    all_meshes = [obj_bnc, obj_rj, obj_pwr]
    for child in all_meshes:
        child_bm = bmesh.new()
        child_bm.from_mesh(child.data)
        bmesh.ops.triangulate(child_bm, faces=child_bm.faces)
        total_tris += len(child_bm.faces)
        child_bm.free()
        
    print(f"Professional SEC_Cable_Connector_Set: Total Triangles = {total_tris}")
    
    # Configure Material Preview shading across all screens
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'
                        r3d = space.region_3d
                        r3d.view_distance = 0.20
                        r3d.view_location = (0.0, 0.0, -0.005)
                        
    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Cable_Connector_Set.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Cable_Connector_Set.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
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
    status = "SUCCESS" if (reimported_meshes == 3 and reimported_empties == 1 and reimported_tris == original_tris) else "FAILED"
    
    manifest = {
        "asset_name": "SEC_Cable_Connector_Set",
        "fbx_path": "exports/SEC_Cable_Connector_Set.fbx",
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
    export_directory = r"C:\Users\Burak\Desktop\Security_CCTV\71. SEC_Cable_Connector_Set\exports"
    build_sec_cable_connector_set(export_directory)
