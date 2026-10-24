"""
=============================================================================
Security CCTV Asset Production Suite - Asset 34
Asset Name: SEC_Sensor_Glass_Break (Cam Kırılma Dedektörü)
Production Script: BMesh Construction, Accurate UV Mapping, FBX Export, Re-import QA

SPECIFICATION REQUIREMENTS:
- Root Object: 'SEC_Sensor_Glass_Break' (Empty at 0, 0, 0)
- Hierarchy:
    SEC_Sensor_Glass_Break (Root Empty at 0, 0, 0)
      ├── Backplate (Mesh - child of Root)
      └── Sensor_Housing (Mesh - child of Root)
           ├── Microphone_Grille (Mesh - child of Sensor_Housing)
           └── Status_LED (Mesh - child of Sensor_Housing)
- Materials:
    Slot 0: M_Security_Atlas
    Slot 1: M_Emission
- Triangle Budget: Max 240 tris (Strict Ceiling)
- Dimensions: 60mm x 104mm x 21.5mm (True industrial scale)
- Standard Orientation: Wall-mounted at Y=0, facing +Y into room.
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
import math
import os
import json

ATLAS_W = 2048
ATLAS_H = 2048

def uv_rect_from_pixels(x0, y0, x1, y1):
    """Converts pixel box (x0, y0, x1, y1) in PIL coordinates to Blender UV (u0, v0, u1, v1)."""
    return (x0 / ATLAS_W, 1.0 - (y1 / ATLAS_H), x1 / ATLAS_W, 1.0 - (y0 / ATLAS_H))

# Exact UV regions from T_Security_Atlas.png (v3 2048x2048 architecture)
RECT_FRONT      = uv_rect_from_pixels(48, 48, 968, 1628)     # 920 x 1580 px (Front Housing)
RECT_BACK       = uv_rect_from_pixels(1080, 48, 2000, 1640)  # 920 x 1592 px (Backplate Label)
RECT_MIC_GRILLE = uv_rect_from_pixels(48, 1680, 408, 2000)   # 360 x 320 px (Acoustic Mesh)
RECT_LED_LENS   = uv_rect_from_pixels(448, 1680, 788, 2000)  # 340 x 320 px (Status Lens)

FLAT_UV_WHITE   = (970 / ATLAS_W, 1.0 - 1830 / ATLAS_H)
FLAT_UV_BEVEL   = (1270 / ATLAS_W, 1.0 - 1830 / ATLAS_H)
FLAT_UV_DARK    = (1570 / ATLAS_W, 1.0 - 1830 / ATLAS_H)
FLAT_UV_METAL   = (1870 / ATLAS_W, 1.0 - 1830 / ATLAS_H)

def set_face_uv_rect(face, uv_layer, rect, flip_u=False, bbox=None):
    """
    Maps face loops proportionally onto the given UV rectangle.
    flip_u: True for faces with +Y normal (viewer in room looks towards -Y, world +X is left).
            False for faces with -Y normal (viewer looks towards +Y, world -X is left).
    """
    u0, v0, u1, v1 = rect
    if bbox is not None:
        minx, maxx, minz, maxz = bbox
    else:
        xs = [loop.vert.co.x for loop in face.loops]
        zs = [loop.vert.co.z for loop in face.loops]
        minx, maxx = min(xs), max(xs)
        minz, maxz = min(zs), max(zs)

    dx = (maxx - minx) if (maxx - minx) > 1e-9 else 1.0
    dz = (maxz - minz) if (maxz - minz) > 1e-9 else 1.0

    for loop in face.loops:
        nx = (loop.vert.co.x - minx) / dx
        nz = (loop.vert.co.z - minz) / dz
        u = (u1 - nx * (u1 - u0)) if flip_u else (u0 + nx * (u1 - u0))
        v = v0 + nz * (v1 - v0)
        loop[uv_layer].uv = (u, v)

def set_flat_uv(face, uv_layer, point=FLAT_UV_BEVEL):
    for loop in face.loops:
        loop[uv_layer].uv = point

def mark_sharp_edges_by_angle(bm, threshold_deg=35.0):
    bm.normal_update()
    rad = math.radians(threshold_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            f1, f2 = edge.link_faces
            if f1.normal.length > 1e-6 and f2.normal.length > 1e-6:
                ang = f1.normal.angle(f2.normal)
                if ang > rad:
                    edge.smooth = False
        elif len(edge.link_faces) == 1:
            edge.smooth = False

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
        img = bpy.data.images.load(tex_atlas_path)
        try:
            img.pack()
        except Exception:
            pass
        tex_node = nodes.new("ShaderNodeTexImage")
        tex_node.image = img
        links.new(tex_node.outputs["Color"], bsdf_atlas.inputs["Base Color"])

    bsdf_atlas.inputs["Roughness"].default_value = 0.32
    bsdf_atlas.inputs["Metallic"].default_value = 0.05

    # Slot 1: M_Emission
    mat_emission = bpy.data.materials.new("M_Emission")
    mat_emission.use_nodes = True
    nodes_em = mat_emission.node_tree.nodes
    bsdf_em = nodes_em.get("Principled BSDF")

    em_col = (0.12, 0.95, 0.30, 1.0)
    if "Base Color" in bsdf_em.inputs:
        bsdf_em.inputs["Base Color"].default_value = em_col
    if "Emission Color" in bsdf_em.inputs:
        bsdf_em.inputs["Emission Color"].default_value = em_col
    elif "Emission" in bsdf_em.inputs:
        bsdf_em.inputs["Emission"].default_value = em_col
    if "Emission Strength" in bsdf_em.inputs:
        bsdf_em.inputs["Emission Strength"].default_value = 5.0

    return [mat_atlas, mat_emission]

def build_backplate(mats):
    """
    Backplate: Wall-mount base plate flush against wall at Y=0.0.
    Dimensions: X: -0.030..+0.030 (60mm), Z: -0.052..+0.052 (104mm), Y: 0.0..0.0035.
    45° Chamfered corners (c = 0.006m).
    Rear face (-Y normal) maps to RECT_BACK (flip_u=False) with zero mirroring.
    Perimeter bevels map to FLAT_UV_BEVEL.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    dx, dz = 0.030, 0.052
    c = 0.006
    y0, y1 = 0.0, 0.0035

    profile_2d = [
        Vector((-dx + c, 0.0, -dz)),
        Vector(( dx - c, 0.0, -dz)),
        Vector(( dx,     0.0, -dz + c)),
        Vector(( dx,     0.0,  dz - c)),
        Vector(( dx - c, 0.0,  dz)),
        Vector((-dx + c, 0.0,  dz)),
        Vector((-dx,     0.0,  dz - c)),
        Vector((-dx,     0.0, -dz + c))
    ]

    v_back = [bm.verts.new(Vector((p.x, y0, p.z))) for p in profile_2d]
    v_front = [bm.verts.new(Vector((p.x, y1, p.z))) for p in profile_2d]

    # Rear face against wall (-Y normal)
    # v_back winding [0..7] has normal -Y
    f_rear = bm.faces.new(v_back)
    f_rear.smooth = False
    f_rear.material_index = 0
    set_face_uv_rect(f_rear, uv_layer, RECT_BACK, flip_u=False, bbox=(-dx, dx, -dz, dz))

    # Front mating face (+Y normal)
    f_front = bm.faces.new(list(reversed(v_front)))
    f_front.smooth = False
    f_front.material_index = 0
    set_flat_uv(f_front, uv_layer, FLAT_UV_BEVEL)

    # 8 perimeter sides
    n_p = len(profile_2d)
    for i in range(n_p):
        i_next = (i + 1) % n_p
        f = bm.faces.new((v_back[i], v_back[i_next], v_front[i_next], v_front[i]))
        f.smooth = False
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BEVEL)

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.normal_update()

    mesh = bpy.data.meshes.new("Backplate")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Backplate", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_sensor_housing(mats):
    """
    Sensor_Housing: Ergonomic chamfered front sensor enclosure.
    Extends from Y=0.0035 to Y=0.0215 (18mm depth).
    Features a clean two-stage ergonomic contour:
      Base:  X: -0.029..+0.029 (58mm), Z: -0.051..+0.051 (102mm) at Y=0.0035.
      Mid:   X: -0.0275..+0.0275 (55mm), Z: -0.0485..+0.0485 (97mm) at Y=0.0140.
      Front: X: -0.026..+0.026 (52mm), Z: -0.046..+0.046 (92mm) at Y=0.0215.
    Front face (+Y normal) is a clean single beveled polygon mapping to RECT_FRONT (flip_u=True).
    Slot 0: M_Security_Atlas, Slot 1: M_Emission.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    dx0, dz0, c0 = 0.029, 0.051, 0.006
    dx_mid, dz_mid, c_mid = 0.0275, 0.0485, 0.0055
    dx1, dz1, c1 = 0.026, 0.046, 0.005

    y_base = 0.0035
    y_mid  = 0.0140
    y_front = 0.0215

    def make_profile(dx, dz, c, y):
        return [
            Vector((-dx + c, y, -dz)),
            Vector(( dx - c, y, -dz)),
            Vector(( dx,     y, -dz + c)),
            Vector(( dx,     y,  dz - c)),
            Vector(( dx - c, y,  dz)),
            Vector((-dx + c, y,  dz)),
            Vector((-dx,     y,  dz - c)),
            Vector((-dx,     y, -dz + c))
        ]

    p_base = make_profile(dx0, dz0, c0, y_base)
    p_mid  = make_profile(dx_mid, dz_mid, c_mid, y_mid)
    p_front = make_profile(dx1, dz1, c1, y_front)

    v_base = [bm.verts.new(p) for p in p_base]
    v_mid  = [bm.verts.new(p) for p in p_mid]
    v_front = [bm.verts.new(p) for p in p_front]

    # Lower stage side quads (base to mid)
    n_p = len(p_base)
    for i in range(n_p):
        i_next = (i + 1) % n_p
        f = bm.faces.new((v_base[i], v_base[i_next], v_mid[i_next], v_mid[i]))
        f.smooth = True
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_WHITE)

    # Upper stage side quads (mid to front)
    for i in range(n_p):
        i_next = (i + 1) % n_p
        f = bm.faces.new((v_mid[i], v_mid[i_next], v_front[i_next], v_front[i]))
        f.smooth = True
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_BEVEL)

    # Front Face (+Y normal) - Single pristine planar beveled face!
    # reversed(v_front) gives normal strictly +Y (0, 1, 0)
    f_front = bm.faces.new(list(reversed(v_front)))
    f_front.smooth = False
    f_front.material_index = 0
    set_face_uv_rect(f_front, uv_layer, RECT_FRONT, flip_u=True, bbox=(-dx1, dx1, -dz1, dz1))

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.normal_update()

    mesh = bpy.data.meshes.new("Sensor_Housing")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Sensor_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_microphone_grille(mats):
    """
    Microphone_Grille: Recessed acoustic intake port and electret microphone chamber.
    Centered at (0.0, 0.0215, -0.018).
    14-radial concentric acoustic horn geometry:
      Outer base rim: radius 0.0115m at Y=0.0215 (flush with housing front face)
      Raised bezel ridge: radius 0.0098m at Y=0.0236
      Recessed acoustic floor: radius 0.0075m at Y=0.0225 (proud of front face, zero clipping)
      Center electret diaphragm: radius 0.0m at Y=0.0220
    Mapped to RECT_MIC_GRILLE.
    Slot 0: M_Security_Atlas.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 14
    cz_pos = -0.018
    r_outer = 0.0115
    r_rim   = 0.0098
    r_floor = 0.0075
    y_base  = 0.0215
    y_rim   = 0.0236
    y_floor = 0.0225
    y_center = 0.0220

    v_base  = []
    v_rim   = []
    v_floor = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / float(n_radial))
        ca, sa = math.cos(ang), math.sin(ang)
        v_base.append(bm.verts.new(Vector((ca * r_outer, y_base, cz_pos + sa * r_outer))))
        v_rim.append(bm.verts.new(Vector((ca * r_rim, y_rim, cz_pos + sa * r_rim))))
        v_floor.append(bm.verts.new(Vector((ca * r_floor, y_floor, cz_pos + sa * r_floor))))

    v_center = bm.verts.new(Vector((0.0, y_center, cz_pos)))

    u0, v0, u1, v1 = RECT_MIC_GRILLE
    cu = (u0 + u1) / 2.0
    cv = (v0 + v1) / 2.0
    r_uv = (u1 - u0) / 2.0 * 0.95

    # Outer bevel collar (base to rim)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_base[i], v_rim[i], v_rim[i_next], v_base[i_next]))
        f.smooth = True
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    # Inset acoustic baffle slope (rim to floor)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_rim[i], v_floor[i], v_floor[i_next], v_rim[i_next]))
        f.smooth = True
        f.material_index = 0
        ang0 = i * (2.0 * math.pi / float(n_radial))
        ang1 = (i + 1) * (2.0 * math.pi / float(n_radial))
        for loop in f.loops:
            is_rim = loop.vert in (v_rim[i], v_rim[i_next])
            rad = r_uv if is_rim else (r_uv * 0.65)
            ang = ang0 if loop.vert in (v_rim[i], v_floor[i]) else ang1
            loop[uv_layer].uv = (cu - rad * math.cos(ang), cv + rad * math.sin(ang))

    # Center electret diaphragm fan (floor to center)
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_floor[i], v_center, v_floor[i_next]))
        f.smooth = True
        f.material_index = 0
        ang0 = i * (2.0 * math.pi / float(n_radial))
        ang1 = (i + 1) * (2.0 * math.pi / float(n_radial))
        for loop in f.loops:
            if loop.vert == v_center:
                loop[uv_layer].uv = (cu, cv)
            elif loop.vert == v_floor[i]:
                loop[uv_layer].uv = (cu - r_uv * 0.65 * math.cos(ang0), cv + r_uv * 0.65 * math.sin(ang0))
            else:
                loop[uv_layer].uv = (cu - r_uv * 0.65 * math.cos(ang1), cv + r_uv * 0.65 * math.sin(ang1))

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.normal_update()

    mesh = bpy.data.meshes.new("Microphone_Grille")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Microphone_Grille", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_status_led(mats):
    """
    Status_LED: Dual bi-color indicator lens (Green Power/Armed + Red Alarm).
    Pill/oval beveled lens located at (0.0, 0.0215, 0.010).
    Dimensions: Width: 9.6mm (X: -0.0048..+0.0048), Height: 5.0mm (Z: 0.0075..0.0125).
    Lens domed apex at Y=0.0232 (protrudes 1.7mm past housing face).
    Perimeter rim: Slot 0 (M_Security_Atlas), dark bezel.
    Lens cap: Slot 1 (M_Emission), glowing bi-color indicator.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")

    cz = 0.010
    rx = 0.0048
    rz = 0.0025
    y_base = 0.0215
    y_rim  = 0.0225
    y_apex = 0.0233
    n_pts = 12

    v_base = []
    v_rim  = []
    for i in range(n_pts):
        ang = i * (2.0 * math.pi / float(n_pts))
        vx = math.cos(ang) * rx
        vz = math.sin(ang) * rz
        v_base.append(bm.verts.new(Vector((vx, y_base, cz + vz))))
        v_rim.append(bm.verts.new(Vector((vx * 0.88, y_rim, cz + vz * 0.88))))

    # Side bevel collar (Slot 0 M_Security_Atlas)
    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        f = bm.faces.new((v_base[i], v_rim[i], v_rim[i_next], v_base[i_next]))
        f.smooth = True
        f.material_index = 0
        set_flat_uv(f, uv_layer, FLAT_UV_DARK)

    # Top domed emitting cap (Slot 1 M_Emission)
    v_cap_center = bm.verts.new(Vector((0.0, y_apex, cz)))
    u0, v0, u1, v1 = RECT_LED_LENS
    cu = (u0 + u1) / 2.0
    cv = (v0 + v1) / 2.0

    for i in range(n_pts):
        i_next = (i + 1) % n_pts
        f = bm.faces.new((v_rim[i], v_cap_center, v_rim[i_next]))
        f.smooth = True
        f.material_index = 1 # M_Emission
        ang0 = i * (2.0 * math.pi / float(n_pts))
        ang1 = (i + 1) * (2.0 * math.pi / float(n_pts))
        for loop in f.loops:
            if loop.vert == v_cap_center:
                loop[uv_layer].uv = (cu, cv)
            elif loop.vert == v_rim[i]:
                loop[uv_layer].uv = (cu - 0.07 * math.cos(ang0), cv + 0.07 * math.sin(ang0))
            else:
                loop[uv_layer].uv = (cu - 0.07 * math.cos(ang1), cv + 0.07 * math.sin(ang1))

    mark_sharp_edges_by_angle(bm, 35.0)
    bm.normal_update()

    mesh = bpy.data.meshes.new("Status_LED")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Status_LED", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def main():
    # 1. Clean scene
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

    # 2. Setup Materials
    mats = setup_materials()

    # 3. Create Root Empty: SEC_Sensor_Glass_Break at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Sensor_Glass_Break", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root)

    # 4. Build Hierarchy
    backplate = build_backplate(mats)
    backplate.parent = root

    housing = build_sensor_housing(mats)
    housing.parent = root

    grille = build_microphone_grille(mats)
    grille.parent = housing

    led = build_status_led(mats)
    led.parent = housing

    # 5. Save .blend file (force all screens & viewports to MATERIAL preview)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'
                        try:
                            space.shading.color_type = 'TEXTURE'
                        except Exception:
                            pass

    blend_path = os.path.join(exports_dir, "SEC_Sensor_Glass_Break.blend")
    fbx_path = os.path.join(exports_dir, "SEC_Sensor_Glass_Break.fbx")

    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Remove automatic .blend1 if created
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[CLEAN] Removed backup: {blend1_path}")

    # 6. Select hierarchy for FBX export
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root

    # 7. FBX Export
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
    # 8. HEADLESS QA VERIFICATION TEST (Strict Re-import Check)
    # -------------------------------------------------------------
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 34) ---")
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for m in list(bpy.data.meshes):
        bpy.data.meshes.remove(m)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    re_root = bpy.data.objects.get("SEC_Sensor_Glass_Break")
    assert re_root is not None, "FAIL: Root SEC_Sensor_Glass_Break missing in FBX"

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
    assert total_tris <= 240, f"FAIL: Total triangles {total_tris} exceeds 240 budget!"
    print("[PASS] Triangle count verified strictly (<= 240)!")

    # Verify hierarchy
    re_back = bpy.data.objects.get("Backplate")
    re_housing = bpy.data.objects.get("Sensor_Housing")
    re_grille = bpy.data.objects.get("Microphone_Grille")
    re_led = bpy.data.objects.get("Status_LED")

    assert re_back and re_back.parent == re_root, "FAIL: Backplate parent mismatch"
    assert re_housing and re_housing.parent == re_root, "FAIL: Sensor_Housing parent mismatch"
    assert re_grille and re_grille.parent == re_housing, "FAIL: Microphone_Grille parent mismatch"
    assert re_led and re_led.parent == re_housing, "FAIL: Status_LED parent mismatch"
    print("[PASS] Full parent-child hierarchy strictly verified!")

    # Verify Material Slots
    expected_mats = ["M_Security_Atlas", "M_Emission"]
    for m_obj in [re_back, re_housing, re_grille, re_led]:
        m_names = [slot.material.name.split('.')[0] for slot in m_obj.material_slots if slot.material]
        for em in expected_mats:
            assert em in m_names, f"FAIL: {m_obj.name} missing material {em}"
    print("[PASS] Material slots strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest = {
        "SEC_Sensor_Glass_Break": {
            "asset_name": "SEC_Sensor_Glass_Break",
            "fbx_path": "exports/SEC_Sensor_Glass_Break.fbx",
            "blend_path": "exports/SEC_Sensor_Glass_Break.blend",
            "tris_count": total_tris,
            "mesh_count": len(mesh_names),
            "empty_count": len(empty_names) + 1, # include root empty
            "materials": expected_mats,
            "status": "SUCCESS"
        }
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Updated manifest: {manifest_path}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")

    # Clean backup .blend1 if created
    if os.path.exists(blend1_path):
        os.remove(blend1_path)

if __name__ == "__main__":
    main()
