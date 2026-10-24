import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
import math
import os
import json

def setup_materials():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    tex_atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    # Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes = mat_atlas.node_tree.nodes
    links = mat_atlas.node_tree.links
    bsdf_atlas = nodes.get("Principled BSDF")
    if os.path.exists(tex_atlas_path):
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.load(tex_atlas_path)
        links.new(tex_node.outputs["Color"], bsdf_atlas.inputs["Base Color"])
    bsdf_atlas.inputs["Roughness"].default_value = 0.40
    bsdf_atlas.inputs["Metallic"].default_value = 0.05

    # Slot 1: M_Metal
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    bsdf_metal = mat_metal.node_tree.nodes.get("Principled BSDF")
    bsdf_metal.inputs["Base Color"].default_value = (0.75, 0.78, 0.82, 1.0)
    bsdf_metal.inputs["Metallic"].default_value = 0.95
    bsdf_metal.inputs["Roughness"].default_value = 0.22

    # Slot 2: M_Lens_Glass
    mat_glass = bpy.data.materials.new("M_Lens_Glass")
    mat_glass.use_nodes = True
    bsdf_glass = mat_glass.node_tree.nodes.get("Principled BSDF")
    bsdf_glass.inputs["Base Color"].default_value = (0.05, 0.12, 0.20, 1.0)
    bsdf_glass.inputs["Transmission Weight"].default_value = 0.92
    bsdf_glass.inputs["Roughness"].default_value = 0.04
    bsdf_glass.inputs["IOR"].default_value = 1.55

    return [mat_atlas, mat_metal, mat_glass]

def add_hex_bolt(bm, uv_layer, center, radius, height, normal_axis='Y', with_washer=True):
    """Helper to add 3D hexagonal bolt head with washer."""
    n_hex = 6
    if with_washer:
        # 6-sided washer base
        w_verts = []
        r_washer = radius * 1.4
        for i in range(6):
            ang = i * (2.0 * math.pi / 6.0)
            ca, sa = math.cos(ang), math.sin(ang)
            if normal_axis == 'Y':
                w_verts.append(bm.verts.new(center + Vector((ca * r_washer, 0.0005, sa * r_washer))))
            elif normal_axis == 'X':
                w_verts.append(bm.verts.new(center + Vector((0.0005, ca * r_washer, sa * r_washer))))
            else: # Z
                w_verts.append(bm.verts.new(center + Vector((ca * r_washer, sa * r_washer, 0.0005))))
        f_w = bm.faces.new(w_verts)
        f_w.material_index = 1
        for loop in f_w.loops: loop[uv_layer].uv = (0.25, 0.75)

    # Hex head
    b_bot = []
    b_top = []
    y_off = 0.0005 if with_washer else 0.0
    for i in range(n_hex):
        ang = i * (2.0 * math.pi / float(n_hex))
        ca, sa = math.cos(ang), math.sin(ang)
        if normal_axis == 'Y':
            b_bot.append(bm.verts.new(center + Vector((ca * radius, y_off, sa * radius))))
            b_top.append(bm.verts.new(center + Vector((ca * radius, y_off + height, sa * radius))))
        elif normal_axis == 'X':
            b_bot.append(bm.verts.new(center + Vector((y_off, ca * radius, sa * radius))))
            b_top.append(bm.verts.new(center + Vector((y_off + height, ca * radius, sa * radius))))
        else: # Z
            b_bot.append(bm.verts.new(center + Vector((ca * radius, sa * radius, y_off))))
            b_top.append(bm.verts.new(center + Vector((ca * radius, sa * radius, y_off + height))))

    for i in range(n_hex):
        i_next = (i + 1) % n_hex
        f = bm.faces.new((b_bot[i], b_bot[i_next], b_top[i_next], b_top[i]))
        f.smooth = False; f.material_index = 1
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.75)

    f_top = bm.faces.new(b_top if normal_axis == 'Y' else reversed(b_top))
    f_top.smooth = False; f_top.material_index = 1
    for loop in f_top.loops: loop[uv_layer].uv = (0.25, 0.75)

def build_mount_base(mats):
    """
    Mount_Base: Heavy-duty 4-bolt cast aluminum mounting flange and swivel knuckle fork.
    Sits flush against wall at Y=0.0.
    Flange: X: -0.055..+0.055, Z: -0.065..+0.065, Y: 0.0..0.018.
    Knuckle fork extends into +Y to joint center at (0.0, 0.080, 0.040).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # 1. Main Flange Block (Chamfered Corners)
    dx = 0.055
    dz = 0.065
    dy = 0.016
    c = 0.012 # corner chamfer

    f_profile = [
        Vector((-dx + c, 0.0, -dz)),
        Vector(( dx - c, 0.0, -dz)),
        Vector(( dx,     0.0, -dz + c)),
        Vector(( dx,     0.0,  dz - c)),
        Vector(( dx - c, 0.0,  dz)),
        Vector((-dx + c, 0.0,  dz)),
        Vector((-dx,     0.0,  dz - c)),
        Vector((-dx,     0.0, -dz + c))
    ]

    v_back = [bm.verts.new(p) for p in f_profile]
    v_front = [bm.verts.new(p + Vector((0.0, dy, 0.0))) for p in f_profile]

    # Back wall face
    f_back = bm.faces.new(reversed(v_back))
    f_back.smooth = False; f_back.material_index = 0
    for loop in f_back.loops: loop[uv_layer].uv = (0.25, 0.75)

    # Front face
    f_fr = bm.faces.new(v_front)
    f_fr.smooth = False; f_fr.material_index = 0
    for loop in f_fr.loops: loop[uv_layer].uv = (0.25, 0.75)

    # Perimeter sides
    n_p = len(f_profile)
    for i in range(n_p):
        i_next = (i + 1) % n_p
        f = bm.faces.new((v_back[i], v_front[i], v_front[i_next], v_back[i_next]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.75)

    # 4 Heavy 3D Anchor Bolts on Flange
    bolt_locs = [
        Vector((-0.038, dy, -0.045)),
        Vector(( 0.038, dy, -0.045)),
        Vector((-0.038, dy,  0.045)),
        Vector(( 0.038, dy,  0.045))
    ]
    for b_pos in bolt_locs:
        add_hex_bolt(bm, uv_layer, b_pos, radius=0.0055, height=0.005, normal_axis='Y')

    # 2. Knuckle Neck & Dual Fork Lugs (Extending from flange to joint at Y=0.080, Z=0.040)
    # Neck transition block
    neck_stations = [
        (0.016, 0.030, 0.024, 0.024),
        (0.050, 0.035, 0.020, 0.020),
        (0.075, 0.040, 0.018, 0.018)
    ]
    n_rings = []
    for y_pos, z_pos, rx, rz in neck_stations:
        v0 = bm.verts.new(Vector((-rx, y_pos, z_pos - rz)))
        v1 = bm.verts.new(Vector(( rx, y_pos, z_pos - rz)))
        v2 = bm.verts.new(Vector(( rx, y_pos, z_pos + rz)))
        v3 = bm.verts.new(Vector((-rx, y_pos, z_pos + rz)))
        n_rings.append([v0, v1, v2, v3])

    for s in range(len(neck_stations) - 1):
        r_a = n_rings[s]
        r_b = n_rings[s + 1]
        for i in range(4):
            i_next = (i + 1) % 4
            f = bm.faces.new((r_a[i], r_b[i], r_b[i_next], r_a[i_next]))
            f.smooth = True; f.material_index = 0
            for loop in f.loops: loop[uv_layer].uv = (0.25, 0.75)

    # Dual Fork Lugs on Left and Right of Knuckle Joint (X: ±0.012 to ±0.018)
    # Joint center is at (0.0, 0.080, 0.040), radius 0.016
    for side in (-1, 1):
        x_in = side * 0.010
        x_out = side * 0.018
        l_in = []
        l_out = []
        n_lug = 6
        for i in range(n_lug):
            ang = i * (2.0 * math.pi / float(n_lug))
            dy_l = math.cos(ang) * 0.016
            dz_l = math.sin(ang) * 0.016
            l_in.append(bm.verts.new(Vector((x_in, 0.080 + dy_l, 0.040 + dz_l))))
            l_out.append(bm.verts.new(Vector((x_out, 0.080 + dy_l, 0.040 + dz_l))))

        for i in range(n_lug):
            i_next = (i + 1) % n_lug
            f = bm.faces.new((l_in[i], l_out[i], l_out[i_next], l_in[i_next]))
            f.smooth = True; f.material_index = 0
            for loop in f.loops: loop[uv_layer].uv = (0.25, 0.75)

        f_outer = bm.faces.new(l_out if side > 0 else reversed(l_out))
        f_outer.smooth = False; f_outer.material_index = 0
        for loop in f_outer.loops: loop[uv_layer].uv = (0.25, 0.75)

    # Heavy Transverse M10 Knuckle Bolt along X axis (through fork lugs)
    add_hex_bolt(bm, uv_layer, Vector((0.018, 0.080, 0.040)), radius=0.007, height=0.006, normal_axis='X')
    add_hex_bolt(bm, uv_layer, Vector((-0.018, 0.080, 0.040)), radius=0.007, height=-0.006, normal_axis='X')

    bm.normal_update()
    mesh = bpy.data.meshes.new("Mount_Base")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Mount_Base", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_armored_housing(mats):
    """
    Armored_Housing: Heavy industrial vandal-proof cylindrical body with reinforcement ribs.
    Origin at Aim_Pivot (0.0, 0.080, 0.040).
    Local coordinates:
      Central tongue lug sits inside Mount_Base fork (X: -0.009..+0.009).
      Heavy cradle arm extends to body centerline at (0.0, 0.045, -0.020).
      14-radial heavy armored casing runs from Y=0.020 (bolted rear cap) to Y=0.145 (front armor collar).
      Longitudinal reinforcement ribs (top, bottom, flanks).
      Placards mapped to clean equator faces on left and right flanks.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # 1. Knuckle Central Tongue Lug (X: -0.009 to +0.009, center at (0, 0, 0))
    n_tongue = 6
    t_left = []
    t_right = []
    for i in range(n_tongue):
        ang = i * (2.0 * math.pi / float(n_tongue))
        dy = math.cos(ang) * 0.015
        dz = math.sin(ang) * 0.015
        t_left.append(bm.verts.new(Vector((-0.009, dy, dz))))
        t_right.append(bm.verts.new(Vector(( 0.009, dy, dz))))

    for i in range(n_tongue):
        i_next = (i + 1) % n_tongue
        f = bm.faces.new((t_left[i], t_right[i], t_right[i_next], t_left[i_next]))
        f.smooth = True; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.75)

    # Cradle arm extending from tongue to camera body cradle (at Y=0.035, Z=-0.024)
    c_stations = [
        (0.000,  0.000, 0.009, 0.012),
        (0.018, -0.012, 0.010, 0.011),
        (0.035, -0.024, 0.011, 0.010)
    ]
    c_rings = []
    for y_pos, z_pos, rx, rz in c_stations:
        v0 = bm.verts.new(Vector((-rx, y_pos, z_pos - rz)))
        v1 = bm.verts.new(Vector(( rx, y_pos, z_pos - rz)))
        v2 = bm.verts.new(Vector(( rx, y_pos, z_pos + rz)))
        v3 = bm.verts.new(Vector((-rx, y_pos, z_pos + rz)))
        c_rings.append([v0, v1, v2, v3])

    for s in range(len(c_stations) - 1):
        r_a = c_rings[s]
        r_b = c_rings[s + 1]
        for i in range(4):
            i_next = (i + 1) % 4
            f = bm.faces.new((r_a[i], r_b[i], r_b[i_next], r_a[i_next]))
            f.smooth = False; f.material_index = 0
            for loop in f.loops: loop[uv_layer].uv = (0.25, 0.75)

    # 2. Main Armored Camera Body Cylinder (14 radial segments)
    # Body centerline is at (0.0, Y, 0.0) relative to housing body
    n_radial = 14
    body_stations = [
        (0.015, 0.027),  # Rear bolted flange
        (0.035, 0.030),  # Main body start (cradle junction)
        (0.125, 0.030),  # Main body end
        (0.142, 0.028)   # Front guard collar junction
    ]
    b_rings = []
    for y_pos, rad in body_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / float(n_radial))
            vx = math.cos(ang) * rad
            vz = math.sin(ang) * rad
            ring.append(bm.verts.new(Vector((vx, y_pos, vz))))
        b_rings.append(ring)

    # Rear Heavy Bolted Cap (at Y=0.015)
    f_rear = bm.faces.new(reversed(b_rings[0]))
    f_rear.smooth = False; f_rear.material_index = 0
    for loop in f_rear.loops: loop[uv_layer].uv = (0.25, 0.75)

    # PG-16 Cable Gland extending from rear cap (Y: 0.015 to 0.000, radius 0.010)
    n_gland = 8
    g_base = []
    g_tip = []
    for i in range(n_gland):
        ang = i * (2.0 * math.pi / float(n_gland))
        vx = math.cos(ang) * 0.010
        vz = math.sin(ang) * 0.010
        g_base.append(bm.verts.new(Vector((vx, 0.015, vz))))
        g_tip.append(bm.verts.new(Vector((vx * 0.9, -0.002, vz * 0.9))))

    for i in range(n_gland):
        i_next = (i + 1) % n_gland
        f = bm.faces.new((g_base[i], g_base[i_next], g_tip[i_next], g_tip[i]))
        f.smooth = True; f.material_index = 1 # M_Metal
        for loop in f.loops: loop[uv_layer].uv = (0.75, 0.40)

    f_gtip = bm.faces.new(reversed(g_tip))
    f_gtip.smooth = False; f_gtip.material_index = 1
    for loop in f_gtip.loops: loop[uv_layer].uv = (0.75, 0.40)

    # Quads along Main Cylinder Body
    for s in range(len(body_stations) - 1):
        r_a = b_rings[s]
        r_b = b_rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]; vb = r_a[i_next]; vc = r_b[i_next]; vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True; f.material_index = 0

            # UV Mapping on Main Body (s == 1: Y=0.035 to Y=0.125)
            # Equator faces: Left Flank (i=6, 7 at -X) & Right Flank (i=13, 0 at +X)
            if s == 1 and i in (6, 7): # Left Flank
                for loop in f.loops:
                    t_y = (loop.vert.co.y - 0.035) / (0.125 - 0.035)
                    u = 0.53 + (1.0 - t_y) * 0.45
                    v = 0.88 + (loop.vert.co.z / 0.014) * 0.075
                    loop[uv_layer].uv = (u, v)
            elif s == 1 and i in (13, 0): # Right Flank
                for loop in f.loops:
                    t_y = (loop.vert.co.y - 0.035) / (0.125 - 0.035)
                    u = 0.53 + t_y * 0.45
                    v = 0.88 + (loop.vert.co.z / 0.014) * 0.075
                    loop[uv_layer].uv = (u, v)
            else:
                for loop in f.loops:
                    loop[uv_layer].uv = (0.25, 0.75)

    # 3. Four 3D Longitudinal Armored Reinforcement Ribs (Top-left, top-right, bot-left, bot-right)
    rib_angles = [
        math.pi / 4.0,       # 45 deg (top-right)
        3.0 * math.pi / 4.0, # 135 deg (top-left)
        5.0 * math.pi / 4.0, # 225 deg (bot-left)
        7.0 * math.pi / 4.0  # 315 deg (bot-right)
    ]
    for r_ang in rib_angles:
        ca = math.cos(r_ang)
        sa = math.sin(r_ang)
        # Tangent vector perpendicular to radial
        tx = -sa * 0.003
        tz =  ca * 0.003
        r_inner = 0.029
        r_outer = 0.0335

        # 4 vertices at rear (Y=0.038) and 4 at front (Y=0.122)
        y0, y1 = 0.038, 0.122
        rv0 = bm.verts.new(Vector((ca * r_inner - tx, y0, sa * r_inner - tz)))
        rv1 = bm.verts.new(Vector((ca * r_inner + tx, y0, sa * r_inner + tz)))
        rv2 = bm.verts.new(Vector((ca * r_outer + tx, y0, sa * r_outer + tz)))
        rv3 = bm.verts.new(Vector((ca * r_outer - tx, y0, sa * r_outer - tz)))

        fv0 = bm.verts.new(Vector((ca * r_inner - tx, y1, sa * r_inner - tz)))
        fv1 = bm.verts.new(Vector((ca * r_inner + tx, y1, sa * r_inner + tz)))
        fv2 = bm.verts.new(Vector((ca * r_outer + tx, y1, sa * r_outer + tz)))
        fv3 = bm.verts.new(Vector((ca * r_outer - tx, y1, sa * r_outer - tz)))

        # Side quads & top quad
        f_top = bm.faces.new((rv3, rv2, fv2, fv3))
        f_top.smooth = False; f_top.material_index = 0
        for loop in f_top.loops: loop[uv_layer].uv = (0.25, 0.75)

        f_side1 = bm.faces.new((rv0, rv3, fv3, fv0))
        f_side1.smooth = False; f_side1.material_index = 0
        for loop in f_side1.loops: loop[uv_layer].uv = (0.25, 0.75)

        f_side2 = bm.faces.new((rv2, rv1, fv1, fv2))
        f_side2.smooth = False; f_side2.material_index = 0
        for loop in f_side2.loops: loop[uv_layer].uv = (0.25, 0.75)

        # Front / rear bevel caps
        f_rcap = bm.faces.new((rv0, rv1, rv2, rv3))
        f_rcap.smooth = False; f_rcap.material_index = 0
        for loop in f_rcap.loops: loop[uv_layer].uv = (0.25, 0.75)

        f_fcap = bm.faces.new((fv0, fv3, fv2, fv1))
        f_fcap.smooth = False; f_fcap.material_index = 0
        for loop in f_fcap.loops: loop[uv_layer].uv = (0.25, 0.75)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Armored_Housing")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Armored_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_guard(mats):
    """
    Lens_Guard: Heavy stainless steel vandal armor bezel ring with 4 Torx locking bolts.
    Parented to Armored_Housing.
    Origin at (0.0, 0.0, 0.0) in Housing space.
    Runs from Y=0.142 to Y=0.165 (extending well past the glass for high impact protection).
    Materials: Slot 0 M_Security_Atlas, Slot 1 M_Metal.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 14

    # Heavy stepped steel armor ring stations (5 stations = 4 quad rings)
    guard_stations = [
        (0.142, 0.0315), # Base collar mount
        (0.147, 0.0340), # Thick armored outer shoulder
        (0.165, 0.0340), # Front protective hood lip
        (0.165, 0.0250), # Front inner lip rim
        (0.148, 0.0150)  # Recessed optic seat rim
    ]
    g_rings = []
    for y_pos, rad in guard_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / float(n_radial))
            vx = math.cos(ang) * rad
            vz = math.sin(ang) * rad
            ring.append(bm.verts.new(Vector((vx, y_pos, vz))))
        g_rings.append(ring)

    for s in range(len(guard_stations) - 1):
        r_a = g_rings[s]
        r_b = g_rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]; vb = r_a[i_next]; vc = r_b[i_next]; vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True

            # Outer rings (s <= 1) are M_Metal, inner recessed rings (s >= 2) map to M_Security_Atlas LED array
            if s <= 1:
                f.material_index = 1 # M_Metal
                for loop in f.loops: loop[uv_layer].uv = (0.75, 0.35)
            elif s == 2: # Front lip face
                f.material_index = 1
                for loop in f.loops: loop[uv_layer].uv = (0.75, 0.35)
            else: # Recessed LED and ballistic bezel (Quadrant 3)
                f.material_index = 0
                ang0 = i * (2.0 * math.pi / float(n_radial))
                ang1 = (i + 1) * (2.0 * math.pi / float(n_radial))
                r_uv_a = 0.20
                r_uv_b = 0.10
                for loop in f.loops:
                    r_uv = r_uv_a if loop.vert in (va, vb) else r_uv_b
                    loop_ang = ang0 if loop.vert in (va, vd) else ang1
                    loop[uv_layer].uv = (0.25 + r_uv * math.cos(loop_ang), 0.25 + r_uv * math.sin(loop_ang))

    # 4 3D Torx Security Locking Bolts on Guard Shoulder (Y=0.147, radius 0.0315)
    for b_idx in range(4):
        ang = (math.pi / 4.0) + b_idx * (math.pi / 2.0)
        bx = math.cos(ang) * 0.0315
        bz = math.sin(ang) * 0.0315
        add_hex_bolt(bm, uv_layer, Vector((bx, 0.147, bz)), radius=0.0035, height=0.003, normal_axis='Y', with_washer=False)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Lens_Guard")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Lens_Guard", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_glass(mats):
    """
    Lens_Glass: Deeply recessed multi-coated ballistic optical glass element.
    Convex dome from Y=0.148 to Y=0.152, radius 0.015m.
    Parented to Armored_Housing.
    Material: Slot 2 M_Lens_Glass.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 12
    r_lens = 0.015

    v_rim = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / float(n_radial))
        vx = math.cos(ang) * r_lens
        vz = math.sin(ang) * r_lens
        v_rim.append(bm.verts.new(Vector((vx, 0.148, vz))))

    # Apex vertex at center of convex dome
    v_apex = bm.verts.new(Vector((0.0, 0.152, 0.0)))

    # Triangle fan for dome
    cu, cv = 0.75, 0.25 # Quadrant 4 in atlas
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        va = v_rim[i]
        vb = v_rim[i_next]
        f = bm.faces.new((va, vb, v_apex))
        f.smooth = True
        f.material_index = 2 # M_Lens_Glass

        ang0 = i * (2.0 * math.pi / float(n_radial))
        ang1 = (i + 1) * (2.0 * math.pi / float(n_radial))
        for loop in f.loops:
            if loop.vert == va:
                loop[uv_layer].uv = (cu + 0.21 * math.cos(ang0), cv + 0.21 * math.sin(ang0))
            elif loop.vert == vb:
                loop[uv_layer].uv = (cu + 0.21 * math.cos(ang1), cv + 0.21 * math.sin(ang1))
            else: # Apex
                loop[uv_layer].uv = (cu, cv)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Lens_Glass")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Lens_Glass", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def main():
    # Clear existing scene
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    # 1. Setup Materials
    mats = setup_materials()

    # 2. Build Armored_Root (SEC_Camera_Armored)
    root = bpy.data.objects.new("SEC_Camera_Armored", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    # 3. Build Mount_Base (Child of Root)
    mount_base = build_mount_base(mats)
    mount_base.parent = root

    # 4. Build Aim_Pivot (Empty at knuckle joint, Child of Mount_Base)
    aim_pivot = bpy.data.objects.new("Aim_Pivot", None)
    aim_pivot.empty_display_type = 'ARROWS'
    aim_pivot.location = Vector((0.0, 0.080, 0.040))
    aim_pivot.parent = mount_base
    bpy.context.collection.objects.link(aim_pivot)

    # Add Limit Rotation constraint on Aim_Pivot (Local X ±25 deg)
    con = aim_pivot.constraints.new('LIMIT_ROTATION')
    con.owner_space = 'LOCAL'
    con.use_limit_x = True
    con.min_x = math.radians(-25.0)
    con.max_x = math.radians(25.0)
    con.use_limit_y = True
    con.min_y = 0.0
    con.max_y = 0.0
    con.use_limit_z = True
    con.min_z = 0.0
    con.max_z = 0.0

    aim_pivot["tilt_min_deg"] = -25.0
    aim_pivot["tilt_max_deg"] = 25.0

    # 5. Build Armored_Housing (Child of Aim_Pivot)
    housing = build_armored_housing(mats)
    housing.parent = aim_pivot

    # 6. Build Lens_Guard (Child of Armored_Housing)
    guard = build_lens_guard(mats)
    guard.parent = housing

    # 7. Build Lens_Glass (Child of Armored_Housing)
    glass = build_lens_glass(mats)
    glass.parent = housing

    # Export paths
    blend_path = os.path.join(exports_dir, "SEC_Camera_Armored.blend")
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Armored.fbx")

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Select all hierarchy for export
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
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

    # -------------------------------------------------------------
    # HEADLESS QA VERIFICATION TEST
    # -------------------------------------------------------------
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 33) ---")
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    re_root = bpy.data.objects.get("SEC_Camera_Armored")
    assert re_root is not None, "FAIL: Root SEC_Camera_Armored missing in FBX"

    total_tris = 0
    mesh_names = []
    empty_names = []

    for obj in re_root.children_recursive + [re_root]:
        if obj.type == 'MESH':
            mesh_names.append(obj.name)
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            tris = len(bm.faces)
            total_tris += tris
            bm.free()
            print(f"       -> {obj.name}: {tris} tris")
        elif obj.type == 'EMPTY':
            empty_names.append(obj.name)

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 620, f"FAIL: Total triangles {total_tris} exceeds 620 budget!"
    print("[PASS] Triangle count verified strictly (<= 620)!")

    # Verify hierarchy
    re_mount = bpy.data.objects.get("Mount_Base")
    re_pivot = bpy.data.objects.get("Aim_Pivot")
    re_housing = bpy.data.objects.get("Armored_Housing")
    re_guard = bpy.data.objects.get("Lens_Guard")
    re_glass = bpy.data.objects.get("Lens_Glass")

    assert re_mount and re_mount.parent == re_root, "FAIL: Mount_Base parent mismatch"
    assert re_pivot and re_pivot.parent == re_mount, "FAIL: Aim_Pivot parent mismatch"
    assert re_housing and re_housing.parent == re_pivot, "FAIL: Armored_Housing parent mismatch"
    assert re_guard and re_guard.parent == re_housing, "FAIL: Lens_Guard parent mismatch"
    assert re_glass and re_glass.parent == re_housing, "FAIL: Lens_Glass parent mismatch"
    print("[PASS] Full parent-child hierarchy strictly verified!")

    # Verify Material Slots
    expected_mats = ["M_Security_Atlas", "M_Metal", "M_Lens_Glass"]
    for m_obj in [re_mount, re_housing, re_guard, re_glass]:
        m_names = [slot.material.name.split('.')[0] for slot in m_obj.material_slots if slot.material]
        for em in expected_mats:
            assert em in m_names, f"FAIL: {m_obj.name} missing material {em}"
    print("[PASS] Material slots strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest = {
        "SEC_Camera_Armored": {
            "asset_name": "SEC_Camera_Armored",
            "fbx_path": "exports/SEC_Camera_Armored.fbx",
            "blend_path": "exports/SEC_Camera_Armored.blend",
            "tris_count": total_tris,
            "mesh_count": len(mesh_names),
            "empty_count": len(empty_names),
            "materials": expected_mats,
            "status": "SUCCESS"
        }
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Updated manifest: {manifest_path}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")

    # Clean backup .blend1 if created
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[CLEAN] Removed backup: {blend1_path}")

if __name__ == "__main__":
    main()
