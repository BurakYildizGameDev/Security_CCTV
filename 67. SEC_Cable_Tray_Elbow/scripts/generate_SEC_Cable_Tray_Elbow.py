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

def create_metal_material(texture_path):
    mat = bpy.data.materials.new(name="M_Security_Atlas")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (400, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (0, 0)
    node_bsdf.inputs['Metallic'].default_value = 0.0
    node_bsdf.inputs['Roughness'].default_value = 0.35
    
    if os.path.exists(texture_path):
        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.location = (-400, 0)
        img = bpy.data.images.load(texture_path)
        img.name = "T_Security_Atlas.png"
        node_tex.image = img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])
        links.new(node_tex.outputs['Alpha'], node_bsdf.inputs['Alpha'])
        nodes.active = node_tex
    else:
        node_bsdf.inputs['Base Color'].default_value = (0.78, 0.80, 0.82, 1.0)

    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    mat.blend_method = 'CLIP'
    mat.alpha_threshold = 0.5
    if hasattr(mat, 'surface_render_method'):
        mat.surface_render_method = 'DITHERED'
        
    mat.diffuse_color = (0.75, 0.77, 0.80, 1.0)
    return mat

def build_sec_cable_tray_elbow(export_dir):
    clear_scene()
    setup_units()
    
    atlas_path = os.path.join(export_dir, "T_Security_Atlas.png")
    mat_metal = create_metal_material(atlas_path)
    
    coll = bpy.data.collections.new("SEC_Cable_Tray_Elbow_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    root = bpy.data.objects.new("SEC_Cable_Tray_Elbow", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.20
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    R_in = 0.150
    R_out = 0.350
    H = 0.050
    hem_h = 0.043
    num_segs = 12
    
    # 1. Elbow_Base with physical punched radial slot perforations
    base_mesh = bpy.data.meshes.new("Elbow_Base")
    bm_b = bmesh.new()
    uv_b = bm_b.loops.layers.uv.new("UVMap")
    
    r_rings = [0.150, 0.200, 0.235, 0.265, 0.300, 0.350]
    
    grid_verts = []
    for i in range(num_segs + 1):
        frac = i / num_segs
        theta = frac * (math.pi / 2.0)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        
        col = []
        for r in r_rings:
            v = bm_b.verts.new((r * cos_t, r * sin_t, 0.001))
            col.append((v, frac, r))
        grid_verts.append(col)

    bm_b.verts.ensure_lookup_table()

    for i in range(num_segs):
        c0 = grid_verts[i]
        c1 = grid_verts[i+1]
        
        bm_b.faces.new((c0[0][0], c1[0][0], c1[1][0], c0[1][0]))
        bm_b.faces.new((c0[1][0], c1[1][0], c1[2][0], c0[2][0]))
        if i % 2 == 0:
            bm_b.faces.new((c0[2][0], c1[2][0], c1[3][0], c0[3][0]))
        bm_b.faces.new((c0[3][0], c1[3][0], c1[4][0], c0[4][0]))
        bm_b.faces.new((c0[4][0], c1[4][0], c1[5][0], c0[5][0]))

    for f in bm_b.faces:
        for loop in f.loops:
            v = loop.vert.co
            r = math.hypot(v.x, v.y)
            theta = math.atan2(v.y, v.x)
            u = 0.03 + (theta / (math.pi / 2.0)) * 0.94
            v_coord = 0.52 + ((r - R_in) / (R_out - R_in)) * 0.44
            loop[uv_b].uv = (u, v_coord)

    bm_b.to_mesh(base_mesh)
    bm_b.free()
    obj_base = bpy.data.objects.new("Elbow_Base", base_mesh)
    obj_base.data.materials.append(mat_metal)
    obj_base.parent = root
    coll.objects.link(obj_base)

    # 2. Side_Walls
    walls_mesh = bpy.data.meshes.new("Side_Walls")
    bm_w = bmesh.new()
    uv_w = bm_w.loops.layers.uv.new("UVMap")

    # Inner Wall
    in_profile = []
    for i in range(num_segs + 1):
        frac = i / num_segs
        theta = frac * (math.pi / 2.0)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        
        v0 = bm_w.verts.new((R_in * cos_t, R_in * sin_t, 0.0))
        v1 = bm_w.verts.new((R_in * cos_t, R_in * sin_t, H))
        v2 = bm_w.verts.new(((R_in + 0.008) * cos_t, (R_in + 0.008) * sin_t, H))
        v3 = bm_w.verts.new(((R_in + 0.008) * cos_t, (R_in + 0.008) * sin_t, hem_h))
        in_profile.append((v0, v1, v2, v3, frac))

    for i in range(num_segs):
        p0 = in_profile[i]
        p1 = in_profile[i+1]
        f_wall = bm_w.faces.new((p0[0], p1[0], p1[1], p0[1]))
        f_htop = bm_w.faces.new((p0[1], p1[1], p1[2], p0[2]))
        f_hlip = bm_w.faces.new((p0[2], p1[2], p1[3], p0[3]))
        
        for f in (f_wall, f_htop, f_hlip):
            for loop in f.loops:
                u = 0.03 + (p0[4] if loop.vert in (p0[0], p0[1], p0[2], p0[3]) else p1[4]) * 0.94
                v_c = 0.38 + (loop.vert.co.z / H) * 0.12
                loop[uv_w].uv = (u, v_c)

    # Outer Wall
    out_profile = []
    for i in range(num_segs + 1):
        frac = i / num_segs
        theta = frac * (math.pi / 2.0)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        
        v0 = bm_w.verts.new((R_out * cos_t, R_out * sin_t, 0.0))
        v1 = bm_w.verts.new((R_out * cos_t, R_out * sin_t, H))
        v2 = bm_w.verts.new(((R_out - 0.008) * cos_t, (R_out - 0.008) * sin_t, H))
        v3 = bm_w.verts.new(((R_out - 0.008) * cos_t, (R_out - 0.008) * sin_t, hem_h))
        out_profile.append((v0, v1, v2, v3, frac))

    for i in range(num_segs):
        p0 = out_profile[i]
        p1 = out_profile[i+1]
        f_wall = bm_w.faces.new((p1[0], p0[0], p0[1], p1[1]))
        f_htop = bm_w.faces.new((p1[1], p0[1], p0[2], p1[2]))
        f_hlip = bm_w.faces.new((p1[2], p0[2], p0[3], p1[3]))
        
        for f in (f_wall, f_htop, f_hlip):
            for loop in f.loops:
                u = 0.03 + (1.0 - (p0[4] if loop.vert in (p0[0], p0[1], p0[2], p0[3]) else p1[4])) * 0.94
                v_c = 0.26 + (loop.vert.co.z / H) * 0.12
                loop[uv_w].uv = (u, v_c)

    bm_w.to_mesh(walls_mesh)
    bm_w.free()

    for poly in walls_mesh.polygons:
        poly.use_smooth = True

    obj_walls = bpy.data.objects.new("Side_Walls", walls_mesh)
    obj_walls.data.materials.append(mat_metal)
    obj_walls.parent = root
    coll.objects.link(obj_walls)

    total_tris = 0
    for child in [obj_base, obj_walls]:
        child_bm = bmesh.new()
        child_bm.from_mesh(child.data)
        bmesh.ops.triangulate(child_bm, faces=child_bm.faces)
        total_tris += len(child_bm.faces)
        child_bm.free()
        
    print(f"SEC_Cable_Tray_Elbow: Total Triangles = {total_tris} (Budget <= 360 tris)")
    assert total_tris <= 360, f"Triangle budget exceeded: {total_tris} > 360"
    
    # Set all screens to Material Preview and Texture color
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'

    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Cable_Tray_Elbow.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Cable_Tray_Elbow.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    obj_base.select_set(True)
    obj_walls.select_set(True)
    
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
    
    imported_meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    imported_empties = [obj for obj in bpy.context.scene.objects if obj.type == 'EMPTY']
    
    reimport_tris = 0
    for m in imported_meshes:
        bm = bmesh.new()
        bm.from_mesh(m.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        reimport_tris += len(bm.faces)
        bm.free()
        
    print(f"Re-import check: Meshes={len(imported_meshes)}, Empties={len(imported_empties)}, Tris={reimport_tris}")
    
    manifest_path = os.path.join(export_dir, "manifest.json")
    manifest_data = {
        "asset_name": "SEC_Cable_Tray_Elbow",
        "fbx_path": "SEC_Cable_Tray_Elbow.fbx",
        "blend_path": "SEC_Cable_Tray_Elbow.blend",
        "triangles": reimport_tris,
        "mesh_count": len(imported_meshes),
        "empty_count": len(imported_empties),
        "materials": ["M_Metal"],
        "dimensions_meters": {
            "inner_radius": 0.15,
            "outer_radius": 0.35,
            "width": 0.20,
            "height": 0.05
        },
        "status": "SUCCESS" if (reimport_tris <= 360 and len(imported_meshes) == 2) else "FAILED"
    }
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    export_dir = os.path.abspath(r"67. SEC_Cable_Tray_Elbow\exports")
    build_sec_cable_tray_elbow(export_dir)
