import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Euler

def reset_scene():
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
    Slot 1: M_Lens_Glass
    Slot 2: M_Metal
    """
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes = mat_atlas.node_tree.nodes
    links = mat_atlas.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Metallic'].default_value = 0.12

    if os.path.exists(atlas_path):
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(atlas_path)
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.88, 0.90, 0.92, 1.0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

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
        g_bsdf.inputs['Base Color'].default_value = (0.05, 0.08, 0.14, 1.0)
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

    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    mnodes = mat_metal.node_tree.nodes
    mlinks = mat_metal.node_tree.links
    mnodes.clear()

    m_out = mnodes.new("ShaderNodeOutputMaterial")
    m_bsdf = mnodes.new("ShaderNodeBsdfPrincipled")
    m_bsdf.inputs['Base Color'].default_value = (0.75, 0.78, 0.82, 1.0)
    m_bsdf.inputs['Roughness'].default_value = 0.20
    m_bsdf.inputs['Metallic'].default_value = 0.92
    mlinks.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])

    return [mat_atlas, mat_glass, mat_metal]

def build_corner_plate(mats):
    """
    Corner_Plate: Heavy-duty 90-degree inside corner bracket adapter.
    Sits flush into inside corner at (0, 0, 0).
    Convex solid 10-sided profile with dual wall mounting flanges,
    4 3D hex anchor bolts with washers, front mounting pad, and knuckle collar.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # Corner bracket 2D contour in (X, Y) plane:
    # Wall Left is along (-s, +s), Wall Right is along (+s, +s).
    H_half = 0.065 # 130mm bracket height (Z: -0.065 to +0.065)

    p_2d = [
        Vector(( 0.000, 0.000, 0.0)),  # 0: Corner Apex
        Vector((-0.075, 0.075, 0.0)),  # 1: Left Wall Contact Tip
        Vector((-0.082, 0.082, 0.0)),  # 2: Left Wing Flange Outer Lip
        Vector((-0.078, 0.092, 0.0)),  # 3: Left Wing Front Corner
        Vector((-0.042, 0.092, 0.0)),  # 4: Left Wing Inner Step
        Vector((-0.035, 0.080, 0.0)),  # 5: Center Front Mounting Face Left
        Vector(( 0.035, 0.080, 0.0)),  # 6: Center Front Mounting Face Right
        Vector(( 0.042, 0.092, 0.0)),  # 7: Right Wing Inner Step
        Vector(( 0.078, 0.092, 0.0)),  # 8: Right Wing Front Corner
        Vector(( 0.082, 0.082, 0.0)),  # 9: Right Wing Flange Outer Lip
        Vector(( 0.075, 0.075, 0.0))   # 10: Right Wall Contact Tip
    ]

    v_bot = [bm.verts.new(p + Vector((0, 0, -H_half))) for p in p_2d]
    v_top = [bm.verts.new(p + Vector((0, 0,  H_half))) for p in p_2d]

    n_pts = len(p_2d)
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        f = bm.faces.new((v_bot[i], v_bot[i_next], v_top[i_next], v_top[i]))
        f.smooth = False
        f.material_index = 0

        # Clean powder-coat off-white finish for corner bracket
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.68)

    # Top and bottom end caps
    f_top = bm.faces.new(reversed(v_top))
    f_top.smooth = False; f_top.material_index = 0
    for loop in f_top.loops: loop[uv_layer].uv = (0.25, 0.68)

    f_bot = bm.faces.new(v_bot)
    f_bot.smooth = False; f_bot.material_index = 0
    for loop in f_bot.loops: loop[uv_layer].uv = (0.25, 0.68)

    # Center Mounting Collar on front face (X: -0.035 to +0.035, Y=0.080)
    # Raised circular boss: center at (0.0, 0.080, 0.0), normal into +Y
    r_collar = 0.024
    h_collar = 0.005
    n_col = 8
    c_base = []
    c_front = []
    for i in range(n_col):
        ang = i * (2.0 * math.pi / n_col)
        vx = math.cos(ang) * r_collar
        vz = math.sin(ang) * r_collar
        c_base.append(bm.verts.new(Vector((vx, 0.080, vz))))
        c_front.append(bm.verts.new(Vector((vx, 0.080 + h_collar, vz))))

    for i in range(n_col):
        i_next = (i + 1) % n_col
        f = bm.faces.new((c_base[i], c_base[i_next], c_front[i_next], c_front[i]))
        f.smooth = True; f.material_index = 2
        for loop in f.loops: loop[uv_layer].uv = (0.75, 0.60)

    f_cfront = bm.faces.new(c_front)
    f_cfront.smooth = False; f_cfront.material_index = 2
    for loop in f_cfront.loops: loop[uv_layer].uv = (0.75, 0.60)

    # Swivel Knuckle Drum (horizontal cylinder for pivot joint)
    # Center at (0.0, 0.092, 0.0), cylinder axis along X
    r_drum = 0.015
    x_d_half = 0.015
    n_drum = 8
    d_left = []
    d_right = []
    for i in range(n_drum):
        ang = i * (2.0 * math.pi / n_drum)
        dy = math.cos(ang) * r_drum
        dz = math.sin(ang) * r_drum
        d_left.append(bm.verts.new(Vector((-x_d_half, 0.092 + dy, dz))))
        d_right.append(bm.verts.new(Vector(( x_d_half, 0.092 + dy, dz))))

    for i in range(n_drum):
        i_next = (i + 1) % n_drum
        f = bm.faces.new((d_left[i], d_right[i], d_right[i_next], d_left[i_next]))
        f.smooth = True; f.material_index = 0
        u0 = 0.55 + (i / float(n_drum)) * 0.40
        u1 = 0.55 + ((i + 1) / float(n_drum)) * 0.40
        for loop in f.loops:
            v_val = 0.55 if loop.vert in (d_left[i], d_left[i_next]) else 0.51
            loop[uv_layer].uv = (u0 if loop.vert in (d_left[i], d_right[i]) else u1, v_val)

    f_dl = bm.faces.new(reversed(d_left))
    f_dl.smooth = False; f_dl.material_index = 2
    for loop in f_dl.loops: loop[uv_layer].uv = (0.75, 0.60)

    f_dr = bm.faces.new(d_right)
    f_dr.smooth = False; f_dr.material_index = 2
    for loop in f_dr.loops: loop[uv_layer].uv = (0.75, 0.60)

    # M8 Locking Clamp Bolt & Nut on Knuckle
    bolt_c = Vector((x_d_half + 0.003, 0.092, 0.0))
    n_hex = 6
    b_head_k = []
    for h in range(n_hex):
        hang = h * (2.0 * math.pi / n_hex)
        b_head_k.append(bm.verts.new(bolt_c + Vector((0.004, 0.004 * math.cos(hang), 0.004 * math.sin(hang)))))
    f_kbolt = bm.faces.new(b_head_k)
    f_kbolt.smooth = False; f_kbolt.material_index = 2

    # 4 3D Hex Anchor Bolts with Washers (2 on Left Wing, 2 on Right Wing)
    bolt_configs = [
        # Left wing (normal +Y)
        (Vector((-0.060, 0.092, -0.038)), Vector((0, 1, 0))),
        (Vector((-0.060, 0.092,  0.038)), Vector((0, 1, 0))),
        # Right wing (normal +Y)
        (Vector(( 0.060, 0.092, -0.038)), Vector((0, 1, 0))),
        (Vector(( 0.060, 0.092,  0.038)), Vector((0, 1, 0)))
    ]

    for b_pos, b_norm in bolt_configs:
        t1 = Vector((0, 0, 1))
        t2 = b_norm.cross(t1).normalized()

        # Washer
        r_w = 0.0065
        h_w = 0.0020
        w_base = []
        w_top = []
        for h in range(6):
            hang = h * (2.0 * math.pi / 6.0)
            off = r_w * (math.cos(hang) * t2 + math.sin(hang) * t1)
            w_base.append(bm.verts.new(b_pos + off))
            w_top.append(bm.verts.new(b_pos + off + b_norm * h_w))

        for h in range(6):
            h_next = (h + 1) % 6
            f = bm.faces.new((w_base[h], w_base[h_next], w_top[h_next], w_top[h]))
            f.smooth = False; f.material_index = 2
            for loop in f.loops: loop[uv_layer].uv = (0.75, 0.60)

        # Hex Head
        r_b = 0.0045
        h_b = 0.0040
        b_head = []
        for h in range(6):
            hang = h * (2.0 * math.pi / 6.0)
            off = r_b * (math.cos(hang) * t2 + math.sin(hang) * t1)
            b_head.append(bm.verts.new(b_pos + off + b_norm * (h_w + h_b)))

        for h in range(6):
            h_next = (h + 1) % 6
            f = bm.faces.new((w_top[h], w_top[h_next], b_head[h_next], b_head[h]))
            f.smooth = False; f.material_index = 2
            for loop in f.loops: loop[uv_layer].uv = (0.75, 0.60)

        f_bhead = bm.faces.new(b_head)
        f_bhead.smooth = False; f_bhead.material_index = 2
        for loop in f_bhead.loops: loop[uv_layer].uv = (0.75, 0.60)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Corner_Plate")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Corner_Plate", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_camera_housing(mats):
    """
    Camera_Housing: Sleek industrial bullet camera with swivel arm and dual-layer visor.
    Origin at Aim_Pivot (0.0, 0.092, 0.0).
    Local coordinates:
      Knuckle fork extends into +Y to body cradle at Y=0.038.
      14-radial camera body runs from Y=0.020 (rear cap) to Y=0.135 (front bezel).
      Dual-layer visor extends to Y=0.155.
      Rear PG-11 gland from Y=0.020 to 0.006.
      Left flank UV maps branding placard right-side up and natural left-to-right.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # 1. Swivel Knuckle Arm
    fork_stations = [
        (0.000,  0.000, 0.010, 0.012),
        (0.020, -0.008, 0.008, 0.010),
        (0.038, -0.018, 0.007, 0.009)
    ]
    f_rings = []
    for y_pos, z_pos, rx, rz in fork_stations:
        v0 = bm.verts.new(Vector((-rx, y_pos, z_pos - rz)))
        v1 = bm.verts.new(Vector(( rx, y_pos, z_pos - rz)))
        v2 = bm.verts.new(Vector(( rx, y_pos, z_pos + rz)))
        v3 = bm.verts.new(Vector((-rx, y_pos, z_pos + rz)))
        f_rings.append([v0, v1, v2, v3])

    for s in range(len(fork_stations) - 1):
        r_a = f_rings[s]
        r_b = f_rings[s + 1]
        for i in range(4):
            i_next = (i + 1) % 4
            f = bm.faces.new((r_a[i], r_b[i], r_b[i_next], r_a[i_next]))
            f.smooth = False; f.material_index = 0
            for loop in f.loops: loop[uv_layer].uv = (0.75, 0.60)

    # 2. Main Camera Body (14 radial segments)
    n_radial = 14
    body_stations = [
        (0.020, 0.022),
        (0.038, 0.025),
        (0.120, 0.025),
        (0.135, 0.021)
    ]
    b_rings = []
    for y_pos, rad in body_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * rad
            vz = math.sin(ang) * rad
            ring.append(bm.verts.new(Vector((vx, y_pos, vz))))
        b_rings.append(ring)

    # Rear Cap
    f_rear = bm.faces.new(reversed(b_rings[0]))
    f_rear.smooth = False; f_rear.material_index = 0
    for loop in f_rear.loops: loop[uv_layer].uv = (0.75, 0.60)

    # Quads along body
    for s in range(len(body_stations) - 1):
        r_a = b_rings[s]
        r_b = b_rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]; vb = r_a[i_next]; vc = r_b[i_next]; vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True; f.material_index = 0

            # UV Mapping:
            # On the main cylinder (s == 1: Y=0.038 to Y=0.120), map clean side badges on Left Flank and Right Flank
            if s == 1 and i in (6, 7): # Left Flank (centered at ang=180 deg, -X)
                # Front lens (Y=0.120) is at viewer's left -> U=0.55
                # Rear knuckle (Y=0.038) is at viewer's right -> U=0.98
                for loop in f.loops:
                    t_y = (loop.vert.co.y - 0.038) / (0.120 - 0.038)
                    u = 0.55 + (1.0 - t_y) * 0.43
                    v = 0.875 + (loop.vert.co.z / 0.012) * 0.065
                    loop[uv_layer].uv = (u, v)
            elif s == 1 and i in (13, 0): # Right Flank (centered at ang=0 deg, +X)
                # Rear knuckle (Y=0.038) is at viewer's left -> U=0.55
                # Front lens (Y=0.120) is at viewer's right -> U=0.98
                for loop in f.loops:
                    t_y = (loop.vert.co.y - 0.038) / (0.120 - 0.038)
                    u = 0.55 + t_y * 0.43
                    v = 0.875 + (loop.vert.co.z / 0.012) * 0.065
                    loop[uv_layer].uv = (u, v)
            else: # Clean off-white powder-coated metal
                for loop in f.loops:
                    loop[uv_layer].uv = (0.25, 0.68)

    # Front Bezel Ring (recessed into Y=0.131, radius 0.014)
    v_bezel_inner = []
    r_inner = 0.014
    y_inner = 0.131
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        vx = math.cos(ang) * r_inner
        vz = math.sin(ang) * r_inner
        v_bezel_inner.append(bm.verts.new(Vector((vx, y_inner, vz))))

    r_outer_ring = b_rings[-1]
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((r_outer_ring[i], r_outer_ring[i_next], v_bezel_inner[i_next], v_bezel_inner[i]))
        f.smooth = True; f.material_index = 0
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        for loop in f.loops:
            if loop.vert == r_outer_ring[i]: loop[uv_layer].uv = (0.25 + 0.18 * math.cos(ang0), 0.25 + 0.18 * math.sin(ang0))
            elif loop.vert == r_outer_ring[i_next]: loop[uv_layer].uv = (0.25 + 0.18 * math.cos(ang1), 0.25 + 0.18 * math.sin(ang1))
            elif loop.vert == v_bezel_inner[i_next]: loop[uv_layer].uv = (0.25 + 0.12 * math.cos(ang1), 0.25 + 0.12 * math.sin(ang1))
            elif loop.vert == v_bezel_inner[i]: loop[uv_layer].uv = (0.25 + 0.12 * math.cos(ang0), 0.25 + 0.12 * math.sin(ang0))

    # 3. Sunshield Visor (with 3D thickness lip)
    n_visor = 7
    r_v_outer = 0.028
    r_v_inner = 0.0265
    v_vo_rear = []
    v_vo_front = []
    for i in range(n_visor):
        ang = (math.pi / 6.0) + i * (2.0 * math.pi / 3.0) / (n_visor - 1)
        vx = math.cos(ang) * r_v_outer
        vz = math.sin(ang) * r_v_outer
        v_vo_rear.append(bm.verts.new(Vector((vx, 0.038, vz))))
        v_vo_front.append(bm.verts.new(Vector((vx * 1.04, 0.155, vz * 1.04))))

    for i in range(n_visor - 1):
        f = bm.faces.new((v_vo_rear[i], v_vo_front[i], v_vo_front[i + 1], v_vo_rear[i + 1]))
        f.smooth = True; f.material_index = 0
        for loop in f.loops:
            u = 0.25 + (loop.vert.co.x / 0.028) * 0.12
            v = 0.68
            loop[uv_layer].uv = (u, v)

    # 4. Rear PG-11 Cable Gland
    gland_radial = 8
    r_gland = 0.007
    g_base = []
    g_tip = []
    for i in range(gland_radial):
        ang = i * (2.0 * math.pi / gland_radial)
        vx = math.cos(ang) * r_gland
        vz = math.sin(ang) * r_gland
        g_base.append(bm.verts.new(Vector((vx, 0.020, vz))))
        g_tip.append(bm.verts.new(Vector((vx * 0.85, 0.006, vz * 0.85))))

    for i in range(gland_radial):
        i_next = (i + 1) % gland_radial
        f = bm.faces.new((g_base[i], g_tip[i], g_tip[i_next], g_base[i_next]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.75, 0.60)

    f_gtip = bm.faces.new(reversed(g_tip))
    f_gtip.smooth = False; f_gtip.material_index = 0
    for loop in f_gtip.loops: loop[uv_layer].uv = (0.75, 0.60)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Camera_Housing")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Camera_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_glass(mats):
    """
    Lens_Glass: Multi-coated optical camera lens element at front aperture.
    Convex optical dome from Y=0.131 to Y=0.135, radius 0.014.
    Slot 1: M_Lens_Glass.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 14
    r_lens = 0.014
    y_base = 0.131
    y_apex = 0.135

    v_ring = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        vx = math.cos(ang) * r_lens
        vz = math.sin(ang) * r_lens
        v_ring.append(bm.verts.new(Vector((vx, y_base, vz))))

    v_apex = bm.verts.new(Vector((0.0, y_apex, 0.0)))
    bm.verts.ensure_lookup_table()

    cu, cv = 0.75, 0.25 # Quadrant 4 in 1024x1024 atlas
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_ring[i], v_apex, v_ring[i_next]))
        f.smooth = True; f.material_index = 1
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        for loop in f.loops:
            if loop.vert == v_ring[i]: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang0), cv + 0.12 * math.sin(ang0))
            elif loop.vert == v_ring[i_next]: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang1), cv + 0.12 * math.sin(ang1))
            elif loop.vert == v_apex: loop[uv_layer].uv = (cu, cv)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Lens_Glass")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.material_index = 1

    obj = bpy.data.objects.new("Lens_Glass", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_asset():
    """Build full SEC_Camera_Corner_Mount hierarchy and run headless QA."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mats = create_materials(atlas_path)

    # 1. Root Empty: SEC_Camera_Corner_Mount at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Camera_Corner_Mount", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 2. Corner_Plate (Child of Root)
    plate = build_corner_plate(mats)
    plate.parent = root

    # 3. Aim_Pivot (Empty at knuckle center, Child of Corner_Plate)
    aim_pivot = bpy.data.objects.new("Aim_Pivot", None)
    aim_pivot.empty_display_type = 'ARROWS'
    aim_pivot.empty_display_size = 0.03
    aim_pivot.location = (0.0, 0.092, 0.0)
    bpy.context.collection.objects.link(aim_pivot)
    aim_pivot.parent = plate
    aim_pivot["limit_rot_x_min"] = -30.0
    aim_pivot["limit_rot_x_max"] = 30.0
    aim_pivot["limit_rot_z_min"] = -30.0
    aim_pivot["limit_rot_z_max"] = 30.0

    # 4. Camera_Housing (Child of Aim_Pivot, origin at Aim_Pivot)
    housing = build_camera_housing(mats)
    housing.parent = aim_pivot

    # 5. Lens_Glass (Child of Camera_Housing)
    lens = build_lens_glass(mats)
    lens.parent = housing

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Camera_Corner_Mount.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Corner_Mount.fbx")
    export_fbx(root, [plate, housing, lens], aim_pivot, fbx_path)

    # QA Verification
    run_qa_verification(fbx_path, blend_path, exports_dir)

def export_fbx(root, meshes, aim_pivot, fbx_path):
    """Export asset hierarchy to FBX with Unity-compatible orientation."""
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    aim_pivot.select_set(True)
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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 31) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Camera_Corner_Mount")
    assert root is not None, "FAIL: Root object 'SEC_Camera_Corner_Mount' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    plate = bpy.data.objects.get("Corner_Plate")
    assert plate is not None, "FAIL: Corner_Plate missing!"
    assert plate.parent == root, "FAIL: Corner_Plate parent != root!"

    aim_pivot = bpy.data.objects.get("Aim_Pivot")
    assert aim_pivot is not None, "FAIL: Aim_Pivot missing!"
    assert aim_pivot.parent == plate, "FAIL: Aim_Pivot parent != plate!"
    assert aim_pivot.type == 'EMPTY', f"FAIL: Aim_Pivot is type {aim_pivot.type}, expected EMPTY!"

    expected_meshes = {
        "Corner_Plate",
        "Camera_Housing",
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

    housing = bpy.data.objects.get("Camera_Housing")
    lens = bpy.data.objects.get("Lens_Glass")

    assert housing.parent == aim_pivot, "FAIL: Camera_Housing parent != aim_pivot!"
    assert lens.parent == housing, "FAIL: Lens_Glass parent != housing!"

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 450, f"FAIL: Total triangles {total_tris} exceeds 450 budget!"
    print("[PASS] Triangle count verified strictly (<= 450)!")
    print("[PASS] Full parent-child hierarchy strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Camera_Corner_Mount"] = {
        "asset_name": "SEC_Camera_Corner_Mount",
        "fbx_path": "exports/SEC_Camera_Corner_Mount.fbx",
        "blend_path": "exports/SEC_Camera_Corner_Mount.blend",
        "tris_count": total_tris,
        "mesh_count": len(found_meshes),
        "empty_count": 2,
        "materials": ["M_Security_Atlas", "M_Lens_Glass", "M_Metal"],
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
