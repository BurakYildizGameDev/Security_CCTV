"""
Generate SEC_Camera_PTZ_Industrial 3D Asset
Industrial low-poly PTZ Camera for security/CCTV applications.
Follows general production standards:
- Real low-poly geometry (< 800 tris)
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


def create_materials():
    """Create the 4 standard materials with rich, distinct colors and contrast."""
    mat_configs = [
        # (name, base_color, metallic, roughness, emit_color, emit_strength, transmission, diffuse_color)
        ("M_Security_Atlas", (0.86, 0.87, 0.89, 1.0), 0.05, 0.35, (0, 0, 0, 1), 0.0, 0.0, (0.86, 0.87, 0.89, 1.0)),
        ("M_Lens_Glass", (0.01, 0.03, 0.08, 1.0), 0.10, 0.04, (0, 0, 0, 1), 0.0, 0.95, (0.05, 0.18, 0.35, 1.0)),
        ("M_Emission", (0.9, 0.08, 0.03, 1.0), 0.0, 0.3, (1.0, 0.08, 0.02, 1.0), 10.0, 0.0, (1.0, 0.12, 0.03, 1.0)),
        ("M_Metal", (0.12, 0.13, 0.15, 1.0), 0.95, 0.25, (0, 0, 0, 1), 0.0, 0.0, (0.13, 0.14, 0.16, 1.0)),
    ]

    materials = {}
    for name, color, metallic, roughness, emit_col, emit_str, trans, diff_col in mat_configs:
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf:
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
    """Pre-attach materials to mesh so bmesh face material indices are preserved."""
    ordered_keys = ["M_Security_Atlas", "M_Lens_Glass", "M_Emission", "M_Metal"]
    mesh.materials.clear()
    for k in ordered_keys:
        mesh.materials.append(materials[k])


# -------------------------------------------------------------
# Geometry Generation Helpers
# -------------------------------------------------------------

def add_chamfered_plate(bm, center, size, chamfer=0.015, mat_idx=0):
    """Create an 8-sided chamfered plate in X-Z extruded along Y."""
    sx, sy, sz = size.x / 2.0, size.y / 2.0, size.z / 2.0
    c = min(chamfer, sx * 0.35, sz * 0.35)
    pts_2d = [
        (sx - c, sz),
        (-sx + c, sz),
        (-sx, sz - c),
        (-sx, -sz + c),
        (-sx + c, -sz),
        (sx - c, -sz),
        (sx, -sz + c),
        (sx, sz - c)
    ]
    front_verts = []
    back_verts = []
    for x, z in pts_2d:
        front_verts.append(bm.verts.new((center.x + x, center.y + sy, center.z + z)))
        back_verts.append(bm.verts.new((center.x + x, center.y - sy, center.z + z)))

    f_front = bm.faces.new(front_verts)
    f_front.material_index = mat_idx
    f_back = bm.faces.new(reversed(back_verts))
    f_back.material_index = mat_idx

    n = len(pts_2d)
    for i in range(n):
        ni = (i + 1) % n
        f_side = bm.faces.new([front_verts[i], front_verts[ni], back_verts[ni], back_verts[i]])
        f_side.material_index = mat_idx


def add_cylinder(bm, center, radius, height, segments=10, axis='Z', cap_top=True, cap_bottom=True, mat_idx=0):
    """Create a regular cylinder along X, Y, or Z axis."""
    half_h = height / 2.0
    angles = [2.0 * math.pi * i / segments for i in range(segments)]
    top_verts = []
    bot_verts = []
    for a in angles:
        c = math.cos(a) * radius
        s = math.sin(a) * radius
        if axis == 'Z':
            vt = center + Vector((c, s, half_h))
            vb = center + Vector((c, s, -half_h))
        elif axis == 'Y':
            vt = center + Vector((c, half_h, s))
            vb = center + Vector((c, -half_h, s))
        elif axis == 'X':
            vt = center + Vector((half_h, c, s))
            vb = center + Vector((-half_h, c, s))
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


def add_box(bm, center, size, mat_idx=0):
    """Create an axis-aligned box with specified material index."""
    hx, hy, hz = size.x / 2.0, size.y / 2.0, size.z / 2.0
    v = [
        bm.verts.new(center + Vector((-hx, -hy, -hz))),
        bm.verts.new(center + Vector((hx, -hy, -hz))),
        bm.verts.new(center + Vector((hx, hy, -hz))),
        bm.verts.new(center + Vector((-hx, hy, -hz))),
        bm.verts.new(center + Vector((-hx, -hy, hz))),
        bm.verts.new(center + Vector((hx, -hy, hz))),
        bm.verts.new(center + Vector((hx, hy, hz))),
        bm.verts.new(center + Vector((-hx, hy, hz))),
    ]
    face_indices = [
        (0, 1, 2, 3),  # bottom (-Z)
        (4, 7, 6, 5),  # top (+Z)
        (0, 4, 5, 1),  # front (-Y)
        (2, 6, 7, 3),  # back (+Y)
        (0, 3, 7, 4),  # left (-X)
        (1, 5, 6, 2),  # right (+X)
    ]
    for idxs in face_indices:
        f = bm.faces.new([v[i] for i in idxs])
        f.material_index = mat_idx


def add_swept_arm(bm, waypoints, radii, segments=6, mat_idx=0):
    """Extrude a polygonal cross-section along waypoints to form an industrial arm."""
    rings = []
    for i, pt in enumerate(waypoints):
        r = radii[i]
        if i == 0:
            tangent = (waypoints[1] - pt).normalized()
        elif i == len(waypoints) - 1:
            tangent = (pt - waypoints[i - 1]).normalized()
        else:
            tangent = ((waypoints[i + 1] - pt).normalized() + (pt - waypoints[i - 1]).normalized()).normalized()

        up = Vector((1, 0, 0)) if abs(tangent.dot(Vector((0, 0, 1)))) > 0.95 else Vector((0, 0, 1))
        norm1 = tangent.cross(up).normalized()
        norm2 = tangent.cross(norm1).normalized()

        ring = []
        for s in range(segments):
            angle = 2.0 * math.pi * s / segments
            pos = pt + norm1 * (math.cos(angle) * r) + norm2 * (math.sin(angle) * r)
            ring.append(bm.verts.new(pos))
        rings.append(ring)

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i + 1]
        for s in range(segments):
            ns = (s + 1) % segments
            f = bm.faces.new([r1[s], r1[ns], r2[ns], r2[s]])
            f.material_index = mat_idx


# -------------------------------------------------------------
# Mesh Builders
# -------------------------------------------------------------

def build_base_mount_mesh(mesh):
    """Build root Base_Mount (Wall plate + Arm + Collar)."""
    bm = bmesh.new()

    # 1. Wall Plate: flat against wall at Y=0, extending to Y=0.016m (M_Security_Atlas, slot 0)
    add_chamfered_plate(bm, Vector((0, 0.008, 0)), Vector((0.12, 0.016, 0.15)), chamfer=0.018, mat_idx=0)

    # 2. 4 Hexagonal Mounting Bolts (M_Metal, slot 3)
    for bx in [-0.042, 0.042]:
        for bz in [-0.055, 0.055]:
            add_cylinder(bm, Vector((bx, 0.018, bz)), radius=0.0055, height=0.005, segments=6, axis='Y', cap_top=True, cap_bottom=False, mat_idx=3)

    # 3. Tapered Arm Mounting Boss (M_Security_Atlas, slot 0)
    add_cylinder(bm, Vector((0, 0.020, 0)), radius=0.022, height=0.010, segments=8, axis='Y', cap_top=True, cap_bottom=False, mat_idx=0)

    # 4. Gracefully Arched Gooseneck Arm with vertical entry into pan collar
    arm_points = [
        Vector((0.0, 0.025, 0.000)),
        Vector((0.0, 0.090, 0.020)),
        Vector((0.0, 0.180, 0.035)),
        Vector((0.0, 0.245, 0.022)),
        Vector((0.0, 0.275, -0.005)),
        Vector((0.0, 0.280, -0.025)),
        Vector((0.0, 0.280, -0.038))  # Vertical into collar!
    ]
    arm_radii = [0.020, 0.019, 0.0185, 0.018, 0.018, 0.0185, 0.019]
    add_swept_arm(bm, arm_points, arm_radii, segments=6, mat_idx=0)

    # 5. Pan Top Flange Collar (M_Security_Atlas, slot 0)
    add_cylinder(bm, Vector((0, 0.28, -0.042)), radius=0.036, height=0.012, segments=10, axis='Z', mat_idx=0)
    # Dark Metal Gasket Seal Ring (M_Metal, slot 3)
    add_cylinder(bm, Vector((0, 0.28, -0.0485)), radius=0.037, height=0.003, segments=10, axis='Z', mat_idx=3)

    bm.to_mesh(mesh)
    bm.free()


def build_swivel_body_mesh(mesh):
    """Build Swivel_Y_Body (Pan rotor + Dual fork arms + Hinge hubs)."""
    bm = bmesh.new()

    # 1. Rotating upper turret rotor dome (M_Security_Atlas, slot 0)
    add_cylinder(bm, Vector((0, 0, -0.008)), radius=0.034, height=0.016, segments=10, axis='Z', mat_idx=0)

    # 2. Fork upper bridge / crossbar (M_Security_Atlas, slot 0)
    add_box(bm, Vector((0, 0, -0.020)), Vector((0.104, 0.040, 0.012)), mat_idx=0)

    # 3. Left and Right Fork Arms (M_Security_Atlas, slot 0)
    add_box(bm, Vector((-0.049, 0, -0.052)), Vector((0.012, 0.034, 0.054)), mat_idx=0)
    add_box(bm, Vector((0.049, 0, -0.052)), Vector((0.012, 0.034, 0.054)), mat_idx=0)

    # 4. Tilt Hinge Bearing Hubs (M_Metal, slot 3)
    add_cylinder(bm, Vector((-0.056, 0, -0.070)), radius=0.015, height=0.006, segments=8, axis='X', mat_idx=3)
    add_cylinder(bm, Vector((0.056, 0, -0.070)), radius=0.015, height=0.006, segments=8, axis='X', mat_idx=3)

    # 5. Hinge center bolt hex heads (M_Metal, slot 3)
    add_cylinder(bm, Vector((-0.060, 0, -0.070)), radius=0.006, height=0.003, segments=6, axis='X', mat_idx=3)
    add_cylinder(bm, Vector((0.060, 0, -0.070)), radius=0.006, height=0.003, segments=6, axis='X', mat_idx=3)

    bm.to_mesh(mesh)
    bm.free()


def build_camera_head_mesh(mesh):
    """Build Camera_Head (Housing + Visor + Front Bezel & Dark Faceplate)."""
    bm = bmesh.new()

    # 1. Main Camera Barrel (M_Security_Atlas, slot 0)
    add_cylinder(bm, Vector((0, 0.005, 0)), radius=0.036, height=0.120, segments=12, axis='Y', cap_top=False, cap_bottom=False, mat_idx=0)

    # 2. Rear Tapered Cap (M_Security_Atlas, slot 0)
    add_cylinder(bm, Vector((0, -0.060, 0)), radius=0.036, height=0.010, segments=12, axis='Y', cap_top=False, cap_bottom=True, mat_idx=0)

    # 3. Front Housing Bezel Rim (M_Metal, slot 3)
    add_cylinder(bm, Vector((0, 0.066, 0)), radius=0.037, height=0.012, segments=12, axis='Y', cap_top=False, cap_bottom=False, mat_idx=3)

    # 4. Front Recessed Dark Faceplate (M_Metal, slot 3)
    add_cylinder(bm, Vector((0, 0.071, 0)), radius=0.033, height=0.002, segments=12, axis='Y', cap_top=True, cap_bottom=True, mat_idx=3)

    # 5. Form-fitting Sunshield Visor (M_Security_Atlas, slot 0)
    v_segs = 6
    v_r = 0.0425
    v_y_back = -0.068
    v_y_front = 0.082
    v_front = []
    v_back = []
    for i in range(v_segs + 1):
        ang = math.radians(25 + i * (130 / v_segs))
        vx = math.cos(ang) * v_r
        vz = math.sin(ang) * v_r
        v_front.append(bm.verts.new(Vector((vx, v_y_front, vz))))
        v_back.append(bm.verts.new(Vector((vx, v_y_back, vz))))

    for i in range(v_segs):
        f = bm.faces.new([v_front[i], v_front[i + 1], v_back[i + 1], v_back[i]])
        f.material_index = 0

    # 6. Status LED Indicator on body (M_Emission, slot 2)
    add_cylinder(bm, Vector((-0.0365, 0.015, 0.015)), radius=0.003, height=0.002, segments=6, axis='X', mat_idx=2)

    bm.to_mesh(mesh)
    bm.free()


def build_lens_glass_mesh(mesh):
    """Build central convex optical lens glass (M_Lens_Glass, slot 1)."""
    bm = bmesh.new()

    center_v = bm.verts.new(Vector((0, 0.003, 0)))
    l_segs = 12
    l_r = 0.0135
    perimeter = []
    for i in range(l_segs):
        ang = 2.0 * math.pi * i / l_segs
        lx = math.cos(ang) * l_r
        lz = math.sin(ang) * l_r
        perimeter.append(bm.verts.new(Vector((lx, 0.0, lz))))

    for i in range(l_segs):
        ni = (i + 1) % l_segs
        f = bm.faces.new([center_v, perimeter[i], perimeter[ni]])
        f.material_index = 1  # M_Lens_Glass

    bm.to_mesh(mesh)
    bm.free()


def build_ir_led_array_mesh(mesh):
    """Build peripheral 8-LED IR array around the lens."""
    bm = bmesh.new()

    ir_ring_r = 0.0235
    num_leds = 8
    c_segs = 6
    led_r = 0.0032
    led_h = 0.0035

    for i in range(num_leds):
        ang = 2.0 * math.pi * i / num_leds
        cx = math.cos(ang) * ir_ring_r
        cz = math.sin(ang) * ir_ring_r

        t_verts = []
        b_verts = []
        for s in range(c_segs):
            sang = 2.0 * math.pi * s / c_segs
            vx = cx + math.cos(sang) * led_r
            vz = cz + math.sin(sang) * led_r
            t_verts.append(bm.verts.new(Vector((vx, led_h, vz))))
            b_verts.append(bm.verts.new(Vector((vx, 0.0, vz))))

        # Side barrel faces (M_Metal, slot 3)
        for s in range(c_segs):
            ns = (s + 1) % c_segs
            f = bm.faces.new([t_verts[s], t_verts[ns], b_verts[ns], b_verts[s]])
            f.material_index = 3  # M_Metal

        # Front emitting face (M_Emission, slot 2: Glowing Red!)
        f_top = bm.faces.new(t_verts)
        f_top.material_index = 2  # M_Emission

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
    materials = create_materials()

    # 1. Root Object: SEC_Camera_PTZ_Industrial (Base Mount + Arm)
    mesh_base = bpy.data.meshes.new("SEC_Camera_PTZ_Industrial")
    attach_standard_materials(mesh_base, materials)
    build_base_mount_mesh(mesh_base)
    root_obj = bpy.data.objects.new("SEC_Camera_PTZ_Industrial", mesh_base)
    bpy.context.collection.objects.link(root_obj)
    root_obj.location = Vector((0.0, 0.0, 0.0))
    unwrap_and_smooth(root_obj)

    # 2. Pan Pivot Empty: Swivel_Y_Pivot
    swivel_pivot = bpy.data.objects.new("Swivel_Y_Pivot", None)
    swivel_pivot.empty_display_type = 'ARROWS'
    swivel_pivot.empty_display_size = 0.04
    bpy.context.collection.objects.link(swivel_pivot)
    swivel_pivot.parent = root_obj
    swivel_pivot.location = Vector((0.0, 0.28, -0.050))
    swivel_pivot["rotation_axis"] = "Z"
    swivel_pivot["min_limit_deg"] = -180.0
    swivel_pivot["max_limit_deg"] = 180.0
    swivel_pivot["range_deg"] = 360.0
    swivel_pivot["swivel_type"] = "PAN_YAW"

    c_swivel = swivel_pivot.constraints.new(type='LIMIT_ROTATION')
    c_swivel.owner_space = 'LOCAL'
    c_swivel.use_limit_x = True
    c_swivel.min_x = 0.0
    c_swivel.max_x = 0.0
    c_swivel.use_limit_y = True
    c_swivel.min_y = 0.0
    c_swivel.max_y = 0.0
    c_swivel.use_limit_z = False

    # 3. Pan Body Mesh: Swivel_Y_Body
    mesh_swivel = bpy.data.meshes.new("Swivel_Y_Body")
    attach_standard_materials(mesh_swivel, materials)
    build_swivel_body_mesh(mesh_swivel)
    swivel_body = bpy.data.objects.new("Swivel_Y_Body", mesh_swivel)
    bpy.context.collection.objects.link(swivel_body)
    swivel_body.parent = swivel_pivot
    swivel_body.location = Vector((0.0, 0.0, 0.0))
    unwrap_and_smooth(swivel_body)

    # 4. Tilt Pivot Empty: Tilt_X_Pivot
    tilt_pivot = bpy.data.objects.new("Tilt_X_Pivot", None)
    tilt_pivot.empty_display_type = 'ARROWS'
    tilt_pivot.empty_display_size = 0.035
    bpy.context.collection.objects.link(tilt_pivot)
    tilt_pivot.parent = swivel_body
    tilt_pivot.location = Vector((0.0, 0.0, -0.070))  # World: (0.0, 0.28, -0.120)
    tilt_pivot["rotation_axis"] = "X"
    tilt_pivot["min_limit_deg"] = -90.0
    tilt_pivot["max_limit_deg"] = 30.0
    tilt_pivot["min_rot_x"] = -90.0
    tilt_pivot["max_rot_x"] = 30.0
    tilt_pivot["swivel_type"] = "TILT_PITCH"

    c_tilt = tilt_pivot.constraints.new(type='LIMIT_ROTATION')
    c_tilt.owner_space = 'LOCAL'
    c_tilt.use_limit_x = True
    c_tilt.min_x = math.radians(-90.0)
    c_tilt.max_x = math.radians(30.0)
    c_tilt.use_limit_y = True
    c_tilt.min_y = 0.0
    c_tilt.max_y = 0.0
    c_tilt.use_limit_z = True
    c_tilt.min_z = 0.0
    c_tilt.max_z = 0.0

    # 5. Camera Head Mesh: Camera_Head
    mesh_cam = bpy.data.meshes.new("Camera_Head")
    attach_standard_materials(mesh_cam, materials)
    build_camera_head_mesh(mesh_cam)
    cam_head = bpy.data.objects.new("Camera_Head", mesh_cam)
    bpy.context.collection.objects.link(cam_head)
    cam_head.parent = tilt_pivot
    cam_head.location = Vector((0.0, 0.0, 0.0))
    unwrap_and_smooth(cam_head)

    # 6. Lens Glass Mesh: Lens_Glass
    mesh_lens = bpy.data.meshes.new("Lens_Glass")
    attach_standard_materials(mesh_lens, materials)
    build_lens_glass_mesh(mesh_lens)
    lens_obj = bpy.data.objects.new("Lens_Glass", mesh_lens)
    bpy.context.collection.objects.link(lens_obj)
    lens_obj.parent = cam_head
    lens_obj.location = Vector((0.0, 0.072, 0.0))
    unwrap_and_smooth(lens_obj)

    # 7. IR LED Array Mesh: IR_LED_Array
    mesh_ir = bpy.data.meshes.new("IR_LED_Array")
    attach_standard_materials(mesh_ir, materials)
    build_ir_led_array_mesh(mesh_ir)
    ir_obj = bpy.data.objects.new("IR_LED_Array", mesh_ir)
    bpy.context.collection.objects.link(ir_obj)
    ir_obj.parent = cam_head
    ir_obj.location = Vector((0.0, 0.072, 0.0))
    unwrap_and_smooth(ir_obj)

    bpy.context.view_layer.update()

    mesh_objects = [root_obj, swivel_body, cam_head, lens_obj, ir_obj]
    empty_objects = [swivel_pivot, tilt_pivot]
    all_asset_objects = mesh_objects + empty_objects

    total_tris = count_triangles(mesh_objects)
    print(f"[INFO] Asset generated successfully. Total triangles: {total_tris} (Budget: 800)")

    if total_tris > 800:
        raise ValueError(f"Triangle budget exceeded: {total_tris} > 800")

    # FBX Export
    os.makedirs("exports", exist_ok=True)
    fbx_path = os.path.join("exports", "SEC_Camera_PTZ_Industrial.fbx")

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

    # Also save .blend file for immediate viewing in Blender
    blend_path = os.path.join("exports", "SEC_Camera_PTZ_Industrial.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Blend file saved to {blend_path}")

    return {
        "asset_name": "SEC_Camera_PTZ_Industrial",
        "fbx_path": fbx_path,
        "tris_count": total_tris,
        "mesh_count": len(mesh_objects),
        "empty_count": len(empty_objects),
        "materials": list(materials.keys())
    }


def verify_fbx(fbx_path):
    """Import FBX into a fresh clean scene and thoroughly verify geometry, UV, materials, hierarchy, and pivot rotations."""
    print("[VERIFY] Starting verification on fresh scene...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.import_scene.fbx(filepath=fbx_path)
    bpy.context.view_layer.update()

    imported_objects = {o.name: o for o in bpy.data.objects}
    print(f"[VERIFY] Imported objects: {list(imported_objects.keys())}")

    expected_meshes = ["SEC_Camera_PTZ_Industrial", "Swivel_Y_Body", "Camera_Head", "Lens_Glass", "IR_LED_Array"]
    expected_empties = ["Swivel_Y_Pivot", "Tilt_X_Pivot"]

    # 1. Check all objects exist
    for name in expected_meshes + expected_empties:
        if name not in imported_objects:
            raise AssertionError(f"Expected object '{name}' missing from imported FBX!")

    root_obj = imported_objects["SEC_Camera_PTZ_Industrial"]
    swivel_pivot = imported_objects["Swivel_Y_Pivot"]
    swivel_body = imported_objects["Swivel_Y_Body"]
    tilt_pivot = imported_objects["Tilt_X_Pivot"]
    cam_head = imported_objects["Camera_Head"]
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
    if swivel_pivot.parent != root_obj:
        raise AssertionError(f"Swivel_Y_Pivot parent is {swivel_pivot.parent}, expected {root_obj.name}")
    if swivel_body.parent != swivel_pivot:
        raise AssertionError(f"Swivel_Y_Body parent is {swivel_body.parent}, expected {swivel_pivot.name}")
    if tilt_pivot.parent != swivel_body:
        raise AssertionError(f"Tilt_X_Pivot parent is {tilt_pivot.parent}, expected {swivel_body.name}")
    if cam_head.parent != tilt_pivot:
        raise AssertionError(f"Camera_Head parent is {cam_head.parent}, expected {tilt_pivot.name}")
    if lens_obj.parent != cam_head:
        raise AssertionError(f"Lens_Glass parent is {lens_obj.parent}, expected {cam_head.name}")
    if ir_obj.parent != cam_head:
        raise AssertionError(f"IR_LED_Array parent is {ir_obj.parent}, expected {cam_head.name}")
    print("[VERIFY] Hierarchy structure OK.")

    # 4. Check Materials & UVs on meshes
    expected_mats = ["M_Security_Atlas", "M_Lens_Glass", "M_Emission", "M_Metal"]
    mesh_objs = [root_obj, swivel_body, cam_head, lens_obj, ir_obj]
    for o in mesh_objs:
        if len(o.data.uv_layers) == 0:
            raise AssertionError(f"Mesh '{o.name}' has no UV layers!")
        mat_slots = [s.material.name for s in o.material_slots if s.material]
        for em in expected_mats:
            if not any(em in s for s in mat_slots):
                raise AssertionError(f"Mesh '{o.name}' missing material slot '{em}'. Found: {mat_slots}")

    color_map = {
        "M_Security_Atlas": (0.86, 0.87, 0.89, 1.0),
        "M_Lens_Glass": (0.05, 0.18, 0.35, 1.0),
        "M_Emission": (1.0, 0.12, 0.03, 1.0),
        "M_Metal": (0.13, 0.14, 0.16, 1.0),
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
    if total_tris > 800:
        raise AssertionError(f"Triangles exceeded: {total_tris} > 800")

    # 6. Check Dimensions / Real-world scale
    dims = root_obj.dimensions
    print(f"[VERIFY] Root object dimensions: {dims.x:.3f}m x {dims.y:.3f}m x {dims.z:.3f}m")
    if dims.x <= 0 or dims.y <= 0 or dims.z <= 0:
        raise AssertionError("Asset dimensions must be positive non-zero numbers.")

    # 7. Check Pivot Functional Rotations
    initial_lens_loc = lens_obj.matrix_world.translation.copy()
    initial_cam_rot_z = cam_head.matrix_world.to_euler().z
    swivel_pivot.rotation_euler.z += math.radians(45.0)
    bpy.context.view_layer.update()

    rotated_lens_loc = lens_obj.matrix_world.translation.copy()
    rotated_cam_rot_z = cam_head.matrix_world.to_euler().z
    diff_pan_lens = (rotated_lens_loc - initial_lens_loc).length
    diff_pan_rot = abs(rotated_cam_rot_z - initial_cam_rot_z)

    if diff_pan_lens < 0.005 and diff_pan_rot < 0.1:
        raise AssertionError("Rotating Swivel_Y_Pivot did not affect child orientation or translation!")
    print(f"[VERIFY] Swivel pan rotation verified (lens delta: {diff_pan_lens:.4f}m, rot delta: {math.degrees(diff_pan_rot):.1f} deg).")

    swivel_pivot.rotation_euler.z -= math.radians(45.0)
    bpy.context.view_layer.update()

    initial_lens_loc = lens_obj.matrix_world.translation.copy()
    initial_cam_rot_x = cam_head.matrix_world.to_euler().x
    tilt_pivot.rotation_euler.x += math.radians(-30.0)
    bpy.context.view_layer.update()

    rotated_lens_loc = lens_obj.matrix_world.translation.copy()
    rotated_cam_rot_x = cam_head.matrix_world.to_euler().x
    diff_tilt_lens = (rotated_lens_loc - initial_lens_loc).length
    diff_tilt_rot = abs(rotated_cam_rot_x - initial_cam_rot_x)

    if diff_tilt_lens < 0.005 and diff_tilt_rot < 0.1:
        raise AssertionError("Rotating Tilt_X_Pivot did not tilt Lens_Glass or Camera_Head!")
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
        "asset_name": "SEC_Camera_PTZ_Industrial",
        "fbx_path": os.path.join("exports", "SEC_Camera_PTZ_Industrial.fbx"),
        "tris_count": 0,
        "mesh_count": 0,
        "empty_count": 0,
        "materials": ["M_Security_Atlas", "M_Lens_Glass", "M_Emission", "M_Metal"]
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
