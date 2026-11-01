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
    node_bsdf.inputs['Roughness'].default_value = 0.22
    
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

def add_cylinder_y(bm, center_xz, radius, y_min, y_max, segments=16, uv_coord=(0.25, 0.75), add_caps=False):
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

def add_detailed_compression_fitting(bm, center_xz, y_base, y_tip, is_end_b=False, uv_nut=(0.75, 0.75), uv_thread=(0.25, 0.25)):
    # Direction along Y
    cx, cz = center_xz
    uv_layer = bm.loops.layers.uv.verify()
    
    # Sign for fitting orientation
    sign = -1.0 if is_end_b else 1.0
    
    # 1. Threaded male connector with 4 real thread rings (segments = 16)
    # y ranges from y_base to y_base + sign * 0.015
    y_th_start = y_base - 0.016 if not is_end_b else y_base + 0.002
    y_th_end   = y_base        if not is_end_b else y_base + 0.018
    add_cylinder_y(bm, (cx, cz), radius=0.010, y_min=y_th_start, y_max=y_th_end, segments=16, uv_coord=uv_thread, add_caps=True)
    # 4 thread crest rings
    for tr in range(4):
        ty = y_th_start + (tr + 0.5) * ((y_th_end - y_th_start) / 4.0)
        add_cylinder_y(bm, (cx, cz), radius=0.0112, y_min=ty - 0.001, y_max=ty + 0.001, segments=16, uv_coord=uv_thread, add_caps=True)
        
    # 2. Hexagonal compression body nut (12-segment chamfered hex nut)
    y_nut_start = y_base if not is_end_b else y_base - 0.018
    y_nut_end   = y_base + 0.018 if not is_end_b else y_base
    
    r_hex = 0.0155
    r_in = 0.0105
    vb, vt = [], []
    for s in range(6):
        ang = s * (2.0 * math.pi / 6.0)
        vb.append(bm.verts.new((cx + r_hex * math.cos(ang), y_nut_start, cz + r_hex * math.sin(ang))))
        vt.append(bm.verts.new((cx + r_hex * math.cos(ang), y_nut_end, cz + r_hex * math.sin(ang))))
    for s in range(6):
        sn = (s + 1) % 6
        f = bm.faces.new((vb[s], vb[sn], vt[sn], vt[s]))
        f.material_index = 0
        for l in f.loops: l[uv_layer].uv = uv_nut
        
    # Chamfered annular end faces
    vb_in, vt_in = [], []
    for s in range(6):
        ang = s * (2.0 * math.pi / 6.0)
        vb_in.append(bm.verts.new((cx + r_in * math.cos(ang), y_nut_start, cz + r_in * math.sin(ang))))
        vt_in.append(bm.verts.new((cx + r_in * math.cos(ang), y_nut_end, cz + r_in * math.sin(ang))))
    for s in range(6):
        sn = (s + 1) % 6
        f_b = bm.faces.new((vb[sn], vb[s], vb_in[s], vb_in[sn]))
        f_b.material_index = 0
        for l in f_b.loops: l[uv_layer].uv = uv_nut
        f_t = bm.faces.new((vt[s], vt[sn], vt_in[sn], vt_in[s]))
        f_t.material_index = 0
        for l in f_t.loops: l[uv_layer].uv = uv_nut
        
    # 3. Crimp ferrule lock sleeve
    y_fer_start = y_nut_end if not is_end_b else y_base - 0.025
    y_fer_end   = y_base + 0.025 if not is_end_b else y_nut_start
    add_cylinder_y(bm, (cx, cz), radius=0.0125, y_min=y_fer_start, y_max=y_fer_end, segments=16, uv_coord=uv_nut, add_caps=False)
    # Ferrule crimp ring bead
    y_cr_mid = (y_fer_start + y_fer_end) * 0.5
    add_cylinder_y(bm, (cx, cz), radius=0.0135, y_min=y_cr_mid - 0.0015, y_max=y_cr_mid + 0.0015, segments=16, uv_coord=uv_nut, add_caps=True)

def build_high_detail_hose(export_dir):
    clear_scene()
    setup_units()
    
    mat_metal = create_metal_material(export_dir)
    
    coll = bpy.data.collections.new("SEC_Conduit_Flexible_Hose_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    # Root Empty at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Conduit_Flexible_Hose", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.10
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    UV_CORRUGATED = (0.25, 0.75)   # Corrugated flex hose ribbing
    UV_NUT = (0.75, 0.75)          # Polished hex fitting
    UV_THREAD = (0.25, 0.25)       # Threaded male connector
    
    # =============================================================
    # 1. End_Fitting_A (At Y = 0.0)
    # =============================================================
    mesh_fa = bpy.data.meshes.new("End_Fitting_A")
    bm_fa = bmesh.new()
    bm_fa.loops.layers.uv.new("UVMap")
    
    add_detailed_compression_fitting(bm_fa, (0.0, 0.0), y_base=0.0, y_tip=-0.016, is_end_b=False, uv_nut=UV_NUT, uv_thread=UV_THREAD)
    
    bm_fa.to_mesh(mesh_fa)
    bm_fa.free()
    obj_fa = bpy.data.objects.new("End_Fitting_A", mesh_fa)
    obj_fa.data.materials.append(mat_metal)
    obj_fa.parent = root
    coll.objects.link(obj_fa)
    
    # =============================================================
    # 2. End_Fitting_B (At Y = 0.50m)
    # =============================================================
    mesh_fb = bpy.data.meshes.new("End_Fitting_B")
    bm_fb = bmesh.new()
    bm_fb.loops.layers.uv.new("UVMap")
    
    add_detailed_compression_fitting(bm_fb, (0.0, 0.0), y_base=0.50, y_tip=0.518, is_end_b=True, uv_nut=UV_NUT, uv_thread=UV_THREAD)
    
    bm_fb.to_mesh(mesh_fb)
    bm_fb.free()
    obj_fb = bpy.data.objects.new("End_Fitting_B", mesh_fb)
    obj_fb.data.materials.append(mat_metal)
    obj_fb.parent = root
    coll.objects.link(obj_fb)
    
    # =============================================================
    # 3. Hose_Mesh (High-Detail 16-Segment Corrugated Flexible Conduit)
    # 45 rings (44 longitudinal segments), 16 radial segments
    # Alternating physical 3D crests (R=0.0105m) and roots (R=0.0090m)!
    # =============================================================
    mesh_hose = bpy.data.meshes.new("Hose_Mesh")
    bm_h = bmesh.new()
    uv_h = bm_h.loops.layers.uv.new("UVMap")
    
    N_RINGS = 45
    N_RADIAL = 16
    rings = []
    
    y_start = 0.025
    y_end = 0.475
    
    for i in range(N_RINGS):
        t = i / (N_RINGS - 1)
        # S-curve with zero tangent tilt at endpoints
        s_curve = math.sin(math.pi * t) ** 2
        cy = y_start + (y_end - y_start) * t
        cx = 0.045 * s_curve
        cz = -0.055 * s_curve
        
        # Tangent vector
        dy = y_end - y_start
        dx = 0.045 * math.pi * math.sin(2.0 * math.pi * t)
        dz = -0.055 * math.pi * math.sin(2.0 * math.pi * t)
        t_len = math.sqrt(dx*dx + dy*dy + dz*dz)
        tx, ty, tz = dx / t_len, dy / t_len, dz / t_len
        
        # Orthogonal basis
        ux, uy, uz = -tz * ty, -tz * (-tx), tx*tx + ty*ty
        u_len = math.sqrt(ux*ux + uy*uy + uz*uz)
        if u_len < 1e-4:
            nx, ny, nz = 1.0, 0.0, 0.0
            bx, by, bz = 0.0, 0.0, 1.0
        else:
            bx, by, bz = ux / u_len, uy / u_len, uz / u_len
            nx = ty * bz - tz * by
            ny = tz * bx - tx * bz
            nz = tx * by - ty * bx
            
        # Alternating physical 3D corrugation rings
        r_curr = 0.0106 if (i % 2 == 0) else 0.0092
        
        ring_verts = []
        for s in range(N_RADIAL):
            ang = s * (2.0 * math.pi / N_RADIAL)
            vx = cx + r_curr * (math.cos(ang) * nx + math.sin(ang) * bx)
            vy = cy + r_curr * (math.cos(ang) * ny + math.sin(ang) * by)
            vz = cz + r_curr * (math.cos(ang) * nz + math.sin(ang) * bz)
            ring_verts.append(bm_h.verts.new((vx, vy, vz)))
        rings.append(ring_verts)
        
    for i in range(N_RINGS - 1):
        v1 = rings[i]
        v2 = rings[i + 1]
        v_coord_0 = (i / (N_RINGS - 1)) * 0.45 + 0.50
        v_coord_1 = ((i + 1) / (N_RINGS - 1)) * 0.45 + 0.50
        for s in range(N_RADIAL):
            sn = (s + 1) % N_RADIAL
            f = bm_h.faces.new((v1[s], v1[sn], v2[sn], v2[s]))
            f.material_index = 0
            u_coord_0 = s / N_RADIAL
            u_coord_1 = (s + 1) / N_RADIAL
            f.loops[0][uv_h].uv = (u_coord_0, v_coord_0)
            f.loops[1][uv_h].uv = (u_coord_1, v_coord_0)
            f.loops[2][uv_h].uv = (u_coord_1, v_coord_1)
            f.loops[3][uv_h].uv = (u_coord_0, v_coord_1)
            
    bm_h.to_mesh(mesh_hose)
    bm_h.free()
    obj_hose = bpy.data.objects.new("Hose_Mesh", mesh_hose)
    obj_hose.data.materials.append(mat_metal)
    obj_hose.parent = root
    coll.objects.link(obj_hose)
    
    # Smooth shading and edge split modifier
    all_meshes = [obj_hose, obj_fa, obj_fb]
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
        
    print(f"High-Detail SEC_Conduit_Flexible_Hose Triangles: {total_tris}")
    
    # Set Material Preview on 3D view
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'
                        space.region_3d.view_distance = 0.70
                        space.region_3d.view_location = (0.02, 0.25, -0.025)
                        
    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Conduit_Flexible_Hose.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Conduit_Flexible_Hose.fbx")
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
                if mat: materials_found.add(mat.name)
        elif obj.type == 'EMPTY':
            reimported_empties += 1
            
    print(f"Re-import check: Meshes={reimported_meshes}, Empties={reimported_empties}, Tris={reimported_tris}")
    status = "SUCCESS" if (reimported_meshes == 3 and reimported_empties == 1 and reimported_tris == original_tris) else "FAILED"
    
    manifest = {
        "asset_name": "SEC_Conduit_Flexible_Hose",
        "fbx_path": "exports/SEC_Conduit_Flexible_Hose.fbx",
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
    export_directory = r"C:\Users\Burak\Desktop\Security_CCTV\73. SEC_Conduit_Flexible_Hose\exports"
    build_high_detail_hose(export_directory)
