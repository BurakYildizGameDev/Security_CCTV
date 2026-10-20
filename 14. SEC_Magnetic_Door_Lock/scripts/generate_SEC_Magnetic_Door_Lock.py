"""
SEC_Magnetic_Door_Lock Generator Script (V3 - Premium Industrial Fidelity)
Industrial Low-Poly Security & CCTV Asset Pack
Upper Budget Limit: 350 triangles
Target Triangles: ~325 triangles

Hierarchy:
SEC_Magnetic_Door_Lock (Lock_Root Empty at 0, 0, 0)
 ├── Mount_Brackets (Mesh, child of Root)
 ├── Magnet_Housing (Mesh, child of Root)
 └── Armature_Plate_Root (Empty, child of Root, at armature plate center 0.000, 0.0525, 0.000)
      └── Armature_Plate (Mesh, child of Armature_Plate_Root)

Materials:
    Slot 0: M_Security_Atlas (Dark Titanium Anodized Aluminum, Labels, Rubber, Resin)
    Slot 1: M_Metal (Brilliant Polished Laminated Steel Core, Armature Plate, Chrome Hardware)
"""

import os
import sys
import math
import json
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

# Absolute path resolution
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
    Generate high-contrast, premium 512x512 industrial texture atlas:
    - Quadrant 0 (X: 0..256, Y: 256..512): Dark Charcoal/Titanium Brushed Anodized Aluminum
    - Quadrant 1 (X: 256..512, Y: 256..512): Brilliant Polished Laminated Steel (Pole Shoes & Armature)
    - Quadrant 2 (X: 0..256, Y: 0..256): Crisp Laser-Etched Nameplate ("SEC-600LB MAG-LOCK • 280KG")
    - Quadrant 3 (X: 256..512, Y: 0..256): Matte Black Potted Resin & Vibrant Glowing Green LED Lens
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
                    # Quadrant 0: Dark Titanium Anodized Aluminum (X: 0..256, Y: 256..512)
                    # -------------------------------------------------------------
                    # Dark charcoal industrial metallic finish with fine horizontal brushed texture
                    base_val = 0.22 + 0.02 * math.sin(x * 0.15)
                    grain = ((y * 19 + x * 37) % 23) / 450.0
                    r = base_val + grain
                    g = base_val + grain + 0.015
                    b = base_val + grain + 0.025

                    # Subtle bevel edge highlights
                    if y in [510, 511]:
                        r, g, b = 0.42, 0.44, 0.48
                    elif y in [256, 257]:
                        r, g, b = 0.15, 0.16, 0.18

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = a

                else:
                    # -------------------------------------------------------------
                    # Quadrant 1: Brilliant Polished Ground Steel (X: 256..512, Y: 256..512)
                    # -------------------------------------------------------------
                    # High-reflectivity ground carbon steel with fine machining marks
                    t = (x - 256) / 256.0
                    spec = 0.85 + 0.09 * math.cos(t * math.pi * 4.0)
                    r = spec
                    g = spec + 0.015
                    b = spec + 0.035

                    # Fine vertical grind striations
                    if (x % 16 in [0, 1]):
                        r *= 0.93; g *= 0.93; b *= 0.93

                    # Horizontal core isolation lines
                    if y in [340, 420]:
                        r, g, b = 0.20, 0.22, 0.25

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = a

            else:
                if x < 256:
                    # -------------------------------------------------------------
                    # Quadrant 2: Laser-Etched Technical Nameplate (X: 0..256, Y: 0..256)
                    # -------------------------------------------------------------
                    # Deep matte dark plate with silver laser-engraved markings
                    r, g, b = 0.16, 0.17, 0.20
                    if (x % 4 in [0, 1]):
                        r, g, b = 0.18, 0.19, 0.22

                    # Silver perimeter border
                    if x in [10, 11, 244, 245] or y in [10, 11, 244, 245]:
                        r, g, b = 0.65, 0.68, 0.72

                    # Title banner: "SEC-600LB MAGLOCK"
                    if 180 <= y <= 220 and 20 <= x <= 235:
                        r, g, b = 0.12, 0.13, 0.15
                        # Laser etched white text blocks
                        if 192 <= y <= 208 and (x % 6 in [0, 1, 2, 3]):
                            r, g, b = 0.95, 0.96, 0.98

                    # Rating details: "280KG • 12/24V DC • FAIL-SAFE"
                    if 115 <= y <= 160 and 25 <= x <= 230:
                        if 128 <= y <= 148 and (x % 5 in [0, 1, 2]):
                            r, g, b = 0.85, 0.88, 0.92

                    # Wire schematic lines (fine crisp technical lines)
                    if 35 <= y <= 95 and 25 <= x <= 230:
                        if y in [45, 65, 85] or x in [55, 100, 145, 190]:
                            r, g, b = 0.55, 0.58, 0.62
                        elif 40 <= y <= 90 and (x % 4 in [0, 1]):
                            r, g, b = 0.75, 0.78, 0.82

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = a

                else:
                    # -------------------------------------------------------------
                    # Quadrant 3: Matte Black Potted Resin & Status LED (X: 256..512, Y: 0..256)
                    # -------------------------------------------------------------
                    # Deep matte dark charcoal / epoxy resin
                    r, g, b = 0.10, 0.11, 0.12
                    if (x % 8 in [0, 1]) or (y % 8 in [0, 1]):
                        r, g, b = 0.08, 0.09, 0.10

                    # Status LED Lens at center (X: 364..404, Y: 108..148)
                    dx_led = x - 384
                    dy_led = y - 128
                    dist_led = math.sqrt(dx_led**2 + dy_led**2)
                    if dist_led <= 18:
                        if dist_led <= 10:
                            # Vibrant Glowing Emerald Green LED Core
                            r, g, b = 0.10, 1.00, 0.30
                        elif dist_led <= 14:
                            # Chrome Bezel Chamfer
                            r, g, b = 0.75, 0.78, 0.82
                        else:
                            r, g, b = 0.15, 0.16, 0.18

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
    Slot 1: M_Metal
    """
    materials = {}

    # 1. Slot 0: M_Security_Atlas (Dark titanium body, labels, rubber washer, dark resin)
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

    bsdf0.inputs['Roughness'].default_value = 0.28
    bsdf0.inputs['Metallic'].default_value = 0.65
    mat_atlas.diffuse_color = (0.22, 0.24, 0.27, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. Slot 1: M_Metal (Polished ground steel core, armature plate, chrome hardware)
    mat_metal = bpy.data.materials.get("M_Metal")
    if not mat_metal:
        mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    nodes1 = mat_metal.node_tree.nodes
    links1 = mat_metal.node_tree.links
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

    bsdf1.inputs['Roughness'].default_value = 0.14
    bsdf1.inputs['Metallic'].default_value = 0.98
    mat_metal.diffuse_color = (0.85, 0.88, 0.92, 1.0)
    materials["M_Metal"] = mat_metal

    return materials


def attach_standard_materials(mesh, materials):
    """Attach the 2 standard materials in strict order [M_Security_Atlas, M_Metal]."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Metal"])           # Slot 1


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
UV_DARK_ALUMINUM    = (0.050, 0.550, 0.450, 0.950)  # Dark titanium brushed aluminum (Housing & Bracket)
UV_POLISHED_STEEL   = (0.550, 0.550, 0.950, 0.950)  # Brilliant ground steel (Poles & Armature)
UV_SPEC_NAMEPLATE   = (0.050, 0.050, 0.450, 0.450)  # Laser-etched specification nameplate
UV_DARK_EPOXY       = (0.550, 0.050, 0.750, 0.450)  # Matte dark black resin & neoprene washer
UV_STATUS_LED       = (0.710, 0.200, 0.790, 0.300)  # Glowing emerald green LED lens core


# -------------------------------------------------------------
# High-Density Low-Poly Mesh Builders (~322 tris total)
# -------------------------------------------------------------

def build_mount_brackets_mesh(mesh, materials):
    """
    Build Mount_Brackets:
    Heavy-duty industrial L-mounting plate for door frame / header jamb mounting.
    Dimensions: Length 250mm (X: -0.125 to +0.125), Depth 6mm (Y: 0.000 to 0.006m),
    Height 48mm (Z: -0.024 to +0.024m) with top overhang mounting lip (Z: 0.024 to 0.030m).
    Includes:
    - Extruded L-bracket profile in dark titanium aluminum
    - 4 side fastening hex cap bolts with washers (M_Metal)
    - 2 top flange countersunk mounting screw slots (M_Metal)
    Tris count: ~116 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_half = 0.125
    z_bot = -0.024
    z_top = 0.024
    y_back = 0.000
    y_front = 0.006
    y_lip = 0.012

    # 1. Extruded L-bracket profile
    pts_profile = [
        (y_back, z_bot),
        (y_front, z_bot),
        (y_front, z_top),
        (y_lip, z_top),
        (y_lip, z_top + 0.006),
        (y_back, z_top + 0.006)
    ]
    np = len(pts_profile)

    v_left = [bm.verts.new(Vector((-x_half, y, z))) for y, z in pts_profile]
    v_right = [bm.verts.new(Vector((x_half, y, z))) for y, z in pts_profile]

    # End caps (Left & Right)
    f_end_l = bm.faces.new(list(reversed(v_left)))
    f_end_l.material_index = 0
    set_face_uv_rect(bm, f_end_l, UV_DARK_ALUMINUM)

    f_end_r = bm.faces.new(v_right)
    f_end_r.material_index = 0
    set_face_uv_rect(bm, f_end_r, UV_DARK_ALUMINUM)

    # Perimeter faces (All uniform dark titanium aluminum - NO stretched graphics!)
    for i in range(np):
        ni = (i + 1) % np
        f = bm.faces.new([v_left[i], v_right[i], v_right[ni], v_left[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_ALUMINUM)

    # 2. Side Fastening Hex Cap Bolts with Washers (4 bolts: 2 left, 2 right)
    r_bolt = 0.0032
    for s_x in [-0.120, 0.120]:
        for s_z in [-0.012, 0.012]:
            v_b_bot = []
            v_b_top = []
            for i in range(6):
                ang = 2.0 * math.pi * i / 6
                xb = s_x + r_bolt * math.cos(ang)
                zb = s_z + r_bolt * math.sin(ang)
                v_b_bot.append(bm.verts.new(Vector((xb, 0.006, zb))))
                v_b_top.append(bm.verts.new(Vector((xb, 0.009, zb))))

            for i in range(6):
                ni = (i + 1) % 6
                fb = bm.faces.new([v_b_bot[i], v_b_top[i], v_b_top[ni], v_b_bot[ni]])
                fb.material_index = 1  # M_Metal
                set_face_uv_rect(bm, fb, UV_POLISHED_STEEL)

            f_btop = bm.faces.new(v_b_top)
            f_btop.material_index = 1
            set_face_uv_rect(bm, f_btop, UV_POLISHED_STEEL)

    # 3. Top Flange Countersunk Mounting Screws (2 screws along top lip)
    r_tscrew = 0.0030
    for s_x in [-0.050, 0.050]:
        v_ts_b = []
        v_ts_t = []
        for i in range(6):
            ang = 2.0 * math.pi * i / 6
            xt = s_x + r_tscrew * math.cos(ang)
            yt = 0.006 + r_tscrew * math.sin(ang)
            v_ts_b.append(bm.verts.new(Vector((xt, yt, z_top))))
            v_ts_t.append(bm.verts.new(Vector((xt, yt, z_top + 0.003))))

        for i in range(6):
            ni = (i + 1) % 6
            f = bm.faces.new([v_ts_b[i], v_ts_t[i], v_ts_t[ni], v_ts_b[ni]])
            f.material_index = 1
            set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

        f_tstop = bm.faces.new(v_ts_t)
        f_tstop.material_index = 1
        set_face_uv_rect(bm, f_tstop, UV_POLISHED_STEEL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_magnet_housing_mesh(mesh, materials):
    """
    Build Magnet_Housing:
    Primary electromagnetic lock body:
    - Dark titanium anodized aluminum body with 45° chamfers on top/bottom front corners
    - Dual brilliant polished E-core steel pole shoes (M_Metal, upper and lower)
    - 3D recessed central epoxy resin isolation trench (depth 2mm, M_Security_Atlas dark)
    - Left electronics access cover with laser-engraved nameplate badge ("SEC-600LB MAGLOCK")
    - 3D status LED bezel & glowing emerald green lens
    - Top conduit cable entry gland hex nut (M_Metal)
    - 2 front tamper-proof hex socket screws
    Dimensions: Length 250mm (X: -0.125 to +0.125), Depth 29mm (Y: 0.006 to 0.035m),
    Height 48mm (Z: -0.024 to +0.024m).
    Tris count: ~110 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    y_base = 0.006
    y_face = 0.035
    c_edge = 0.0035  # 3.5mm crisp chamfer on top/bottom front corners
    z_half = 0.024
    x_half = 0.125

    # 1. Outer Aluminum Body Profile
    prof_outer = [
        (y_base, -z_half),
        (y_face - c_edge, -z_half),
        (y_face, -z_half + c_edge),
        (y_face,  z_half - c_edge),
        (y_face - c_edge,  z_half),
        (y_base,  z_half)
    ]
    n_po = len(prof_outer)

    v_c_left = [bm.verts.new(Vector((-x_half, y, z))) for y, z in prof_outer]
    v_c_right = [bm.verts.new(Vector((x_half, y, z))) for y, z in prof_outer]

    # End caps (Left & Right)
    f_c_left = bm.faces.new(list(reversed(v_c_left)))
    f_c_left.material_index = 0
    set_face_uv_rect(bm, f_c_left, UV_DARK_ALUMINUM)

    f_c_right = bm.faces.new(v_c_right)
    f_c_right.material_index = 0
    set_face_uv_rect(bm, f_c_right, UV_DARK_ALUMINUM)

    # Perimeter casing faces (rear, bottom, bottom chamfer, top chamfer, top)
    for i in range(n_po):
        ni = (i + 1) % n_po
        if i == 2:
            continue  # Front face handled separately below
        f = bm.faces.new([v_c_left[i], v_c_right[i], v_c_right[ni], v_c_left[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_DARK_ALUMINUM)

    # 2. Detailed Front Magnetic Faceplate (Y = 0.035m)
    # Split:
    # Left electronics access cover: X: -0.125 to -0.095 (Width 30mm)
    # Magnetic pole core zone: X: -0.095 to +0.125 (Width 220mm)
    x_split = -0.095
    z_f_bot = -z_half + c_edge
    z_f_top =  z_half - c_edge

    v_fc_bl = bm.verts.new(Vector((-x_half, y_face, z_f_bot)))
    v_fc_br = bm.verts.new(Vector((x_split, y_face, z_f_bot)))
    v_fc_tr = bm.verts.new(Vector((x_split, y_face, z_f_top)))
    v_fc_tl = bm.verts.new(Vector((-x_half, y_face, z_f_top)))

    # Left access cover face with laser-engraved nameplate badge (+Y normal, flip_u=True)
    f_left_cover = bm.faces.new([v_fc_bl, v_fc_br, v_fc_tr, v_fc_tl])
    f_left_cover.material_index = 0
    set_face_uv_rect(bm, f_left_cover, UV_SPEC_NAMEPLATE, flip_u=True)

    # Magnetic Core with 3D Recessed Trench:
    # Lower Pole: Z: z_f_bot to -0.0025, Y = 0.035 (Polished Steel)
    # Recessed Epoxy Trench: Z: -0.0025 to +0.0025, Y = 0.0330 (Recessed 2mm!)
    # Upper Pole: Z: +0.0025 to z_f_top, Y = 0.035 (Polished Steel)
    z_sep = 0.0025
    y_recess = y_face - 0.0020

    # Lower pole plate
    v_p1_bl = v_fc_br
    v_p1_br = bm.verts.new(Vector((x_half, y_face, z_f_bot)))
    v_p1_tr = bm.verts.new(Vector((x_half, y_face, -z_sep)))
    v_p1_tl = bm.verts.new(Vector((x_split, y_face, -z_sep)))

    f_p1 = bm.faces.new([v_p1_bl, v_p1_br, v_p1_tr, v_p1_tl])
    f_p1.material_index = 1  # M_Metal (Polished Steel)
    set_face_uv_rect(bm, f_p1, UV_POLISHED_STEEL, flip_u=True)

    # 3D Recessed Trench Walls & Floor
    v_t_bl = bm.verts.new(Vector((x_split, y_recess, -z_sep)))
    v_t_br = bm.verts.new(Vector((x_half,  y_recess, -z_sep)))
    v_t_tr = bm.verts.new(Vector((x_half,  y_recess,  z_sep)))
    v_t_tl = bm.verts.new(Vector((x_split, y_recess,  z_sep)))

    # Trench lower step wall
    f_tw_bot = bm.faces.new([v_p1_tl, v_p1_tr, v_t_br, v_t_bl])
    f_tw_bot.material_index = 0
    set_face_uv_rect(bm, f_tw_bot, UV_DARK_EPOXY)

    # Trench floor (Dark matte black potted resin)
    f_t_floor = bm.faces.new([v_t_bl, v_t_br, v_t_tr, v_t_tl])
    f_t_floor.material_index = 0
    set_face_uv_rect(bm, f_t_floor, UV_DARK_EPOXY)

    # Upper pole plate
    v_p2_tr = bm.verts.new(Vector((x_half, y_face, z_f_top)))
    v_p2_tl = v_fc_tr
    v_p2_br = bm.verts.new(Vector((x_half, y_face, z_sep)))
    v_p2_bl = bm.verts.new(Vector((x_split, y_face, z_sep)))

    # Trench upper step wall
    f_tw_top = bm.faces.new([v_t_tl, v_t_tr, v_p2_br, v_p2_bl])
    f_tw_top.material_index = 0
    set_face_uv_rect(bm, f_tw_top, UV_DARK_EPOXY)

    # Upper pole plate face
    f_p2 = bm.faces.new([v_p2_bl, v_p2_br, v_p2_tr, v_p2_tl])
    f_p2.material_index = 1  # M_Metal (Polished Steel)
    set_face_uv_rect(bm, f_p2, UV_POLISHED_STEEL, flip_u=True)

    # 3. Status LED Bezel on Left Cover (X = -0.110, Y = 0.035 to 0.0375, Z = 0.000)
    # 6-sided chrome bezel with vibrant green LED lens
    r_led = 0.0035
    x_led = -0.110
    z_led = 0.000
    y_led_t = 0.0375

    v_lb = []
    v_lt = []
    for i in range(6):
        ang = 2.0 * math.pi * i / 6
        xl = x_led + r_led * math.cos(ang)
        zl = z_led + r_led * math.sin(ang)
        v_lb.append(bm.verts.new(Vector((xl, y_face, zl))))
        v_lt.append(bm.verts.new(Vector((xl, y_led_t, zl))))

    for i in range(6):
        ni = (i + 1) % 6
        f = bm.faces.new([v_lb[i], v_lt[i], v_lt[ni], v_lb[ni]])
        f.material_index = 1  # Chrome bezel
        set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

    f_led_face = bm.faces.new(v_lt)
    f_led_face.material_index = 0  # Glowing Emerald Green LED
    set_face_uv_rect(bm, f_led_face, UV_STATUS_LED)

    # 4. Conduit Wiring Cable Entry Gland on Top (X = -0.110, Y = 0.018, Z = +0.024 to +0.033)
    # 6-sided hex nut fitting
    r_gland = 0.0055
    y_gland = 0.018
    z_g_b = 0.024
    z_g_t = 0.033

    v_gb = []
    v_gt = []
    for i in range(6):
        ang = 2.0 * math.pi * i / 6
        xg = x_led + r_gland * math.cos(ang)
        yg = y_gland + r_gland * math.sin(ang)
        v_gb.append(bm.verts.new(Vector((xg, yg, z_g_b))))
        v_gt.append(bm.verts.new(Vector((xg, yg, z_g_t))))

    for i in range(6):
        ni = (i + 1) % 6
        f = bm.faces.new([v_gb[i], v_gt[i], v_gt[ni], v_gb[ni]])
        f.material_index = 1  # M_Metal
        set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

    f_gtop = bm.faces.new(v_gt)
    f_gtop.material_index = 0  # Rubber seal cap
    set_face_uv_rect(bm, f_gtop, UV_DARK_EPOXY)

    # 5. Front Access Panel Security Screws (2 screws at X = -0.120, Z = ±0.015)
    r_fsc = 0.0022
    for sz_fsc in [-0.015, 0.015]:
        v_fsc_b = []
        v_fsc_t = []
        for i in range(6):
            ang = 2.0 * math.pi * i / 6
            xf = -0.120 + r_fsc * math.cos(ang)
            zf = sz_fsc + r_fsc * math.sin(ang)
            v_fsc_b.append(bm.verts.new(Vector((xf, y_face, zf))))
            v_fsc_t.append(bm.verts.new(Vector((xf, y_face + 0.0014, zf))))

        for i in range(6):
            ni = (i + 1) % 6
            f = bm.faces.new([v_fsc_b[i], v_fsc_t[i], v_fsc_t[ni], v_fsc_b[ni]])
            f.material_index = 1
            set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

        f_fsctop = bm.faces.new(v_fsc_t)
        f_fsctop.material_index = 1
        set_face_uv_rect(bm, f_fsctop, UV_POLISHED_STEEL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_armature_plate_mesh(mesh, materials):
    """
    Build Armature_Plate:
    Precision solid steel counter-plate mounted to the door leaf.
    Dimensions: Length 180mm (X: -0.090 to +0.090), Height 38mm (Z: -0.019 to +0.019),
    Thickness 11mm (Y: -0.0055 to +0.0055 relative to Armature_Plate_Root at Y = 0.0525m).
    World Y position: 0.047 to 0.058m (12mm visible air gap from magnet face at Y = 0.035m).
    Includes:
    - 45-degree beveled perimeter chamfers on both front and rear
    - Central countersunk sex bolt head (8-sided) with recessed Allen driver socket (6-sided)
    - Rear neoprene rubber floating compression washer (8-sided)
    - Dual steel anti-rotation alignment guide pins on left & right
    Tris count: ~100 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_ap_half = 0.090
    z_ap_half = 0.019
    y_ap_f = -0.0055  # Front mating face (facing -Y towards magnet)
    y_ap_b =  0.0055  # Rear door face (facing +Y towards door leaf)
    c_ap = 0.0025    # 2.5mm perimeter chamfer

    # Chamfered profile on front face
    pts_ap = [
        (y_ap_b, -z_ap_half),
        (y_ap_f + c_ap, -z_ap_half),
        (y_ap_f, -z_ap_half + c_ap),
        (y_ap_f,  z_ap_half - c_ap),
        (y_ap_f + c_ap,  z_ap_half),
        (y_ap_b,  z_ap_half)
    ]
    np = len(pts_ap)

    v_apl = [bm.verts.new(Vector((-x_ap_half, y, z))) for y, z in pts_ap]
    v_apr = [bm.verts.new(Vector((x_ap_half, y, z))) for y, z in pts_ap]

    # End caps
    f_apl = bm.faces.new(list(reversed(v_apl)))
    f_apl.material_index = 1
    set_face_uv_rect(bm, f_apl, UV_POLISHED_STEEL)

    f_apr = bm.faces.new(v_apr)
    f_apr.material_index = 1
    set_face_uv_rect(bm, f_apr, UV_POLISHED_STEEL)

    # Perimeter faces (All clean polished ground steel)
    for i in range(np):
        ni = (i + 1) % np
        f = bm.faces.new([v_apl[i], v_apr[i], v_apr[ni], v_apl[ni]])
        f.material_index = 1  # Polished Steel
        set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

    # 2. Central Countersunk Sex Bolt Head (Recessed into front mating face at Y = -0.0055)
    r_bolt = 0.0065
    y_bolt_base = -0.0055
    y_bolt_tip  = -0.0070

    v_sb_b = []
    v_sb_t = []
    for i in range(8):
        ang = 2.0 * math.pi * i / 8
        xb = r_bolt * math.cos(ang)
        zb = r_bolt * math.sin(ang)
        v_sb_b.append(bm.verts.new(Vector((xb, y_bolt_base, zb))))
        v_sb_t.append(bm.verts.new(Vector((xb, y_bolt_tip, zb))))

    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([v_sb_b[i], v_sb_t[i], v_sb_t[ni], v_sb_b[ni]])
        f.material_index = 1  # M_Metal
        set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

    f_sbtop = bm.faces.new(v_sb_t)
    f_sbtop.material_index = 1
    set_face_uv_rect(bm, f_sbtop, UV_POLISHED_STEEL)

    # 2b. Central Hex Socket Driver (6-sided Allen socket detail)
    r_hex_in = 0.0032
    v_hin_b = []
    v_hin_t = []
    for i in range(6):
        ang = 2.0 * math.pi * i / 6
        xh = r_hex_in * math.cos(ang)
        zh = r_hex_in * math.sin(ang)
        v_hin_b.append(bm.verts.new(Vector((xh, y_bolt_tip, zh))))
        v_hin_t.append(bm.verts.new(Vector((xh, y_bolt_tip - 0.0008, zh))))

    for i in range(6):
        ni = (i + 1) % 6
        f = bm.faces.new([v_hin_b[i], v_hin_t[i], v_hin_t[ni], v_hin_b[ni]])
        f.material_index = 1
        set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

    f_hex_tip = bm.faces.new(v_hin_t)
    f_hex_tip.material_index = 1
    set_face_uv_rect(bm, f_hex_tip, UV_POLISHED_STEEL)

    # 3. Neoprene Compression Washer (Behind plate at rear door face at Y = +0.0055)
    r_wash = 0.012
    y_w_b = 0.0055
    y_w_t = 0.0085

    v_wb = []
    v_wt = []
    for i in range(8):
        ang = 2.0 * math.pi * i / 8
        xw = r_wash * math.cos(ang)
        zw = r_wash * math.sin(ang)
        v_wb.append(bm.verts.new(Vector((xw, y_w_b, zw))))
        v_wt.append(bm.verts.new(Vector((xw, y_w_t, zw))))

    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([v_wb[i], v_wt[i], v_wt[ni], v_wb[ni]])
        f.material_index = 0  # Neoprene rubber (Slot 0)
        set_face_uv_rect(bm, f, UV_DARK_EPOXY)

    f_wtop = bm.faces.new(v_wt)
    f_wtop.material_index = 0
    set_face_uv_rect(bm, f_wtop, UV_DARK_EPOXY)

    # 4. Dual Anti-Rotation Alignment Guide Pins on Left and Right (X = ±0.065m)
    r_pin = 0.0022
    for sx_p in [-0.065, 0.065]:
        v_pb = []
        v_pt = []
        for i in range(4):
            ang = 2.0 * math.pi * i / 4 + math.pi / 4.0
            xp = sx_p + r_pin * math.cos(ang)
            zp = r_pin * math.sin(ang)
            v_pb.append(bm.verts.new(Vector((xp, 0.0055, zp))))
            v_pt.append(bm.verts.new(Vector((xp, 0.0095, zp))))

        for i in range(4):
            ni = (i + 1) % 4
            f = bm.faces.new([v_pb[i], v_pt[i], v_pt[ni], v_pb[ni]])
            f.material_index = 1
            set_face_uv_rect(bm, f, UV_POLISHED_STEEL)

        f_ptop = bm.faces.new(v_pt)
        f_ptop.material_index = 1
        set_face_uv_rect(bm, f_ptop, UV_POLISHED_STEEL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Main Assembly & Verification Routine
# -------------------------------------------------------------

def generate_asset():
    """Build, assemble, export, and thoroughly verify SEC_Magnetic_Door_Lock."""
    print("=" * 42)
    print("  SEC_Magnetic_Door_Lock Generator")
    print("=" * 42)

    setup_clean_scene()
    atlas_img = create_security_atlas_texture()
    materials = create_materials(atlas_img)

    # 1. Root Empty: SEC_Magnetic_Door_Lock at (0, 0, 0)
    root_obj = bpy.data.objects.new("SEC_Magnetic_Door_Lock", None)
    root_obj.empty_display_type = 'ARROWS'
    root_obj.empty_display_size = 0.08
    root_obj.location = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(root_obj)

    # 2. Mount_Brackets (Child of Root)
    brackets_mesh = bpy.data.meshes.new("Mount_Brackets_Mesh")
    build_mount_brackets_mesh(brackets_mesh, materials)
    brackets_obj = bpy.data.objects.new("Mount_Brackets", brackets_mesh)
    bpy.context.collection.objects.link(brackets_obj)
    brackets_obj.parent = root_obj
    brackets_obj.location = (0.0, 0.0, 0.0)

    # 3. Magnet_Housing (Child of Root)
    housing_mesh = bpy.data.meshes.new("Magnet_Housing_Mesh")
    build_magnet_housing_mesh(housing_mesh, materials)
    housing_obj = bpy.data.objects.new("Magnet_Housing", housing_mesh)
    bpy.context.collection.objects.link(housing_obj)
    housing_obj.parent = root_obj
    housing_obj.location = (0.0, 0.0, 0.0)

    # 4. Armature_Plate_Root Empty (Child of Root at Armature Plate Center)
    # Magnet front face is at Y = 0.035m
    # 12mm visible air gap -> Armature front mating face is at Y = 0.047m
    # Thickness is 11mm -> Center is at Y = 0.0525m
    armature_pivot = bpy.data.objects.new("Armature_Plate_Root", None)
    armature_pivot.empty_display_type = 'PLAIN_AXES'
    armature_pivot.empty_display_size = 0.05
    armature_pivot.location = (0.0, 0.0525, 0.0)
    bpy.context.collection.objects.link(armature_pivot)
    armature_pivot.parent = root_obj

    # Custom properties for interaction and physics
    armature_pivot["part_type"] = "ARMATURE_PLATE"
    armature_pivot["holding_force_n"] = 2800  # 600 lbs / 280 kg
    armature_pivot["operating_voltage"] = "12/24V DC"
    armature_pivot["air_gap_m"] = 0.012
    armature_pivot["lock_state"] = "UNLOCKED_PREVIEW"

    # 5. Armature_Plate (Child of Armature_Plate_Root)
    armature_mesh = bpy.data.meshes.new("Armature_Plate_Mesh")
    build_armature_plate_mesh(armature_mesh, materials)
    armature_obj = bpy.data.objects.new("Armature_Plate", armature_mesh)
    bpy.context.collection.objects.link(armature_obj)
    armature_obj.parent = armature_pivot
    armature_obj.location = (0.0, 0.0, 0.0)

    # Apply weighted normal modifiers for crisp CAD look
    for obj in [brackets_obj, housing_obj, armature_obj]:
        mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        mod.keep_sharp = True

    bpy.context.view_layer.update()

    # Calculate triangulated polygon counts
    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [brackets_obj, housing_obj, armature_obj]:
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
    if total_tris > 350:
        raise ValueError(f"Triangle count {total_tris} exceeds upper limit of 350 tris!")

    # Select only this asset for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root_obj, brackets_obj, housing_obj, armature_pivot, armature_obj]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    # FBX Export
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Magnetic_Door_Lock.fbx")
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

    # Save Blend file
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Magnetic_Door_Lock.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Saved blend file to: {blend_path}")

    # Remove temporary .blend1
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        try:
            os.remove(blend1_path)
            print(f"[INFO] Cleaned up temporary backup file: {blend1_path}")
        except Exception:
            pass

    # -------------------------------------------------------------
    # QA Verification via Re-import
    # -------------------------------------------------------------
    print(f"\n[VERIFY] Re-importing FBX from: {fbx_path}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    imported_names = [o.name for o in bpy.context.scene.objects]
    print(f"[VERIFY] Imported objects count: {len(imported_names)}")

    imp_root = bpy.data.objects.get("SEC_Magnetic_Door_Lock")
    imp_brackets = bpy.data.objects.get("Mount_Brackets")
    imp_housing = bpy.data.objects.get("Magnet_Housing")
    imp_armature_pivot = bpy.data.objects.get("Armature_Plate_Root")
    imp_armature = bpy.data.objects.get("Armature_Plate")

    assert imp_root is not None, "Root object 'SEC_Magnetic_Door_Lock' missing!"
    assert imp_brackets is not None, "'Mount_Brackets' missing!"
    assert imp_housing is not None, "'Magnet_Housing' missing!"
    assert imp_armature_pivot is not None, "'Armature_Plate_Root' missing!"
    assert imp_armature is not None, "'Armature_Plate' missing!"

    # Verify hierarchy
    assert imp_brackets.parent == imp_root, "Mount_Brackets must be child of root!"
    assert imp_housing.parent == imp_root, "Magnet_Housing must be child of root!"
    assert imp_armature_pivot.parent == imp_root, "Armature_Plate_Root must be child of root!"
    assert imp_armature.parent == imp_armature_pivot, "Armature_Plate must be child of Armature_Plate_Root!"
    print("[VERIFY] Full parent-child hierarchy verified successfully.")

    # Verify triangle count on re-imported meshes
    reimport_tris = 0
    for o in [imp_brackets, imp_housing, imp_armature]:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        reimport_tris += len(bm.faces)
        bm.free()

    print(f"[VERIFY] Total verified triangulated triangles: {reimport_tris}")
    assert reimport_tris <= 350, f"Re-imported tris {reimport_tris} exceeds limit 350!"

    # Verify materials & UV layers
    for o in [imp_brackets, imp_housing, imp_armature]:
        mat_names = [slot.material.name for slot in o.material_slots if slot.material]
        assert len(mat_names) >= 1, f"Mesh {o.name} has no materials!"
        assert len(o.data.uv_layers) >= 1, f"Mesh {o.name} missing UV layer!"
    print("[VERIFY] Material slots and UV layers verified across all meshes.")

    # Verify physical clearance gap between magnet and armature plate
    # Magnet front face is at Y = 0.035, Armature front mating face is at Y = 0.047 -> 0.012m gap
    gap_y = imp_armature_pivot.matrix_world.translation.y - 0.035
    print(f"[VERIFY] Measured physical air gap between Magnet and Armature Plate: {gap_y:.4f}m (expected ~0.0175m to center, 0.012m to face)")
    assert 0.010 <= gap_y <= 0.025, f"Air gap {gap_y} out of realistic range!"

    print("[VERIFY] ALL QA CHECKS PASSED SUCCESSFULLY.")

    # -------------------------------------------------------------
    # Manifest Record Generation
    # -------------------------------------------------------------
    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_Magnetic_Door_Lock"] = {
        "asset_name": "SEC_Magnetic_Door_Lock",
        "fbx_path": "exports/SEC_Magnetic_Door_Lock.fbx",
        "blend_path": "exports/SEC_Magnetic_Door_Lock.blend",
        "tris_count": reimport_tris,
        "mesh_count": 3,
        "empty_count": 2,
        "materials": ["M_Security_Atlas", "M_Metal"],
        "status": "SUCCESS"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[INFO] Manifest updated: {manifest_path}")

    print("\n" + "=" * 42)
    print(f"  PROCESS COMPLETED SUCCESSFULLY [SUCCESS]")
    print(f"  Final Verified Tris: {reimport_tris} / 350")
    print("=" * 42)


if __name__ == "__main__":
    generate_asset()
