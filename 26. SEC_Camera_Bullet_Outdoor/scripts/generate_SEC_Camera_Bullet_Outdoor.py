import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Euler

def reset_scene():
    """Clear all objects, meshes, materials, and textures."""
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
    Slot 2: M_Emission
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

    # 1. M_Lens_Glass (Rich multi-coated optical crystal glass)
    mat_glass = bpy.data.materials.new("M_Lens_Glass")
    mat_glass.use_nodes = True
    gnodes = mat_glass.node_tree.nodes
    glinks = mat_glass.node_tree.links
    gnodes.clear()

    g_out = gnodes.new("ShaderNodeOutputMaterial")
    g_bsdf = gnodes.new("ShaderNodeBsdfPrincipled")
    g_bsdf.inputs['Base Color'].default_value = (0.08, 0.14, 0.20, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.05
    g_bsdf.inputs['Metallic'].default_value = 0.05
    g_bsdf.inputs['Specular IOR Level'].default_value = 0.95
    if 'Transmission Weight' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission Weight'].default_value = 0.40
    elif 'Transmission' in g_bsdf.inputs:
        g_bsdf.inputs['Transmission'].default_value = 0.40
    if 'IOR' in g_bsdf.inputs:
        g_bsdf.inputs['IOR'].default_value = 1.54
    glinks.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])

    # 2. M_Emission (850nm infrared array illuminator)
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
        tex = enodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(atlas_path)
        elinks.new(tex.outputs['Color'], e_bsdf.inputs['Base Color'])
        elinks.new(tex.outputs['Color'], e_bsdf.inputs['Emission Color'])
        if 'Emission Strength' in e_bsdf.inputs:
            e_bsdf.inputs['Emission Strength'].default_value = 3.5
    else:
        e_bsdf.inputs['Base Color'].default_value = (0.12, 0.02, 0.02, 1.0)
        if 'Emission Color' in e_bsdf.inputs:
            e_bsdf.inputs['Emission Color'].default_value = (0.95, 0.20, 0.15, 1.0)
            e_bsdf.inputs['Emission Strength'].default_value = 4.0
    elinks.new(e_bsdf.outputs['BSDF'], e_out.inputs['Surface'])

    return [mat_atlas, mat_glass, mat_emission]

def assign_material_slots(obj, mats):
    """Ensure obj has exactly 3 material slots in standard order."""
    obj.data.materials.clear()
    for m in mats:
        obj.data.materials.append(m)

def build_wall_mount_plate(mats):
    """
    Wall mounting plate at (0, 0, 0), normal pointing in +Y.
    Diameter: 90mm (r=0.045m), thickness: 12mm (Y: 0.0 to 0.012).
    Includes central bracket socket boss extending to Y=0.048 and 3 countersunk hex screws.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 14

    # 1. Base Flange: Y=0.000 to Y=0.012 (r=0.045 to 0.042 chamfer)
    r_outer = 0.045
    r_chamfer = 0.042
    r_boss = 0.016 # central socket boss
    r_hole = 0.008 # central wire passage

    # Stations along Y:
    # 0: Y=0.000, r=0.045 (wall contact)
    # 1: Y=0.008, r=0.045 (outer cylindrical wall)
    # 2: Y=0.012, r=0.042 (chamfered front edge)
    # 3: Y=0.012, r=0.016 (inner face to boss)
    # 4: Y=0.048, r=0.016 (boss tip socket reaching knuckle)
    # 5: Y=0.048, r=0.008 (boss top wire hole)

    v_st0 = []
    v_st1 = []
    v_st2 = []
    v_boss_base = []
    v_boss_top = []
    v_boss_hole = []

    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        cx = math.cos(ang)
        cz = math.sin(ang)
        v_st0.append(bm.verts.new(Vector((cx * r_outer, 0.000, cz * r_outer))))
        v_st1.append(bm.verts.new(Vector((cx * r_outer, 0.008, cz * r_outer))))
        v_st2.append(bm.verts.new(Vector((cx * r_chamfer, 0.012, cz * r_chamfer))))
        v_boss_base.append(bm.verts.new(Vector((cx * r_boss, 0.012, cz * r_boss))))
        v_boss_top.append(bm.verts.new(Vector((cx * r_boss, 0.048, cz * r_boss))))
        v_boss_hole.append(bm.verts.new(Vector((cx * r_hole, 0.048, cz * r_hole))))

    bm.verts.ensure_lookup_table()

    # Outer wall quads (st0 to st1)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_st0[i], v_st0[i_next], v_st1[i_next], v_st1[i]))
        f.smooth = True
        f.material_index = 0
        u0 = (i / float(n_radial)) * 0.20
        u1 = ((i + 1) / float(n_radial)) * 0.20
        for loop in f.loops:
            v_val = 0.05 if loop.vert in (v_st0[i], v_st0[i_next]) else 0.12
            loop[uv_layer].uv = (u0 if loop.vert in (v_st0[i], v_st1[i]) else u1, v_val)

    # Chamfer quads (st1 to st2)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_st1[i], v_st1[i_next], v_st2[i_next], v_st2[i]))
        f.smooth = False
        f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.20, 0.20)

    # Front flange face between st2 and boss_base
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_st2[i], v_st2[i_next], v_boss_base[i_next], v_boss_base[i]))
        f.smooth = False
        f.material_index = 0
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        cu, cv = 0.25, 0.25
        for loop in f.loops:
            if loop.vert == v_st2[i]: loop[uv_layer].uv = (cu + 0.20 * math.cos(ang0), cv + 0.20 * math.sin(ang0))
            elif loop.vert == v_st2[i_next]: loop[uv_layer].uv = (cu + 0.20 * math.cos(ang1), cv + 0.20 * math.sin(ang1))
            elif loop.vert == v_boss_base[i_next]: loop[uv_layer].uv = (cu + 0.07 * math.cos(ang1), cv + 0.07 * math.sin(ang1))
            elif loop.vert == v_boss_base[i]: loop[uv_layer].uv = (cu + 0.07 * math.cos(ang0), cv + 0.07 * math.sin(ang0))

    # Socket Boss cylinder (boss_base to boss_top)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_boss_base[i], v_boss_base[i_next], v_boss_top[i_next], v_boss_top[i]))
        f.smooth = True
        f.material_index = 0
        u0 = 0.20 + (i / float(n_radial)) * 0.10
        u1 = 0.20 + ((i + 1) / float(n_radial)) * 0.10
        for loop in f.loops: loop[uv_layer].uv = (u0, 0.10)

    # 3 Countersunk Screws (6-sided prisms)
    for s_idx in range(3):
        s_ang = s_idx * (2.0 * math.pi / 3.0) + math.pi / 6.0
        s_cx = math.cos(s_ang) * 0.030
        s_cz = math.sin(s_ang) * 0.030
        s_r = 0.0035
        v_sc = []
        for j in range(6):
            ja = j * (2.0 * math.pi / 6.0)
            v_sc.append(bm.verts.new(Vector((s_cx + math.cos(ja) * s_r, 0.0125, s_cz + math.sin(ja) * s_r))))
        bm.verts.ensure_lookup_table()
        f_sc = bm.faces.new(v_sc)
        f_sc.smooth = False
        f_sc.material_index = 0
        for loop in f_sc.loops:
            loop[uv_layer].uv = (0.25 + 0.127 * math.cos(s_ang), 0.25 + 0.127 * math.sin(s_ang))

    bm.normal_update()
    mesh = bpy.data.meshes.new("Wall_Mount_Plate")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Wall_Mount_Plate", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_bracket(mats):
    """
    Articulated knuckle arm linking socket boss to camera body cradle.
    Origin at Aim_Pivot: (0.0, 0.055, 0.0).
    In Aim_Pivot local coordinates:
      - Knuckle joint center at (0, 0, 0).
      - Lower knuckle ball mates seamlessly into boss socket (Y: -0.010 to 0.0).
      - Transverse M6 hex clamp bolt at knuckle (+X).
      - Angled rigid arm extending up and forward to cradle foot at (0, 0.060, 0.032).
      - Saddle cradle foot supporting Camera_Body underside.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    # 1. Knuckle Joint Drum (axis along X: from X=-0.016 to +0.016, radius=0.015m, 12 radial)
    n_k = 12
    r_k = 0.015
    k_l = []
    k_r = []
    for i in range(n_k):
        ang = i * (2.0 * math.pi / n_k)
        cy = math.cos(ang) * r_k
        cz = math.sin(ang) * r_k
        k_l.append(bm.verts.new(Vector((-0.016, cy, cz))))
        k_r.append(bm.verts.new(Vector(( 0.016, cy, cz))))

    bm.verts.ensure_lookup_table()
    for i in range(n_k):
        i_next = (i + 1) % n_k
        f = bm.faces.new((k_l[i], k_l[i_next], k_r[i_next], k_r[i]))
        f.smooth = True
        f.material_index = 0
        u0 = 0.30 + (i / float(n_k)) * 0.15
        u1 = 0.30 + ((i + 1) / float(n_k)) * 0.15
        for loop in f.loops: loop[uv_layer].uv = (u0, 0.30)

    # Knuckle side caps: Plain cap on left, Hex clamp bolt on right
    f_l = bm.faces.new(k_l)
    f_l.smooth = False
    f_l.material_index = 0
    for loop in f_l.loops: loop[uv_layer].uv = (0.35, 0.35)

    f_r = bm.faces.new(reversed(k_r))
    f_r.smooth = False
    f_r.material_index = 0
    for loop in f_r.loops: loop[uv_layer].uv = (0.40, 0.40)

    # 3D M6 Hex Locking Bolt on right side (+X = 0.016 to 0.022, r=0.007)
    v_hex_bot = []
    v_hex_top = []
    for j in range(6):
        ja = j * (2.0 * math.pi / 6.0)
        hy = math.cos(ja) * 0.007
        hz = math.sin(ja) * 0.007
        v_hex_bot.append(bm.verts.new(Vector((0.016, hy, hz))))
        v_hex_top.append(bm.verts.new(Vector((0.022, hy, hz))))

    bm.verts.ensure_lookup_table()
    for j in range(6):
        j_next = (j + 1) % 6
        f = bm.faces.new((v_hex_bot[j], v_hex_bot[j_next], v_hex_top[j_next], v_hex_top[j]))
        f.smooth = False
        f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.38, 0.80)

    f_hex_cap = bm.faces.new(reversed(v_hex_top))
    f_hex_cap.smooth = False
    f_hex_cap.material_index = 0
    for loop in f_hex_cap.loops: loop[uv_layer].uv = (0.38, 0.80)

    # 2. Angled Rigid Arm extending from knuckle (0, 0, 0) forward-up to cradle foot (0, 0.055, 0.028)
    p_start = Vector((0.0, 0.005, 0.005))
    p_end = Vector((0.0, 0.055, 0.028))
    t_arm = (p_end - p_start).normalized()
    n_arm = Vector((1.0, 0.0, 0.0))
    b_arm = t_arm.cross(n_arm).normalized()

    w_half = 0.011
    h_half = 0.007
    corners = [
        Vector((-w_half, -h_half)),
        Vector(( w_half, -h_half)),
        Vector(( w_half,  h_half)),
        Vector((-w_half,  h_half))
    ]

    v_a0 = [bm.verts.new(p_start + n_arm * c.x + b_arm * c.y) for c in corners]
    v_a1 = [bm.verts.new(p_end + n_arm * c.x + b_arm * c.y) for c in corners]
    bm.verts.ensure_lookup_table()

    for i in range(4):
        i_next = (i + 1) % 4
        f = bm.faces.new((v_a0[i], v_a0[i_next], v_a1[i_next], v_a1[i]))
        f.smooth = False
        f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.25, 0.40)

    # 3. Saddle Cradle Foot (mounting pad under camera body at Y=0.035 to 0.075, Z=0.030)
    cradle_corners = [
        Vector((-0.016, 0.035, 0.027)),
        Vector(( 0.016, 0.035, 0.027)),
        Vector(( 0.016, 0.075, 0.027)),
        Vector((-0.016, 0.075, 0.027)),
        Vector((-0.016, 0.035, 0.034)),
        Vector(( 0.016, 0.035, 0.034)),
        Vector(( 0.016, 0.075, 0.034)),
        Vector((-0.016, 0.075, 0.034))
    ]
    v_cr = [bm.verts.new(c) for c in cradle_corners]
    bm.verts.ensure_lookup_table()

    cr_faces = [
        (v_cr[0], v_cr[1], v_cr[2], v_cr[3]), # bottom
        (v_cr[4], v_cr[7], v_cr[6], v_cr[5]), # top
        (v_cr[0], v_cr[4], v_cr[5], v_cr[1]), # front
        (v_cr[2], v_cr[6], v_cr[7], v_cr[3]), # rear
        (v_cr[0], v_cr[3], v_cr[7], v_cr[4]), # left
        (v_cr[1], v_cr[5], v_cr[6], v_cr[2])  # right
    ]
    for face_verts in cr_faces:
        f = bm.faces.new(face_verts)
        f.smooth = False
        f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.22, 0.35)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Bracket")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Bracket", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_camera_body(mats):
    """
    Camera body with integrated double-walled sunshield hood and rear PG-9 cable gland.
    In Aim_Pivot local space:
      Cylinder axis centered at Z=0.065, parallel to Y-axis.
      Radius: r=0.034m (68mm diameter), 16 radial segments!
      Length: Y=-0.015 (rear gland) to Y=0.145 (front lens bezel).
      Sunshield: Overhangs front by 35mm (to Y=0.180), solid double wall.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16
    zc = 0.065 # Camera centerline Z

    # 1. Main Cylindrical Body
    # Stations along Y:
    # 0: Y=-0.015, r=0.011 (rear cable gland entry)
    # 1: Y= 0.000, r=0.024 (rear taper step)
    # 2: Y= 0.010, r=0.034 (main body rear)
    # 3: Y= 0.080, r=0.034 (middle body)
    # 4: Y= 0.145, r=0.034 (front body rim)
    # 5: Y= 0.145, r=0.031 (recessed bezel step)
    body_stations = [
        (-0.015, 0.011),
        ( 0.000, 0.024),
        ( 0.010, 0.034),
        ( 0.080, 0.034),
        ( 0.145, 0.034),
        ( 0.145, 0.031)
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

    # Rear cap at station 0 (pointing in -Y)
    f_rear = bm.faces.new(rings[0])
    f_rear.smooth = False
    f_rear.material_index = 0
    for loop in f_rear.loops: loop[uv_layer].uv = (0.90, 0.25) # knurled gland zone

    # Cylindrical quads between stations (radially outward normals)
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
            f.smooth = True
            f.material_index = 0

            u0 = (i / float(n_radial)) * 0.48
            u1 = ((i + 1) / float(n_radial)) * 0.48
            v0 = 0.55 + (s / float(len(body_stations) - 1)) * 0.38
            v1 = 0.55 + ((s + 1) / float(len(body_stations) - 1)) * 0.38

            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    # 2. Solid Double-Walled Sunshield Hood (Visor)
    # Arches over top from angle ~ -18 deg to 198 deg (10 segments over 216 degrees)
    # Extends from Y=0.015 to Y=0.180 (overhangs lens bezel by 35mm!)
    # Outer radius: r=0.041 to 0.043; inner radius: r=0.037 to 0.039 (solid 3.5mm wall!)
    n_hood_seg = 10
    start_ang = -math.radians(18)
    end_ang = math.radians(198)
    hood_angles = [start_ang + k * (end_ang - start_ang) / n_hood_seg for k in range(n_hood_seg + 1)]

    hood_out_back = []
    hood_out_front = []
    hood_in_back = []
    hood_in_front = []

    for ang in hood_angles:
        cx = math.cos(ang)
        cz = math.sin(ang)

        # Back station (Y=0.015)
        hood_out_back.append(bm.verts.new(Vector((cx * 0.041, 0.015, zc + cz * 0.041))))
        hood_in_back.append(bm.verts.new(Vector((cx * 0.037, 0.015, zc + cz * 0.037))))

        # Front station (Y=0.180, forward flare)
        hood_out_front.append(bm.verts.new(Vector((cx * 0.043, 0.180, zc + cz * 0.043))))
        hood_in_front.append(bm.verts.new(Vector((cx * 0.039, 0.180, zc + cz * 0.039))))

    bm.verts.ensure_lookup_table()

    # Outer hood quads (normals pointing OUTWARD)
    for k in range(n_hood_seg):
        va = hood_out_back[k]
        vb = hood_out_back[k + 1]
        vc = hood_out_front[k + 1]
        vd = hood_out_front[k]
        f = bm.faces.new((va, vd, vc, vb))
        f.smooth = True
        f.material_index = 0
        u0 = 0.52 + (k / float(n_hood_seg)) * 0.44
        u1 = 0.52 + ((k + 1) / float(n_hood_seg)) * 0.44
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.85)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.85)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.98)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.98)

    # Inner hood quads (anti-glare matte coating, normals pointing INWARD)
    for k in range(n_hood_seg):
        va = hood_in_back[k]
        vb = hood_in_back[k + 1]
        vc = hood_in_front[k + 1]
        vd = hood_in_front[k]
        f = bm.faces.new((va, vb, vc, vd))
        f.smooth = True
        f.material_index = 0
        u0 = 0.55 + (k / float(n_hood_seg)) * 0.40
        u1 = 0.55 + ((k + 1) / float(n_hood_seg)) * 0.40
        for loop in f.loops:
            if loop.vert == va: loop[uv_layer].uv = (u0, 0.65)
            elif loop.vert == vb: loop[uv_layer].uv = (u1, 0.65)
            elif loop.vert == vc: loop[uv_layer].uv = (u1, 0.75)
            elif loop.vert == vd: loop[uv_layer].uv = (u0, 0.75)

    # Front rim of sunshield (connecting hood_out_front to hood_in_front, pointing in +Y)
    for k in range(n_hood_seg):
        va = hood_out_front[k]
        vb = hood_out_front[k + 1]
        vc = hood_in_front[k + 1]
        vd = hood_in_front[k]
        f = bm.faces.new((va, vd, vc, vb))
        f.smooth = False
        f.material_index = 0
        for loop in f.loops: loop[uv_layer].uv = (0.75, 0.52) # rubber bumper lip

    # Side wall lips (solid thickness closure at k=0 and k=n_hood_seg)
    f_side0 = bm.faces.new((hood_out_back[0], hood_out_front[0], hood_in_front[0], hood_in_back[0]))
    f_side0.smooth = False
    f_side0.material_index = 0
    for loop in f_side0.loops: loop[uv_layer].uv = (0.75, 0.52)

    f_side1 = bm.faces.new((hood_out_back[-1], hood_in_back[-1], hood_in_front[-1], hood_out_front[-1]))
    f_side1.smooth = False
    f_side1.material_index = 0
    for loop in f_side1.loops: loop[uv_layer].uv = (0.75, 0.52)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Camera_Body")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Camera_Body", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_ir_led_ring(mats):
    """
    IR LED illuminator faceplate at Y=0.146.
    Outer radius: 0.031m, inner aperture: 0.012m.
    Smooth 16-radial annular quad ring, normals pointing FORWARD in +Y.
    Slot 2: M_Emission (dark faceplate with concentric IR LED arrays and optical aperture).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16
    zc = 0.065

    r_outer = 0.031
    r_inner = 0.012
    y_pos = 0.146

    v_out = []
    v_in = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        cx = math.cos(ang)
        cz = math.sin(ang)
        v_out.append(bm.verts.new(Vector((cx * r_outer, y_pos, zc + cz * r_outer))))
        v_in.append(bm.verts.new(Vector((cx * r_inner, y_pos, zc + cz * r_inner))))

    bm.verts.ensure_lookup_table()

    # Annular face quads (pointing forward in +Y)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_out[i], v_in[i], v_in[i_next], v_out[i_next]))
        f.smooth = True
        f.material_index = 2 # Slot 2: M_Emission

        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        cu, cv = 0.75, 0.25 # center of IR LED faceplate in atlas
        for loop in f.loops:
            if loop.vert == v_out[i]: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang0), cv + 0.21 * math.sin(ang0))
            elif loop.vert == v_out[i_next]: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang1), cv + 0.21 * math.sin(ang1))
            elif loop.vert == v_in[i_next]: loop[uv_layer].uv = (cu + 0.065 * math.cos(ang1), cv + 0.065 * math.sin(ang1))
            elif loop.vert == v_in[i]: loop[uv_layer].uv = (cu + 0.065 * math.cos(ang0), cv + 0.065 * math.sin(ang0))

    bm.normal_update()
    mesh = bpy.data.meshes.new("IR_LED_Ring")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.material_index = 2

    obj = bpy.data.objects.new("IR_LED_Ring", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_glass(mats):
    """
    Recessed optical lens element at aperture center (Y=0.146 to 0.149, r=0.012m).
    Smooth 12-radial convex optical element, normals pointing FORWARD in +Y.
    Slot 1: M_Lens_Glass.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 12
    zc = 0.065
    r_lens = 0.012

    base_ring = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        vx = math.cos(ang) * r_lens
        vz = zc + math.sin(ang) * r_lens
        base_ring.append(bm.verts.new(Vector((vx, 0.146, vz))))

    v_apex = bm.verts.new(Vector((0.0, 0.149, zc)))
    bm.verts.ensure_lookup_table()

    # Convex fan faces (pointing forward in +Y)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((base_ring[i], v_apex, base_ring[i_next]))
        f.smooth = True
        f.material_index = 1 # Slot 1: M_Lens_Glass

        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        cu, cv = 0.75, 0.25
        for loop in f.loops:
            if loop.vert == base_ring[i]: loop[uv_layer].uv = (cu + 0.06 * math.cos(ang0), cv + 0.06 * math.sin(ang0))
            elif loop.vert == base_ring[i_next]: loop[uv_layer].uv = (cu + 0.06 * math.cos(ang1), cv + 0.06 * math.sin(ang1))
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

def build_asset():
    """Build the full SEC_Camera_Bullet_Outdoor asset hierarchy."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mats = create_materials(atlas_path)

    # 1. Root Empty: SEC_Camera_Bullet_Outdoor at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Camera_Bullet_Outdoor", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 2. Wall Mount Plate (Child of Root)
    mount_plate = build_wall_mount_plate(mats)
    mount_plate.parent = root

    # 3. Aim_Pivot (Child Empty at knuckle joint center: (0, 0.055, 0))
    aim_pivot = bpy.data.objects.new("Aim_Pivot", None)
    aim_pivot.empty_display_type = 'ARROWS'
    aim_pivot.empty_display_size = 0.04
    aim_pivot.location = (0.0, 0.055, 0.0)
    bpy.context.collection.objects.link(aim_pivot)
    aim_pivot.parent = root
    aim_pivot["limit_rot_x_min"] = -35.0
    aim_pivot["limit_rot_x_max"] = 35.0
    aim_pivot["limit_rot_z_min"] = -35.0
    aim_pivot["limit_rot_z_max"] = 35.0

    # 4. Bracket (Child of Aim_Pivot, origin at Aim_Pivot)
    bracket = build_bracket(mats)
    bracket.parent = aim_pivot

    # 5. Camera_Body (Child of Aim_Pivot, origin at Aim_Pivot)
    body = build_camera_body(mats)
    body.parent = aim_pivot

    # 6. Lens_Glass & IR_LED_Ring (Children of Camera_Body)
    ir_ring = build_ir_led_ring(mats)
    ir_ring.parent = body

    lens = build_lens_glass(mats)
    lens.parent = body

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Camera_Bullet_Outdoor.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Bullet_Outdoor.fbx")
    export_fbx(root, [mount_plate, bracket, body, ir_ring, lens], aim_pivot, fbx_path)

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
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 26) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Camera_Bullet_Outdoor")
    assert root is not None, "FAIL: Root object 'SEC_Camera_Bullet_Outdoor' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    aim_pivot = bpy.data.objects.get("Aim_Pivot")
    assert aim_pivot is not None, "FAIL: Aim_Pivot missing!"
    assert aim_pivot.parent == root, "FAIL: Aim_Pivot parent != root!"
    assert aim_pivot.type == 'EMPTY', f"FAIL: Aim_Pivot is type {aim_pivot.type}, expected EMPTY!"

    expected_meshes = {
        "Wall_Mount_Plate",
        "Bracket",
        "Camera_Body",
        "IR_LED_Ring",
        "Lens_Glass"
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
    assert total_tris <= 520, f"FAIL: Total triangles {total_tris} exceeds 520 budget!"
    print("[PASS] Triangle count verified strictly (<= 520)!")

    # Check Material Slots
    for m in mesh_objs:
        assert len(m.data.materials) >= 3, f"FAIL: Mesh '{m.name}' has fewer than 3 material slots!"
        assert m.data.materials[0].name.startswith("M_Security_Atlas"), f"FAIL: Slot 0 is '{m.data.materials[0].name}', expected 'M_Security_Atlas'!"
        assert m.data.materials[1].name.startswith("M_Lens_Glass"), f"FAIL: Slot 1 is '{m.data.materials[1].name}', expected 'M_Lens_Glass'!"
        assert m.data.materials[2].name.startswith("M_Emission"), f"FAIL: Slot 2 is '{m.data.materials[2].name}', expected 'M_Emission'!"
    print("[PASS] Material slots strictly verified: Slot 0: M_Security_Atlas, Slot 1: M_Lens_Glass, Slot 2: M_Emission!")

    # Check UV layers
    for m in mesh_objs:
        assert len(m.data.uv_layers) > 0, f"FAIL: Mesh '{m.name}' has no UV layers!"
    print("[PASS] All meshes have valid UV coordinates!")

    # Check Parent-Child Hierarchy
    plate = bpy.data.objects.get("Wall_Mount_Plate")
    assert plate and plate.parent == root, "FAIL: Wall_Mount_Plate parent != root!"

    bracket = bpy.data.objects.get("Bracket")
    assert bracket and bracket.parent == aim_pivot, "FAIL: Bracket parent != Aim_Pivot!"

    body = bpy.data.objects.get("Camera_Body")
    assert body and body.parent == aim_pivot, "FAIL: Camera_Body parent != Aim_Pivot!"

    ir = bpy.data.objects.get("IR_LED_Ring")
    assert ir and ir.parent == body, "FAIL: IR_LED_Ring parent != Camera_Body!"

    lens = bpy.data.objects.get("Lens_Glass")
    assert lens and lens.parent == body, "FAIL: Lens_Glass parent != Camera_Body!"

    print("[PASS] Full parent-child hierarchy strictly verified!")

    # Update manifest
    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Camera_Bullet_Outdoor"] = {
        "asset_name": "SEC_Camera_Bullet_Outdoor",
        "fbx_path": "exports/SEC_Camera_Bullet_Outdoor.fbx",
        "blend_path": "exports/SEC_Camera_Bullet_Outdoor.blend",
        "tris_count": total_tris,
        "mesh_count": len(mesh_objs),
        "empty_count": 2,
        "materials": [
            "M_Security_Atlas",
            "M_Lens_Glass",
            "M_Emission"
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
