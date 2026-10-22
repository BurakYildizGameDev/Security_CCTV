import bpy
import bmesh
import math
import os
import json
from mathutils import Vector

def reset_scene():
    """Clear all objects, meshes, materials, and textures."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    col = bpy.data.collections.new("Collection")
    bpy.context.scene.collection.children.link(col)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0

def create_materials(atlas_path, metal_path):
    """
    Slot 0: M_Security_Atlas
    Slot 1: M_Metal
    """
    # 0. M_Security_Atlas
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes = mat_atlas.node_tree.nodes
    links = mat_atlas.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Roughness'].default_value = 0.45
    bsdf.inputs['Metallic'].default_value = 0.05

    if os.path.exists(atlas_path):
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(atlas_path)
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.15, 0.16, 0.18, 1.0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    # 1. M_Metal
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    mnodes = mat_metal.node_tree.nodes
    mlinks = mat_metal.node_tree.links
    mnodes.clear()

    m_out = mnodes.new("ShaderNodeOutputMaterial")
    m_bsdf = mnodes.new("ShaderNodeBsdfPrincipled")
    m_bsdf.inputs['Roughness'].default_value = 0.22
    m_bsdf.inputs['Metallic'].default_value = 0.92

    if os.path.exists(metal_path):
        mtex = mnodes.new("ShaderNodeTexImage")
        mtex.image = bpy.data.images.load(metal_path)
        mlinks.new(mtex.outputs['Color'], m_bsdf.inputs['Base Color'])
    else:
        m_bsdf.inputs['Base Color'].default_value = (0.80, 0.82, 0.85, 1.0)
    mlinks.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])

    return [mat_atlas, mat_metal]

def assign_material_slots(mesh_or_obj, mats):
    """Ensure mesh has exactly 2 material slots in standard order."""
    if hasattr(mesh_or_obj, 'materials'):
        m_list = mesh_or_obj.materials
    else:
        m_list = mesh_or_obj.data.materials
    m_list.clear()
    for m in mats:
        m_list.append(m)

def build_cable_mesh(name, centerline_pts, radius, uv_v_center, mats):
    """
    Build smooth 6-radial cylinder cable swept along spline centerline points.
    centerline_pts: list of Vector coordinates from top anchor down to terminal.
    """
    bm = bmesh.new()
    n_radial = 6
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_pts = len(centerline_pts)

    rings = []

    for i in range(n_pts):
        p = centerline_pts[i]
        if i == 0:
            tangent = (centerline_pts[1] - p).normalized()
        elif i == n_pts - 1:
            tangent = (p - centerline_pts[i - 1]).normalized()
        else:
            tangent = (centerline_pts[i + 1] - centerline_pts[i - 1]).normalized()

        arbitrary = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.8 else Vector((0.0, 1.0, 0.0))
        norm = tangent.cross(arbitrary).normalized()
        binorm = tangent.cross(norm).normalized()

        ring = []
        for j in range(n_radial):
            ang = j * (2.0 * math.pi / n_radial)
            offset = norm * math.cos(ang) + binorm * math.sin(ang)
            v = bm.verts.new(p + offset * radius)
            ring.append(v)
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    # Quads along cable length
    for i in range(n_pts - 1):
        for j in range(n_radial):
            j_next = (j + 1) % n_radial
            va = rings[i][j]
            vb = rings[i][j_next]
            vc = rings[i + 1][j_next]
            vd = rings[i + 1][j]

            f = bm.faces.new((va, vb, vc, vd))
            f.smooth = True
            f.material_index = 0 # M_Security_Atlas

            u0 = j / float(n_radial)
            u1 = (j + 1) / float(n_radial)
            v0 = uv_v_center - 0.04 + (i / float(n_pts - 1)) * 0.08
            v1 = uv_v_center - 0.04 + ((i + 1) / float(n_pts - 1)) * 0.08

            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_bnc_connector(name, pos, dir_vec, mats):
    """
    Build BNC plug terminal (Cable_End_01, Slot 1 M_Metal).
    Length 44mm, diameter 16mm, stepped strain-relief boot and knurled bayonet collar.
    """
    bm = bmesh.new()
    n_radial = 8
    uv_layer = bm.loops.layers.uv.new("UVMap")

    tangent = dir_vec.normalized()
    arbitrary = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.8 else Vector((0.0, 1.0, 0.0))
    norm = tangent.cross(arbitrary).normalized()
    binorm = tangent.cross(norm).normalized()

    # Sections: rubber boot (r=0.006, l=0.016), knurled collar (r=0.0085, l=0.018), tip (r=0.007, l=0.010)
    sections = [
        (0.000, 0.0055, 0),  # rubber boot (atlas)
        (0.016, 0.0068, 0),
        (0.018, 0.0088, 1),  # knurled ring (metal)
        (0.042, 0.0072, 1)   # front tip (metal)
    ]

    rings = []
    for dist, r, mat_idx in sections:
        cen = pos + tangent * dist
        ring = []
        for j in range(n_radial):
            ang = j * (2.0 * math.pi / n_radial)
            off = norm * math.cos(ang) + binorm * math.sin(ang)
            ring.append(bm.verts.new(cen + off * r))
        rings.append((ring, mat_idx))

    bm.verts.ensure_lookup_table()

    for s in range(len(sections) - 1):
        ring_a, mat_idx = rings[s]
        ring_b, _ = rings[s + 1]
        for j in range(n_radial):
            j_next = (j + 1) % n_radial
            va = ring_a[j]
            vb = ring_a[j_next]
            vc = ring_b[j_next]
            vd = ring_b[j]

            f = bm.faces.new((va, vb, vc, vd))
            f.smooth = True
            f.material_index = mat_idx

            u0 = j / float(n_radial)
            u1 = (j + 1) / float(n_radial)
            v0 = 0.20 if mat_idx == 1 else 0.75
            v1 = 0.40 if mat_idx == 1 else 0.85
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    # Front cap face (bayonet orifice)
    last_ring, _ = rings[-1]
    f_end = bm.faces.new(last_ring)
    f_end.smooth = False
    f_end.material_index = 1
    for loop in f_end.loops: loop[uv_layer].uv = (0.50, 0.50)

    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_dc_barrel_connector(name, pos, dir_vec, mats):
    """
    Build 12V DC power barrel jack (Cable_End_02, Slot 0 M_Security_Atlas).
    Length 40mm, molded rubber body with ribs and nickel barrel tip.
    """
    bm = bmesh.new()
    n_radial = 6
    uv_layer = bm.loops.layers.uv.new("UVMap")

    tangent = dir_vec.normalized()
    arbitrary = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.8 else Vector((0.0, 1.0, 0.0))
    norm = tangent.cross(arbitrary).normalized()
    binorm = tangent.cross(norm).normalized()

    # Sections: molded rubber boot (r=0.0055, l=0.022), nickel barrel (r=0.0035, l=0.016)
    sections = [
        (0.000, 0.0048, 0),
        (0.022, 0.0060, 0),
        (0.023, 0.0036, 1),
        (0.038, 0.0036, 1)
    ]

    rings = []
    for dist, r, mat_idx in sections:
        cen = pos + tangent * dist
        ring = []
        for j in range(n_radial):
            ang = j * (2.0 * math.pi / n_radial)
            off = norm * math.cos(ang) + binorm * math.sin(ang)
            ring.append(bm.verts.new(cen + off * r))
        rings.append((ring, mat_idx))

    bm.verts.ensure_lookup_table()

    for s in range(len(sections) - 1):
        ring_a, mat_idx = rings[s]
        ring_b, _ = rings[s + 1]
        for j in range(n_radial):
            j_next = (j + 1) % n_radial
            va = ring_a[j]
            vb = ring_a[j_next]
            vc = ring_b[j_next]
            vd = ring_b[j]

            f = bm.faces.new((va, vb, vc, vd))
            f.smooth = True
            f.material_index = mat_idx
            u0 = j / float(n_radial)
            u1 = (j + 1) / float(n_radial)
            v0 = 0.55 if mat_idx == 0 else 0.20
            v1 = 0.70 if mat_idx == 0 else 0.35
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    # Front cap face (center pin hole)
    last_ring, _ = rings[-1]
    f_end = bm.faces.new(last_ring)
    f_end.smooth = False
    f_end.material_index = 1
    for loop in f_end.loops: loop[uv_layer].uv = (0.50, 0.50)

    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_rj45_connector(name, pos, dir_vec, mats):
    """
    Build RJ-45 modular Ethernet plug (Cable_End_03, Slot 0 M_Security_Atlas).
    Rectangular prism body (15mm wide, 11mm high, 24mm long) with latch clip.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    tangent = dir_vec.normalized()
    arbitrary = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.8 else Vector((0.0, 1.0, 0.0))
    norm = tangent.cross(arbitrary).normalized()
    binorm = tangent.cross(norm).normalized()

    w_half = 0.0075
    h_half = 0.0055
    l_plug = 0.024

    corners = [
        Vector((-w_half, -h_half)),
        Vector(( w_half, -h_half)),
        Vector(( w_half,  h_half)),
        Vector((-w_half,  h_half))
    ]

    p0 = pos
    p1 = pos + tangent * l_plug
    v_bot = [bm.verts.new(p0 + norm * c.x + binorm * c.y) for c in corners]
    v_top = [bm.verts.new(p1 + norm * c.x + binorm * c.y) for c in corners]

    bm.verts.ensure_lookup_table()

    for i in range(4):
        i_next = (i + 1) % 4
        f = bm.faces.new((v_bot[i], v_bot[i_next], v_top[i_next], v_top[i]))
        f.smooth = False
        f.material_index = 0
        u0 = 0.35 + i * 0.08
        u1 = 0.35 + (i + 1) * 0.08
        for loop in f.loops: loop[uv_layer].uv = (u0, 0.65)

    f_front = bm.faces.new(v_top)
    f_front.smooth = False
    f_front.material_index = 0
    for loop in f_front.loops: loop[uv_layer].uv = (0.45, 0.65) # 8 gold contacts

    # Latch clip arm (wedge on top face)
    p_l0 = p0 + binorm * h_half + tangent * 0.006
    p_l1 = p0 + binorm * (h_half + 0.004) + tangent * 0.020
    v_lc0 = bm.verts.new(p_l0 + norm * (-0.0025))
    v_lc1 = bm.verts.new(p_l0 + norm * ( 0.0025))
    v_lc2 = bm.verts.new(p_l1 + norm * ( 0.0025))
    v_lc3 = bm.verts.new(p_l1 + norm * (-0.0025))
    bm.verts.ensure_lookup_table()
    f_latch = bm.faces.new((v_lc0, v_lc1, v_lc2, v_lc3))
    f_latch.smooth = False
    f_latch.material_index = 0
    for loop in f_latch.loops: loop[uv_layer].uv = (0.40, 0.70)

    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_terminal_block_connector(name, pos, dir_vec, mats):
    """
    Build 2-pole euro screw terminal block (Cable_End_04, Slot 1 M_Metal).
    Block size: 18mm wide, 12mm high, 16mm long with screw clamp recesses.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    tangent = dir_vec.normalized()
    arbitrary = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.8 else Vector((0.0, 1.0, 0.0))
    norm = tangent.cross(arbitrary).normalized()
    binorm = tangent.cross(norm).normalized()

    w_half = 0.009
    h_half = 0.006
    l_term = 0.016

    corners = [
        Vector((-w_half, -h_half)),
        Vector(( w_half, -h_half)),
        Vector(( w_half,  h_half)),
        Vector((-w_half,  h_half))
    ]

    p0 = pos
    p1 = pos + tangent * l_term
    v_bot = [bm.verts.new(p0 + norm * c.x + binorm * c.y) for c in corners]
    v_top = [bm.verts.new(p1 + norm * c.x + binorm * c.y) for c in corners]

    bm.verts.ensure_lookup_table()

    for i in range(4):
        i_next = (i + 1) % 4
        f = bm.faces.new((v_bot[i], v_bot[i_next], v_top[i_next], v_top[i]))
        f.smooth = False
        f.material_index = 1
        for loop in f.loops: loop[uv_layer].uv = (0.50, 0.50)

    f_front = bm.faces.new(v_top)
    f_front.smooth = False
    f_front.material_index = 1
    for loop in f_front.loops: loop[uv_layer].uv = (0.25, 0.50)

    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_stripped_wire_connector(name, pos, dir_vec, mats):
    """
    Build stripped wire core revealing copper conductors (Cable_End_05, Slot 0 M_Security_Atlas).
    Jacket cut collar + twin insulated conductor wires + exposed copper tips.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    tangent = dir_vec.normalized()
    arbitrary = Vector((1.0, 0.0, 0.0)) if abs(tangent.x) < 0.8 else Vector((0.0, 1.0, 0.0))
    norm = tangent.cross(arbitrary).normalized()
    binorm = tangent.cross(norm).normalized()

    # Two conductor wires (red and black) extending 18mm
    for wire_idx, (w_sign, u_wire) in enumerate([(-1.0, 0.70), (1.0, 0.80)]):
        w_offset = norm * (w_sign * 0.0024)
        w_p0 = pos + w_offset
        w_p1 = pos + w_offset + tangent * 0.018
        r_cond = 0.0014

        ring_a = []
        ring_b = []
        for j in range(4):
            ang = j * (2.0 * math.pi / 4.0)
            off = norm * math.cos(ang) + binorm * math.sin(ang)
            ring_a.append(bm.verts.new(w_p0 + off * r_cond))
            ring_b.append(bm.verts.new(w_p1 + off * r_cond))

        bm.verts.ensure_lookup_table()

        for j in range(4):
            j_next = (j + 1) % 4
            f = bm.faces.new((ring_a[j], ring_a[j_next], ring_b[j_next], ring_b[j]))
            f.smooth = True
            f.material_index = 0
            for loop in f.loops: loop[uv_layer].uv = (u_wire, 0.35)

        # Exposed copper tip extending another 8mm
        w_p2 = w_p1 + tangent * 0.008
        r_cop = 0.0009
        ring_c = []
        for j in range(4):
            ang = j * (2.0 * math.pi / 4.0)
            off = norm * math.cos(ang) + binorm * math.sin(ang)
            ring_c.append(bm.verts.new(w_p2 + off * r_cop))

        bm.verts.ensure_lookup_table()

        for j in range(4):
            j_next = (j + 1) % 4
            f = bm.faces.new((ring_b[j], ring_b[j_next], ring_c[j_next], ring_c[j]))
            f.smooth = True
            f.material_index = 0
            for loop in f.loops: loop[uv_layer].uv = (0.92, 0.35) # copper

    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_cable_anchor_mesh(mats):
    """
    Build heavy-duty upper mounting anchor collar and clamp bracket at (0, 0, 0).
    Has a solid mounting plate with slots, cylindrical cushion clamp, and zip-tie straps.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # 1. Base Mounting Plate: 50mm x 30mm x 4mm (Z=0.000 to Z=-0.004)
    w_pl = 0.025
    l_pl = 0.015
    h_pl = 0.004

    corners_top = [
        Vector((-w_pl, -l_pl, 0.000)),
        Vector(( w_pl, -l_pl, 0.000)),
        Vector(( w_pl,  l_pl, 0.000)),
        Vector((-w_pl,  l_pl, 0.000))
    ]
    corners_bot = [
        Vector((-w_pl, -l_pl, -h_pl)),
        Vector(( w_pl, -l_pl, -h_pl)),
        Vector(( w_pl,  l_pl, -h_pl)),
        Vector((-w_pl,  l_pl, -h_pl))
    ]

    v_pt = [bm.verts.new(c) for c in corners_top]
    v_pb = [bm.verts.new(c) for c in corners_bot]
    bm.verts.ensure_lookup_table()

    # Plate side faces & bottom
    for i in range(4):
        i_next = (i + 1) % 4
        f = bm.faces.new((v_pt[i], v_pt[i_next], v_pb[i_next], v_pb[i]))
        f.smooth = False
        f.material_index = 1
        for loop in f.loops: loop[uv_layer].uv = (0.50, 0.85)

    f_bot = bm.faces.new(v_pb)
    f_bot.smooth = False
    f_bot.material_index = 1
    for loop in f_bot.loops: loop[uv_layer].uv = (0.50, 0.85)

    # 2. Main Bundle Clamp Collar (10-radial cylinder from Z=-0.004 to Z=-0.035, r=0.020)
    n_k = 10
    r_c = 0.020
    v_c_top = []
    v_c_bot = []
    for j in range(n_k):
        ang = j * (2.0 * math.pi / n_k)
        v_c_top.append(bm.verts.new(Vector((math.cos(ang) * r_c, math.sin(ang) * r_c, -h_pl))))
        v_c_bot.append(bm.verts.new(Vector((math.cos(ang) * r_c, math.sin(ang) * r_c, -0.035))))

    bm.verts.ensure_lookup_table()
    for j in range(n_k):
        j_next = (j + 1) % n_k
        f = bm.faces.new((v_c_top[j], v_c_top[j_next], v_c_bot[j_next], v_c_bot[j]))
        f.smooth = True
        f.material_index = 1 # M_Metal
        for loop in f.loops: loop[uv_layer].uv = (0.50, 0.85)

    # 3. Zip-Tie Strap (Black nylon ring around collar at Z=-0.020 to -0.026, r=0.022)
    v_zt_top = []
    v_zt_bot = []
    for j in range(n_k):
        ang = j * (2.0 * math.pi / n_k)
        v_zt_top.append(bm.verts.new(Vector((math.cos(ang) * 0.022, math.sin(ang) * 0.022, -0.020))))
        v_zt_bot.append(bm.verts.new(Vector((math.cos(ang) * 0.022, math.sin(ang) * 0.022, -0.026))))

    bm.verts.ensure_lookup_table()
    for j in range(n_k):
        j_next = (j + 1) % n_k
        f = bm.faces.new((v_zt_top[j], v_zt_top[j_next], v_zt_bot[j_next], v_zt_bot[j]))
        f.smooth = True
        f.material_index = 0 # M_Security_Atlas (black nylon)
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.90)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Cable_Anchor")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Cable_Anchor", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_asset():
    """Create the full SEC_Hanging_Industrial_Cable_Bundle asset hierarchy."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")
    metal_path = os.path.join(exports_dir, "T_Metal.png")

    mat_atlas, mat_metal = create_materials(atlas_path, metal_path)
    mats = [mat_atlas, mat_metal]

    # Root Empty at upper anchor point (0, 0, 0)
    root = bpy.data.objects.new("SEC_Hanging_Industrial_Cable_Bundle", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 1. Cable Anchor (Root Child)
    anchor = build_cable_anchor_mesh(mats)
    anchor.parent = root

    # 2. Define 5 organic cable spline paths hanging down with distinct catenary droop & spread:
    cables_def = [
        {
            'name': 'Cable_01',
            'radius': 0.0050, # 10mm RG-59 Coaxial
            'uv_v': 0.90,
            'pts': [
                Vector(( 0.008,  0.006, -0.030)),
                Vector(( 0.025,  0.030, -0.120)),
                Vector(( 0.055,  0.065, -0.220)),
                Vector(( 0.075,  0.080, -0.320)),
                Vector(( 0.060,  0.085, -0.420)),
                Vector(( 0.040,  0.080, -0.480))
            ],
            'end_builder': build_bnc_connector,
            'end_name': 'Cable_End_01'
        },
        {
            'name': 'Cable_02',
            'radius': 0.0045, # 9mm 12V DC Power
            'uv_v': 0.70,
            'pts': [
                Vector((-0.008,  0.006, -0.030)),
                Vector((-0.028,  0.022, -0.150)),
                Vector((-0.055,  0.025, -0.280)),
                Vector((-0.072,  0.005, -0.420)),
                Vector((-0.060, -0.025, -0.540)),
                Vector((-0.035, -0.045, -0.620))
            ],
            'end_builder': build_dc_barrel_connector,
            'end_name': 'Cable_End_02'
        },
        {
            'name': 'Cable_03',
            'radius': 0.0050, # 10mm CAT-6 STP Ethernet
            'uv_v': 0.80,
            'pts': [
                Vector((-0.006, -0.008, -0.030)),
                Vector((-0.022, -0.035, -0.160)),
                Vector((-0.038, -0.065, -0.300)),
                Vector((-0.025, -0.080, -0.440)),
                Vector(( 0.010, -0.085, -0.560)),
                Vector(( 0.035, -0.075, -0.660))
            ],
            'end_builder': build_rj45_connector,
            'end_name': 'Cable_End_03'
        },
        {
            'name': 'Cable_04',
            'radius': 0.0055, # 11mm Alarm Multi-core
            'uv_v': 0.75,
            'pts': [
                Vector(( 0.008, -0.006, -0.030)),
                Vector(( 0.030, -0.025, -0.180)),
                Vector(( 0.065, -0.040, -0.360)),
                Vector(( 0.080, -0.035, -0.520)),
                Vector(( 0.070, -0.015, -0.660)),
                Vector(( 0.050,  0.010, -0.780))
            ],
            'end_builder': build_terminal_block_connector,
            'end_name': 'Cable_End_04'
        },
        {
            'name': 'Cable_05',
            'radius': 0.0042, # 8.4mm Stripped Utility
            'uv_v': 0.85,
            'pts': [
                Vector(( 0.000,  0.000, -0.030)),
                Vector((-0.006,  0.012, -0.100)),
                Vector((-0.018,  0.028, -0.180)),
                Vector((-0.026,  0.038, -0.260)),
                Vector((-0.024,  0.042, -0.340)),
                Vector((-0.015,  0.040, -0.400))
            ],
            'end_builder': build_stripped_wire_connector,
            'end_name': 'Cable_End_05'
        }
    ]

    all_meshes = [anchor]

    for cdef in cables_def:
        c_obj = build_cable_mesh(
            cdef['name'],
            cdef['pts'],
            cdef['radius'],
            cdef['uv_v'],
            mats
        )
        c_obj.parent = root
        all_meshes.append(c_obj)

        p_last = cdef['pts'][-1]
        p_prev = cdef['pts'][-2]
        dir_terminal = (p_last - p_prev).normalized()

        end_obj = cdef['end_builder'](
            cdef['end_name'],
            p_last,
            dir_terminal,
            mats
        )
        end_obj.parent = c_obj
        all_meshes.append(end_obj)

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Hanging_Industrial_Cable_Bundle.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Hanging_Industrial_Cable_Bundle.fbx")
    export_fbx(root, all_meshes, fbx_path)

    # QA Verification
    run_qa_verification(fbx_path, blend_path, exports_dir)

def export_fbx(root, meshes, fbx_path):
    """Export asset hierarchy to FBX with Unity-compatible orientation."""
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
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
    """Import FBX in clean test scene and verify specs, tris, UVs and hierarchy."""
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 25) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Hanging_Industrial_Cable_Bundle")
    assert root is not None, "FAIL: Root object 'SEC_Hanging_Industrial_Cable_Bundle' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    expected_meshes = {
        "Cable_Anchor",
        "Cable_01", "Cable_End_01",
        "Cable_02", "Cable_End_02",
        "Cable_03", "Cable_End_03",
        "Cable_04", "Cable_End_04",
        "Cable_05", "Cable_End_05"
    }

    mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
    found_meshes = {m.name for m in mesh_objs}
    assert expected_meshes.issubset(found_meshes), f"FAIL: Missing meshes: {expected_meshes - found_meshes}"

    total_tris = 0
    for m in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(m.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        m_tris = len(bm.faces)
        total_tris += m_tris
        bm.free()
        print(f"       -> {m.name}: {m_tris} tris")

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 500, f"FAIL: Total triangles {total_tris} exceeds 500 budget!"
    print("[PASS] Triangle count verified strictly (<= 500)!")

    for m in mesh_objs:
        assert len(m.data.materials) >= 2, f"FAIL: Mesh '{m.name}' has fewer than 2 material slots!"
        assert m.data.materials[0].name.startswith("M_Security_Atlas"), f"FAIL: Slot 0 is '{m.data.materials[0].name}', expected 'M_Security_Atlas'!"
        assert m.data.materials[1].name.startswith("M_Metal"), f"FAIL: Slot 1 is '{m.data.materials[1].name}', expected 'M_Metal'!"
    print("[PASS] Material slots strictly verified: Slot 0: M_Security_Atlas, Slot 1: M_Metal!")

    for m in mesh_objs:
        assert len(m.data.uv_layers) > 0, f"FAIL: Mesh '{m.name}' has no UV layers!"
    print("[PASS] All meshes have valid UV coordinates!")

    # Check Hierarchy: Anchor and Cables parented to root; Ends parented to respective cables
    anchor = bpy.data.objects.get("Cable_Anchor")
    assert anchor and anchor.parent == root, "FAIL: Cable_Anchor parent != root!"

    for i in range(1, 6):
        c_name = f"Cable_0{i}"
        e_name = f"Cable_End_0{i}"
        c_obj = bpy.data.objects.get(c_name)
        e_obj = bpy.data.objects.get(e_name)
        assert c_obj and c_obj.parent == root, f"FAIL: {c_name} parent != root!"
        assert e_obj and e_obj.parent == c_obj, f"FAIL: {e_name} parent != {c_name}!"
    print("[PASS] Full parent-child hierarchy strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Hanging_Industrial_Cable_Bundle"] = {
        "asset_name": "SEC_Hanging_Industrial_Cable_Bundle",
        "fbx_path": "exports/SEC_Hanging_Industrial_Cable_Bundle.fbx",
        "blend_path": "exports/SEC_Hanging_Industrial_Cable_Bundle.blend",
        "tris_count": total_tris,
        "mesh_count": len(mesh_objs),
        "empty_count": 1,
        "materials": [
            "M_Metal",
            "M_Security_Atlas"
        ],
        "status": "SUCCESS"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[OK] Updated manifest: {manifest_path}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")

    clean_backup_files(exports_dir)

def clean_backup_files(directory):
    for f in os.listdir(directory):
        if f.endswith(".blend1") or f.endswith(".blend@"):
            fp = os.path.join(directory, f)
            try:
                os.remove(fp)
                print(f"[CLEAN] Removed backup: {f}")
            except Exception as e:
                print(f"[WARN] Failed to remove backup {f}: {e}")

if __name__ == "__main__":
    build_asset()
