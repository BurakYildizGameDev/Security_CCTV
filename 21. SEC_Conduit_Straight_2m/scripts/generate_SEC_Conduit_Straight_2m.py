"""
=============================================================================
Security CCTV Asset Production Suite - Asset 21
Asset Name: SEC_Conduit_Straight_2m
Production Script (Blender 4.x / 5.x Python API)
Description: 2-meter straight galvanized steel conduit (25mm OD, 20mm ID)
             with hollow inner bore and threaded end collar couplers.
Budget: <= 128 triangles
Slot 0: M_Metal
Hierarchy:
    SEC_Conduit_Straight_2m (Root Empty at 0, 0, 0)
     ├── Pipe_Mesh (Mesh, Y: 0.000 to 2.000)
     ├── Optional_End_Collar_A (Mesh, Y: 0.000 to 0.025)
     └── Optional_End_Collar_B (Mesh, Y: 1.975 to 2.000)
=============================================================================
"""

import os
import sys
import math
import json
import bpy
import bmesh
from mathutils import Vector

# Directory Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

TEXTURE_PATH = os.path.join(EXPORTS_DIR, "T_Metal.png")
FBX_OUT = os.path.join(EXPORTS_DIR, "SEC_Conduit_Straight_2m.fbx")
BLEND_OUT = os.path.join(EXPORTS_DIR, "SEC_Conduit_Straight_2m.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")


def reset_scene():
    """Clear all objects, meshes, materials, and textures."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.scene.unit_settings.length_unit = 'METERS'


def mark_sharp_edges_by_angle(bm, threshold_deg=40.0):
    """Mark edges sharp if face angle exceeds threshold for clean normals."""
    rad = math.radians(threshold_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            try:
                angle = edge.calc_face_angle()
                if angle > rad:
                    edge.smooth = False
                else:
                    edge.smooth = True
            except Exception:
                edge.smooth = False
        else:
            edge.smooth = False


def create_material():
    """Create Slot 0: M_Metal galvanized steel material with matching Solid Mode color."""
    mat = bpy.data.materials.new(name="M_Metal")
    mat.use_nodes = True
    mat.diffuse_color = (0.70, 0.72, 0.75, 1.0) # Realistic galvanized metal in Solid mode

    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = (0.75, 0.77, 0.80, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.88
    bsdf.inputs["Roughness"].default_value = 0.28

    out = nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (300, 0)
    mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    if os.path.exists(TEXTURE_PATH):
        img = bpy.data.images.load(TEXTURE_PATH)
        tex_node = nodes.new(type="ShaderNodeTexImage")
        tex_node.location = (-350, 0)
        tex_node.image = img
        mat.node_tree.links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])

    return mat


def build_pipe_mesh(material):
    """
    Build 2.000m hollow metal conduit tube extending along local Y from 0.000 to 2.000.
    OD = 0.025m (radius 0.0125m), ID = 0.020m (radius 0.0100m).
    Tris: Outer wall (16) + Inner wall (16) + Start rim (16) + End rim (16) = 64 tris.
    """
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    r_out = 0.0125 # 25mm outer diameter
    r_in  = 0.0100 # 20mm inner diameter
    length = 2.000 # 2.000 meters exactly
    segments = 8   # 8-sided octagonal cylinder

    # Vertices generation
    # Outer start (Y = 0) and end (Y = 2)
    v_out_0 = []
    v_out_1 = []
    # Inner start (Y = 0) and end (Y = 2)
    v_in_0 = []
    v_in_1 = []

    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        ca = math.cos(ang)
        sa = math.sin(ang)

        # X = r * ca, Z = r * sa, Y = length
        v_out_0.append(bm.verts.new((r_out * ca, 0.000, r_out * sa)))
        v_out_1.append(bm.verts.new((r_out * ca, length, r_out * sa)))
        v_in_0.append(bm.verts.new((r_in * ca, 0.000, r_in * sa)))
        v_in_1.append(bm.verts.new((r_in * ca, length, r_in * sa)))

    # 1. Outer Cylinder Faces (8 quads = 16 tris)
    for i in range(segments):
        i_next = (i + 1) % segments
        f_out = bm.faces.new([v_out_0[i], v_out_1[i], v_out_1[i_next], v_out_0[i_next]])
        f_out.material_index = 0
        f_out.smooth = True

        # UV unwrap: U wraps along pipe length (0 to 1), V wraps around circumference (0.30 to 0.98)
        v0 = 0.30 + (i / segments) * 0.68
        v1 = 0.30 + ((i + 1) / segments) * 0.68
        for l in f_out.loops:
            vy = l.vert.co.y
            u = vy / length # 0.0 at start, 1.0 at end
            if l.vert == v_out_0[i] or l.vert == v_out_1[i]:
                l[uv_lay].uv = Vector((u, v0))
            else:
                l[uv_lay].uv = Vector((u, v1))

    # 2. Inner Cylinder Faces (Hollow interior bore, normals facing inward: 8 quads = 16 tris)
    for i in range(segments):
        i_next = (i + 1) % segments
        f_in = bm.faces.new([v_in_0[i_next], v_in_1[i_next], v_in_1[i], v_in_0[i]])
        f_in.material_index = 0
        f_in.smooth = True

        v0 = 0.01 + (i / segments) * 0.10
        v1 = 0.01 + ((i + 1) / segments) * 0.10
        for l in f_in.loops:
            vy = l.vert.co.y
            u = vy / length
            if l.vert == v_in_0[i] or l.vert == v_in_1[i]:
                l[uv_lay].uv = Vector((u, v0))
            else:
                l[uv_lay].uv = Vector((u, v1))

    # 3. Start Rim Faces at Y = 0.000 (Wall thickness connecting out to in: 8 quads = 16 tris)
    for i in range(segments):
        i_next = (i + 1) % segments
        f_rim0 = bm.faces.new([v_out_0[i_next], v_in_0[i_next], v_in_0[i], v_out_0[i]])
        f_rim0.material_index = 0
        f_rim0.smooth = False
        for l in f_rim0.loops:
            l[uv_lay].uv = Vector((0.50, 0.05))

    # 4. End Rim Faces at Y = 2.000 (Wall thickness connecting in to out: 8 quads = 16 tris)
    for i in range(segments):
        i_next = (i + 1) % segments
        f_rim1 = bm.faces.new([v_out_1[i], v_in_1[i], v_in_1[i_next], v_out_1[i_next]])
        f_rim1.material_index = 0
        f_rim1.smooth = False
        for l in f_rim1.loops:
            l[uv_lay].uv = Vector((0.50, 0.05))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, threshold_deg=40.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new("Pipe_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Pipe_Mesh", mesh)
    obj.data.materials.append(material)
    return obj


def build_end_collar(material, name, y_start, y_end, is_start=True):
    """
    Build threaded end collar sleeve coupler.
    Outer cylinder (16 tris) + step bevel (16 tris) = 32 tris.
    """
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    r_pipe = 0.0125
    r_col  = 0.0145 # 29mm OD collar (2mm proud of 25mm pipe)
    segments = 8

    v_c_0 = []
    v_c_1 = []
    v_step = []

    y0 = min(y_start, y_end)
    y1 = max(y_start, y_end)

    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        ca = math.cos(ang)
        sa = math.sin(ang)

        v_c_0.append(bm.verts.new((r_col * ca, y0, r_col * sa)))
        v_c_1.append(bm.verts.new((r_col * ca, y1, r_col * sa)))

        # Step vertex on pipe outer surface
        if is_start:
            # Step at y1 (inner end)
            v_step.append(bm.verts.new((r_pipe * ca, y1, r_pipe * sa)))
        else:
            # Step at y0 (inner end)
            v_step.append(bm.verts.new((r_pipe * ca, y0, r_pipe * sa)))

    # Outer cylinder (8 quads = 16 tris)
    for i in range(segments):
        i_next = (i + 1) % segments
        f_out = bm.faces.new([v_c_0[i], v_c_1[i], v_c_1[i_next], v_c_0[i_next]])
        f_out.material_index = 0
        f_out.smooth = True

        u0 = i / segments
        u1 = (i + 1) / segments
        for l in f_out.loops:
            vy = l.vert.co.y
            v = 0.14 + (vy - y0) / (y1 - y0) * 0.14
            if l.vert == v_c_0[i] or l.vert == v_c_1[i]:
                l[uv_lay].uv = Vector((u0, v))
            else:
                l[uv_lay].uv = Vector((u1, v))

    # Step rim to pipe outer wall (8 quads = 16 tris)
    for i in range(segments):
        i_next = (i + 1) % segments
        if is_start:
            f_step = bm.faces.new([v_c_1[i], v_step[i], v_step[i_next], v_c_1[i_next]])
        else:
            f_step = bm.faces.new([v_step[i], v_c_0[i], v_c_0[i_next], v_step[i_next]])
        f_step.material_index = 0
        f_step.smooth = False
        for l in f_step.loops:
            l[uv_lay].uv = Vector((0.50, 0.22))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, threshold_deg=40.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    return obj


def build_asset():
    """Assemble the entire SEC_Conduit_Straight_2m hierarchy."""
    reset_scene()
    material = create_material()

    # 1. Root Empty at (0, 0, 0)
    root_empty = bpy.data.objects.new("SEC_Conduit_Straight_2m", None)
    root_empty.empty_display_type = 'PLAIN_AXES'
    root_empty.empty_display_size = 0.10
    root_empty.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root_empty)

    # 2. Main Pipe Mesh (Y: 0.000 to 2.000)
    obj_pipe = build_pipe_mesh(material)
    bpy.context.scene.collection.objects.link(obj_pipe)
    obj_pipe.parent = root_empty

    # 3. Optional End Collar A (at Y = 0.000 to 0.025)
    obj_collar_a = build_end_collar(material, "Optional_End_Collar_A", 0.000, 0.025, is_start=True)
    bpy.context.scene.collection.objects.link(obj_collar_a)
    obj_collar_a.parent = root_empty

    # 4. Optional End Collar B (at Y = 1.975 to 2.000)
    obj_collar_b = build_end_collar(material, "Optional_End_Collar_B", 1.975, 2.000, is_start=False)
    bpy.context.scene.collection.objects.link(obj_collar_b)
    obj_collar_b.parent = root_empty

    # Apply weighted normals modifier
    bpy.context.view_layer.update()
    for obj in [obj_pipe, obj_collar_a, obj_collar_b]:
        for p in obj.data.polygons:
            p.use_smooth = True
        wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        wn.keep_sharp = True

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[OK] Saved Blend file: {BLEND_OUT}")

    return root_empty, [obj_pipe, obj_collar_a, obj_collar_b]


def export_fbx(root_empty, mesh_objs):
    """Export FBX with strict Unity coordinate parameters."""
    bpy.ops.object.select_all(action='DESELECT')
    root_empty.select_set(True)
    for m in mesh_objs:
        m.select_set(True)

    bpy.context.view_layer.objects.active = root_empty

    bpy.ops.export_scene.fbx(
        filepath=FBX_OUT,
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
    print(f"[OK] Exported FBX: {FBX_OUT}")


def run_qa_verification():
    """Automated re-import QA verification."""
    print("\n--- RUNNING AUTOMATED QA RE-IMPORT VERIFICATION ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=FBX_OUT)

    all_objs = list(bpy.context.scene.objects)
    root = bpy.data.objects.get("SEC_Conduit_Straight_2m")
    mesh_objs = [o for o in all_objs if o.type == 'MESH']
    empty_objs = [o for o in all_objs if o.type == 'EMPTY']

    print(f"Total Objects Imported: {len(all_objs)}")
    print(f"Mesh Count: {len(mesh_objs)}")
    print(f"Empty Count: {len(empty_objs)}")

    # 1. Check Root
    assert root is not None, "FAIL: Root Empty 'SEC_Conduit_Straight_2m' not found!"
    print("[PASS] Root object found with exact name 'SEC_Conduit_Straight_2m'")

    # 2. Check Dimensions
    pipe = bpy.data.objects.get("Pipe_Mesh")
    assert pipe is not None, "FAIL: Pipe_Mesh not found!"
    dims = pipe.dimensions
    print(f"Pipe Dimensions: X={dims.x:.4f}m, Y={dims.y:.4f}m, Z={dims.z:.4f}m")
    assert abs(dims.y - 2.000) < 0.005, f"FAIL: Conduit length {dims.y} != 2.000m!"
    assert abs(dims.x - 0.025) < 0.002, f"FAIL: Conduit outer diameter {dims.x} != 0.025m!"
    print("[PASS] Pipe dimensions verified: Length = 2.000m, OD = 0.025m")

    # 3. Triangle Count
    total_tris = 0
    for m in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(m.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        tris = len(bm.faces)
        total_tris += tris
        print(f"  - Mesh '{m.name}': {tris} tris")
        bm.free()

    print(f"Total Triangles: {total_tris} (Budget <= 128)")
    assert total_tris <= 128, f"FAIL: Triangle count {total_tris} exceeds budget 128!"
    print("[PASS] Triangle budget satisfied!")

    # 4. Check Materials
    expected_mats = ["M_Metal"]
    imported_mats = sorted(list(bpy.data.materials.keys()))
    print(f"Imported Materials: {imported_mats}")
    for em in expected_mats:
        found = any(m.startswith(em) for m in imported_mats)
        assert found, f"FAIL: Expected material '{em}' not found!"
    print("[PASS] Required material 'M_Metal' verified!")

    # 5. Check UVs
    for m in mesh_objs:
        assert len(m.data.uv_layers) > 0, f"FAIL: Mesh '{m.name}' has no UV layers!"
    print("[PASS] All meshes have valid UV coordinates!")

    # 6. Check Hierarchy
    col_a = bpy.data.objects.get("Optional_End_Collar_A")
    col_b = bpy.data.objects.get("Optional_End_Collar_B")
    assert pipe.parent == root, "FAIL: Pipe_Mesh parent != root!"
    assert col_a and col_a.parent == root, "FAIL: Collar A parent != root!"
    assert col_b and col_b.parent == root, "FAIL: Collar B parent != root!"
    print("[PASS] Hierarchy relationships strictly verified!")

    # Update manifest.json
    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Conduit_Straight_2m"] = {
        "asset_name": "SEC_Conduit_Straight_2m",
        "fbx_path": "exports/SEC_Conduit_Straight_2m.fbx",
        "blend_path": "exports/SEC_Conduit_Straight_2m.blend",
        "tris_count": total_tris,
        "mesh_count": len(mesh_objs),
        "empty_count": len(empty_objs),
        "materials": [m.name for m in bpy.data.materials],
        "status": "SUCCESS"
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[OK] Updated manifest: {MANIFEST_PATH}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")


def clean_backup_files():
    """Remove any temporary .blend1 backup files."""
    for root, dirs, files in os.walk(EXPORTS_DIR):
        for file in files:
            if file.endswith(".blend1"):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"[CLEAN] Removed backup: {file}")
                except Exception:
                    pass


if __name__ == "__main__":
    root, meshes = build_asset()
    export_fbx(root, meshes)
    run_qa_verification()
    clean_backup_files()
