"""
SEC_Biometric_Fingerprint_Reader Asset Generator
Automated production script for Blender 5.2 LTS.
Asset 10 in Security & CCTV Asset Pack.

Hierarchy:
SEC_Biometric_Fingerprint_Reader (Root Empty at 0, 0, 0)
    ├── Mount_Plate (Mesh, child of Root)
    └── Main_Housing (Mesh, child of Root)
            ├── Display (Mesh, child of Main_Housing)
            ├── Status_LED (Mesh, child of Main_Housing)
            └── Fingerprint_Sensor (Mesh, child of Main_Housing, origin at its geometric center)

Materials:
    Slot 0: M_Security_Atlas
    Slot 1: M_Screen
    Slot 2: M_Emission

Budget: <= 350 tris. Target: ~280-320 tris with ultra-smooth clean quad bevels.
"""

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import os
import sys
import json
import math


def setup_scene():
    """Reset to clean metric scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'


def create_security_atlas_texture():
    """
    Generate high-fidelity 512x512 texture atlas:
    Quadrant 0 (Top-Left, X: 0..256, Y: 256..512):
        Authentic optical sapphire biometric fingerprint sensor with dermatoglyphic ridge whorls,
        cyan luminescence, and active emerald laser scan line.
    Quadrant 1 (Top-Right, X: 256..512, Y: 256..512):
        Dark obsidian titanium housing with clean metal & security screw detail.
    Quadrant 2 (Bottom-Left, X: 0..256, Y: 0..256):
        Backplate industrial spec label & Wiegand/RS485 wiring pinout.
    Quadrant 3 (Bottom-Right, X: 256..512, Y: 0..256):
        Top: High-Tech Cyber OLED UI graphics.
        Bottom: Vivid Emissive LED light blade glow.
    """
    img_name = "T_Security_Atlas"
    atlas_img = bpy.data.images.get(img_name)
    if atlas_img:
        bpy.data.images.remove(atlas_img)

    width, height = 512, 512
    atlas_img = bpy.data.images.new(img_name, width=width, height=height, alpha=True)
    pixels = [0.0] * (width * height * 4)

    for y in range(height):
        for x in range(width):
            idx = (y * width + x) * 4
            if y >= 256:
                if x < 256:
                    # -------------------------------------------------------------
                    # Quadrant 0: Biometric Optical Sensor (X: 0..256, Y: 256..512)
                    # Center at X = 128, Y = 384
                    # -------------------------------------------------------------
                    dx_f = x - 128
                    dy_f = y - 384
                    dist_f = math.sqrt(dx_f**2 + dy_f**2)

                    # Sapphire glass background
                    r = max(0.04, 0.08 - dist_f * 0.0003)
                    g = max(0.08, 0.13 - dist_f * 0.0003)
                    b = max(0.14, 0.22 - dist_f * 0.0003)

                    # Rounded Sensor Glass Rim (Width 104, Height 140)
                    bx0, bx1 = 76, 180
                    by0, by1 = 314, 454
                    cr = 16
                    if bx0 <= x <= bx1 and by0 <= y <= by1:
                        px_c = bx0 + cr if x < bx0 + cr else (bx1 - cr if x > bx1 - cr else x)
                        py_c = by0 + cr if y < by0 + cr else (by1 - cr if y > by1 - cr else y)
                        dist_edge = math.sqrt((x - px_c)**2 + (y - py_c)**2)
                        if dist_edge <= cr:
                            # Glass base
                            r, g, b = 0.05, 0.10, 0.18
                            if cr - 2.5 <= dist_edge <= cr:
                                r, g, b = 0.25, 0.80, 0.98  # Cyan illuminated rim
                            elif cr - 4.5 <= dist_edge < cr - 2.5:
                                r, g, b = 0.12, 0.35, 0.50

                            # Dermatoglyphic Ridge Flow (Whorl Pattern)
                            xf = (x - 128) * 1.08
                            yf = (y - 374) * 1.38
                            r_d = math.sqrt(xf**2 + yf**2)
                            ang_d = math.atan2(yf, xf)

                            phase = r_d - 7.5 * math.sin(ang_d * 0.9)
                            if 6 <= r_d <= 52:
                                ridge = math.sin(phase * 0.72)
                                if ridge > 0.28:
                                    intensity = (ridge - 0.28) / 0.72
                                    r = max(r, 0.08 + 0.12 * intensity)
                                    g = max(g, 0.35 + 0.55 * intensity)
                                    b = max(b, 0.60 + 0.40 * intensity)

                            # Active Laser Sweep Line at Y = 396
                            if abs(y - 396) <= 1:
                                r, g, b = 0.20, 1.00, 0.65  # Emerald core
                            elif abs(y - 396) <= 3:
                                r = max(r, 0.10)
                                g = max(g, 0.70)
                                b = max(b, 0.50)

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # -------------------------------------------------------------
                    # Quadrant 1: Dark Obsidian Metal (X: 256..512, Y: 256..512)
                    # -------------------------------------------------------------
                    r, g, b = 0.12, 0.13, 0.15
                    if x % 6 in [0, 1]:
                        r, g, b = 0.11, 0.12, 0.14
                    if (x - 256) in [0, 1, 254, 255] or (y - 256) in [0, 1, 254, 255]:
                        r, g, b = 0.28, 0.32, 0.38

                    # Torx Screw Detail at (X=448, Y=304)
                    dist_screw = math.sqrt((x - 448)**2 + (y - 304)**2)
                    if dist_screw <= 18:
                        if 14 <= dist_screw <= 18:
                            r, g, b = 0.24, 0.26, 0.30
                        elif 10 <= dist_screw < 14:
                            r, g, b = 0.70, 0.75, 0.82
                        elif dist_screw < 10:
                            ang = (math.atan2(y - 304, x - 448) + math.pi) % (math.pi / 3) - (math.pi / 6)
                            star_r = 7.0 * (1.0 - 0.25 * math.sin(ang * 3)**2)
                            if dist_screw <= star_r:
                                r, g, b = 0.05, 0.05, 0.06
                                if dist_screw <= 2.2:
                                    r, g, b = 0.35, 0.40, 0.48
                            else:
                                r, g, b = 0.45, 0.50, 0.58

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

            else:
                if x < 256:
                    # -------------------------------------------------------------
                    # Quadrant 2: Backplate Specification Label & Pinout (X: 0..256, Y: 0..256)
                    # -------------------------------------------------------------
                    r, g, b = 0.82, 0.84, 0.88
                    if (y in [30, 80, 135, 190, 240]) or (x in [30, 85, 140, 195, 240]):
                        r, g, b = 0.16, 0.18, 0.22
                    # Title banner
                    if 200 <= y <= 230 and 40 <= x <= 220:
                        r, g, b = 0.12, 0.15, 0.20
                        if 210 <= y <= 220 and (x % 5 in [0, 1, 2]):
                            r, g, b = 0.92, 0.94, 0.98
                    # Wiring terminal blocks
                    if 50 <= y <= 160 and 45 <= x <= 215:
                        wire_row = int((y - 50) / 18)
                        if wire_row == 0:   # RED (+12V DC)
                            r, g, b = 0.85, 0.15, 0.15
                        elif wire_row == 1: # BLK (GND)
                            r, g, b = 0.15, 0.15, 0.15
                        elif wire_row == 2: # GRN (DATA 0)
                            r, g, b = 0.15, 0.80, 0.25
                        elif wire_row == 3: # WHT (DATA 1)
                            r, g, b = 0.95, 0.95, 0.95
                        elif wire_row == 4: # BLU (RS485 A+)
                            r, g, b = 0.20, 0.45, 0.85
                        elif wire_row == 5: # YEL (RS485 B-)
                            r, g, b = 0.85, 0.75, 0.15

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # -------------------------------------------------------------
                    # Quadrant 3: OLED Screen UI (Top) & Emissive LED Blade (Bottom)
                    # (X: 256..512, Y: 0..256)
                    # -------------------------------------------------------------
                    if y >= 120:
                        # Top Section: OLED Screen UI Graphics (X: 272..496, Y: 128..248)
                        dx_s = x - 384
                        dy_s = y - 188
                        if abs(dx_s) <= 96 and abs(dy_s) <= 56:
                            # OLED deep blue background
                            r, g, b = 0.04, 0.06, 0.10
                            if abs(dx_s) in [95, 96] or abs(dy_s) in [55, 56]:
                                r, g, b = 0.22, 0.40, 0.60

                            # 1. Header: Red Lock Icon + System Locked Text
                            if 36 <= dy_s <= 46 and abs(dx_s) <= 86:
                                if dy_s in [36, 46] or abs(dx_s) == 86:
                                    r, g, b = 0.15, 0.30, 0.50
                                # Lock icon
                                if -80 <= dx_s <= -66 and 38 <= dy_s <= 44:
                                    r, g, b = 0.95, 0.25, 0.30
                                # Header text bars
                                if -55 <= dx_s <= 75 and 39 <= dy_s <= 43 and (dx_s % 4 in [0, 1]):
                                    r, g, b = 0.25, 0.85, 1.00

                            # 2. Central Biometric Shield & Targeting Reticle
                            ds_x = abs(dx_s)
                            ds_y = dy_s - 5
                            # Corner brackets
                            if 20 <= ds_x <= 28 and -22 <= ds_y <= 18:
                                if (ds_x == 28 and (ds_y >= 12 or ds_y <= -16)) or ((ds_y == 18 or ds_y == -22) and ds_x >= 22):
                                    r, g, b = 0.25, 0.85, 1.00

                            # Biometric shield
                            if ds_x <= 16 and -16 <= ds_y <= 16:
                                if (ds_x == 16 and ds_y <= 8) or (ds_y == 16 and ds_x <= 10) or (ds_x + ds_y == 24 and ds_x > 10):
                                    r, g, b = 0.30, 0.85, 1.00
                                for loop_rad in [6, 11]:
                                    if abs(math.sqrt(ds_x**2 + (max(0, ds_y))**2) - loop_rad) <= 1.2:
                                        r, g, b = 0.15, 0.95, 0.55
                                if ds_x <= 1.5 and -8 <= ds_y <= 4:
                                    r, g, b = 0.15, 0.95, 0.55

                            # 3. Bottom Action Banner: "SCAN FINGER"
                            if -46 <= dy_s <= -34 and abs(dx_s) <= 86:
                                if dy_s in [-46, -34] or abs(dx_s) == 86:
                                    r, g, b = 0.12, 0.25, 0.40
                                # Emerald status dot
                                if -78 <= dx_s <= -70 and -42 <= dy_s <= -38:
                                    r, g, b = 0.20, 1.00, 0.65
                                # Text
                                if -60 <= dx_s <= 75 and -42 <= dy_s <= -38 and (dx_s % 3 in [0, 1]):
                                    r, g, b = 0.20, 0.90, 0.70
                        else:
                            r, g, b = 0.10, 0.12, 0.15

                    else:
                        # Bottom Section: Emissive LED Light Blade Gradient (Y: 0..119)
                        dx_led = abs(x - 384)
                        dy_led = abs(y - 60)
                        if dx_led <= 110 and dy_led <= 35:
                            if dy_led <= 10 and dx_led <= 85:
                                r, g, b = 0.95, 1.00, 0.98  # Hot white core
                            elif dy_led <= 20:
                                r, g, b = 0.15, 0.95, 0.65  # Glowing emerald/cyan
                            else:
                                r, g, b = 0.05, 0.55, 0.35
                        else:
                            r, g, b = 0.12, 0.14, 0.18

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
        print(f"[WARN] Could not save texture image to disk: {e}")

    return atlas_img


def create_materials(atlas_img):
    """Create standard 3 materials: M_Security_Atlas, M_Screen, M_Emission."""
    materials = {}

    mat_configs = [
        ("M_Security_Atlas", 0.0, 0.35, 0.85, (0.12, 0.13, 0.15, 1.0)),
        ("M_Screen",         2.2, 0.05, 0.00, (0.05, 0.10, 0.20, 1.0)),
        ("M_Emission",       4.5, 0.20, 0.00, (0.20, 1.00, 0.65, 1.0))
    ]

    for name, emiss_str, rough, metal, view_col in mat_configs:
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new(type='ShaderNodeOutputMaterial')
        out_node.location = (300, 0)
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 0)
        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.location = (-300, 0)
        tex_node.image = atlas_img
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])

        if emiss_str > 0.0:
            links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
            bsdf.inputs['Emission Strength'].default_value = emiss_str

        bsdf.inputs['Roughness'].default_value = rough
        bsdf.inputs['Metallic'].default_value = metal
        mat.diffuse_color = view_col
        materials[name] = mat

    return materials


def attach_standard_materials(mesh, materials):
    """Attach the 3 standard materials in strict order [M_Security_Atlas, M_Screen, M_Emission]."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Screen"])          # Slot 1
    mesh.materials.append(materials["M_Emission"])        # Slot 2


def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    """Map face planar projections to a rectangular UV sub-region [u0, v0, u1, v1]."""
    face.normal_update()
    u0, v0, u1, v1 = uv_rect
    uv_lay = bm.loops.layers.uv.verify()

    coords_2d = []
    normal = face.normal
    nx, ny, nz = abs(normal.x), abs(normal.y), abs(normal.z)

    if (ny >= nx and ny >= nz) or (nx < 1e-4 and ny < 1e-4 and nz < 1e-4):
        for loop in face.loops:
            coords_2d.append((loop.vert.co.x, loop.vert.co.z))
    elif nx >= ny and nx >= nz:
        for loop in face.loops:
            coords_2d.append((loop.vert.co.y, loop.vert.co.z))
    else:
        for loop in face.loops:
            coords_2d.append((loop.vert.co.x, loop.vert.co.y))

    min_x = min(c[0] for c in coords_2d)
    max_x = max(c[0] for c in coords_2d)
    min_y = min(c[1] for c in coords_2d)
    max_y = max(c[1] for c in coords_2d)
    span_x = max_x - min_x if max_x > min_x else 1.0
    span_y = max_y - min_y if max_y > min_y else 1.0

    for i, loop in enumerate(face.loops):
        cx, cy = coords_2d[i]
        factor_u = (cx - min_x) / span_x
        factor_v = (cy - min_y) / span_y
        if flip_u:
            factor_u = 1.0 - factor_u
        if flip_v:
            factor_v = 1.0 - factor_v
        u = u0 + factor_u * (u1 - u0)
        v = v0 + factor_v * (v1 - v0)
        loop[uv_lay].uv = (u, v)


def mark_sharp_edges_by_angle(bm, threshold_deg=35.0):
    """Mark edges sharp if face angle exceeds threshold for clean hard-surface normals."""
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


# Constant UV coordinates
UV_DARK_METAL  = (0.580, 0.650, 0.820, 0.880)
UV_BACK_LABEL  = (0.050, 0.050, 0.450, 0.450)
UV_FINGERPRINT = (0.1500, 0.6150, 0.3500, 0.8850)
UV_OLED_SCREEN = (0.5350, 0.2520, 0.9650, 0.4820)
UV_EMISS_BLADE = (0.5350, 0.0480, 0.9650, 0.1850)


# -------------------------------------------------------------
# Clean Quad Topology Mesh Builders (~280-320 tris budget)
# -------------------------------------------------------------

def build_mount_plate_mesh(mesh, materials):
    """
    Build Mount_Plate:
    Flush with wall at Y = 0 (Y: 0.000 to 0.003m).
    Dimensions: Width 52mm, Height 144mm.
    12-sided perimeter with smooth beveled corners.
    Tris count: ~44 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.026, 0.072
    c1, c2 = 0.0035, 0.0065

    pts = [
        (sx - c2, sz), (-sx + c2, sz),
        (-sx + c1, sz - c1), (-sx, sz - c2),
        (-sx, -sz + c2), (-sx + c1, -sz + c1),
        (-sx + c2, -sz), (sx - c2, -sz),
        (sx - c1, -sz + c1), (sx, -sz + c2),
        (sx, sz - c2), (sx - c1, sz - c1)
    ]
    n_pts = len(pts)

    v_back = [bm.verts.new(Vector((x, 0.000, z))) for x, z in pts]
    v_front = [bm.verts.new(Vector((x, 0.003, z))) for x, z in pts]

    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_BACK_LABEL)

    f_front = bm.faces.new(v_front)
    f_front.material_index = 0
    set_face_uv_rect(bm, f_front, UV_DARK_METAL)

    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_back[i], v_front[i], v_front[ni], v_back[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_main_housing_mesh(mesh, materials):
    """
    Build Main_Housing:
    Origin at (0.0, 0.003, 0.0).
    Clean quad-based cross-sectional slices with smooth rounded chamfers.
    No non-planar n-gons. Beautiful bevel highlights.
    Tris count: ~150-180 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # Half-width and chamfer parameters
    sx = 0.0240      # 48mm total width
    cx1 = 0.0022     # 2-segment chamfer offset 1
    cx2 = 0.0042     # 2-segment chamfer offset 2
    y_back = 0.0000  # relative to housing origin (world Y = 0.003)

    # Display window cavity bounds (Z: 0.015 to 0.047, X: -0.017 to +0.017)
    dw_x = 0.0170
    y_disp_rec = 0.0165

    # Fingerprint ramp sensor cavity bounds (Z: -0.033 to -0.005, X: -0.012 to +0.012)
    sw_x = 0.0120

    # Cross-sectional slices along Z: (z, y_front)
    slices = [
        (-0.0700, 0.0170),  # Slice 0: Bottom Chin
        (-0.0520, 0.0225),  # Slice 1: Lower Chin Transition
        (-0.0330, 0.0285),  # Slice 2: Sensor Well Bottom / Ramp Incline
        (-0.0050, 0.0235),  # Slice 3: Sensor Well Top / Ramp Shoulder
        ( 0.0060, 0.0210),  # Slice 4: Ramp Bridge / Display Bottom
        ( 0.0150, 0.0205),  # Slice 5: Display Lower Margin
        ( 0.0470, 0.0205),  # Slice 6: Display Upper Margin
        ( 0.0540, 0.0220),  # Slice 7: Status LED Slot
        ( 0.0700, 0.0240),  # Slice 8: Top Visor Canopy
    ]

    # For each slice, construct ring of 8 vertices:
    # 0: back-left (-sx, y_back)
    # 1: flank-left (-sx, y_f - cx2)
    # 2: chamfer-left (-sx + cx1, y_f - cx1)
    # 3: front-left (-sx + cx2, y_f)
    # 4: front-right (sx - cx2, y_f)
    # 5: chamfer-right (sx - cx1, y_f - cx1)
    # 6: flank-right (sx, y_f - cx2)
    # 7: back-right (sx, y_back)
    rings = []
    for z, yf in slices:
        v0 = bm.verts.new(Vector((-sx,        y_back,     z)))
        v1 = bm.verts.new(Vector((-sx,        yf - cx2,   z)))
        v2 = bm.verts.new(Vector((-sx + cx1,  yf - cx1,   z)))
        v3 = bm.verts.new(Vector((-sx + cx2,  yf,         z)))
        v4 = bm.verts.new(Vector(( sx - cx2,  yf,         z)))
        v5 = bm.verts.new(Vector(( sx - cx1,  yf - cx1,   z)))
        v6 = bm.verts.new(Vector(( sx,        yf - cx2,   z)))
        v7 = bm.verts.new(Vector(( sx,        y_back,     z)))
        rings.append((v0, v1, v2, v3, v4, v5, v6, v7))

    n_slices = len(slices)

    # Connect side flanks, chamfers, and back with clean quads
    for i in range(n_slices - 1):
        rA = rings[i]
        rB = rings[i + 1]

        # Back quad
        fb = bm.faces.new([rA[7], rA[0], rB[0], rB[7]])
        fb.material_index = 0; set_face_uv_rect(bm, fb, UV_DARK_METAL)

        # Left side flank
        fsl = bm.faces.new([rA[0], rA[1], rB[1], rB[0]])
        fsl.material_index = 0; set_face_uv_rect(bm, fsl, UV_DARK_METAL)

        # Left chamfer 1
        fc1l = bm.faces.new([rA[1], rA[2], rB[2], rB[1]])
        fc1l.material_index = 0; set_face_uv_rect(bm, fc1l, UV_DARK_METAL)

        # Left chamfer 2
        fc2l = bm.faces.new([rA[2], rA[3], rB[3], rB[2]])
        fc2l.material_index = 0; set_face_uv_rect(bm, fc2l, UV_DARK_METAL)

        # Right chamfer 2
        fc2r = bm.faces.new([rA[4], rA[5], rB[5], rB[4]])
        fc2r.material_index = 0; set_face_uv_rect(bm, fc2r, UV_DARK_METAL)

        # Right chamfer 1
        fc1r = bm.faces.new([rA[5], rA[6], rB[6], rB[5]])
        fc1r.material_index = 0; set_face_uv_rect(bm, fc1r, UV_DARK_METAL)

        # Right side flank
        fsr = bm.faces.new([rA[6], rA[7], rB[7], rB[6]])
        fsr.material_index = 0; set_face_uv_rect(bm, fsr, UV_DARK_METAL)

    # --- Front Face Sections ---
    # Section 0..1: Chin front panel
    f_ch0 = bm.faces.new([rings[0][3], rings[0][4], rings[1][4], rings[1][3]])
    f_ch0.material_index = 0; set_face_uv_rect(bm, f_ch0, UV_DARK_METAL, flip_u=True)

    # Section 1..2: Lower ramp transition
    f_ch1 = bm.faces.new([rings[1][3], rings[1][4], rings[2][4], rings[2][3]])
    f_ch1.material_index = 0; set_face_uv_rect(bm, f_ch1, UV_DARK_METAL, flip_u=True)

    # Section 2..3: Sensor Ramp Area (Z: -0.033 to -0.005)
    # Subdivide into Left flank, Recessed sensor well, Right flank
    r2 = rings[2]
    r3 = rings[3]
    # Front-left/right ramp margins
    v2_sl = bm.verts.new(Vector((-sw_x, r2[3].co.y, r2[3].co.z)))
    v2_sr = bm.verts.new(Vector(( sw_x, r2[4].co.y, r2[4].co.z)))
    v3_sl = bm.verts.new(Vector((-sw_x, r3[3].co.y, r3[3].co.z)))
    v3_sr = bm.verts.new(Vector(( sw_x, r3[4].co.y, r3[4].co.z)))

    f_s_ml = bm.faces.new([r2[3], v2_sl, v3_sl, r3[3]])
    f_s_ml.material_index = 0; set_face_uv_rect(bm, f_s_ml, UV_DARK_METAL)

    f_s_mr = bm.faces.new([v2_sr, r2[4], r3[4], v3_sr])
    f_s_mr.material_index = 0; set_face_uv_rect(bm, f_s_mr, UV_DARK_METAL)

    # Recessed sensor well bed (recessed 3.5mm)
    y_rec_s2 = r2[3].co.y - 0.0040
    y_rec_s3 = r3[3].co.y - 0.0035
    v2_s_rec_l = bm.verts.new(Vector((-sw_x, y_rec_s2, r2[3].co.z)))
    v2_s_rec_r = bm.verts.new(Vector(( sw_x, y_rec_s2, r2[4].co.z)))
    v3_s_rec_l = bm.verts.new(Vector((-sw_x, y_rec_s3, r3[3].co.z)))
    v3_s_rec_r = bm.verts.new(Vector(( sw_x, y_rec_s3, r3[4].co.z)))

    f_sw_b = bm.faces.new([v2_sl, v2_sr, v2_s_rec_r, v2_s_rec_l]); f_sw_b.material_index = 0; set_face_uv_rect(bm, f_sw_b, UV_DARK_METAL)
    f_sw_t = bm.faces.new([v3_s_rec_l, v3_s_rec_r, v3_sr, v3_sl]); f_sw_t.material_index = 0; set_face_uv_rect(bm, f_sw_t, UV_DARK_METAL)
    f_sw_floor = bm.faces.new([v2_s_rec_l, v2_s_rec_r, v3_s_rec_r, v3_s_rec_l]); f_sw_floor.material_index = 0; set_face_uv_rect(bm, f_sw_floor, UV_DARK_METAL, flip_u=True)

    # Section 3..4: Ramp shoulder bridge
    f_sh = bm.faces.new([rings[3][3], rings[3][4], rings[4][4], rings[4][3]])
    f_sh.material_index = 0; set_face_uv_rect(bm, f_sh, UV_DARK_METAL, flip_u=True)

    # Section 4..5: Display lower margin
    f_dl = bm.faces.new([rings[4][3], rings[4][4], rings[5][4], rings[5][3]])
    f_dl.material_index = 0; set_face_uv_rect(bm, f_dl, UV_DARK_METAL, flip_u=True)

    # Section 5..6: Display Cavity Area (Z: 0.015 to 0.047)
    r5 = rings[5]
    r6 = rings[6]
    v5_dl = bm.verts.new(Vector((-dw_x, r5[3].co.y, r5[3].co.z)))
    v5_dr = bm.verts.new(Vector(( dw_x, r5[4].co.y, r5[4].co.z)))
    v6_dl = bm.verts.new(Vector((-dw_x, r6[3].co.y, r6[3].co.z)))
    v6_dr = bm.verts.new(Vector(( dw_x, r6[4].co.y, r6[4].co.z)))

    f_d_ml = bm.faces.new([r5[3], v5_dl, v6_dl, r6[3]])
    f_d_ml.material_index = 0; set_face_uv_rect(bm, f_d_ml, UV_DARK_METAL)

    f_d_mr = bm.faces.new([v5_dr, r5[4], r6[4], v6_dr])
    f_d_mr.material_index = 0; set_face_uv_rect(bm, f_d_mr, UV_DARK_METAL)

    # Recessed display well floor (recessed 3.5mm to Y=0.0165)
    v5_d_rec_l = bm.verts.new(Vector((-dw_x, y_disp_rec, r5[3].co.z)))
    v5_d_rec_r = bm.verts.new(Vector(( dw_x, y_disp_rec, r5[4].co.z)))
    v6_d_rec_l = bm.verts.new(Vector((-dw_x, y_disp_rec, r6[3].co.z)))
    v6_d_rec_r = bm.verts.new(Vector(( dw_x, y_disp_rec, r6[4].co.z)))

    f_dw_b = bm.faces.new([v5_dl, v5_dr, v5_d_rec_r, v5_d_rec_l]); f_dw_b.material_index = 0; set_face_uv_rect(bm, f_dw_b, UV_DARK_METAL)
    f_dw_t = bm.faces.new([v6_d_rec_l, v6_d_rec_r, v6_dr, v6_dl]); f_dw_t.material_index = 0; set_face_uv_rect(bm, f_dw_t, UV_DARK_METAL)
    f_dw_floor = bm.faces.new([v5_d_rec_l, v5_d_rec_r, v6_d_rec_r, v6_d_rec_l]); f_dw_floor.material_index = 0; set_face_uv_rect(bm, f_dw_floor, UV_DARK_METAL, flip_u=True)

    # Section 6..7: Forehead panel below LED
    f_fh = bm.faces.new([rings[6][3], rings[6][4], rings[7][4], rings[7][3]])
    f_fh.material_index = 0; set_face_uv_rect(bm, f_fh, UV_DARK_METAL, flip_u=True)

    # Section 7..8: Top Visor Hood
    f_vhd = bm.faces.new([rings[7][3], rings[7][4], rings[8][4], rings[8][3]])
    f_vhd.material_index = 0; set_face_uv_rect(bm, f_vhd, UV_DARK_METAL, flip_u=True)

    # Top Cap (Slice 8)
    r8 = rings[8]
    f_top = bm.faces.new([r8[0], r8[7], r8[6], r8[5], r8[4], r8[3], r8[2], r8[1]])
    f_top.material_index = 0; set_face_uv_rect(bm, f_top, UV_DARK_METAL)

    # Bottom Cap (Slice 0)
    r0 = rings[0]
    f_bot = bm.faces.new([r0[0], r0[1], r0[2], r0[3], r0[4], r0[5], r0[6], r0[7]])
    f_bot.material_index = 0; set_face_uv_rect(bm, f_bot, UV_DARK_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_display_mesh(mesh, materials):
    """
    Build Display:
    Origin at (0.0, 0.0175, 0.031) relative to Main_Housing.
    High-contrast OLED screen panel with beveled bezel.
    Tris count: ~28 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.0160, 0.0120
    cb = 0.0018
    y_b, y_f = -0.0010, 0.0030

    pts_b = [
        (-sx, sz), (sx, sz), (sx, -sz), (-sx, -sz)
    ]
    pts_f = [
        (-sx + cb, sz - cb), (sx - cb, sz - cb),
        (sx - cb, -sz + cb), (-sx + cb, -sz + cb)
    ]

    v_b = [bm.verts.new(Vector((x, y_b, z))) for x, z in pts_b]
    v_f = [bm.verts.new(Vector((x, y_f, z))) for x, z in pts_f]

    # Front active screen face
    f_front = bm.faces.new(v_f)
    f_front.material_index = 1  # M_Screen
    set_face_uv_rect(bm, f_front, UV_OLED_SCREEN, flip_u=True)

    # Bezel collar quads
    for i in range(4):
        ni = (i + 1) % 4
        f_bez = bm.faces.new([v_b[i], v_b[ni], v_f[ni], v_f[i]])
        f_bez.material_index = 0  # M_Security_Atlas
        set_face_uv_rect(bm, f_bez, UV_DARK_METAL)

    # Back face
    f_back = bm.faces.new(list(reversed(v_b)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_DARK_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_status_led_mesh(mesh, materials):
    """
    Build Status_LED:
    Origin at (0.0, 0.0215, 0.054) relative to Main_Housing.
    Horizontal indicator light blade nestled beneath visor canopy.
    Tris count: ~20 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx_b, sz_b = 0.0150, 0.0022
    sx_t, sz_t = 0.0140, 0.0018
    y_b, y_t = 0.0000, 0.0025

    v_b = [
        bm.verts.new(Vector((-sx_b, y_b,  sz_b))),
        bm.verts.new(Vector(( sx_b, y_b,  sz_b))),
        bm.verts.new(Vector(( sx_b, y_b, -sz_b))),
        bm.verts.new(Vector((-sx_b, y_b, -sz_b)))
    ]
    v_t = [
        bm.verts.new(Vector((-sx_t, y_t,  sz_t))),
        bm.verts.new(Vector(( sx_t, y_t,  sz_t))),
        bm.verts.new(Vector(( sx_t, y_t, -sz_t))),
        bm.verts.new(Vector((-sx_t, y_t, -sz_t)))
    ]

    f_front = bm.faces.new(v_t)
    f_front.material_index = 2  # M_Emission
    set_face_uv_rect(bm, f_front, UV_EMISS_BLADE, flip_u=True)

    f_back = bm.faces.new(list(reversed(v_b)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_DARK_METAL)

    for i in range(4):
        ni = (i + 1) % 4
        f = bm.faces.new([v_b[i], v_t[i], v_t[ni], v_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_fingerprint_sensor_mesh(mesh, materials):
    """
    Build Fingerprint_Sensor:
    "Sensör plakası ayrı mesh ve kendi merkezinde origin kullansın."
    Origin is at its exact geometric center (0, 0, 0).
    Octagonal beveled optical sapphire prism with metallic collar.
    Tris count: ~44 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx_b, sz_b = 0.0105, 0.0135
    cb1, cb2 = 0.0020, 0.0035

    sx_t, sz_t = 0.0095, 0.0125
    ct1, ct2 = 0.0018, 0.0030

    y_b, y_t = -0.00175, 0.00175

    pts_b = [
        (sx_b - cb2, sz_b), (-sx_b + cb2, sz_b),
        (-sx_b + cb1, sz_b - cb1), (-sx_b, sz_b - cb2),
        (-sx_b, -sz_b + cb2), (-sx_b + cb1, -sz_b + cb1),
        (-sx_b + cb2, -sz_b), (sx_b - cb2, -sz_b),
        (sx_b - cb1, -sz_b + cb1), (sx_b, -sz_b + cb2),
        (sx_b, sz_b - cb2), (sx_b - cb1, sz_b - cb1)
    ]
    pts_t = [
        (sx_t - ct2, sz_t), (-sx_t + ct2, sz_t),
        (-sx_t + ct1, sz_t - ct1), (-sx_t, sz_t - ct2),
        (-sx_t, -sz_t + ct2), (-sx_t + ct1, -sz_t + ct1),
        (-sx_t + ct2, -sz_t), (sx_t - ct2, -sz_t),
        (sx_t - ct1, -sz_t + ct1), (sx_t, -sz_t + ct2),
        (sx_t, sz_t - ct2), (sx_t - ct1, sz_t - ct1)
    ]

    n_p = len(pts_b)
    v_b = [bm.verts.new(Vector((x, y_b, z))) for x, z in pts_b]
    v_t = [bm.verts.new(Vector((x, y_t, z))) for x, z in pts_t]

    f_front = bm.faces.new(v_t)
    f_front.material_index = 0
    set_face_uv_rect(bm, f_front, UV_FINGERPRINT, flip_u=True)

    f_back = bm.faces.new(list(reversed(v_b)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_DARK_METAL)

    for i in range(n_p):
        ni = (i + 1) % n_p
        f = bm.faces.new([v_b[i], v_t[i], v_t[ni], v_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Scene Assembly & Hierarchy
# -------------------------------------------------------------

def assemble_asset(materials):
    """
    Assemble the complete asset hierarchy:
    SEC_Biometric_Fingerprint_Reader (Root Empty at 0, 0, 0)
        ├── Mount_Plate (Mesh, child of Root)
        └── Main_Housing (Mesh, child of Root)
                ├── Display (Mesh, child of Main_Housing)
                ├── Status_LED (Mesh, child of Main_Housing)
                └── Fingerprint_Sensor (Mesh, child of Main_Housing, origin at its geometric center)
    """
    # 1. Root Empty
    root_obj = bpy.data.objects.new("SEC_Biometric_Fingerprint_Reader", None)
    root_obj.empty_display_type = 'PLAIN_AXES'
    root_obj.empty_display_size = 0.05
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.collection.objects.link(root_obj)

    # 2. Mount_Plate (child of Root)
    mesh_plate = bpy.data.meshes.new("Mount_Plate")
    build_mount_plate_mesh(mesh_plate, materials)
    obj_plate = bpy.data.objects.new("Mount_Plate", mesh_plate)
    obj_plate.location = Vector((0.0, 0.0, 0.0))
    obj_plate.parent = root_obj
    bpy.context.scene.collection.objects.link(obj_plate)

    # 3. Main_Housing (child of Root)
    mesh_housing = bpy.data.meshes.new("Main_Housing")
    build_main_housing_mesh(mesh_housing, materials)
    obj_housing = bpy.data.objects.new("Main_Housing", mesh_housing)
    obj_housing.location = Vector((0.0, 0.003, 0.0))
    obj_housing.parent = root_obj
    bpy.context.scene.collection.objects.link(obj_housing)

    # 4. Display (child of Main_Housing)
    mesh_display = bpy.data.meshes.new("Display")
    build_display_mesh(mesh_display, materials)
    obj_display = bpy.data.objects.new("Display", mesh_display)
    obj_display.location = Vector((0.0, 0.0175, 0.031))
    obj_display.parent = obj_housing
    bpy.context.scene.collection.objects.link(obj_display)

    # 5. Status_LED (child of Main_Housing)
    mesh_led = bpy.data.meshes.new("Status_LED")
    build_status_led_mesh(mesh_led, materials)
    obj_led = bpy.data.objects.new("Status_LED", mesh_led)
    obj_led.location = Vector((0.0, 0.0215, 0.054))
    obj_led.parent = obj_housing
    bpy.context.scene.collection.objects.link(obj_led)

    # 6. Fingerprint_Sensor (child of Main_Housing)
    # Origin at its exact geometric center (0, 0, 0)
    # Angled matching the finger rest ramp (~ -10 deg pitch)
    mesh_sensor = bpy.data.meshes.new("Fingerprint_Sensor")
    build_fingerprint_sensor_mesh(mesh_sensor, materials)
    obj_sensor = bpy.data.objects.new("Fingerprint_Sensor", mesh_sensor)
    obj_sensor.location = Vector((0.0, 0.0245, -0.019))
    obj_sensor.rotation_euler = Euler((math.radians(-10.0), 0.0, 0.0), 'XYZ')
    obj_sensor.parent = obj_housing
    bpy.context.scene.collection.objects.link(obj_sensor)

    # Count initial triangles across all meshes
    bpy.context.view_layer.update()
    all_mesh_objs = [obj_plate, obj_housing, obj_display, obj_led, obj_sensor]
    total_tris = 0
    for obj in all_mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        tris = len(bm.faces)
        total_tris += tris
        bm.free()
        print(f"  Object '{obj.name}': {tris} tris")

    print(f"[INFO] Initial Triangulated Triangle Count: {total_tris}")
    assert total_tris <= 350, f"Triangle budget exceeded! {total_tris} > 350 tris"

    return root_obj, all_mesh_objs, total_tris


def export_and_verify(root_obj, mesh_objs, initial_tris):
    """Export FBX and verify all constraints."""
    exports_dir = os.path.abspath("exports")
    os.makedirs(exports_dir, exist_ok=True)

    fbx_path = os.path.join(exports_dir, "SEC_Biometric_Fingerprint_Reader.fbx")
    blend_path = os.path.join(exports_dir, "SEC_Biometric_Fingerprint_Reader.blend")

    # Select all objects for export
    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    for obj in mesh_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    # Export FBX
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        bake_space_transform=False,
        object_types={'EMPTY', 'MESH'},
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f"[INFO] Exported FBX to: {fbx_path}")

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Saved blend file to: {blend_path}")

    # Clean up temporary .blend1 file
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        try:
            os.remove(blend1_path)
            print(f"[INFO] Cleaned up temporary backup file: {blend1_path}")
        except Exception as e:
            print(f"[WARN] Failed to remove backup file: {e}")

    # QA Verification
    print(f"\n[VERIFY] Re-importing FBX from: {fbx_path}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    imported_objs = {obj.name: obj for obj in bpy.context.scene.objects}
    print(f"[VERIFY] Imported objects count: {len(imported_objs)}")

    # 1. Check Root
    assert "SEC_Biometric_Fingerprint_Reader" in imported_objs, "Root object missing in FBX!"
    v_root = imported_objs["SEC_Biometric_Fingerprint_Reader"]

    # 2. Check Hierarchy
    expected_children = ["Mount_Plate", "Main_Housing"]
    for c_name in expected_children:
        assert c_name in imported_objs, f"Child object '{c_name}' missing!"
        child_obj = imported_objs[c_name]
        assert child_obj.parent == v_root, f"Object '{c_name}' not parented to Root!"

    housing_children = ["Display", "Status_LED", "Fingerprint_Sensor"]
    v_housing = imported_objs["Main_Housing"]
    for hc_name in housing_children:
        assert hc_name in imported_objs, f"Housing child '{hc_name}' missing!"
        hchild = imported_objs[hc_name]
        assert hchild.parent == v_housing, f"Object '{hc_name}' not parented to Main_Housing!"

    print("[VERIFY] Full parent-child hierarchy verified successfully.")

    # 3. Check Verified Triangle Count
    verified_tris = 0
    for name, obj in imported_objs.items():
        if obj.type == 'MESH':
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            t = len(bm.faces)
            verified_tris += t
            bm.free()

    print(f"[VERIFY] Total verified triangulated triangles: {verified_tris}")
    assert verified_tris <= 350, f"Verified triangle count {verified_tris} exceeds budget 350!"

    # 4. Check Materials & UVs
    for name in ["Mount_Plate", "Main_Housing", "Display", "Status_LED", "Fingerprint_Sensor"]:
        m_obj = imported_objs[name]
        assert len(m_obj.material_slots) >= 1, f"Mesh {name} has no materials!"
        assert len(m_obj.data.uv_layers) >= 1, f"Mesh {name} has no UV layer!"

    print("[VERIFY] Material slots and UV layers verified across all meshes.")
    print("[VERIFY] ALL QA CHECKS PASSED SUCCESSFULLY.")

    # Update manifest
    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    manifest["SEC_Biometric_Fingerprint_Reader"] = {
        "asset_name": "SEC_Biometric_Fingerprint_Reader",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "triangle_count": verified_tris,
        "mesh_count": 5,
        "empty_count": 1,
        "materials": ["M_Security_Atlas", "M_Screen", "M_Emission"],
        "status": "SUCCESS"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    print(f"[INFO] Manifest updated: {manifest_path}")

    return verified_tris


def main():
    print("==========================================")
    print("  SEC_Biometric_Fingerprint_Reader Generator")
    print("==========================================")

    setup_scene()
    atlas_img = create_security_atlas_texture()
    materials = create_materials(atlas_img)
    root_obj, mesh_objs, initial_tris = assemble_asset(materials)
    verified_tris = export_and_verify(root_obj, mesh_objs, initial_tris)

    print("\n==========================================")
    print(f"  PROCESS COMPLETED SUCCESSFULLY [SUCCESS]")
    print(f"  Final Verified Tris: {verified_tris} / 350")
    print("==========================================")


if __name__ == "__main__":
    main()
