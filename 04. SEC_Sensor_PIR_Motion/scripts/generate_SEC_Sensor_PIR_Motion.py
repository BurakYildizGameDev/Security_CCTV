"""
Generate SEC_Sensor_PIR_Motion 3D Asset
High-End Industrial Wall/Corner Mounted PIR Motion Sensor for security applications.
Follows general production standards:
- Real low-poly geometry (< 220 tris)
- Metric units, Z-up Blender, Unity FBX export (Y-up)
- Full hierarchy (Base root -> Housing -> Lens & LED)
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
    """Generate high-contrast, professional 512x512 texture atlas for PIR sensor."""
    atlas_img = bpy.data.images.get("T_Security_Atlas")
    if atlas_img is None:
        atlas_img = bpy.data.images.new("T_Security_Atlas", 512, 512)

    pixels = [0.0] * (512 * 512 * 4)
    for y in range(512):
        for x in range(512):
            idx = (y * 512 + x) * 4
            if y >= 256:
                if x < 256:  # Quadrant 0: Clean Security White PIR Housing & Refined Accents
                    # Side chamfers / accent panels (x: 0..38 or 218..255) -> Dark Anthracite Accents with horizontal vents
                    if x <= 38 or x >= 218:
                        r, g, b = 0.14, 0.15, 0.18
                        # 4 horizontal cooling / acoustic vent slots
                        if (310 <= y <= 316) or (330 <= y <= 336) or (350 <= y <= 356) or (370 <= y <= 376):
                            r, g, b = 0.28, 0.31, 0.36
                    else:
                        # Clean security matte white front body
                        r, g, b = 0.94, 0.95, 0.97

                        # High-End Brand Printing directly on white casing (y: 395..425, x: 60..195)
                        # "OPTEX PIR-12M" and IR sensor waves in sleek graphite
                        if 395 <= y <= 425 and 60 <= x <= 195:
                            # Subtle recessed brand badge zone
                            if 402 <= y <= 418 and 68 <= x <= 188:
                                # Subtle cool-grey backing
                                r, g, b = 0.88, 0.90, 0.93
                                # Bold typography lettering
                                if 407 <= y <= 413 and (x % 4 in [0, 1]):
                                    r, g, b = 0.18, 0.20, 0.25
                                # IR wave logo icon at left (x: 74..86)
                                if 74 <= x <= 86 and (abs(y - 410) == abs(x - 80) // 2):
                                    r, g, b = 0.18, 0.20, 0.25

                        # Status LED bevel border ring (y: 470..495, x: 120..136)
                        if 470 <= y <= 495 and 120 <= x <= 136:
                            dist_led_slot = math.sqrt(((x - 128) * 1.5)**2 + (y - 482)**2)
                            if 10 <= dist_led_slot <= 13:
                                r, g, b = 0.72, 0.75, 0.80  # Bevel edge ring

                        # Lower chin tamper release latch icon (y: 270..284, x: 90..165)
                        elif 270 <= y <= 284 and 90 <= x <= 165:
                            r, g, b = 0.82, 0.85, 0.89
                            if y == 276:
                                r, g, b = 0.30, 0.33, 0.38
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 1: Industrial Dark Anthracite Wall/Corner Mount Base & Rubber Gasket
                    r, g, b = 0.12, 0.13, 0.15
                    # Central cable knockout grommet (center: x=384, y=384)
                    dist_ko = math.sqrt((x - 384)**2 + (y - 384)**2)
                    if dist_ko < 22:
                        r, g, b = 0.05, 0.05, 0.06
                    elif dist_ko < 28:
                        r, g, b = 0.24, 0.26, 0.30
                    # Mounting screw slots at top and bottom
                    if (y in [465, 466, 305, 306]) and 350 <= x <= 418:
                        r, g, b = 0.05, 0.05, 0.06
                    # 45-degree corner-mount alignment guides
                    if abs((x - 256) - (y - 256)) < 2 or abs((x - 256) - (512 - y)) < 2:
                        r, g, b = 0.20, 0.22, 0.25
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

            else:
                if x < 256:  # Quadrant 2: Technical Spec Label & Pyroelectric Sensor Element
                    # Upper section (y: 120..255): Wiring Diagram & Spec Label
                    if y >= 120:
                        r, g, b = 0.78, 0.80, 0.84
                        # Circuit diagram lines & terminal markings
                        if (y in [140, 180, 220, 245]) or (x in [30, 90, 160, 225]):
                            r, g, b = 0.14, 0.15, 0.18
                        # 110-degree PIR coverage pattern fan
                        dx_fan = x - 128
                        dy_fan = y - 145
                        dist_fan = math.sqrt(dx_fan**2 + dy_fan**2)
                        if 30 <= dist_fan <= 60 and dy_fan > 0 and abs(dx_fan) <= dy_fan * 1.4:
                            if int(dist_fan) % 8 < 2:
                                r, g, b = 0.20, 0.35, 0.65
                    else:
                        # Lower section (y: 0..119): Internal Pyroelectric Sensor Can (TO-5 metallic gold/silver)
                        r, g, b = 0.16, 0.17, 0.20  # PCB substrate
                        # Sensor can centered at x=128, y=60
                        dist_can = math.sqrt((x - 128)**2 + (y - 60)**2)
                        if dist_can < 42:
                            # Metallic gold / brass body
                            r, g, b = 0.88, 0.78, 0.45
                            # Circular rim highlight
                            if 38 <= dist_can <= 42 or 28 <= dist_can <= 31:
                                r, g, b = 0.98, 0.92, 0.65
                            # Central rectangular optical silicon filter window
                            if abs(x - 128) <= 16 and abs(y - 60) <= 10:
                                r, g, b = 0.08, 0.09, 0.12
                                # Dual pyroelectric sensing elements inside
                                if abs(x - 128) in [4, 5, 6, 7, 10, 11, 12, 13] and abs(y - 60) <= 7:
                                    r, g, b = 0.32, 0.36, 0.44
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 3: High-Fidelity Fresnel Optical Prism Grating Pattern
                    # Milky pearl-white optical polymer base with soft blue tint
                    r, g, b = 0.93, 0.95, 0.98
                    # 4 columns (64px wide), 3 tiers (85px high)
                    col = (x - 256) // 64
                    row = y // 85
                    col_x_center = 256 + col * 64 + 32
                    row_y_center = row * 85 + 42

                    # Distinct facet border groove lines
                    if (x - 256) % 64 in [0, 1, 62, 63] or y % 85 in [0, 1, 83, 84]:
                        r, g, b = 0.65, 0.70, 0.78  # Defined cool facet separators
                    else:
                        # Concentric Fresnel lens ridges within each zone facet
                        dist_facet_ctr = math.sqrt((x - col_x_center)**2 + (y - row_y_center)**2)
                        ring_phase = int(dist_facet_ctr) % 7
                        if ring_phase in [0, 1]:
                            r, g, b = 0.78, 0.83, 0.90  # Shadow groove
                        elif ring_phase in [2]:
                            r, g, b = 0.99, 1.00, 1.00  # Specular ridge glint
                        
                        # Bottom tier (row 0: creep zone) has dense look-down micro-faceting
                        if row == 0 and ((x + y) % 5 in [0, 1]):
                            r, g, b = 0.72, 0.78, 0.86

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
    Create the 3 standard materials required for SEC_Sensor_PIR_Motion:
    Slot 0: M_Security_Atlas
    Slot 1: M_Transparent
    Slot 2: M_Emission
    """
    mat_configs = [
        # (name, base_color, metallic, roughness, trans, emit_col, emit_str, diff_col)
        ("M_Security_Atlas", (0.94, 0.95, 0.97, 1.0), 0.05, 0.35, 0.0, (0, 0, 0, 1), 0.0, (0.94, 0.95, 0.97, 1.0)),
        ("M_Transparent", (0.94, 0.96, 0.99, 1.0), 0.02, 0.12, 0.10, (0, 0, 0, 1), 0.0, (0.94, 0.96, 0.98, 0.88)),
        ("M_Emission", (1.0, 0.04, 0.02, 1.0), 0.0, 0.20, 0.0, (1.0, 0.04, 0.02, 1.0), 12.0, (1.0, 0.08, 0.04, 1.0)),
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

            elif name == "M_Transparent":
                # Connect atlas texture so Fresnel optical prism rings & facets are rendered!
                img_node = next((n for n in tree.nodes if n.type == "ShaderNodeTexImage"), None)
                if img_node is None:
                    img_node = tree.nodes.new(type="ShaderNodeTexImage")
                    img_node.location = (-300, 200)
                img_node.image = atlas_img
                tree.links.new(img_node.outputs["Color"], bsdf.inputs["Base Color"])
                bsdf.inputs["Roughness"].default_value = roughness
                bsdf.inputs["Metallic"].default_value = metallic
                if "Alpha" in bsdf.inputs:
                    bsdf.inputs["Alpha"].default_value = 0.94
                mat.blend_method = 'BLEND'

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
    """Pre-attach materials to mesh so bmesh face material indices are preserved."""
    ordered_keys = ["M_Security_Atlas", "M_Transparent", "M_Emission"]
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


# -------------------------------------------------------------
# Mesh Builders
# -------------------------------------------------------------

def build_sensor_base_mesh(mesh, materials):
    """
    Build SEC_Sensor_PIR_Motion (Sensor_Base):
    Root object at (0, 0, 0).
    - 45-degree corner mount & flat wall mount plate at Y=0 (Y: 0.0 to 0.008)
    - Dark Anthracite base plate with high contrast against white wall/cover
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.033, 0.055
    c = 0.012
    plate_pts = [
        (sx - c, sz), (-sx + c, sz),
        (-sx, sz - c), (-sx, -sz + c),
        (-sx + c, -sz), (sx - c, -sz),
        (sx, -sz + c), (sx, sz - c)
    ]
    back_verts = [bm.verts.new(Vector((x, 0.000, z))) for x, z in plate_pts]
    front_verts = [bm.verts.new(Vector((x, 0.008, z))) for x, z in plate_pts]

    # Back face (flush against wall, mapped to spec label & wiring diagram in quadrant 2)
    f_back = bm.faces.new(list(reversed(back_verts)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, (0.05, 0.25, 0.45, 0.48))

    # Front rim face
    f_front = bm.faces.new(front_verts)
    f_front.material_index = 0
    set_face_uv_rect(bm, f_front, (0.55, 0.55, 0.95, 0.95))

    # 8 Side chamfer quads (Dark Anthracite mounting base in quadrant 1)
    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([back_verts[i], front_verts[i], front_verts[ni], back_verts[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_sensor_housing_mesh(mesh, materials):
    """
    Build Sensor_Housing:
    Origin is at (0, 0, 0) local relative to Sensor_Base.
    High-End Sculpted Industrial CCTV PIR Housing:
    - Angled top brow overhang visor (shades optics)
    - Clean Security White front faceplate
    - Printed Brand Logo ("OPTEX PIR-12M") on white casing above lens
    - Recessed vertical status LED pocket
    - Deep optical lens cavity framing the Fresnel lens
    - Authentic internal Pyroelectric sensor element visible behind lens
    - Tapered chin with tamper release notch
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    # 1. Base ring at Y=0.008 (snaps onto base plate)
    sx_r, sz_r = 0.033, 0.055
    c_r = 0.012
    rear_pts = [
        (sx_r - c_r, sz_r), (-sx_r + c_r, sz_r),
        (-sx_r, sz_r - c_r), (-sx_r, -sz_r + c_r),
        (-sx_r + c_r, -sz_r), (sx_r - c_r, -sz_r),
        (sx_r, -sz_r + c_r), (sx_r, sz_r - c_r)
    ]
    r_verts = [bm.verts.new(Vector((x, 0.008, z))) for x, z in rear_pts]

    # 2. Front Sculpted Rim at Y=0.038
    sx_f, sz_f = 0.028, 0.048
    c_f = 0.008
    front_pts = [
        (sx_f - c_f, sz_f), (-sx_f + c_f, sz_f),
        (-sx_f, sz_f - c_f), (-sx_f, -sz_f + c_f),
        (-sx_f + c_f, -sz_f), (sx_f - c_f, -sz_f),
        (sx_f, -sz_f + c_f), (sx_f, sz_f - c_f)
    ]
    # Y-depth profile: Top brow extends to Y=0.040, center to Y=0.038, chin to Y=0.035
    f_verts = []
    for i, (x, z) in enumerate(front_pts):
        if z > 0.03:
            y_proj = 0.040  # Top brow overhang
        elif z < -0.03:
            y_proj = 0.035  # Tapered chin
        else:
            y_proj = 0.038
        f_verts.append(bm.verts.new(Vector((x, y_proj, z))))

    # 8 Side faces connecting rear to front
    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([r_verts[i], f_verts[i], f_verts[ni], r_verts[ni]])
        f.material_index = 0
        if i in [2, 6]:  # Left and right side flanks -> Dark Anthracite accent vents
            set_face_uv_rect(bm, f, (0.01, 0.60, 0.07, 0.75))
        elif i in [1, 3, 5, 7]:  # Corner chamfers -> Clean security white
            set_face_uv_rect(bm, f, (0.12, 0.60, 0.40, 0.75))
        elif i == 0:  # Top visor slope -> Clean security white
            set_face_uv_rect(bm, f, (0.12, 0.60, 0.40, 0.75))
        else:  # Bottom slope -> Clean security white
            set_face_uv_rect(bm, f, (0.12, 0.60, 0.40, 0.75))

    # 3. Front Face Topology:
    # Forehead section: Z from 0.018 to sz_f (0.048)
    # Window section: Z from -0.034 to 0.018, X from -0.022 to +0.022
    # Chin section: Z from -sz_f (-0.048) to -0.034
    wx = 0.022
    wz_top = 0.018
    wz_bot = -0.034
    wy_front = 0.038
    wy_recess = 0.028

    # Forehead Vertices
    # Split forehead into Upper Brow (with Status LED) and Lower Forehead (with brand printing)
    fh_mid_z = 0.032
    fh_top_l = bm.verts.new(Vector((-wx, wy_front, fh_mid_z)))
    fh_top_r = bm.verts.new(Vector(( wx, wy_front, fh_mid_z)))
    fh_bot_l = bm.verts.new(Vector((-wx, wy_front, wz_top)))
    fh_bot_r = bm.verts.new(Vector(( wx, wy_front, wz_top)))

    # Upper Brow Face (around LED indicator) -> Pure Security White
    f_brow = bm.faces.new([f_verts[0], f_verts[1], fh_top_l, fh_top_r])
    f_brow.material_index = 0
    set_face_uv_rect(bm, f_brow, (0.12, 0.88, 0.38, 0.98))

    # Upper Brow side triangles
    f_brow_l = bm.faces.new([f_verts[1], f_verts[2], fh_top_l])
    f_brow_l.material_index = 0
    set_face_uv_rect(bm, f_brow_l, (0.12, 0.60, 0.38, 0.75))

    f_brow_r = bm.faces.new([f_verts[7], f_verts[0], fh_top_r])
    f_brow_r.material_index = 0
    set_face_uv_rect(bm, f_brow_r, (0.12, 0.60, 0.38, 0.75))

    # Lower Forehead Face (with elegant "OPTEX PIR-12M" brand print on white)
    f_badge = bm.faces.new([fh_top_r, fh_top_l, fh_bot_l, fh_bot_r])
    f_badge.material_index = 0
    set_face_uv_rect(bm, f_badge, (0.12, 0.76, 0.38, 0.84))

    # Lower Forehead side triangles
    f_badge_l = bm.faces.new([f_verts[2], fh_bot_l, fh_top_l])
    f_badge_l.material_index = 0
    set_face_uv_rect(bm, f_badge_l, (0.12, 0.60, 0.38, 0.75))

    f_badge_r = bm.faces.new([f_verts[7], fh_top_r, fh_bot_r])
    f_badge_r.material_index = 0
    set_face_uv_rect(bm, f_badge_r, (0.12, 0.60, 0.38, 0.75))

    # Lower Chin Vertices
    ch_v0 = bm.verts.new(Vector(( wx, 0.035, wz_bot)))
    ch_v1 = bm.verts.new(Vector((-wx, 0.035, wz_bot)))
    f_ch = bm.faces.new([ch_v0, ch_v1, f_verts[4], f_verts[5]])
    f_ch.material_index = 0
    set_face_uv_rect(bm, f_ch, (0.18, 0.52, 0.32, 0.56))  # Tamper release latch area

    f_chl = bm.faces.new([f_verts[3], ch_v1, f_verts[4]])
    f_chl.material_index = 0
    set_face_uv_rect(bm, f_chl, (0.12, 0.60, 0.38, 0.75))

    f_chr = bm.faces.new([ch_v0, f_verts[6], f_verts[5]])
    f_chr.material_index = 0
    set_face_uv_rect(bm, f_chr, (0.12, 0.60, 0.38, 0.75))

    # Window side jambs (Left & Right)
    f_wl = bm.faces.new([f_verts[2], f_verts[3], ch_v1, fh_bot_l])
    f_wl.material_index = 0
    set_face_uv_rect(bm, f_wl, (0.12, 0.60, 0.38, 0.75))

    f_wr = bm.faces.new([fh_bot_r, ch_v0, f_verts[6], f_verts[7]])
    f_wr.material_index = 0
    set_face_uv_rect(bm, f_wr, (0.12, 0.60, 0.38, 0.75))

    # Recessed inner step collar framing the lens window
    rw_tl = bm.verts.new(Vector((-wx, wy_recess, wz_top)))
    rw_tr = bm.verts.new(Vector(( wx, wy_recess, wz_top)))
    rw_bl = bm.verts.new(Vector((-wx, wy_recess, wz_bot)))
    rw_br = bm.verts.new(Vector(( wx, wy_recess, wz_bot)))

    f_sw_t = bm.faces.new([fh_bot_r, fh_bot_l, rw_tl, rw_tr])
    f_sw_t.material_index = 0
    set_face_uv_rect(bm, f_sw_t, (0.55, 0.55, 0.95, 0.95))

    f_sw_b = bm.faces.new([ch_v1, ch_v0, rw_br, rw_bl])
    f_sw_b.material_index = 0
    set_face_uv_rect(bm, f_sw_b, (0.55, 0.55, 0.95, 0.95))

    f_sw_l = bm.faces.new([fh_bot_l, ch_v1, rw_bl, rw_tl])
    f_sw_l.material_index = 0
    set_face_uv_rect(bm, f_sw_l, (0.55, 0.55, 0.95, 0.95))

    f_sw_r = bm.faces.new([ch_v0, fh_bot_r, rw_tr, rw_br])
    f_sw_r.material_index = 0
    set_face_uv_rect(bm, f_sw_r, (0.55, 0.55, 0.95, 0.95))

    # Window back floor (assigned to Quadrant 2: Metallic Pyroelectric Sensor TO-5 can!)
    f_w_back = bm.faces.new([rw_tl, rw_bl, rw_br, rw_tr])
    f_w_back.material_index = 0
    set_face_uv_rect(bm, f_w_back, (0.10, 0.02, 0.40, 0.22))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_fresnel_lens_mesh(mesh, materials):
    """
    Build Fresnel_Lens:
    Origin is at center of lens window (0, 0.028, -0.008) relative to Sensor_Housing.
    Authentic High-Profile Multi-Zone Convex Fresnel Shield:
    - 4 columns across X, 3 tiered detection zones across Z (12 faceted quads)
    - Bulges forward from Y=0.003 to Y=0.013 (center peak)
    - Upper zone (wide angle), Middle zone (intermediate), Lower zone (look-down creep zone)
    - Each 3D facet maps exactly to its corresponding optical Fresnel prism ring zone on T_Security_Atlas!
    - Perimeter rim walls mapped to dark anthracite rubber weather-sealing gasket!
    - Assigned to Slot 1: M_Transparent
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.verify()

    xs = [-0.021, -0.0105, 0.0, 0.0105, 0.021]
    zs = [-0.025, -0.008, 0.009, 0.025]

    grid_verts = []
    for r, z in enumerate(zs):
        row = []
        for c, x in enumerate(xs):
            norm_x = (x / 0.021)
            norm_z = (z / 0.025)
            # High-profile forward cylindrical & spherical bulge
            bulge = (1.0 - norm_x**2) * (1.0 - 0.22 * norm_z**2) * 0.010
            # Downward slant on the lower creep zone
            z_tilt = -0.002 if z < 0 else 0.000
            curv_y = 0.003 + bulge + z_tilt
            row.append(bm.verts.new(Vector((x, curv_y, z))))
        grid_verts.append(row)

    # 12 Facet Quads with exact 1-to-1 UV mapping to Quadrant 3 optical grating
    for r in range(3):
        v_low = 0.00 + r * (0.50 / 3.0)
        v_high = 0.00 + (r + 1) * (0.50 / 3.0)
        for c in range(4):
            u_low = 0.50 + c * (0.50 / 4.0)
            u_high = 0.50 + (c + 1) * (0.50 / 4.0)

            v0 = grid_verts[r][c]
            v1 = grid_verts[r][c+1]
            v2 = grid_verts[r+1][c+1]
            v3 = grid_verts[r+1][c]
            f = bm.faces.new([v0, v1, v2, v3])
            f.smooth = False  # Faceted Fresnel look catches crisp specular highlights!
            f.material_index = 1  # M_Transparent

            # Explicit 4-point UV loop mapping
            f.loops[0][uv_lay].uv = (u_low, v_low)
            f.loops[1][uv_lay].uv = (u_high, v_low)
            f.loops[2][uv_lay].uv = (u_high, v_high)
            f.loops[3][uv_lay].uv = (u_low, v_high)

    # Perimeter sealing rim walls (mapped to dark rubber weather seal)
    # Top rim
    for c in range(4):
        v0 = grid_verts[3][c]
        v1 = grid_verts[3][c+1]
        v0_b = bm.verts.new(Vector((v0.co.x, 0.001, v0.co.z)))
        v1_b = bm.verts.new(Vector((v1.co.x, 0.001, v1.co.z)))
        f = bm.faces.new([v0, v0_b, v1_b, v1])
        f.material_index = 0  # M_Security_Atlas
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # Bottom rim
    for c in range(4):
        v0 = grid_verts[0][c]
        v1 = grid_verts[0][c+1]
        v0_b = bm.verts.new(Vector((v0.co.x, 0.001, v0.co.z)))
        v1_b = bm.verts.new(Vector((v1.co.x, 0.001, v1.co.z)))
        f = bm.faces.new([v0, v1, v1_b, v0_b])
        f.material_index = 0  # M_Security_Atlas
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # Left & Right side rim walls
    for r in range(3):
        # Left
        vl0 = grid_verts[r][0]
        vl1 = grid_verts[r+1][0]
        vl0_b = bm.verts.new(Vector((vl0.co.x, 0.001, vl0.co.z)))
        vl1_b = bm.verts.new(Vector((vl1.co.x, 0.001, vl1.co.z)))
        f_l = bm.faces.new([vl0, vl0_b, vl1_b, vl1])
        f_l.material_index = 0  # M_Security_Atlas
        set_face_uv_rect(bm, f_l, (0.55, 0.55, 0.95, 0.95))

        # Right
        vr0 = grid_verts[r][4]
        vr1 = grid_verts[r+1][4]
        vr0_b = bm.verts.new(Vector((vr0.co.x, 0.001, vr0.co.z)))
        vr1_b = bm.verts.new(Vector((vr1.co.x, 0.001, vr1.co.z)))
        f_r = bm.faces.new([vr0, vr1, vr1_b, vr0_b])
        f_r.material_index = 0  # M_Security_Atlas
        set_face_uv_rect(bm, f_r, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_status_led_mesh(mesh, materials):
    """
    Build Status_LED:
    Origin is at center of upper forehead LED aperture (0, 0.038, 0.041) relative to Sensor_Housing.
    High-tech vertical lozenge / hexagonal jewel indicator:
    - Assigned to Slot 2: M_Emission (Alarm Ruby Red Infrared Glow)
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    hw = 0.0022
    hz = 0.0048
    pts_led = [
        (0.0, hz), (-hw, hz * 0.5), (-hw, -hz * 0.5),
        (0.0, -hz), (hw, -hz * 0.5), (hw, hz * 0.5)
    ]
    base_v = [bm.verts.new(Vector((x, 0.000, z))) for x, z in pts_led]
    v_tip = bm.verts.new(Vector((0.0, 0.0028, 0.0)))

    # Front faceted jewel fan
    for i in range(6):
        ni = (i + 1) % 6
        f = bm.faces.new([v_tip, base_v[i], base_v[ni]])
        f.smooth = True
        f.material_index = 2  # M_Emission
        set_face_uv_rect(bm, f, (0.1, 0.1, 0.9, 0.9))

    # Base back cap
    f_b = bm.faces.new(list(reversed(base_v)))
    f_b.material_index = 2
    set_face_uv_rect(bm, f_b, (0.1, 0.1, 0.9, 0.9))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Asset Assembly and Hierarchy
# -------------------------------------------------------------

def generate_asset():
    """Build the entire SEC_Sensor_PIR_Motion asset with strict hierarchy."""
    setup_scene()
    atlas_img = setup_texture_atlas()
    materials = create_materials(atlas_img)

    # 1. Root Object: Sensor_Base named SEC_Sensor_PIR_Motion
    root_mesh = bpy.data.meshes.new("SEC_Sensor_PIR_Motion_Mesh")
    build_sensor_base_mesh(root_mesh, materials)
    root_obj = bpy.data.objects.new("SEC_Sensor_PIR_Motion", root_mesh)
    bpy.context.collection.objects.link(root_obj)
    root_obj.location = (0.0, 0.0, 0.0)

    # 2. Sensor_Housing (Child of SEC_Sensor_PIR_Motion)
    housing_mesh = bpy.data.meshes.new("Sensor_Housing_Mesh")
    build_sensor_housing_mesh(housing_mesh, materials)
    housing_obj = bpy.data.objects.new("Sensor_Housing", housing_mesh)
    bpy.context.collection.objects.link(housing_obj)
    housing_obj.parent = root_obj
    housing_obj.location = (0.0, 0.0, 0.0)

    # 3. Fresnel_Lens (Child of Sensor_Housing)
    # Origin at center of lens window: Y=0.028, Z=-0.008
    lens_mesh = bpy.data.meshes.new("Fresnel_Lens_Mesh")
    build_fresnel_lens_mesh(lens_mesh, materials)
    lens_obj = bpy.data.objects.new("Fresnel_Lens", lens_mesh)
    bpy.context.collection.objects.link(lens_obj)
    lens_obj.parent = housing_obj
    lens_obj.location = (0.0, 0.028, -0.008)

    # 4. Status_LED (Child of Sensor_Housing)
    # Origin at upper forehead aperture: Y=0.038, Z=0.041
    led_mesh = bpy.data.meshes.new("Status_LED_Mesh")
    build_status_led_mesh(led_mesh, materials)
    led_obj = bpy.data.objects.new("Status_LED", led_mesh)
    bpy.context.collection.objects.link(led_obj)
    led_obj.parent = housing_obj
    led_obj.location = (0.0, 0.038, 0.041)

    for obj in [root_obj, housing_obj, lens_obj, led_obj]:
        mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        mod.keep_sharp = True

    bpy.context.view_layer.update()

    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, housing_obj, lens_obj, led_obj]:
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
    if total_tris > 220:
        raise ValueError(f"Triangle count {total_tris} exceeds limit of 220 tris!")

    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root_obj, housing_obj, lens_obj, led_obj]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    fbx_path = os.path.join(exports_dir, "SEC_Sensor_PIR_Motion.fbx")

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

    blend_path = os.path.join(exports_dir, "SEC_Sensor_PIR_Motion.blend")
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
        "asset_name": "SEC_Sensor_PIR_Motion",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "tris_count": total_tris,
        "mesh_count": 4,
        "empty_count": 0,
        "materials": ["M_Security_Atlas", "M_Transparent", "M_Emission"]
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
        "SEC_Sensor_PIR_Motion",
        "Sensor_Housing",
        "Fresnel_Lens",
        "Status_LED"
    ]
    for name in expected_objects:
        if name not in imported_names:
            raise AssertionError(f"Expected object '{name}' was not found in imported FBX!")

    root_obj = bpy.data.objects["SEC_Sensor_PIR_Motion"]
    housing_obj = bpy.data.objects["Sensor_Housing"]
    lens_obj = bpy.data.objects["Fresnel_Lens"]
    led_obj = bpy.data.objects["Status_LED"]

    if housing_obj.parent != root_obj:
        raise AssertionError("Sensor_Housing is not parented to SEC_Sensor_PIR_Motion!")
    if lens_obj.parent != housing_obj:
        raise AssertionError("Fresnel_Lens is not parented to Sensor_Housing!")
    if led_obj.parent != housing_obj:
        raise AssertionError("Status_LED is not parented to Sensor_Housing!")
    print("[VERIFY] Full parent-child hierarchy verified.")

    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, housing_obj, lens_obj, led_obj]:
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
    if total_tris > 220:
        raise AssertionError(f"Verified triangle count {total_tris} exceeds limit 220!")

    expected_materials = ["M_Security_Atlas", "M_Transparent", "M_Emission"]
    for obj in [root_obj, housing_obj, lens_obj, led_obj]:
        slot_names = [slot.name for slot in obj.material_slots]
        print(f"[VERIFY] Object '{obj.name}' material slots: {slot_names}")
        if not slot_names:
            raise AssertionError(f"Object '{obj.name}' has no material slots!")
        for exp in expected_materials:
            if not any(exp in s for s in slot_names):
                raise AssertionError(f"Object '{obj.name}' is missing expected material {exp}!")

    for obj in [root_obj, housing_obj, lens_obj, led_obj]:
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
        "asset_name": "SEC_Sensor_PIR_Motion",
        "fbx_path": os.path.join("exports", "SEC_Sensor_PIR_Motion.fbx"),
        "tris_count": 0,
        "mesh_count": 0,
        "empty_count": 0,
        "materials": ["M_Security_Atlas", "M_Transparent", "M_Emission"]
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
