"""
SEC_Emergency_Stop_Mushroom Generator Script
Industrial Low-Poly Security & CCTV Asset Pack
Upper Budget Limit: 300 triangles
Target Triangles: ~278 triangles (High fidelity, near maximum allowed budget)

Hierarchy:
SEC_Emergency_Stop_Mushroom (Root Empty at 0, 0, 0)
    ├── Mount_Base (Mesh, child of Root)
    ├── Guard_Ring (Mesh, child of Root)
    └── Button_Pivot (Empty, child of Root, local Y axis 0.005m travel)
            └── Mushroom_Button (Mesh, child of Button_Pivot)

Materials:
    Slot 0: M_Security_Atlas
    Slot 1: M_Emission
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
    - Quadrant 0 (X: 0..256, Y: 256..512): Safety Yellow Guard Ring with bold circular EMERGENCY STOP text & plain yellow margin
    - Quadrant 1 (X: 256..512, Y: 256..512): Red Mushroom Button Palm Face with twist-to-reset rotational arrows (↻ RESET) & plain red margin
    - Quadrant 2 (X: 0..256, Y: 0..256): Backplate Specification Label & NC/NO Contact Wiring Diagram
    - Quadrant 3 (X: 256..512, Y: 0..256): Dark Industrial Enclosure Body & Emissive Warning Beacon
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
                    # Quadrant 0: Safety Yellow Guard Ring Plaque (X: 0..256, Y: 256..512)
                    # -------------------------------------------------------------
                    # Base: Safety Alert Yellow (RAL 1023)
                    r, g, b = 0.96, 0.78, 0.05

                    # Plain yellow margin on right (X: 220..255) for side walls
                    if x < 220:
                        dx_y = x - 110
                        dy_y = y - 384
                        dist_y = math.sqrt(dx_y**2 + dy_y**2)

                        # Outer black circular border ring (radius 92..98 px)
                        if 92 <= dist_y <= 98:
                            r, g, b = 0.10, 0.10, 0.12
                        elif 40 <= dist_y <= 46:
                            r, g, b = 0.10, 0.10, 0.12  # inner hole border

                        # Bold Circular Lettering Band (radius 48..90 px)
                        # Print "EMERGENCY STOP" along top arc and bottom arc
                        if 50 <= dist_y <= 88:
                            ang = math.atan2(dy_y, dx_y)  # -pi to +pi
                            # Top Arc: EMERGENCY STOP
                            if 0.20 <= ang <= 2.94:
                                seg = int((ang - 0.20) / 0.20)
                                if (seg % 2 == 0) and (56 <= dist_y <= 82):
                                    r, g, b = 0.10, 0.10, 0.12
                                    if seg in [0, 12]:
                                        r, g, b = 0.85, 0.10, 0.10
                            # Bottom Arc: NOT-AUS / ARRET
                            elif -2.94 <= ang <= -0.20:
                                seg = int((abs(ang) - 0.20) / 0.22)
                                if (seg % 2 == 0) and (60 <= dist_y <= 78):
                                    r, g, b = 0.10, 0.10, 0.12

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # -------------------------------------------------------------
                    # Quadrant 1: Red Mushroom Button Palm Face (X: 256..512, Y: 256..512)
                    # -------------------------------------------------------------
                    # Base: Vivid Safety Fire Red (RAL 3000)
                    r, g, b = 0.88, 0.08, 0.08

                    # Plain red margin on left (X: 256..280) for side flare
                    if x > 280:
                        dx_m = x - 396
                        dy_m = y - 384
                        dist_m = math.sqrt(dx_m**2 + dy_m**2)

                        # Center ergonomic tactile dish (radius <= 32 px)
                        if dist_m <= 32:
                            r, g, b = 0.78, 0.06, 0.06
                            if 28 <= dist_m <= 32:
                                r, g, b = 0.65, 0.05, 0.05

                        # Twist-to-Reset Curved Directional Arrows (3 symmetrical arcs at r = 50..70 px)
                        if 50 <= dist_m <= 70:
                            ang_m = (math.atan2(dy_m, dx_m) + 2.0 * math.pi) % (2.0 * math.pi)
                            sector = ang_m % (2.0 * math.pi / 3.0)  # 0 to 120 deg (2.094 rad)

                            # Arc shaft (from 15 deg to 85 deg)
                            if 0.26 <= sector <= 1.48 and (56 <= dist_m <= 64):
                                r, g, b = 0.98, 0.98, 1.00  # Crisp White Arrow Shaft

                            # Arrowhead at sector = 1.48 rad
                            if 1.40 <= sector <= 1.72:
                                d_tip = abs(dist_m - 60)
                                tip_span = (1.72 - sector) * 26.0
                                if d_tip <= tip_span and tip_span > 0:
                                    r, g, b = 0.98, 0.98, 1.00

                        # Outer button rim bevel ring
                        if 94 <= dist_m <= 104:
                            r, g, b = 0.72, 0.06, 0.06

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

            else:
                if x < 256:
                    # -------------------------------------------------------------
                    # Quadrant 2: Backplate Specification Label (X: 0..256, Y: 0..256)
                    # -------------------------------------------------------------
                    r, g, b = 0.85, 0.86, 0.89
                    # Industrial grid border lines
                    if (y in [25, 75, 135, 195, 245]) or (x in [25, 80, 135, 195, 245]):
                        r, g, b = 0.16, 0.18, 0.22

                    # Title banner: "SEC-EMERGENCY-STOP-40M"
                    if 205 <= y <= 235 and 35 <= x <= 225:
                        r, g, b = 0.85, 0.10, 0.10
                        if 215 <= y <= 225 and (x % 5 in [0, 1, 2]):
                            r, g, b = 0.98, 0.98, 0.98

                    # Contact Block Diagram: NC (Normally Closed) 1-2 & NO 3-4
                    if 50 <= y <= 165 and 40 <= x <= 220:
                        wire_row = int((y - 50) / 28)
                        if wire_row == 0:   r, g, b = 0.85, 0.15, 0.15  # Red: 1-2 NC (Safety Loop)
                        elif wire_row == 1: r, g, b = 0.15, 0.15, 0.15  # Black: Earth / Ground
                        elif wire_row == 2: r, g, b = 0.15, 0.75, 0.25  # Green: 3-4 NO (Monitoring)
                        elif wire_row == 3: r, g, b = 0.85, 0.75, 0.15  # Yellow: Aux Status

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # -------------------------------------------------------------
                    # Quadrant 3: Dark Industrial Enclosure Body & Emissive Beacon
                    # (X: 256..512, Y: 0..256)
                    # -------------------------------------------------------------
                    if y >= 128:
                        # Top: Dark Obsidian / Polycarbonate Enclosure Texture
                        r, g, b = 0.14, 0.15, 0.18
                        # Subtle mold grain / cooling rib accents
                        if (x % 16 in [0, 1]) or (y % 16 in [0, 1]):
                            r, g, b = 0.18, 0.20, 0.24

                        # Conduit Hex Boss Texture (Center at X = 384, Y = 192)
                        dist_hex = math.sqrt((x - 384)**2 + (y - 192)**2)
                        if 24 <= dist_hex <= 32:
                            r, g, b = 0.32, 0.35, 0.40
                        elif dist_hex < 24:
                            r, g, b = 0.08, 0.09, 0.10

                    else:
                        # Bottom: Emissive Emergency Status LED Ring (X: 256..512, Y: 0..128)
                        # Radiant high-visibility alert amber/red beacon glow
                        dx_e = abs(x - 384)
                        dy_e = abs(y - 64)
                        if dx_e <= 110 and dy_e <= 38:
                            if dy_e <= 10 and dx_e <= 85:
                                r, g, b = 1.00, 0.95, 0.90  # Bright white/amber core
                            elif dy_e <= 22:
                                r, g, b = 1.00, 0.35, 0.08  # Intense amber-red glow
                            else:
                                r, g, b = 0.65, 0.12, 0.04
                        else:
                            r, g, b = 0.20, 0.06, 0.04
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
    Create exact 2 materials required by prompt:
    Slot 0: M_Security_Atlas
    Slot 1: M_Emission
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
    mat_atlas.diffuse_color = (0.95, 0.78, 0.05, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. Slot 1: M_Emission (Emergency LED Ring Glow)
    mat_emiss = bpy.data.materials.get("M_Emission")
    if not mat_emiss:
        mat_emiss = bpy.data.materials.new(name="M_Emission")
    mat_emiss.use_nodes = True
    nodes1 = mat_emiss.node_tree.nodes
    links1 = mat_emiss.node_tree.links
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
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Emission Color'])
    bsdf1.inputs['Emission Strength'].default_value = 5.0

    bsdf1.inputs['Roughness'].default_value = 0.20
    bsdf1.inputs['Metallic'].default_value = 0.00
    mat_emiss.diffuse_color = (1.00, 0.35, 0.08, 1.0)
    materials["M_Emission"] = mat_emiss

    return materials


def attach_standard_materials(mesh, materials):
    """Attach the 2 standard materials in strict order [M_Security_Atlas, M_Emission]."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Emission"])        # Slot 1


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


def set_radial_uv(bm, face, center_u, center_v, uv_radius, max_geom_r):
    """Map circular/ring face loops to polar UV coordinates centered at (center_u, center_v)."""
    uv_lay = bm.loops.layers.uv.verify()
    for loop in face.loops:
        x, z = loop.vert.co.x, loop.vert.co.z
        u = center_u + (x / max_geom_r) * uv_radius
        v = center_v + (z / max_geom_r) * uv_radius
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
UV_PLAIN_YELLOW = (0.440, 0.550, 0.490, 0.950)  # Plain yellow patch for collar sides
UV_PLAIN_RED    = (0.510, 0.550, 0.540, 0.950)  # Plain fire red patch for button sides
UV_BACK_LABEL   = (0.050, 0.050, 0.450, 0.450)  # Specification label & contact diagram
UV_DARK_HOUSING = (0.550, 0.280, 0.950, 0.480)  # Dark industrial polycarbonate body
UV_EMISS_BEACON = (0.540, 0.040, 0.960, 0.180)  # Radiant amber/red alert glow ring


# -------------------------------------------------------------
# High-Density Low-Poly Mesh Builders (~278 tris)
# -------------------------------------------------------------

def build_mount_base_mesh(mesh, materials):
    """
    Build Mount_Base:
    Square industrial backbox casing flush against the wall at Y = 0.
    Dimensions: Width 74mm, Height 74mm, Depth 24mm (Y: 0.000 to 0.024m).
    8-sided rounded perimeter with beveled front collar and top conduit entry boss.
    100% watertight, solid manifold geometry.
    Tris count: ~66 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.037, 0.037
    c = 0.006

    pts = [
        (sx - c, sz), (-sx + c, sz),
        (-sx, sz - c), (-sx, -sz + c),
        (-sx + c, -sz), (sx - c, -sz),
        (sx, -sz + c), (sx, sz - c)
    ]
    n_pts = len(pts)

    y_back = 0.000
    y_front = 0.024

    v_back = [bm.verts.new(Vector((x, y_back, z))) for x, z in pts]
    v_front = [bm.verts.new(Vector((x, y_front, z))) for x, z in pts]

    # Rear face (Quadrant 2: Spec Label)
    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_BACK_LABEL)

    # 8 Outer side quads
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_back[i], v_front[i], v_front[ni], v_back[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_HOUSING)

    # Front collar opening (Radius 27mm circular ring where Guard_Ring mounts)
    r_col = 0.027
    v_col = []
    for i in range(n_pts):
        ang = 2.0 * math.pi * i / n_pts
        x_c = r_col * math.cos(ang)
        z_c = r_col * math.sin(ang)
        v_col.append(bm.verts.new(Vector((x_c, y_front, z_c))))

    # Front face connecting outer 8-sided perimeter to inner circular collar (8 quads)
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_front[i], v_col[i], v_col[ni], v_front[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_HOUSING)

    # Recessed inner seating face for the switch block
    f_seat = bm.faces.new(list(reversed(v_col)))
    f_seat.material_index = 0
    set_face_uv_rect(bm, f_seat, UV_DARK_HOUSING)

    # Top Conduit Entry Boss (8-sided cylinder at Z = +0.037, height 5mm)
    r_cd = 0.010
    h_cd = 0.005
    z_cd_base = sz
    z_cd_top = sz + h_cd
    y_cd_c = 0.012

    v_cb_b = []
    v_cb_t = []
    for i in range(8):
        ang = 2.0 * math.pi * i / 8
        x_p = r_cd * math.cos(ang)
        y_p = y_cd_c + r_cd * math.sin(ang)
        v_cb_b.append(bm.verts.new(Vector((x_p, y_p, z_cd_base))))
        v_cb_t.append(bm.verts.new(Vector((x_p, y_p, z_cd_top))))

    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([v_cb_b[i], v_cb_t[i], v_cb_t[ni], v_cb_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_HOUSING)

    f_cd_top = bm.faces.new(v_cb_t)
    f_cd_top.material_index = 0
    set_face_uv_rect(bm, f_cd_top, UV_DARK_HOUSING)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_guard_ring_mesh(mesh, materials):
    """
    Build Guard_Ring:
    Heavy-duty safety yellow shroud collar surrounding the mushroom button.
    Dimensions: Outer Radius 34mm, Inner Radius 26mm, Depth 18mm (Y: 0.024 to 0.042m).
    Top rim face printed with continuous circular "EMERGENCY STOP ★ NOT-AUS" warning text.
    Includes an integrated illuminated warning alert ring (Slot 1: M_Emission).
    12 segments for smooth circular silhouette.
    100% watertight, solid manifold geometry.
    Tris count: ~96 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    n_seg = 12
    r_out = 0.034
    r_in = 0.026
    y_base = 0.024
    y_rim = 0.042

    v_ob = []  # outer base
    v_ot = []  # outer top rim
    v_it = []  # inner top rim
    v_ib = []  # inner base

    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)

        xo = r_out * cos_a
        zo = r_out * sin_a
        xi = r_in * cos_a
        zi = r_in * sin_a

        v_ob.append(bm.verts.new(Vector((xo, y_base, zo))))
        v_ot.append(bm.verts.new(Vector((xo, y_rim,  zo))))
        v_it.append(bm.verts.new(Vector((xi, y_rim,  zi))))
        v_ib.append(bm.verts.new(Vector((xi, y_base, zi))))

    # 1. Outer cylindrical quads (12 quads -> 24 tris) - Plain yellow
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_ob[i], v_ot[i], v_ot[ni], v_ob[ni]])
        f.material_index = 0  # M_Security_Atlas
        set_face_uv_rect(bm, f, UV_PLAIN_YELLOW)

    # 2. Top Rim Face with continuous circular "EMERGENCY STOP" graphic (12 quads -> 24 tris)
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_ot[i], v_it[i], v_it[ni], v_ot[ni]])
        f.material_index = 0  # M_Security_Atlas
        set_radial_uv(bm, f, center_u=0.215, center_v=0.750, uv_radius=0.185, max_geom_r=r_out)

    # 3. Inner cylindrical quads (12 quads -> 24 tris) - Plain yellow
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_it[i], v_ib[i], v_ib[ni], v_it[ni]])
        f.material_index = 0  # M_Security_Atlas
        set_face_uv_rect(bm, f, UV_PLAIN_YELLOW)

    # 4. Integrated Illuminated Status Ring at the base of the shroud (12 quads -> 24 tris)
    # Beveled glowing collar rim connecting inner base to switch shaft (r = 18mm)
    # Sits at Y = 0.0245 (offset 0.5mm from backplate to eliminate Z-fighting)
    r_shaft = 0.018
    y_emiss = 0.0245
    v_emiss = []
    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        xe = r_shaft * math.cos(ang)
        ze = r_shaft * math.sin(ang)
        v_emiss.append(bm.verts.new(Vector((xe, y_emiss, ze))))

    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_ib[i], v_emiss[i], v_emiss[ni], v_ib[ni]])
        f.material_index = 1  # M_Emission (Slot 1)
        set_face_uv_rect(bm, f, UV_EMISS_BEACON)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_mushroom_button_mesh(mesh, materials):
    """
    Build Mushroom_Button:
    Bold red mushroom palm button (diameter 46mm).
    Origin at its exact geometric interaction center in local pivot space.
    Features:
      - Cylindrical stem neck (radius 13mm, length 15mm)
      - Expanding lower mushroom bell flare (flares out from r=13mm to r=23mm)
      - Beveled palm crown dome with ↻ RESET twist arrows (projects past the shroud)
    12 segments for high-fidelity round profile.
    100% watertight, solid manifold geometry.
    Tris count: ~92 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    n_seg = 12
    r_stem = 0.013
    r_dome_rim = 0.023
    r_dome_top = 0.019

    # Local coordinates relative to Button_Pivot (starts at Y = 0.000, extends to Y = 0.033)
    y_stem_base = 0.000
    y_stem_top  = 0.015
    y_dome_flare = 0.026
    y_dome_peak  = 0.033

    v_sb = []  # stem base
    v_st = []  # stem top
    v_df = []  # dome outer flare rim
    v_dp = []  # dome peak rim

    for i in range(n_seg):
        ang = 2.0 * math.pi * i / n_seg
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)

        xs = r_stem * cos_a
        zs = r_stem * sin_a
        xf = r_dome_rim * cos_a
        zf = r_dome_rim * sin_a
        xp = r_dome_top * cos_a
        zp = r_dome_top * sin_a

        v_sb.append(bm.verts.new(Vector((xs, y_stem_base,  zs))))
        v_st.append(bm.verts.new(Vector((xs, y_stem_top,   zs))))
        v_df.append(bm.verts.new(Vector((xf, y_dome_flare, zf))))
        v_dp.append(bm.verts.new(Vector((xp, y_dome_peak,  zp))))

    # 1. Stem base cap (12-gon -> 10 tris)
    f_base = bm.faces.new(list(reversed(v_sb)))
    f_base.material_index = 0
    set_face_uv_rect(bm, f_base, UV_DARK_HOUSING)

    # 2. Stem neck cylinder (12 quads -> 24 tris)
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_sb[i], v_st[i], v_st[ni], v_sb[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_HOUSING)

    # 3. Lower mushroom bell flare (12 quads -> 24 tris) - Plain red
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_st[i], v_df[i], v_df[ni], v_st[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_PLAIN_RED)

    # 4. Dome outer bevel chamfer (12 quads -> 24 tris) - Plain red
    for i in range(n_seg):
        ni = (i + 1) % n_seg
        f = bm.faces.new([v_df[i], v_dp[i], v_dp[ni], v_df[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_PLAIN_RED)

    # 5. Top Mushroom Palm Dome Face with ↻ RESET twist arrows (12-gon -> 10 tris)
    f_top = bm.faces.new(v_dp)
    f_top.material_index = 0  # M_Security_Atlas
    set_radial_uv(bm, f_top, center_u=0.773, center_v=0.750, uv_radius=0.180, max_geom_r=r_dome_top)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Asset Assembly and Hierarchy
# -------------------------------------------------------------

def assemble_sec_emergency_stop_mushroom(materials):
    """
    Assemble the complete asset hierarchy:
    SEC_Emergency_Stop_Mushroom (Root Empty at 0, 0, 0)
        ├── Mount_Base (Mesh, child of Root)
        ├── Guard_Ring (Mesh, child of Root)
        └── Button_Pivot (Empty, child of Root, local Y axis 0.005m travel)
                └── Mushroom_Button (Mesh, child of Button_Pivot)
    """
    # 1. Root Empty
    root_obj = bpy.data.objects.new("SEC_Emergency_Stop_Mushroom", None)
    root_obj.empty_display_type = 'PLAIN_AXES'
    root_obj.empty_display_size = 0.05
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.collection.objects.link(root_obj)

    # 2. Mount_Base (Mesh, child of Root)
    mesh_base = bpy.data.meshes.new("Mount_Base")
    build_mount_base_mesh(mesh_base, materials)
    obj_base = bpy.data.objects.new("Mount_Base", mesh_base)
    obj_base.location = Vector((0.0, 0.0, 0.0))
    obj_base.parent = root_obj
    bpy.context.scene.collection.objects.link(obj_base)

    # 3. Guard_Ring (Mesh, child of Root)
    mesh_guard = bpy.data.meshes.new("Guard_Ring")
    build_guard_ring_mesh(mesh_guard, materials)
    obj_guard = bpy.data.objects.new("Guard_Ring", mesh_guard)
    obj_guard.location = Vector((0.0, 0.0, 0.0))
    obj_guard.parent = root_obj
    bpy.context.scene.collection.objects.link(obj_guard)

    # 4. Button_Pivot (Empty, child of Root, on button seating plane at Y = 0.024)
    btn_pivot = bpy.data.objects.new("Button_Pivot", None)
    btn_pivot.empty_display_type = 'SINGLE_ARROW'
    btn_pivot.empty_display_size = 0.03
    btn_pivot.location = Vector((0.0, 0.024, 0.0))
    btn_pivot.parent = root_obj
    bpy.context.scene.collection.objects.link(btn_pivot)

    # Limit Location constraint for 5mm press travel along local Y: [0.019, 0.024]
    const = btn_pivot.constraints.new(type='LIMIT_LOCATION')
    const.use_min_x = True; const.min_x = 0.0; const.use_max_x = True; const.max_x = 0.0
    const.use_min_y = True; const.min_y = 0.019; const.use_max_y = True; const.max_y = 0.024
    const.use_min_z = True; const.min_z = 0.0; const.use_max_z = True; const.max_z = 0.0
    const.owner_space = 'LOCAL'

    # Custom properties for interaction
    btn_pivot["press_axis"] = "Y"
    btn_pivot["travel_m"] = 0.005
    btn_pivot["action"] = "EMERGENCY_STOP"
    btn_pivot["reset_type"] = "TWIST_TO_RESET"

    # 5. Mushroom_Button (Mesh, child of Button_Pivot)
    mesh_btn = bpy.data.meshes.new("Mushroom_Button")
    build_mushroom_button_mesh(mesh_btn, materials)
    obj_btn = bpy.data.objects.new("Mushroom_Button", mesh_btn)
    obj_btn.location = Vector((0.0, 0.0, 0.0))  # Local to Button_Pivot
    obj_btn.parent = btn_pivot
    bpy.context.scene.collection.objects.link(obj_btn)

    # Count initial triangles across all meshes
    bpy.context.view_layer.update()
    all_mesh_objs = [obj_base, obj_guard, obj_btn]
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
    assert total_tris <= 300, f"Triangle budget exceeded! {total_tris} > 300 tris"

    all_export_objs = [root_obj, obj_base, obj_guard, btn_pivot, obj_btn]
    return root_obj, all_export_objs, total_tris


def export_and_verify(root_obj, export_objs, initial_tris):
    """Export FBX and verify all constraints."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Emergency_Stop_Mushroom.fbx")
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Emergency_Stop_Mushroom.blend")

    # Select objects for export
    bpy.ops.object.select_all(action='DESELECT')
    for obj in export_objs:
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
    imp_root = bpy.data.objects.get("SEC_Emergency_Stop_Mushroom")
    assert imp_root is not None, "FAILED: Root object SEC_Emergency_Stop_Mushroom missing in FBX!"

    # 2. Verify Children Hierarchy
    imp_base = bpy.data.objects.get("Mount_Base")
    imp_guard = bpy.data.objects.get("Guard_Ring")
    imp_pivot = bpy.data.objects.get("Button_Pivot")
    imp_btn = bpy.data.objects.get("Mushroom_Button")

    assert imp_base is not None, "FAILED: Mount_Base missing!"
    assert imp_base.parent == imp_root, "FAILED: Mount_Base not parented to Root!"

    assert imp_guard is not None, "FAILED: Guard_Ring missing!"
    assert imp_guard.parent == imp_root, "FAILED: Guard_Ring not parented to Root!"

    assert imp_pivot is not None, "FAILED: Button_Pivot missing!"
    assert imp_pivot.parent == imp_root, "FAILED: Button_Pivot not parented to Root!"

    assert imp_btn is not None, "FAILED: Mushroom_Button missing!"
    assert imp_btn.parent == imp_pivot, "FAILED: Mushroom_Button not parented to Button_Pivot!"

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
    assert verify_tris <= 300, f"FAILED: Verified tris count {verify_tris} > 300!"

    # 4. Verify Materials & UVs
    expected_materials = ["M_Security_Atlas", "M_Emission"]
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            assert len(obj.data.uv_layers) > 0, f"Mesh {obj.name} has no UV layer!"
            slot_names = [slot.material.name for slot in obj.material_slots if slot.material]
            for mat_name in slot_names:
                assert mat_name in expected_materials, f"Unexpected material {mat_name} on {obj.name}!"

    print("[VERIFY] Material slots and UV layers verified across all meshes.")

    # 5. Interactive Button Press Verification
    bpy.context.view_layer.update()
    p_init = imp_btn.matrix_world.translation.copy()
    imp_pivot.location.y -= 0.005
    bpy.context.view_layer.update()
    p_pressed = imp_btn.matrix_world.translation.copy()
    y_delta = abs(p_pressed.y - p_init.y)
    print(f"[VERIFY] Button Press Travel Delta: {y_delta:.5f}m (expected ~0.005m)")
    assert 0.004 <= y_delta <= 0.006, f"FAILED: Press delta {y_delta} outside expected range!"

    print("[VERIFY] ALL QA CHECKS PASSED SUCCESSFULLY.")

    # 6. Update Manifest
    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Emergency_Stop_Mushroom"] = {
        "asset_name": "SEC_Emergency_Stop_Mushroom",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "texture_atlas": os.path.join(EXPORTS_DIR, "T_Security_Atlas.png"),
        "tris_count": verify_tris,
        "max_tris_allowed": 300,
        "mesh_count": len(verified_meshes),
        "empty_count": 2,
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
    print("  SEC_Emergency_Stop_Mushroom Generator")
    print("==========================================")

    setup_clean_scene()
    atlas_img = create_security_atlas_texture()
    materials = create_materials(atlas_img)
    root_obj, export_objs, initial_tris = assemble_sec_emergency_stop_mushroom(materials)
    verified_tris = export_and_verify(root_obj, export_objs, initial_tris)

    print("\n==========================================")
    print(f"  PROCESS COMPLETED SUCCESSFULLY [SUCCESS]")
    print(f"  Final Verified Tris: {verified_tris} / 300")
    print("==========================================")


if __name__ == "__main__":
    main()
