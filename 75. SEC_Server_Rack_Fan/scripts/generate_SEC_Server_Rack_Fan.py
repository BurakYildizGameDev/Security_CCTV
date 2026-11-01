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

    # 1. Slot 0: M_Metal (Polished Chrome / Nickel Wire Guard)
    mat_metal = bpy.data.materials.new("M_Metal")
    mat_metal.use_nodes = True
    nodes_m = mat_metal.node_tree.nodes
    links_m = mat_metal.node_tree.links
    nodes_m.clear()

    out_m = nodes_m.new('ShaderNodeOutputMaterial')
    bsdf_m = nodes_m.new('ShaderNodeBsdfPrincipled')
    bsdf_m.inputs['Metallic'].default_value = 0.95
    bsdf_m.inputs['Roughness'].default_value = 0.18

    if img:
        tex_node_m = nodes_m.new('ShaderNodeTexImage')
        tex_node_m.image = img
        links_m.new(tex_node_m.outputs['Color'], bsdf_m.inputs['Base Color'])
    else:
        bsdf_m.inputs['Base Color'].default_value = (0.85, 0.88, 0.92, 1.0)
    links_m.new(bsdf_m.outputs['BSDF'], out_m.inputs['Surface'])

    if hasattr(mat_metal, 'blend_method'): mat_metal.blend_method = 'OPAQUE'
    if hasattr(mat_metal, 'shadow_method'): mat_metal.shadow_method = 'OPAQUE'

    # 2. Slot 1: M_Security_Atlas (Matte Industrial PBT Housing & Motor Badge)
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes_a = mat_atlas.node_tree.nodes
    links_a = mat_atlas.node_tree.links
    nodes_a.clear()

    out_a = nodes_a.new('ShaderNodeOutputMaterial')
    bsdf_a = nodes_a.new('ShaderNodeBsdfPrincipled')
    bsdf_a.inputs['Metallic'].default_value = 0.08
    bsdf_a.inputs['Roughness'].default_value = 0.40

    if img:
        tex_node_a = nodes_a.new('ShaderNodeTexImage')
        tex_node_a.image = img
        links_a.new(tex_node_a.outputs['Color'], bsdf_a.inputs['Base Color'])
    else:
        bsdf_a.inputs['Base Color'].default_value = (0.12, 0.13, 0.15, 1.0)
    links_a.new(bsdf_a.outputs['BSDF'], out_a.inputs['Surface'])

    if hasattr(mat_atlas, 'blend_method'): mat_atlas.blend_method = 'OPAQUE'
    if hasattr(mat_atlas, 'shadow_method'): mat_atlas.shadow_method = 'OPAQUE'

    return [mat_metal, mat_atlas]

UV_FRAME       = (0.25, 0.75)
UV_METAL       = (0.75, 0.75)
UV_BLADES      = (0.75, 0.25)
UV_HUB_CENTER  = (0.25, 0.25)

def build_fan_frame(mats):
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    w = 0.060       # 60mm half-width (120mm overall)
    c_off = 0.009   # 9mm corner chamfer
    r_bore = 0.056  # 56mm circular bore (112mm diameter)
    y_f = 0.000     # front face
    y_b = 0.025     # rear face
    n_seg = 16

    # 16-segment circular tunnel bore at front and back
    v_bore_f = []
    v_bore_b = []
    for i in range(n_seg):
        ang = i * (2.0 * math.pi / n_seg)
        x = math.cos(ang) * r_bore
        z = math.sin(ang) * r_bore
        v_bore_f.append(bm.verts.new((x, y_f, z)))
        v_bore_b.append(bm.verts.new((x, y_b, z)))

    # 12-sided outer profile with corner chamfers
    outer_2d = [
        ( w,         0.0),          # 0: Mid +X
        ( w,         w - c_off),    # 1: Corner +X,+Z
        ( w - c_off, w),            # 2: Corner +X,+Z
        ( 0.0,       w),            # 3: Mid +Z
        (-w + c_off, w),            # 4: Corner -X,+Z
        (-w,         w - c_off),    # 5: Corner -X,+Z
        (-w,         0.0),          # 6: Mid -X
        (-w,        -w + c_off),    # 7: Corner -X,-Z
        (-w + c_off,-w),            # 8: Corner -X,-Z
        ( 0.0,      -w),            # 9: Mid -Z
        ( w - c_off,-w),            # 10: Corner +X,-Z
        ( w,        -w + c_off)     # 11: Corner +X,-Z
    ]
    v_out_f = [bm.verts.new((p[0], y_f, p[1])) for p in outer_2d]
    v_out_b = [bm.verts.new((p[0], y_b, p[1])) for p in outer_2d]

    bm.verts.ensure_lookup_table()

    # Outer side walls (12 quads = 24 tris)
    for i in range(12):
        inxt = (i + 1) % 12
        f = bm.faces.new((v_out_f[i], v_out_f[inxt], v_out_b[inxt], v_out_b[i]))
        f.smooth = False
        f.material_index = 1
        for l in f.loops: l[uv_layer].uv = UV_FRAME

    # Inner cylindrical tunnel (16 quads = 32 tris)
    for i in range(n_seg):
        inext = (i + 1) % n_seg
        f = bm.faces.new((v_bore_f[i], v_bore_b[i], v_bore_b[inext], v_bore_f[inext]))
        f.smooth = True
        f.material_index = 1
        for l in f.loops: l[uv_layer].uv = UV_FRAME

    # Front & Rear Faces (4 quadrants)
    for q in range(4):
        o_mid_start = q * 3
        o_ch1       = q * 3 + 1
        o_ch2       = q * 3 + 2
        o_mid_end   = (q * 3 + 3) % 12

        c0 = (q * 4) % 16
        c1 = (q * 4 + 1) % 16
        c2 = (q * 4 + 2) % 16
        c3 = (q * 4 + 3) % 16
        c4 = (q * 4 + 4) % 16

        # Front (facing -Y)
        ff1 = bm.faces.new((v_out_f[o_mid_start], v_out_f[o_ch1], v_bore_f[c1], v_bore_f[c0]))
        ff2 = bm.faces.new((v_out_f[o_ch1], v_out_f[o_ch2], v_bore_f[c2], v_bore_f[c1]))
        ff3 = bm.faces.new((v_out_f[o_ch2], v_bore_f[c3], v_bore_f[c2]))
        ff4 = bm.faces.new((v_out_f[o_ch2], v_out_f[o_mid_end], v_bore_f[c4], v_bore_f[c3]))

        for ff in [ff1, ff2, ff3, ff4]:
            ff.smooth = False
            ff.material_index = 1
            for l in ff.loops: l[uv_layer].uv = UV_FRAME

        # Rear (facing +Y)
        fb1 = bm.faces.new((v_out_b[o_ch1], v_out_b[o_mid_start], v_bore_b[c0], v_bore_b[c1]))
        fb2 = bm.faces.new((v_out_b[o_ch2], v_out_b[o_ch1], v_bore_b[c1], v_bore_b[c2]))
        fb3 = bm.faces.new((v_out_b[o_ch2], v_bore_b[c2], v_bore_b[c3]))
        fb4 = bm.faces.new((v_out_b[o_mid_end], v_out_b[o_ch2], v_bore_b[c3], v_bore_b[c4]))

        for fb in [fb1, fb2, fb3, fb4]:
            fb.smooth = False
            fb.material_index = 1
            for l in fb.loops: l[uv_layer].uv = UV_FRAME

    # 4 Corner Mounting Holes (recessed round holes at ±0.050, ±0.050)
    for cx_s in [-1, 1]:
        for cz_s in [-1, 1]:
            h_c = Vector((cx_s * 0.050, y_f, cz_s * 0.050))
            vh_in = []
            vh_lip = []
            r_in = 0.0022  # 4.4mm hole
            r_lip = 0.0042 # 8.4mm washer rim
            for s in range(4):
                ang = s * (0.5 * math.pi) + 0.25 * math.pi
                vh_in.append(bm.verts.new(h_c + Vector((math.cos(ang) * r_in, 0.0025, math.sin(ang) * r_in))))
                vh_lip.append(bm.verts.new(h_c + Vector((math.cos(ang) * r_lip, -0.0004, math.sin(ang) * r_lip))))

            f_bot = bm.faces.new(vh_in)
            f_bot.smooth = False
            f_bot.material_index = 1
            for l in f_bot.loops: l[uv_layer].uv = UV_FRAME

            for s in range(4):
                sn = (s + 1) % 4
                f_wash = bm.faces.new((vh_lip[s], vh_in[s], vh_in[sn], vh_lip[sn]))
                f_wash.smooth = False
                f_wash.material_index = 0 # M_Metal
                for l in f_wash.loops: l[uv_layer].uv = UV_METAL

    # Rear Stator Motor Mount (8-sided central bearing cup + 4 aerodynamic struts)
    r_stat = 0.021
    y_stat = y_b - 0.002
    v_stat = []
    for i in range(8):
        ang = i * (2.0 * math.pi / 8)
        v_stat.append(bm.verts.new((math.cos(ang) * r_stat, y_stat, math.sin(ang) * r_stat)))

    f_stat = bm.faces.new(reversed(v_stat))
    f_stat.smooth = False
    f_stat.material_index = 1
    for l in f_stat.loops: l[uv_layer].uv = UV_FRAME

    stator_conn = [(2, 1), (6, 3), (10, 5), (14, 7)]
    for b_idx, s_idx in stator_conn:
        ang = b_idx * (2.0 * math.pi / n_seg)
        perp = Vector((-math.sin(ang), 0, math.cos(ang))) * 0.0022
        b_pos = Vector((v_bore_b[b_idx].co.x, y_stat, v_bore_b[b_idx].co.z))
        s_pos = Vector((v_stat[s_idx].co.x, y_stat, v_stat[s_idx].co.z))

        v1 = bm.verts.new(s_pos - perp)
        v2 = bm.verts.new(s_pos + perp)
        v3 = bm.verts.new(b_pos + perp)
        v4 = bm.verts.new(b_pos - perp)

        f_strut = bm.faces.new((v1, v2, v3, v4))
        f_strut.smooth = False
        f_strut.material_index = 1
        for l in f_strut.loops: l[uv_layer].uv = UV_FRAME

    bm.normal_update()
    mesh = bpy.data.meshes.new("Frame")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def build_fan_grille(mats):
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    y_g = -0.0026
    w_w = 0.0010

    # 2 Concentric Rings with uniform 16 segments (Outer 52mm, Mid 34mm)
    for r_guard in [0.052, 0.034]:
        v_in  = []
        v_out = []
        for i in range(16):
            ang = i * (2.0 * math.pi / 16)
            ca, sa = math.cos(ang), math.sin(ang)
            v_in.append(bm.verts.new((ca * (r_guard - w_w), y_g, sa * (r_guard - w_w))))
            v_out.append(bm.verts.new((ca * (r_guard + w_w), y_g - w_w * 0.8, sa * (r_guard + w_w))))

        bm.verts.ensure_lookup_table()
        for i in range(16):
            inxt = (i + 1) % 16
            f = bm.faces.new((v_in[i], v_in[inxt], v_out[inxt], v_out[i]))
            f.smooth = True
            f.material_index = 0
            for l in f.loops: l[uv_layer].uv = UV_METAL

    # 4 Radial Struts connecting center R=0.018m out to corner screw holes at R=0.0707m
    for k in range(4):
        ang = (k * 0.5 + 0.25) * math.pi
        ca, sa = math.cos(ang), math.sin(ang)
        dir_arm = Vector((ca, 0, sa))
        perp = Vector((-sa, 0, ca)) * w_w

        p_start = dir_arm * 0.018 + Vector((0, y_g - w_w * 0.4, 0))
        p_end   = dir_arm * 0.0707 + Vector((0, y_g - w_w * 0.4, 0))

        v1 = bm.verts.new(p_start - perp)
        v2 = bm.verts.new(p_start + perp)
        v3 = bm.verts.new(p_end + perp)
        v4 = bm.verts.new(p_end - perp)

        f_arm = bm.faces.new((v1, v4, v3, v2))
        f_arm.smooth = True
        f_arm.material_index = 0
        for l in f_arm.loops: l[uv_layer].uv = UV_METAL

        vh_eye = []
        r_eye = 0.0038
        for s in range(4):
            sang = s * (0.5 * math.pi) + 0.25 * math.pi
            vh_eye.append(bm.verts.new(p_end + Vector((math.cos(sang) * r_eye, -0.0005, math.sin(sang) * r_eye))))
        f_eye = bm.faces.new((vh_eye[0], vh_eye[3], vh_eye[2], vh_eye[1]))
        f_eye.smooth = False
        f_eye.material_index = 0
        for l in f_eye.loops: l[uv_layer].uv = UV_METAL

    bm.normal_update()
    mesh = bpy.data.meshes.new("Grille")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def build_fan_hub(mats):
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    r_hub = 0.0210
    y_h_front = -0.009
    y_h_back  =  0.009
    n_hub = 12

    v_hf = []
    v_hb = []
    for i in range(n_hub):
        ang = i * (2.0 * math.pi / n_hub)
        ca, sa = math.cos(ang), math.sin(ang)
        v_hf.append(bm.verts.new((ca * r_hub, y_h_front, sa * r_hub)))
        v_hb.append(bm.verts.new((ca * r_hub, y_h_back, sa * r_hub)))

    bm.verts.ensure_lookup_table()

    for i in range(n_hub):
        inext = (i + 1) % n_hub
        f = bm.faces.new((v_hf[i], v_hb[i], v_hb[inext], v_hf[inext]))
        f.smooth = True
        f.material_index = 1
        for l in f.loops: l[uv_layer].uv = UV_FRAME

    v_h_cen = bm.verts.new((0.0, y_h_front - 0.0015, 0.0))
    for i in range(n_hub):
        inext = (i + 1) % n_hub
        f_cap = bm.faces.new((v_h_cen, v_hf[inext], v_hf[i]))
        f_cap.smooth = False
        f_cap.material_index = 1

        ang_i = i * (2.0 * math.pi / n_hub)
        ang_nxt = inext * (2.0 * math.pi / n_hub)
        u_i   = 0.25 + math.cos(ang_i) * 0.20
        v_i   = 0.25 + math.sin(ang_i) * 0.20
        u_nxt = 0.25 + math.cos(ang_nxt) * 0.20
        v_nxt = 0.25 + math.sin(ang_nxt) * 0.20

        f_cap.loops[0][uv_layer].uv = (0.25, 0.25)
        f_cap.loops[1][uv_layer].uv = (u_nxt, v_nxt)
        f_cap.loops[2][uv_layer].uv = (u_i, v_i)

    v_h_rcen = bm.verts.new((0.0, y_h_back, 0.0))
    for i in range(n_hub):
        inext = (i + 1) % n_hub
        f_rc = bm.faces.new((v_h_rcen, v_hb[i], v_hb[inext]))
        f_rc.smooth = False
        f_rc.material_index = 1
        for l in f_rc.loops: l[uv_layer].uv = UV_FRAME

    bm.normal_update()
    mesh = bpy.data.meshes.new("Fan_Hub")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()
    return mesh

def build_single_blade(name, mats, blade_idx):
    bm_b = bmesh.new()
    uv_b = bm_b.loops.layers.uv.new("UVMap")

    blade_ang_base = blade_idx * (0.5 * math.pi)
    t_half = 0.0006

    stations = [
        (0.0210, 0.028, 44.0,  0.0, -0.003),
        (0.0380, 0.036, 32.0, 10.0, -0.001),
        (0.0540, 0.038, 22.0, 22.0,  0.002)
    ]

    station_pairs = []
    for r_st, chord, p_deg, sw_deg, y_c in stations:
        tot_ang = blade_ang_base + math.radians(sw_deg)
        ca, sa = math.cos(tot_ang), math.sin(tot_ang)
        r_dir = Vector((ca, 0, sa))
        t_dir = Vector((-sa, 0, ca))

        p_rad = math.radians(p_deg)
        cp, sp = math.cos(p_rad), math.sin(p_rad)
        w_h = chord * 0.5

        p_le = r_dir * r_st - t_dir * (w_h * cp) + Vector((0, y_c + w_h * sp, 0))
        p_te = r_dir * r_st + t_dir * (w_h * cp) + Vector((0, y_c - w_h * sp, 0))

        v_le_t = bm_b.verts.new(p_le - Vector((0, t_half, 0)))
        v_te_t = bm_b.verts.new(p_te - Vector((0, t_half, 0)))
        v_le_b = bm_b.verts.new(p_le + Vector((0, t_half, 0)))
        v_te_b = bm_b.verts.new(p_te + Vector((0, t_half, 0)))

        station_pairs.append({
            'top': [v_le_t, v_te_t],
            'bot': [v_le_b, v_te_b]
        })

    bm_b.verts.ensure_lookup_table()

    for s in range(len(stations) - 1):
        s1 = station_pairs[s]
        s2 = station_pairs[s + 1]

        f_t = bm_b.faces.new((s1['top'][0], s2['top'][0], s2['top'][1], s1['top'][1]))
        f_b = bm_b.faces.new((s1['bot'][1], s2['bot'][1], s2['bot'][0], s1['bot'][0]))
        f_le = bm_b.faces.new((s1['bot'][0], s2['bot'][0], s2['top'][0], s1['top'][0]))
        f_te = bm_b.faces.new((s1['top'][1], s2['top'][1], s2['bot'][1], s1['bot'][1]))

        for f in [f_t, f_b, f_le, f_te]:
            f.smooth = True
            f.material_index = 1
            for l in f.loops: l[uv_b].uv = UV_BLADES

    tip = station_pairs[-1]
    f_tip = bm_b.faces.new((tip['top'][0], tip['top'][1], tip['bot'][1], tip['bot'][0]))
    f_tip.smooth = True
    f_tip.material_index = 1
    for l in f_tip.loops: l[uv_b].uv = UV_BLADES

    bm_b.normal_update()
    mesh = bpy.data.meshes.new(name)
    for m in mats: mesh.materials.append(m)
    bm_b.to_mesh(mesh)
    bm_b.free()
    return mesh

def build_asset(export_dir):
    clear_scene()
    setup_units()

    mats = create_materials(export_dir)

    coll = bpy.data.collections.new("SEC_Server_Rack_Fan_Coll")
    bpy.context.scene.collection.children.link(coll)

    # 1. Root Empty at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Server_Rack_Fan", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.12
    root.location = (0.0, 0.0, 0.0)
    coll.objects.link(root)

    # 2. Frame (child of Root)
    mesh_frame = build_fan_frame(mats)
    obj_frame = bpy.data.objects.new("Frame", mesh_frame)
    obj_frame.parent = root
    coll.objects.link(obj_frame)

    mod_f = obj_frame.modifiers.new(name="EdgeSplit", type='EDGE_SPLIT')
    mod_f.split_angle = math.radians(35)

    # 3. Grille (child of Frame)
    mesh_grille = build_fan_grille(mats)
    obj_grille = bpy.data.objects.new("Grille", mesh_grille)
    obj_grille.parent = obj_frame
    coll.objects.link(obj_grille)

    # 4. Fan_Rotation_Pivot Empty at fan center (0.0, 0.012, 0.0)
    fan_center = Vector((0.0, 0.012, 0.0))
    fan_pivot = bpy.data.objects.new("Fan_Rotation_Pivot", None)
    fan_pivot.empty_display_type = 'CIRCLE'
    fan_pivot.empty_display_size = 0.035
    fan_pivot.location = fan_center
    fan_pivot.parent = root
    coll.objects.link(fan_pivot)

    fan_pivot["rot_axis"] = "Y"
    fan_pivot["rotation_type"] = "CONTINUOUS_360"
    fan_pivot["part_type"] = "FAN_ROTOR"

    # 5. Fan_Hub (child of Fan_Rotation_Pivot)
    mesh_hub = build_fan_hub(mats)
    obj_hub = bpy.data.objects.new("Fan_Hub", mesh_hub)
    obj_hub.parent = fan_pivot
    coll.objects.link(obj_hub)

    # 6. Four Blades: Blade_01..04 (children of Fan_Rotation_Pivot)
    blade_objs = []
    for idx in range(4):
        b_name = f"Blade_0{idx + 1}"
        mesh_b = build_single_blade(b_name, mats, idx)
        obj_b = bpy.data.objects.new(b_name, mesh_b)
        obj_b.parent = fan_pivot
        coll.objects.link(obj_b)
        blade_objs.append(obj_b)

    all_meshes = [obj_frame, obj_grille, obj_hub] + blade_objs

    # Calculate total triangles
    total_tris = 0
    for child in all_meshes:
        bm = bmesh.new()
        bm.from_mesh(child.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        m_tris = len(bm.faces)
        total_tris += m_tris
        bm.free()
        print(f"       -> {child.name}: {m_tris} tris")

    print(f"\n[INFO] Total Triangles for SEC_Server_Rack_Fan: {total_tris}")
    assert total_tris <= 380, f"FAIL: Triangle count {total_tris} exceeds budget of 380!"

    os.makedirs(export_dir, exist_ok=True)
    blend_path = os.path.join(export_dir, "SEC_Server_Rack_Fan.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[EXPORT] Saved blend to {blend_path}")

    fbx_path = os.path.join(export_dir, "SEC_Server_Rack_Fan.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=False,
        use_active_collection=False,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        bake_space_transform=False,
        object_types={'EMPTY', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        path_mode='AUTO',
        embed_textures=False,
        batch_mode='OFF'
    )
    print(f"[EXPORT] Saved FBX to {fbx_path}")

    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)

    return total_tris, len(all_meshes), 2

def verify_headless_import(fbx_path, expected_budget=380):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    imported_meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    imported_empties = [o for o in bpy.data.objects if o.type == 'EMPTY']

    total_tris = 0
    assigned_materials = set()
    for obj in imported_meshes:
        me = obj.data
        me.calc_loop_triangles()
        total_tris += len(me.loop_triangles)
        for mat in me.materials:
            if mat: assigned_materials.add(mat.name)

    roots = [o for o in bpy.data.objects if o.parent is None]
    assert len(roots) == 1, f"Expected 1 root, found {len(roots)}"
    assert roots[0].name == "SEC_Server_Rack_Fan", f"Unexpected root: {roots[0].name}"

    assert total_tris <= expected_budget, f"Triangles {total_tris} exceed {expected_budget}"
    assert len(imported_meshes) == 7, f"Expected 7 meshes, got {len(imported_meshes)}"
    assert len(imported_empties) == 2, f"Expected 2 empties, got {len(imported_empties)}"

    frame_obj = bpy.data.objects.get("Frame")
    grille_obj = bpy.data.objects.get("Grille")
    pivot_obj = bpy.data.objects.get("Fan_Rotation_Pivot")
    hub_obj = bpy.data.objects.get("Fan_Hub")

    assert frame_obj and frame_obj.parent == roots[0], "Frame must be child of root"
    assert grille_obj and grille_obj.parent == frame_obj, "Grille must be child of Frame"
    assert pivot_obj and pivot_obj.parent == roots[0], "Fan_Rotation_Pivot must be child of root"
    assert hub_obj and hub_obj.parent == pivot_obj, "Fan_Hub must be child of Fan_Rotation_Pivot"

    for b in range(1, 5):
        bl = bpy.data.objects.get(f"Blade_0{b}")
        assert bl and bl.parent == pivot_obj, f"Blade_0{b} must be child of Fan_Rotation_Pivot"

    print(f"\n[RE-IMPORT QA PASS]")
    print(f"       -> Meshes: {len(imported_meshes)} (Frame, Grille, Fan_Hub, Blade_01..04)")
    print(f"       -> Empties: {len(imported_empties)} (SEC_Server_Rack_Fan, Fan_Rotation_Pivot)")
    print(f"       -> Triangles: {total_tris} (Budget <= {expected_budget})")
    print(f"       -> Materials: {sorted(list(assigned_materials))}")
    print(f"       -> Hierarchy: PASS")
    return total_tris, len(imported_meshes), len(imported_empties), sorted(list(assigned_materials))

def main():
    root_dir = r"C:\Users\Burak\Desktop\Security_CCTV\75. SEC_Server_Rack_Fan"
    export_dir = os.path.join(root_dir, "exports")

    tris, meshes, empties = build_asset(export_dir)
    fbx_file = os.path.join(export_dir, "SEC_Server_Rack_Fan.fbx")

    qa_tris, qa_m, qa_e, qa_mats = verify_headless_import(fbx_file, expected_budget=380)

    manifest_path = os.path.join(export_dir, "manifest.json")
    manifest = {
        "SEC_Server_Rack_Fan": {
            "asset_name": "SEC_Server_Rack_Fan",
            "fbx_path": "exports/SEC_Server_Rack_Fan.fbx",
            "blend_path": "exports/SEC_Server_Rack_Fan.blend",
            "tris_count": qa_tris,
            "mesh_count": qa_m,
            "empty_count": qa_e,
            "materials": qa_mats,
            "status": "SUCCESS"
        }
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[MANIFEST] Updated {manifest_path} with SUCCESS")

if __name__ == "__main__":
    main()
