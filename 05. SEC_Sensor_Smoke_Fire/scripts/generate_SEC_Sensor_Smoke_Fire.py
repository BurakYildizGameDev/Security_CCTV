"""
Generate SEC_Sensor_Smoke_Fire 3D Asset
High-End Industrial Ceiling-Mounted Optical Smoke and Fire Detector.
Follows general production standards:
- Real low-poly geometry (<= 250 tris)
- 16-segment circular resolution with 8 physical 3D peripheral smoke intake vents
- Metric units, Z-up Blender, Unity FBX export (Y-up)
- Full hierarchy (Ceiling_Base root -> Detector_Housing -> Vent_Grille & Status_LED)
- Standard materials (M_Security_Atlas, M_Emission) and valid UV unwraps
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
    """Generate high-contrast, professional 512x512 texture atlas for smoke/fire detector."""
    atlas_img = bpy.data.images.get("T_Security_Atlas")
    if atlas_img is None:
        atlas_img = bpy.data.images.new("T_Security_Atlas", 512, 512)

    pixels = [0.0] * (512 * 512 * 4)
    for y in range(512):
        for x in range(512):
            idx = (y * 512 + x) * 4
            if y >= 256:
                if x < 256:  # Quadrant 0: Clean White Security Polymer with Brand & Test Markings
                    # Base clean fire-rated security white
                    r, g, b = 0.94, 0.95, 0.96

                    # Red Fire Alarm Warning Triangle / Flame Symbol (center: x=65, y=384)
                    dx_flame = x - 65
                    dy_flame = y - 384
                    if -22 <= dy_flame <= 22 and abs(dx_flame) <= (22 - dy_flame) * 0.65:
                        r, g, b = 0.92, 0.14, 0.10  # Fire alarm bright red
                        if abs(dx_flame) <= 7 and -10 <= dy_flame <= 10:
                            r, g, b = 0.98, 0.88, 0.20  # Inner golden flame core

                    # Brand Typography "SYSTEM SENSOR" & "OPTICAL SMOKE SD-200"
                    if 365 <= y <= 405 and 100 <= x <= 245:
                        if (y in [372, 373, 374, 388, 389, 390]) and (x % 4 in [0, 1]):
                            r, g, b = 0.18, 0.20, 0.25

                    # "PUSH TO TEST / HUSH" button circular ring (center: x=128, y=460)
                    dist_test_btn = math.sqrt((x - 128)**2 + (y - 460)**2)
                    if 18 <= dist_test_btn <= 22:
                        r, g, b = 0.28, 0.31, 0.36
                    elif dist_test_btn < 18:
                        r, g, b = 0.88, 0.90, 0.93
                        if abs(x - 128) <= 8 and abs(y - 460) <= 2:
                            r, g, b = 0.18, 0.20, 0.24

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 1: Dark Charcoal Peripheral Smoke Intake Chamber & Wire Mesh
                    rel_x = (x - 256) % 128
                    r, g, b = 0.08, 0.09, 0.11  # Deep dark intake cavity
                    # Stainless steel insect screen mesh wires inside
                    if (y % 6 in [0, 1]) or (x % 6 in [0, 1]):
                        r, g, b = 0.28, 0.31, 0.38
                    # Side highlight edges
                    if rel_x in [0, 1, 126, 127]:
                        r, g, b = 0.40, 0.44, 0.50

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

            else:
                if x < 256:  # Quadrant 2: Ceiling Mounting Plate & Specification Label
                    r, g, b = 0.78, 0.80, 0.84
                    # Regulatory certification box & wiring terminal diagram
                    if (y in [30, 70, 110, 150, 190, 230]) or (x in [30, 80, 130, 180, 230]):
                        r, g, b = 0.14, 0.15, 0.18
                    # Circular twist-lock alignment arrows
                    dist_lbl_ctr = math.sqrt((x - 128)**2 + (y - 128)**2)
                    if 68 <= dist_lbl_ctr <= 74:
                        r, g, b = 0.12, 0.13, 0.16
                    # Red alignment arrow at rim
                    if 75 <= dist_lbl_ctr <= 95 and abs(x - 128) <= (95 - dist_lbl_ctr) * 0.8:
                        r, g, b = 0.85, 0.15, 0.12
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 3: Optical Sensing Maze & Metallic Heat Thermistor
                    # Center at x=384, y=128
                    dist_baffle = math.sqrt((x - 384)**2 + (y - 128)**2)
                    
                    if dist_baffle < 30:
                        # Center Metallic Heat Thermistor (radius < 30)
                        r, g, b = 0.88, 0.90, 0.94
                        if 25 <= dist_baffle <= 29 or 13 <= dist_baffle <= 16:
                            r, g, b = 0.99, 1.00, 1.00  # Specular ring highlight
                        elif dist_baffle < 7:
                            # Central thermistor sensor bead
                            r, g, b = 0.15, 0.16, 0.20
                    else:
                        # Concentric labyrinth smoke inlet rings (dist: 30..128)
                        ring_id = int(dist_baffle) % 16
                        if ring_id < 6:
                            # Deep optical scatter trap ring
                            r, g, b = 0.05, 0.05, 0.06
                        elif ring_id < 11:
                            # Stainless steel insect screen mesh
                            r, g, b = 0.38, 0.42, 0.48
                            if (x + y) % 4 in [0, 1]:
                                r, g, b = 0.62, 0.66, 0.74
                        else:
                            r, g, b = 0.22, 0.24, 0.28

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

    atlas_img.pixels = pixels
    atlas_path = os.path.abspath(os.path.join("exports", "T_Security_Atlas.png"))
    os.makedirs(os.path.dirname(atlas_path), exist_ok=True)
    atlas_img.filepath_raw = atlas_path
    atlas_img.file_format = 'PNG'
    try:
        atlas_img.save()
        print(f"[INFO] Texture atlas saved to: {atlas_path}")
    except Exception as e:
        print(f"[WARN] Failed to save atlas: {e}")
    atlas_img.pack()
    return atlas_img


def create_materials(atlas_img):
    """
    Create the 2 standard materials required for SEC_Sensor_Smoke_Fire:
    Slot 0: M_Security_Atlas
    Slot 1: M_Emission
    """
    mat_configs = [
        # (name, base_color, metallic, roughness, trans, emit_col, emit_str, diff_col)
        ("M_Security_Atlas", (0.94, 0.95, 0.96, 1.0), 0.05, 0.35, 0.0, (0, 0, 0, 1), 0.0, (0.94, 0.95, 0.96, 1.0)),
        ("M_Emission", (0.85, 0.02, 0.01, 1.0), 0.0, 0.20, 0.0, (1.0, 0.02, 0.01, 1.0), 6.0, (0.90, 0.04, 0.02, 1.0)),
    ]

    materials = {}
    for name, color, metallic, roughness, trans, emit_col, emit_str, diff_col in mat_configs:
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

            elif name == "M_Emission":
                bsdf.inputs["Base Color"].default_value = color
                bsdf.inputs["Roughness"].default_value = roughness
                if "Emission Color" in bsdf.inputs:
                    bsdf.inputs["Emission Color"].default_value = emit_col
                elif "Emission" in bsdf.inputs:
                    bsdf.inputs["Emission"].default_value = emit_col
                if "Emission Strength" in bsdf.inputs:
                    bsdf.inputs["Emission Strength"].default_value = emit_str

        mat.diffuse_color = diff_col
        materials[name] = mat

    return materials


def attach_standard_materials(mesh, materials):
    """Attach standard materials in exact order: Slot 0 = Atlas, Slot 1 = Emission."""
    ordered_keys = ["M_Security_Atlas", "M_Emission"]
    mesh.materials.clear()
    for k in ordered_keys:
        mesh.materials.append(materials[k])


# -------------------------------------------------------------
# UV Mapping Helpers
# -------------------------------------------------------------

def set_face_uv_rect(bm, face, uv_rect):
    """
    Project planar face UVs to a specific rectangular region [u0, v0, u1, v1] in the atlas.
    """
    u0, v0, u1, v1 = uv_rect
    uv_lay = bm.loops.layers.uv.verify()

    coords_2d = []
    normal = face.normal
    nx, ny, nz = abs(normal.x), abs(normal.y), abs(normal.z)

    for loop in face.loops:
        v = loop.vert.co
        if nx >= ny and nx >= nz:
            coords_2d.append((v.y, v.z))
        elif ny >= nx and ny >= nz:
            coords_2d.append((v.x, v.z))
        else:
            coords_2d.append((v.x, v.y))

    min_x = min(c[0] for c in coords_2d)
    max_x = max(c[0] for c in coords_2d)
    min_y = min(c[1] for c in coords_2d)
    max_y = max(c[1] for c in coords_2d)
    span_x = max_x - min_x if max_x > min_x else 1.0
    span_y = max_y - min_y if max_y > min_y else 1.0

    for i, loop in enumerate(face.loops):
        cx, cy = coords_2d[i]
        u = u0 + ((cx - min_x) / span_x) * (u1 - u0)
        v = v0 + ((cy - min_y) / span_y) * (v1 - v0)
        loop[uv_lay].uv = (u, v)


def set_face_uv_radial(bm, face, uv_center, uv_radius):
    """Map a circular or fan face radially to [uv_center_u, uv_center_v] with radius uv_radius."""
    cu, cv = uv_center
    uv_lay = bm.loops.layers.uv.verify()

    coords = [loop.vert.co for loop in face.loops]
    max_r = max(math.sqrt(co.x**2 + co.y**2) for co in coords)
    if max_r < 1e-6:
        max_r = 1.0

    for loop in face.loops:
        co = loop.vert.co
        u = cu + (co.x / max_r) * uv_radius
        v = cv + (co.y / max_r) * uv_radius
        loop[uv_lay].uv = (u, v)


# -------------------------------------------------------------
# Mesh Builders
# -------------------------------------------------------------

def build_ceiling_base_mesh(mesh, materials):
    """
    Build SEC_Sensor_Smoke_Fire (Ceiling_Base):
    Root object at (0, 0, 0).
    - Circular ceiling mounting flange at Z=0 (mounts flush to ceiling)
    - 16-segment circular resolution: diameter 120mm (radius 0.060m), depth 5mm (Z: 0.0 to -0.005m)
    - Top cap (14 tris), Side bevel (32 tris), Bottom lip (32 tris) = 78 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    segs = 16
    r_top = 0.060
    r_rim = 0.056
    r_lip = 0.052
    z_top = 0.000
    z_bot = -0.005

    angles = [2.0 * math.pi * i / segs for i in range(segs)]
    v_top = [bm.verts.new(Vector((r_top * math.cos(a), r_top * math.sin(a), z_top))) for a in angles]
    v_rim = [bm.verts.new(Vector((r_rim * math.cos(a), r_rim * math.sin(a), z_bot))) for a in angles]
    v_lip = [bm.verts.new(Vector((r_lip * math.cos(a), r_lip * math.sin(a), z_bot))) for a in angles]

    # 1. Top cap face (flush against ceiling, mapped to wiring schematic & spec label in Quadrant 2)
    f_top = bm.faces.new(list(reversed(v_top)))
    f_top.material_index = 0
    set_face_uv_radial(bm, f_top, (0.25, 0.25), 0.22)

    # 2. Outer side chamfer quads (white casing)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_top[i], v_rim[i], v_rim[ni], v_top[ni]])
        f.smooth = True
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.10, 0.55, 0.40, 0.70))

    # 3. Bottom annular mounting lip quads (meets Detector_Housing with zero gap!)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_rim[i], v_lip[i], v_lip[ni], v_rim[ni]])
        f.smooth = False
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.10, 0.55, 0.40, 0.70))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_detector_housing_mesh(mesh, materials):
    """
    Build Detector_Housing:
    Origin is at (0, 0, -0.005) local relative to SEC_Sensor_Smoke_Fire.
    Aerodynamic, contoured industrial optical smoke detector body:
    - 16 segments with 8 real physical 3D intake slots alternating with 8 structural ribs!
    - Ring 0: radius 0.052m at Z = 0.000m (meets Base lip seamlessly with zero gap!)
    - Ring 1 (upper intake shoulder at Z = -0.006m):
      Even i: R = 0.050m (outer rib)
      Odd i:  R = 0.044m (recessed intake slot!)
    - Ring 2 (lower intake baffle at Z = -0.013m):
      Even i: R = 0.048m (outer rib baffle)
      Odd i:  R = 0.043m (recessed intake channel floor!)
    - Ring 3 (smoothly sloping faceplate at Z = -0.024m):
      All vertices at R = 0.024m
    Tris count: 3 rings x 32 = 96 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.verify()

    segs = 16
    angles = [2.0 * math.pi * i / segs for i in range(segs)]

    # Ring 0: Top Collar (R = 0.052, Z = 0.000)
    v_r0 = [bm.verts.new(Vector((0.052 * math.cos(a), 0.052 * math.sin(a), 0.000))) for a in angles]

    # Ring 1: Upper Intake Shoulder (Z = -0.006)
    # Even: R = 0.050 (rib), Odd: R = 0.044 (recessed slot)
    v_r1 = []
    for i, a in enumerate(angles):
        r = 0.050 if (i % 2 == 0) else 0.044
        v_r1.append(bm.verts.new(Vector((r * math.cos(a), r * math.sin(a), -0.006))))

    # Ring 2: Lower Intake Baffle (Z = -0.013)
    # Even: R = 0.048 (rib baffle), Odd: R = 0.043 (intake slot)
    v_r2 = []
    for i, a in enumerate(angles):
        r = 0.048 if (i % 2 == 0) else 0.043
        v_r2.append(bm.verts.new(Vector((r * math.cos(a), r * math.sin(a), -0.013))))

    # Ring 3: Bottom Faceplate Rim (R = 0.024, Z = -0.024)
    v_r3 = [bm.verts.new(Vector((0.024 * math.cos(a), 0.024 * math.sin(a), -0.024))) for a in angles]

    # Ring 0 -> Ring 1 (Upper Dome Collar: Clean White Polymer)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_r0[i], v_r1[i], v_r1[ni], v_r0[ni]])
        f.smooth = True
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.05, 0.55, 0.45, 0.68))

    # Ring 1 -> Ring 2 (The 360-Degree Peripheral Intake Vents & Ribs!)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_r1[i], v_r2[i], v_r2[ni], v_r1[ni]])
        f.smooth = False
        f.material_index = 0
        if i % 2 == 1:  # Recessed Vent Slot -> Dark intake cavity with insect wire mesh!
            set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))
        else:           # Protruding Outer Rib -> Clean white casing
            set_face_uv_rect(bm, f, (0.05, 0.55, 0.45, 0.68))

    # Ring 2 -> Ring 3 (Smooth Sloping Front Faceplate)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_r2[i], v_r3[i], v_r3[ni], v_r2[ni]])
        f.smooth = True
        f.material_index = 0
        # Around -Y (segments 10, 11, 12, 13, 14): Red Flame, "SYSTEM SENSOR", and "TEST" button!
        if i in [10, 11]:   # Left of LED: Fire Alarm Red Flame & Brand Typography
            set_face_uv_rect(bm, f, (0.05, 0.68, 0.48, 0.84))
        elif i == 12:       # Center beneath LED (at -Y): "TEST / HUSH" button markings
            set_face_uv_rect(bm, f, (0.12, 0.82, 0.42, 0.98))
        elif i in [13, 14]: # Right of LED: Model & Certification marks
            set_face_uv_rect(bm, f, (0.05, 0.68, 0.48, 0.84))
        else:
            set_face_uv_rect(bm, f, (0.05, 0.55, 0.45, 0.68))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_vent_grille_mesh(mesh, materials):
    """
    Build Vent_Grille:
    Origin is at (0, 0, -0.024) local relative to Detector_Housing.
    Recessed Optical Sensing Labyrinth & Heat Thermistor:
    - Ring A (outer collar): radius 0.024m at Z = 0.000m (meets Ring 3 seamlessly)
    - Ring B (recessed optical labyrinth ring): radius 0.015m at Z = +0.003m (recessed into housing!)
    - Center Thermistor Heat Probe: apex vertex at Z = -0.002m
    Tris count: 16 quads (32 tris) + 16-fan tip (16 tris) = 48 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    segs = 16
    angles = [2.0 * math.pi * i / segs for i in range(segs)]

    r_a, z_a = 0.024,  0.000
    r_b, z_b = 0.015,  0.003  # Recessed into chamber!
    z_apex   = -0.002

    v_a = [bm.verts.new(Vector((r_a * math.cos(a), r_a * math.sin(a), z_a))) for a in angles]
    v_b = [bm.verts.new(Vector((r_b * math.cos(a), r_b * math.sin(a), z_b))) for a in angles]
    v_tip = bm.verts.new(Vector((0.0, 0.0, z_apex)))

    # 1. Outer Baffle Quads (Concentric smoke intake rings & stainless steel mesh)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_a[i], v_b[i], v_b[ni], v_a[ni]])
        f.smooth = False
        f.material_index = 0
        set_face_uv_radial(bm, f, (0.75, 0.25), 0.23)

    # 2. Central Thermistor Sensor Fan (Shiny metallic spun disc + sensor bead)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_b[i], v_tip, v_b[ni]])
        f.smooth = True
        f.material_index = 0
        set_face_uv_radial(bm, f, (0.75, 0.25), 0.12)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_status_led_mesh(mesh, materials):
    """
    Build Status_LED:
    Origin is at (0.0, -0.034, -0.019) local relative to Detector_Housing.
    Low-profile rounded jewel status LED nestled flush into the faceplate:
    - 6-sided jewel fan (6 tris) assigned to Slot 1: M_Emission (Ruby Red Alarm)
    - Back cap (4 tris) assigned to Slot 0: M_Security_Atlas
    Tris count: 10 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    r_led   = 0.0028
    h_tip   = 0.0012
    segs    = 6
    angles  = [2.0 * math.pi * i / segs for i in range(segs)]

    v_base = [bm.verts.new(Vector((r_led * math.cos(a), r_led * math.sin(a), 0.0))) for a in angles]
    v_tip  = bm.verts.new(Vector((0.0, 0.0, -h_tip)))

    # 1. Jewel Dome (Bright Red Alarm Emission)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_base[i], v_tip, v_base[ni]])
        f.smooth = True
        f.material_index = 1  # M_Emission
        set_face_uv_rect(bm, f, (0.1, 0.1, 0.9, 0.9))

    # 2. Back base cap
    f_b = bm.faces.new(v_base)
    f_b.material_index = 0
    set_face_uv_rect(bm, f_b, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Asset Assembly and Hierarchy
# -------------------------------------------------------------

def generate_asset():
    """Build the entire SEC_Sensor_Smoke_Fire asset with strict hierarchy."""
    setup_scene()
    atlas_img = setup_texture_atlas()
    materials = create_materials(atlas_img)

    # 1. Root Object: Ceiling_Base named SEC_Sensor_Smoke_Fire
    root_mesh = bpy.data.meshes.new("SEC_Sensor_Smoke_Fire_Mesh")
    build_ceiling_base_mesh(root_mesh, materials)
    root_obj = bpy.data.objects.new("SEC_Sensor_Smoke_Fire", root_mesh)
    bpy.context.collection.objects.link(root_obj)
    root_obj.location = (0.0, 0.0, 0.0)

    # 2. Detector_Housing (Child of SEC_Sensor_Smoke_Fire)
    housing_mesh = bpy.data.meshes.new("Detector_Housing_Mesh")
    build_detector_housing_mesh(housing_mesh, materials)
    housing_obj = bpy.data.objects.new("Detector_Housing", housing_mesh)
    bpy.context.collection.objects.link(housing_obj)
    housing_obj.parent = root_obj
    housing_obj.location = (0.0, 0.0, -0.005)

    # 3. Vent_Grille (Child of Detector_Housing)
    grille_mesh = bpy.data.meshes.new("Vent_Grille_Mesh")
    build_vent_grille_mesh(grille_mesh, materials)
    grille_obj = bpy.data.objects.new("Vent_Grille", grille_mesh)
    bpy.context.collection.objects.link(grille_obj)
    grille_obj.parent = housing_obj
    grille_obj.location = (0.0, 0.0, -0.024)

    # 4. Status_LED (Child of Detector_Housing)
    # Positioned flush on lower sloping faceplate at front (-Y)
    led_mesh = bpy.data.meshes.new("Status_LED_Mesh")
    build_status_led_mesh(led_mesh, materials)
    led_obj = bpy.data.objects.new("Status_LED", led_mesh)
    bpy.context.collection.objects.link(led_obj)
    led_obj.parent = housing_obj
    led_obj.location = (0.0, -0.034, -0.019)

    for obj in [root_obj, housing_obj, grille_obj, led_obj]:
        mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        mod.keep_sharp = True

    bpy.context.view_layer.update()

    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, housing_obj, grille_obj, led_obj]:
        eval_obj = obj.evaluated_get(depsgraph)
        mesh_eval = eval_obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh_eval)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        tris = len(bm.faces)
        total_tris += tris
        print(f"  Object '{obj.name}': {tris} tris")
        bm.free()
        eval_obj.to_mesh_clear()

    print(f"[INFO] Initial Triangulated Triangle Count: {total_tris}")
    if total_tris > 250:
        raise ValueError(f"Triangle count {total_tris} exceeds limit of 250 tris!")

    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root_obj, housing_obj, grille_obj, led_obj]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    fbx_path = os.path.join(exports_dir, "SEC_Sensor_Smoke_Fire.fbx")

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
    print(f"[INFO] Exported FBX to: {fbx_path}")

    blend_path = os.path.join(exports_dir, "SEC_Sensor_Smoke_Fire.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Saved blend file to: {blend_path}")

    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        try:
            os.remove(blend1_path)
            print(f"[INFO] Cleaned up temporary backup file: {blend1_path}")
        except Exception:
            pass

    return {
        "asset_name": "SEC_Sensor_Smoke_Fire",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "tris_count": total_tris,
        "mesh_count": 4,
        "empty_count": 0,
        "materials": ["M_Security_Atlas", "M_Emission"]
    }


def verify_fbx(fbx_path):
    """Re-import FBX and verify all constraints."""
    print(f"\n[VERIFY] Re-importing FBX from: {fbx_path}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    imported_names = {obj.name for obj in bpy.data.objects}
    print(f"[VERIFY] Imported objects: {imported_names}")

    expected_objects = [
        "SEC_Sensor_Smoke_Fire",
        "Detector_Housing",
        "Vent_Grille",
        "Status_LED"
    ]
    for name in expected_objects:
        if name not in imported_names:
            raise AssertionError(f"Expected object '{name}' was not found in imported FBX!")

    root_obj = bpy.data.objects["SEC_Sensor_Smoke_Fire"]
    housing_obj = bpy.data.objects["Detector_Housing"]
    grille_obj = bpy.data.objects["Vent_Grille"]
    led_obj = bpy.data.objects["Status_LED"]

    if housing_obj.parent != root_obj:
        raise AssertionError("Detector_Housing is not parented to SEC_Sensor_Smoke_Fire!")
    if grille_obj.parent != housing_obj:
        raise AssertionError("Vent_Grille is not parented to Detector_Housing!")
    if led_obj.parent != housing_obj:
        raise AssertionError("Status_LED is not parented to Detector_Housing!")
    print("[VERIFY] Full parent-child hierarchy verified.")

    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, housing_obj, grille_obj, led_obj]:
        eval_obj = obj.evaluated_get(depsgraph)
        mesh_eval = eval_obj.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(mesh_eval)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        tris = len(bm.faces)
        total_tris += tris
        bm.free()
        eval_obj.to_mesh_clear()

    print(f"[VERIFY] Total verified triangulated triangles: {total_tris}")
    if total_tris > 250:
        raise AssertionError(f"Verified triangle count {total_tris} exceeds limit 250!")

    expected_materials = ["M_Security_Atlas", "M_Emission"]
    for obj in [root_obj, housing_obj, grille_obj, led_obj]:
        slot_names = [slot.name for slot in obj.material_slots]
        print(f"[VERIFY] Object '{obj.name}' material slots: {slot_names}")
        if not slot_names:
            raise AssertionError(f"Object '{obj.name}' has no material slots!")
        for exp in expected_materials:
            if not any(exp in s for s in slot_names):
                raise AssertionError(f"Object '{obj.name}' is missing expected material {exp}!")

    for obj in [root_obj, housing_obj, grille_obj, led_obj]:
        if not obj.data.uv_layers:
            raise AssertionError(f"Object '{obj.name}' has no UV layers!")
        print(f"[VERIFY] Object '{obj.name}' has UV layer: {obj.data.uv_layers.active.name}")

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
        "asset_name": "SEC_Sensor_Smoke_Fire",
        "fbx_path": os.path.join("exports", "SEC_Sensor_Smoke_Fire.fbx"),
        "tris_count": 0,
        "mesh_count": 0,
        "empty_count": 0,
        "materials": ["M_Security_Atlas", "M_Emission"]
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
