import os
import sys
import math
import json
import mathutils
from mathutils import Vector, Matrix
import bpy
import bmesh

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    for block in bpy.data.textures: bpy.data.textures.remove(block)
    for block in bpy.data.images: bpy.data.images.remove(block)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)

def setup_units():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

def create_materials(export_dir):
    tex_path = os.path.join(export_dir, "T_Security_Atlas.png")
    img = None
    if os.path.exists(tex_path):
        img = bpy.data.images.load(tex_path)

    # 1. Slot 0: M_Metal
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    nodes_m = mat_metal.node_tree.nodes
    links_m = mat_metal.node_tree.links
    nodes_m.clear()

    out_m = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf_m = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf_m.inputs['Metallic'].default_value = 0.92
    bsdf_m.inputs['Roughness'].default_value = 0.22

    if img:
        tex_node = nodes_m.new('ShaderNodeTexImage')
        tex_node.image = img
        links_m.new(tex_node.outputs['Color'], bsdf_m.inputs['Base Color'])
    else:
        bsdf_m.inputs['Base Color'].default_value = (0.78, 0.81, 0.84, 1.0)
    links_m.new(bsdf_m.outputs['BSDF'], out_m.inputs['Surface'])

    if hasattr(mat_metal, 'blend_method'): mat_metal.blend_method = 'OPAQUE'
    if hasattr(mat_metal, 'shadow_method'): mat_metal.shadow_method = 'OPAQUE'

    # 2. Slot 1: M_Rubber
    mat_rubber = bpy.data.materials.new("M_Rubber")
    mat_rubber.use_nodes = True
    nodes_r = mat_rubber.node_tree.nodes
    links_r = mat_rubber.node_tree.links
    nodes_r.clear()

    out_r = nodes_r.new('ShaderNodeOutputMaterial')
    bsdf_r = nodes_r.new('ShaderNodeBsdfPrincipled')
    bsdf_r.inputs['Metallic'].default_value = 0.04
    bsdf_r.inputs['Roughness'].default_value = 0.82

    if img:
        tex_node_r = nodes_r.new('ShaderNodeTexImage')
        tex_node_r.image = img
        links_r.new(tex_node_r.outputs['Color'], bsdf_r.inputs['Base Color'])
    else:
        bsdf_r.inputs['Base Color'].default_value = (0.12, 0.13, 0.14, 1.0)
    links_r.new(bsdf_r.outputs['BSDF'], out_r.inputs['Surface'])

    if hasattr(mat_rubber, 'blend_method'): mat_rubber.blend_method = 'OPAQUE'
    if hasattr(mat_rubber, 'shadow_method'): mat_rubber.shadow_method = 'OPAQUE'

    return [mat_metal, mat_rubber]

# UV landmarks in 2048x2048 atlas (Blender UV space [0..1, 0..1])
UV_STEEL       = (0.25, 0.75)  # Region 0: Satin Galvanized Steel
UV_HARDWARE    = (0.75, 0.75)  # Region 1: Darkened Hardware Zinc / Bolt Steel
UV_CABLE       = (0.25, 0.25)  # Region 2: Matte EPDM Cable Jacket
UV_BOOT        = (0.75, 0.35)  # Region 3: Molded Ribbed Connector Boot
UV_POLISHED    = (0.75, 0.10)  # Region 4: Polished BNC Bayonet Ring

def build_ceiling_rosette(mats):
    """
    Tavan Montaj Rozeti (Ceiling_Rosette)
    Mounted flat against ceiling at Z=0.0.
    8-segment circular flange with bevel, 4 mounting screws, and central pipe hub.
    Tris budget: 80 tris.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_seg = 8

    r_outer = 0.045
    r_bevel = 0.038
    r_step  = 0.024
    r_inner = 0.0135

    z0 = 0.0000
    z1 = -0.0025
    z2 = -0.0045
    z3 = -0.0100

    # 1. Outer rim rings
    v_rim_top = []
    v_rim_mid = []
    v_rim_bot = []
    v_step    = []
    v_inner   = []

    for s in range(n_seg):
        ang = s * (2.0 * math.pi / n_seg)
        ca, sa = math.cos(ang), math.sin(ang)
        v_rim_top.append(bm.verts.new((ca * r_outer, sa * r_outer, z0)))
        v_rim_mid.append(bm.verts.new((ca * r_bevel, sa * r_bevel, z1)))
        v_rim_bot.append(bm.verts.new((ca * r_step,  sa * r_step,  z2)))
        v_step.append(bm.verts.new((ca * r_step,     sa * r_step,  z3)))
        v_inner.append(bm.verts.new((ca * r_inner,   sa * r_inner, z3)))

    bm.verts.ensure_lookup_table()

    # Outer bevel quads
    for s in range(n_seg):
        sn = (s + 1) % n_seg
        f1 = bm.faces.new((v_rim_top[s], v_rim_top[sn], v_rim_mid[sn], v_rim_mid[s]))
        f1.smooth = True
        f1.material_index = 0
        for l in f1.loops: l[uv_layer].uv = UV_STEEL

        f2 = bm.faces.new((v_rim_mid[s], v_rim_mid[sn], v_rim_bot[sn], v_rim_bot[s]))
        f2.smooth = True
        f2.material_index = 0
        for l in f2.loops: l[uv_layer].uv = UV_STEEL

        f3 = bm.faces.new((v_rim_bot[s], v_rim_bot[sn], v_step[sn], v_step[s]))
        f3.smooth = True
        f3.material_index = 0
        for l in f3.loops: l[uv_layer].uv = UV_STEEL

        f4 = bm.faces.new((v_step[s], v_step[sn], v_inner[sn], v_inner[s]))
        f4.smooth = True
        f4.material_index = 0
        for l in f4.loops: l[uv_layer].uv = UV_STEEL

    # 2. Add 4 countersunk mounting screws
    r_screw_pos = 0.031
    r_sc = 0.0035
    for idx in range(4):
        s_ang = (idx * 0.5 + 0.25) * math.pi
        scx = math.cos(s_ang) * r_screw_pos
        scy = math.sin(s_ang) * r_screw_pos
        scz = z1 - 0.0002

        sv_rim = []
        sv_cen = bm.verts.new((scx, scy, scz - 0.0012))
        for k in range(4):
            kang = k * (0.5 * math.pi)
            kcx = scx + math.cos(kang) * r_sc
            kcy = scy + math.sin(kang) * r_sc
            sv_rim.append(bm.verts.new((kcx, kcy, scz)))

        for k in range(4):
            kn = (k + 1) % 4
            f_sc = bm.faces.new((sv_rim[k], sv_rim[kn], sv_cen))
            f_sc.smooth = False
            f_sc.material_index = 0
            for l in f_sc.loops: l[uv_layer].uv = UV_HARDWARE

    bm.normal_update()
    mesh = bpy.data.meshes.new("Ceiling_Rosette")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def build_drop_pipe(mats):
    """
    Kısa Boru (Drop_Pipe)
    Rigid EMT conduit extending down from Z=-0.008 to Z=-0.075.
    8-segment pipe + compression cable gland collar.
    Tris budget: 64 tris.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_seg = 8

    r_pipe = 0.0125
    r_gland = 0.0155
    r_seal = 0.0070

    z_top = -0.008
    z_mid = -0.058
    z_gland_top = -0.060
    z_bot = -0.075

    v_pipe_top = []
    v_pipe_mid = []
    v_gland_top = []
    v_gland_bot = []
    v_seal_bot = []

    for s in range(n_seg):
        ang = s * (2.0 * math.pi / n_seg)
        ca, sa = math.cos(ang), math.sin(ang)
        v_pipe_top.append(bm.verts.new((ca * r_pipe, sa * r_pipe, z_top)))
        v_pipe_mid.append(bm.verts.new((ca * r_pipe, sa * r_pipe, z_mid)))
        v_gland_top.append(bm.verts.new((ca * r_gland, sa * r_gland, z_gland_top)))
        v_gland_bot.append(bm.verts.new((ca * r_gland, sa * r_gland, z_bot)))
        v_seal_bot.append(bm.verts.new((ca * r_seal, sa * r_seal, z_bot)))

    bm.verts.ensure_lookup_table()

    for s in range(n_seg):
        sn = (s + 1) % n_seg
        # 1. Pipe cylinder (Slot 0 M_Metal)
        f_p = bm.faces.new((v_pipe_top[s], v_pipe_top[sn], v_pipe_mid[sn], v_pipe_mid[s]))
        f_p.smooth = True
        f_p.material_index = 0
        for l in f_p.loops: l[uv_layer].uv = UV_STEEL

        # 2. Pipe to Gland transition flare (Slot 0 M_Metal)
        f_tr = bm.faces.new((v_pipe_mid[s], v_pipe_mid[sn], v_gland_top[sn], v_gland_top[s]))
        f_tr.smooth = True
        f_tr.material_index = 0
        for l in f_tr.loops: l[uv_layer].uv = UV_HARDWARE

        # 3. Gland hex nut outer wall (Slot 0 M_Metal)
        f_gl = bm.faces.new((v_gland_top[s], v_gland_top[sn], v_gland_bot[sn], v_gland_bot[s]))
        f_gl.smooth = True
        f_gl.material_index = 0
        for l in f_gl.loops: l[uv_layer].uv = UV_HARDWARE

        # 4. Gland bottom seal annulus (Slot 1 M_Rubber)
        f_sl = bm.faces.new((v_gland_bot[s], v_gland_bot[sn], v_seal_bot[sn], v_seal_bot[s]))
        f_sl.smooth = False
        f_sl.material_index = 1 # Slot 1: M_Rubber
        for l in f_sl.loops: l[uv_layer].uv = UV_CABLE

    bm.normal_update()
    mesh = bpy.data.meshes.new("Drop_Pipe")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def build_cable_segment(mats, pivot_loc):
    """
    Aşağı Sarkan Kablo (Cable_Segment)
    Swept cylinder child of Cable_Pivot.
    Starts at pivot (0, 0, -0.075) and hangs down to Z=-0.420.
    Subtle natural catenary sag.
    Tris budget: 48 tris (4 sections x 6 radial segments = 24 quads).
    Entirely Slot 1: M_Rubber (EPDM matte black rubber).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 6

    # 5 spline points in local space (from local Z=0 to local Z=-0.345)
    spline_pts = [
        Vector(( 0.0000,  0.0000,  0.000)),
        Vector(( 0.0055, -0.0035, -0.085)),
        Vector(( 0.0120, -0.0070, -0.170)),
        Vector(( 0.0090, -0.0050, -0.260)),
        Vector(( 0.0030, -0.0015, -0.345))
    ]

    r_cable = 0.0052  # 10.4mm industrial cable jacket

    n_pts = len(spline_pts)
    rings = []

    for i in range(n_pts):
        p = spline_pts[i]
        if i == 0:
            tangent = (spline_pts[1] - p).normalized()
        elif i == n_pts - 1:
            tangent = (p - spline_pts[i - 1]).normalized()
        else:
            tangent = (spline_pts[i + 1] - spline_pts[i - 1]).normalized()

        arb = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.8 else Vector((0.0, 1.0, 0.0))
        norm = tangent.cross(arb).normalized()
        binorm = tangent.cross(norm).normalized()

        ring = []
        for j in range(n_radial):
            ang = j * (2.0 * math.pi / n_radial)
            off = norm * math.cos(ang) + binorm * math.sin(ang)
            ring.append(bm.verts.new(p + off * r_cable))
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    # Map UVs cleanly inside Region 2 (U: [0.02..0.48], V: [0.02..0.48])
    for i in range(n_pts - 1):
        v0 = 0.02 + (i / float(n_pts - 1)) * 0.44
        v1 = 0.02 + ((i + 1) / float(n_pts - 1)) * 0.44
        for j in range(n_radial):
            jn = (j + 1) % n_radial
            va = rings[i][j]
            vb = rings[i][jn]
            vc = rings[i + 1][jn]
            vd = rings[i + 1][j]
            f = bm.faces.new((va, vb, vc, vd))
            f.smooth = True
            f.material_index = 1 # Slot 1: M_Rubber
            u0 = 0.02 + (j / float(n_radial)) * 0.44
            u1 = 0.02 + ((j + 1) / float(n_radial)) * 0.44
            f.loops[0][uv_layer].uv = (u0, v0)
            f.loops[1][uv_layer].uv = (u1, v0)
            f.loops[2][uv_layer].uv = (u1, v1)
            f.loops[3][uv_layer].uv = (u0, v1)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Cable_Segment")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    return mesh, spline_pts[-1]

def build_connector(mats, end_pt_local):
    """
    Kablo Başlığı (Connector)
    Industrial BNC terminal assembly attached to the end of Cable_Segment.
    Molded rubber strain relief boot (Slot 1 M_Rubber) + polished nickel bayonet locking ring (Slot 0 M_Metal).
    Tris budget: 54 tris.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_seg = 8

    cx, cy, cz = end_pt_local.x, end_pt_local.y, end_pt_local.z

    # 4 profile levels (3 quad rings)
    # 1. Rubber boot top (r=0.0062, z=cz) -> Slot 1 M_Rubber
    # 2. Rubber boot base (r=0.0078, z=cz - 0.016) -> Slot 1 M_Rubber
    # 3. Metal bayonet collar (r=0.0086, z=cz - 0.036) -> Slot 0 M_Metal
    # 4. Metal connector tip (r=0.0068, z=cz - 0.046) -> Slot 0 M_Metal

    z_levels = [
        (cz,          0.0062, 1, UV_BOOT),      # boot top (Slot 1 M_Rubber)
        (cz - 0.016,  0.0078, 1, UV_BOOT),      # boot base (Slot 1 M_Rubber)
        (cz - 0.036,  0.0086, 0, UV_POLISHED),  # metal collar (Slot 0 M_Metal)
        (cz - 0.046,  0.0068, 0, UV_HARDWARE)   # connector tip (Slot 0 M_Metal)
    ]

    rings = []
    for z_pos, radius, mat_idx, uv_c in z_levels:
        ring = []
        for s in range(n_seg):
            ang = s * (2.0 * math.pi / n_seg)
            ring.append(bm.verts.new((cx + math.cos(ang) * radius, cy + math.sin(ang) * radius, z_pos)))
        rings.append((ring, mat_idx, uv_c))

    bm.verts.ensure_lookup_table()

    for i in range(len(z_levels) - 1):
        ring_a, mat_a, uv_a = rings[i]
        ring_b, _, _ = rings[i + 1]
        for s in range(n_seg):
            sn = (s + 1) % n_seg
            f = bm.faces.new((ring_a[s], ring_a[sn], ring_b[sn], ring_b[s]))
            f.smooth = True
            f.material_index = mat_a
            for l in f.loops: l[uv_layer].uv = uv_a

    # Front cap face (center pin orifice) -> Slot 0 M_Metal
    last_ring, _, _ = rings[-1]
    f_cap = bm.faces.new(reversed(last_ring))
    f_cap.smooth = False
    f_cap.material_index = 0
    for l in f_cap.loops: l[uv_layer].uv = UV_HARDWARE

    bm.normal_update()
    mesh = bpy.data.meshes.new("Connector")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def build_asset(export_dir):
    clear_scene()
    setup_units()

    mats = create_materials(export_dir)

    coll = bpy.data.collections.new("SEC_Ceiling_Cable_Drop_Coll")
    bpy.context.scene.collection.children.link(coll)

    # 1. Root Empty at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Ceiling_Cable_Drop", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.10
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)

    # 2. Ceiling_Rosette (child of root)
    mesh_rosette = build_ceiling_rosette(mats)
    obj_rosette = bpy.data.objects.new("Ceiling_Rosette", mesh_rosette)
    obj_rosette.parent = root
    coll.objects.link(obj_rosette)

    # 3. Drop_Pipe (child of root)
    mesh_pipe = build_drop_pipe(mats)
    obj_pipe = bpy.data.objects.new("Drop_Pipe", mesh_pipe)
    obj_pipe.parent = root
    coll.objects.link(obj_pipe)

    # 4. Cable_Pivot Empty at exit point (0.0, 0.0, -0.075)
    # Child of root, local X/Z rotation limits ±20°
    pivot_loc = Vector((0.0, 0.0, -0.075))
    cable_pivot = bpy.data.objects.new("Cable_Pivot", None)
    cable_pivot.empty_display_type = 'SPHERE'
    cable_pivot.empty_display_size = 0.02
    cable_pivot.location = pivot_loc
    cable_pivot.parent = root
    coll.objects.link(cable_pivot)

    # Add Limit Rotation constraint to Cable_Pivot
    con_rot = cable_pivot.constraints.new('LIMIT_ROTATION')
    con_rot.use_limit_x = True
    con_rot.min_x = math.radians(-20.0)
    con_rot.max_x = math.radians(20.0)
    con_rot.use_limit_z = True
    con_rot.min_z = math.radians(-20.0)
    con_rot.max_z = math.radians(20.0)
    con_rot.use_limit_y = True
    con_rot.min_y = 0.0
    con_rot.max_y = 0.0
    con_rot.owner_space = 'LOCAL'

    cable_pivot["rot_axis"] = "XZ"
    cable_pivot["min_angle_deg"] = -20.0
    cable_pivot["max_angle_deg"] = 20.0
    cable_pivot["part_type"] = "CABLE_PIVOT"

    # 5. Cable_Segment (child of Cable_Pivot)
    mesh_cable, end_pt_local = build_cable_segment(mats, pivot_loc)
    obj_cable = bpy.data.objects.new("Cable_Segment", mesh_cable)
    obj_cable.parent = cable_pivot
    coll.objects.link(obj_cable)

    # 6. Connector (child of Cable_Segment)
    mesh_conn = build_connector(mats, end_pt_local)
    obj_conn = bpy.data.objects.new("Connector", mesh_conn)
    obj_conn.parent = obj_cable
    coll.objects.link(obj_conn)

    # Smooth shading and edge split modifiers
    all_meshes = [obj_rosette, obj_pipe, obj_cable, obj_conn]
    for child in all_meshes:
        for p in child.data.polygons:
            p.use_smooth = True
        mod = child.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
        mod.split_angle = math.radians(35)

    # Count tris
    total_tris = 0
    for child in all_meshes:
        bm = bmesh.new()
        bm.from_mesh(child.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        m_tris = len(bm.faces)
        total_tris += m_tris
        bm.free()
        print(f"       -> {child.name}: {m_tris} tris")

    print(f"\n[INFO] Total Triangles for SEC_Ceiling_Cable_Drop: {total_tris}")
    assert total_tris <= 260, f"FAIL: Triangle count {total_tris} exceeds budget of 260!"

    # Material preview settings
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        space.shading.color_type = 'TEXTURE'
                        space.region_3d.view_distance = 0.60
                        space.region_3d.view_location = (0.0, 0.0, -0.22)

    # Save .blend
    bpy.ops.file.pack_all()
    blend_path = os.path.join(export_dir, "SEC_Ceiling_Cable_Drop.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Remove automatic .blend1 backup if exists
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)

    # Export FBX
    fbx_path = os.path.join(export_dir, "SEC_Ceiling_Cable_Drop.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    cable_pivot.select_set(True)
    for m in all_meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = root

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
        use_custom_props=True,
        path_mode='AUTO'
    )
    print(f"[OK] Exported FBX: {fbx_path}")

    # Headless Re-Import QA Test
    test_reimport(fbx_path, total_tris, export_dir)

def test_reimport(fbx_path, original_tris, export_dir):
    print("\n--- RUNNING RE-IMPORT QA VERIFICATION (Asset 74) ---")
    clear_scene()
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    reimported_tris = 0
    reimported_meshes = 0
    reimported_empties = 0
    materials_found = set()
    mesh_names = set()
    empty_names = set()

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            reimported_meshes += 1
            mesh_names.add(obj.name)
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            reimported_tris += len(bm.faces)
            bm.free()
            for mat in obj.data.materials:
                if mat: materials_found.add(mat.name)
        elif obj.type == 'EMPTY':
            reimported_empties += 1
            empty_names.add(obj.name)

    print(f"Re-import counts: Meshes={reimported_meshes}, Empties={reimported_empties}, Tris={reimported_tris}")
    print(f"Meshes: {mesh_names}")
    print(f"Empties: {empty_names}")
    print(f"Materials: {materials_found}")

    expected_meshes = {"Ceiling_Rosette", "Drop_Pipe", "Cable_Segment", "Connector"}
    expected_empties = {"SEC_Ceiling_Cable_Drop", "Cable_Pivot"}
    expected_mats = {"M_Metal", "M_Rubber"}

    pass_meshes = expected_meshes.issubset(mesh_names)
    pass_empties = expected_empties.issubset(empty_names)
    pass_tris = (reimported_tris <= 260) and (reimported_tris == original_tris)
    pass_mats = expected_mats.issubset(materials_found)

    # Check hierarchy
    root = bpy.data.objects.get("SEC_Ceiling_Cable_Drop")
    rosette = bpy.data.objects.get("Ceiling_Rosette")
    pipe = bpy.data.objects.get("Drop_Pipe")
    pivot = bpy.data.objects.get("Cable_Pivot")
    cable = bpy.data.objects.get("Cable_Segment")
    conn = bpy.data.objects.get("Connector")

    pass_hier = (
        root is not None and
        rosette and rosette.parent == root and
        pipe and pipe.parent == root and
        pivot and pivot.parent == root and
        cable and cable.parent == pivot and
        conn and conn.parent == cable
    )

    all_passed = pass_meshes and pass_empties and pass_tris and pass_mats and pass_hier
    status = "SUCCESS" if all_passed else "FAILED"

    print(f"Hierarchy verification: {'PASS' if pass_hier else 'FAIL'}")
    print(f"Tris budget check (<= 260): {'PASS' if pass_tris else 'FAIL'} ({reimported_tris} tris)")
    print(f"Materials check: {'PASS' if pass_mats else 'FAIL'}")
    print(f"[QA] FINAL STATUS: {status}")

    manifest = {
        "SEC_Ceiling_Cable_Drop": {
            "asset_name": "SEC_Ceiling_Cable_Drop",
            "fbx_path": "exports/SEC_Ceiling_Cable_Drop.fbx",
            "blend_path": "exports/SEC_Ceiling_Cable_Drop.blend",
            "tris_count": reimported_tris,
            "mesh_count": reimported_meshes,
            "empty_count": reimported_empties,
            "materials": sorted(list(materials_found)),
            "status": status
        }
    }

    manifest_path = os.path.join(export_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Manifest written to: {manifest_path}")

    assert all_passed, "QA checks failed!"

if __name__ == "__main__":
    out_dir = r"C:\Users\Burak\Desktop\Security_CCTV\74. SEC_Ceiling_Cable_Drop\exports"
    build_asset(out_dir)
