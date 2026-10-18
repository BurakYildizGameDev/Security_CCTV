"""
Generate SEC_Camera_Dome_Ceiling 3D Asset
Low-poly ceiling-mounted security dome camera.
Follows general production standards:
- Real low-poly geometry (< 500 tris)
- Metric units, Z-up Blender, Unity FBX export (Y-up)
- Full hierarchy with functional Empty pivots
- Standard materials and valid UV unwraps
- Verification via FBX re-import and manifest generation
"""

import bpy
import bmesh
import math
import os
import sys
import json
from mathutils import Vector, Matrix


def setup_scene():
    """Clear default objects and set metric units."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)

    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0


def setup_texture_atlas():
    """Generate and pack 512x512 texture atlas with distinct color zones."""
    atlas_img = bpy.data.images.get("T_Security_Atlas")
    if atlas_img is None:
        atlas_img = bpy.data.images.new("T_Security_Atlas", 512, 512)

    pixels = [0.0] * (512 * 512 * 4)
    for y in range(512):
        for x in range(512):
            idx = (y * 512 + x) * 4
            if y >= 256:
                if x < 256:  # Top-left: White CCTV Plastic (0.88, 0.89, 0.91)
                    pixels[idx] = 0.88; pixels[idx+1] = 0.89; pixels[idx+2] = 0.91; pixels[idx+3] = 1.0
                else:       # Top-right: Dark Rubber / Trim (0.08, 0.08, 0.09)
                    pixels[idx] = 0.08; pixels[idx+1] = 0.08; pixels[idx+2] = 0.09; pixels[idx+3] = 1.0
            else:
                if x < 256:  # Bottom-left: Dark Matte Black Eyeball (0.12, 0.13, 0.15)
                    pixels[idx] = 0.12; pixels[idx+1] = 0.13; pixels[idx+2] = 0.15; pixels[idx+3] = 1.0
                else:       # Bottom-right: Gunmetal Metal (0.22, 0.24, 0.26)
                    pixels[idx] = 0.22; pixels[idx+1] = 0.24; pixels[idx+2] = 0.26; pixels[idx+3] = 1.0

    atlas_img.pixels = pixels
    atlas_img.pack()
    atlas_path = os.path.join("exports", "T_Security_Atlas.png")
    os.makedirs(os.path.dirname(atlas_path), exist_ok=True)
    atlas_img.filepath_raw = atlas_path
    atlas_img.file_format = 'PNG'
    try:
        atlas_img.save()
    except Exception:
        pass
    return atlas_img


def create_materials(atlas_img):
    """Create the 4 standard materials: Atlas, Transparent, Lens Glass, Emission."""
    mat_configs = [
        # (name, base_color, metallic, roughness, emit_color, emit_strength, transmission, diffuse_color)
        ("M_Security_Atlas", (0.88, 0.89, 0.91, 1.0), 0.05, 0.35, (0, 0, 0, 1), 0.0, 0.0, (0.88, 0.89, 0.91, 1.0)),
        ("M_Transparent", (0.8, 0.9, 1.0, 1.0), 0.02, 0.0, (0, 0, 0, 1), 0.0, 0.0, (0.7, 0.85, 1.0, 0.22)),
        ("M_Lens_Glass", (0.01, 0.03, 0.08, 1.0), 0.10, 0.04, (0, 0, 0, 1), 0.0, 0.95, (0.04, 0.15, 0.35, 1.0)),
        ("M_Emission", (0.9, 0.08, 0.03, 1.0), 0.0, 0.3, (1.0, 0.08, 0.02, 1.0), 10.0, 0.0, (1.0, 0.12, 0.03, 1.0)),
    ]

    materials = {}
    for name, color, metallic, roughness, emit_col, emit_str, trans, diff_col in mat_configs:
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        tree = mat.node_tree
        bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
            if name == "M_Security_Atlas":
                img_node = next((n for n in tree.nodes if n.type == "ShaderNodeTexImage"), None)
                if img_node is None:
                    img_node = tree.nodes.new(type="ShaderNodeTexImage")
                    img_node.location = (-300, 200)
                img_node.image = atlas_img
                tree.links.new(img_node.outputs["Color"], bsdf.inputs["Base Color"])
                bsdf.inputs["Roughness"].default_value = roughness
                bsdf.inputs["Metallic"].default_value = metallic
            elif name == "M_Transparent":
                bsdf.inputs["Base Color"].default_value = color
                bsdf.inputs["Roughness"].default_value = 0.0
                if "Alpha" in bsdf.inputs:
                    bsdf.inputs["Alpha"].default_value = 0.22
                mat.blend_method = 'BLEND'
            else:
                if "Base Color" in bsdf.inputs:
                    bsdf.inputs["Base Color"].default_value = color
                if "Metallic" in bsdf.inputs:
                    bsdf.inputs["Metallic"].default_value = metallic
                if "Roughness" in bsdf.inputs:
                    bsdf.inputs["Roughness"].default_value = roughness
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emit_col
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emit_col
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emit_str
                if "Transmission Weight" in bsdf.inputs:
                    bsdf.inputs["Transmission Weight"].default_value = trans
                elif "Transmission" in bsdf.inputs:
                    bsdf.inputs["Transmission"].default_value = trans

        mat.diffuse_color = diff_col
        materials[name] = mat

    return materials


def attach_standard_materials(mesh, materials):
    """Pre-attach materials to mesh in exact order: Atlas, Transparent, Lens Glass, Emission."""
    ordered_keys = ["M_Security_Atlas", "M_Transparent", "M_Lens_Glass", "M_Emission"]
    mesh.materials.clear()
    for k in ordered_keys:
        mesh.materials.append(materials[k])


# -------------------------------------------------------------
# Geometry Generation Helpers
# -------------------------------------------------------------

def add_cylinder(bm, center, radius, height, segments=12, axis='Z', cap_top=True, cap_bottom=True, mat_idx=0):
    """Create a cylinder along X, Y, or Z axis."""
    half_h = height / 2.0
    top_verts = []
    bot_verts = []
    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        c = math.cos(ang) * radius
        s = math.sin(ang) * radius
        if axis == 'Z':
            vt = center + Vector((c, s, half_h))
            vb = center + Vector((c, s, -half_h))
        top_verts.append(bm.verts.new(vt))
        bot_verts.append(bm.verts.new(vb))

    for i in range(segments):
        ni = (i + 1) % segments
        f = bm.faces.new([top_verts[i], top_verts[ni], bot_verts[ni], bot_verts[i]])
        f.material_index = mat_idx

    if cap_top:
        f = bm.faces.new(top_verts)
        f.material_index = mat_idx
    if cap_bottom:
        f = bm.faces.new(reversed(bot_verts))
        f.material_index = mat_idx


def add_dome_hemisphere(bm, center, radius, segments_u=12, segments_v=4, mat_idx=1):
    """Create a single-layer transparent hemisphere bubble pointing downwards along -Z."""
    rings = []
    for v in range(segments_v):
        phi = (math.pi / 2.0) * (v / segments_v)
        r = math.cos(phi) * radius
        z = center.z - math.sin(phi) * radius
        ring = []
        for u in range(segments_u):
            theta = 2.0 * math.pi * u / segments_u
            ring.append(bm.verts.new(Vector((center.x + math.cos(theta) * r, center.y + math.sin(theta) * r, z))))
        rings.append(ring)

    apex = bm.verts.new(Vector((center.x, center.y, center.z - radius)))

    for v in range(segments_v - 1):
        r1, r2 = rings[v], rings[v + 1]
        for u in range(segments_u):
            nu = (u + 1) % segments_u
            f = bm.faces.new([r1[u], r1[nu], r2[nu], r2[u]])
            f.material_index = mat_idx

    r_last = rings[-1]
    for u in range(segments_u):
        nu = (u + 1) % segments_u
        f = bm.faces.new([r_last[u], r_last[nu], apex])
        f.material_index = mat_idx


# -------------------------------------------------------------
# Mesh Builders
# -------------------------------------------------------------

def build_ceiling_mount_mesh(mesh):
    """Build root Ceiling_Mount (circular ceiling mounting flange at Z=0)."""
    bm = bmesh.new()

    # Circular ceiling mounting plate (Z from 0.0 to -0.005m, radius 0.065m)
    add_cylinder(bm, Vector((0, 0, -0.0025)), radius=0.065, height=0.005, segments=12, axis='Z', cap_top=True, cap_bottom=True, mat_idx=0)

    # 3 Mounting Screws on outer flange (radius 0.054m)
    for i in range(3):
        ang = 2.0 * math.pi * i / 3.0
        bx = math.cos(ang) * 0.054
        by = math.sin(ang) * 0.054
        add_cylinder(bm, Vector((bx, by, -0.0055)), radius=0.004, height=0.002, segments=6, axis='Z', cap_top=True, cap_bottom=False, mat_idx=0)

    bm.to_mesh(mesh)
    bm.free()


def build_dome_base_mesh(mesh):
    """Build Dome_Base (cylindrical base housing collar)."""
    bm = bmesh.new()

    # Stepped collar (upper radius 0.061m, lower radius 0.056m)
    add_cylinder(bm, Vector((0, 0, -0.004)), radius=0.061, height=0.008, segments=12, axis='Z', cap_top=True, cap_bottom=False, mat_idx=0)
    add_cylinder(bm, Vector((0, 0, -0.012)), radius=0.056, height=0.008, segments=12, axis='Z', cap_top=False, cap_bottom=True, mat_idx=0)

    # Status LED on base rim (Emission, slot 3)
    add_cylinder(bm, Vector((0.0, -0.054, -0.014)), radius=0.0025, height=0.002, segments=6, axis='Z', cap_top=True, cap_bottom=False, mat_idx=3)

    bm.to_mesh(mesh)
    bm.free()


def build_dome_cover_mesh(mesh):
    """Build Dome_Cover (single-layer transparent hemisphere bubble)."""
    bm = bmesh.new()

    # Transparent dome cover starting at Z = 0 and curving downwards along -Z to Z = -0.042m
    add_dome_hemisphere(bm, Vector((0, 0, 0)), radius=0.042, segments_u=12, segments_v=4, mat_idx=1)

    bm.to_mesh(mesh)
    bm.free()


def build_camera_module_mesh(mesh):
    """Build Camera_Module (rounded spherical eyeball gimbal in matte black)."""
    bm = bmesh.new()

    radius = 0.027
    u_segs = 12
    v_segs = 6
    rings = []
    for v in range(1, v_segs):
        phi = -math.pi / 2.0 + math.pi * (v / v_segs)
        r_ring = math.cos(phi) * radius
        y_ring = math.sin(phi) * radius
        if y_ring > 0.014:
            continue
        ring = []
        for u in range(u_segs):
            theta = 2.0 * math.pi * u / u_segs
            ring.append(bm.verts.new(Vector((math.cos(theta) * r_ring, y_ring, math.sin(theta) * r_ring))))
        rings.append(ring)

    apex_back = bm.verts.new(Vector((0, -radius, 0)))
    for u in range(u_segs):
        nu = (u + 1) % u_segs
        f = bm.faces.new([apex_back, rings[0][nu], rings[0][u]])
        f.material_index = 0

    for v in range(len(rings) - 1):
        r1, r2 = rings[v], rings[v + 1]
        for u in range(u_segs):
            nu = (u + 1) % u_segs
            f = bm.faces.new([r1[u], r1[nu], r2[nu], r2[u]])
            f.material_index = 0

    front_ring = rings[-1]
    face_verts = []
    for u in range(u_segs):
        theta = 2.0 * math.pi * u / u_segs
        face_verts.append(bm.verts.new(Vector((math.cos(theta) * 0.019, 0.016, math.sin(theta) * 0.019))))

    for u in range(u_segs):
        nu = (u + 1) % u_segs
        f = bm.faces.new([front_ring[u], front_ring[nu], face_verts[nu], face_verts[u]])
        f.material_index = 0

    f_center = bm.faces.new(face_verts)
    f_center.material_index = 0

    bm.to_mesh(mesh)
    bm.free()


def build_lens_glass_mesh(mesh):
    """Build central optical lens glass (M_Lens_Glass, slot 2)."""
    bm = bmesh.new()

    center_v = bm.verts.new(Vector((0, 0.019, 0)))
    lens_verts = []
    for i in range(10):
        ang = 2.0 * math.pi * i / 10.0
        lx = math.cos(ang) * 0.009
        lz = math.sin(ang) * 0.009
        lens_verts.append(bm.verts.new(Vector((lx, 0.0175, lz))))

    for i in range(10):
        ni = (i + 1) % 10
        f = bm.faces.new([center_v, lens_verts[i], lens_verts[ni]])
        f.material_index = 2  # M_Lens_Glass

    bm.to_mesh(mesh)
    bm.free()


def build_ir_led_array_mesh(mesh):
    """Build peripheral 6-LED IR array around the lens."""
    bm = bmesh.new()

    num_leds = 6
    ring_radius = 0.0145
    for i in range(num_leds):
        ang = 2.0 * math.pi * i / num_leds
        lx = math.cos(ang) * ring_radius
        lz = math.sin(ang) * ring_radius

        c_top = []
        c_bot = []
        for s in range(5):
            sang = 2.0 * math.pi * s / 5.0
            vx = lx + math.cos(sang) * 0.0022
            vz = lz + math.sin(sang) * 0.0022
            c_top.append(bm.verts.new(Vector((vx, 0.019, vz))))
            c_bot.append(bm.verts.new(Vector((vx, 0.0165, vz))))

        for s in range(5):
            ns = (s + 1) % 5
            f = bm.faces.new([c_top[s], c_top[ns], c_bot[ns], c_bot[s]])
            f.material_index = 0

        f_emit = bm.faces.new(c_top)
        f_emit.material_index = 3  # M_Emission (Glowing Red!)

    bm.to_mesh(mesh)
    bm.free()


def unwrap_and_smooth(obj):
    """Generate UV map and apply smooth normals with WeightedNormal modifier."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    for poly in obj.data.polygons:
        poly.use_smooth = True

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')

    mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
    mod.keep_sharp = True


def remap_uvs(obj, u_min, v_min, u_max, v_max):
    """Remap UV island coordinates to specific zone on the texture atlas."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    uvs = [loop[uv_layer].uv for face in bm.faces for loop in face.loops]
    if uvs:
        min_u = min(uv.x for uv in uvs)
        max_u = max(uv.x for uv in uvs)
        min_v = min(uv.y for uv in uvs)
        max_v = max(uv.y for uv in uvs)
        range_u = max(max_u - min_u, 0.0001)
        range_v = max(max_v - min_v, 0.0001)
        target_range_u = u_max - u_min
        target_range_v = v_max - v_min
        for face in bm.faces:
            for loop in face.loops:
                norm_u = (loop[uv_layer].uv.x - min_u) / range_u
                norm_v = (loop[uv_layer].uv.y - min_v) / range_v
                loop[uv_layer].uv.x = u_min + norm_u * target_range_u
                loop[uv_layer].uv.y = v_min + norm_v * target_range_v
    bm.to_mesh(obj.data)
    bm.free()


def count_triangles(mesh_objects):
    """Triangulate copies of meshes to measure exact triangle count."""
    total_tris = 0
    for obj in mesh_objects:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        tris = len(bm.faces)
        total_tris += tris
        bm.free()
    return total_tris


# -------------------------------------------------------------
# Main Generation Function
# -------------------------------------------------------------

def generate_asset():
    setup_scene()
    atlas_img = setup_texture_atlas()
    materials = create_materials(atlas_img)

    # 1. Root Object: SEC_Camera_Dome_Ceiling (Ceiling Mount Plate at Z=0)
    mesh_mount = bpy.data.meshes.new("SEC_Camera_Dome_Ceiling")
    attach_standard_materials(mesh_mount, materials)
    build_ceiling_mount_mesh(mesh_mount)
    root_obj = bpy.data.objects.new("SEC_Camera_Dome_Ceiling", mesh_mount)
    bpy.context.collection.objects.link(root_obj)
    root_obj.location = Vector((0.0, 0.0, 0.0))
    unwrap_and_smooth(root_obj)
    remap_uvs(root_obj, 0.05, 0.55, 0.45, 0.95)  # White CCTV plastic

    # 2. Dome Base: Dome_Base (child of root)
    mesh_base = bpy.data.meshes.new("Dome_Base")
    attach_standard_materials(mesh_base, materials)
    build_dome_base_mesh(mesh_base)
    dome_base = bpy.data.objects.new("Dome_Base", mesh_base)
    bpy.context.collection.objects.link(dome_base)
    dome_base.parent = root_obj
    dome_base.location = Vector((0.0, 0.0, -0.005))
    unwrap_and_smooth(dome_base)
    remap_uvs(dome_base, 0.05, 0.55, 0.45, 0.95)  # White CCTV plastic

    # 3. Transparent Dome Cover: Dome_Cover (child of Dome_Base)
    mesh_dome = bpy.data.meshes.new("Dome_Cover")
    attach_standard_materials(mesh_dome, materials)
    build_dome_cover_mesh(mesh_dome)
    dome_cover = bpy.data.objects.new("Dome_Cover", mesh_dome)
    bpy.context.collection.objects.link(dome_cover)
    dome_cover.parent = dome_base
    dome_cover.location = Vector((0.0, 0.0, -0.016))
    unwrap_and_smooth(dome_cover)

    # 4. Camera Module Pivot Empty: Camera_Module_Pivot (child of Dome_Base)
    cam_pivot = bpy.data.objects.new("Camera_Module_Pivot", None)
    cam_pivot.empty_display_type = 'ARROWS'
    cam_pivot.empty_display_size = 0.03
    bpy.context.collection.objects.link(cam_pivot)
    cam_pivot.parent = dome_base
    cam_pivot.location = Vector((0.0, 0.0, -0.014))
    # Angle downward at 35 degrees into the room
    cam_pivot.rotation_euler.x = math.radians(-35.0)

    cam_pivot["rotation_axis"] = "X"
    cam_pivot["min_limit_deg"] = -30.0
    cam_pivot["max_limit_deg"] = 30.0
    cam_pivot["min_rot_x"] = -30.0
    cam_pivot["max_rot_x"] = 30.0
    cam_pivot["swivel_type"] = "TILT_PITCH"

    c_tilt = cam_pivot.constraints.new(type='LIMIT_ROTATION')
    c_tilt.owner_space = 'LOCAL'
    c_tilt.use_limit_x = True
    c_tilt.min_x = math.radians(-65.0)   # -35 - 30 = -65 deg
    c_tilt.max_x = math.radians(-5.0)    # -35 + 30 = -5 deg
    c_tilt.use_limit_y = True
    c_tilt.min_y = 0.0
    c_tilt.max_y = 0.0
    c_tilt.use_limit_z = True
    c_tilt.min_z = 0.0
    c_tilt.max_z = 0.0

    # 5. Camera Module: Camera_Module (child of Camera_Module_Pivot, Matte Black Eyeball)
    mesh_module = bpy.data.meshes.new("Camera_Module")
    attach_standard_materials(mesh_module, materials)
    build_camera_module_mesh(mesh_module)
    cam_module = bpy.data.objects.new("Camera_Module", mesh_module)
    bpy.context.collection.objects.link(cam_module)
    cam_module.parent = cam_pivot
    cam_module.location = Vector((0.0, 0.0, 0.0))
    unwrap_and_smooth(cam_module)
    remap_uvs(cam_module, 0.05, 0.05, 0.45, 0.45)  # Dark Matte Black Eyeball!

    # 6. Lens Glass: Lens_Glass (child of Camera_Module)
    mesh_lens = bpy.data.meshes.new("Lens_Glass")
    attach_standard_materials(mesh_lens, materials)
    build_lens_glass_mesh(mesh_lens)
    lens_obj = bpy.data.objects.new("Lens_Glass", mesh_lens)
    bpy.context.collection.objects.link(lens_obj)
    lens_obj.parent = cam_module
    lens_obj.location = Vector((0.0, 0.0, 0.0))
    unwrap_and_smooth(lens_obj)

    # 7. IR LED Array: IR_LED_Array (child of Camera_Module)
    mesh_ir = bpy.data.meshes.new("IR_LED_Array")
    attach_standard_materials(mesh_ir, materials)
    build_ir_led_array_mesh(mesh_ir)
    ir_obj = bpy.data.objects.new("IR_LED_Array", mesh_ir)
    bpy.context.collection.objects.link(ir_obj)
    ir_obj.parent = cam_module
    ir_obj.location = Vector((0.0, 0.0, 0.0))
    unwrap_and_smooth(ir_obj)
    remap_uvs(ir_obj, 0.55, 0.05, 0.95, 0.45)  # Gunmetal Barrels

    bpy.context.view_layer.update()

    mesh_objects = [root_obj, dome_base, dome_cover, cam_module, lens_obj, ir_obj]
    empty_objects = [cam_pivot]
    all_asset_objects = mesh_objects + empty_objects

    total_tris = count_triangles(mesh_objects)
    print(f"[INFO] Asset generated successfully. Total triangles: {total_tris} (Budget: 500)")

    if total_tris > 500:
        raise ValueError(f"Triangle budget exceeded: {total_tris} > 500")

    # FBX Export
    os.makedirs("exports", exist_ok=True)
    fbx_path = os.path.join("exports", "SEC_Camera_Dome_Ceiling.fbx")

    bpy.ops.object.select_all(action='DESELECT')
    for o in all_asset_objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

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
    print(f"[INFO] FBX exported to {fbx_path}")

    # Also save .blend file
    blend_path = os.path.join("exports", "SEC_Camera_Dome_Ceiling.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Blend file saved to {blend_path}")

    return {
        "asset_name": "SEC_Camera_Dome_Ceiling",
        "fbx_path": fbx_path,
        "tris_count": total_tris,
        "mesh_count": len(mesh_objects),
        "empty_count": len(empty_objects),
        "materials": list(materials.keys())
    }


def verify_fbx(fbx_path):
    """Import FBX into a fresh clean scene and thoroughly verify geometry, UV, materials, hierarchy, and pivot rotation."""
    print("[VERIFY] Starting verification on fresh scene...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.import_scene.fbx(filepath=fbx_path)
    bpy.context.view_layer.update()

    imported_objects = {o.name: o for o in bpy.data.objects}
    print(f"[VERIFY] Imported objects: {list(imported_objects.keys())}")

    expected_meshes = ["SEC_Camera_Dome_Ceiling", "Dome_Base", "Dome_Cover", "Camera_Module", "Lens_Glass", "IR_LED_Array"]
    expected_empties = ["Camera_Module_Pivot"]

    # 1. Check all objects exist
    for name in expected_meshes + expected_empties:
        if name not in imported_objects:
            raise AssertionError(f"Expected object '{name}' missing from imported FBX!")

    root_obj = imported_objects["SEC_Camera_Dome_Ceiling"]
    dome_base = imported_objects["Dome_Base"]
    dome_cover = imported_objects["Dome_Cover"]
    cam_pivot = imported_objects["Camera_Module_Pivot"]
    cam_module = imported_objects["Camera_Module"]
    lens_obj = imported_objects["Lens_Glass"]
    ir_obj = imported_objects["IR_LED_Array"]

    # 2. Check types
    for name in expected_meshes:
        if imported_objects[name].type != 'MESH':
            raise AssertionError(f"Object '{name}' expected type MESH, got {imported_objects[name].type}")
    for name in expected_empties:
        if imported_objects[name].type != 'EMPTY':
            raise AssertionError(f"Object '{name}' expected type EMPTY, got {imported_objects[name].type}")

    # 3. Check Hierarchy
    if root_obj.parent is not None:
        raise AssertionError("Root object should have no parent.")
    if dome_base.parent != root_obj:
        raise AssertionError(f"Dome_Base parent is {dome_base.parent}, expected {root_obj.name}")
    if dome_cover.parent != dome_base:
        raise AssertionError(f"Dome_Cover parent is {dome_cover.parent}, expected {dome_base.name}")
    if cam_pivot.parent != dome_base:
        raise AssertionError(f"Camera_Module_Pivot parent is {cam_pivot.parent}, expected {dome_base.name}")
    if cam_module.parent != cam_pivot:
        raise AssertionError(f"Camera_Module parent is {cam_module.parent}, expected {cam_pivot.name}")
    if lens_obj.parent != cam_module:
        raise AssertionError(f"Lens_Glass parent is {lens_obj.parent}, expected {cam_module.name}")
    if ir_obj.parent != cam_module:
        raise AssertionError(f"IR_LED_Array parent is {ir_obj.parent}, expected {cam_module.name}")
    print("[VERIFY] Hierarchy structure OK.")

    # 4. Check Materials & UVs on meshes
    expected_mats = ["M_Security_Atlas", "M_Transparent", "M_Lens_Glass", "M_Emission"]
    mesh_objs = [root_obj, dome_base, dome_cover, cam_module, lens_obj, ir_obj]
    for o in mesh_objs:
        if len(o.data.uv_layers) == 0:
            raise AssertionError(f"Mesh '{o.name}' has no UV layers!")
        mat_slots = [s.material.name for s in o.material_slots if s.material]
        for em in expected_mats:
            if not any(em in s for s in mat_slots):
                raise AssertionError(f"Mesh '{o.name}' missing material slot '{em}'. Found: {mat_slots}")

    color_map = {
        "M_Security_Atlas": (0.88, 0.89, 0.91, 1.0),
        "M_Transparent": (0.7, 0.85, 1.0, 0.22),
        "M_Lens_Glass": (0.04, 0.15, 0.35, 1.0),
        "M_Emission": (1.0, 0.12, 0.03, 1.0),
    }
    for m in bpy.data.materials:
        for k, col in color_map.items():
            if k in m.name:
                m.diffuse_color = col

    print("[VERIFY] Materials and UV layers OK.")

    # 5. Check Triangles
    total_tris = 0
    for o in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        total_tris += len(bm.faces)
        bm.free()

    print(f"[VERIFY] Total triangulated tris in FBX: {total_tris}")
    if total_tris > 500:
        raise AssertionError(f"Triangles exceeded: {total_tris} > 500")

    # 6. Check Dimensions / Real-world scale
    dims = root_obj.dimensions
    print(f"[VERIFY] Root object dimensions: {dims.x:.3f}m x {dims.y:.3f}m x {dims.z:.3f}m")
    if dims.x <= 0 or dims.y <= 0 or dims.z <= 0:
        raise AssertionError("Asset dimensions must be positive non-zero numbers.")

    # 7. Check Pivot Functional Rotation
    initial_lens_loc = lens_obj.matrix_world.translation.copy()
    initial_module_rot_x = cam_module.matrix_world.to_euler().x
    cam_pivot.rotation_euler.x += math.radians(20.0)
    bpy.context.view_layer.update()

    rotated_lens_loc = lens_obj.matrix_world.translation.copy()
    rotated_module_rot_x = cam_module.matrix_world.to_euler().x
    diff_tilt_lens = (rotated_lens_loc - initial_lens_loc).length
    diff_tilt_rot = abs(rotated_module_rot_x - initial_module_rot_x)

    if diff_tilt_lens < 0.003 and diff_tilt_rot < 0.1:
        raise AssertionError("Rotating Camera_Module_Pivot did not tilt Lens_Glass or Camera_Module!")
    print(f"[VERIFY] Tilt rotation verified (lens delta: {diff_tilt_lens:.4f}m, rot delta: {math.degrees(diff_tilt_rot):.1f} deg).")

    print("[VERIFY] ALL CHECKS PASSED SUCCESSFULLY.")
    return total_tris


def update_manifest(info, success):
    manifest_path = os.path.join("exports", "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:
            print(f"[WARN] Could not parse existing manifest: {e}")
            manifest = {}

    manifest[info["asset_name"]] = {
        "asset_name": info["asset_name"],
        "fbx_path": info["fbx_path"].replace("\\", "/"),
        "tris_count": info["tris_count"],
        "mesh_count": info["mesh_count"],
        "empty_count": info["empty_count"],
        "materials": info["materials"],
        "status": "SUCCESS" if success else "FAILED"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[INFO] Manifest updated: {manifest_path}")


def main():
    info = {
        "asset_name": "SEC_Camera_Dome_Ceiling",
        "fbx_path": os.path.join("exports", "SEC_Camera_Dome_Ceiling.fbx"),
        "tris_count": 0,
        "mesh_count": 0,
        "empty_count": 0,
        "materials": ["M_Security_Atlas", "M_Transparent", "M_Lens_Glass", "M_Emission"]
    }
    try:
        gen_info = generate_asset()
        info.update(gen_info)
        verified_tris = verify_fbx(gen_info["fbx_path"])
        info["tris_count"] = verified_tris
        update_manifest(info, success=True)
        print("\n==========================================")
        print("  PROCESS COMPLETED SUCCESSFULLY [SUCCESS]")
        print("==========================================")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        update_manifest(info, success=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
