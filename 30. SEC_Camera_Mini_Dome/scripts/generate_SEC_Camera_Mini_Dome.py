import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Euler

def reset_scene():
    """Clear scene completely."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Collection")
    bpy.context.scene.collection.children.link(col)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0

def create_materials(atlas_path):
    """
    Slot 0: M_Security_Atlas
    Slot 1: M_Transparent (Polycarbonate dome cover)
    Slot 2: M_Lens_Glass (Multi-coated optical lens glass)
    """
    # 0. M_Security_Atlas
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes = mat_atlas.node_tree.nodes
    links = mat_atlas.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Metallic'].default_value = 0.15

    if os.path.exists(atlas_path):
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(atlas_path)
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.88, 0.90, 0.92, 1.0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    # 1. M_Transparent (Optical polycarbonate transparent protective dome)
    mat_trans = bpy.data.materials.new("M_Transparent")
    mat_trans.use_nodes = True
    tnodes = mat_trans.node_tree.nodes
    tlinks = mat_trans.node_tree.links
    tnodes.clear()

    t_out = tnodes.new("ShaderNodeOutputMaterial")
    t_bsdf = tnodes.new("ShaderNodeBsdfPrincipled")
    t_bsdf.inputs['Base Color'].default_value = (0.90, 0.94, 0.98, 1.0)
    t_bsdf.inputs['Alpha'].default_value = 0.35
    t_bsdf.inputs['Roughness'].default_value = 0.06
    t_bsdf.inputs['Metallic'].default_value = 0.02
    if 'Specular IOR Level' in t_bsdf.inputs:
        t_bsdf.inputs['Specular IOR Level'].default_value = 0.90
    if 'Transmission Weight' in t_bsdf.inputs:
        t_bsdf.inputs['Transmission Weight'].default_value = 0.50
    elif 'Transmission' in t_bsdf.inputs:
        t_bsdf.inputs['Transmission'].default_value = 0.50
    if 'IOR' in t_bsdf.inputs:
        t_bsdf.inputs['IOR'].default_value = 1.58
    tlinks.new(t_bsdf.outputs['BSDF'], t_out.inputs['Surface'])

    if hasattr(mat_trans, 'blend_method'):
        mat_trans.blend_method = 'BLEND'

    # 2. M_Lens_Glass (Multi-coated optical camera lens glass)
    mat_glass = bpy.data.materials.new("M_Lens_Glass")
    mat_glass.use_nodes = True
    gnodes = mat_glass.node_tree.nodes
    glinks = mat_glass.node_tree.links
    gnodes.clear()

    g_out = gnodes.new("ShaderNodeOutputMaterial")
    g_bsdf = gnodes.new("ShaderNodeBsdfPrincipled")
    if os.path.exists(atlas_path):
        gtex = gnodes.new("ShaderNodeTexImage")
        gtex.image = bpy.data.images.load(atlas_path)
        glinks.new(gtex.outputs['Color'], g_bsdf.inputs['Base Color'])
    else:
        g_bsdf.inputs['Base Color'].default_value = (0.06, 0.12, 0.18, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.04
    g_bsdf.inputs['Metallic'].default_value = 0.08
    if 'Specular IOR Level' in g_bsdf.inputs:
        g_bsdf.inputs['Specular IOR Level'].default_value = 1.0
    if 'Transmission Weight' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission Weight'].default_value = 0.35
    elif 'Transmission' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission'].default_value = 0.35
    if 'IOR' in g_bsdf.inputs:
        g_bsdf.inputs['IOR'].default_value = 1.54
    glinks.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    return [mat_atlas, mat_trans, mat_glass]

def build_mount_base(mats):
    """
    Mount_Base: Compact ceiling mounting disc flush at Z=0.
    Diameter: 100mm (r=0.050m), height: 16mm (Z=0.000 to -0.016).
    14-radial smooth contour with sloped bevel, Torx screws, and recessed dome seat.
    Slot 0: M_Security_Atlas.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 14

    # Stations along -Z:
    # 0: Z= 0.000, r=0.050 (ceiling contact rim)
    # 1: Z=-0.006, r=0.050 (vertical rim)
    # 2: Z=-0.010, r=0.046 (chamfer bevel)
    # 3: Z=-0.016, r=0.035 (dome seating rim)
    stations = [
        ( 0.000, 0.050),
        (-0.006, 0.050),
        (-0.010, 0.046),
        (-0.016, 0.035)
    ]
    rings = []
    for z_pos, r_rad in stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        rings.append(ring)

    v_center = bm.verts.new(Vector((0.0, 0.0, -0.016)))
    bm.verts.ensure_lookup_table()

    # Quads between consecutive rings (pointing outward into -Z)
    for s in range(len(stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True
            f.material_index = 0

            ang0 = i * (2.0 * math.pi / n_radial)
            ang1 = (i + 1) * (2.0 * math.pi / n_radial)
            cu, cv = 0.25, 0.75 # Quadrant 1 in 1024x1024 atlas

            if s == 0:
                # Vertical rim
                u0 = 0.02 + (i / float(n_radial)) * 0.45
                u1 = 0.02 + ((i + 1) / float(n_radial)) * 0.45
                for loop in f.loops:
                    v_val = 0.95 if loop.vert in (va, vb) else 0.92
                    loop[uv_layer].uv = (u0 if loop.vert in (va, vd) else u1, v_val)
            elif s == 1:
                # Chamfer rim
                for loop in f.loops: loop[uv_layer].uv = (cu + 0.22 * math.cos(ang0), cv + 0.22 * math.sin(ang0))
            else:
                # Sloped face with Torx screws and brand
                for loop in f.loops:
                    if loop.vert == va: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang0), cv + 0.21 * math.sin(ang0))
                    elif loop.vert == vb: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang1), cv + 0.21 * math.sin(ang1))
                    elif loop.vert == vc: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang1), cv + 0.12 * math.sin(ang1))
                    elif loop.vert == vd: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang0), cv + 0.12 * math.sin(ang0))

    # Center floor (pointing into -Z)
    r_floor = rings[-1]
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((r_floor[i], v_center, r_floor[i_next]))
        f.smooth = False
        f.material_index = 0
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        cu, cv = 0.25, 0.75
        for loop in f.loops:
            if loop.vert == r_floor[i]: loop[uv_layer].uv = (cu + 0.06 * math.cos(ang0), cv + 0.06 * math.sin(ang0))
            elif loop.vert == r_floor[i_next]: loop[uv_layer].uv = (cu + 0.06 * math.cos(ang1), cv + 0.06 * math.sin(ang1))
            elif loop.vert == v_center: loop[uv_layer].uv = (cu, cv)

    # 3D Countersunk Torx Security Screw Heads on sloped bevel
    for s_idx in range(3):
        sang = s_idx * (2.0 * math.pi / 3.0) + math.pi / 6.0
        r_screw = 0.0415
        z_screw = -0.0125
        pos = Vector((math.cos(sang) * r_screw, math.sin(sang) * r_screw, z_screw))

        u_r = Vector((math.cos(sang), math.sin(sang), 0.0))
        u_z = Vector((0.0, 0.0, 1.0))
        n_vec = (0.479 * u_r - 0.878 * u_z).normalized()
        t1_vec = Vector((-math.sin(sang), math.cos(sang), 0.0))
        t2_vec = n_vec.cross(t1_vec).normalized()

        r_head = 0.0028
        h_protrude = 0.0004
        h_recess = 0.0005
        n_screw_sides = 5

        cx_tex, cy_tex = 256.0, 256.0
        scx = cx_tex + 195.0 * math.cos(sang)
        scy = cy_tex + 195.0 * math.sin(sang)
        u_c = scx / 1024.0
        v_c = (1024.0 - scy) / 1024.0

        base_ring = []
        rim_ring = []
        for k in range(n_screw_sides):
            phi = k * (2.0 * math.pi / n_screw_sides)
            offset = r_head * (math.cos(phi) * t1_vec + math.sin(phi) * t2_vec)
            v_b = bm.verts.new(pos + offset)
            v_r = bm.verts.new(pos + offset + h_protrude * n_vec)
            base_ring.append(v_b)
            rim_ring.append(v_r)

        v_recess = bm.verts.new(pos + (h_protrude - h_recess) * n_vec)

        # Skirt quads
        for k in range(n_screw_sides):
            k_next = (k + 1) % n_screw_sides
            f_skirt = bm.faces.new((base_ring[k], base_ring[k_next], rim_ring[k_next], rim_ring[k]))
            f_skirt.smooth = False
            f_skirt.material_index = 0
            for loop in f_skirt.loops:
                loop[uv_layer].uv = (u_c, v_c)

        # Recessed Torx drive socket faces
        for k in range(n_screw_sides):
            k_next = (k + 1) % n_screw_sides
            phi0 = k * (2.0 * math.pi / n_screw_sides)
            phi1 = (k + 1) * (2.0 * math.pi / n_screw_sides)
            f_socket = bm.faces.new((rim_ring[k], rim_ring[k_next], v_recess))
            f_socket.smooth = False
            f_socket.material_index = 0
            for loop in f_socket.loops:
                if loop.vert == rim_ring[k]: loop[uv_layer].uv = (u_c + 0.012 * math.cos(phi0), v_c + 0.012 * math.sin(phi0))
                elif loop.vert == rim_ring[k_next]: loop[uv_layer].uv = (u_c + 0.012 * math.cos(phi1), v_c + 0.012 * math.sin(phi1))
                elif loop.vert == v_recess: loop[uv_layer].uv = (u_c, v_c)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Mount_Base")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Mount_Base", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_dome_cover(mats):
    """
    Dome_Cover: Transparent hemispherical polycarbonate protective cover.
    Base seating rim at Z=-0.015 (radius 0.035m), apex at Z=-0.038 (height 23mm).
    14 radial segments, 2 quad rings + 1 apex fan.
    Slot 1: M_Transparent.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 14

    dome_stations = [
        (-0.015, 0.035),
        (-0.026, 0.029),
        (-0.034, 0.018)
    ]
    rings = []
    for z_pos, r_rad in dome_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        rings.append(ring)

    v_apex = bm.verts.new(Vector((0.0, 0.0, -0.038)))
    bm.verts.ensure_lookup_table()

    # Quads between latitude rings (pointing into -Z)
    for s in range(len(dome_stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True
            f.material_index = 1 # Slot 1: M_Transparent
            for loop in f.loops: loop[uv_layer].uv = (0.25, 0.25)

    # Apex fan (pointing into -Z)
    r_top = rings[-1]
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((r_top[i], v_apex, r_top[i_next]))
        f.smooth = True
        f.material_index = 1 # Slot 1: M_Transparent
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.25)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Dome_Cover")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.material_index = 1

    obj = bpy.data.objects.new("Dome_Cover", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_camera_module(mats):
    """
    Camera_Module: Internal directional gimbal eyeball sphere inside dome cover.
    Origin at Camera_Module_Pivot: (0.0, 0.0, -0.020).
    Local coordinates:
      Eyeball radius 0.022m, extending into -Z to aperture at Z=-0.014.
    Slot 0: M_Security_Atlas.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 10

    # Spherical stations along local Z:
    # 0: Z= 0.010, r=0.016
    # 1: Z= 0.000, r=0.022 (equator)
    # 2: Z=-0.010, r=0.018
    # 3: Z=-0.014, r=0.011 (front lens aperture)
    mod_stations = [
        ( 0.010, 0.016),
        ( 0.000, 0.022),
        (-0.010, 0.018),
        (-0.014, 0.011)
    ]
    rings = []
    for z_pos, r_rad in mod_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        rings.append(ring)
    bm.verts.ensure_lookup_table()

    # Back cap at station 0
    f_back = bm.faces.new(reversed(rings[0]))
    f_back.smooth = False; f_back.material_index = 0
    for loop in f_back.loops: loop[uv_layer].uv = (0.75, 0.25)

    # Quads along eyeball sphere
    for s in range(len(mod_stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True
            f.material_index = 0

            # Map to Quadrant 2 in 1024x1024 atlas (dark graphite gimbal eyeball)
            ang0 = i * (2.0 * math.pi / n_radial)
            ang1 = (i + 1) * (2.0 * math.pi / n_radial)
            cu, cv = 0.75, 0.75
            rad_uv = 0.18 - s * 0.05
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (cu + rad_uv * math.cos(ang0), cv + rad_uv * math.sin(ang0))
                elif loop.vert == vb: loop[uv_layer].uv = (cu + rad_uv * math.cos(ang1), cv + rad_uv * math.sin(ang1))
                elif loop.vert == vc: loop[uv_layer].uv = (cu + (rad_uv - 0.04) * math.cos(ang1), cv + (rad_uv - 0.04) * math.sin(ang1))
                elif loop.vert == vd: loop[uv_layer].uv = (cu + (rad_uv - 0.04) * math.cos(ang0), cv + (rad_uv - 0.04) * math.sin(ang0))

    bm.normal_update()
    mesh = bpy.data.meshes.new("Camera_Module")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Camera_Module", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_glass(mats):
    """
    Lens_Glass: Optical lens element at module aperture center (Z=-0.014 to -0.016, r=0.011m).
    10-radial smooth convex optical dome pointing into -Z.
    Slot 2: M_Lens_Glass.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 10
    r_lens = 0.011

    v_ring = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        vx = math.cos(ang) * r_lens
        vy = math.sin(ang) * r_lens
        v_ring.append(bm.verts.new(Vector((vx, vy, -0.014))))

    v_apex = bm.verts.new(Vector((0.0, 0.0, -0.016)))
    bm.verts.ensure_lookup_table()

    cu, cv = 0.75, 0.25 # Quadrant 4 in 1024x1024 atlas (optical lens multi-coated reflections)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_ring[i], v_apex, v_ring[i_next]))
        f.smooth = True
        f.material_index = 2 # Slot 2: M_Lens_Glass
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        for loop in f.loops:
            if loop.vert == v_ring[i]: loop[uv_layer].uv = (cu + 0.07 * math.cos(ang0), cv + 0.07 * math.sin(ang0))
            elif loop.vert == v_ring[i_next]: loop[uv_layer].uv = (cu + 0.07 * math.cos(ang1), cv + 0.07 * math.sin(ang1))
            elif loop.vert == v_apex: loop[uv_layer].uv = (cu, cv)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Lens_Glass")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.material_index = 2

    obj = bpy.data.objects.new("Lens_Glass", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_asset():
    """Build full SEC_Camera_Mini_Dome hierarchy."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mats = create_materials(atlas_path)

    # 1. Root Empty: SEC_Camera_Mini_Dome at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Camera_Mini_Dome", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 2. Mount_Base (Child of Root)
    base = build_mount_base(mats)
    base.parent = root

    # 3. Dome_Cover (Child of Mount_Base)
    dome = build_dome_cover(mats)
    dome.parent = base

    # 4. Camera_Module_Pivot (Empty at (0, 0, -0.020), Child of Mount_Base)
    cam_pivot = bpy.data.objects.new("Camera_Module_Pivot", None)
    cam_pivot.empty_display_type = 'ARROWS'
    cam_pivot.empty_display_size = 0.03
    cam_pivot.location = (0.0, 0.0, -0.020)
    bpy.context.collection.objects.link(cam_pivot)
    cam_pivot.parent = base
    cam_pivot["limit_rot_x_min"] = -25.0
    cam_pivot["limit_rot_x_max"] = 25.0

    # 5. Camera_Module (Child of Camera_Module_Pivot, origin at Camera_Module_Pivot)
    module = build_camera_module(mats)
    module.parent = cam_pivot

    # 6. Lens_Glass (Child of Camera_Module)
    lens = build_lens_glass(mats)
    lens.parent = module

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Camera_Mini_Dome.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Mini_Dome.fbx")
    export_fbx(root, [base, dome, module, lens], cam_pivot, fbx_path)

    # QA Verification
    run_qa_verification(fbx_path, blend_path, exports_dir)

def export_fbx(root, meshes, cam_pivot, fbx_path):
    """Export asset hierarchy to FBX with Unity-compatible orientation."""
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    cam_pivot.select_set(True)
    for m in meshes:
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
        path_mode='AUTO'
    )
    print(f"[OK] Exported FBX: {fbx_path}")

def run_qa_verification(fbx_path, blend_path, exports_dir):
    """Import FBX into clean scene and verify tris, hierarchy, materials, UVs."""
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 30) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Camera_Mini_Dome")
    assert root is not None, "FAIL: Root object 'SEC_Camera_Mini_Dome' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    base = bpy.data.objects.get("Mount_Base")
    assert base is not None, "FAIL: Mount_Base missing!"
    assert base.parent == root, "FAIL: Mount_Base parent != root!"

    cam_pivot = bpy.data.objects.get("Camera_Module_Pivot")
    assert cam_pivot is not None, "FAIL: Camera_Module_Pivot missing!"
    assert cam_pivot.parent == base, "FAIL: Camera_Module_Pivot parent != base!"
    assert cam_pivot.type == 'EMPTY', f"FAIL: Camera_Module_Pivot is type {cam_pivot.type}, expected EMPTY!"

    expected_meshes = {
        "Mount_Base",
        "Dome_Cover",
        "Camera_Module",
        "Lens_Glass"
    }

    found_meshes = set()
    total_tris = 0

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            found_meshes.add(obj.name)
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            tris = len(bm.faces)
            total_tris += tris
            print(f"       -> {obj.name}: {tris} tris")

            assert len(obj.data.uv_layers) > 0, f"FAIL: {obj.name} missing UV layer!"
            slot_names = [slot.material.name for slot in obj.material_slots if slot.material]
            print(f"          Materials: {slot_names}")
            assert len(slot_names) > 0, f"FAIL: {obj.name} has no materials assigned!"
            bm.free()

    assert expected_meshes == found_meshes, f"FAIL: Missing meshes! Expected: {expected_meshes}, Found: {found_meshes}"

    # Verify parent relationships
    dome = bpy.data.objects.get("Dome_Cover")
    module = bpy.data.objects.get("Camera_Module")
    lens = bpy.data.objects.get("Lens_Glass")

    assert dome.parent == base, "FAIL: Dome_Cover parent != base!"
    assert module.parent == cam_pivot, "FAIL: Camera_Module parent != cam_pivot!"
    assert lens.parent == module, "FAIL: Lens_Glass parent != module!"

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 300, f"FAIL: Total triangles {total_tris} exceeds 300 budget!"
    print("[PASS] Triangle count verified strictly (<= 300)!")
    print("[PASS] Full parent-child hierarchy strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Camera_Mini_Dome"] = {
        "asset_name": "SEC_Camera_Mini_Dome",
        "fbx_path": "exports/SEC_Camera_Mini_Dome.fbx",
        "blend_path": "exports/SEC_Camera_Mini_Dome.blend",
        "tris_count": total_tris,
        "mesh_count": len(found_meshes),
        "empty_count": 2, # root + cam_pivot
        "materials": ["M_Security_Atlas", "M_Transparent", "M_Lens_Glass"],
        "status": "SUCCESS"
    }

    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[OK] Updated manifest: {manifest_path}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")

    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[CLEAN] Removed backup: {os.path.basename(blend1_path)}")

if __name__ == "__main__":
    build_asset()
