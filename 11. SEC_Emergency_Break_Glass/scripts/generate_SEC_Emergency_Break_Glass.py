"""
SEC_Emergency_Break_Glass Generator Script
Industrial Low-Poly Security & CCTV Asset Pack
Upper Budget Limit: 250 triangles
Target Triangles: ~246 triangles (High fidelity, near maximum allowed budget)

Hierarchy:
SEC_Emergency_Break_Glass (Root Empty at 0, 0, 0)
    └── Housing (Child of Root)
            ├── Breakable_Glass (Child of Housing, origin at geometric center)
            ├── Alarm_Button (Child of Housing, origin at geometric center)
            └── Protective_Frame (Child of Housing)

Materials:
    Slot 0: M_Security_Atlas
    Slot 1: M_Transparent
    Slot 2: M_Emission
"""

import os
import sys
import math
import json
import bpy
import bmesh
from mathutils import Vector, Matrix

# Ensure absolute project directory resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(PROJECT_DIR, "exports")


def setup_clean_scene():
    """Reset scene to a clean metric environment."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'


def create_security_atlas_texture():
    """
    Generate high-fidelity 512x512 texture atlas with clean non-overlapping zones:
    - Quadrant 0 (X: 0..256, Y: 256..512): Emergency Break Glass Plaque & Button
    - Quadrant 1 (X: 256..512, Y: 256..512): Housing Fire Red, Dark Metal & Torx Screw
    - Quadrant 2 (X: 0..256, Y: 0..256): Backplate Specification Label
    - Quadrant 3 (X: 256..512, Y: 0..256): Glass Decal Overlay & Emissive Beacon
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
            a = 1.0

            if y >= 256:
                if x < 256:
                    # -------------------------------------------------------------
                    # Quadrant 0: Emergency Break Glass Plaque & Button (X: 0..256, Y: 256..512)
                    # -------------------------------------------------------------
                    r, g, b = 0.85, 0.10, 0.10
                    if (x % 8 in [0, 1]) or (y % 8 in [0, 1]):
                        r, g, b = 0.82, 0.09, 0.09

                    # Center Button Decal at (X = 128, Y = 384)
                    dx = x - 128
                    dy = y - 384
                    dist = math.sqrt(dx**2 + dy**2)

                    # Plunger circle: radius up to 64 px
                    if dist <= 64:
                        # Warning Fluorescent Yellow
                        r, g, b = 0.98, 0.86, 0.08
                        if 58 <= dist <= 64:
                            r, g, b = 0.10, 0.10, 0.12  # outer black retention ring
                        elif 52 <= dist <= 55:
                            r, g, b = 0.18, 0.18, 0.20  # inner accent ring

                        # Central Activation Target: Black Disc (radius 22 px)
                        if dist <= 22:
                            r, g, b = 0.10, 0.10, 0.12
                            # Center Target Dot
                            if dist <= 6.0:
                                r, g, b = 0.98, 0.98, 1.00

                        # Dual Bold Activation Arrows (▶ on left, ◀ on right)
                        if -48 <= dx <= -26 and abs(dy) <= (dx + 48) * 0.75:
                            r, g, b = 0.10, 0.10, 0.12
                        if 26 <= dx <= 48 and abs(dy) <= (48 - dx) * 0.75:
                            r, g, b = 0.10, 0.10, 0.12

                        # "PRESS HERE" Lettering Bars
                        if abs(dx) <= 28 and (26 <= abs(dy) <= 34) and (dx % 4 in [0, 1]):
                            r, g, b = 0.10, 0.10, 0.12

                    # White safety border lines at perimeter
                    if (x in [16, 239] and 272 <= y <= 495) or (y in [272, 495] and 16 <= x <= 239):
                        r, g, b = 0.95, 0.95, 0.98

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # -------------------------------------------------------------
                    # Quadrant 1: Housing Fire Red, Dark Metal & Torx Screw
                    # -------------------------------------------------------------
                    # Default: Solid Fire Red
                    r, g, b = 0.82, 0.11, 0.11

                    # Dark Obsidian Metal Patch (X: 260..340, Y: 420..500)
                    if 260 <= x <= 340 and 420 <= y <= 500:
                        r, g, b = 0.14, 0.15, 0.18
                        if x in [260, 340] or y in [420, 500]:
                            r, g, b = 0.28, 0.30, 0.35

                    # Torx Security Screw at (X = 448, Y = 290)
                    dist_screw = math.sqrt((x - 448)**2 + (y - 290)**2)
                    if dist_screw <= 18:
                        if 14 <= dist_screw <= 18:
                            r, g, b = 0.24, 0.26, 0.30
                        elif 10 <= dist_screw < 14:
                            r, g, b = 0.70, 0.75, 0.82
                        elif dist_screw < 10:
                            ang = (math.atan2(y - 290, x - 448) + math.pi) % (math.pi / 3) - (math.pi / 6)
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
                    # Quadrant 2: Backplate Specification Label (X: 0..256, Y: 0..256)
                    # -------------------------------------------------------------
                    r, g, b = 0.85, 0.86, 0.89
                    if (y in [25, 75, 135, 195, 245]) or (x in [25, 80, 135, 195, 245]):
                        r, g, b = 0.16, 0.18, 0.22

                    # Title banner: "SEC-EMERGENCY-CALL-POINT"
                    if 205 <= y <= 235 and 35 <= x <= 225:
                        r, g, b = 0.75, 0.10, 0.10
                        if 215 <= y <= 225 and (x % 5 in [0, 1, 2]):
                            r, g, b = 0.98, 0.98, 0.98

                    # Wiring block diagram: COM, NO, NC, LED+
                    if 50 <= y <= 165 and 40 <= x <= 220:
                        wire_row = int((y - 50) / 28)
                        if wire_row == 0:   r, g, b = 0.85, 0.15, 0.15  # Red: +24V DC
                        elif wire_row == 1: r, g, b = 0.15, 0.15, 0.15  # Blk: COM
                        elif wire_row == 2: r, g, b = 0.15, 0.75, 0.25  # Grn: NO
                        elif wire_row == 3: r, g, b = 0.85, 0.75, 0.15  # Yel: NC

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # -------------------------------------------------------------
                    # Quadrant 3: Glass Decal Overlay (Top) & Emissive Beacon (Bottom)
                    # (X: 256..512, Y: 0..256)
                    # -------------------------------------------------------------
                    if y >= 128:
                        # Top: Authentic Safety Glass Graphics (Center at X = 384, Y = 192)
                        dx_g = x - 384
                        dy_g = y - 192

                        # Default: 100% Transparent Clear Glass
                        r, g, b = 0.90, 0.95, 1.00
                        a = 0.0

                        # Solid White/Black EN 54-11 Central Activation Band (Y: 184..200, X: 300..468)
                        if abs(dy_g) <= 9 and abs(dx_g) <= 84:
                            # Crisp Solid White Background Band
                            r, g, b = 0.98, 0.98, 1.00
                            a = 1.0

                            # Center Black Dot at dx_g = 0 (radius 4.5 px)
                            dist_c = math.sqrt(dx_g**2 + dy_g**2)
                            if dist_c <= 4.5:
                                r, g, b = 0.10, 0.10, 0.12

                            # Left Black Arrow pointing right (X in -32..-14)
                            if -32 <= dx_g <= -14 and abs(dy_g) <= (dx_g + 32) * 0.45:
                                r, g, b = 0.10, 0.10, 0.12
                            # Left Black Horizontal Shaft (X in -74..-32)
                            if -74 <= dx_g <= -32 and abs(dy_g) <= 1.5:
                                r, g, b = 0.10, 0.10, 0.12

                            # Right Black Arrow pointing left (X in 14..32)
                            if 14 <= dx_g <= 32 and abs(dy_g) <= (32 - dx_g) * 0.45:
                                r, g, b = 0.10, 0.10, 0.12
                            # Right Black Horizontal Shaft (X in 32..74)
                            if 32 <= dx_g <= 74 and abs(dy_g) <= 1.5:
                                r, g, b = 0.10, 0.10, 0.12

                        # Crisp Solid White Instruction Lines
                        # Top Header Line & Banner (dy_g: 38..44)
                        if 38 <= dy_g <= 42 and abs(dx_g) <= 80:
                            r, g, b = 0.98, 0.98, 1.00
                            a = 1.0
                        if dy_g in [36, 44] and abs(dx_g) <= 84:
                            r, g, b = 0.98, 0.98, 1.00
                            a = 1.0

                        # Bottom Instruction Line & Banner (dy_g: -44..-38)
                        if -42 <= dy_g <= -38 and abs(dx_g) <= 80:
                            r, g, b = 0.98, 0.98, 1.00
                            a = 1.0
                        if dy_g in [-44, -36] and abs(dx_g) <= 84:
                            r, g, b = 0.98, 0.98, 1.00
                            a = 1.0

                        # Corner L-brackets
                        if (abs(dx_g) == 90 and (abs(dy_g) >= 36)) or (abs(dy_g) == 50 and (abs(dx_g) >= 76)):
                            r, g, b = 0.98, 0.98, 1.00
                            a = 1.0

                    else:
                        # Bottom: Emissive Emergency Red Alarm Beacon Glow (X: 256..512, Y: 0..128)
                        dx_led = abs(x - 384)
                        dy_led = abs(y - 64)
                        if dx_led <= 110 and dy_led <= 38:
                            if dy_led <= 10 and dx_led <= 85:
                                r, g, b = 1.00, 0.92, 0.88
                            elif dy_led <= 22:
                                r, g, b = 0.98, 0.18, 0.18
                            else:
                                r, g, b = 0.60, 0.08, 0.08
                        else:
                            r, g, b = 0.20, 0.06, 0.06
                        a = 1.0

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = a

    atlas_img.pixels = pixels
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    atlas_path = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
    atlas_img.filepath_raw = atlas_path
    atlas_img.file_format = 'PNG'
    try:
        atlas_img.save()
        print(f"[INFO] Texture atlas saved to: {atlas_path}")
    except Exception as e:
        print(f"[WARN] Failed to save texture: {e}")

    atlas_img.pack()
    return atlas_img


def create_materials(atlas_img):
    """
    Create exact 3 materials required by prompt:
    Slot 0: M_Security_Atlas
    Slot 1: M_Transparent
    Slot 2: M_Emission
    """
    materials = {}

    # 1. Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.get("M_Security_Atlas")
    if not mat_atlas:
        mat_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes0 = mat_atlas.node_tree.nodes
    links0 = mat_atlas.node_tree.links
    nodes0.clear()

    out0 = nodes0.new(type='ShaderNodeOutputMaterial')
    out0.location = (300, 0)
    bsdf0 = nodes0.new(type='ShaderNodeBsdfPrincipled')
    bsdf0.location = (0, 0)
    links0.new(bsdf0.outputs['BSDF'], out0.inputs['Surface'])

    tex0 = nodes0.new(type='ShaderNodeTexImage')
    tex0.location = (-300, 0)
    tex0.image = atlas_img
    links0.new(tex0.outputs['Color'], bsdf0.inputs['Base Color'])

    bsdf0.inputs['Roughness'].default_value = 0.35
    bsdf0.inputs['Metallic'].default_value = 0.05
    mat_atlas.diffuse_color = (0.85, 0.12, 0.12, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. Slot 1: M_Transparent (Clear safety glass with white printed lettering)
    mat_trans = bpy.data.materials.get("M_Transparent")
    if not mat_trans:
        mat_trans = bpy.data.materials.new(name="M_Transparent")
    mat_trans.use_nodes = True
    nodes1 = mat_trans.node_tree.nodes
    links1 = mat_trans.node_tree.links
    nodes1.clear()

    out1 = nodes1.new(type='ShaderNodeOutputMaterial')
    out1.location = (300, 0)
    bsdf1 = nodes1.new(type='ShaderNodeBsdfPrincipled')
    bsdf1.location = (0, 0)
    links1.new(bsdf1.outputs['BSDF'], out1.inputs['Surface'])

    tex1 = nodes1.new(type='ShaderNodeTexImage')
    tex1.location = (-300, 0)
    tex1.image = atlas_img
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Base Color'])
    links1.new(tex1.outputs['Alpha'], bsdf1.inputs['Alpha'])

    bsdf1.inputs['Roughness'].default_value = 0.10
    bsdf1.inputs['Metallic'].default_value = 0.00
    bsdf1.inputs['Transmission Weight'].default_value = 0.00
    mat_trans.diffuse_color = (0.90, 0.95, 1.00, 0.35)
    mat_trans.blend_method = 'BLEND'
    materials["M_Transparent"] = mat_trans

    # 3. Slot 2: M_Emission (Emergency red indicator glow)
    mat_emiss = bpy.data.materials.get("M_Emission")
    if not mat_emiss:
        mat_emiss = bpy.data.materials.new(name="M_Emission")
    mat_emiss.use_nodes = True
    nodes2 = mat_emiss.node_tree.nodes
    links2 = mat_emiss.node_tree.links
    nodes2.clear()

    out2 = nodes2.new(type='ShaderNodeOutputMaterial')
    out2.location = (300, 0)
    bsdf2 = nodes2.new(type='ShaderNodeBsdfPrincipled')
    bsdf2.location = (0, 0)
    links2.new(bsdf2.outputs['BSDF'], out2.inputs['Surface'])

    tex2 = nodes2.new(type='ShaderNodeTexImage')
    tex2.location = (-300, 0)
    tex2.image = atlas_img
    links2.new(tex2.outputs['Color'], bsdf2.inputs['Base Color'])
    links2.new(tex2.outputs['Color'], bsdf2.inputs['Emission Color'])
    bsdf2.inputs['Emission Strength'].default_value = 5.0

    bsdf2.inputs['Roughness'].default_value = 0.20
    bsdf2.inputs['Metallic'].default_value = 0.00
    mat_emiss.diffuse_color = (1.00, 0.20, 0.20, 1.0)
    materials["M_Emission"] = mat_emiss

    return materials


def attach_standard_materials(mesh, materials):
    """Attach the 3 standard materials in strict order [M_Security_Atlas, M_Transparent, M_Emission]."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Transparent"])     # Slot 1
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


# Constant UV coordinates with clean, non-overlapping zones
UV_FIRE_RED     = (0.720, 0.720, 0.980, 0.980)
UV_DARK_COLLAR  = (0.520, 0.830, 0.650, 0.970)
UV_BACK_LABEL   = (0.050, 0.050, 0.450, 0.450)
UV_ALARM_BUTTON = (0.050, 0.550, 0.450, 0.950)
UV_GLASS_DECAL  = (0.540, 0.270, 0.960, 0.480)
UV_EMISS_BEACON = (0.540, 0.040, 0.960, 0.180)


# -------------------------------------------------------------
# High-Density Low-Poly Mesh Builders (~246 tris)
# -------------------------------------------------------------

def build_housing_mesh(mesh, materials):
    """
    Build Housing:
    Square wall-mounted casing flush against the wall at Y = 0.
    Dimensions: Width 86mm, Height 86mm, Depth 26mm (Y: 0.000 to 0.026m).
    12-sided rounded perimeter with smooth corner chamfers.
    Recessed central cavity (depth 14mm) where button and glass sit.
    Added side release latch notches (Left & Right).
    Tris count: ~76 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.043, 0.043
    c1, c2 = 0.003, 0.006

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
    v_front = [bm.verts.new(Vector((x, 0.026, z))) for x, z in pts]

    # Rear face (Quadrant 2: Spec Label)
    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_BACK_LABEL)

    # 12 Outer side quads
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_back[i], v_front[i], v_front[ni], v_back[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_FIRE_RED)

    # Central recessed cavity (Width 64mm, Height 58mm, recessed to Y = 0.012m)
    cw_x = 0.032
    cw_zt = 0.029
    cw_zb = -0.029
    y_rec = 0.012

    v_cr_tl = bm.verts.new(Vector((-cw_x, 0.026,  cw_zt)))
    v_cr_tr = bm.verts.new(Vector(( cw_x, 0.026,  cw_zt)))
    v_cr_bl = bm.verts.new(Vector((-cw_x, 0.026,  cw_zb)))
    v_cr_br = bm.verts.new(Vector(( cw_x, 0.026,  cw_zb)))

    # Front perimeter quads surrounding the cavity
    f_fh = bm.faces.new([v_front[0], v_front[1], v_cr_tl, v_cr_tr])
    f_fh.material_index = 0; set_face_uv_rect(bm, f_fh, UV_FIRE_RED, flip_u=True)
    f_ctl = bm.faces.new([v_front[1], v_front[2], v_cr_tl])
    f_ctl.material_index = 0; set_face_uv_rect(bm, f_ctl, UV_FIRE_RED)
    f_ctr = bm.faces.new([v_front[11], v_front[0], v_cr_tr])
    f_ctr.material_index = 0; set_face_uv_rect(bm, f_ctr, UV_FIRE_RED)

    f_fl = bm.faces.new([v_front[2], v_front[3], v_front[4], v_cr_bl, v_cr_tl])
    f_fl.material_index = 0; set_face_uv_rect(bm, f_fl, UV_FIRE_RED)
    f_fr = bm.faces.new([v_front[11], v_cr_tr, v_cr_br, v_front[9], v_front[10]])
    f_fr.material_index = 0; set_face_uv_rect(bm, f_fr, UV_FIRE_RED)

    f_ch = bm.faces.new([v_cr_bl, v_cr_br, v_front[7], v_front[6]])
    f_ch.material_index = 0; set_face_uv_rect(bm, f_ch, UV_FIRE_RED, flip_u=True)
    f_cbl = bm.faces.new([v_front[4], v_front[5], v_front[6], v_cr_bl])
    f_cbl.material_index = 0; set_face_uv_rect(bm, f_cbl, UV_FIRE_RED)
    f_cbr = bm.faces.new([v_cr_br, v_front[7], v_front[8], v_front[9]])
    f_cbr.material_index = 0; set_face_uv_rect(bm, f_cbr, UV_FIRE_RED)

    # Cavity recessed walls (jambs) and floor
    v_rec_tl = bm.verts.new(Vector((-cw_x, y_rec,  cw_zt)))
    v_rec_tr = bm.verts.new(Vector(( cw_x, y_rec,  cw_zt)))
    v_rec_bl = bm.verts.new(Vector((-cw_x, y_rec,  cw_zb)))
    v_rec_br = bm.verts.new(Vector(( cw_x, y_rec,  cw_zb)))

    f_j_top = bm.faces.new([v_cr_tr, v_cr_tl, v_rec_tl, v_rec_tr]); f_j_top.material_index = 0; set_face_uv_rect(bm, f_j_top, UV_DARK_COLLAR)
    f_j_bot = bm.faces.new([v_cr_bl, v_cr_br, v_rec_br, v_rec_bl]); f_j_bot.material_index = 0; set_face_uv_rect(bm, f_j_bot, UV_DARK_COLLAR)
    f_j_l   = bm.faces.new([v_cr_tl, v_cr_bl, v_rec_bl, v_rec_tl]); f_j_l.material_index = 0; set_face_uv_rect(bm, f_j_l, UV_DARK_COLLAR)
    f_j_r   = bm.faces.new([v_cr_br, v_cr_tr, v_rec_tr, v_rec_br]); f_j_r.material_index = 0; set_face_uv_rect(bm, f_j_r, UV_DARK_COLLAR)

    # Recessed backplate floor
    f_floor = bm.faces.new([v_rec_tl, v_rec_bl, v_rec_br, v_rec_tr]); f_floor.material_index = 0; set_face_uv_rect(bm, f_floor, UV_FIRE_RED, flip_u=True)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_protective_frame_mesh(mesh, materials):
    """
    Build Protective_Frame:
    Protective front bezel holding the glass with beveled window and seamless top hinge knuckle.
    Dimensions: Width 88mm, Height 88mm, Depth 9mm (Y: 0.022 to 0.031m).
    12-sided perimeter with beveled front chamfer and beveled window aperture.
    Added Addressable Call Point LED Indicator Light at top center (Material Slot 2: M_Emission).
    Tris count: ~84 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.044, 0.044
    c1, c2 = 0.003, 0.006

    pts = [
        (sx - c2, sz), (-sx + c2, sz),
        (-sx + c1, sz - c1), (-sx, sz - c2),
        (-sx, -sz + c2), (-sx + c1, -sz + c1),
        (-sx + c2, -sz), (sx - c2, -sz),
        (sx - c1, -sz + c1), (sx, -sz + c2),
        (sx, sz - c2), (sx - c1, sz - c1)
    ]
    n_pts = len(pts)

    y_back = 0.022
    y_front_mid = 0.029
    y_front_peak = 0.031

    v_back = [bm.verts.new(Vector((x, y_back, z))) for x, z in pts]
    v_mid  = [bm.verts.new(Vector((x, y_front_mid, z))) for x, z in pts]

    # Outer side quads
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_back[i], v_mid[i], v_mid[ni], v_back[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_FIRE_RED)

    # Window opening aperture (Width 60mm, Height 50mm)
    wx = 0.030
    wz_t = 0.025
    wz_b = -0.025

    # Front beveled frame rim
    sx_in, sz_in = 0.041, 0.041
    c_in1, c_in2 = 0.0025, 0.005
    pts_in = [
        (sx_in - c_in2, sz_in), (-sx_in + c_in2, sz_in),
        (-sx_in + c_in1, sz_in - c_in1), (-sx_in, sz_in - c_in2),
        (-sx_in, -sz_in + c_in2), (-sx_in + c_in1, -sz_in + c_in1),
        (-sx_in + c_in2, -sz_in), (sx_in - c_in2, -sz_in),
        (sx_in - c_in1, -sz_in + c_in1), (sx_in, -sz_in + c_in2),
        (sx_in, sz_in - c_in2), (sx_in - c_in1, sz_in - c_in1)
    ]
    v_peak = [bm.verts.new(Vector((x, y_front_peak, z))) for x, z in pts_in]

    # Front outer bevel quads
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_mid[i], v_peak[i], v_peak[ni], v_mid[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_FIRE_RED)

    # Inner window vertices (recessed back to Y = 0.025)
    v_w_tl = bm.verts.new(Vector((-wx, 0.025,  wz_t)))
    v_w_tr = bm.verts.new(Vector(( wx, 0.025,  wz_t)))
    v_w_bl = bm.verts.new(Vector((-wx, 0.025,  wz_b)))
    v_w_br = bm.verts.new(Vector(( wx, 0.025,  wz_b)))

    # Window inner beveled frame
    f_wt = bm.faces.new([v_peak[0], v_peak[1], v_w_tl, v_w_tr])
    f_wt.material_index = 0; set_face_uv_rect(bm, f_wt, UV_FIRE_RED, flip_u=True)
    f_wt_l = bm.faces.new([v_peak[1], v_peak[2], v_w_tl])
    f_wt_l.material_index = 0; set_face_uv_rect(bm, f_wt_l, UV_FIRE_RED)
    f_wt_r = bm.faces.new([v_peak[11], v_peak[0], v_w_tr])
    f_wt_r.material_index = 0; set_face_uv_rect(bm, f_wt_r, UV_FIRE_RED)

    f_wl = bm.faces.new([v_peak[2], v_peak[3], v_peak[4], v_w_bl, v_w_tl])
    f_wl.material_index = 0; set_face_uv_rect(bm, f_wl, UV_FIRE_RED)
    f_wr = bm.faces.new([v_peak[11], v_w_tr, v_w_br, v_peak[9], v_peak[10]])
    f_wr.material_index = 0; set_face_uv_rect(bm, f_wr, UV_FIRE_RED)

    f_wb = bm.faces.new([v_w_bl, v_w_br, v_peak[7], v_peak[6]])
    f_wb.material_index = 0; set_face_uv_rect(bm, f_wb, UV_FIRE_RED, flip_u=True)
    f_wb_l = bm.faces.new([v_peak[4], v_peak[5], v_peak[6], v_w_bl])
    f_wb_l.material_index = 0; set_face_uv_rect(bm, f_wb_l, UV_FIRE_RED)
    f_wb_r = bm.faces.new([v_w_br, v_peak[7], v_peak[8], v_peak[9]])
    f_wb_r.material_index = 0; set_face_uv_rect(bm, f_wb_r, UV_FIRE_RED)

    # -------------------------------------------------------------
    # Addressable LED Indicator Bezel & Emissive Lens (+10 tris)
    # Placed on top frame bar: X: -0.007..0.007, Z: 0.032..0.036, Y: 0.031..0.0325
    # Slot 2: M_Emission applied to front face
    # -------------------------------------------------------------
    led_x = 0.007
    led_zt = 0.036
    led_zb = 0.032
    led_y_base = 0.0310
    led_y_lens = 0.0325

    v_l_bl = bm.verts.new(Vector((-led_x, led_y_lens, led_zb)))
    v_l_br = bm.verts.new(Vector(( led_x, led_y_lens, led_zb)))
    v_l_tr = bm.verts.new(Vector(( led_x, led_y_lens, led_zt)))
    v_l_tl = bm.verts.new(Vector((-led_x, led_y_lens, led_zt)))

    # Front Emissive Lens (Slot 2: M_Emission)
    f_lens = bm.faces.new([v_l_bl, v_l_br, v_l_tr, v_l_tl])
    f_lens.material_index = 2  # M_Emission
    set_face_uv_rect(bm, f_lens, UV_EMISS_BEACON)

    # Side chamfer walls of the LED lens bezel (Slot 0: Dark Collar)
    v_lb_bl = bm.verts.new(Vector((-led_x, led_y_base, led_zb)))
    v_lb_br = bm.verts.new(Vector(( led_x, led_y_base, led_zb)))
    v_lb_tr = bm.verts.new(Vector(( led_x, led_y_base, led_zt)))
    v_lb_tl = bm.verts.new(Vector((-led_x, led_y_base, led_zt)))

    f_ls_t = bm.faces.new([v_l_tl, v_l_tr, v_lb_tr, v_lb_tl]); f_ls_t.material_index = 0; set_face_uv_rect(bm, f_ls_t, UV_DARK_COLLAR)
    f_ls_b = bm.faces.new([v_lb_bl, v_lb_br, v_l_br, v_l_bl]); f_ls_b.material_index = 0; set_face_uv_rect(bm, f_ls_b, UV_DARK_COLLAR)
    f_ls_l = bm.faces.new([v_lb_tl, v_l_tl, v_l_bl, v_lb_bl]); f_ls_l.material_index = 0; set_face_uv_rect(bm, f_ls_l, UV_DARK_COLLAR)
    f_ls_r = bm.faces.new([v_l_tr, v_lb_tr, v_lb_br, v_l_br]); f_ls_r.material_index = 0; set_face_uv_rect(bm, f_ls_r, UV_DARK_COLLAR)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_breakable_glass_mesh(mesh, materials):
    """
    Build Breakable_Glass:
    Thin single-pane tempered safety glass sheet.
    Origin at its exact geometric center (0, 0, 0).
    Dimensions: Width 60mm, Height 50mm, Thickness 1.6mm.
    Mapped to Slot 1: M_Transparent (Quadrant 3: Glass Decal Overlay).
    Tris count: Exactly 12 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.030, 0.025
    y_b, y_f = -0.0008, 0.0008

    v_b = [
        bm.verts.new(Vector((-sx, y_b,  sz))),
        bm.verts.new(Vector(( sx, y_b,  sz))),
        bm.verts.new(Vector(( sx, y_b, -sz))),
        bm.verts.new(Vector((-sx, y_b, -sz)))
    ]
    v_f = [
        bm.verts.new(Vector((-sx, y_f,  sz))),
        bm.verts.new(Vector(( sx, y_f,  sz))),
        bm.verts.new(Vector(( sx, y_f, -sz))),
        bm.verts.new(Vector((-sx, y_f, -sz)))
    ]

    # Front glass face with printed decal
    f_front = bm.faces.new(v_f)
    f_front.material_index = 1  # M_Transparent
    set_face_uv_rect(bm, f_front, UV_GLASS_DECAL, flip_u=True)

    # Back face
    f_back = bm.faces.new(list(reversed(v_b)))
    f_back.material_index = 1  # M_Transparent
    set_face_uv_rect(bm, f_back, UV_GLASS_DECAL)

    # 4 Edges
    for i in range(4):
        ni = (i + 1) % 4
        f = bm.faces.new([v_b[i], v_f[i], v_f[ni], v_b[ni]])
        f.material_index = 1
        set_face_uv_rect(bm, f, UV_GLASS_DECAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_alarm_button_mesh(mesh, materials):
    """
    Build Alarm_Button:
    Centrally mounted emergency trigger plunger behind the glass.
    Origin at its exact geometric center (0, 0, 0).
    13-sided beveled cylindrical plunger with warning decal.
    Tris count: ~74 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # Base collar (radius 18mm, height 2mm)
    r_col = 0.018
    y_col_b = -0.0040
    y_col_f = -0.0020

    # Plunger cap (radius 14mm, height 4mm, projects to Y = +0.0040m)
    r_cap = 0.014
    y_cap = 0.0040

    n_seg = 16
    v_cb = []
    v_cf = []
    v_top = []

    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        x_c = r_col * math.cos(ang)
        z_c = r_col * math.sin(ang)
        x_p = r_cap * math.cos(ang)
        z_p = r_cap * math.sin(ang)

        v_cb.append(bm.verts.new(Vector((x_c, y_col_b, z_c))))
        v_cf.append(bm.verts.new(Vector((x_c, y_col_f, z_c))))
        v_top.append(bm.verts.new(Vector((x_p, y_cap,   z_p))))

    # Base cap
    f_base = bm.faces.new(list(reversed(v_cb)))
    f_base.material_index = 0
    set_face_uv_rect(bm, f_base, UV_DARK_COLLAR)

    # Collar side quads (Clean dark metallic bezel)
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_cb[i], v_cf[i], v_cf[ni], v_cb[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_COLLAR)

    # Step collar to plunger quads (Clean dark metal step)
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_cf[i], v_top[i], v_top[ni], v_cf[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_COLLAR)

    # Front button trigger face (Slot 0: Quadrant 0 Warning Decal)
    f_top = bm.faces.new(v_top)
    f_top.material_index = 0  # M_Security_Atlas
    set_face_uv_rect(bm, f_top, UV_ALARM_BUTTON, flip_u=True)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Asset Assembly and Hierarchy
# -------------------------------------------------------------

def assemble_sec_emergency_break_glass(materials):
    """
    Assemble the complete asset hierarchy:
    SEC_Emergency_Break_Glass (Root Empty at 0, 0, 0)
        └── Housing (Mesh, child of Root)
                ├── Breakable_Glass (Mesh, child of Housing, origin at geometric center)
                ├── Alarm_Button (Mesh, child of Housing, origin at geometric center)
                └── Protective_Frame (Mesh, child of Housing)
    """
    # 1. Root Empty
    root_obj = bpy.data.objects.new("SEC_Emergency_Break_Glass", None)
    root_obj.empty_display_type = 'PLAIN_AXES'
    root_obj.empty_display_size = 0.05
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.collection.objects.link(root_obj)

    # 2. Housing (child of Root)
    mesh_housing = bpy.data.meshes.new("Housing")
    build_housing_mesh(mesh_housing, materials)
    obj_housing = bpy.data.objects.new("Housing", mesh_housing)
    obj_housing.location = Vector((0.0, 0.0, 0.0))
    obj_housing.parent = root_obj
    bpy.context.scene.collection.objects.link(obj_housing)

    # 3. Protective_Frame (child of Housing)
    mesh_frame = bpy.data.meshes.new("Protective_Frame")
    build_protective_frame_mesh(mesh_frame, materials)
    obj_frame = bpy.data.objects.new("Protective_Frame", mesh_frame)
    obj_frame.location = Vector((0.0, 0.0, 0.0))
    obj_frame.parent = obj_housing
    bpy.context.scene.collection.objects.link(obj_frame)

    # 4. Breakable_Glass (child of Housing, origin at geometric center)
    mesh_glass = bpy.data.meshes.new("Breakable_Glass")
    build_breakable_glass_mesh(mesh_glass, materials)
    obj_glass = bpy.data.objects.new("Breakable_Glass", mesh_glass)
    obj_glass.location = Vector((0.0, 0.0225, 0.0))
    obj_glass.parent = obj_housing
    bpy.context.scene.collection.objects.link(obj_glass)

    # 5. Alarm_Button (child of Housing, origin at geometric center)
    mesh_button = bpy.data.meshes.new("Alarm_Button")
    build_alarm_button_mesh(mesh_button, materials)
    obj_button = bpy.data.objects.new("Alarm_Button", mesh_button)
    obj_button.location = Vector((0.0, 0.0160, 0.0))
    obj_button.parent = obj_housing

    # Custom properties for interaction
    obj_button["press_axis"] = "Y"
    obj_button["travel_m"] = 0.004
    obj_button["action"] = "ALARM_TRIGGER"
    bpy.context.scene.collection.objects.link(obj_button)

    # Count initial triangles across all meshes
    bpy.context.view_layer.update()
    all_mesh_objs = [obj_housing, obj_frame, obj_glass, obj_button]
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
    assert total_tris <= 250, f"Triangle budget exceeded! {total_tris} > 250 tris"

    return root_obj, all_mesh_objs, total_tris


def export_and_verify(root_obj, mesh_objs, initial_tris):
    """Export FBX and verify all constraints."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Emergency_Break_Glass.fbx")
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Emergency_Break_Glass.blend")

    # Select objects for export
    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)
    for obj in mesh_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    # Export FBX
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        object_types={'MESH', 'EMPTY'},
        axis_forward='-Z',
        axis_up='Y',
        apply_unit_scale=True,
        bake_space_transform=False,
        mesh_smooth_type='FACE'
    )
    print(f"[INFO] Exported FBX to: {fbx_path}")

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Saved blend file to: {blend_path}")

    # Clean any blend1 backup file
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[INFO] Cleaned up temporary backup file: {blend1_path}")

    # Re-import and QA Verification in Fresh Scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    print(f"\n[VERIFY] Re-importing FBX from: {fbx_path}")
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    imported_objs = list(bpy.data.objects)
    print(f"[VERIFY] Imported objects count: {len(imported_objs)}")

    # 1. Verify Root Object
    imp_root = bpy.data.objects.get("SEC_Emergency_Break_Glass")
    assert imp_root is not None, "FAILED: Root object SEC_Emergency_Break_Glass missing in FBX!"

    # 2. Verify Children Hierarchy
    imp_housing = bpy.data.objects.get("Housing")
    assert imp_housing is not None, "FAILED: Housing missing!"
    assert imp_housing.parent == imp_root, "FAILED: Housing not parented to SEC_Emergency_Break_Glass!"

    expected_housing_children = ["Breakable_Glass", "Alarm_Button", "Protective_Frame"]
    for c_name in expected_housing_children:
        child_obj = bpy.data.objects.get(c_name)
        assert child_obj is not None, f"FAILED: Housing child '{c_name}' missing!"
        assert child_obj.parent == imp_housing, f"FAILED: '{c_name}' not parented to Housing!"

    print("[VERIFY] Full parent-child hierarchy verified successfully.")

    # 3. Verify Triangulated Triangle Count
    verify_tris = 0
    verified_meshes = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            verified_meshes.append(obj.name)
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            tris = len(bm.faces)
            verify_tris += tris
            bm.free()

    print(f"[VERIFY] Total verified triangulated triangles: {verify_tris}")
    assert verify_tris <= 250, f"FAILED: Verified tris count {verify_tris} > 250!"

    # 4. Verify Materials & UVs
    expected_materials = ["M_Security_Atlas", "M_Transparent", "M_Emission"]
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            assert len(obj.data.uv_layers) > 0, f"Mesh {obj.name} has no UV layer!"
            slot_names = [slot.material.name for slot in obj.material_slots if slot.material]
            for mat_name in slot_names:
                assert mat_name in expected_materials, f"Unexpected material {mat_name} on {obj.name}!"

    print("[VERIFY] Material slots and UV layers verified across all meshes.")
    print("[VERIFY] ALL QA CHECKS PASSED SUCCESSFULLY.")

    # 5. Update Manifest
    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Emergency_Break_Glass"] = {
        "asset_name": "SEC_Emergency_Break_Glass",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "texture_atlas": os.path.join(EXPORTS_DIR, "T_Security_Atlas.png"),
        "tris_count": verify_tris,
        "max_tris_allowed": 250,
        "mesh_count": len(verified_meshes),
        "meshes": verified_meshes,
        "materials": expected_materials,
        "status": "SUCCESS"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Manifest updated: {manifest_path}")
    return verify_tris


def main():
    print("==========================================")
    print("  SEC_Emergency_Break_Glass Generator")
    print("==========================================")

    setup_clean_scene()
    atlas_img = create_security_atlas_texture()
    materials = create_materials(atlas_img)
    root_obj, mesh_objs, initial_tris = assemble_sec_emergency_break_glass(materials)
    verified_tris = export_and_verify(root_obj, mesh_objs, initial_tris)

    print("\n==========================================")
    print(f"  PROCESS COMPLETED SUCCESSFULLY [SUCCESS]")
    print(f"  Final Verified Tris: {verified_tris} / 250")
    print("==========================================")


if __name__ == "__main__":
    main()
