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

def create_materials(atlas_path):
    """
    Slot 0: M_Security_Atlas
    Slot 1: M_Lens_Glass
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

    # 1. M_Lens_Glass (Multi-coated optical glass with glossy specular reflections)
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
        g_bsdf.inputs['Base Color'].default_value = (0.06, 0.12, 0.18, 1.0)
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

def assign_material_slots(mesh_or_obj, mats):
    """Ensure mesh has exactly 2 material slots in standard order."""
    if hasattr(mesh_or_obj, 'materials'):
        m_list = mesh_or_obj.materials
    else:
        m_list = mesh_or_obj.data.materials
    m_list.clear()
    for m in mats:
        m_list.append(m)

def build_ceiling_base(mats):
    """
    Ceiling_Base: Low-profile disc housing flush with ceiling at Z=0.
    Diameter: 140mm (r=0.070m), height: 26mm (Z=0.0 to -0.026).
    16-radial smooth contour with sloped bevel, text/mic ring, Torx screws and recessed lens well.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16

    # Z-stations from ceiling down into -Z:
    # 0: Z= 0.000, r=0.070 (ceiling edge)
    # 1: Z=-0.008, r=0.070 (outer vertical rim)
    # 2: Z=-0.012, r=0.066 (chamfered bevel)
    # 3: Z=-0.022, r=0.044 (conical slope with brand, Torx screws, mics, LED)
    # 4: Z=-0.026, r=0.033 (recessed dark aperture floor)
    stations = [
        ( 0.000, 0.070),
        (-0.008, 0.070),
        (-0.012, 0.066),
        (-0.022, 0.044),
        (-0.026, 0.033)
    ]

    rings = []
    for z_pos, r_rad in stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        rings.append(ring)

    # Center vertex on recessed aperture floor
    v_center = bm.verts.new(Vector((0.0, 0.0, -0.026)))
    bm.verts.ensure_lookup_table()

    # Quads between consecutive rings (pointing outward into -Z)
    for s in range(len(stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True
            f.material_index = 0

            ang0 = i * (2.0 * math.pi / n_radial)
            ang1 = (i + 1) * (2.0 * math.pi / n_radial)
            cu, cv = 0.25, 0.75 # Center of housing disc in 1024x1024 atlas (Quadrant 1)

            if s == 0:
                # Outer vertical rim
                u0 = 0.02 + (i / float(n_radial)) * 0.45
                u1 = 0.02 + ((i + 1) / float(n_radial)) * 0.45
                for loop in f.loops:
                    v_val = 0.95 if loop.vert in (va, vb) else 0.92
                    loop[uv_layer].uv = (u0 if loop.vert in (va, vd) else u1, v_val)
            elif s == 1:
                # Chamfer rim
                for loop in f.loops:
                    loop[uv_layer].uv = (cu + 0.22 * math.cos(ang0), cv + 0.22 * math.sin(ang0))
            elif s == 2:
                # Conical sloped face (main graphic ring with brand, Torx screws, mics, and status LED)
                for loop in f.loops:
                    if loop.vert == va: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang0), cv + 0.21 * math.sin(ang0))
                    elif loop.vert == vb: loop[uv_layer].uv = (cu + 0.21 * math.cos(ang1), cv + 0.21 * math.sin(ang1))
                    elif loop.vert == vc: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang1), cv + 0.12 * math.sin(ang1))
                    elif loop.vert == vd: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang0), cv + 0.12 * math.sin(ang0))
            else:
                # Recessed well step
                for loop in f.loops:
                    if loop.vert == va: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang0), cv + 0.12 * math.sin(ang0))
                    elif loop.vert == vb: loop[uv_layer].uv = (cu + 0.12 * math.cos(ang1), cv + 0.12 * math.sin(ang1))
                    elif loop.vert == vc: loop[uv_layer].uv = (cu + 0.06 * math.cos(ang1), cv + 0.06 * math.sin(ang1))
                    elif loop.vert == vd: loop[uv_layer].uv = (cu + 0.06 * math.cos(ang0), cv + 0.06 * math.sin(ang0))

    # Center fan triangles on recessed floor (pointing into -Z)
    r_floor = rings[-1]
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((r_floor[i], v_center, r_floor[i_next]))
        f.smooth = False
        f.material_index = 0
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        cu, cv = 0.25, 0.75
        for loop in f.loops:
            if loop.vert == r_floor[i]: loop[uv_layer].uv = (cu + 0.05 * math.cos(ang0), cv + 0.05 * math.sin(ang0))
            elif loop.vert == r_floor[i_next]: loop[uv_layer].uv = (cu + 0.05 * math.cos(ang1), cv + 0.05 * math.sin(ang1))
            elif loop.vert == v_center: loop[uv_layer].uv = (cu, cv)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Ceiling_Base")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Ceiling_Base", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_trim_ring(mats):
    """
    Trim_Ring: Decorative anodized aluminum chamfered bezel encircling the lens dome base.
    Position: Z=-0.021 to -0.027, radius: r=0.033 to 0.044m.
    16 radial segments, Slot 0: M_Security_Atlas (dark metallic anodized zone).
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16

    # 3 profile rings:
    # 0: outer edge: Z=-0.021, r=0.044
    # 1: chamfer apex: Z=-0.027, r=0.040
    # 2: inner seating rim: Z=-0.026, r=0.033
    r_stations = [
        (-0.021, 0.044),
        (-0.027, 0.040),
        (-0.026, 0.033)
    ]

    rings = []
    for z_pos, r_rad in r_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    for s in range(len(r_stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True
            f.material_index = 0

            u0 = 0.55 + (i / float(n_radial)) * 0.40
            u1 = 0.55 + ((i + 1) / float(n_radial)) * 0.40
            v0 = 0.72 if s == 0 else 0.80
            v1 = 0.80 if s == 0 else 0.88
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (u0, v0)
                elif loop.vert == vb: loop[uv_layer].uv = (u1, v0)
                elif loop.vert == vc: loop[uv_layer].uv = (u1, v1)
                elif loop.vert == vd: loop[uv_layer].uv = (u0, v1)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Trim_Ring")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Trim_Ring", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_lens_dome(mats):
    """
    Lens_Dome: Wide-angle convex optical fisheye dome extending into -Z.
    Base at Z=-0.025 (r=0.033m), apex at Z=-0.044 (r=0.0m).
    16 radial segments, 2 quad latitude rings + 1 apex triangle fan (80 tris).
    Slot 1: M_Lens_Glass.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    n_radial = 16

    # Spherical profile stations:
    # 0: base rim: Z=-0.025, r=0.033
    # 1: mid bulge: Z=-0.034, r=0.028
    # 2: top curve: Z=-0.040, r=0.018
    # Apex vertex: Z=-0.044, r=0.000
    dome_stations = [
        (-0.025, 0.033),
        (-0.034, 0.028),
        (-0.040, 0.018)
    ]

    rings = []
    for z_pos, r_rad in dome_stations:
        ring = []
        for i in range(n_radial):
            ang = i * (2.0 * math.pi / n_radial)
            vx = math.cos(ang) * r_rad
            vy = math.sin(ang) * r_rad
            ring.append(bm.verts.new(Vector((vx, vy, z_pos))))
        rings.append(ring)

    v_apex = bm.verts.new(Vector((0.0, 0.0, -0.044)))
    bm.verts.ensure_lookup_table()

    # Quads between latitude rings (pointing into -Z)
    for s in range(len(dome_stations) - 1):
        r_a = rings[s]
        r_b = rings[s + 1]
        for i in range(n_radial):
            i_next = (i + 1) % n_radial
            va = r_a[i]
            vb = r_a[i_next]
            vc = r_b[i_next]
            vd = r_b[i]
            f = bm.faces.new((va, vd, vc, vb))
            f.smooth = True
            f.material_index = 1 # Slot 1: M_Lens_Glass

            ang0 = i * (2.0 * math.pi / n_radial)
            ang1 = (i + 1) * (2.0 * math.pi / n_radial)
            cu, cv = 0.75, 0.25
            rad0 = 0.21 if s == 0 else 0.14
            rad1 = 0.14 if s == 0 else 0.07
            for loop in f.loops:
                if loop.vert == va: loop[uv_layer].uv = (cu + rad0 * math.cos(ang0), cv + rad0 * math.sin(ang0))
                elif loop.vert == vb: loop[uv_layer].uv = (cu + rad0 * math.cos(ang1), cv + rad0 * math.sin(ang1))
                elif loop.vert == vc: loop[uv_layer].uv = (cu + rad1 * math.cos(ang1), cv + rad1 * math.sin(ang1))
                elif loop.vert == vd: loop[uv_layer].uv = (cu + rad1 * math.cos(ang0), cv + rad1 * math.sin(ang0))

    # Apex triangle fan (pointing into -Z)
    r_top = rings[-1]
    for i in range(n_radial):
        i_next = (i + 1) % n_radial
        f = bm.faces.new((r_top[i], v_apex, r_top[i_next]))
        f.smooth = True
        f.material_index = 1 # Slot 1: M_Lens_Glass
        ang0 = i * (2.0 * math.pi / n_radial)
        ang1 = (i + 1) * (2.0 * math.pi / n_radial)
        cu, cv = 0.75, 0.25
        for loop in f.loops:
            if loop.vert == r_top[i]: loop[uv_layer].uv = (cu + 0.07 * math.cos(ang0), cv + 0.07 * math.sin(ang0))
            elif loop.vert == r_top[i_next]: loop[uv_layer].uv = (cu + 0.07 * math.cos(ang1), cv + 0.07 * math.sin(ang1))
            elif loop.vert == v_apex: loop[uv_layer].uv = (cu, cv)

    bm.normal_update()
    mesh = bpy.data.meshes.new("Lens_Dome")
    for m in mats:
        mesh.materials.append(m)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.material_index = 1

    obj = bpy.data.objects.new("Lens_Dome", mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def build_asset():
    """Build the full SEC_Camera_Fisheye_360 asset hierarchy."""
    reset_scene()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    asset_dir = os.path.dirname(script_dir)
    exports_dir = os.path.join(asset_dir, "exports")
    atlas_path = os.path.join(exports_dir, "T_Security_Atlas.png")

    mats = create_materials(atlas_path)

    # 1. Root Empty: SEC_Camera_Fisheye_360 at (0, 0, 0)
    root = bpy.data.objects.new("SEC_Camera_Fisheye_360", None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.06
    root.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root)

    # 2. Ceiling_Base (Child of Root)
    base = build_ceiling_base(mats)
    base.parent = root

    # 3. Trim_Ring & Lens_Dome (Children of Ceiling_Base)
    trim = build_trim_ring(mats)
    trim.parent = base

    lens = build_lens_dome(mats)
    lens.parent = base

    # Save .blend
    blend_path = os.path.join(exports_dir, "SEC_Camera_Fisheye_360.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved .blend: {blend_path}")

    # Export FBX
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Fisheye_360.fbx")
    export_fbx(root, [base, trim, lens], fbx_path)

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
    """Import FBX into a clean scene and verify tris, hierarchy, materials, UVs."""
    print("\n--- RUNNING HEADLESS QA VERIFICATION (Asset 27) ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    root = bpy.data.objects.get("SEC_Camera_Fisheye_360")
    assert root is not None, "FAIL: Root object 'SEC_Camera_Fisheye_360' missing!"
    assert root.type == 'EMPTY', f"FAIL: Root is type {root.type}, expected EMPTY!"

    expected_meshes = {
        "Ceiling_Base",
        "Trim_Ring",
        "Lens_Dome"
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
    assert total_tris <= 320, f"FAIL: Total triangles {total_tris} exceeds 320 budget!"
    print("[PASS] Triangle count verified strictly (<= 320)!")

    # Check Material Slots
    for m in mesh_objs:
        assert len(m.data.materials) >= 2, f"FAIL: Mesh '{m.name}' has fewer than 2 material slots!"
        assert m.data.materials[0].name.startswith("M_Security_Atlas"), f"FAIL: Slot 0 is '{m.data.materials[0].name}', expected 'M_Security_Atlas'!"
        assert m.data.materials[1].name.startswith("M_Lens_Glass"), f"FAIL: Slot 1 is '{m.data.materials[1].name}', expected 'M_Lens_Glass'!"
    print("[PASS] Material slots strictly verified: Slot 0: M_Security_Atlas, Slot 1: M_Lens_Glass!")

    # Check UV layers
    for m in mesh_objs:
        assert len(m.data.uv_layers) > 0, f"FAIL: Mesh '{m.name}' has no UV layers!"
    print("[PASS] All meshes have valid UV coordinates!")

    # Check Parent-Child Hierarchy
    base = bpy.data.objects.get("Ceiling_Base")
    assert base and base.parent == root, "FAIL: Ceiling_Base parent != root!"

    trim = bpy.data.objects.get("Trim_Ring")
    assert trim and trim.parent == base, "FAIL: Trim_Ring parent != Ceiling_Base!"

    lens = bpy.data.objects.get("Lens_Dome")
    assert lens and lens.parent == base, "FAIL: Lens_Dome parent != Ceiling_Base!"

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

    manifest_data["SEC_Camera_Fisheye_360"] = {
        "asset_name": "SEC_Camera_Fisheye_360",
        "fbx_path": "exports/SEC_Camera_Fisheye_360.fbx",
        "blend_path": "exports/SEC_Camera_Fisheye_360.blend",
        "tris_count": total_tris,
        "mesh_count": len(mesh_objs),
        "empty_count": 1,
        "materials": [
            "M_Security_Atlas",
            "M_Lens_Glass"
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
