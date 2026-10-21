"""
=============================================================================
Security CCTV Asset Production Suite - Asset 19
Asset Name: SEC_Alarm_Siren_Beacon
Category: Industrial Security Sounder & Strobe Warning Beacon
Target Polycount Budget: <= 350 Triangles
Hierarchy & Pivot:
    SEC_Alarm_Siren_Beacon (Root Empty at (0, 0, 0) flush on wall plane)
     ├── Mount_Plate (Mesh, root child, Slot 0)
     ├── Siren_Housing (Mesh, root child, Slot 0)
     │    └── Speaker_Grille (Mesh, housing child, Slot 0)
     └── Beacon_Base (Mesh, root child, Slot 0 & Slot 2)
          └── Beacon_Lens (Mesh, base child, Slot 1 M_Transparent)
Material Slots:
    Slot 0: M_Security_Atlas (Housing, mounting plate, louvers, ratings)
    Slot 1: M_Transparent (Translucent emergency red/amber strobe Fresnel dome)
    Slot 2: M_Emission (High-intensity xenon strobe flash tube / warning LED)
Output:
    - exports/SEC_Alarm_Siren_Beacon.fbx
    - exports/SEC_Alarm_Siren_Beacon.blend
    - exports/T_Security_Atlas.png
    - exports/manifest.json
=============================================================================
"""

import bpy
import bmesh
from mathutils import Vector, Euler, Matrix
import math
import os
import sys
import json

# Ensure PIL / Pillow is available in Blender Python
site_pkg = r"C:\Users\Burak\AppData\Local\Programs\Python\Python311\Lib\site-packages"
if site_pkg not in sys.path:
    sys.path.append(site_pkg)

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Paths configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

# -------------------------------------------------------------
# Font Helper
# -------------------------------------------------------------

def get_fonts():
    """Load crisp industrial fonts with standard fallbacks."""
    f_xl = f_lg = f_md = f_sm = f_xs = None
    t_xl = t_lg = t_md = t_sm = t_xs = None

    font_paths = [
        "C:\\Windows\\Fonts\\consola.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeuib.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf"
    ]
    primary_font = None
    bold_font = "C:\\Windows\\Fonts\\arialbd.ttf" if os.path.exists("C:\\Windows\\Fonts\\arialbd.ttf") else None

    for p in font_paths:
        if os.path.exists(p):
            primary_font = p
            break

    if primary_font and HAS_PIL:
        try:
            f_xl = ImageFont.truetype(primary_font, 56)
            f_lg = ImageFont.truetype(primary_font, 40)
            f_md = ImageFont.truetype(primary_font, 28)
            f_sm = ImageFont.truetype(primary_font, 22)
            f_xs = ImageFont.truetype(primary_font, 18)

            bf = bold_font if bold_font else primary_font
            t_xl = ImageFont.truetype(bf, 64)
            t_lg = ImageFont.truetype(bf, 46)
            t_md = ImageFont.truetype(bf, 32)
            t_sm = ImageFont.truetype(bf, 24)
            t_xs = ImageFont.truetype(bf, 20)
        except Exception as e:
            print(f"[WARN] Failed loading TTF fonts: {e}")

    if f_xl is None:
        f_xl = f_lg = f_md = f_sm = f_xs = ImageFont.load_default()
        t_xl = t_lg = t_md = t_sm = t_xs = ImageFont.load_default()

    return f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs


# -------------------------------------------------------------
# High-Resolution 2048x2048 Texture Atlas Generator
# -------------------------------------------------------------

def generate_security_atlas_texture():
    """Generate 2048x2048 Ultra-Sharp Texture Atlas (T_Security_Atlas.png)."""
    out_path = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
    if not HAS_PIL:
        return out_path

    w, h = 2048, 2048
    # Base background: deep dark anthracite
    img = Image.new("RGBA", (w, h), (28, 32, 38, 255))
    draw = ImageDraw.Draw(img)
    f_xl, f_lg, f_md, f_sm, f_xs, t_xl, t_lg, t_md, t_sm, t_xs = get_fonts()

    # =========================================================================
    # ZONE 1: FRONT SIREN FASCIA & WARNING GRAPHICS (X: 0..1100, Y: 0..1100)
    # Applied to upper front face of the siren housing
    # =========================================================================
    # Polycarbonate pure white housing casing
    draw.rectangle([0, 0, 1100, 1100], fill=(238, 242, 246, 255))
    # Beveled shadow borders
    draw.line([(0, 0), (1100, 0)], fill=(255, 255, 255, 255), width=4)
    draw.line([(0, 1096), (1100, 1096)], fill=(180, 190, 200, 255), width=4)
    draw.line([(0, 0), (0, 1100)], fill=(255, 255, 255, 255), width=4)
    draw.line([(1096, 0), (1096, 1100)], fill=(180, 190, 200, 255), width=4)

    # Top Warning Header Banner (Emergency Red with white typography)
    draw.rectangle([40, 50, 1060, 210], fill=(205, 25, 25, 255), outline=(150, 15, 15, 255), width=3)
    draw.rectangle([50, 60, 1050, 200], fill=(220, 30, 30, 255))
    draw.text((100, 75), "SECURITY WARNING", fill=(255, 255, 255, 255), font=t_xl)
    draw.text((105, 150), "24HR ELECTRONIC INTRUDER ALARM & CCTV SYSTEM", fill=(255, 240, 240, 255), font=t_sm)

    # Strobe Hazard Warning Triangle (Yellow / Black ISO Warning)
    tri_x, tri_y = 550, 420
    tri_r = 130
    p1 = (tri_x, tri_y - tri_r)
    p2 = (tri_x + int(tri_r * 1.15), tri_y + int(tri_r * 0.75))
    p3 = (tri_x - int(tri_r * 1.15), tri_y + int(tri_r * 0.75))
    draw.polygon([p1, p2, p3], fill=(250, 200, 20, 255), outline=(20, 20, 20, 255))
    # Inner border
    p1_in = (tri_x, tri_y - tri_r + 14)
    p2_in = (tri_x + int(tri_r * 1.15) - 12, tri_y + int(tri_r * 0.75) - 8)
    p3_in = (tri_x - int(tri_r * 1.15) + 12, tri_y + int(tri_r * 0.75) - 8)
    draw.polygon([p1_in, p2_in, p3_in], outline=(20, 20, 20, 255), width=6)

    # Flash lightning bolt symbol inside triangle
    bolt = [
        (tri_x + 10, tri_y - 65),
        (tri_x - 30, tri_y + 10),
        (tri_x + 5,  tri_y + 10),
        (tri_x - 12, tri_y + 70),
        (tri_x + 35, tri_y - 5),
        (tri_x + 2,  tri_y - 5)
    ]
    draw.polygon(bolt, fill=(20, 20, 20, 255))

    # Product Brand & Specification Badges
    draw.text((230, 600), "SEC-SOUNDER 350-X", fill=(20, 30, 45, 255), font=t_lg)
    draw.text((150, 665), "115dB TWIN PIEZO & HIGH-INTENSITY XENON BEACON", fill=(70, 85, 105, 255), font=t_sm)
    draw.text((250, 710), "GRADE 3 ENVIRONMENTAL CLASS IV", fill=(100, 115, 135, 255), font=f_md)

    # Dual Tamper / System Status Indicators
    draw.rectangle([120, 780, 980, 890], fill=(225, 230, 238, 255), outline=(180, 190, 205, 255), width=2)
    # Left: SYS OK (Green)
    draw.ellipse([160, 810, 210, 860], fill=(35, 210, 65, 255), outline=(20, 140, 40, 255), width=3)
    draw.ellipse([175, 825, 195, 845], fill=(180, 255, 190, 255))
    draw.text((230, 822), "SYSTEM ARMED / OK", fill=(25, 35, 45, 255), font=t_sm)
    # Right: TAMPER / ALARM (Red)
    draw.ellipse([610, 810, 660, 860], fill=(235, 35, 35, 255), outline=(160, 20, 20, 255), width=3)
    draw.ellipse([625, 825, 645, 845], fill=(255, 180, 180, 255))
    draw.text((680, 822), "TAMPER PROTECTED", fill=(25, 35, 45, 255), font=t_sm)

    # Bottom Security Accent Navy Band
    draw.rectangle([0, 960, 1100, 1100], fill=(18, 35, 68, 255))
    draw.line([(0, 960), (1100, 960)], fill=(240, 180, 20, 255), width=5)
    draw.text((160, 1010), "ACTIVE ALARM SURVEILLANCE NETWORK", fill=(255, 255, 255, 255), font=t_md)

    # =========================================================================
    # ZONE 2: SPEAKER GRILLE ACOUSTIC PERFORATED PATTERN (X: 1140..2048, Y: 0..900)
    # =========================================================================
    draw.rectangle([1140, 0, 2048, 900], fill=(16, 18, 22, 255))
    # Sound perforation mesh matrix
    for gy in range(40, 860, 32):
        for gx in range(1180, 2020, 32):
            shift = 16 if (gy // 32) % 2 == 1 else 0
            px = gx + shift
            if px < 2010:
                draw.ellipse([px - 8, gy - 8, px + 8, gy + 8], fill=(6, 8, 10, 255), outline=(45, 52, 62, 255), width=2)
                draw.ellipse([px - 4, gy - 4, px + 4, gy + 4], fill=(0, 0, 0, 255))
    # Louver shadow lines
    for ly in range(100, 800, 160):
        draw.rectangle([1140, ly, 2048, ly + 25], fill=(10, 12, 15, 255))
        draw.line([(1140, ly + 25), (2048, ly + 25)], fill=(65, 75, 90, 255), width=2)

    # =========================================================================
    # ZONE 3: TECHNICAL RATING & COMPLIANCE LABEL (X: 0..1200, Y: 1140..1700)
    # =========================================================================
    draw.rectangle([0, 1140, 1200, 1700], fill=(230, 235, 240, 255))
    draw.rectangle([15, 1155, 1185, 1685], fill=(242, 245, 250, 255), outline=(50, 60, 75, 255), width=3)

    # Header
    draw.rectangle([25, 1165, 1175, 1250], fill=(24, 32, 45, 255))
    draw.text((45, 1180), "INDUSTRIAL SECURITY SOUNDER & STROBE BEACON", fill=(255, 255, 255, 255), font=t_md)
    draw.text((45, 1220), "MODEL: SEC-ALM-350X  |  GRADE 3 EN 50131-4", fill=(180, 200, 225, 255), font=f_sm)

    # Specs table
    specs = [
        "OPERATING VOLTAGE: 9.0 - 15.0 VDC (NOMINAL 12V DC)",
        "CURRENT DRAW: 25mA STANDBY  |  350mA FULL ALARM",
        "ACOUSTIC OUTPUT: 115 dB(A) @ 1 METRE (DUAL PIEZO)",
        "STROBE BEACON: 1W XENON FLASH TUBE @ 1Hz (60 FPM)",
        "ENVIRONMENTAL: IP65 WEATHERPROOF / UV RESISTANT",
        "BACKUP BATTERY: 7.2V 250mAh Ni-MH RECHARGEABLE"
    ]
    for i, sp in enumerate(specs):
        sy = 1275 + i * 42
        draw.text((45, sy), sp, fill=(20, 25, 35, 255), font=f_sm)

    # Barcode
    draw.rectangle([45, 1540, 520, 1630], fill=(255, 255, 255, 255), outline=(80, 90, 100, 255), width=2)
    for bx in range(65, 500, 7):
        if (bx * 13) % 17 < 11:
            draw.line([(bx, 1550), (bx, 1605)], fill=(15, 20, 30, 255), width=4)
    draw.text((160, 1610), "*ALM202688941S*", fill=(20, 25, 35, 255), font=f_xs)

    # Certification logos
    certs = ["CE", "FCC", "UKCA", "RoHS", "WEEE", "UL"]
    for i, c in enumerate(certs):
        cx = 620 + (i % 3) * 180
        cy = 1540 + (i // 3) * 55
        draw.rectangle([cx, cy, cx + 150, cy + 45], fill=(225, 230, 240, 255), outline=(70, 80, 95, 255), width=2)
        draw.text((cx + 35, cy + 10), c, fill=(20, 25, 35, 255), font=t_sm)

    # =========================================================================
    # ZONE 4: FRESNEL PRISMS & REFLECTOR CHROME (X: 1220..2048, Y: 920..1700)
    # =========================================================================
    draw.rectangle([1220, 920, 2048, 1700], fill=(160, 25, 25, 255))
    for fx in range(1220, 2048, 16):
        draw.line([(fx, 920), (fx, 1700)], fill=(220, 45, 45, 255), width=6)
        draw.line([(fx + 8, 920), (fx + 8, 1700)], fill=(120, 15, 15, 255), width=6)
    # Specular highlight streak
    draw.line([(1220, 1310), (2048, 1310)], fill=(255, 180, 180, 255), width=12)

    # =========================================================================
    # ZONE 5: ISOLATED NEUTRAL BUFFERS (Guaranteed ZERO text bleed!)
    # =========================================================================
    # 5.1 Pure White Casing Buffer: (X: 1980..2048, Y: 1980..2048) -> UV (0.967, 0.000, 1.000, 0.033) in Blender
    draw.rectangle([1980, 1980, 2048, 2048], fill=(238, 242, 246, 255))
    # 5.2 Dark Anthracite Metal Buffer: (X: 1980..2048, Y: 1900..1968)
    draw.rectangle([1980, 1900, 2048, 1968], fill=(32, 36, 42, 255))

    img.save(out_path, format="PNG")
    print(f"[INFO] Generated 2048x2048 T_Security_Atlas.png: {out_path}")
    return out_path


# Normalized UV Coordinate Constants (u0, v0, u1, v1 in Blender UV where (0,0) is bottom-left)
# Zone 1: X: 0..1100 -> u: [0.000, 0.537], Y: 0..1100 -> v: [0.463, 1.000]
UV_SIREN_FASCIA  = (0.000, 0.463, 0.537, 1.000)
# Zone 2: X: 1140..2048 -> u: [0.557, 1.000], Y: 0..900 -> v: [0.561, 1.000]
UV_GRILLE_MESH   = (0.557, 0.561, 1.000, 1.000)
# Zone 3: X: 0..1200 -> u: [0.000, 0.586], Y: 1140..1700 -> v: [0.170, 0.443]
UV_RATING_PLATE  = (0.000, 0.170, 0.586, 0.443)
# Zone 4: X: 1220..2048 -> u: [0.596, 1.000], Y: 920..1700 -> v: [0.170, 0.551]
UV_FRESNEL_LENS  = (0.596, 0.170, 1.000, 0.551)
# Zone 5.1 White Casing Neutral: X: 1980..2048, Y: 1980..2048 -> v: [0.000, 0.033]
UV_NEUTRAL_WHITE = (0.967, 0.000, 1.000, 0.033)
# Zone 5.2 Dark Metal Neutral: X: 1980..2048, Y: 1900..1968 -> v: [0.039, 0.072]
UV_NEUTRAL_DARK  = (0.967, 0.039, 1.000, 0.072)


# -------------------------------------------------------------
# Material Factory
# -------------------------------------------------------------

def create_or_get_materials():
    """Create Slot 0: M_Security_Atlas, Slot 1: M_Transparent, Slot 2: M_Emission."""
    atlas_path = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
    if not os.path.exists(atlas_path):
        import subprocess
        tex_script = os.path.join(SCRIPT_DIR, "generate_textures.py")
        if os.path.exists(tex_script):
            subprocess.run(["python", tex_script], check=True)

    # Slot 0: M_Security_Atlas
    mat_atlas = bpy.data.materials.get("M_Security_Atlas")
    if not mat_atlas:
        mat_atlas = bpy.data.materials.new("M_Security_Atlas")
    mat_atlas.use_nodes = True
    nodes0 = mat_atlas.node_tree.nodes
    nodes0.clear()
    bsdf0 = nodes0.new(type="ShaderNodeBsdfPrincipled")
    bsdf0.location = (300, 300)
    bsdf0.inputs["Roughness"].default_value = 0.35
    bsdf0.inputs["Specular IOR Level"].default_value = 0.50

    tex0 = nodes0.new(type="ShaderNodeTexImage")
    tex0.location = (0, 300)
    if os.path.exists(atlas_path):
        img0 = bpy.data.images.load(atlas_path, check_existing=True)
        tex0.image = img0
    mat_atlas.node_tree.links.new(tex0.outputs["Color"], bsdf0.inputs["Base Color"])

    out0 = nodes0.new(type="ShaderNodeOutputMaterial")
    out0.location = (550, 300)
    mat_atlas.node_tree.links.new(bsdf0.outputs["BSDF"], out0.inputs["Surface"])

    # Slot 1: M_Transparent (Translucent emergency red Fresnel strobe dome)
    mat_trans = bpy.data.materials.get("M_Transparent")
    if not mat_trans:
        mat_trans = bpy.data.materials.new("M_Transparent")
    mat_trans.use_nodes = True
    nodes1 = mat_trans.node_tree.nodes
    nodes1.clear()
    bsdf1 = nodes1.new(type="ShaderNodeBsdfPrincipled")
    bsdf1.location = (300, 300)
    # Vibrant emergency red
    bsdf1.inputs["Base Color"].default_value = (0.92, 0.08, 0.05, 1.0)
    bsdf1.inputs["Roughness"].default_value = 0.12
    bsdf1.inputs["Transmission Weight"].default_value = 0.85
    bsdf1.inputs["Alpha"].default_value = 0.55
    bsdf1.inputs["IOR"].default_value = 1.54
    # Subtle inner Fresnel emission glow
    if "Emission Color" in bsdf1.inputs:
        bsdf1.inputs["Emission Color"].default_value = (0.95, 0.15, 0.05, 1.0)
        bsdf1.inputs["Emission Strength"].default_value = 0.40

    out1 = nodes1.new(type="ShaderNodeOutputMaterial")
    out1.location = (550, 300)
    mat_trans.node_tree.links.new(bsdf1.outputs["BSDF"], out1.inputs["Surface"])

    # Blend modes for transparency
    mat_trans.blend_method = 'BLEND' if hasattr(mat_trans, 'blend_method') else 'HASHED'
    if hasattr(mat_trans, 'shadow_method'):
        mat_trans.shadow_method = 'HASHED'

    # Slot 2: M_Emission (High-intensity xenon strobe flash tube / LED)
    mat_emiss = bpy.data.materials.get("M_Emission")
    if not mat_emiss:
        mat_emiss = bpy.data.materials.new("M_Emission")
    mat_emiss.use_nodes = True
    nodes2 = mat_emiss.node_tree.nodes
    nodes2.clear()
    bsdf2 = nodes2.new(type="ShaderNodeBsdfPrincipled")
    bsdf2.location = (300, 300)
    bsdf2.inputs["Base Color"].default_value = (1.0, 0.95, 0.88, 1.0)
    if "Emission Color" in bsdf2.inputs:
        bsdf2.inputs["Emission Color"].default_value = (1.0, 0.96, 0.85, 1.0)
        bsdf2.inputs["Emission Strength"].default_value = 8.0

    out2 = nodes2.new(type="ShaderNodeOutputMaterial")
    out2.location = (550, 300)
    mat_emiss.node_tree.links.new(bsdf2.outputs["BSDF"], out2.inputs["Surface"])

    return [mat_atlas, mat_trans, mat_emiss]


def attach_standard_materials(mesh, materials):
    """Ensure standard material slot ordering: 0: Atlas, 1: Transparent, 2: Emission."""
    mesh.materials.clear()
    for mat in materials:
        mesh.materials.append(mat)


# -------------------------------------------------------------
# UV Mapping Utilities
# -------------------------------------------------------------

def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    """Map face planar bounds to UV rectangle [u0, v0, u1, v1]."""
    u0, v0, u1, v1 = uv_rect
    uv_lay = bm.loops.layers.uv.verify()

    n = len(face.loops)
    if n == 0:
        return

    pts = [loop.vert.co for loop in face.loops]
    norm = face.normal

    if abs(norm.y) >= abs(norm.x) and abs(norm.y) >= abs(norm.z):
        xs = [p.x for p in pts]
        ys = [p.z for p in pts]
    elif abs(norm.x) >= abs(norm.y) and abs(norm.x) >= abs(norm.z):
        xs = [p.y for p in pts]
        ys = [p.z for p in pts]
    else:
        xs = [p.x for p in pts]
        ys = [p.y for p in pts]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    dx = max_x - min_x if max_x > min_x else 1.0
    dy = max_y - min_y if max_y > min_y else 1.0

    for i, loop in enumerate(face.loops):
        fu = (xs[i] - min_x) / dx
        fv = (ys[i] - min_y) / dy
        if flip_u:
            fu = 1.0 - fu
        if flip_v:
            fv = 1.0 - fv
        u = u0 + fu * (u1 - u0)
        v = v0 + fv * (v1 - v0)
        loop[uv_lay].uv = (u, v)


def set_fascia_continuous_uv(bm, face, uv_rect, x_bounds, z_bounds):
    """Continuous projection of front siren fascia graphics."""
    u0, v0, u1, v1 = uv_rect
    xmin, xmax = x_bounds
    zmin, zmax = z_bounds
    dx = xmax - xmin if xmax > xmin else 1.0
    dz = zmax - zmin if zmax > zmin else 1.0
    uv_lay = bm.loops.layers.uv.verify()

    for loop in face.loops:
        x = loop.vert.co.x
        z = loop.vert.co.z
        # When viewed from +Y looking towards wall (-Y): +X is screen-left, -X is screen-right.
        # So fu goes from 0 at xmax (+X) to 1 at xmin (-X) for natural un-mirrored reading!
        fu = (xmax - x) / dx
        fv = (z - zmin) / dz
        u = u0 + fu * (u1 - u0)
        v = v0 + fv * (v1 - v0)
        loop[uv_lay].uv = (u, v)


def mark_sharp_edges_by_angle(bm, threshold_deg=35.0):
    """Mark edges sharp if face angle exceeds threshold for crisp hard-surface normals."""
    rad = math.radians(threshold_deg)
    for edge in bm.edges:
        if len(edge.link_faces) == 2:
            angle = edge.link_faces[0].normal.angle(edge.link_faces[1].normal, 0.0)
            if angle > rad:
                edge.smooth = False
            else:
                edge.smooth = True
        else:
            edge.smooth = False


# -------------------------------------------------------------
# High-Density Low-Poly Mesh Builders
# -------------------------------------------------------------

def build_mount_plate_mesh(mesh, materials):
    """
    Build Mount_Plate:
    Rigid wall-mounting chassis plate with corner screw flanges and rear tamper pad.
    Flush against wall at Y = 0.000 to 0.008m.
    Width: 190mm (X: -0.095 .. +0.095), Height: 290mm (Z: -0.145 .. +0.145).
    Material: M_Security_Atlas (Slot 0).
    Tris count: 12 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    hw = 0.088
    hh = 0.138
    d = 0.008

    # 8 corner vertices
    v_b_bl = bm.verts.new(Vector((-hw, 0.0, -hh)))
    v_b_br = bm.verts.new(Vector(( hw, 0.0, -hh)))
    v_f_br = bm.verts.new(Vector(( hw, d,   -hh)))
    v_f_bl = bm.verts.new(Vector((-hw, d,   -hh)))

    v_b_tl = bm.verts.new(Vector((-hw, 0.0,  hh)))
    v_b_tr = bm.verts.new(Vector(( hw, 0.0,  hh)))
    v_f_tr = bm.verts.new(Vector(( hw, d,    hh)))
    v_f_tl = bm.verts.new(Vector((-hw, d,    hh)))

    # Faces
    f_back  = bm.faces.new([v_b_bl, v_b_br, v_b_tr, v_b_tl]) # Back to wall (-Y)
    f_front = bm.faces.new([v_f_bl, v_f_tl, v_f_tr, v_f_br]) # Front facing room (+Y)
    f_bot   = bm.faces.new([v_b_bl, v_f_bl, v_f_br, v_b_br])
    f_top   = bm.faces.new([v_b_tl, v_b_tr, v_f_tr, v_f_tl])
    f_left  = bm.faces.new([v_b_bl, v_b_tl, v_f_tl, v_f_bl])
    f_right = bm.faces.new([v_b_br, v_f_br, v_f_tr, v_b_tr])

    for f in [f_front, f_bot, f_top, f_left, f_right]:
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_NEUTRAL_DARK)

    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_RATING_PLATE, flip_u=True)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_siren_housing_mesh(mesh, materials):
    """
    Build Siren_Housing:
    Streamlined aerodynamic security sounder casing with upper graphics fascia,
    lower recessed acoustic grille bay, and top beacon saddle collar.
    Width: 180mm, Height: 280mm, Depth: 72mm (Y: 0.008 .. 0.076).
    Material: M_Security_Atlas (Slot 0).
    Tris count: ~90 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # Base rear perimeter against mount plate (Y = 0.008)
    hw_r = 0.090
    hz_r = 0.140
    y_r = 0.008

    # Front face bounds (Y = 0.074)
    hw_f = 0.076
    y_f = 0.074

    # Top beacon mounting saddle (Z: 0.125 .. 0.140, Y: 0.015 .. 0.065)
    # Upper fascia (Z: 0.000 .. 0.115)
    # Lower acoustic recess chamber (Z: -0.115 .. -0.010, recessed to Y = 0.045)
    # Bottom chin (Z: -0.140 .. -0.125)

    # 1. Rear outer perimeter vertices
    v_r_bl = bm.verts.new(Vector((-hw_r, y_r, -hz_r)))
    v_r_br = bm.verts.new(Vector(( hw_r, y_r, -hz_r)))
    v_r_mr = bm.verts.new(Vector(( hw_r, y_r,  0.000)))
    v_r_ml = bm.verts.new(Vector((-hw_r, y_r,  0.000)))
    v_r_tr = bm.verts.new(Vector(( hw_r, y_r,  hz_r)))
    v_r_tl = bm.verts.new(Vector((-hw_r, y_r,  hz_r)))

    # 2. Front fascia vertices (Upper Graphic Section)
    z_mid = -0.005
    z_top_fascia = 0.115
    v_f_fascia_bl = bm.verts.new(Vector((-hw_f, y_f, z_mid)))
    v_f_fascia_br = bm.verts.new(Vector(( hw_f, y_f, z_mid)))
    v_f_fascia_tr = bm.verts.new(Vector(( hw_f, y_f, z_top_fascia)))
    v_f_fascia_tl = bm.verts.new(Vector((-hw_f, y_f, z_top_fascia)))

    # Main Front Warning Fascia Face (Facing +Y into room)
    f_fascia = bm.faces.new([v_f_fascia_bl, v_f_fascia_tl, v_f_fascia_tr, v_f_fascia_br])
    f_fascia.material_index = 0
    set_fascia_continuous_uv(bm, f_fascia, UV_SIREN_FASCIA, (-hw_f, hw_f), (z_mid, z_top_fascia))

    # 3. Top Strobe Beacon Saddle Platform (Z = 0.130, Y: 0.015 .. 0.065)
    sw = 0.040
    y_sad_b = 0.015
    y_sad_f = 0.062
    z_sad = 0.130
    v_sad_bl = bm.verts.new(Vector((-sw, y_sad_b, z_sad)))
    v_sad_br = bm.verts.new(Vector(( sw, y_sad_b, z_sad)))
    v_sad_fr = bm.verts.new(Vector(( sw, y_sad_f, z_sad)))
    v_sad_fl = bm.verts.new(Vector((-sw, y_sad_f, z_sad)))

    f_saddle = bm.faces.new([v_sad_bl, v_sad_fl, v_sad_fr, v_sad_br])
    f_saddle.material_index = 0
    set_face_uv_rect(bm, f_saddle, UV_NEUTRAL_DARK)

    # Transition from Fascia Top to Saddle Front
    f_fas_to_sad = bm.faces.new([v_f_fascia_tl, v_sad_fl, v_sad_fr, v_f_fascia_tr])
    f_fas_to_sad.material_index = 0
    set_face_uv_rect(bm, f_fas_to_sad, UV_NEUTRAL_WHITE)

    # Crown slope from Saddle to Rear Top
    f_crown_top = bm.faces.new([v_sad_bl, v_sad_br, v_r_tr, v_r_tl])
    f_crown_top.material_index = 0
    set_face_uv_rect(bm, f_crown_top, UV_NEUTRAL_WHITE)

    # Left & Right Top Shoulder Caps (Sealing the top of the housing)
    f_shldr_l = bm.faces.new([v_r_tl, v_f_fascia_tl, v_sad_fl, v_sad_bl])
    f_shldr_l.material_index = 0
    set_face_uv_rect(bm, f_shldr_l, UV_NEUTRAL_WHITE)

    f_shldr_r = bm.faces.new([v_r_tr, v_sad_br, v_sad_fr, v_f_fascia_tr])
    f_shldr_r.material_index = 0
    set_face_uv_rect(bm, f_shldr_r, UV_NEUTRAL_WHITE)

    # 4. Lower Acoustic Chamber Cavity (Recessed Bay)
    # Recess opening on front face: X: [-0.065, 0.065], Z: [-0.115, -0.012]
    gw = 0.065
    z_grille_top = -0.012
    z_grille_bot = -0.115
    y_cav_d = 0.045 # 30mm deep recessed socket

    # Cavity outer rim on front face (Y = 0.074)
    v_rim_tl = bm.verts.new(Vector((-gw, y_f, z_grille_top)))
    v_rim_tr = bm.verts.new(Vector(( gw, y_f, z_grille_top)))
    v_rim_br = bm.verts.new(Vector(( gw, y_f, z_grille_bot)))
    v_rim_bl = bm.verts.new(Vector((-gw, y_f, z_grille_bot)))

    # Cavity inner bed vertices (Y = 0.045)
    v_cav_tl = bm.verts.new(Vector((-gw, y_cav_d, z_grille_top)))
    v_cav_tr = bm.verts.new(Vector(( gw, y_cav_d, z_grille_top)))
    v_cav_br = bm.verts.new(Vector(( gw, y_cav_d, z_grille_bot)))
    v_cav_bl = bm.verts.new(Vector((-gw, y_cav_d, z_grille_bot)))

    # Cavity bed face (acoustic baffle backing, Facing +Y into room)
    f_cav_bed = bm.faces.new([v_cav_bl, v_cav_tl, v_cav_tr, v_cav_br])
    f_cav_bed.material_index = 0
    set_face_uv_rect(bm, f_cav_bed, UV_GRILLE_MESH)

    # Cavity 4 inner walls
    f_cw_top = bm.faces.new([v_rim_tl, v_cav_tl, v_cav_tr, v_rim_tr]); f_cw_top.material_index = 0; set_face_uv_rect(bm, f_cw_top, UV_NEUTRAL_DARK)
    f_cw_bot = bm.faces.new([v_rim_bl, v_rim_br, v_cav_br, v_cav_bl]); f_cw_bot.material_index = 0; set_face_uv_rect(bm, f_cw_bot, UV_NEUTRAL_DARK)
    f_cw_l   = bm.faces.new([v_rim_bl, v_cav_bl, v_cav_tl, v_rim_tl]); f_cw_l.material_index = 0; set_face_uv_rect(bm, f_cw_l, UV_NEUTRAL_DARK)
    f_cw_r   = bm.faces.new([v_rim_br, v_rim_tr, v_cav_tr, v_cav_br]); f_cw_r.material_index = 0; set_face_uv_rect(bm, f_cw_r, UV_NEUTRAL_DARK)

    # Front framing around cavity
    # Divider between Fascia and Grille Cavity (Facing +Y into room)
    f_div = bm.faces.new([v_rim_tl, v_rim_tr, v_f_fascia_br, v_f_fascia_bl])
    f_div.material_index = 0
    set_face_uv_rect(bm, f_div, UV_NEUTRAL_WHITE)

    # Front left / right cheek frames (Facing +Y into room)
    v_f_chin_l = bm.verts.new(Vector((-hw_f, y_f, z_grille_bot)))
    v_f_chin_r = bm.verts.new(Vector(( hw_f, y_f, z_grille_bot)))
    f_chk_l = bm.faces.new([v_f_chin_l, v_rim_bl, v_rim_tl, v_f_fascia_bl])
    f_chk_l.material_index = 0; set_face_uv_rect(bm, f_chk_l, UV_NEUTRAL_WHITE)
    f_chk_r = bm.faces.new([v_f_chin_r, v_f_fascia_br, v_rim_tr, v_rim_br])
    f_chk_r.material_index = 0; set_face_uv_rect(bm, f_chk_r, UV_NEUTRAL_WHITE)

    # Lower Chin Bevel (Z: -0.140 .. -0.115)
    v_f_bot_l = bm.verts.new(Vector((-hw_f * 0.9, y_f * 0.7, -hz_r)))
    v_f_bot_r = bm.verts.new(Vector(( hw_f * 0.9, y_f * 0.7, -hz_r)))
    f_chin_mid = bm.faces.new([v_f_bot_l, v_f_bot_r, v_rim_br, v_rim_bl])
    f_chin_mid.material_index = 0; set_face_uv_rect(bm, f_chin_mid, UV_NEUTRAL_WHITE)

    f_chin_bl = bm.faces.new([v_f_bot_l, v_f_chin_l, v_rim_bl])
    f_chin_bl.material_index = 0; set_face_uv_rect(bm, f_chin_bl, UV_NEUTRAL_WHITE)
    f_chin_br = bm.faces.new([v_f_bot_r, v_rim_br, v_f_chin_r])
    f_chin_br.material_index = 0; set_face_uv_rect(bm, f_chin_br, UV_NEUTRAL_WHITE)

    # Bottom enclosure closure face to rear
    f_bot_close = bm.faces.new([v_r_bl, v_f_bot_l, v_f_bot_r, v_r_br])
    f_bot_close.material_index = 0; set_face_uv_rect(bm, f_bot_close, UV_NEUTRAL_WHITE)

    # 5. Left and Right Outer Beveled Side Walls
    # Left Wall
    f_side_l1 = bm.faces.new([v_r_bl, v_r_ml, v_f_chin_l, v_f_bot_l])
    f_side_l2 = bm.faces.new([v_r_ml, v_r_tl, v_f_fascia_tl, v_f_fascia_bl, v_f_chin_l])
    for f in [f_side_l1, f_side_l2]:
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_NEUTRAL_WHITE)

    # Right Wall (with technical rating plate sticker on side)
    f_side_r1 = bm.faces.new([v_r_br, v_f_bot_r, v_f_chin_r, v_r_mr])
    f_side_r2 = bm.faces.new([v_r_mr, v_f_chin_r, v_f_fascia_br, v_f_fascia_tr, v_r_tr])
    f_side_r1.material_index = 0; set_face_uv_rect(bm, f_side_r1, UV_NEUTRAL_WHITE)
    f_side_r2.material_index = 0; set_face_uv_rect(bm, f_side_r2, UV_NEUTRAL_WHITE)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_speaker_grille_mesh(mesh, materials):
    """
    Build Speaker_Grille:
    Four downward-angled acoustic weather-louvers and perforated sound chamber.
    Sits inside acoustic bay (X: -0.063 .. 0.063, Z: -0.112 .. -0.015, Y: 0.046 .. 0.076).
    Material: M_Security_Atlas (Slot 0).
    Tris count: ~48 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    gw = 0.062
    y_in = 0.048
    y_out = 0.076

    # 4 horizontal weather louvers angled down at 35 degrees
    z_slots = [
        (-0.024, -0.038),
        (-0.046, -0.060),
        (-0.068, -0.082),
        (-0.090, -0.104)
    ]

    for z_top, z_bot in z_slots:
        # Louver upper facet (slanted outward and down)
        v_in_l  = bm.verts.new(Vector((-gw, y_in,  z_top)))
        v_in_r  = bm.verts.new(Vector(( gw, y_in,  z_top)))
        v_out_r = bm.verts.new(Vector(( gw, y_out, z_bot)))
        v_out_l = bm.verts.new(Vector((-gw, y_out, z_bot)))

        # Louver lower return lip (horizontal return inward)
        v_ret_r = bm.verts.new(Vector(( gw, y_in + 0.006, z_bot - 0.003)))
        v_ret_l = bm.verts.new(Vector((-gw, y_in + 0.006, z_bot - 0.003)))

        f_slant = bm.faces.new([v_out_l, v_in_l, v_in_r, v_out_r])
        f_slant.material_index = 0
        set_face_uv_rect(bm, f_slant, UV_NEUTRAL_DARK)

        f_ret = bm.faces.new([v_ret_l, v_out_l, v_out_r, v_ret_r])
        f_ret.material_index = 0
        set_face_uv_rect(bm, f_ret, UV_NEUTRAL_DARK)

        # Side caps
        f_cap_l = bm.faces.new([v_in_l, v_out_l, v_ret_l])
        f_cap_r = bm.faces.new([v_in_r, v_ret_r, v_out_r])
        f_cap_l.material_index = 0; set_face_uv_rect(bm, f_cap_l, UV_NEUTRAL_DARK)
        f_cap_r.material_index = 0; set_face_uv_rect(bm, f_cap_r, UV_NEUTRAL_DARK)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_beacon_base_mesh(mesh, materials):
    """
    Build Beacon_Base:
    Stepped circular strobe mounting socket collar with integrated central xenon flasher tube.
    Mounted on housing top saddle at (X: 0.000, Y: 0.040, Z: 0.130).
    Material: M_Security_Atlas (Slot 0) for collar, M_Emission (Slot 2) for strobe flash bulb.
    Tris count: ~60 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # Outer collar rings
    rings = [
        (0.035, 0.000), # Base sitting flush on housing saddle
        (0.033, 0.006), # Outer bezel rim
        (0.029, 0.010)  # Inner lens seal shoulder
    ]

    ring_verts = []
    for r, z in rings:
        v_layer = []
        for a in range(10):
            ang = 2.0 * math.pi * a / 10.0
            vx = r * math.cos(ang)
            vy = r * math.sin(ang)
            v_layer.append(bm.verts.new(Vector((vx, vy, z))))
        ring_verts.append(v_layer)

    for rg in range(len(rings) - 1):
        v1 = ring_verts[rg]
        v2 = ring_verts[rg + 1]
        for a in range(10):
            a_n = (a + 1) % 10
            f_col = bm.faces.new([v1[a], v1[a_n], v2[a_n], v2[a]])
            f_col.material_index = 0
            set_face_uv_rect(bm, f_col, UV_NEUTRAL_DARK)

    # Central Xenon Strobe Flash Bulb Core (Slot 2: M_Emission)
    rb = 0.009
    z_b0 = 0.010
    z_b1 = 0.028

    v_bulb_bot = []
    v_bulb_top = []
    for a in range(8):
        ang = 2.0 * math.pi * a / 8.0
        vx = rb * math.cos(ang)
        vy = rb * math.sin(ang)
        v_bulb_bot.append(bm.verts.new(Vector((vx, vy, z_b0))))
        v_bulb_top.append(bm.verts.new(Vector((vx, vy, z_b1))))

    for a in range(8):
        a_n = (a + 1) % 8
        f_b = bm.faces.new([v_bulb_bot[a], v_bulb_bot[a_n], v_bulb_top[a_n], v_bulb_top[a]])
        f_b.material_index = 2 # M_Emission
        set_face_uv_rect(bm, f_b, (0.0, 0.0, 1.0, 1.0))

    # Top apex of xenon flash tube
    v_apex = bm.verts.new(Vector((0.0, 0.0, z_b1 + 0.003)))
    for a in range(8):
        a_n = (a + 1) % 8
        f_cap = bm.faces.new([v_bulb_top[a], v_bulb_top[a_n], v_apex])
        f_cap.material_index = 2 # M_Emission
        set_face_uv_rect(bm, f_cap, (0.0, 0.0, 1.0, 1.0))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


def build_beacon_lens_mesh(mesh, materials):
    """
    Build Beacon_Lens:
    Translucent fluted Fresnel emergency strobe dome covering the flasher bulb.
    Easily selectable in Unity for emergency strobe flashing animations.
    Origin at local (0, 0, 0) relative to Beacon_Base.
    Material: M_Transparent (Slot 1).
    Tris count: ~50 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    profile = [
        (0.029, 0.008), # Overlaps base seal collar
        (0.029, 0.036), # Fluted vertical Fresnel body
        (0.023, 0.045), # Upper crown taper
    ]

    ring_verts = []
    for r, z in profile:
        v_layer = []
        for a in range(10):
            ang = 2.0 * math.pi * a / 10.0
            vx = r * math.cos(ang)
            vy = r * math.sin(ang)
            v_layer.append(bm.verts.new(Vector((vx, vy, z))))
        ring_verts.append(v_layer)

    for p in range(len(profile) - 1):
        v1 = ring_verts[p]
        v2 = ring_verts[p + 1]
        for a in range(10):
            a_n = (a + 1) % 10
            f_lens = bm.faces.new([v1[a], v1[a_n], v2[a_n], v2[a]])
            f_lens.material_index = 1 # M_Transparent
            set_face_uv_rect(bm, f_lens, UV_FRESNEL_LENS)

    # Top dome cap apex
    v_crown = ring_verts[-1]
    v_top_apex = bm.verts.new(Vector((0.0, 0.0, 0.050)))
    for a in range(10):
        a_n = (a + 1) % 10
        f_top = bm.faces.new([v_crown[a], v_crown[a_n], v_top_apex])
        f_top.material_index = 1 # M_Transparent
        set_face_uv_rect(bm, f_top, UV_FRESNEL_LENS)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.to_mesh(mesh)
    bm.free()


# -------------------------------------------------------------
# Assembly, FBX Export and Automated QA Pipeline
# -------------------------------------------------------------

def assemble_and_export():
    """Build full asset hierarchy, export FBX and run automated QA."""
    # Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0

    print("[INFO] Creating textures and materials...")
    materials = create_or_get_materials()

    # 1. Root Empty: SEC_Alarm_Siren_Beacon at (0, 0, 0) flush on wall plane
    root_empty = bpy.data.objects.new("SEC_Alarm_Siren_Beacon", None)
    root_empty.empty_display_type = 'PLAIN_AXES'
    root_empty.empty_display_size = 0.15
    root_empty.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_empty)

    # 2. Mount_Plate (child of Root)
    mesh_mount = bpy.data.meshes.new("Mount_Plate")
    obj_mount = bpy.data.objects.new("Mount_Plate", mesh_mount)
    build_mount_plate_mesh(mesh_mount, materials)
    bpy.context.collection.objects.link(obj_mount)
    obj_mount.location = Vector((0.0, 0.0, 0.0))
    obj_mount.parent = root_empty

    # 3. Siren_Housing (child of Root)
    mesh_housing = bpy.data.meshes.new("Siren_Housing")
    obj_housing = bpy.data.objects.new("Siren_Housing", mesh_housing)
    build_siren_housing_mesh(mesh_housing, materials)
    bpy.context.collection.objects.link(obj_housing)
    obj_housing.location = Vector((0.0, 0.0, 0.0))
    obj_housing.parent = root_empty

    # 4. Speaker_Grille (child of Siren_Housing)
    mesh_grille = bpy.data.meshes.new("Speaker_Grille")
    obj_grille = bpy.data.objects.new("Speaker_Grille", mesh_grille)
    build_speaker_grille_mesh(mesh_grille, materials)
    bpy.context.collection.objects.link(obj_grille)
    obj_grille.location = Vector((0.0, 0.0, 0.0))
    obj_grille.parent = obj_housing

    # 5. Beacon_Base (child of Root)
    mesh_bbase = bpy.data.meshes.new("Beacon_Base")
    obj_bbase = bpy.data.objects.new("Beacon_Base", mesh_bbase)
    build_beacon_base_mesh(mesh_bbase, materials)
    bpy.context.collection.objects.link(obj_bbase)
    obj_bbase.location = Vector((0.000, 0.038, 0.130))
    obj_bbase.parent = root_empty

    # 6. Beacon_Lens (child of Beacon_Base)
    mesh_blens = bpy.data.meshes.new("Beacon_Lens")
    obj_blens = bpy.data.objects.new("Beacon_Lens", mesh_blens)
    build_beacon_lens_mesh(mesh_blens, materials)
    bpy.context.collection.objects.link(obj_blens)
    obj_blens.location = Vector((0.0, 0.0, 0.0))
    obj_blens.parent = obj_bbase

    bpy.context.view_layer.update()

    # Save Blend file
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Alarm_Siren_Beacon.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Saved blend file: {blend_path}")

    # Remove backup .blend1 if created
    blend1_path = blend_path + "1"
    if os.path.exists(blend1_path):
        os.remove(blend1_path)
        print(f"[INFO] Removed backup file: {blend1_path}")

    # Select all hierarchy objects for export
    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root_empty, obj_mount, obj_housing, obj_grille, obj_bbase, obj_blens]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_empty

    # Export Unity-compliant FBX
    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Alarm_Siren_Beacon.fbx")
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
    print(f"[INFO] Exported FBX: {fbx_path}")

    # Run automated QA in clean test scene
    run_automated_qa(fbx_path, blend_path)


def run_automated_qa(fbx_path, blend_path):
    """Re-import exported FBX in isolated scene and verify constraints."""
    print("\n--- RUNNING AUTOMATED QA ON EXPORTED FBX ---")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    imported_objs = bpy.context.selected_objects
    print(f"[QA] Imported objects ({len(imported_objs)}): {[o.name for o in imported_objs]}")

    mesh_objs = [o for o in imported_objs if o.type == 'MESH']
    empty_objs = [o for o in imported_objs if o.type == 'EMPTY']

    total_tris = 0
    for obj in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        tris = len(bm.faces)
        total_tris += tris
        bm.free()

    print(f"[QA] TOTAL TRIANGLES: {total_tris} (Budget limit: 350)")

    budget_limit = 350
    status = "SUCCESS"
    reasons = []

    if total_tris > budget_limit:
        status = "FAILED"
        reasons.append(f"Triangles ({total_tris}) exceeded budget limit of {budget_limit}")

    if len(mesh_objs) < 5:
        status = "FAILED"
        reasons.append(f"Expected 5 mesh components, found {len(mesh_objs)}")

    # Check root empty presence
    root_names = [o.name for o in empty_objs if "SEC_Alarm_Siren_Beacon" in o.name]
    if not root_names:
        status = "FAILED"
        reasons.append("Root object 'SEC_Alarm_Siren_Beacon' not found in imported objects")

    # Check material slot count
    all_materials = set()
    for o in mesh_objs:
        for slot in o.material_slots:
            if slot.material:
                all_materials.add(slot.material.name)

    manifest_data = {
        "SEC_Alarm_Siren_Beacon": {
            "asset_name": "SEC_Alarm_Siren_Beacon",
            "fbx_path": "exports/SEC_Alarm_Siren_Beacon.fbx",
            "blend_path": "exports/SEC_Alarm_Siren_Beacon.blend",
            "tris_count": total_tris,
            "mesh_count": len(mesh_objs),
            "empty_count": len(empty_objs),
            "materials": sorted(list(all_materials)),
            "status": status
        }
    }
    if reasons:
        manifest_data["SEC_Alarm_Siren_Beacon"]["failure_reasons"] = reasons

    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[QA] Manifest written to {manifest_path}")

    if status == "SUCCESS":
        print("[QA] ALL CHECKS PASSED SUCCESSFULLY!\n")
    else:
        print(f"[QA] VALIDATION FAILED: {reasons}\n")
        sys.exit(1)


if __name__ == "__main__":
    assemble_and_export()
