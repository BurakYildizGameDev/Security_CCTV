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

def build_sec_cable_tray_straight(export_dir):
    clear_scene()
    setup_units()
    
    atlas_path = os.path.join(export_dir, "T_Security_Atlas.png")
    mat_metal = create_metal_material(atlas_path)
    
    coll = bpy.data.collections.new("SEC_Cable_Tray_Straight_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    root = bpy.data.objects.new("SEC_Cable_Tray_Straight", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.15
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    # 1. Tray_Base with physical punched rectangular mounting slots
    # Width 200mm (X: -0.100 to +0.100), Length 1000mm (Y: 0.000 to 1.000)
    # We create 8 slots along Y.
    # Longitudinal strips:
    # Track 0: X: -0.100 to -0.040 (solid left flange)
    # Track 1: X: -0.040 to +0.040 (center slot region: alternating hole/solid rung)
    # Track 2: X: +0.040 to +0.100 (solid right flange)
    base_mesh = bpy.data.meshes.new("Tray_Base")
    bm_b = bmesh.new()
    uv_b = bm_b.loops.layers.uv.new("UVMap")
    
    num_rungs = 16 # 8 holes, 8 rungs
    y_steps = [i / num_rungs for i in range(num_rungs + 1)]
    x_tracks = [-0.100, -0.040, 0.040, 0.100]
    
    grid = []
    for yi, y in enumerate(y_steps):
        row = []
        for xi, x in enumerate(x_tracks):
            v = bm_b.verts.new((x, y, 0.001))
            row.append(v)
        grid.append(row)
        
    bm_b.verts.ensure_lookup_table()
    
    for yi in range(num_rungs):
        r0 = grid[yi]
        r1 = grid[yi+1]
        
        # Left solid track
        bm_b.faces.new((r0[0], r1[0], r1[1], r0[1]))
        # Center track (leave odd cells as real cutout holes!)
        if yi % 2 == 0:
            bm_b.faces.new((r0[1], r1[1], r1[2], r0[2]))
        # Right solid track
        bm_b.faces.new((r0[2], r1[2], r1[3], r0[3]))

    for f in bm_b.faces:
        for loop in f.loops:
            v = loop.vert.co
            u = 0.03 + (v.y / 1.0) * 0.94
            v_coord = 0.52 + ((v.x - (-0.100)) / 0.200) * 0.44
            loop[uv_b].uv = (u, v_coord)

    bm_b.to_mesh(base_mesh)
    bm_b.free()
    obj_base = bpy.data.objects.new("Tray_Base", base_mesh)
    obj_base.data.materials.append(mat_metal)
    obj_base.parent = root
    coll.objects.link(obj_base)
    
    # 2. Side_Wall_Left with top rolled safety hem
    mesh_lw = bpy.data.meshes.new("Side_Wall_Left")
    bm_l = bmesh.new()
    uv_l = bm_l.loops.layers.uv.new("UVMap")
    
    lw_verts = [
        bm_l.verts.new((-0.100, 0.0, 0.0)),
        bm_l.verts.new((-0.100, 0.0, 0.050)),
        bm_l.verts.new((-0.092, 0.0, 0.050)),
        bm_l.verts.new((-0.092, 0.0, 0.043)),
        bm_l.verts.new((-0.100, 1.0, 0.0)),
        bm_l.verts.new((-0.100, 1.0, 0.050)),
        bm_l.verts.new((-0.092, 1.0, 0.050)),
        bm_l.verts.new((-0.092, 1.0, 0.043)),
    ]
    bm_l.faces.new((lw_verts[0], lw_verts[1], lw_verts[5], lw_verts[4]))
    bm_l.faces.new((lw_verts[1], lw_verts[2], lw_verts[6], lw_verts[5]))
    bm_l.faces.new((lw_verts[2], lw_verts[3], lw_verts[7], lw_verts[6]))
    
    for f in bm_l.faces:
        for loop in f.loops:
            v = loop.vert.co
            u = 0.03 + (v.y / 1.0) * 0.94
            v_coord = 0.38 + (v.z / 0.050) * 0.12
            loop[uv_l].uv = (u, v_coord)
            
    bm_l.to_mesh(mesh_lw)
    bm_l.free()
    obj_lw = bpy.data.objects.new("Side_Wall_Left", mesh_lw)
    obj_lw.data.materials.append(mat_metal)
    obj_lw.parent = root
    coll.objects.link(obj_lw)

    # 3. Side_Wall_Right with top rolled safety hem
    mesh_rw = bpy.data.meshes.new("Side_Wall_Right")
    bm_r = bmesh.new()
    uv_r = bm_r.loops.layers.uv.new("UVMap")
    
    rw_verts = [
        bm_r.verts.new((0.100, 0.0, 0.0)),
        bm_r.verts.new((0.100, 0.0, 0.050)),
        bm_r.verts.new((0.092, 0.0, 0.050)),
        bm_r.verts.new((0.092, 0.0, 0.043)),
        bm_r.verts.new((0.100, 1.0, 0.0)),
        bm_r.verts.new((0.100, 1.0, 0.050)),
        bm_r.verts.new((0.092, 1.0, 0.050)),
        bm_r.verts.new((0.092, 1.0, 0.043)),
    ]
    bm_r.faces.new((rw_verts[4], rw_verts[5], rw_verts[1], rw_verts[0]))
    bm_r.faces.new((rw_verts[5], rw_verts[6], rw_verts[2], rw_verts[1]))
    bm_r.faces.new((rw_verts[6], rw_verts[7], rw_verts[3], rw_verts[2]))
    
    for f in bm_r.faces:
        for loop in f.loops:
            v = loop.vert.co
            u = 0.03 + ((1.0 - v.y) / 1.0) * 0.94
            v_coord = 0.26 + (v.z / 0.050) * 0.12
            loop[uv_r].uv = (u, v_coord)
            
    bm_r.to_mesh(mesh_rw)
    bm_r.free()
    obj_rw = bpy.data.objects.new("Side_Wall_Right", mesh_rw)
    obj_rw.data.materials.append(mat_metal)
    obj_rw.parent = root
    coll.objects.link(obj_rw)
    
    # Tris count
    total_tris = 0
    for child in [obj_base, obj_lw, obj_rw]:
        child_bm = bmesh.new()
        child_bm.from_mesh(child.data)
        bmesh.ops.triangulate(child_bm, faces=child_bm.faces)
        total_tris += len(child_bm.faces)
        child_bm.free()
        
    print(f"SEC_Cable_Tray_Straight: Total Triangles = {total_tris} (Budget <= 220 tris)")
    assert total_tris <= 220, f"Triangle budget exceeded: {total_tris} > 220"
    
    # Set all screens to Material Preview and Texture color
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'

    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Cable_Tray_Straight.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Cable_Tray_Straight.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    obj_base.select_set(True)
    obj_lw.select_set(True)
    obj_rw.select_set(True)
    
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
        "asset_name": "SEC_Cable_Tray_Straight",
        "fbx_path": "SEC_Cable_Tray_Straight.fbx",
        "blend_path": "SEC_Cable_Tray_Straight.blend",
        "triangles": reimport_tris,
        "mesh_count": len(imported_meshes),
        "empty_count": len(imported_empties),
        "materials": ["M_Metal"],
        "dimensions_meters": {
            "width": 0.20,
            "height": 0.05,
            "length": 1.00
        },
        "status": "SUCCESS" if (reimport_tris <= 220 and len(imported_meshes) == 3) else "FAILED"
    }
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    export_dir = os.path.abspath(r"66. SEC_Cable_Tray_Straight\exports")
    build_sec_cable_tray_straight(export_dir)
