"""
Security CCTV Asset Production Suite - Asset 64
Asset Name: SEC_Alarm_Strobe_Light (Industrial Fire Alarm Strobe Light)
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

BLEND_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Strobe_Light.blend")
FBX_PATH = os.path.join(EXPORTS_DIR, "SEC_Alarm_Strobe_Light.fbx")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")
ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

MAX_TRIS = 280

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
    bsdf.inputs["Roughness"].default_value = 0.35
    mat_atlas.diffuse_color = (0.85, 0.15, 0.18, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. M_Transparent (Slot 1)
    mat_trans = bpy.data.materials.new(name="M_Transparent")
    mat_trans.use_nodes = True
    bsdf_tr = mat_trans.node_tree.nodes.get("Principled BSDF")
    if os.path.exists(ATLAS_PATH):
        tex_tr = mat_trans.node_tree.nodes.new("ShaderNodeTexImage")
        tex_tr.image = bpy.data.images.get(os.path.basename(ATLAS_PATH)) or bpy.data.images.load(ATLAS_PATH)
        mat_trans.node_tree.links.new(tex_tr.outputs["Color"], bsdf_tr.inputs["Base Color"])
    else:
        bsdf_tr.inputs["Base Color"].default_value = (0.95, 0.25, 0.28, 1.0)
    bsdf_tr.inputs["Roughness"].default_value = 0.08
    if "Alpha" in bsdf_tr.inputs:
        bsdf_tr.inputs["Alpha"].default_value = 0.35
    if "IOR" in bsdf_tr.inputs:
        bsdf_tr.inputs["IOR"].default_value = 1.52
    mat_trans.blend_method = 'BLEND'
    mat_trans.diffuse_color = (0.95, 0.25, 0.28, 0.35)
    materials["M_Transparent"] = mat_trans

    # 3. M_Emission (Slot 2)
    mat_emit = bpy.data.materials.new(name="M_Emission")
    mat_emit.use_nodes = True
    bsdf_emit = mat_emit.node_tree.nodes.get("Principled BSDF")
    bsdf_emit.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_emit.inputs["Emission Color"].default_value = (1.0, 0.98, 0.92, 1.0)
    bsdf_emit.inputs["Emission Strength"].default_value = 12.0
    mat_emit.diffuse_color = (1.0, 1.0, 1.0, 1.0)
    materials["M_Emission"] = mat_emit

    return materials

def assign_material_slots(obj, mat_dict):
    slot_order = ["M_Security_Atlas", "M_Transparent", "M_Emission"]
    for mat_name in slot_order:
        obj.data.materials.append(mat_dict[mat_name])

def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    uv_layer = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv_rect
    xs = [l.vert.co.x for l in face.loops]
    ys = [l.vert.co.y for l in face.loops]
    zs = [l.vert.co.z for l in face.loops]
    
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    dz = max(zs) - min(zs)
    
    if dy > dx and dy > dz:
        min_u_val, max_u_val = min(xs), max(xs)
        min_v_val, max_v_val = min(ys), max(ys)
        u_vals, v_vals = xs, ys
    elif dx >= dz:
        min_u_val, max_u_val = min(xs), max(xs)
        min_v_val, max_v_val = min(zs), max(zs)
        u_vals, v_vals = xs, zs
    else:
        min_u_val, max_u_val = min(ys), max(ys)
        min_v_val, max_v_val = min(zs), max(zs)
        u_vals, v_vals = ys, zs

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

    # Root Empty: SEC_Alarm_Strobe_Light at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Alarm_Strobe_Light", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.12
    bpy.context.collection.objects.link(root)

    uv_swatch_red    = ((250)/2048, 1.0 - 1750/2048)
    uv_swatch_chrome = ((750)/2048, 1.0 - 1750/2048)
    uv_swatch_xenon  = ((1250)/2048, 1.0 - 1750/2048)
    uv_swatch_dark   = ((1750)/2048, 1.0 - 1750/2048)

    # -------------------------------------------------------------------------
    # 1. MOUNT_BASE (Mesh - Child of Root)
    # Circular 16-sided ceiling/wall plate: Y: 0.000 to 0.006, Radius 0.065m
    # -------------------------------------------------------------------------
    base_me = bpy.data.meshes.new("Mount_Base")
    base_bm = bmesh.new()

    segs = 16
    r_base = 0.065
    v_b_bot = []
    v_b_top = []
    for s in range(segs):
        ang = s * (2.0 * math.pi / segs)
        vx = r_base * math.cos(ang)
        vz = r_base * math.sin(ang)
        v_b_bot.append(base_bm.verts.new((vx, 0.000, vz)))
        v_b_top.append(base_bm.verts.new((vx, 0.006, vz)))

    # Back face
    f_b_back = base_bm.faces.new(v_b_bot[::-1])
    f_b_back.material_index = 0
    uv_flange = (1500/2048, 1.0 - 1450/2048, 2000/2048, 1.0 - 800/2048)
    set_face_uv_rect(base_bm, f_b_back, uv_flange)

    # Sides
    for s in range(segs):
        s_next = (s + 1) % segs
        f_bside = base_bm.faces.new([v_b_bot[s], v_b_bot[s_next], v_b_top[s_next], v_b_top[s]])
        f_bside.material_index = 0
        set_face_uv_constant(base_bm, f_bside, uv_swatch_red)

    mark_sharp_edges(base_bm)
    base_bm.to_mesh(base_me)
    base_bm.free()

    base_obj = bpy.data.objects.new("Mount_Base", base_me)
    bpy.context.collection.objects.link(base_obj)
    base_obj.parent = root
    assign_material_slots(base_obj, materials)

    # -------------------------------------------------------------------------
    # 2. BEACON_HOUSING (Mesh - Child of Mount_Base)
    # Red sloped collar: Y: 0.006 to 0.026, Radius 0.062m tapering to 0.052m
    # Retaining rim: Y: 0.026 to 0.030, Radius 0.050m
    # -------------------------------------------------------------------------
    hsg_me = bpy.data.meshes.new("Beacon_Housing")
    hsg_bm = bmesh.new()

    r_c_bot = 0.062
    r_c_top = 0.052
    r_rim   = 0.048
    v_c_bot = []
    v_c_top = []
    v_c_rim = []

    for s in range(segs):
        ang = s * (2.0 * math.pi / segs)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_c_bot.append(hsg_bm.verts.new((r_c_bot * cos_a, 0.006, r_c_bot * sin_a)))
        v_c_top.append(hsg_bm.verts.new((r_c_top * cos_a, 0.026, r_c_top * sin_a)))
        v_c_rim.append(hsg_bm.verts.new((r_rim * cos_a, 0.030, r_rim * sin_a)))

    uv_layer_hsg = hsg_bm.loops.layers.uv.verify()
    u_left = 50 / 2048.0
    u_right = 1450 / 2048.0
    v_bot = 1.0 - 650 / 2048.0
    v_top = 1.0 - 50 / 2048.0

    # Sloped collar with molded FIRE lettering and candela ratings
    for s in range(segs):
        s_next = (s + 1) % segs
        f_cside = hsg_bm.faces.new([v_c_bot[s], v_c_bot[s_next], v_c_top[s_next], v_c_top[s]])
        f_cside.material_index = 0
        u0_seg = u_right - (s / segs) * (u_right - u_left)
        u1_seg = u_right - ((s + 1) / segs) * (u_right - u_left)
        for loop in f_cside.loops:
            if loop.vert == v_c_bot[s]:
                loop[uv_layer_hsg].uv = (u0_seg, v_top)
            elif loop.vert == v_c_bot[s_next]:
                loop[uv_layer_hsg].uv = (u1_seg, v_top)
            elif loop.vert == v_c_top[s_next]:
                loop[uv_layer_hsg].uv = (u1_seg, v_bot)
            elif loop.vert == v_c_top[s]:
                loop[uv_layer_hsg].uv = (u0_seg, v_bot)

        # Bezel rim step
        f_rim = hsg_bm.faces.new([v_c_top[s], v_c_top[s_next], v_c_rim[s_next], v_c_rim[s]])
        f_rim.material_index = 0
        set_face_uv_constant(hsg_bm, f_rim, uv_swatch_red)

    mark_sharp_edges(hsg_bm)
    hsg_bm.to_mesh(hsg_me)
    hsg_bm.free()

    hsg_obj = bpy.data.objects.new("Beacon_Housing", hsg_me)
    bpy.context.collection.objects.link(hsg_obj)
    hsg_obj.parent = base_obj
    assign_material_slots(hsg_obj, materials)

    # -------------------------------------------------------------------------
    # 3. REFLECTOR (Mesh - Child of Beacon_Housing)
    # Parabolic chrome dish inside collar: Y: 0.016 to 0.028, Radius 0.047m to 0.012m
    # -------------------------------------------------------------------------
    ref_me = bpy.data.meshes.new("Reflector")
    ref_bm = bmesh.new()

    v_dish_rim = []
    v_dish_bot = []
    r_dish_rim = 0.047
    r_dish_bot = 0.012

    for s in range(segs):
        ang = s * (2.0 * math.pi / segs)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_dish_rim.append(ref_bm.verts.new((r_dish_rim * cos_a, 0.028, r_dish_rim * sin_a)))
        v_dish_bot.append(ref_bm.verts.new((r_dish_bot * cos_a, 0.016, r_dish_bot * sin_a)))

    uv_layer_ref = ref_bm.loops.layers.uv.verify()
    u_c = 1750.0 / 2048.0
    v_c = 1.0 - 400.0 / 2048.0
    s_uv = (210.0 / 2048.0) / r_dish_rim

    for s in range(segs):
        s_next = (s + 1) % segs
        f_d1 = ref_bm.faces.new([v_dish_rim[s], v_dish_rim[s_next], v_dish_bot[s_next], v_dish_bot[s]])
        f_d1.material_index = 0
        for loop in f_d1.loops:
            loop[uv_layer_ref].uv = (u_c + loop.vert.co.x * s_uv, v_c + loop.vert.co.z * s_uv)

    v_center_dish = ref_bm.verts.new((0.0, 0.016, 0.0))
    for s in range(segs):
        s_next = (s + 1) % segs
        f_db = ref_bm.faces.new([v_dish_bot[s], v_dish_bot[s_next], v_center_dish])
        f_db.material_index = 0
        for loop in f_db.loops:
            loop[uv_layer_ref].uv = (u_c + loop.vert.co.x * s_uv, v_c + loop.vert.co.z * s_uv)

    mark_sharp_edges(ref_bm)
    ref_bm.to_mesh(ref_me)
    ref_bm.free()

    ref_obj = bpy.data.objects.new("Reflector", ref_me)
    bpy.context.collection.objects.link(ref_obj)
    ref_obj.parent = hsg_obj
    assign_material_slots(ref_obj, materials)

    # -------------------------------------------------------------------------
    # 4. LED_CORE (Mesh - Child of Beacon_Housing)
    # Xenon flash column at center: Y: 0.018 to 0.044, Radius 0.008m (8 sides)
    # -------------------------------------------------------------------------
    core_me = bpy.data.meshes.new("LED_Core")
    core_bm = bmesh.new()

    c_segs = 8
    r_core = 0.008
    v_c0 = []
    v_c1 = []
    for s in range(c_segs):
        ang = s * (2.0 * math.pi / c_segs)
        v_c0.append(core_bm.verts.new((r_core * math.cos(ang), 0.018, r_core * math.sin(ang))))
        v_c1.append(core_bm.verts.new((r_core * math.cos(ang), 0.044, r_core * math.sin(ang))))

    for s in range(c_segs):
        s_next = (s + 1) % c_segs
        f_core = core_bm.faces.new([v_c0[s], v_c0[s_next], v_c1[s_next], v_c1[s]])
        f_core.material_index = 2 # M_Emission
        set_face_uv_constant(core_bm, f_core, uv_swatch_xenon)

    f_core_cap = core_bm.faces.new(v_c1)
    f_core_cap.material_index = 2
    set_face_uv_constant(core_bm, f_core_cap, uv_swatch_xenon)

    mark_sharp_edges(core_bm)
    core_bm.to_mesh(core_me)
    core_bm.free()

    core_obj = bpy.data.objects.new("LED_Core", core_me)
    bpy.context.collection.objects.link(core_obj)
    core_obj.parent = hsg_obj
    assign_material_slots(core_obj, materials)

    # -------------------------------------------------------------------------
    # 5. LENS_COVER (Mesh - Child of Beacon_Housing)
    # Transparent Fresnel refractive optical dome: Y: 0.026 to 0.054, Radius 0.049m
    # -------------------------------------------------------------------------
    lens_me = bpy.data.meshes.new("Lens_Cover")
    lens_bm = bmesh.new()

    r_lens_base = 0.049
    r_lens_dome = 0.042
    r_lens_tip  = 0.022
    y_l0 = 0.026
    y_l1 = 0.046
    y_l2 = 0.054

    v_l0 = []
    v_l1 = []
    v_l2 = []

    for s in range(segs):
        ang = s * (2.0 * math.pi / segs)
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        v_l0.append(lens_bm.verts.new((r_lens_base * cos_a, y_l0, r_lens_base * sin_a)))
        v_l1.append(lens_bm.verts.new((r_lens_dome * cos_a, y_l1, r_lens_dome * sin_a)))
        v_l2.append(lens_bm.verts.new((r_lens_tip * cos_a, y_l2, r_lens_tip * sin_a)))

    v_l_apex = lens_bm.verts.new((0.0, 0.056, 0.0))

    uv_fresnel = (50/2048, 1.0 - 1450/2048, 1450/2048, 1.0 - 720/2048)

    # Fresnel cylindrical prism barrel
    for s in range(segs):
        s_next = (s + 1) % segs
        f_lb1 = lens_bm.faces.new([v_l0[s], v_l0[s_next], v_l1[s_next], v_l1[s]])
        f_lb1.material_index = 1 # M_Transparent
        set_face_uv_rect(lens_bm, f_lb1, uv_fresnel)

        # Fresnel domed crown
        f_lb2 = lens_bm.faces.new([v_l1[s], v_l1[s_next], v_l2[s_next], v_l2[s]])
        f_lb2.material_index = 1
        set_face_uv_rect(lens_bm, f_lb2, uv_fresnel)

        # Apex cap
        f_lb3 = lens_bm.faces.new([v_l2[s], v_l2[s_next], v_l_apex])
        f_lb3.material_index = 1
        set_face_uv_rect(lens_bm, f_lb3, uv_fresnel)

    mark_sharp_edges(lens_bm)
    lens_bm.to_mesh(lens_me)
    lens_bm.free()

    lens_obj = bpy.data.objects.new("Lens_Cover", lens_me)
    bpy.context.collection.objects.link(lens_obj)
    lens_obj.parent = hsg_obj
    assign_material_slots(lens_obj, materials)

    # -------------------------------------------------------------------------
    # QA Check & Triangulation
    # -------------------------------------------------------------------------
    total_tris = 0
    meshes = [base_obj, hsg_obj, ref_obj, core_obj, lens_obj]
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

    # Set smooth shading
    for obj in [hsg_obj, ref_obj, lens_obj]:
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
    reimp_tris = 0
    for o in reimp_meshes:
        m = o.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(m)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        reimp_tris += len(bm.faces)
        bm.free()
        o.to_mesh_clear()

    print(f"[QA Reimport] Meshes: {len(reimp_meshes)}, Tris: {reimp_tris}")
    assert len(reimp_meshes) == 5, f"Mesh count mismatch: {len(reimp_meshes)} != 5"
    assert reimp_tris <= MAX_TRIS, f"Re-imported tris exceed budget: {reimp_tris} > {MAX_TRIS}"

    # Manifest update
    manifest = {
        "SEC_Alarm_Strobe_Light": {
            "status": "SUCCESS",
            "fbx_path": FBX_PATH,
            "blend_path": BLEND_PATH,
            "total_tris": total_tris,
            "max_tris": MAX_TRIS,
            "mesh_count": len(meshes),
            "empty_count": 1,
            "materials": ["M_Security_Atlas", "M_Transparent", "M_Emission"]
        }
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    print(f"[Manifest] Updated {MANIFEST_PATH} with status SUCCESS")

if __name__ == "__main__":
    build_scene()
