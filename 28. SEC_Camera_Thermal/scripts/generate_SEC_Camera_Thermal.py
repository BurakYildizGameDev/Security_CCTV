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
    Slot 1: M_Lens_Glass (Germanium LWIR optical window)
    Slot 2: M_Metal
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

    # 1. M_Lens_Glass (Germanium optical window with distinctive warm amber/golden LWIR reflection)
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
        g_bsdf.inputs['Base Color'].default_value = (0.45, 0.30, 0.10, 1.0) # Germanium amber
    g_bsdf.inputs['Roughness'].default_value = 0.04
    g_bsdf.inputs['Metallic'].default_value = 0.20
    if 'Specular IOR Level' in g_bsdf.inputs:
        g_bsdf.inputs['Specular IOR Level'].default_value = 1.0
    if 'Transmission Weight' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission Weight'].default_value = 0.25
    elif 'Transmission' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission'].default_value = 0.25
    if 'IOR' in g_bsdf.inputs:
        g_bsdf.inputs['IOR'].default_value = 4.0 # Germanium refractive index ~4.0!
    glinks.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    # 2. M_Metal (Stainless steel / anodized hardware)
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    mnodes = mat_metal.node_tree.nodes
    mlinks = mat_metal.node_tree.links
    mnodes.clear()

    m_out = mnodes.new("ShaderNodeOutputMaterial")
    m_bsdf = mnodes.new("ShaderNodeBsdfPrincipled")
    m_bsdf.inputs['Base Color'].default_value = (0.75, 0.78, 0.82, 1.0)
    m_bsdf.inputs['Metallic'].default_value = 0.90
    m_bsdf.inputs['Roughness'].default_value = 0.22
    mlinks.new(m_bsdf.outputs['BSDF'], m_out.inputs['Surface'])

    return [mat_atlas, mat_glass, mat_metal]

def build_mount_bracket(mats):
    """
    Mount_Bracket: Rectangular wall mount flange at (0, 0, 0), normal pointing in +Y.
    Dimensions: 80x80mm, thickness 10mm.
    4 real 3D countersunk screws, tubular stalk, dual-clevis knuckle drum at (0, 0.060, 0),
    transverse M6 bolt head (+X) and hex locking nut (-X).
    Slot 0: M_Security_Atlas, Slot 2: M_Metal.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # 1. Base Plate (8-corner chamfered flange)
    w, h, th = 0.040, 0.040, 0.010
    ch = 0.010
    profile_2d = [
        (-w + ch, -h), (w - ch, -h),
        (w, -h + ch), (w, h - ch),
        (w - ch, h), (-w + ch, h),
        (-w, h - ch), (-w, -h + ch)
    ]
    v_back = [bm.verts.new(Vector((x, 0.000, z))) for x, z in profile_2d]
    v_front = [bm.verts.new(Vector((x, th, z))) for x, z in profile_2d]
    bm.verts.ensure_lookup_table()

    # Front face
    f_front = bm.faces.new(reversed(v_front))
    f_front.smooth = False
    f_front.material_index = 0
    cu, cv = 0.25, 0.25 # Quadrant 3
    for loop in f_front.loops:
        v = loop.vert
        loop[uv_layer].uv = (cu + (v.co.x / 0.040) * 0.20, cv + (v.co.z / 0.040) * 0.20)

    # Perimeter sides
    n_p = len(profile_2d)
    for i in range(n_p):
        i_next = (i + 1) % n_p
        f = bm.faces.new((v_back[i], v_back[i_next], v_front[i_next], v_front[i]))
        f.smooth = False
        f.material_index = 2 # Slot 2: M_Metal
        for loop in f.loops: loop[uv_layer].uv = (0.20, 0.10)

    # 4 Countersunk Screws (6-sided prisms)
    for sx, sz in [(-0.026, -0.026), (0.026, -0.026), (0.026, 0.026), (-0.026, 0.026)]:
        v_sc = []
        for j in range(6):
            ja = j * (2.0 * math.pi / 6.0)
            v_sc.append(bm.verts.new(Vector((sx + math.cos(ja) * 0.0035, th + 0.0005, sz + math.sin(ja) * 0.0035))))
        bm.verts.ensure_lookup_table()
        f_sc = bm.faces.new(reversed(v_sc))
        f_sc.smooth = False
        f_sc.material_index = 2
        for loop in f_sc.loops: loop[uv_layer].uv = (0.22, 0.22)

    # 2. Tubular Stalk from Y=0.010 to Y=0.046 (radius 0.014, 8 radial)
    n_st = 8
    r_st = 0.014
    v_st0 = []
    v_st1 = []
    for i in range(n_st):
        ang = i * (2.0 * math.pi / n_st)
        cx = math.cos(ang) * r_st
        cz = math.sin(ang) * r_st
        v_st0.append(bm.verts.new(Vector((cx, 0.010, cz))))
        v_st1.append(bm.verts.new(Vector((cx, 0.046, cz))))
    bm.verts.ensure_lookup_table()

    for i in range(n_st):
        i_next = (i + 1) % n_st
        f = bm.faces.new((v_st0[i], v_st0[i_next], v_st1[i_next], v_st1[i]))
        f.smooth = True
        f.material_index = 0
        u0 = 0.10 + (i / float(n_st)) * 0.25
        u1 = 0.10 + ((i + 1) / float(n_st)) * 0.25
        for loop in f.loops:
            v_val = 0.20 if loop.vert in (v_st0[i], v_st0[i_next]) else 0.30
            loop[uv_layer].uv = (u0 if loop.vert in (v_st0[i], v_st1[i]) else u1, v_val)

    # 3. Knuckle Joint Drum at Y=0.060 (radius 0.015, X: -0.016 to +0.016, 10 radial)
    n_k = 10
    r_k = 0.015
    y_k = 0.060
    k_l = []
    k_r = []
    for i in range(n_k):
        ang = i * (2.0 * math.pi / n_k)
        cy = y_k + math.cos(ang) * r_k
        cz = math.sin(ang) * r_k
        k_l.append(bm.verts.new(Vector((-0.016, cy, cz))))
        k_r.append(bm.verts.new(Vector(( 0.016, cy, cz))))
    bm.verts.ensure_lookup_table()

    for i in range(n_k):
        i_next = (i + 1) % n_k
        f = bm.faces.new((k_l[i], k_l[i_next], k_r[i_next], k_r[i]))
        f.smooth = True
        f.material_index = 2 # Slot 2: M_Metal
        for loop in f.loops: loop[uv_layer].uv = (0.15, 0.15)

    f_kl = bm.faces.new(k_l)
    f_kl.smooth = False; f_kl.material_index = 2
    for loop in f_kl.loops: loop[uv_layer].uv = (0.18, 0.18)

    f_kr = bm.faces.new(reversed(k_r))
    f_kr.smooth = False; f_kr.material_index = 2
    for loop in f_kr.loops: loop[uv_layer].uv = (0.18, 0.18)

    # M6 Hex Bolt on +X (X: 0.016 to 0.023, r=0.007)
    v_hex_b = []
    v_hex_t = []
    for j in range(6):
        ja = j * (2.0 * math.pi / 6.0)
        hy = y_k + math.cos(ja) * 0.007
        hz = math.sin(ja) * 0.007
        v_hex_b.append(bm.verts.new(Vector((0.016, hy, hz))))
        v_hex_t.append(bm.verts.new(Vector((0.023, hy, hz))))
    bm.verts.ensure_lookup_table()

    for j in range(6):
        j_next = (j + 1) % 6
        f = bm.faces.new((v_hex_b[j], v_hex_b[j_next], v_hex_t[j_next], v_hex_t[j]))
        f.smooth = False; f.material_index = 2
        for loop in f.loops: loop[uv_layer].uv = (0.22, 0.22)

    f_hex_cap = bm.faces.new(reversed(v_hex_t))
    f_hex_cap.smooth = False; f_hex_cap.material_index = 2
    for loop in f_hex_cap.loops: loop[uv_layer].uv = (0.22, 0.22)

    # Hex Locking Nut on -X (X: -0.016 to -0.021, r=0.006)
    v_nut_b = []
    v_nut_t = []
    for j in range(6):
        ja = j * (2.0 * math.pi / 6.0)
        hy = y_k + math.cos(ja) * 0.006
        hz = math.sin(ja) * 0.006
        v_nut_b.append(bm.verts.new(Vector((-0.016, hy, hz))))
        v_nut_t.append(bm.verts.new(Vector((-0.021, hy, hz))))
    bm.verts.ensure_lookup_table()

    for j in range(6):
        j_next = (j + 1) % 6
        f = bm.faces.new((v_nut_t[j], v_nut_t[j_next], v_nut_b[j_next], v_nut_b[j]))
        f.smooth = False; f.material_index = 2
        for loop in f.loops: loop[uv_layer].uv = (0.22, 0.22)

    f_nut_cap = bm.faces.new(v_nut_t)
    f_nut_cap.smooth = False; f_nut_cap.material_index = 2
    for loop in f_nut_cap.loops: loop[uv_layer].uv = (0.22, 0.22)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Mount_Bracket")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Mount_Bracket", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_thermal_housing(mats):
    """
    Thermal_Housing: Ruggedized rectangular thermal imager body with side & top cooling fins,
    stepped knurled manual focus lens barrel, and rear PG-11 gland + BNC connector.
    Origin at Aim_Pivot: (0.0, 0.060, 0.0).
    Local coordinates:
      Camera optical centerline at Z=0.075.
      Main body width X: ±0.040, height Z: 0.040..0.110, length Y: -0.020..0.130.
      Front lens barrel extends to Y=0.170, radius 0.027.
    Slot 0: M_Security_Atlas, Slot 2: M_Metal.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    zc = 0.075 # Camera centerline Z

    # 1. Lower knuckle clevis arm connecting Aim_Pivot (0,0,0) to main housing bottom (Z=0.040)
    sw, sh = 0.011, 0.010
    v_c0 = [
        bm.verts.new(Vector((-sw, -sh, -0.005))),
        bm.verts.new(Vector(( sw, -sh, -0.005))),
        bm.verts.new(Vector(( sw,  sh, -0.005))),
        bm.verts.new(Vector((-sw,  sh, -0.005)))
    ]
    v_c1 = [
        bm.verts.new(Vector((-0.016, 0.010, 0.040))),
        bm.verts.new(Vector(( 0.016, 0.010, 0.040))),
        bm.verts.new(Vector(( 0.016, 0.060, 0.040))),
        bm.verts.new(Vector((-0.016, 0.060, 0.040)))
    ]
    bm.verts.ensure_lookup_table()
    for i in range(4):
        i_next = (i + 1) % 4
        f = bm.faces.new((v_c0[i], v_c0[i_next], v_c1[i_next], v_c1[i]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.15, 0.65)

    # 2. Main Rectangular Body with Chamfered Corners
    dx, dz, ch = 0.040, 0.035, 0.008
    body_section = [
        (-dx + ch, zc - dz), (dx - ch, zc - dz),  # 0, 1: bottom
        (dx, zc - dz + ch), (dx, zc + dz - ch),   # 2, 3: right side (+X)
        (dx - ch, zc + dz), (-dx + ch, zc + dz),  # 4, 5: top
        (-dx, zc + dz - ch), (-dx, zc - dz + ch)  # 6, 7: left side (-X)
    ]

    y_stations = [-0.020, 0.010, 0.100, 0.130]
    rings = []
    for y_pos in y_stations:
        scale = 0.96 if y_pos == 0.130 else 1.0
        ring = [bm.verts.new(Vector((x * scale, y_pos, zc + (z - zc) * scale))) for x, z in body_section]
        rings.append(ring)
    bm.verts.ensure_lookup_table()

    # Rear cap at station 0 (pointing in -Y)
    f_rear = bm.faces.new(rings[0])
    f_rear.smooth = False; f_rear.material_index = 0
    for loop in f_rear.loops: loop[uv_layer].uv = (0.45, 0.75)

    # Quads along body with continuous UV mapping
    n_bs = len(body_section)
    for s in range(len(y_stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_bs):
            i_next = (i + 1) % n_bs
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True
            f.material_index = 0

            # Side panels (i=2 on right, i=6 on left) map continuously to Quadrant 1
            if i in [2, 6]:
                for loop in f.loops:
                    v_co = loop.vert.co
                    ty = max(0.0, min(1.0, (v_co.y - (-0.020)) / 0.150))
                    tz = max(0.0, min(1.0, (v_co.z - (zc - dz)) / (2.0 * dz)))
                    if i == 2:
                        u_val = 0.45 - ty * 0.40
                    else:
                        u_val = 0.05 + ty * 0.40
                    v_val = 0.72 + tz * 0.20
                    loop[uv_layer].uv = (u_val, v_val)
            else:
                for loop in f.loops: loop[uv_layer].uv = (0.10, 0.96)

    # 3. Cooling Fin Ridges on Top of Body (4 transverse ribs)
    for fin_y in [0.020, 0.045, 0.070, 0.095]:
        v_fin = [
            bm.verts.new(Vector((-dx + ch, fin_y - 0.003, zc + dz))),
            bm.verts.new(Vector(( dx - ch, fin_y - 0.003, zc + dz))),
            bm.verts.new(Vector(( dx - ch, fin_y + 0.003, zc + dz))),
            bm.verts.new(Vector((-dx + ch, fin_y + 0.003, zc + dz))),
            bm.verts.new(Vector((-dx + ch, fin_y - 0.003, zc + dz + 0.005))),
            bm.verts.new(Vector(( dx - ch, fin_y - 0.003, zc + dz + 0.005))),
            bm.verts.new(Vector(( dx - ch, fin_y + 0.003, zc + dz + 0.005))),
            bm.verts.new(Vector((-dx + ch, fin_y + 0.003, zc + dz + 0.005)))
        ]
        bm.verts.ensure_lookup_table()
        f_top = bm.faces.new((v_fin[4], v_fin[7], v_fin[6], v_fin[5]))
        f_top.smooth = False; f_top.material_index = 0
        for loop in f_top.loops: loop[uv_layer].uv = (0.15, 0.40)
        f_f = bm.faces.new((v_fin[0], v_fin[1], v_fin[5], v_fin[4]))
        f_b = bm.faces.new((v_fin[2], v_fin[3], v_fin[7], v_fin[6]))
        f_f.smooth = False; f_b.smooth = False
        f_f.material_index = 0; f_b.material_index = 0
        for loop in f_f.loops: loop[uv_layer].uv = (0.15, 0.40)
        for loop in f_b.loops: loop[uv_layer].uv = (0.15, 0.40)

    # Side Heatsink Rails (+X and -X)
    for side_x in [-dx, dx]:
        s_sign = 1.0 if side_x > 0 else -1.0
        for s_z in [zc - 0.015, zc + 0.015]:
            v_sr = [
                bm.verts.new(Vector((side_x, 0.010, s_z - 0.003))),
                bm.verts.new(Vector((side_x, 0.100, s_z - 0.003))),
                bm.verts.new(Vector((side_x, 0.100, s_z + 0.003))),
                bm.verts.new(Vector((side_x, 0.010, s_z + 0.003))),
                bm.verts.new(Vector((side_x + s_sign * 0.004, 0.010, s_z - 0.003))),
                bm.verts.new(Vector((side_x + s_sign * 0.004, 0.100, s_z - 0.003))),
                bm.verts.new(Vector((side_x + s_sign * 0.004, 0.100, s_z + 0.003))),
                bm.verts.new(Vector((side_x + s_sign * 0.004, 0.010, s_z + 0.003)))
            ]
            bm.verts.ensure_lookup_table()
            f_sr_out = bm.faces.new((v_sr[4], v_sr[5], v_sr[6], v_sr[7]) if side_x > 0 else (v_sr[4], v_sr[7], v_sr[6], v_sr[5]))
            f_sr_out.smooth = False; f_sr_out.material_index = 0
            for loop in f_sr_out.loops: loop[uv_layer].uv = (0.15, 0.40)

    # 4. Stepped Lens Barrel with Manual Focus Ring
    # Stations:
    # 0: Y=0.130, r=0.027 (barrel rear collar)
    # 1: Y=0.145, r=0.027
    # 2: Y=0.148, r=0.0285 (focus ring knurl step)
    # 3: Y=0.162, r=0.0285
    # 4: Y=0.165, r=0.025 (front bezel collar)
    # 5: Y=0.170, r=0.025
    # 6: Y=0.170, r=0.019 (inner aperture floor)
    n_radial = 14
    b_stations = [
        (0.130, 0.027),
        (0.145, 0.027),
        (0.148, 0.0285),
        (0.162, 0.0285),
        (0.165, 0.025),
        (0.170, 0.025),
        (0.170, 0.019)
    ]
    b_rings = []
    for y_pos, r_rad in b_stations:
        b_ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vz = zc + math.sin(ang) * r_rad
            b_ring.append(bm.verts.new(Vector((vx, y_pos, vz))))
        b_rings.append(b_ring)
    bm.verts.ensure_lookup_table()

    for s in range(len(b_stations) - 1):
        r_a = b_rings[s]
        r_b = b_rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            f = bm.faces.new((r_a[i], r_a[i_next], r_b[i_next], r_b[i]))
            f.smooth = True if s not in [1, 3, 5] else False
            f.material_index = 0
            u0 = 0.52 + (i / float(n_radial)) * 0.44
            u1 = 0.52 + ((i + 1) / float(n_radial)) * 0.44
            v_val = 0.85 if s in [2, 3] else 0.75 # knurled focus ring texture
            for loop in f.loops: loop[uv_layer].uv = (u0, v_val)

    # 5. Rear Connectors: PG-11 Gland & BNC Port
    # PG-11 Gland at (0, -0.020, zc)
    n_gl = 8
    r_gl = 0.010
    v_gl0 = []
    v_gl1 = []
    for i in range(n_gl):
        ang = i * (2.0 * math.pi / n_gl)
        v_gl0.append(bm.verts.new(Vector((math.cos(ang) * r_gl, -0.020, zc + math.sin(ang) * r_gl))))
        v_gl1.append(bm.verts.new(Vector((math.cos(ang) * r_gl, -0.036, zc + math.sin(ang) * r_gl))))
    bm.verts.ensure_lookup_table()

    for i in range(n_gl):
        i_next = (i + 1) % n_gl
        f = bm.faces.new((v_gl0[i], v_gl1[i], v_gl1[i_next], v_gl0[i_next]))
        f.smooth = True; f.material_index = 2
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.15)
    f_gl_cap = bm.faces.new(reversed(v_gl1))
    f_gl_cap.smooth = False; f_gl_cap.material_index = 2
    for loop in f_gl_cap.loops: loop[uv_layer].uv = (0.25, 0.15)

    # BNC Test Port at (0.022, -0.020, zc - 0.015)
    bnc_c = Vector((0.022, -0.020, zc - 0.015))
    v_bnc0 = []
    v_bnc1 = []
    for j in range(6):
        ja = j * (2.0 * math.pi / 6.0)
        v_bnc0.append(bm.verts.new(bnc_c + Vector((math.cos(ja) * 0.005, 0.000, math.sin(ja) * 0.005))))
        v_bnc1.append(bm.verts.new(bnc_c + Vector((math.cos(ja) * 0.005, -0.012, math.sin(ja) * 0.005))))
    bm.verts.ensure_lookup_table()

    for j in range(6):
        j_next = (j + 1) % 6
        f = bm.faces.new((v_bnc0[j], v_bnc1[j], v_bnc1[j_next], v_bnc0[j_next]))
        f.smooth = True; f.material_index = 2
        for loop in f.loops: loop[uv_layer].uv = (0.20, 0.20)
    f_bnc_cap = bm.faces.new(reversed(v_bnc1))
    f_bnc_cap.smooth = False; f_bnc_cap.material_index = 2
    for loop in f_bnc_cap.loops: loop[uv_layer].uv = (0.20, 0.20)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Thermal_Housing")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Thermal_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_sensor_window(mats):
    """
    Sensor_Window: Germanium optical sensor window recessed at Y=0.168.
    Radius: r=0.019m, 16 radial segments.
    Subtle convex dome pointing FORWARD in +Y (apex at Y=0.172).
    Slot 1: M_Lens_Glass (Germanium LWIR anti-reflective golden interference layer).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16
    zc = 0.075
    r_window = 0.019
    y_base = 0.168

    v_ring = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        cx = math.cos(ang) * r_window
        cz = math.sin(ang) * r_window
        v_ring.append(bm.verts.new(Vector((cx, y_base, zc + cz))))

    v_apex = bm.verts.new(Vector((0.0, 0.172, zc)))
    bm.verts.ensure_lookup_table()

    # Convex fan faces pointing forward in +Y
    cu, cv = 0.75, 0.25 # Quadrant 4 in 1024x1024 atlas
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_ring[i], v_apex, v_ring[i_next]))
        f.smooth = True
        f.material_index = 1 # Slot 1: M_Lens_Glass
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        for loop in f.loops:
            if loop.vert == v_ring[i]: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang0), cv + 0.21 * math.sin(ang0))
            elif loop.vert == v_ring[i_next]: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang1), cv + 0.21 * math.sin(ang1))
            elif loop.vert == v_apex: loop[uv_layer].uv = (cu, cv)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Sensor_Window")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.material_index = 1

    obj = bpy.data.objects.new("Sensor_Window", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_asset():
    """Build full SEC_Camera_Thermal hierarchy."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mats = create_materials(atlas_path)

    # 1. Root Empty: SEC_Camera_Thermal at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Camera_Thermal", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 2. Mount_Bracket (Child of Root)
    bracket = build_mount_bracket(mats)
    bracket.parent = root

    # 3. Aim_Pivot (Empty at knuckle joint center: (0, 0.060, 0))
    aim_pivot = bpy.data.objects.new("Aim_Pivot", None)
    aim_pivot.empty_display_type = 'ARROWS'
    aim_pivot.empty_display_size = 0.04
    aim_pivot.location = (0.0, 0.060, 0.0)
    bpy.context.collection.objects.link(aim_pivot)
    aim_pivot.parent = root
    aim_pivot["limit_rot_x_min"] = -30.0
    aim_pivot["limit_rot_x_max"] = 30.0
    aim_pivot["limit_rot_z_min"] = -30.0
    aim_pivot["limit_rot_z_max"] = 30.0

    # 4. Thermal_Housing (Child of Aim_Pivot, origin at Aim_Pivot)
    housing = build_thermal_housing(mats)
    housing.parent = aim_pivot

    # 5. Sensor_Window (Child of Thermal_Housing)
    sensor = build_sensor_window(mats)
    sensor.parent = housing

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Camera_Thermal.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Thermal.fbx")
    export_fbx(root, [bracket, housing, sensor], aim_pivot, fbx_path)

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
    """Import FBX into a clean scene and verify tris, hierarchy, materials, UVs."""
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 28) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Camera_Thermal")
    assert root is not None, "FAIL: Root object 'SEC_Camera_Thermal' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    aim_pivot = bpy.data.objects.get("Aim_Pivot")
    assert aim_pivot is not None, "FAIL: Aim_Pivot missing!"
    assert aim_pivot.parent == root, "FAIL: Aim_Pivot parent != root!"
    assert aim_pivot.type == 'EMPTY', f"FAIL: Aim_Pivot is type {aim_pivot.type}, expected EMPTY!"

    expected_meshes = {
        "Mount_Bracket",
        "Thermal_Housing",
        "Sensor_Window"
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
    bracket = bpy.data.objects.get("Mount_Bracket")
    housing = bpy.data.objects.get("Thermal_Housing")
    sensor = bpy.data.objects.get("Sensor_Window")

    assert bracket.parent == root, "FAIL: Mount_Bracket parent != root!"
    assert housing.parent == aim_pivot, "FAIL: Thermal_Housing parent != aim_pivot!"
    assert sensor.parent == housing, "FAIL: Sensor_Window parent != housing!"

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 480, f"FAIL: Total triangles {total_tris} exceeds 480 budget!"
    print("[PASS] Triangle count verified strictly (<= 480)!")
    print("[PASS] Full parent-child hierarchy strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Camera_Thermal"] = {
        "asset_name": "SEC_Camera_Thermal",
        "fbx_path": "exports/SEC_Camera_Thermal.fbx",
        "blend_path": "exports/SEC_Camera_Thermal.blend",
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
