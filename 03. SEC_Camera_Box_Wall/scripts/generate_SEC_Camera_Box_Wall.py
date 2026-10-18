"""
Generate SEC_Camera_Box_Wall 3D Asset
Wall-mounted Industrial Box CCTV Camera for security applications.
Follows general production standards:
- Real low-poly geometry (< 450 tris)
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
    """Generate high-detail packed 512x512 texture atlas with rich CCTV graphics."""
    atlas_img = bpy.data.images.get("T_Security_Atlas")
    if atlas_img is None:
        atlas_img = bpy.data.images.new("T_Security_Atlas", 512, 512)

    pixels = [0.0] * (512 * 512 * 4)
    for y in range(512):
        for x in range(512):
            idx = (y * 512 + x) * 4
            if y >= 256:
                if x < 256:  # Quadrant 0: CCTV White Plastic Body & Sunshield
                    # Base off-white
                    r, g, b = 0.92, 0.93, 0.94
                    # Dark Side Racing Stripe (y: 374..386)
                    if 374 <= y <= 386:
                        r, g, b = 0.12, 0.13, 0.15
                        # Model badge: "SEC-PRO 4K" metallic plate in center of stripe
                        if 85 <= x <= 170 and 377 <= y <= 383:
                            r, g, b = 0.80, 0.82, 0.85
                    # Side ventilation louvers (horizontal dark vent slits)
                    elif 30 <= x <= 85 and ((325 <= y <= 327) or (333 <= y <= 335) or (341 <= y <= 343) or (349 <= y <= 351)):
                        r, g, b = 0.10, 0.11, 0.12
                    # Sunshield Adjustment Slider Channel & Screw
                    elif 460 <= y <= 468 and 50 <= x <= 205:
                        r, g, b = 0.15, 0.16, 0.18
                        dist_screw = math.sqrt((x - 128)**2 + (y - 464)**2)
                        if dist_screw < 7:
                            # Silver lock screw with cross slot
                            if abs(x - 128) <= 1 or abs(y - 464) <= 1:
                                r, g, b = 0.1, 0.1, 0.1
                            else:
                                r, g, b = 0.85, 0.85, 0.88
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 1: Dark Matte Anthracite (Front & Rear Panels)
                    r, g, b = 0.08, 0.09, 0.11
                    # RJ45 Ethernet port cavity (x: 275..315, y: 275..315)
                    if 275 <= x <= 315 and 275 <= y <= 315:
                        if 280 <= x <= 310 and 280 <= y <= 310:
                            r, g, b = 0.03, 0.03, 0.03
                            # Gold pin contacts
                            if 285 <= x <= 305 and 302 <= y <= 308 and (x % 3 == 0):
                                r, g, b = 0.95, 0.78, 0.20
                        else:
                            r, g, b = 0.18, 0.19, 0.22
                    # Product Spec Label / Barcode (x: 340..490, y: 275..325)
                    elif 340 <= x <= 490 and 275 <= y <= 325:
                        r, g, b = 0.72, 0.74, 0.76
                        # Black barcode lines and spec text rows
                        if (y in [282, 288, 294, 300, 312]) or (318 <= y <= 322 and (x % 4 in [0, 1])):
                            r, g, b = 0.12, 0.12, 0.12
                    # Front CdS optical light sensor dot (x: 288..304, y: 448..464)
                    elif math.sqrt((x - 296)**2 + (y - 456)**2) < 8:
                        r, g, b = 0.04, 0.04, 0.06
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

            else:
                if x < 256:  # Quadrant 2: Gunmetal Metal (Bracket, Knurling & Screws)
                    r, g, b = 0.14, 0.15, 0.18
                    # Knurled diamond grip texture (x: 10..120, y: 10..120)
                    if 10 <= x <= 120 and 10 <= y <= 120:
                        if (x + y) % 6 < 3:
                            r, g, b = 0.24, 0.25, 0.28
                        else:
                            r, g, b = 0.10, 0.11, 0.12
                    # Angle measurement tick marks on knuckle dial (x: 140..240, y: 30..70)
                    elif 140 <= x <= 240 and 30 <= y <= 70:
                        if 45 <= y <= 55 and (x % 10 in [0, 1]):
                            r, g, b = 0.85, 0.88, 0.90
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 3: Tech Accents, Dual LEDs & Lens Markings
                    r, g, b = 0.10, 0.11, 0.13
                    # Green Power LED (center: 330, 128)
                    dist_pwr = math.sqrt((x - 330)**2 + (y - 128)**2)
                    if dist_pwr < 20:
                        r, g, b = 0.10, 0.98, 0.25
                    elif dist_pwr < 28:
                        r, g, b = 0.04, 0.04, 0.05
                    # Amber Network LED (center: 430, 128)
                    dist_net = math.sqrt((x - 430)**2 + (y - 128)**2)
                    if dist_net < 20:
                        r, g, b = 1.00, 0.65, 0.05
                    elif dist_net < 28:
                        r, g, b = 0.04, 0.04, 0.05
                    # Lens focal ring calibration text: "W <---> T" & "N <---> F"
                    elif 180 <= y <= 215 and 270 <= x <= 490:
                        if (y in [186, 208]) or (x in [300, 340, 380, 420, 460] and 190 <= y <= 204):
                            r, g, b = 0.85, 0.88, 0.92
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
    Create the 3 standard materials required for SEC_Camera_Box_Wall:
    Slot 0: M_Security_Atlas
    Slot 1: M_Lens_Glass
    Slot 2: M_Metal
    """
    mat_configs = [
        # (name, base_color, metallic, roughness, diff_col)
        ("M_Security_Atlas", (0.92, 0.93, 0.94, 1.0), 0.05, 0.35, (0.92, 0.93, 0.94, 1.0)),
        ("M_Lens_Glass", (0.01, 0.03, 0.08, 1.0), 0.10, 0.02, (0.05, 0.25, 0.60, 1.0)),
        ("M_Metal", (0.18, 0.19, 0.22, 1.0), 0.85, 0.25, (0.18, 0.19, 0.22, 1.0)),
    ]

    materials = {}
    for name, color, metallic, roughness, diff_col in mat_configs:
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
            elif name == "M_Lens_Glass":
                bsdf.inputs["Base Color"].default_value = color
                bsdf.inputs["Roughness"].default_value = 0.02
                bsdf.inputs["Metallic"].default_value = 0.12
                if "Specular IOR Level" in bsdf.inputs:
                    bsdf.inputs["Specular IOR Level"].default_value = 0.95
                elif "Specular" in bsdf.inputs:
                    bsdf.inputs["Specular"].default_value = 0.95
                if "Transmission Weight" in bsdf.inputs:
                    bsdf.inputs["Transmission Weight"].default_value = 0.0
                elif "Transmission" in bsdf.inputs:
                    bsdf.inputs["Transmission"].default_value = 0.0
            else:  # M_Metal
                bsdf.inputs["Base Color"].default_value = color
                bsdf.inputs["Roughness"].default_value = roughness
                bsdf.inputs["Metallic"].default_value = metallic

        mat.diffuse_color = diff_col
        materials[name] = mat

    return materials


def attach_standard_materials(mesh, materials):
    """Pre-attach materials to mesh so bmesh face material indices are preserved."""
    ordered_keys = ["M_Security_Atlas", "M_Lens_Glass", "M_Metal"]
    mesh.materials.clear()
    for k in ordered_keys:
        mesh.materials.append(materials[k])


# -------------------------------------------------------------
# UV Mapping Helpers
# -------------------------------------------------------------

def set_face_uv_rect(bm, face, uv_rect):
    """Map face loops to a given UV bounding box (u_min, v_min, u_max, v_max)."""
    uv_lay = bm.loops.layers.uv.verify()
    u0, v0, u1, v1 = uv_rect
    coords_2d = []
    norm = face.normal
    nx, ny, nz = abs(norm.x), abs(norm.y), abs(norm.z)
    for loop in face.loops:
        v = loop.vert.co
        if nx >= ny and nx >= nz:
            coords_2d.append((v.y, v.z))
        elif ny >= nx and ny >= nz:
            coords_2d.append((v.x, v.z))
        else:
            coords_2d.append((v.x, v.y))

    if not coords_2d:
        return

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


# -------------------------------------------------------------
# Mesh Builders
# -------------------------------------------------------------

def build_mount_plate_mesh(mesh, materials):
    """
    Build SEC_Camera_Box_Wall (Mount Plate):
    - Chamfered wall plate flush at Y=0 (from Y=0.0 to Y=0.012, width 0.09m, height 0.09m)
    - 4 corner screw insets
    - Base collar reinforcement flange at arm-plate junction
    - Sturdy horizontal bracket arm extending to Y=0.105
    - Knuckle clevis fork tabs extending to Y=0.128 (knuckle center at Y=0.120)
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # 1. Chamfered Wall Plate (8-sided profile in X-Z)
    sx, sz = 0.045, 0.045
    c = 0.012
    plate_pts = [
        (sx - c, sz), (-sx + c, sz),
        (-sx, sz - c), (-sx, -sz + c),
        (-sx + c, -sz), (sx - c, -sz),
        (sx, -sz + c), (sx, sz - c)
    ]
    back_verts = [bm.verts.new(Vector((x, 0.0, z))) for x, z in plate_pts]
    front_verts = [bm.verts.new(Vector((x, 0.012, z))) for x, z in plate_pts]

    # Back face
    f_back = bm.faces.new(list(reversed(back_verts)))
    f_back.material_index = 2
    set_face_uv_rect(bm, f_back, (0.05, 0.05, 0.45, 0.45))

    # Front face
    f_front = bm.faces.new(front_verts)
    f_front.material_index = 2
    set_face_uv_rect(bm, f_front, (0.05, 0.05, 0.45, 0.45))

    # Side chamfer quads
    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([back_verts[i], front_verts[i], front_verts[ni], back_verts[ni]])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    # 2. 4 Corner Screw Insets
    screw_locs = [(0.030, 0.030), (-0.030, 0.030), (-0.030, -0.030), (0.030, -0.030)]
    sr = 0.004
    for cx, cz in screw_locs:
        sb_verts = [
            bm.verts.new(Vector((cx - sr, 0.013, cz - sr))),
            bm.verts.new(Vector((cx + sr, 0.013, cz - sr))),
            bm.verts.new(Vector((cx + sr, 0.013, cz + sr))),
            bm.verts.new(Vector((cx - sr, 0.013, cz + sr))),
        ]
        f_sb = bm.faces.new(sb_verts)
        f_sb.material_index = 0
        set_face_uv_rect(bm, f_sb, (0.55, 0.55, 0.95, 0.95))

    # 3. Base Collar Reinforcement Flange (at Y=0.012 to Y=0.018, radius 0.022m)
    collar_r = 0.022
    n_seg = 6
    col_v0 = []
    col_v1 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = collar_r * math.cos(ang)
        vz = collar_r * math.sin(ang)
        col_v0.append(bm.verts.new(Vector((vx, 0.012, vz))))
        col_v1.append(bm.verts.new(Vector((vx * 0.85, 0.020, vz * 0.85))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([col_v0[i], col_v1[i], col_v1[ni], col_v0[ni]])
        f.smooth = True
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    # 4. Horizontal Bracket Arm (extends from Y=0.020 to Y=0.105, radius 0.015m)
    stem_r = 0.015
    arm_base_verts = col_v1
    arm_end_verts = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = stem_r * math.cos(ang)
        vz = stem_r * math.sin(ang)
        arm_end_verts.append(bm.verts.new(Vector((vx, 0.105, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([arm_base_verts[i], arm_end_verts[i], arm_end_verts[ni], arm_base_verts[ni]])
        f.smooth = True
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    f_acap = bm.faces.new(arm_end_verts)
    f_acap.material_index = 2
    set_face_uv_rect(bm, f_acap, (0.05, 0.05, 0.45, 0.45))

    # 5. Knuckle Clevis Fork Tabs (extends Y=0.102 to Y=0.128, knuckle pivot at Y=0.120)
    def add_clevis_prong(x_min, x_max):
        y_min, y_max = 0.102, 0.128
        z_min, z_max = -0.012, 0.012
        corners = [
            (x_min, y_min, z_min), (x_max, y_min, z_min), (x_max, y_max, z_min), (x_min, y_max, z_min),
            (x_min, y_min, z_max), (x_max, y_min, z_max), (x_max, y_max, z_max), (x_min, y_max, z_max)
        ]
        cv = [bm.verts.new(Vector(c)) for c in corners]
        faces_idx = [
            [0, 1, 2, 3], [4, 7, 6, 5],
            [0, 4, 5, 1], [2, 6, 7, 3],
            [0, 3, 7, 4], [1, 5, 6, 2]
        ]
        for f_idx in faces_idx:
            f = bm.faces.new([cv[j] for j in f_idx])
            f.material_index = 2
            set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    add_clevis_prong(-0.016, -0.010)
    add_clevis_prong(0.010, 0.016)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_mount_bracket_mesh(mesh, materials):
    """
    Build Mount_Bracket:
    Origin is at Bracket_Pivot (knuckle center at (0, 0, 0) local).
    Contains:
    - Knuckle cylinder (X-axis, width X: -0.0095 to +0.0095, radius 0.0095m)
    - Locking thumbscrew / T-bolt on left side with knurled grips
    - Vertical neck reaching directly up to camera mounting shoe
    - Camera mounting shoe cradle plate attached to bottom of camera body
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # 1. Knuckle cylinder (aligned with X axis)
    kr = 0.0095
    n_seg = 6
    lx = -0.0095
    rx = 0.0095
    left_verts = []
    right_verts = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vy = kr * math.cos(ang)
        vz = kr * math.sin(ang)
        left_verts.append(bm.verts.new(Vector((lx, vy, vz))))
        right_verts.append(bm.verts.new(Vector((rx, vy, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([left_verts[i], right_verts[i], right_verts[ni], left_verts[ni]])
        f.smooth = True
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.55, 0.10, 0.95, 0.30))  # Angle index tick marks

    f_lc = bm.faces.new(list(reversed(left_verts)))
    f_lc.material_index = 2
    set_face_uv_rect(bm, f_lc, (0.05, 0.05, 0.45, 0.45))

    f_rc = bm.faces.new(right_verts)
    f_rc.material_index = 2
    set_face_uv_rect(bm, f_rc, (0.05, 0.05, 0.45, 0.45))

    # 2. Locking Thumbscrew / T-bar bolt on left side
    bolt_x0 = -0.016
    bolt_x1 = -0.024
    bolt_r = 0.0065
    b_seg = 6
    bv_in = []
    bv_out = []
    for i in range(b_seg):
        ang = 2.0 * math.pi * i / b_seg
        vy = bolt_r * math.cos(ang)
        vz = bolt_r * math.sin(ang)
        bv_in.append(bm.verts.new(Vector((bolt_x0, vy, vz))))
        bv_out.append(bm.verts.new(Vector((bolt_x1, vy, vz))))

    for i in range(b_seg):
        ni = (i + 1) % b_seg
        f = bm.faces.new([bv_in[i], bv_out[i], bv_out[ni], bv_in[ni]])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.25, 0.25))  # Diamond knurl texture
    f_bout = bm.faces.new(list(reversed(bv_out)))
    f_bout.material_index = 2
    set_face_uv_rect(bm, f_bout, (0.05, 0.05, 0.45, 0.45))

    # 3. Vertical Support Neck (from knuckle up to camera shoe Z=0.018)
    nw = 0.008
    ny = 0.009
    neck_verts = [
        bm.verts.new(Vector((-nw, -ny, 0.000))),
        bm.verts.new(Vector(( nw, -ny, 0.000))),
        bm.verts.new(Vector(( nw,  ny, 0.000))),
        bm.verts.new(Vector((-nw,  ny, 0.000))),
        bm.verts.new(Vector((-nw, -ny, 0.018))),
        bm.verts.new(Vector(( nw, -ny, 0.018))),
        bm.verts.new(Vector(( nw,  ny, 0.018))),
        bm.verts.new(Vector((-nw,  ny, 0.018))),
    ]
    neck_faces = [
        [0, 1, 5, 4],  # rear
        [2, 3, 7, 6],  # front
        [0, 4, 7, 3],  # left
        [1, 2, 6, 5],  # right
    ]
    for nf in neck_faces:
        f = bm.faces.new([neck_verts[j] for j in nf])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    # 4. Camera Mounting Shoe (Flat cradle plate directly on camera bottom)
    sx0, sx1 = -0.018, 0.018
    sy0, sy1 = -0.024, 0.024
    sz0, sz1 = 0.018, 0.022
    shoe_corners = [
        (sx0, sy0, sz0), (sx1, sy0, sz0), (sx1, sy1, sz0), (sx0, sy1, sz0),
        (sx0, sy0, sz1), (sx1, sy0, sz1), (sx1, sy1, sz1), (sx0, sy1, sz1)
    ]
    shv = [bm.verts.new(Vector(c)) for c in shoe_corners]
    shoe_faces = [
        [0, 1, 2, 3], [4, 7, 6, 5],
        [0, 4, 5, 1], [2, 6, 7, 3],
        [0, 3, 7, 4], [1, 5, 6, 2]
    ]
    for sf in shoe_faces:
        f = bm.faces.new([shv[j] for j in sf])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_camera_housing_mesh(mesh, materials):
    """
    Build Camera_Housing:
    Origin is at Bracket_Pivot (knuckle center at (0, 0, 0) local).
    Contains:
    - Main rectangular camera body with chamfered edges, balanced over pivot
    - Front faceplate with lens mount collar and CdS optical ambient light sensor
    - Rear faceplate with BNC connector gland, flexible curved conduit cable, and dual LEDs
    - Sunshield Canopy: 100% planar extrusion with adjustment slot, lock screw, and mount rails
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # 1. Main Housing Body (Z from 0.022 to 0.082, Y from -0.065 to +0.095)
    hx, hz_mid = 0.038, 0.052
    z_min, z_max = 0.022, 0.082
    ch = 0.008

    body_pts = [
        (hx - ch, z_max), (-hx + ch, z_max),
        (-hx, z_max - ch), (-hx, z_min + ch),
        (-hx + ch, z_min), (hx - ch, z_min),
        (hx, z_min + ch), (hx, z_max - ch)
    ]

    y_rear = -0.065
    y_front = 0.095

    rear_verts = [bm.verts.new(Vector((x, y_rear, z))) for x, z in body_pts]
    front_verts = [bm.verts.new(Vector((x, y_front, z))) for x, z in body_pts]

    # Rear face (mapped to spec label, barcode, and ethernet port in quadrant 1)
    f_rear = bm.faces.new(list(reversed(rear_verts)))
    f_rear.material_index = 0
    set_face_uv_rect(bm, f_rear, (0.55, 0.55, 0.95, 0.95))

    # Front face
    f_front = bm.faces.new(front_verts)
    f_front.material_index = 0
    set_face_uv_rect(bm, f_front, (0.55, 0.55, 0.95, 0.95))

    # 8 Body sides (mapped to model branding badge and ventilation louvers)
    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([rear_verts[i], front_verts[i], front_verts[ni], rear_verts[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.05, 0.55, 0.45, 0.95))

    # 2. Front Bezel Lip & CdS Light Sensor
    # Front Collar step (Y: 0.095 to 0.100, radius 0.026m)
    f_lip_r = 0.026
    n_seg = 6
    lip_verts0 = []
    lip_verts1 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = f_lip_r * math.cos(ang)
        vz = hz_mid + f_lip_r * math.sin(ang)
        lip_verts0.append(bm.verts.new(Vector((vx, 0.095, vz))))
        lip_verts1.append(bm.verts.new(Vector((vx, 0.100, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([lip_verts0[i], lip_verts1[i], lip_verts1[ni], lip_verts0[ni]])
        f.smooth = True
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    f_lip_cap = bm.faces.new(lip_verts1)
    f_lip_cap.material_index = 0
    set_face_uv_rect(bm, f_lip_cap, (0.55, 0.55, 0.95, 0.95))

    # CdS Ambient Light Sensor on front faceplate (at X=-0.022, Z=0.068, Y=0.096)
    cds_r = 0.003
    cds_verts = [
        bm.verts.new(Vector((-0.022 - cds_r, 0.096, 0.068 - cds_r))),
        bm.verts.new(Vector((-0.022 + cds_r, 0.096, 0.068 - cds_r))),
        bm.verts.new(Vector((-0.022 + cds_r, 0.096, 0.068 + cds_r))),
        bm.verts.new(Vector((-0.022 - cds_r, 0.096, 0.068 + cds_r))),
    ]
    f_cds = bm.faces.new(cds_verts)
    f_cds.material_index = 0
    set_face_uv_rect(bm, f_cds, (0.56, 0.88, 0.60, 0.92))

    # 3. Rear Details: BNC Gland, Curved Conduit Cable, and Dual LEDs
    # BNC metal gland at rear (Y from -0.065 to -0.075, radius 0.008m at (0, Y, 0.046))
    g_r = 0.008
    g_z = 0.046
    g_seg = 6
    gv0 = []
    gv1 = []
    for i in range(g_seg):
        ang = 2.0 * math.pi * i / g_seg
        vx = g_r * math.cos(ang)
        vz = g_z + g_r * math.sin(ang)
        gv0.append(bm.verts.new(Vector((vx, -0.065, vz))))
        gv1.append(bm.verts.new(Vector((vx, -0.075, vz))))

    for i in range(g_seg):
        ni = (i + 1) % g_seg
        f = bm.faces.new([gv0[i], gv1[i], gv1[ni], gv0[ni]])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))
    f_gcap = bm.faces.new(list(reversed(gv1)))
    f_gcap.material_index = 2
    set_face_uv_rect(bm, f_gcap, (0.05, 0.05, 0.45, 0.45))

    # Flexible Curved Conduit Cable (loops down from BNC gland towards bracket)
    cab_r = 0.004
    # Ring 1: at BNC exit (Y=-0.075, Z=0.046)
    # Ring 2: curved down (Y=-0.060, Z=0.015)
    # Ring 3: entering towards bracket (Y=-0.035, Z=0.008)
    cab_nodes = [
        Vector((0.0, -0.075, 0.046)),
        Vector((0.0, -0.058, 0.016)),
        Vector((0.0, -0.032, 0.008))
    ]
    c_seg = 4
    cab_rings = []
    for k, node in enumerate(cab_nodes):
        ring_v = []
        for i in range(c_seg):
            ang = 2.0 * math.pi * i / c_seg
            if k == 0:
                vx = cab_r * math.cos(ang)
                vz = node.z + cab_r * math.sin(ang)
                vy = node.y
            else:
                vx = cab_r * math.cos(ang)
                vy = node.y + cab_r * math.sin(ang) * 0.7
                vz = node.z
            ring_v.append(bm.verts.new(Vector((vx, vy, vz))))
        cab_rings.append(ring_v)

    for k in range(2):
        for i in range(c_seg):
            ni = (i + 1) % c_seg
            f = bm.faces.new([cab_rings[k][i], cab_rings[k+1][i], cab_rings[k+1][ni], cab_rings[k][ni]])
            f.smooth = True
            f.material_index = 0
            set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # Rear Dual LEDs (Green Power LED & Amber Network Activity LED)
    led_sz = 0.0035
    # Green LED
    led_g = [
        bm.verts.new(Vector((0.022 - led_sz, -0.0652, 0.068 - led_sz))),
        bm.verts.new(Vector((0.022 + led_sz, -0.0652, 0.068 - led_sz))),
        bm.verts.new(Vector((0.022 + led_sz, -0.0652, 0.068 + led_sz))),
        bm.verts.new(Vector((0.022 - led_sz, -0.0652, 0.068 + led_sz))),
    ]
    f_led_g = bm.faces.new(list(reversed(led_g)))
    f_led_g.material_index = 0
    set_face_uv_rect(bm, f_led_g, (0.60, 0.20, 0.70, 0.30))  # Green LED

    # Amber LED
    led_a = [
        bm.verts.new(Vector((0.012 - led_sz, -0.0652, 0.068 - led_sz))),
        bm.verts.new(Vector((0.012 + led_sz, -0.0652, 0.068 - led_sz))),
        bm.verts.new(Vector((0.012 + led_sz, -0.0652, 0.068 + led_sz))),
        bm.verts.new(Vector((0.012 - led_sz, -0.0652, 0.068 + led_sz))),
    ]
    f_led_a = bm.faces.new(list(reversed(led_a)))
    f_led_a.material_index = 0
    set_face_uv_rect(bm, f_led_a, (0.80, 0.20, 0.90, 0.30))  # Amber LED

    # 4. Sunshield Canopy (Visor Hood)
    # Strictly planar extrusion along Y: from Y = -0.075 to Y = +0.125
    y_sh_r = -0.075
    y_sh_f =  0.125

    sh_prof_outer = [
        (-0.046, 0.078),
        (-0.042, 0.086),
        ( 0.000, 0.090),
        ( 0.042, 0.086),
        ( 0.046, 0.078),
    ]
    sh_prof_inner = [
        (-0.044, 0.080),
        (-0.040, 0.084),
        ( 0.000, 0.088),
        ( 0.040, 0.084),
        ( 0.044, 0.080),
    ]

    rf_out_r = [bm.verts.new(Vector((x, y_sh_r, z))) for x, z in sh_prof_outer]
    rf_out_f = [bm.verts.new(Vector((x, y_sh_f, z))) for x, z in sh_prof_outer]

    rf_in_r = [bm.verts.new(Vector((x, y_sh_r, z))) for x, z in sh_prof_inner]
    rf_in_f = [bm.verts.new(Vector((x, y_sh_f, z))) for x, z in sh_prof_inner]

    # Outer roof faces (mapped to adjustment slide channel and lock screw in quadrant 0)
    for i in range(4):
        f = bm.faces.new([rf_out_r[i], rf_out_f[i], rf_out_f[i+1], rf_out_r[i+1]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.05, 0.70, 0.45, 0.98))

    # Inner roof underside faces (dark anthracite)
    for i in range(4):
        f = bm.faces.new([rf_in_r[i+1], rf_in_f[i+1], rf_in_f[i], rf_in_r[i]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # Front and rear rim thickness edges (dark trim)
    for i in range(4):
        f_frim = bm.faces.new([rf_out_f[i], rf_in_f[i], rf_in_f[i+1], rf_out_f[i+1]])
        f_frim.material_index = 0
        set_face_uv_rect(bm, f_frim, (0.55, 0.55, 0.95, 0.95))

        f_rrim = bm.faces.new([rf_out_r[i+1], rf_in_r[i+1], rf_in_r[i], rf_out_r[i]])
        f_rrim.material_index = 0
        set_face_uv_rect(bm, f_rrim, (0.55, 0.55, 0.95, 0.95))

    # 5. Low-profile Mounting Rails (connect sunshield to camera body top)
    for rx in [-0.022, 0.022]:
        rw = 0.003
        rz0, rz1 = 0.082, 0.088
        ry0, ry1 = -0.040, 0.070
        rc = [
            (rx - rw, ry0, rz0), (rx + rw, ry0, rz0), (rx + rw, ry1, rz0), (rx - rw, ry1, rz0),
            (rx - rw, ry0, rz1), (rx + rw, ry0, rz1), (rx + rw, ry1, rz1), (rx - rw, ry1, rz1),
        ]
        rcv = [bm.verts.new(Vector(p)) for p in rc]
        for f_idx in [[0, 1, 5, 4], [2, 3, 7, 6], [0, 3, 7, 4], [1, 2, 6, 5]]:
            f = bm.faces.new([rcv[j] for j in f_idx])
            f.material_index = 0
            set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_lens_barrel_mesh(mesh, materials):
    """
    Build Lens_Barrel:
    Origin is at camera front center (0, 0.100, 0.052) relative to Bracket_Pivot.
    8-sided CS-Mount Industrial Varifocal Lens with zoom & focus thumb levers:
    - Base collar: 8-sided cylinder, radius 0.023m, Y: 0.0 to 0.010
    - Stepped zoom ring: 8-sided cylinder, radius 0.025m, Y: 0.010 to 0.024
    - Zoom adjustment thumb pin (pyramid lever at angle +45°)
    - Stepped focus ring: 8-sided cylinder, radius 0.024m, Y: 0.024 to 0.038
    - Focus adjustment thumb pin (pyramid lever at angle -45°)
    - Front cone taper: 8-sided cylinder, radius 0.020m, Y: 0.038 to 0.046
    - Recessed front bezel rim holding glass: Y=0.044, radius 0.016m
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    n_seg = 6
    # Step 1: Base collar
    r_base = 0.023
    v_base0 = []
    v_base1 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = r_base * math.cos(ang)
        vz = r_base * math.sin(ang)
        v_base0.append(bm.verts.new(Vector((vx, 0.000, vz))))
        v_base1.append(bm.verts.new(Vector((vx, 0.010, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_base0[i], v_base1[i], v_base1[ni], v_base0[ni]])
        f.smooth = True
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    f_bcap = bm.faces.new(list(reversed(v_base0)))
    f_bcap.material_index = 2
    set_face_uv_rect(bm, f_bcap, (0.05, 0.05, 0.45, 0.45))

    # Step 2: Zoom Ring (radius 0.025m, Y: 0.010 to 0.024)
    r_zoom = 0.025
    v_zm0 = []
    v_zm1 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = r_zoom * math.cos(ang)
        vz = r_zoom * math.sin(ang)
        v_zm0.append(bm.verts.new(Vector((vx, 0.010, vz))))
        v_zm1.append(bm.verts.new(Vector((vx, 0.024, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_base1[i], v_zm0[i], v_zm0[ni], v_base1[ni]])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_zm0[i], v_zm1[i], v_zm1[ni], v_zm0[ni]])
        f.smooth = True
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.25, 0.25))

    # Zoom Pin (clean 5-vert pyramid lever at +45 deg)
    ang_zp = math.radians(45)
    px, pz = math.cos(ang_zp), math.sin(ang_zp)
    zp_base = Vector((px * r_zoom, 0.017, pz * r_zoom))
    zp_tip  = Vector((px * (r_zoom + 0.007), 0.017, pz * (r_zoom + 0.007)))
    pr = 0.0025
    zv_b0 = bm.verts.new(zp_base + Vector((-pr, -pr, 0)))
    zv_b1 = bm.verts.new(zp_base + Vector(( pr, -pr, 0)))
    zv_b2 = bm.verts.new(zp_base + Vector(( pr,  pr, 0)))
    zv_b3 = bm.verts.new(zp_base + Vector((-pr,  pr, 0)))
    zv_top = bm.verts.new(zp_tip)
    for z_side in [[zv_b0, zv_b1, zv_top], [zv_b1, zv_b2, zv_top], [zv_b2, zv_b3, zv_top], [zv_b3, zv_b0, zv_top]]:
        f = bm.faces.new(z_side)
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    # Step 3: Focus Ring (radius 0.024m, Y: 0.024 to 0.038)
    r_foc = 0.024
    v_foc0 = []
    v_foc1 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = r_foc * math.cos(ang)
        vz = r_foc * math.sin(ang)
        v_foc0.append(bm.verts.new(Vector((vx, 0.024, vz))))
        v_foc1.append(bm.verts.new(Vector((vx, 0.038, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_zm1[i], v_foc0[i], v_foc0[ni], v_zm1[ni]])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_foc0[i], v_foc1[i], v_foc1[ni], v_foc0[ni]])
        f.smooth = True
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.35, 0.95, 0.45))  # Calibration text band

    # Focus Pin (clean 5-vert pyramid lever at -45 deg)
    ang_fp = math.radians(135)
    fx, fz = math.cos(ang_fp), math.sin(ang_fp)
    fp_base = Vector((fx * r_foc, 0.031, fz * r_foc))
    fp_tip  = Vector((fx * (r_foc + 0.007), 0.031, fz * (r_foc + 0.007)))
    fv_b0 = bm.verts.new(fp_base + Vector((-pr, -pr, 0)))
    fv_b1 = bm.verts.new(fp_base + Vector(( pr, -pr, 0)))
    fv_b2 = bm.verts.new(fp_base + Vector(( pr,  pr, 0)))
    fv_b3 = bm.verts.new(fp_base + Vector((-pr,  pr, 0)))
    fv_top = bm.verts.new(fp_tip)
    for f_side in [[fv_b0, fv_b1, fv_top], [fv_b1, fv_b2, fv_top], [fv_b2, fv_b3, fv_top], [fv_b3, fv_b0, fv_top]]:
        f = bm.faces.new(f_side)
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    # Step 4: Front Cone & Bezel (radius 0.020m, Y: 0.038 to 0.046)
    r_front = 0.020
    v_fr0 = []
    v_fr1 = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = r_front * math.cos(ang)
        vz = r_front * math.sin(ang)
        v_fr0.append(bm.verts.new(Vector((vx, 0.038, vz))))
        v_fr1.append(bm.verts.new(Vector((vx, 0.046, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_foc1[i], v_fr0[i], v_fr0[ni], v_foc1[ni]])
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.05, 0.05, 0.45, 0.45))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_fr0[i], v_fr1[i], v_fr1[ni], v_fr0[ni]])
        f.smooth = True
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # Front inner bezel rim
    r_in = 0.016
    v_in = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = r_in * math.cos(ang)
        vz = r_in * math.sin(ang)
        v_in.append(bm.verts.new(Vector((vx, 0.044, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_fr1[i], v_in[i], v_in[ni], v_fr1[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_lens_glass_mesh(mesh, materials):
    """
    Build Lens_Glass:
    Origin is at front rim of Lens_Barrel (0, 0.044, 0) in local lens space.
    Convex optical glass disc (8-sided).
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    n_seg = 6
    gr = 0.016
    v_center_f = bm.verts.new(Vector((0.0, 0.002, 0.0)))
    v_center_b = bm.verts.new(Vector((0.0, -0.001, 0.0)))

    rim_verts = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        vx = gr * math.cos(ang)
        vz = gr * math.sin(ang)
        rim_verts.append(bm.verts.new(Vector((vx, 0.000, vz))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_center_f, rim_verts[i], rim_verts[ni]])
        f.smooth = True
        f.material_index = 1
        set_face_uv_rect(bm, f, (0.1, 0.1, 0.9, 0.9))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_center_b, rim_verts[ni], rim_verts[i]])
        f.material_index = 1
        set_face_uv_rect(bm, f, (0.1, 0.1, 0.9, 0.9))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    mesh.update()


# -------------------------------------------------------------
# Asset Assembly and Hierarchy
# -------------------------------------------------------------

def generate_asset():
    """Build the entire SEC_Camera_Box_Wall asset with strict hierarchy and pivots."""
    setup_scene()
    atlas_img = setup_texture_atlas()
    materials = create_materials(atlas_img)

    # 1. Root Object: Mount_Plate named SEC_Camera_Box_Wall
    root_mesh = bpy.data.meshes.new("SEC_Camera_Box_Wall_Mesh")
    build_mount_plate_mesh(root_mesh, materials)
    root_obj = bpy.data.objects.new("SEC_Camera_Box_Wall", root_mesh)
    bpy.context.collection.objects.link(root_obj)
    root_obj.location = (0.0, 0.0, 0.0)

    # 2. Empty Pivot: Bracket_Pivot
    pivot = bpy.data.objects.new("Bracket_Pivot", None)
    pivot.empty_display_type = 'ARROWS'
    pivot.empty_display_size = 0.03
    bpy.context.collection.objects.link(pivot)
    pivot.parent = root_obj
    pivot.location = (0.0, 0.120, 0.0)

    # Default resting downward pitch: -16 degrees
    pivot.rotation_euler.x = math.radians(-16.0)

    pivot["limit_rot_x_min"] = -45.0
    pivot["limit_rot_x_max"] = 45.0

    rot_limit = pivot.constraints.new(type='LIMIT_ROTATION')
    rot_limit.use_limit_x = True
    rot_limit.min_x = math.radians(-45.0)
    rot_limit.max_x = math.radians(45.0)
    rot_limit.use_limit_y = True
    rot_limit.min_y = 0.0
    rot_limit.max_y = 0.0
    rot_limit.use_limit_z = True
    rot_limit.min_z = 0.0
    rot_limit.max_z = 0.0
    rot_limit.owner_space = 'LOCAL'

    # 3. Mount_Bracket (Child of Bracket_Pivot)
    bracket_mesh = bpy.data.meshes.new("Mount_Bracket_Mesh")
    build_mount_bracket_mesh(bracket_mesh, materials)
    bracket_obj = bpy.data.objects.new("Mount_Bracket", bracket_mesh)
    bpy.context.collection.objects.link(bracket_obj)
    bracket_obj.parent = pivot
    bracket_obj.location = (0.0, 0.0, 0.0)

    # 4. Camera_Housing (Child of Bracket_Pivot)
    housing_mesh = bpy.data.meshes.new("Camera_Housing_Mesh")
    build_camera_housing_mesh(housing_mesh, materials)
    housing_obj = bpy.data.objects.new("Camera_Housing", housing_mesh)
    bpy.context.collection.objects.link(housing_obj)
    housing_obj.parent = pivot
    housing_obj.location = (0.0, 0.0, 0.0)

    # 5. Lens_Barrel (Child of Camera_Housing)
    lens_barrel_mesh = bpy.data.meshes.new("Lens_Barrel_Mesh")
    build_lens_barrel_mesh(lens_barrel_mesh, materials)
    lens_barrel_obj = bpy.data.objects.new("Lens_Barrel", lens_barrel_mesh)
    bpy.context.collection.objects.link(lens_barrel_obj)
    lens_barrel_obj.parent = housing_obj
    lens_barrel_obj.location = (0.0, 0.100, 0.052)

    # 6. Lens_Glass (Child of Lens_Barrel)
    lens_glass_mesh = bpy.data.meshes.new("Lens_Glass_Mesh")
    build_lens_glass_mesh(lens_glass_mesh, materials)
    lens_glass_obj = bpy.data.objects.new("Lens_Glass", lens_glass_mesh)
    bpy.context.collection.objects.link(lens_glass_obj)
    lens_glass_obj.parent = lens_barrel_obj
    lens_glass_obj.location = (0.0, 0.044, 0.0)

    for obj in [root_obj, bracket_obj, housing_obj, lens_barrel_obj, lens_glass_obj]:
        mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        mod.keep_sharp = True

    bpy.context.view_layer.update()

    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, bracket_obj, housing_obj, lens_barrel_obj, lens_glass_obj]:
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
    if total_tris > 450:
        raise ValueError(f"Triangle count {total_tris} exceeds limit of 450 tris!")

    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root_obj, pivot, bracket_obj, housing_obj, lens_barrel_obj, lens_glass_obj]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    fbx_path = os.path.join(exports_dir, "SEC_Camera_Box_Wall.fbx")

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

    blend_path = os.path.join(exports_dir, "SEC_Camera_Box_Wall.blend")
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
        "asset_name": "SEC_Camera_Box_Wall",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "tris_count": total_tris,
        "mesh_count": 5,
        "empty_count": 1,
        "materials": ["M_Security_Atlas", "M_Lens_Glass", "M_Metal"]
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
        "SEC_Camera_Box_Wall",
        "Bracket_Pivot",
        "Mount_Bracket",
        "Camera_Housing",
        "Lens_Barrel",
        "Lens_Glass"
    ]
    for name in expected_objects:
        if name not in imported_names:
            raise AssertionError(f"Expected object '{name}' was not found in imported FBX!")

    root_obj = bpy.data.objects["SEC_Camera_Box_Wall"]
    pivot = bpy.data.objects["Bracket_Pivot"]
    bracket_obj = bpy.data.objects["Mount_Bracket"]
    housing_obj = bpy.data.objects["Camera_Housing"]
    lens_barrel_obj = bpy.data.objects["Lens_Barrel"]
    lens_glass_obj = bpy.data.objects["Lens_Glass"]

    if pivot.parent != root_obj:
        raise AssertionError("Bracket_Pivot is not parented to SEC_Camera_Box_Wall!")
    if bracket_obj.parent != pivot:
        raise AssertionError("Mount_Bracket is not parented to Bracket_Pivot!")
    if housing_obj.parent != pivot:
        raise AssertionError("Camera_Housing is not parented to Bracket_Pivot!")
    if lens_barrel_obj.parent != housing_obj:
        raise AssertionError("Lens_Barrel is not parented to Camera_Housing!")
    if lens_glass_obj.parent != lens_barrel_obj:
        raise AssertionError("Lens_Glass is not parented to Lens_Barrel!")
    print("[VERIFY] Full parent-child hierarchy verified.")

    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, bracket_obj, housing_obj, lens_barrel_obj, lens_glass_obj]:
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
    if total_tris > 450:
        raise AssertionError(f"Verified triangle count {total_tris} exceeds limit 450!")

    expected_materials = ["M_Security_Atlas", "M_Lens_Glass", "M_Metal"]
    for obj in [root_obj, bracket_obj, housing_obj, lens_barrel_obj, lens_glass_obj]:
        slot_names = [slot.name for slot in obj.material_slots]
        print(f"[VERIFY] Object '{obj.name}' material slots: {slot_names}")
        if not slot_names:
            raise AssertionError(f"Object '{obj.name}' has no material slots!")
        for exp in expected_materials:
            if not any(exp in s for s in slot_names):
                raise AssertionError(f"Object '{obj.name}' is missing expected material {exp}!")

    for obj in [root_obj, bracket_obj, housing_obj, lens_barrel_obj, lens_glass_obj]:
        if not obj.data.uv_layers:
            raise AssertionError(f"Object '{obj.name}' has no UV layers!")
        print(f"[VERIFY] Object '{obj.name}' has UV layer: {obj.data.uv_layers.active.name}")

    bpy.context.view_layer.update()
    initial_glass_loc = lens_glass_obj.matrix_world.translation.copy()
    initial_housing_rot_x = housing_obj.matrix_world.to_euler().x

    pivot.rotation_euler.x += math.radians(-20.0)
    bpy.context.view_layer.update()

    rotated_glass_loc = lens_glass_obj.matrix_world.translation.copy()
    rotated_housing_rot_x = housing_obj.matrix_world.to_euler().x
    diff_tilt_glass = (rotated_glass_loc - initial_glass_loc).length
    diff_tilt_rot = abs(rotated_housing_rot_x - initial_housing_rot_x)

    if diff_tilt_glass < 0.005 and diff_tilt_rot < 0.1:
        raise AssertionError("Rotating Bracket_Pivot did not tilt Lens_Glass or Camera_Housing!")
    print(f"[VERIFY] Tilt rotation verified (lens delta: {diff_tilt_glass:.4f}m, rot delta: {math.degrees(diff_tilt_rot):.1f} deg).")

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
        "asset_name": "SEC_Camera_Box_Wall",
        "fbx_path": os.path.join("exports", "SEC_Camera_Box_Wall.fbx"),
        "tris_count": 0,
        "mesh_count": 0,
        "empty_count": 0,
        "materials": ["M_Security_Atlas", "M_Lens_Glass", "M_Metal"]
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
