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
    
    # Slot 0: M_Metal (High-End Machined Nickel-Plated Brass)
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    nodes_m = mat_metal.node_tree.nodes
    links_m = mat_metal.node_tree.links
    nodes_m.clear()
    
    out_m = nodes_m.new(type='ShaderNodeOutputMaterial')
    out_m.location = (400, 0)
    bsdf_m = nodes_m.new(type='ShaderNodeBsdfPrincipled')
    bsdf_m.location = (0, 0)
    bsdf_m.inputs['Metallic'].default_value = 0.92
    bsdf_m.inputs['Roughness'].default_value = 0.22
    
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
    
    # Slot 1: M_Rubber (Matte Black EPDM)
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

def add_cylinder(bm, center, radius, h_bottom, h_top, segments=24, mat_idx=0, uv_coord=(0.25, 0.75)):
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

def add_chamfered_hex(bm, center, radius, h_bottom, h_top, chamfer=0.0010, mat_idx=0, uv_coord=(0.25, 0.75)):
    cx, cy = center
    v_bot_in, v_bot_out, v_top_out, v_top_in = [], [], [], []
    uv_layer = bm.loops.layers.uv.verify()
    
    for i in range(6):
        ang = i * (math.pi / 3.0) + (math.pi / 6.0)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_bot_in.append(bm.verts.new((cx + (radius - chamfer) * cos_a, cy + (radius - chamfer) * sin_a, h_bottom)))
        v_bot_out.append(bm.verts.new((cx + radius * cos_a, cy + radius * sin_a, h_bottom + chamfer)))
        v_top_out.append(bm.verts.new((cx + radius * cos_a, cy + radius * sin_a, h_top - chamfer)))
        v_top_in.append(bm.verts.new((cx + (radius - chamfer) * cos_a, cy + (radius - chamfer) * sin_a, h_top)))
        
    for i in range(6):
        inxt = (i + 1) % 6
        # Bottom chamfer
        f_bc = bm.faces.new((v_bot_in[i], v_bot_in[inxt], v_bot_out[inxt], v_bot_out[i]))
        f_bc.material_index = mat_idx
        for l in f_bc.loops: l[uv_layer].uv = uv_coord
        # Middle vertical flat
        f_mid = bm.faces.new((v_bot_out[i], v_bot_out[inxt], v_top_out[inxt], v_top_out[i]))
        f_mid.material_index = mat_idx
        for l in f_mid.loops: l[uv_layer].uv = uv_coord
        # Top chamfer
        f_tc = bm.faces.new((v_top_out[i], v_top_out[inxt], v_top_in[inxt], v_top_in[i]))
        f_tc.material_index = mat_idx
        for l in f_tc.loops: l[uv_layer].uv = uv_coord
        
    fb = bm.faces.new(reversed(v_bot_in))
    fb.material_index = mat_idx
    for l in fb.loops: l[uv_layer].uv = uv_coord
    ft = bm.faces.new(v_top_in)
    ft.material_index = mat_idx
    for l in ft.loops: l[uv_layer].uv = uv_coord

def build_high_poly_gland(name, cx, r_thread, r_hex, r_cable, h_thread, h_body, h_nut, mat_metal, mat_rubber):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    
    # Swatch coordinates (Pure metal & rubber, NO text)
    UV_METAL = (0.25, 0.75)
    UV_RUBBER = (0.75, 0.75)
    UV_THREAD = (0.25, 0.25)
    UV_DOME = (0.75, 0.25)
    
    # -------------------------------------------------------------
    # 1. Chamfered Hexagonal Locknut (-h_thread to -h_thread + 0.004)
    # -------------------------------------------------------------
    z_lock_bot = -h_thread
    z_lock_top = -h_thread + 0.0040
    add_chamfered_hex(bm, (cx, 0.0), radius=r_hex * 0.96, h_bottom=z_lock_bot, h_top=z_lock_top, chamfer=0.0008, mat_idx=0, uv_coord=UV_METAL)

    # -------------------------------------------------------------
    # 2. Threaded Shank (8 distinct precision screw thread rings)
    # High-detail 24 segments
    # -------------------------------------------------------------
    z_th_start = z_lock_top
    z_th_end = -0.0018
    num_threads = 8
    th_step = (z_th_end - z_th_start) / num_threads
    segments_cyl = 24
    
    for t in range(num_threads):
        z0 = z_th_start + t * th_step
        z1 = z0 + th_step * 0.65
        z2 = z0 + th_step
        # Thread crest (wider)
        add_cylinder(bm, (cx, 0.0), radius=r_thread, h_bottom=z0, h_top=z1, segments=segments_cyl, mat_idx=0, uv_coord=UV_THREAD)
        # Thread root (narrower)
        add_cylinder(bm, (cx, 0.0), radius=r_thread * 0.88, h_bottom=z1, h_top=z2, segments=segments_cyl, mat_idx=0, uv_coord=UV_THREAD)

    # -------------------------------------------------------------
    # 3. Toroidal NBR Rubber O-Ring Washer (M_Rubber)
    # Smooth 24 segments under body shoulder
    # -------------------------------------------------------------
    add_cylinder(bm, (cx, 0.0), radius=r_hex * 0.94, h_bottom=-0.0018, h_top=0.0005, segments=segments_cyl, mat_idx=1, uv_coord=UV_RUBBER)

    # -------------------------------------------------------------
    # 4. Main Hex Body with Chamfered Wrench Flats (0.0005 to h_body)
    # -------------------------------------------------------------
    add_chamfered_hex(bm, (cx, 0.0), radius=r_hex, h_bottom=0.0005, h_top=h_body, chamfer=0.0010, mat_idx=0, uv_coord=UV_METAL)

    # -------------------------------------------------------------
    # 5. Collet Clamping Crown (12 distinct 3D flexible fingers)
    # -------------------------------------------------------------
    z_collet_bot = h_body
    z_collet_top = h_body + 0.0040
    num_fingers = 12
    for fi in range(num_fingers):
        ang0 = fi * (2.0 * math.pi / num_fingers)
        ang1 = ang0 + (math.pi / num_fingers) * 0.65
        rf0 = r_thread * 0.98
        rf1 = r_thread * 0.88
        p0 = (cx + rf0 * math.cos(ang0), rf0 * math.sin(ang0), z_collet_bot)
        p1 = (cx + rf0 * math.cos(ang1), rf0 * math.sin(ang1), z_collet_bot)
        p2 = (cx + rf1 * math.cos(ang1), rf1 * math.sin(ang1), z_collet_top)
        p3 = (cx + rf1 * math.cos(ang0), rf1 * math.sin(ang0), z_collet_top)
        v0 = bm.verts.new(p0)
        v1 = bm.verts.new(p1)
        v2 = bm.verts.new(p2)
        v3 = bm.verts.new(p3)
        ff = bm.faces.new((v0, v1, v2, v3))
        ff.material_index = 0
        for l in ff.loops: l[uv_layer].uv = UV_METAL

    # -------------------------------------------------------------
    # 6. Compression Cap Nut
    # Chamfered hex base transitioning into smooth 24-segment beveled dome
    # -------------------------------------------------------------
    z_nut_base = h_body + 0.0025
    z_nut_hex_top = z_nut_base + h_nut * 0.55
    z_nut_dome_top = z_nut_base + h_nut
    
    # Hex portion of nut
    add_chamfered_hex(bm, (cx, 0.0), radius=r_hex * 0.98, h_bottom=z_nut_base, h_top=z_nut_hex_top, chamfer=0.0008, mat_idx=0, uv_coord=UV_METAL)
    
    # Smooth beveled dome crown (24 segments, 2 height rings for curved profile)
    r_dome_hole = r_cable * 1.30
    v_dome_b, v_dome_m, v_dome_t = [], [], []
    z_mid = z_nut_hex_top + (z_nut_dome_top - z_nut_hex_top) * 0.55
    r_mid = r_hex * 0.98 * 0.68 + r_dome_hole * 0.32
    
    for s in range(segments_cyl):
        ang = s * (2.0 * math.pi / segments_cyl)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_dome_b.append(bm.verts.new((cx + (r_hex * 0.98 - 0.0008) * cos_a, (r_hex * 0.98 - 0.0008) * sin_a, z_nut_hex_top)))
        v_dome_m.append(bm.verts.new((cx + r_mid * cos_a, r_mid * sin_a, z_mid)))
        v_dome_t.append(bm.verts.new((cx + r_dome_hole * cos_a, r_dome_hole * sin_a, z_nut_dome_top)))
        
    for s in range(segments_cyl):
        sn = (s + 1) % segments_cyl
        f1 = bm.faces.new((v_dome_b[s], v_dome_b[sn], v_dome_m[sn], v_dome_m[s]))
        f1.material_index = 0
        for l in f1.loops: l[uv_layer].uv = UV_DOME
        f2 = bm.faces.new((v_dome_m[s], v_dome_m[sn], v_dome_t[sn], v_dome_t[s]))
        f2.material_index = 0
        for l in f2.loops: l[uv_layer].uv = UV_DOME

    # -------------------------------------------------------------
    # 7. Internal EPDM Rubber Grommet Bushing (M_Rubber)
    # -------------------------------------------------------------
    v_grom_t, v_grom_b = [], []
    for s in range(segments_cyl):
        ang = s * (2.0 * math.pi / segments_cyl)
        v_grom_t.append(bm.verts.new((cx + r_dome_hole * math.cos(ang), r_dome_hole * math.sin(ang), z_nut_dome_top)))
        v_grom_b.append(bm.verts.new((cx + r_cable * 1.05 * math.cos(ang), r_cable * 1.05 * math.sin(ang), z_nut_dome_top - 0.0035)))
    for s in range(segments_cyl):
        sn = (s + 1) % segments_cyl
        f = bm.faces.new((v_grom_t[s], v_grom_t[sn], v_grom_b[sn], v_grom_b[s]))
        f.material_index = 1
        for l in f.loops: l[uv_layer].uv = UV_RUBBER

    # -------------------------------------------------------------
    # 8. High-Poly Round Security Cable (M_Rubber)
    # Smooth 24 segments
    # -------------------------------------------------------------
    z_cable_bot = z_lock_bot - 0.020
    z_cable_top = z_nut_dome_top + 0.026
    add_cylinder(bm, (cx, 0.0), radius=r_cable, h_bottom=z_cable_bot, h_top=z_cable_top, segments=segments_cyl, mat_idx=1, uv_coord=UV_RUBBER)

    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_metal)
    obj.data.materials.append(mat_rubber)
    return obj

def build_sec_cable_gland_set(export_dir):
    clear_scene()
    setup_units()
    
    mat_metal, mat_rubber = create_materials(export_dir)
    
    coll = bpy.data.collections.new("SEC_Cable_Gland_Set_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    root = bpy.data.objects.new("SEC_Cable_Gland_Set", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    # 1. Gland Small (M16x1.5): cx = -0.065
    obj_small = build_high_poly_gland(
        name="Gland_Small",
        cx=-0.065,
        r_thread=0.0080, # Ø16mm
        r_hex=0.0125,    # 22mm across flats
        r_cable=0.0030,  # Ø6mm cable
        h_thread=0.0090,
        h_body=0.0055,
        h_nut=0.0125,
        mat_metal=mat_metal,
        mat_rubber=mat_rubber
    )
    obj_small.parent = root
    coll.objects.link(obj_small)
    
    # 2. Gland Medium (M20x1.5): cx = 0.000
    obj_medium = build_high_poly_gland(
        name="Gland_Medium",
        cx=0.000,
        r_thread=0.0100, # Ø20mm
        r_hex=0.0145,    # 25mm across flats
        r_cable=0.0040,  # Ø8mm cable
        h_thread=0.0100,
        h_body=0.0065,
        h_nut=0.0145,
        mat_metal=mat_metal,
        mat_rubber=mat_rubber
    )
    obj_medium.parent = root
    coll.objects.link(obj_medium)
    
    # 3. Gland Large (M25x1.5): cx = +0.065
    obj_large = build_high_poly_gland(
        name="Gland_Large",
        cx=0.065,
        r_thread=0.0125, # Ø25mm
        r_hex=0.0175,    # 30mm across flats
        r_cable=0.0055,  # Ø11mm cable
        h_thread=0.0115,
        h_body=0.0075,
        h_nut=0.0175,
        mat_metal=mat_metal,
        mat_rubber=mat_rubber
    )
    obj_large.parent = root
    coll.objects.link(obj_large)
    
    total_tris = 0
    all_meshes = [obj_small, obj_medium, obj_large]
    for child in all_meshes:
        child_bm = bmesh.new()
        child_bm.from_mesh(child.data)
        bmesh.ops.triangulate(child_bm, faces=child_bm.faces)
        total_tris += len(child_bm.faces)
        child_bm.free()
        
    print(f"High-Poly Professional SEC_Cable_Gland_Set (NO TEXT): Total Triangles = {total_tris}")
    
    # Configure screens for Material Preview and Texture color
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'
                        r3d = space.region_3d
                        r3d.view_distance = 0.22
                        r3d.view_location = (0.0, 0.0, 0.005)
                        
    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Cable_Gland_Set.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Cable_Gland_Set.fbx")
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
        "asset_name": "SEC_Cable_Gland_Set",
        "fbx_path": "exports/SEC_Cable_Gland_Set.fbx",
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
    export_directory = r"C:\Users\Burak\Desktop\Security_CCTV\69. SEC_Cable_Gland_Set\exports"
    build_sec_cable_gland_set(export_directory)
