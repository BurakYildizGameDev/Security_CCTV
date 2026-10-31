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

def build_sec_cable_tray_tee(export_dir):
    clear_scene()
    setup_units()
    
    atlas_path = os.path.join(export_dir, "T_Security_Atlas.png")
    mat_metal = create_metal_material(atlas_path)
    
    coll = bpy.data.collections.new("SEC_Cable_Tray_Tee_Coll")
    bpy.context.scene.collection.children.link(coll)
    
    root = bpy.data.objects.new("SEC_Cable_Tray_Tee", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.20
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)
    
    H = 0.050
    hem_h = 0.043
    
    # 1. Main_Channel_A Mesh (-Y Half: Y from -0.300 to 0.000)
    mesh_a = bpy.data.meshes.new("Main_Channel_A")
    bm_a = bmesh.new()
    uv_a = bm_a.loops.layers.uv.new("UVMap")
    
    # Slotted Floor for Channel A
    # Y from -0.300 to 0.000 with punched holes
    y_rungs_a = [-0.300, -0.240, -0.180, -0.120, -0.060, 0.000]
    x_tracks = [-0.100, -0.040, 0.040, 0.100]
    grid_a = []
    for y in y_rungs_a:
        row = []
        for x in x_tracks:
            row.append(bm_a.verts.new((x, y, 0.001)))
        grid_a.append(row)
        
    bm_a.verts.ensure_lookup_table()
    for yi in range(len(y_rungs_a) - 1):
        r0 = grid_a[yi]
        r1 = grid_a[yi+1]
        bm_a.faces.new((r0[0], r1[0], r1[1], r0[1])) # left track
        if yi % 2 == 0:
            bm_a.faces.new((r0[1], r1[1], r1[2], r0[2])) # center rung (odd cells are HOLES!)
        bm_a.faces.new((r0[2], r1[2], r1[3], r0[3])) # right track

    # Back continuous wall segment at X = -0.100
    bwa = [
        bm_a.verts.new((-0.100, -0.300, 0.0)),
        bm_a.verts.new((-0.100, -0.300, H)),
        bm_a.verts.new((-0.092, -0.300, H)),
        bm_a.verts.new((-0.092, -0.300, hem_h)),
        bm_a.verts.new((-0.100,  0.000, 0.0)),
        bm_a.verts.new((-0.100,  0.000, H)),
        bm_a.verts.new((-0.092,  0.000, H)),
        bm_a.verts.new((-0.092,  0.000, hem_h)),
    ]
    bm_a.faces.new((bwa[0], bwa[1], bwa[5], bwa[4]))
    bm_a.faces.new((bwa[1], bwa[2], bwa[6], bwa[5]))
    bm_a.faces.new((bwa[2], bwa[3], bwa[7], bwa[6]))

    # Corner 1 wall (seamless from X: 0.100, Y: -0.300 -> Y: -0.180 -> X: 0.180, Y: -0.100)
    c1_pts = [
        ((0.100, -0.300), (0.092, -0.300)),
        ((0.100, -0.180), (0.092, -0.180)),
        ((0.180, -0.100), (0.180, -0.092)),
    ]
    c1_verts = []
    for (px, py), (hx, hy) in c1_pts:
        v0 = bm_a.verts.new((px, py, 0.0))
        v1 = bm_a.verts.new((px, py, H))
        v2 = bm_a.verts.new((hx, hy, H))
        v3 = bm_a.verts.new((hx, hy, hem_h))
        c1_verts.append((v0, v1, v2, v3))
        
    for i in range(len(c1_pts) - 1):
        q0 = c1_verts[i]
        q1 = c1_verts[i+1]
        bm_a.faces.new((q1[0], q1[1], q0[1], q0[0]))
        bm_a.faces.new((q1[1], q1[2], q0[2], q0[1]))
        bm_a.faces.new((q1[2], q1[3], q0[3], q0[2]))

    # Corner 1 floor gusset
    g1_verts = [
        bm_a.verts.new((0.100, -0.100, 0.001)),
        bm_a.verts.new((0.180, -0.100, 0.001)),
        bm_a.verts.new((0.100, -0.180, 0.001)),
    ]
    bm_a.faces.new((g1_verts[0], g1_verts[1], g1_verts[2]))

    for f in bm_a.faces:
        for loop in f.loops:
            v = loop.vert.co
            if abs(f.normal.z) > 0.5:
                u = 0.03 + ((v.y - (-0.300)) / 0.600) * 0.94
                v_coord = 0.52 + ((v.x - (-0.100)) / 0.200) * 0.44
            else:
                u = 0.03 + ((v.y - (-0.300)) / 0.600) * 0.94
                v_coord = 0.38 + (v.z / H) * 0.12
            loop[uv_a].uv = (u, v_coord)

    bm_a.to_mesh(mesh_a)
    bm_a.free()
    obj_main_a = bpy.data.objects.new("Main_Channel_A", mesh_a)
    obj_main_a.data.materials.append(mat_metal)
    obj_main_a.parent = root
    coll.objects.link(obj_main_a)

    # 2. Main_Channel_B Mesh (+Y Half: Y from 0.000 to +0.300)
    mesh_b = bpy.data.meshes.new("Main_Channel_B")
    bm_b = bmesh.new()
    uv_b = bm_b.loops.layers.uv.new("UVMap")
    
    y_rungs_b = [0.000, 0.060, 0.120, 0.180, 0.240, 0.300]
    grid_b = []
    for y in y_rungs_b:
        row = []
        for x in x_tracks:
            row.append(bm_b.verts.new((x, y, 0.001)))
        grid_b.append(row)
        
    bm_b.verts.ensure_lookup_table()
    for yi in range(len(y_rungs_b) - 1):
        r0 = grid_b[yi]
        r1 = grid_b[yi+1]
        bm_b.faces.new((r0[0], r1[0], r1[1], r0[1]))
        if yi % 2 == 0:
            bm_b.faces.new((r0[1], r1[1], r1[2], r0[2]))
        bm_b.faces.new((r0[2], r1[2], r1[3], r0[3]))

    bwb = [
        bm_b.verts.new((-0.100,  0.000, 0.0)),
        bm_b.verts.new((-0.100,  0.000, H)),
        bm_b.verts.new((-0.092,  0.000, H)),
        bm_b.verts.new((-0.092,  0.000, hem_h)),
        bm_b.verts.new((-0.100,  0.300, 0.0)),
        bm_b.verts.new((-0.100,  0.300, H)),
        bm_b.verts.new((-0.092,  0.300, H)),
        bm_b.verts.new((-0.092,  0.300, hem_h)),
    ]
    bm_b.faces.new((bwb[0], bwb[1], bwb[5], bwb[4]))
    bm_b.faces.new((bwb[1], bwb[2], bwb[6], bwb[5]))
    bm_b.faces.new((bwb[2], bwb[3], bwb[7], bwb[6]))

    c2_pts = [
        ((0.180,  0.100), (0.180,  0.092)),
        ((0.100,  0.180), (0.092,  0.180)),
        ((0.100,  0.300), (0.092,  0.300)),
    ]
    c2_verts = []
    for (px, py), (hx, hy) in c2_pts:
        v0 = bm_b.verts.new((px, py, 0.0))
        v1 = bm_b.verts.new((px, py, H))
        v2 = bm_b.verts.new((hx, hy, H))
        v3 = bm_b.verts.new((hx, hy, hem_h))
        c2_verts.append((v0, v1, v2, v3))
        
    for i in range(len(c2_pts) - 1):
        q0 = c2_verts[i]
        q1 = c2_verts[i+1]
        bm_b.faces.new((q0[0], q0[1], q1[1], q1[0]))
        bm_b.faces.new((q0[1], q0[2], q1[2], q1[1]))
        bm_b.faces.new((q0[2], q0[3], q1[3], q1[2]))

    g2_verts = [
        bm_b.verts.new((0.100, 0.100, 0.001)),
        bm_b.verts.new((0.100, 0.180, 0.001)),
        bm_b.verts.new((0.180, 0.100, 0.001)),
    ]
    bm_b.faces.new((g2_verts[0], g2_verts[1], g2_verts[2]))

    for f in bm_b.faces:
        for loop in f.loops:
            v = loop.vert.co
            if abs(f.normal.z) > 0.5:
                u = 0.03 + ((v.y - (-0.300)) / 0.600) * 0.94
                v_coord = 0.52 + ((v.x - (-0.100)) / 0.200) * 0.44
            else:
                u = 0.03 + ((v.y - (-0.300)) / 0.600) * 0.94
                v_coord = 0.38 + (v.z / H) * 0.12
            loop[uv_b].uv = (u, v_coord)

    bm_b.to_mesh(mesh_b)
    bm_b.free()
    obj_main_b = bpy.data.objects.new("Main_Channel_B", mesh_b)
    obj_main_b.data.materials.append(mat_metal)
    obj_main_b.parent = root
    coll.objects.link(obj_main_b)

    # 3. Branch_Channel Mesh (+X Branch: X from 0.100 to 0.300)
    mesh_br = bpy.data.meshes.new("Branch_Channel")
    bm_br = bmesh.new()
    uv_br = bm_br.loops.layers.uv.new("UVMap")
    
    # Slotted Floor for Branch (X: 0.100 to 0.300)
    x_rungs_br = [0.100, 0.150, 0.200, 0.250, 0.300]
    y_tracks_br = [-0.100, -0.040, 0.040, 0.100]
    grid_br = []
    for x in x_rungs_br:
        row = []
        for y in y_tracks_br:
            row.append(bm_br.verts.new((x, y, 0.001)))
        grid_br.append(row)
        
    bm_br.verts.ensure_lookup_table()
    for xi in range(len(x_rungs_br) - 1):
        r0 = grid_br[xi]
        r1 = grid_br[xi+1]
        bm_br.faces.new((r0[0], r1[0], r1[1], r0[1])) # -Y track
        if xi % 2 == 0:
            bm_br.faces.new((r0[1], r1[1], r1[2], r0[2])) # center rung (odd cells HOLES!)
        bm_br.faces.new((r0[2], r1[2], r1[3], r0[3])) # +Y track

    # Branch -Y Wall (seamless from X: 0.180 to 0.300 at Y: -0.100)
    bw_neg = [
        bm_br.verts.new((0.180, -0.100, 0.0)),
        bm_br.verts.new((0.180, -0.100, H)),
        bm_br.verts.new((0.180, -0.092, H)),
        bm_br.verts.new((0.180, -0.092, hem_h)),
        bm_br.verts.new((0.300, -0.100, 0.0)),
        bm_br.verts.new((0.300, -0.100, H)),
        bm_br.verts.new((0.300, -0.092, H)),
        bm_br.verts.new((0.300, -0.092, hem_h)),
    ]
    bm_br.faces.new((bw_neg[4], bw_neg[5], bw_neg[1], bw_neg[0]))
    bm_br.faces.new((bw_neg[5], bw_neg[6], bw_neg[2], bw_neg[1]))
    bm_br.faces.new((bw_neg[6], bw_neg[7], bw_neg[3], bw_neg[2]))

    # Branch +Y Wall (seamless from X: 0.180 to 0.300 at Y: +0.100)
    bw_pos = [
        bm_br.verts.new((0.180,  0.100, 0.0)),
        bm_br.verts.new((0.180,  0.100, H)),
        bm_br.verts.new((0.180,  0.092, H)),
        bm_br.verts.new((0.180,  0.092, hem_h)),
        bm_br.verts.new((0.300,  0.100, 0.0)),
        bm_br.verts.new((0.300,  0.100, H)),
        bm_br.verts.new((0.300,  0.092, H)),
        bm_br.verts.new((0.300,  0.092, hem_h)),
    ]
    bm_br.faces.new((bw_pos[0], bw_pos[1], bw_pos[5], bw_pos[4]))
    bm_br.faces.new((bw_pos[1], bw_pos[2], bw_pos[6], bw_pos[5]))
    bm_br.faces.new((bw_pos[2], bw_pos[3], bw_pos[7], bw_pos[6]))

    for f in bm_br.faces:
        for loop in f.loops:
            v = loop.vert.co
            if abs(f.normal.z) > 0.5:
                u = 0.03 + ((v.x - 0.100) / 0.200) * 0.94
                v_coord = 0.52 + ((v.y - (-0.100)) / 0.200) * 0.44
            else:
                u = 0.03 + ((v.x - 0.100) / 0.200) * 0.94
                v_coord = 0.26 + (v.z / H) * 0.12
            loop[uv_br].uv = (u, v_coord)

    bm_br.to_mesh(mesh_br)
    bm_br.free()
    obj_branch = bpy.data.objects.new("Branch_Channel", mesh_br)
    obj_branch.data.materials.append(mat_metal)
    obj_branch.parent = root
    coll.objects.link(obj_branch)

    total_tris = 0
    for child in [obj_main_a, obj_main_b, obj_branch]:
        child_bm = bmesh.new()
        child_bm.from_mesh(child.data)
        bmesh.ops.triangulate(child_bm, faces=child_bm.faces)
        total_tris += len(child_bm.faces)
        child_bm.free()
        
    print(f"SEC_Cable_Tray_Tee: Total Triangles = {total_tris} (Budget <= 380 tris)")
    assert total_tris <= 380, f"Triangle budget exceeded: {total_tris} > 380"
    
    # Set all screens to Material Preview and Texture color
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'

    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Cable_Tray_Tee.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        
    fbx_path = os.path.join(export_dir, "SEC_Cable_Tray_Tee.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    obj_main_a.select_set(True)
    obj_main_b.select_set(True)
    obj_branch.select_set(True)
    
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
        "asset_name": "SEC_Cable_Tray_Tee",
        "fbx_path": "SEC_Cable_Tray_Tee.fbx",
        "blend_path": "SEC_Cable_Tray_Tee.blend",
        "triangles": reimport_tris,
        "mesh_count": len(imported_meshes),
        "empty_count": len(imported_empties),
        "materials": ["M_Metal"],
        "dimensions_meters": {
            "main_width": 0.20,
            "main_length": 0.60,
            "branch_width": 0.20,
            "branch_length": 0.30,
            "height": 0.05
        },
        "status": "SUCCESS" if (reimport_tris <= 380 and len(imported_meshes) == 3) else "FAILED"
    }
    
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    export_dir = os.path.abspath(r"68. SEC_Cable_Tray_Tee\exports")
    build_sec_cable_tray_tee(export_dir)
