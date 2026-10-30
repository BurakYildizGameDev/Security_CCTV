"""
Security CCTV Asset Production Suite - Asset 63
Asset Name: SEC_Alarm_Outdoor_Speaker (Outdoor Re-entrant Horn Speaker - 30W IP66)
Realistic Low-Poly 3D Generator (bpy)
"""

import bpy
import bmesh
import json
import math
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Outdoor_Speaker.blend")
FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Outdoor_Speaker.fbx")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

MAX_TRIS = 420

def create_materials():
    materials = {}

    # 1. M_Security_Atlas (Slot 0)
    mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    bsdf = mat_atlas.node_tree.nodes.get("Principled BSDF")
    if os.path.exists(ATLAS_PATH):
        tex_node = mat_atlas.node_tree.nodes.new("ShaderNodeTexImage")
        tex_node.image = bpy.data.images.get(os.path.basename(ATLAS_PATH)) or bpy.data.images.load(ATLAS_PATH)
        mat_atlas.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.40
    mat_atlas.diffuse_color = (0.85, 0.87, 0.90, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. M_Metal (Slot 1)
    mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    bsdf_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    if os.path.exists(ATLAS_PATH):
        tex_m = mat_metal.node_tree.nodes.new("ShaderNodeTexImage")
        tex_m.image = bpy.data.images.get(os.path.basename(ATLAS_PATH)) or bpy.data.images.load(ATLAS_PATH)
        mat_metal.node_tree.links.new(tex_m.outputs["Color"], bsdf_m.inputs["Base Color"])
    bsdf_m.inputs["Metallic"].default_value = 0.85
    bsdf_m.inputs["Roughness"].default_value = 0.28
    mat_metal.diffuse_color = (0.70, 0.73, 0.78, 1.0)
    materials["M_Metal"] = mat_metal

    return materials

def assign_material_slots(obj, mat_dict):
    slot_order = ["M_Security_Atlas", "M_Metal"]
    for mat_name in slot_order:
        obj.data.materials.append(mat_dict[mat_name])

def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv_rect
    xs = [l.vert.co.x for l in face.loops]
    ys = [l.vert.co.y for l in face.loops]
    zs = [l.vert.co.z for l in face.loops]
    
    # Project based on dominant bounding extent
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    dz = max(zs) - min(zs)
    
    if dy > dx and dy > dz:
        # Wrap along Y
        min_u_val, max_u_val = min(xs), max(xs)
        min_v_val, max_v_val = min(ys), max(ys)
        u_vals = xs
        v_vals = ys
    elif dx >= dz:
        min_u_val, max_u_val = min(xs), max(xs)
        min_v_val, max_v_val = min(zs), max(zs)
        u_vals = xs
        v_vals = zs
    else:
        min_u_val, max_u_val = min(ys), max(ys)
        min_v_val, max_v_val = min(zs), max(zs)
        u_vals = ys
        v_vals = zs

    span_u = max_u_val - min_u_val if max_u_val > min_u_val else 1e-5
    span_v = max_v_val - min_v_val if max_v_val > min_v_val else 1e-5

    for l in face.loops:
        coord_u = l.vert.co.x if u_vals is xs else (l.vert.co.y if u_vals is ys else l.vert.co.z)
        coord_v = l.vert.co.z if v_vals is zs else (l.vert.co.y if v_vals is ys else l.vert.co.x)
        tu = (coord_u - min_u_val) / span_u
        tv = (coord_v - min_v_val) / span_v
        if flip_u:
            tu = 1.0 - tu
        if flip_v:
            tv = 1.0 - tv
        l[uv_layer].uv = (u0 + tu * (u1 - u0), v0 + tv * (v1 - v0))

def set_face_uv_constant(bm, face, uv_point):
    uv_layer = bm.loops.layers.uv.verify()
    for l in face.loops:
        l[uv_layer].uv = uv_point

def add_box(bm, x0, x1, y0, y1, z0, z1):
    v = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    f_back  = bm.faces.new([v[0], v[1], v[2], v[3]])
    f_front = bm.faces.new([v[5], v[4], v[7], v[6]])
    f_bot   = bm.faces.new([v[0], v[4], v[5], v[1]])
    f_top   = bm.faces.new([v[3], v[2], v[6], v[7]])
    f_left  = bm.faces.new([v[4], v[0], v[3], v[7]])
    f_right = bm.faces.new([v[1], v[5], v[6], v[2]])
    bm.normal_update()
    return {
        'back': f_back, 'front': f_front, 'bot': f_bot,
        'top': f_top, 'left': f_left, 'right': f_right, 'verts': v
    }

def mark_sharp_edges(bm, angle_deg=35.0):
    thresh = math.radians(angle_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            if edge.calc_face_angle() > thresh:
                edge.smooth = False
            else:
                edge.smooth = True
        else:
            edge.smooth = False

def build_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    materials = create_materials()

    # Root Empty: SEC_Alarm_Outdoor_Speaker at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Alarm_Outdoor_Speaker", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.15
    bpy.context.collection.objects.link(root)

    uv_swatch_polymer = ((250)/2048, 1.0 - 1750/2048)
    uv_swatch_metal   = ((750)/2048, 1.0 - 1750/2048)
    uv_swatch_dark    = ((1250)/2048, 1.0 - 1750/2048)
    uv_swatch_rubber  = ((1750)/2048, 1.0 - 1750/2048)

    # -------------------------------------------------------------------------
    # 1. MOUNT_BRACKET (Mesh - Child of Root)
    # Stamped steel U-bracket:
    # Wall plate Y: 0.000 to 0.006, X: -0.045 to +0.045, Z: -0.045 to +0.045
    # Two arms curving forward to pivot axis at Y = 0.085, X = ±0.052
    # -------------------------------------------------------------------------
    brk_me = bpy.data.meshes.new("Mount_Bracket")
    brk_bm = bmesh.new()

    # Back plate against wall
    bp = add_box(brk_bm, -0.045, 0.045, 0.000, 0.006, -0.045, 0.045)
    uv_bracket_back = (1500/2048, 1.0 - 500/2048, 2000/2048, 1.0 - 50/2048)
    for k, face in bp.items():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1 # M_Metal
            if k == 'back':
                set_face_uv_rect(brk_bm, face, uv_bracket_back)
            else:
                set_face_uv_constant(brk_bm, face, uv_swatch_metal)

    # Left U-Arm
    la1 = add_box(brk_bm, -0.052, -0.045, 0.000, 0.006, -0.015, 0.015)
    la2 = add_box(brk_bm, -0.052, -0.048, 0.006, 0.095, -0.020, 0.020)
    # Right U-Arm
    ra1 = add_box(brk_bm, 0.045, 0.052, 0.000, 0.006, -0.015, 0.015)
    ra2 = add_box(brk_bm, 0.048, 0.052, 0.006, 0.095, -0.020, 0.020)

    uv_tilt_scale = (1500/2048, 1.0 - 750/2048, 2000/2048, 1.0 - 520/2048)

    for arm in [la1, ra1]:
        for face in arm.values():
            if isinstance(face, bmesh.types.BMFace):
                face.material_index = 1
                set_face_uv_constant(brk_bm, face, uv_swatch_metal)

    for face in la2.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1
            if face == la2['left']:
                set_face_uv_rect(brk_bm, face, uv_tilt_scale)
            else:
                set_face_uv_constant(brk_bm, face, uv_swatch_metal)

    for face in ra2.values():
        if isinstance(face, bmesh.types.BMFace):
            face.material_index = 1
            if face == ra2['right']:
                set_face_uv_rect(brk_bm, face, uv_tilt_scale)
            else:
                set_face_uv_constant(brk_bm, face, uv_swatch_metal)

    # Left & Right Pivot Bolts (Hex head centered at X = ±0.053, Y = 0.085)
    for sx_c in [-0.054, 0.054]:
        b_box = add_box(brk_bm, sx_c - 0.003, sx_c + 0.003, 0.078, 0.092, -0.007, 0.007)
        for face in b_box.values():
            if isinstance(face, bmesh.types.BMFace):
                face.material_index = 1
                set_face_uv_constant(brk_bm, face, uv_swatch_metal)

    mark_sharp_edges(brk_bm)
    brk_bm.to_mesh(brk_me)
    brk_bm.free()

    brk_obj = bpy.data.objects.new("Mount_Bracket", brk_me)
    bpy.context.collection.objects.link(brk_obj)
    brk_obj.parent = root
    assign_material_slots(brk_obj, materials)

    # -------------------------------------------------------------------------
    # 2. AIM_PIVOT (Empty - Child of Root)
    # Swivel hinge at (0.000, 0.085, 0.000), local X/Z ±25°
    # -------------------------------------------------------------------------
    aim_pivot = bpy.data.objects.new("Aim_Pivot", None)
    aim_pivot.empty_display_type = 'ARROWS'
    aim_pivot.empty_display_size = 0.12
    aim_pivot.location = (0.000, 0.085, 0.000)
    bpy.context.collection.objects.link(aim_pivot)
    aim_pivot.parent = root

    aim_pivot["min_rot_x"] = -25.0
    aim_pivot["max_rot_x"] = 25.0
    aim_pivot["min_rot_z"] = -25.0
    aim_pivot["max_rot_z"] = 25.0

    con_rot = aim_pivot.constraints.new(type='LIMIT_ROTATION')
    con_rot.owner_space = 'LOCAL'
    con_rot.use_limit_x = True
    con_rot.min_x = math.radians(-25.0)
    con_rot.max_x = math.radians(25.0)
    con_rot.use_limit_y = True
    con_rot.min_y = 0.0
    con_rot.max_y = 0.0
    con_rot.use_limit_z = True
    con_rot.min_z = math.radians(-25.0)
    con_rot.max_z = math.radians(25.0)

    # -------------------------------------------------------------------------
    # 3. DRIVER_HOUSING (Mesh - Child of Aim_Pivot)
    # Cylindrical driver chamber: Modeled in local space of Aim_Pivot (hinge at Y=0)
    # Y: -0.040 to +0.045, Radius 0.044m (16 sides, smooth shaded)
    # Stepped rear cap: Y: -0.048, Radius 0.030m
    # -------------------------------------------------------------------------
    spk_me = bpy.data.meshes.new("Driver_Housing")
    spk_bm = bmesh.new()

    segs = 16
    r_drv = 0.044
    y_rear = -0.040
    y_front = 0.045

    v_rear = []
    v_front = []
    v_step = []
    r_step = 0.030
    y_step = -0.048

    for s in range(segs):
        ang = s * (2.0 * math.pi / segs)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_rear.append(spk_bm.verts.new((r_drv * cos_a, y_rear, r_drv * sin_a)))
        v_front.append(spk_bm.verts.new((r_drv * cos_a, y_front, r_drv * sin_a)))
        v_step.append(spk_bm.verts.new((r_step * cos_a, y_step, r_step * sin_a)))

    # Step transition at rear of driver
    for s in range(segs):
        s_next = (s + 1) % segs
        f_tr = spk_bm.faces.new([v_step[s], v_step[s_next], v_rear[s_next], v_rear[s]])
        f_tr.material_index = 0
        set_face_uv_constant(spk_bm, f_tr, uv_swatch_dark)

    # Rear cap
    v_center_rear = spk_bm.verts.new((0.0, y_step, 0.0))
    for s in range(segs):
        s_next = (s + 1) % segs
        f_c = spk_bm.faces.new([v_step[s_next], v_step[s], v_center_rear])
        f_c.material_index = 0
        set_face_uv_constant(spk_bm, f_c, uv_swatch_dark)

    # Side cylinder wrapped with technical nameplate on top, dark ribbed casing on sides/bottom
    uv_nameplate = (50/2048, 1.0 - 650/2048, 1450/2048, 1.0 - 50/2048)
    for s in range(segs):
        s_next = (s + 1) % segs
        f_side = spk_bm.faces.new([v_rear[s], v_rear[s_next], v_front[s_next], v_front[s]])
        f_side.material_index = 0
        z_avg = (v_rear[s].co.z + v_rear[s_next].co.z) / 2.0
        if z_avg > 0.015:
            # Map Y (length) to U, and angle to V
            l_uv = f_side.loops
            uv_layer = spk_bm.loops.layers.uv.verify()
            for l in l_uv:
                ty = (l.vert.co.y - y_rear) / (y_front - y_rear)
                tz = (l.vert.co.z - 0.015) / (r_drv - 0.015)
                l[uv_layer].uv = (uv_nameplate[0] + ty * (uv_nameplate[2] - uv_nameplate[0]),
                                  uv_nameplate[1] + tz * (uv_nameplate[3] - uv_nameplate[1]))
        else:
            set_face_uv_constant(spk_bm, f_side, uv_swatch_dark)

    mark_sharp_edges(spk_bm)
    spk_bm.to_mesh(spk_me)
    spk_bm.free()

    spk_obj = bpy.data.objects.new("Driver_Housing", spk_me)
    bpy.context.collection.objects.link(spk_obj)
    spk_obj.parent = aim_pivot
    assign_material_slots(spk_obj, materials)

    # -------------------------------------------------------------------------
    # 4. CABLE_GLAND (Mesh - Child of Aim_Pivot)
    # Hexagonal gland and black cable sleeve exiting rear at Y = -0.048 to -0.070
    # Clearance with wall plate: ends at world Y = 0.015, wall plate front is Y = 0.006 (9mm gap)
    # -------------------------------------------------------------------------
    gland_me = bpy.data.meshes.new("Cable_Gland")
    gland_bm = bmesh.new()

    g_segs = 6 # Hex nut
    r_nut = 0.012
    v_n0 = []
    v_n1 = []
    for s in range(g_segs):
        ang = s * (2.0 * math.pi / g_segs)
        v_n0.append(gland_bm.verts.new((r_nut * math.cos(ang), -0.048, r_nut * math.sin(ang))))
        v_n1.append(gland_bm.verts.new((r_nut * math.cos(ang), -0.058, r_nut * math.sin(ang))))

    uv_gland = (1500/2048, 1.0 - 1200/2048, 2000/2048, 1.0 - 800/2048)
    for s in range(g_segs):
        s_next = (s + 1) % g_segs
        f_n = gland_bm.faces.new([v_n0[s], v_n0[s_next], v_n1[s_next], v_n1[s]])
        f_n.material_index = 0
        set_face_uv_rect(gland_bm, f_n, uv_gland)

    # Rubber strain relief boot
    r_boot = 0.007
    v_b0 = []
    v_b1 = []
    for s in range(6):
        ang = s * (2.0 * math.pi / 6)
        v_b0.append(gland_bm.verts.new((r_boot * math.cos(ang), -0.058, r_boot * math.sin(ang))))
        v_b1.append(gland_bm.verts.new((r_boot * 0.7 * math.cos(ang), -0.070, r_boot * 0.7 * math.sin(ang))))

    for s in range(6):
        s_next = (s + 1) % 6
        f_b = gland_bm.faces.new([v_b0[s], v_b0[s_next], v_b1[s_next], v_b1[s]])
        f_b.material_index = 0
        set_face_uv_constant(gland_bm, f_b, uv_swatch_rubber)

    # Cap
    f_bcap = gland_bm.faces.new(v_b1[::-1])
    f_bcap.material_index = 0
    set_face_uv_constant(gland_bm, f_bcap, uv_swatch_rubber)

    mark_sharp_edges(gland_bm)
    gland_bm.to_mesh(gland_me)
    gland_bm.free()

    gland_obj = bpy.data.objects.new("Cable_Gland", gland_me)
    bpy.context.collection.objects.link(gland_obj)
    gland_obj.parent = aim_pivot
    assign_material_slots(gland_obj, materials)

    # -------------------------------------------------------------------------
    # 5. HORN_FLARE (Mesh - Child of Aim_Pivot)
    # Double-walled 16-sided aerodynamic bell with rolled lip + Central Acoustic Phase Cone
    # -------------------------------------------------------------------------
    horn_me = bpy.data.meshes.new("Horn_Flare")
    horn_bm = bmesh.new()

    h_segs = 16
    r_throat = 0.044
    r_mouth  = 0.115
    r_lip    = 0.120
    y_start  = 0.045
    y_mouth  = 0.185
    y_lip    = 0.190
    y_in_thr = 0.075
    r_in_thr = 0.038

    # 1. Outer Flare Ring
    v_out_t = []
    v_out_m = []
    v_lip   = []
    v_in_m  = []
    v_in_t  = []

    for s in range(h_segs):
        ang = s * (2.0 * math.pi / h_segs)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_out_t.append(horn_bm.verts.new((r_throat * cos_a, y_start, r_throat * sin_a)))
        v_out_m.append(horn_bm.verts.new((r_mouth * cos_a, y_mouth, r_mouth * sin_a)))
        v_lip.append(horn_bm.verts.new((r_lip * cos_a, y_lip, r_lip * sin_a)))
        v_in_m.append(horn_bm.verts.new((r_mouth * cos_a, y_mouth, r_mouth * sin_a)))
        v_in_t.append(horn_bm.verts.new((r_in_thr * cos_a, y_in_thr, r_in_thr * sin_a)))

    uv_throat_art = (50/2048, 1.0 - 1450/2048, 1450/2048, 1.0 - 720/2048)
    uv_bell_ext = (50/2048, 1.0 - 1850/2048, 1450/2048, 1.0 - 1480/2048)

    # Outer bell surface (Normal points outwards with realistic gradient & markings)
    for s in range(h_segs):
        s_next = (s + 1) % h_segs
        f_out = horn_bm.faces.new([v_out_t[s], v_out_t[s_next], v_out_m[s_next], v_out_m[s]])
        f_out.material_index = 0
        u0_seg = uv_bell_ext[0] + (s / h_segs) * (uv_bell_ext[2] - uv_bell_ext[0])
        u1_seg = uv_bell_ext[0] + ((s + 1) / h_segs) * (uv_bell_ext[2] - uv_bell_ext[0])
        set_face_uv_rect(horn_bm, f_out, (u0_seg, uv_bell_ext[1], u1_seg, uv_bell_ext[3]), flip_v=True)

        # Rolled outer rim lip
        f_lip = horn_bm.faces.new([v_out_m[s], v_out_m[s_next], v_lip[s_next], v_lip[s]])
        f_lip.material_index = 0
        set_face_uv_constant(horn_bm, f_lip, uv_swatch_polymer)

        # Inner flare returning inside into throat (Normal points inwards into mouth)
        f_in = horn_bm.faces.new([v_lip[s], v_lip[s_next], v_in_t[s_next], v_in_t[s]])
        f_in.material_index = 0
        set_face_uv_constant(horn_bm, f_in, uv_swatch_polymer)

    # Inner throat bottom plate
    v_in_center = horn_bm.verts.new((0.0, y_in_thr, 0.0))
    for s in range(h_segs):
        s_next = (s + 1) % h_segs
        f_base = horn_bm.faces.new([v_in_t[s], v_in_t[s_next], v_in_center])
        f_base.material_index = 0
        set_face_uv_rect(horn_bm, f_base, uv_throat_art)

    # 2. Central Re-entrant Acoustic Core (Phase Plug)
    # Sleek bullet-shaped re-entrant dome centered at axis: Y: 0.090 to 0.170
    c_segs = 12
    r_cone_base = 0.035
    r_cone_mid  = 0.024
    r_cone_nose = 0.010
    v_c_base = []
    v_c_mid  = []
    v_c_nose = []

    for s in range(c_segs):
        ang = s * (2.0 * math.pi / c_segs)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_c_base.append(horn_bm.verts.new((r_cone_base * cos_a, 0.090, r_cone_base * sin_a)))
        v_c_mid.append(horn_bm.verts.new((r_cone_mid * cos_a, 0.145, r_cone_mid * sin_a)))
        v_c_nose.append(horn_bm.verts.new((r_cone_nose * cos_a, 0.168, r_cone_nose * sin_a)))

    v_c_tip = horn_bm.verts.new((0.0, 0.172, 0.0))

    for s in range(c_segs):
        s_next = (s + 1) % c_segs
        f_c1 = horn_bm.faces.new([v_c_base[s], v_c_base[s_next], v_c_mid[s_next], v_c_mid[s]])
        f_c1.material_index = 0
        set_face_uv_constant(horn_bm, f_c1, uv_swatch_polymer)

        f_c2 = horn_bm.faces.new([v_c_mid[s], v_c_mid[s_next], v_c_nose[s_next], v_c_nose[s]])
        f_c2.material_index = 0
        set_face_uv_constant(horn_bm, f_c2, uv_swatch_polymer)

        f_c3 = horn_bm.faces.new([v_c_nose[s], v_c_nose[s_next], v_c_tip])
        f_c3.material_index = 0
        set_face_uv_constant(horn_bm, f_c3, uv_swatch_polymer)

    # 3. Three Radial Aerodynamic Struts (Angles: 90°, 210°, 330°)
    for k in range(3):
        theta = math.radians(90.0 + k * 120.0)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        # Perpendicular unit vector
        perp_x = -sin_t
        perp_z = cos_t
        hw = 0.002 # half thickness = 2mm
        y_fin_0 = 0.115
        y_fin_1 = 0.135
        r_inner = 0.026
        r_outer = 0.075

        # 8 vertices for rotated strut box
        p0 = horn_bm.verts.new((r_inner * cos_t - hw * perp_x, y_fin_0, r_inner * sin_t - hw * perp_z))
        p1 = horn_bm.verts.new((r_outer * cos_t - hw * perp_x, y_fin_0, r_outer * sin_t - hw * perp_z))
        p2 = horn_bm.verts.new((r_outer * cos_t - hw * perp_x, y_fin_1, r_outer * sin_t - hw * perp_z))
        p3 = horn_bm.verts.new((r_inner * cos_t - hw * perp_x, y_fin_1, r_inner * sin_t - hw * perp_z))

        p4 = horn_bm.verts.new((r_inner * cos_t + hw * perp_x, y_fin_0, r_inner * sin_t + hw * perp_z))
        p5 = horn_bm.verts.new((r_outer * cos_t + hw * perp_x, y_fin_0, r_outer * sin_t + hw * perp_z))
        p6 = horn_bm.verts.new((r_outer * cos_t + hw * perp_x, y_fin_1, r_outer * sin_t + hw * perp_z))
        p7 = horn_bm.verts.new((r_inner * cos_t + hw * perp_x, y_fin_1, r_inner * sin_t + hw * perp_z))

        f_s1 = horn_bm.faces.new([p0, p1, p2, p3])
        f_s2 = horn_bm.faces.new([p5, p4, p7, p6])
        f_s3 = horn_bm.faces.new([p4, p0, p3, p7])
        f_s4 = horn_bm.faces.new([p1, p5, p6, p2])
        f_s5 = horn_bm.faces.new([p3, p2, p6, p7])
        f_s6 = horn_bm.faces.new([p0, p4, p5, p1])
        for sf in [f_s1, f_s2, f_s3, f_s4, f_s5, f_s6]:
            sf.material_index = 0
            set_face_uv_constant(horn_bm, sf, uv_swatch_polymer)

    mark_sharp_edges(horn_bm)
    horn_bm.to_mesh(horn_me)
    horn_bm.free()

    horn_obj = bpy.data.objects.new("Horn_Flare", horn_me)
    bpy.context.collection.objects.link(horn_obj)
    horn_obj.parent = aim_pivot
    assign_material_slots(horn_obj, materials)

    # -------------------------------------------------------------------------
    # QA Check & Triangulation
    # -------------------------------------------------------------------------
    total_tris = 0
    meshes = [brk_obj, spk_obj, gland_obj, horn_obj]
    for obj in meshes:
        me = obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        t_count = len(bm.faces)
        total_tris += t_count
        bm.free()
        obj.to_mesh_clear()

    print(f"[Geometry] Total meshes: {len(meshes)}, Total tris: {total_tris} (limit: {MAX_TRIS})")
    assert total_tris <= MAX_TRIS, f"Tris budget exceeded: {total_tris} > {MAX_TRIS}"

    # Smooth shading setup
    for obj in [spk_obj, horn_obj]:
        for poly in obj.data.polygons:
            poly.use_smooth = True

    # Pack textures and set viewport
    bpy.ops.file.pack_all()
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.shading.type = 'MATERIAL'

    # Save Blend file
    bpy.ops.wm.save_mainfile(filepath=BLEND_PATH)
    print(f"[Export] Saved blend: {BLEND_PATH}")

    # FBX Export
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for obj in meshes:
        obj.select_set(True)
    aim_pivot.select_set(True)
    bpy.context.view_layer.objects.active = root

    bpy.ops.export_scene.fbx(
        filepath=FBX_PATH,
        use_selection=True,
        object_types={'MESH', 'EMPTY'},
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,
        bake_space_transform=False,
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        path_mode='AUTO',
        use_custom_props=True
    )
    print(f"[Export] Saved FBX: {FBX_PATH}")

    # Reverse Re-import Test
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=FBX_PATH)
    reimp_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    reimp_empties = [o for o in bpy.context.scene.objects if o.type == 'EMPTY']
    reimp_tris = 0
    for o in reimp_meshes:
        m = o.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(m)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        reimp_tris += len(bm.faces)
        bm.free()
        o.to_mesh_clear()

    print(f"[QA Reimport] Meshes: {len(reimp_meshes)}, Empties: {len(reimp_empties)}, Tris: {reimp_tris}")
    assert len(reimp_meshes) == 4, f"Mesh count mismatch: {len(reimp_meshes)} != 4"
    assert len(reimp_empties) == 2, f"Empty count mismatch: {len(reimp_empties)} != 2"
    assert reimp_tris <= MAX_TRIS, f"Re-imported tris exceed budget: {reimp_tris} > {MAX_TRIS}"

    # Manifest update
    manifest = {
        "SEC_Alarm_Outdoor_Speaker": {
            "status": "SUCCESS",
            "fbx_path": FBX_PATH,
            "blend_path": BLEND_PATH,
            "total_tris": total_tris,
            "max_tris": MAX_TRIS,
            "mesh_count": len(meshes),
            "empty_count": 2,
            "materials": ["M_Security_Atlas", "M_Metal"]
        }
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print(f"[Manifest] Updated {MANIFEST_PATH} with status SUCCESS")

if __name__ == "__main__":
    build_scene()
