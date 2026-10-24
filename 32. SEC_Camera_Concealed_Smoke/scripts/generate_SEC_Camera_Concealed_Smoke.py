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
    """
    mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes = mat_atlas.node_tree.nodes
    links = mat_atlas.node_tree.links
    nodes.clear()

    out_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs['Roughness'].default_value = 0.35
    bsdf.inputs['Metallic'].default_value = 0.08

    if os.path.exists(atlas_path):
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(atlas_path)
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.92, 0.94, 0.95, 1.0)
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

    return [mat_atlas, mat_glass]

def build_detector_housing(mats):
    """
    Detector_Housing: Circular ceiling smoke detector body flush at Z=0.
    16-radial smooth contour with ceiling flange, upper skirt, lower conical dome,
    and recessed center cavity for covert camera pinhole.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16

    # Upper housing stations along -Z:
    # 0: Z= 0.000, r=0.060 (ceiling contact base)
    # 1: Z=-0.007, r=0.060 (vertical twist-lock rim)
    # 2: Z=-0.016, r=0.048 (upper conical skirt leading to vent)
    upper_stations = [
        ( 0.000, 0.060),
        (-0.007, 0.060),
        (-0.016, 0.048)
    ]
    u_rings = []
    for z_pos, r_rad in upper_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        u_rings.append(ring)

    # Ceiling back cap (facing +Z)
    f_ceil = bm.faces.new(reversed(u_rings[0]))
    f_ceil.smooth = False; f_ceil.material_index = 0
    for loop in f_ceil.loops: loop[uv_layer].uv = (0.25, 0.75)

    cu, cv = 0.25, 0.75 # Quadrant 1 in atlas
    for s in range(len(upper_stations) - 1):
        r_a = u_rings[s]
        r_b = u_rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]; vb = r_a[i_next]; vc = r_b[i_next]; vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True; f.material_index = 0
            ang0 = i * (2.0 * math.pi / n_radial)
            ang1 = (i + 1) * (2.0 * math.pi / n_radial)
            r_uv_a = 0.23 if s == 0 else 0.21
            r_uv_b = 0.21 if s == 0 else 0.17
            for loop in f.loops:
                r_uv = r_uv_a if loop.vert in (va, vb) else r_uv_b
                loop_ang = ang0 if loop.vert in (va, vd) else ang1
                loop[uv_layer].uv = (cu - r_uv * math.cos(loop_ang), cv + r_uv * math.sin(loop_ang))

    # Lower housing stations along -Z (below Vent_Ring):
    # 0: Z=-0.024, r=0.048 (lower vent intake shelf)
    # 1: Z=-0.033, r=0.034 (main convex dome)
    # 2: Z=-0.037, r=0.014 (recessed center optic cavity rim)
    lower_stations = [
        (-0.024, 0.048),
        (-0.033, 0.034),
        (-0.037, 0.014)
    ]
    l_rings = []
    for z_pos, r_rad in lower_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        l_rings.append(ring)

    for s in range(len(lower_stations) - 1):
        r_a = l_rings[s]
        r_b = l_rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]; vb = r_a[i_next]; vc = r_b[i_next]; vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True; f.material_index = 0
            ang0 = i * (2.0 * math.pi / n_radial)
            ang1 = (i + 1) * (2.0 * math.pi / n_radial)
            rad_uv_a = 0.17 if s == 0 else 0.12
            rad_uv_b = 0.12 if s == 0 else 0.05
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (cu - rad_uv_a * math.cos(ang0), cv + rad_uv_a * math.sin(ang0))
                elif loop.vert == vb: loop[uv_layer].uv = (cu - rad_uv_a * math.cos(ang1), cv + rad_uv_a * math.sin(ang1))
                elif loop.vert == vc: loop[uv_layer].uv = (cu - rad_uv_b * math.cos(ang1), cv + rad_uv_b * math.sin(ang1))
                elif loop.vert == vd: loop[uv_layer].uv = (cu - rad_uv_b * math.cos(ang0), cv + rad_uv_b * math.sin(ang0))

    bm.normal_update()
    mesh = bpy.data.meshes.new("Detector_Housing")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Detector_Housing", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_vent_ring(mats):
    """
    Vent_Ring: 360-degree smoke intake labyrinth chamber vents.
    Recessed perimeter band between Z=-0.016 and Z=-0.024.
    Slot 0: M_Security_Atlas (Mapped to Quadrant 2 dark louver mesh).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16

    r_top = 0.045
    r_bot = 0.045
    z_top = -0.016
    z_bot = -0.024

    ring_top = []
    ring_bot = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        vx = math.cos(ang)
        vy = math.sin(ang)
        ring_top.append(bm.verts.new(Vector((vx * r_top, vy * r_top, z_top))))
        ring_bot.append(bm.verts.new(Vector((vx * r_bot, vy * r_bot, z_bot))))

    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        va = ring_top[i]; vb = ring_top[i_next]; vc = ring_bot[i_next]; vd = ring_bot[i]
        f = bm.faces.new((va, vd, vc, vb))
        f.smooth = True; f.material_index = 0
        u0 = 0.52 + (i / float(n_radial)) * 0.46
        u1 = 0.52 + ((i + 1) / float(n_radial)) * 0.46
        for loop in f.loops:
            u_val = u0 if loop.vert in (va, vd) else u1
            v_val = 0.95 if loop.vert in (va, vb) else 0.55
            loop[uv_layer].uv = (u_val, v_val)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Vent_Ring")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Vent_Ring", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_insert(mats):
    """
    Lens_Insert: Covert pinhole camera aperture bezel.
    Center recessed disc at Z=-0.037 to -0.041, outer radius 0.014 to inner pinhole 0.0035.
    Slot 0: M_Security_Atlas.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 8

    insert_stations = [
        (-0.037, 0.014),
        (-0.039, 0.008),
        (-0.041, 0.0035)
    ]
    rings = []
    for z_pos, r_rad in insert_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        rings.append(ring)

    cu, cv = 0.25, 0.25 # Quadrant 3 in atlas
    for s in range(len(insert_stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]; vb = r_a[i_next]; vc = r_b[i_next]; vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True; f.material_index = 0
            ang0 = i * (2.0 * math.pi / n_radial)
            ang1 = (i + 1) * (2.0 * math.pi / n_radial)
            rad_uv_a = 0.16 if s == 0 else 0.09
            rad_uv_b = 0.09 if s == 0 else 0.04
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (cu - rad_uv_a * math.cos(ang0), cv + rad_uv_a * math.sin(ang0))
                elif loop.vert == vb: loop[uv_layer].uv = (cu - rad_uv_a * math.cos(ang1), cv + rad_uv_a * math.sin(ang1))
                elif loop.vert == vc: loop[uv_layer].uv = (cu - rad_uv_b * math.cos(ang1), cv + rad_uv_b * math.sin(ang1))
                elif loop.vert == vd: loop[uv_layer].uv = (cu - rad_uv_b * math.cos(ang0), cv + rad_uv_b * math.sin(ang0))

    bm.normal_update()
    mesh = bpy.data.meshes.new("Lens_Insert")
    for m in mats: mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Lens_Insert", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_glass(mats):
    """
    Lens_Glass: Miniature covert optical pinhole lens element.
    Convex dome from Z=-0.041 to Z=-0.0425, radius 0.0035m.
    Slot 1: M_Lens_Glass.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 8
    r_lens = 0.0035

    v_ring = []
    for i in range(n_radial):
        ang = i * (2.0 * math.pi / n_radial)
        vx = math.cos(ang) * r_lens
        vy = math.sin(ang) * r_lens
        v_ring.append(bm.verts.new(Vector((vx, vy, -0.041))))

    v_apex = bm.verts.new(Vector((0.0, 0.0, -0.0425)))
    bm.verts.ensure_lookup_table()

    cu, cv = 0.75, 0.25 # Quadrant 4 in atlas
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((v_ring[i], v_apex, v_ring[i_next]))
        f.smooth = True; f.material_index = 1
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        for loop in f.loops:
            if loop.vert == v_ring[i]: loop[uv_layer].uv = (cu + 0.08 * math.cos(ang0), cv + 0.08 * math.sin(ang0))
            elif loop.vert == v_ring[i_next]: loop[uv_layer].uv = (cu + 0.08 * math.cos(ang1), cv + 0.08 * math.sin(ang1))
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
    """Build full SEC_Camera_Concealed_Smoke hierarchy and run headless QA."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mats = create_materials(atlas_path)

    # 1. Root Empty: SEC_Camera_Concealed_Smoke at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Camera_Concealed_Smoke", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.05
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 2. Detector_Housing (Child of Root)
    housing = build_detector_housing(mats)
    housing.parent = root

    # 3. Vent_Ring (Child of Detector_Housing)
    vent = build_vent_ring(mats)
    vent.parent = housing

    # 4. Lens_Insert (Child of Detector_Housing)
    insert = build_lens_insert(mats)
    insert.parent = housing

    # 5. Lens_Glass (Child of Lens_Insert)
    lens = build_lens_glass(mats)
    lens.parent = insert

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Camera_Concealed_Smoke.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Concealed_Smoke.fbx")
    export_fbx(root, [housing, vent, insert, lens], fbx_path)

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
    """Import FBX into clean scene and verify tris, hierarchy, materials, UVs."""
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 32) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Camera_Concealed_Smoke")
    assert root is not None, "FAIL: Root object 'SEC_Camera_Concealed_Smoke' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    housing = bpy.data.objects.get("Detector_Housing")
    assert housing is not None, "FAIL: Detector_Housing missing!"
    assert housing.parent == root, "FAIL: Detector_Housing parent != root!"

    expected_meshes = {
        "Detector_Housing",
        "Vent_Ring",
        "Lens_Insert",
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

    vent = bpy.data.objects.get("Vent_Ring")
    insert = bpy.data.objects.get("Lens_Insert")
    lens = bpy.data.objects.get("Lens_Glass")

    assert vent.parent == housing, "FAIL: Vent_Ring parent != housing!"
    assert insert.parent == housing, "FAIL: Lens_Insert parent != housing!"
    assert lens.parent == insert, "FAIL: Lens_Glass parent != insert!"

    print(f"[QA] Total Triangles: {total_tris}")
    assert total_tris <= 280, f"FAIL: Total triangles {total_tris} exceeds 280 budget!"
    print("[PASS] Triangle count verified strictly (<= 280)!")
    print("[PASS] Full parent-child hierarchy strictly verified!")

    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Camera_Concealed_Smoke"] = {
        "asset_name": "SEC_Camera_Concealed_Smoke",
        "fbx_path": "exports/SEC_Camera_Concealed_Smoke.fbx",
        "blend_path": "exports/SEC_Camera_Concealed_Smoke.blend",
        "tris_count": total_tris,
        "mesh_count": len(found_meshes),
        "empty_count": 1,
        "materials": ["M_Security_Atlas", "M_Lens_Glass"],
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
