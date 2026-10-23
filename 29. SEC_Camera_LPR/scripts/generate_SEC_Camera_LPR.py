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
    Slot 1: M_Lens_Glass
    Slot 2: M_Emission (Pulsed 850nm IR Illuminator)
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

    # 1. M_Lens_Glass (Multi-coated high-speed telephoto lens glass)
    mat_glass = bpy.data.materials.new("M_Lens_Glass")
    mat_glass.use_nodes = True
    gnodes = mat_glass.node_tree.nodes
    glinks = mat_glass.node_tree.links
    gnodes.clear()

    g_out = gnodes.new("ShaderNodeOutputMaterial")
    g_bsdf = gnodes.new("ShaderNodeBsdfPrincipled")
    g_bsdf.inputs['Base Color'].default_value = (0.05, 0.10, 0.16, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.04
    g_bsdf.inputs['Metallic'].default_value = 0.05
    if 'Specular IOR Level' in g_bsdf.inputs:
        g_bsdf.inputs['Specular IOR Level'].default_value = 0.95
    if 'Transmission Weight' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission Weight'].default_value = 0.40
    elif 'Transmission' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission'].default_value = 0.40
    if 'IOR' in g_bsdf.inputs:
        g_bsdf.inputs['IOR'].default_value = 1.54
    glinks.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    # 2. M_Emission (Pulsed 850nm IR LED Strobe Array)
    mat_emission = bpy.data.materials.new("M_Emission")
    mat_emission.use_nodes = True
    enodes = mat_emission.node_tree.nodes
    elinks = mat_emission.node_tree.links
    enodes.clear()

    e_out = enodes.new("ShaderNodeOutputMaterial")
    e_bsdf = enodes.new("ShaderNodeBsdfPrincipled")
    e_bsdf.inputs['Roughness'].default_value = 0.25
    e_bsdf.inputs['Metallic'].default_value = 0.0

    if os.path.exists(atlas_path):
        tex_e = enodes.new("ShaderNodeTexImage")
        tex_e.image = bpy.data.images.load(atlas_path)
        elinks.new(tex_e.outputs['Color'], e_bsdf.inputs['Base Color'])
        elinks.new(tex_e.outputs['Color'], e_bsdf.inputs['Emission Color'])
        if 'Emission Strength' in e_bsdf.inputs:
            e_bsdf.inputs['Emission Strength'].default_value = 3.5
    else:
        e_bsdf.inputs['Base Color'].default_value = (0.08, 0.02, 0.02, 1.0)
        if 'Emission Color' in e_bsdf.inputs:
            e_bsdf.inputs['Emission Color'].default_value = (0.95, 0.20, 0.15, 1.0)
            e_bsdf.inputs['Emission Strength'].default_value = 4.0
    elinks.new(e_bsdf.outputs['BSDF'], e_out.inputs['Surface'])

    return [mat_atlas, mat_glass, mat_emission]

def build_mount_plate(mats):
    """
    Mount_Plate: Heavy-duty wall mount plate at (0, 0, 0), normal pointing in +Y.
    Dimensions: 84x84mm, thickness 10mm.
    4 real 3D hex anchor bolts, central bracket socket boss extending to Y=0.060,
    knuckle joint drum with M6 clamp bolt head and hex nut.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    w, h, th = 0.042, 0.042, 0.010
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
    cu, cv = 0.25, 0.25
    for loop in f_front.loops:
        v = loop.vert
        loop[uv_layer].uv = (cu + (v.co.x / 0.042) * 0.20, cv + (v.co.z / 0.042) * 0.20)

    # Perimeter sides
    n_p = len(profile_2d)
    for i in range(n_p):
        i_next = (i + 1) % n_p
        f = bm.faces.new((v_back[i], v_back[i_next], v_front[i_next], v_front[i]))
        f.smooth = False
        f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.20, 0.10)

    # 4 Real 3D Hex Anchor Bolts with Washers
    for bx, bz in [(-0.028, -0.028), (0.028, -0.028), (0.028, 0.028), (-0.028, 0.028)]:
        v_bolt_b = []
        v_bolt_t = []
        for j in range(6):
            ja = j * (2.0 * math.pi / 6.0)
            v_bolt_b.append(bm.verts.new(Vector((bx + math.cos(ja) * 0.004, th, bz + math.sin(ja) * 0.004))))
            v_bolt_t.append(bm.verts.new(Vector((bx + math.cos(ja) * 0.004, th + 0.004, bz + math.sin(ja) * 0.004))))
        bm.verts.ensure_lookup_table()
        for j in range(6):
            j_next = (j + 1) % 6
            f = bm.faces.new((v_bolt_b[j], v_bolt_b[j_next], v_bolt_t[j_next], v_bolt_t[j]))
            f.smooth = False; f.material_index = 0
            for loop in f.loops: loop[uv_layer].uv = (0.38, 0.80)
        f_bcap = bm.faces.new(reversed(v_bolt_t))
        f_bcap.smooth = False; f_bcap.material_index = 0
        for loop in f_bcap.loops: loop[uv_layer].uv = (0.38, 0.80)

    # Knuckle boss stalk from Y=0.010 to Y=0.055 (radius 0.015, 8 radial)
    n_st = 8
    r_st = 0.015
    v_st0 = []
    v_st1 = []
    for i in range(n_st):
        ang = i * (2.0 * math.pi / n_st)
        cx = math.cos(ang) * r_st
        cz = math.sin(ang) * r_st
        v_st0.append(bm.verts.new(Vector((cx, 0.010, cz))))
        v_st1.append(bm.verts.new(Vector((cx, 0.055, cz))))
    bm.verts.ensure_lookup_table()

    for i in range(n_st):
        i_next = (i + 1) % n_st
        f = bm.faces.new((v_st0[i], v_st0[i_next], v_st1[i_next], v_st1[i]))
        f.smooth = True; f.material_index = 0
        u0 = 0.10 + (i / float(n_st)) * 0.20
        u1 = 0.10 + ((i + 1) / float(n_st)) * 0.20
        for loop in f.loops: loop[uv_layer].uv = (u0, 0.25)

    # Knuckle Joint Drum at Y=0.070 (radius 0.016, X: -0.018 to +0.018, 10 radial)
    n_k = 10
    r_k = 0.016
    y_k = 0.070
    k_l = []
    k_r = []
    for i in range(n_k):
        ang = i * (2.0 * math.pi / n_k)
        cy = y_k + math.cos(ang) * r_k
        cz = math.sin(ang) * r_k
        k_l.append(bm.verts.new(Vector((-0.018, cy, cz))))
        k_r.append(bm.verts.new(Vector(( 0.018, cy, cz))))
    bm.verts.ensure_lookup_table()

    for i in range(n_k):
        i_next = (i + 1) % n_k
        f = bm.faces.new((k_l[i], k_l[i_next], k_r[i_next], k_r[i]))
        f.smooth = True; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.35, 0.35)

    f_kl = bm.faces.new(k_l)
    f_kl.smooth = False; f_kl.material_index = 0
    for loop in f_kl.loops: loop[uv_layer].uv = (0.35, 0.35)

    f_kr = bm.faces.new(reversed(k_r))
    f_kr.smooth = False; f_kr.material_index = 0
    for loop in f_kr.loops: loop[uv_layer].uv = (0.35, 0.35)

    # Transverse M6 Hex Clamp Bolt on +X (X: 0.018 to 0.024, r=0.007)
    v_hex_b = []
    v_hex_t = []
    for j in range(6):
        ja = j * (2.0 * math.pi / 6.0)
        hy = y_k + math.cos(ja) * 0.007
        hz = math.sin(ja) * 0.007
        v_hex_b.append(bm.verts.new(Vector((0.018, hy, hz))))
        v_hex_t.append(bm.verts.new(Vector((0.025, hy, hz))))
    bm.verts.ensure_lookup_table()

    for j in range(6):
        j_next = (j + 1) % 6
        f = bm.faces.new((v_hex_b[j], v_hex_b[j_next], v_hex_t[j_next], v_hex_t[j]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.38, 0.80)

    f_hex_cap = bm.faces.new(reversed(v_hex_t))
    f_hex_cap.smooth = False; f_hex_cap.material_index = 0
    for loop in f_hex_cap.loops: loop[uv_layer].uv = (0.38, 0.80)

    # Hex Locking Nut on -X (X: -0.018 to -0.024, r=0.0065)
    v_nut_b = []
    v_nut_t = []
    for j in range(6):
        ja = j * (2.0 * math.pi / 6.0)
        hy = y_k + math.cos(ja) * 0.0065
        hz = math.sin(ja) * 0.0065
        v_nut_b.append(bm.verts.new(Vector((-0.018, hy, hz))))
        v_nut_t.append(bm.verts.new(Vector((-0.024, hy, hz))))
    bm.verts.ensure_lookup_table()

    for j in range(6):
        j_next = (j + 1) % 6
        f = bm.faces.new((v_nut_t[j], v_nut_t[j_next], v_nut_b[j_next], v_nut_b[j]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.38, 0.80)
    f_nut_cap = bm.faces.new(v_nut_t)
    f_nut_cap.smooth = False; f_nut_cap.material_index = 0
    for loop in f_nut_cap.loops: loop[uv_layer].uv = (0.38, 0.80)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Mount_Plate")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Mount_Plate", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_camera_housing(mats):
    """
    Camera_Housing: Long telephoto camera body with integrated sunshield hood,
    3D top slide rail with knurled thumbscrew locking knob, and rear PG-16 gland + BNC port.
    In Aim_Pivot local space (knuckle at 0, 0, 0):
      Optical axis centered at Z=0.080, parallel to Y.
      Body radius: r=0.035m, 16 radial segments, length Y=-0.020 to 0.180.
      Sunshield visor overhangs front by 40mm (to Y=0.220).
    Slot 0: M_Security_Atlas.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16
    zc = 0.080 # Camera centerline Z

    # 1. Lower mounting bracket cradle connecting knuckle (0,0,0) to body underside (Z=0.045)
    bw, bh = 0.014, 0.012
    v_cr0 = [
        bm.verts.new(Vector((-bw, -bh, -0.005))),
        bm.verts.new(Vector(( bw, -bh, -0.005))),
        bm.verts.new(Vector(( bw,  bh, -0.005))),
        bm.verts.new(Vector((-bw,  bh, -0.005)))
    ]
    v_cr1 = [
        bm.verts.new(Vector((-0.018, 0.010, 0.045))),
        bm.verts.new(Vector(( 0.018, 0.010, 0.045))),
        bm.verts.new(Vector(( 0.018, 0.090, 0.045))),
        bm.verts.new(Vector((-0.018, 0.090, 0.045)))
    ]
    bm.verts.ensure_lookup_table()
    for i in range(4):
        i_next = (i + 1) % 4
        f = bm.faces.new((v_cr0[i], v_cr0[i_next], v_cr1[i_next], v_cr1[i]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.40)

    # 2. Main Cylindrical Telephoto Body (16 radial segments)
    body_stations = [
        (-0.020, 0.015),
        ( 0.000, 0.026),
        ( 0.010, 0.035),
        ( 0.120, 0.035),
        ( 0.180, 0.035),
        ( 0.180, 0.019)
    ]
    rings = []
    for y_pos, r_rad in body_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vz = zc + math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, y_pos, vz))))
        rings.append(ring)
    bm.verts.ensure_lookup_table()

    # Rear cap at station 0
    f_rear = bm.faces.new(rings[0])
    f_rear.smooth = False; f_rear.material_index = 0
    for loop in f_rear.loops: loop[uv_layer].uv = (0.90, 0.25)

    # Cylindrical quads between stations with continuous UV mapping
    for s in range(len(body_stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vb, vc, vd))
            f.smooth = True if s < 4 else False
            f.material_index = 0

            # Side panels map to Quadrant 1 (ANPR markings & barcode)
            u0 = 0.05 + (i / float(n_radial)) * 0.40
            u1 = 0.05 + ((i + 1) / float(n_radial)) * 0.40
            v0 = 0.55 + (s / float(len(body_stations) - 1)) * 0.38
            v1 = 0.55 + ((s + 1) / float(len(body_stations) - 1)) * 0.38
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    # 3. Extended All-Weather Sunshield Hood (Visor)
    n_hood = 10
    start_ang = -math.radians(20)
    end_ang = math.radians(200)
    hood_angles = [start_ang + k * (end_ang - start_ang) / n_hood for k in range(n_hood + 1)]

    h_out_b = []
    h_out_f = []
    h_in_b = []
    h_in_f = []
    for ang in hood_angles:
        cx = math.cos(ang)
        cz = math.sin(ang)
        h_out_b.append(bm.verts.new(Vector((cx * 0.042, 0.015, zc + cz * 0.042))))
        h_in_b.append(bm.verts.new(Vector((cx * 0.038, 0.015, zc + cz * 0.038))))
        h_out_f.append(bm.verts.new(Vector((cx * 0.045, 0.220, zc + cz * 0.045))))
        h_in_f.append(bm.verts.new(Vector((cx * 0.040, 0.220, zc + cz * 0.040))))
    bm.verts.ensure_lookup_table()

    # Outer hood quads
    for k in range(n_hood):
        f = bm.faces.new((h_out_b[k], h_out_f[k], h_out_f[k + 1], h_out_b[k + 1]))
        f.smooth = True; f.material_index = 0
        u0 = 0.52 + (k / float(n_hood)) * 0.44
        u1 = 0.52 + ((k + 1) / float(n_hood)) * 0.44
        for loop in f.loops:
            if loop.vert == h_out_b[k]: loop[uv_layer].uv = (u0, 0.85)
            elif loop.vert == h_out_b[k + 1]: loop[uv_layer].uv = (u1, 0.85)
            elif loop.vert == h_out_f[k + 1]: loop[uv_layer].uv = (u1, 0.98)
            elif loop.vert == h_out_f[k]: loop[uv_layer].uv = (u0, 0.98)

    # Inner hood quads (anti-glare matte coating)
    for k in range(n_hood):
        f = bm.faces.new((h_in_b[k], h_in_b[k + 1], h_in_f[k + 1], h_in_f[k]))
        f.smooth = True; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.75, 0.65)

    # Front rim
    for k in range(n_hood):
        f = bm.faces.new((h_out_f[k], h_in_f[k], h_in_f[k + 1], h_out_f[k + 1]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.75, 0.52)

    # 4. 3D Top Slide Rail with Locking Thumbscrew Knob
    rw = 0.006
    rh0 = zc + 0.042
    rh1 = zc + 0.047
    v_rail = [
        bm.verts.new(Vector((-rw, 0.040, rh0))),
        bm.verts.new(Vector(( rw, 0.040, rh0))),
        bm.verts.new(Vector(( rw, 0.160, rh0))),
        bm.verts.new(Vector((-rw, 0.160, rh0))),
        bm.verts.new(Vector((-rw, 0.040, rh1))),
        bm.verts.new(Vector(( rw, 0.040, rh1))),
        bm.verts.new(Vector(( rw, 0.160, rh1))),
        bm.verts.new(Vector((-rw, 0.160, rh1)))
    ]
    bm.verts.ensure_lookup_table()
    # Rail top & sides
    f_rt = bm.faces.new((v_rail[4], v_rail[7], v_rail[6], v_rail[5]))
    f_rt.smooth = False; f_rt.material_index = 0
    for loop in f_rt.loops: loop[uv_layer].uv = (0.15, 0.85)

    f_rl = bm.faces.new((v_rail[0], v_rail[3], v_rail[7], v_rail[4]))
    f_rr = bm.faces.new((v_rail[1], v_rail[5], v_rail[6], v_rail[2]))
    f_rl.smooth = False; f_rr.smooth = False
    f_rl.material_index = 0; f_rr.material_index = 0
    for loop in f_rl.loops: loop[uv_layer].uv = (0.15, 0.85)
    for loop in f_rr.loops: loop[uv_layer].uv = (0.15, 0.85)

    # Thumbscrew knob at (0, 0.100, rh1)
    n_ts = 8
    r_ts = 0.0055
    y_ts = 0.100
    v_ts_b = []
    v_ts_t = []
    for j in range(n_ts):
        ja = j * (2.0 * math.pi / n_ts)
        v_ts_b.append(bm.verts.new(Vector((math.cos(ja) * r_ts, y_ts + math.sin(ja) * r_ts, rh1))))
        v_ts_t.append(bm.verts.new(Vector((math.cos(ja) * r_ts, y_ts + math.sin(ja) * r_ts, rh1 + 0.005))))
    bm.verts.ensure_lookup_table()
    for j in range(n_ts):
        j_next = (j + 1) % n_ts
        f = bm.faces.new((v_ts_b[j], v_ts_b[j_next], v_ts_t[j_next], v_ts_t[j]))
        f.smooth = True; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.75, 0.10)
    f_tscap = bm.faces.new(reversed(v_ts_t))
    f_tscap.smooth = False; f_tscap.material_index = 0
    for loop in f_tscap.loops: loop[uv_layer].uv = (0.75, 0.10)

    # 5. Rear Cable Gland (PG-16) at (0, -0.020, zc)
    n_gl = 8
    r_gl = 0.012
    v_gl0 = []
    v_gl1 = []
    for i in range(n_gl):
        ang = i * (2.0 * math.pi / n_gl)
        v_gl0.append(bm.verts.new(Vector((math.cos(ang) * r_gl, -0.020, zc + math.sin(ang) * r_gl))))
        v_gl1.append(bm.verts.new(Vector((math.cos(ang) * r_gl, -0.038, zc + math.sin(ang) * r_gl))))
    bm.verts.ensure_lookup_table()

    for i in range(n_gl):
        i_next = (i + 1) % n_gl
        f = bm.faces.new((v_gl0[i], v_gl1[i], v_gl1[i_next], v_gl0[i_next]))
        f.smooth = True; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.90, 0.25)
    f_glcap = bm.faces.new(reversed(v_gl1))
    f_glcap.smooth = False; f_glcap.material_index = 0
    for loop in f_glcap.loops: loop[uv_layer].uv = (0.90, 0.25)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Camera_Housing")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Camera_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_glass(mats):
    """
    Lens_Glass: Recessed optical telephoto lens element at aperture center (Y=0.181, r=0.019m).
    14-radial smooth convex optical element, normals pointing forward in +Y.
    Slot 1: M_Lens_Glass.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 14
    zc = 0.080
    r_lens = 0.019

    v_ring = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        cx = math.cos(ang) * r_lens
        cz = math.sin(ang) * r_lens
        v_ring.append(bm.verts.new(Vector((cx, 0.181, zc + cz))))

    v_apex = bm.verts.new(Vector((0.0, 0.186, zc)))
    bm.verts.ensure_lookup_table()

    cu, cv = 0.75, 0.41
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_ring[i], v_apex, v_ring[i_next]))
        f.smooth = True
        f.material_index = 1
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
        p.material_index = 1

    obj = bpy.data.objects.new("Lens_Glass", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_ir_illuminator(mats):
    """
    IR_Illuminator: High-power pulsed IR strobe illuminator bank mounted under the camera.
    Includes rear cooling heatsink fins, solid mounting clamp, and front 4x4 matrix faceplate.
    Position in Aim_Pivot local space:
      Centered at (0, 0.085, 0.020).
      Dimensions: width X: ±0.038 (76mm), height Z: ±0.020 (40mm), length Y: 0.020 to 0.150.
    Slot 2: M_Emission.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    wx = 0.038
    wz = 0.020
    zc_ir = 0.020
    y_rear = 0.020
    y_front = 0.150

    ch = 0.006
    ir_prof = [
        (-wx + ch, zc_ir - wz), (wx - ch, zc_ir - wz),
        (wx, zc_ir - wz + ch), (wx, zc_ir + wz - ch),
        (wx - ch, zc_ir + wz), (-wx + ch, zc_ir + wz),
        (-wx, zc_ir + wz - ch), (-wx, zc_ir - wz + ch)
    ]

    v_rear = [bm.verts.new(Vector((x, y_rear, z))) for x, z in ir_prof]
    v_front = [bm.verts.new(Vector((x, y_front, z))) for x, z in ir_prof]
    bm.verts.ensure_lookup_table()

    # Rear face
    f_r = bm.faces.new(v_rear)
    f_r.smooth = False; f_r.material_index = 0
    for loop in f_r.loops: loop[uv_layer].uv = (0.20, 0.80)

    # Perimeter body quads
    n_p = len(ir_prof)
    for i in range(n_p):
        i_next = (i + 1) % n_p
        f = bm.faces.new((v_rear[i], v_rear[i_next], v_front[i_next], v_front[i]))
        f.smooth = False; f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.80)

    # Rear Cooling Fins (3 horizontal rib fins on rear face Y=0.020 extending to Y=0.012)
    for fin_z in [zc_ir - 0.010, zc_ir, zc_ir + 0.010]:
        v_rf = [
            bm.verts.new(Vector((-wx + ch, y_rear, fin_z - 0.002))),
            bm.verts.new(Vector(( wx - ch, y_rear, fin_z - 0.002))),
            bm.verts.new(Vector(( wx - ch, y_rear - 0.007, fin_z - 0.002))),
            bm.verts.new(Vector((-wx + ch, y_rear - 0.007, fin_z - 0.002))),
            bm.verts.new(Vector((-wx + ch, y_rear, fin_z + 0.002))),
            bm.verts.new(Vector(( wx - ch, y_rear, fin_z + 0.002))),
            bm.verts.new(Vector(( wx - ch, y_rear - 0.007, fin_z + 0.002))),
            bm.verts.new(Vector((-wx + ch, y_rear - 0.007, fin_z + 0.002)))
        ]
        bm.verts.ensure_lookup_table()
        f_fin_b = bm.faces.new((v_rf[3], v_rf[2], v_rf[6], v_rf[7]))
        f_fin_b.smooth = False; f_fin_b.material_index = 0
        for loop in f_fin_b.loops: loop[uv_layer].uv = (0.20, 0.80)

    # Front Faceplate with 16 High-Power IR LED Matrix
    f_f = bm.faces.new(reversed(v_front))
    f_f.smooth = False
    f_f.material_index = 2

    cu, cv = 0.75, 0.25
    for loop in f_f.loops:
        v = loop.vert
        loop[uv_layer].uv = (cu + (v.co.x / wx) * 0.20, cv + ((v.co.z - zc_ir) / wz) * 0.18)

    bm.normal_update()
    mesh = bpy.data.meshes.new("IR_Illuminator")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        if p.normal.y > 0.5:
            p.material_index = 2
        else:
            p.material_index = 0

    obj = bpy.data.objects.new("IR_Illuminator", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_asset():
    """Build full SEC_Camera_LPR hierarchy."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mats = create_materials(atlas_path)

    # 1. Root Empty: SEC_Camera_LPR at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Camera_LPR", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 2. Mount_Plate (Child of Root)
    mount_plate = build_mount_plate(mats)
    mount_plate.parent = root

    # 3. Aim_Pivot (Empty at knuckle joint: (0, 0.070, 0))
    aim_pivot = bpy.data.objects.new("Aim_Pivot", None)
    aim_pivot.empty_display_type = 'ARROWS'
    aim_pivot.empty_display_size = 0.04
    aim_pivot.location = (0.0, 0.070, 0.0)
    bpy.context.collection.objects.link(aim_pivot)
    aim_pivot.parent = root
    aim_pivot["limit_rot_x_min"] = -25.0
    aim_pivot["limit_rot_x_max"] = 25.0
    aim_pivot["limit_rot_z_min"] = -40.0
    aim_pivot["limit_rot_z_max"] = 40.0

    # 4. Camera_Housing (Child of Aim_Pivot)
    housing = build_camera_housing(mats)
    housing.parent = aim_pivot

    # 5. Lens_Glass (Child of Camera_Housing)
    lens = build_lens_glass(mats)
    lens.parent = housing

    # 6. IR_Illuminator (Child of Aim_Pivot)
    ir_ill = build_ir_illuminator(mats)
    ir_ill.parent = aim_pivot

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Camera_LPR.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Camera_LPR.fbx")
    export_fbx(root, [mount_plate, housing, lens, ir_ill], aim_pivot, fbx_path)

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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 29) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Camera_LPR")
    assert root is not None, "FAIL: Root object 'SEC_Camera_LPR' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    aim_pivot = bpy.data.objects.get("Aim_Pivot")
    assert aim_pivot is not None, "FAIL: Aim_Pivot missing!"
    assert aim_pivot.parent == root, "FAIL: Aim_Pivot parent != root!"
    assert aim_pivot.type == 'EMPTY', f"FAIL: Aim_Pivot is type {aim_pivot.type}, expected EMPTY!"

    expected_meshes = {
        "Mount_Plate",
        "Camera_Housing",
        "Lens_Glass",
        "IR_Illuminator"
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

    plate = bpy.data.objects.get("Mount_Plate")
    housing = bpy.data.objects.get("Camera_Housing")
    lens = bpy.data.objects.get("Lens_Glass")
    ir_ill = bpy.data.objects.get("IR_Illuminator")

    assert plate.parent == root, "FAIL: Mount_Plate parent != root!"
    assert housing.parent == aim_pivot, "FAIL: Camera_Housing parent != aim_pivot!"
    assert lens.parent == housing, "FAIL: Lens_Glass parent != housing!"
    assert ir_ill.parent == aim_pivot, "FAIL: IR_Illuminator parent != aim_pivot!"

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 600, f"FAIL: Total triangles {total_tris} exceeds 600 budget!"
    print("[PASS] Triangle count verified strictly (<= 600)!")
    print("[PASS] Full parent-child hierarchy strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Camera_LPR"] = {
        "asset_name": "SEC_Camera_LPR",
        "fbx_path": "exports/SEC_Camera_LPR.fbx",
        "blend_path": "exports/SEC_Camera_LPR.blend",
        "tris_count": total_tris,
        "mesh_count": len(found_meshes),
        "empty_count": 2,
        "materials": ["M_Security_Atlas", "M_Lens_Glass", "M_Emission"],
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
