r"""
Generate SEC_RFID_Card_Reader (RFID Kart Okuyucu)
Asset: SEC_RFID_Card_Reader
Workspace: C:\Users\Burak\Desktop\Security_CCTV\09. SEC_RFID_Card_Reader

Requirements:
- Metric units, unit_scale = 1.0. Z-up in Blender.
- Unity FBX export standard: axis_forward='-Z', axis_up='Y', apply_unit_scale=True, bake_space_transform=False.
- Total triangulated tris count <= 280 tris. Target: ~210-230 tris.
- Hierarchy:
    SEC_RFID_Card_Reader (Root Empty at 0,0,0, flush against wall)
      ├── Mount_Backplate (Mesh, child of Root)
      └── Reader_Housing (Mesh, child of Root)
            ├── Card_Scan_Area (Mesh, child of Housing)
            └── Status_LED (Mesh, child of Housing)
- Materials (exact 2 slots):
    Slot 0: M_Security_Atlas
    Slot 1: M_Emission
- Clean UV unwrap with 100% ISOTROPIC (distortion-free) aspect-ratio preservation!
- Automated verification: re-import FBX, verify hierarchy, triangle budget, materials, UVs.
- Manifest update in exports/manifest.json with SUCCESS/FAILED.
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import os
import sys
import json
import math


def setup_clean_scene():
    """Reset to clean metric scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'


# Global Pixels-per-meter scale: 1 meter = 2400 pixels (1 mm = 2.4 px)
PIXELS_PER_METER = 2400.0


def create_security_atlas_texture():
    """
    Generate high-fidelity 512x512 texture atlas:
    Quadrant 0 (Top-Left, X: 0..256, Y: 256..512): Smoked acrylic RFID/NFC scan decal with authentic symmetric contactless waves ((( · ))).
    Quadrant 1 (Top-Right, X: 256..512, Y: 256..512): Dark obsidian titanium housing with clean metal & isolated bottom screw.
    Quadrant 2 (Bottom-Left, X: 0..256, Y: 0..256): Backplate industrial spec label & Wiegand wiring pinout.
    Quadrant 3 (Bottom-Right, X: 256..512, Y: 0..256): High-tech status LED light blade gradient.
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
                    # Quadrant 0: Smoked Acrylic RFID/NFC Contactless Decal (Center at X=128, Y=384)
                    dx = x - 128
                    dy = y - 384
                    dist = math.sqrt(dx**2 + dy**2)

                    r = max(0.04, 0.08 - dist * 0.0003)
                    g = max(0.05, 0.09 - dist * 0.0003)
                    b = max(0.07, 0.12 - dist * 0.0003)

                    # Contactless Waves & Center Dot
                    if dist <= 3.2:
                        r, g, b = 0.95, 0.98, 1.00
                    for wave_r in [11.0, 19.0, 27.0]:
                        if abs(dist - wave_r) <= 1.2 and abs(dx) >= abs(dy) * 0.55:
                            r, g, b = 0.90, 0.95, 1.00
                        elif abs(dist - wave_r) <= 2.2 and abs(dx) >= abs(dy) * 0.55:
                            r, g, b = max(r, 0.35), max(g, 0.65), max(b, 0.85)

                    # Perimeter chamfer boundary
                    if abs(dx) >= 44 or abs(dy) >= 64:
                        if abs(dx) >= 48 or abs(dy) >= 68:
                            r, g, b = 0.20, 0.22, 0.26
                        else:
                            r, g, b = 0.60, 0.65, 0.72

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # Quadrant 1: Housing Dark Metal & Torx Screw
                    r, g, b = 0.12, 0.13, 0.15
                    if x % 6 in [0, 1]: r, g, b = 0.11, 0.12, 0.14
                    if (x - 256) in [0, 1, 254, 255] or (y - 256) in [0, 1, 254, 255]:
                        r, g, b = 0.28, 0.32, 0.38

                    # Torx Screw at (X=448, Y=304)
                    dist_screw = math.sqrt((x - 448)**2 + (y - 304)**2)
                    if dist_screw <= 18:
                        if 14 <= dist_screw <= 18: r, g, b = 0.24, 0.26, 0.30
                        elif 10 <= dist_screw < 14: r, g, b = 0.70, 0.75, 0.82
                        elif dist_screw < 10:
                            ang = (math.atan2(y - 304, x - 448) + math.pi) % (math.pi / 3) - (math.pi / 6)
                            star_r = 7.0 * (1.0 - 0.25 * math.sin(ang * 3)**2)
                            if dist_screw <= star_r:
                                r, g, b = 0.05, 0.05, 0.06
                                if dist_screw <= 2.2: r, g, b = 0.35, 0.40, 0.48
                            else:
                                r, g, b = 0.45, 0.50, 0.58

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

            else:
                if x < 256:
                    # Quadrant 2: Backplate Specification Label & Wiring Pinout
                    r, g, b = 0.82, 0.84, 0.88
                    if (y in [30, 80, 135, 190, 240]) or (x in [30, 85, 140, 195, 240]):
                        r, g, b = 0.16, 0.18, 0.22
                    if 200 <= y <= 230 and 40 <= x <= 220:
                        r, g, b = 0.12, 0.15, 0.20
                        if 210 <= y <= 220 and (x % 5 in [0, 1, 2]): r, g, b = 0.92, 0.94, 0.98
                    if 50 <= y <= 160 and 45 <= x <= 215:
                        wire_row = int((y - 50) / 18)
                        if wire_row == 0:   r, g, b = 0.85, 0.15, 0.15 # RED
                        elif wire_row == 1: r, g, b = 0.15, 0.15, 0.15 # BLK
                        elif wire_row == 2: r, g, b = 0.15, 0.80, 0.25 # GRN
                        elif wire_row == 3: r, g, b = 0.95, 0.95, 0.95 # WHT
                        elif wire_row == 4: r, g, b = 0.55, 0.35, 0.15 # BRN
                        elif wire_row == 5: r, g, b = 0.20, 0.45, 0.85 # BLU

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:
                    # Quadrant 3: High-Tech Emissive Light Blade
                    dx_led = abs(x - 384)
                    dy_led = abs(y - 128)
                    if dx_led <= 118 and dy_led <= 44:
                        if dy_led <= 14 and dx_led <= 95:
                            r, g, b = 0.92, 1.00, 0.98
                        elif dy_led <= 26:
                            r, g, b = 0.15, 0.95, 0.75
                        else:
                            r, g, b = 0.05, 0.65, 0.50
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
        print(f"[WARN] Failed to save atlas: {e}")

    atlas_img.pack()
    return atlas_img


def create_materials(atlas_img):
    """
    Create the 2 standard materials required for SEC_RFID_Card_Reader:
    Slot 0: M_Security_Atlas
    Slot 1: M_Emission
    """
    mat_configs = [
        ("M_Security_Atlas", (0.12, 0.13, 0.15, 1.0), 0.15, 0.30, 0.0, (0, 0, 0, 1), 0.0, (0.15, 0.16, 0.18, 1.0)),
        ("M_Emission", (0.15, 0.98, 0.60, 1.0), 0.0, 0.10, 0.0, (0.15, 0.98, 0.60, 1.0), 10.0, (0.20, 1.00, 0.65, 1.0)),
    ]

    materials = {}
    for name, base_col, metal, rough, trans, emiss_col, emiss_str, view_col in mat_configs:
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_out.location = (300, 0)
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf.location = (0, 0)
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])

        node_tex = nodes.new(type='ShaderNodeTexImage')
        node_tex.location = (-300, 0)
        node_tex.image = atlas_img
        links.new(node_tex.outputs['Color'], node_bsdf.inputs['Base Color'])

        if emiss_str > 0.0:
            links.new(node_tex.outputs['Color'], node_bsdf.inputs['Emission Color'])
            node_bsdf.inputs['Emission Strength'].default_value = emiss_str

        node_bsdf.inputs['Metallic'].default_value = metal
        node_bsdf.inputs['Roughness'].default_value = rough
        mat.diffuse_color = view_col
        materials[name] = mat

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


def map_face_uv_uniform(bm, face, uv_center=(0.25, 0.75), world_center=(0.0, 0.0), scale_ppm=PIXELS_PER_METER, atlas_dim=512.0):
    """Uniform isotropic UV mapping with zero aspect distortion."""
    uv_lay = bm.loops.layers.uv.verify()
    u_c, v_c = uv_center
    w_cx, w_cz = world_center
    uv_per_meter = scale_ppm / atlas_dim

    for loop in face.loops:
        x_w = loop.vert.co.x
        z_w = loop.vert.co.z
        dx = x_w - w_cx
        dz = z_w - w_cz
        u = u_c - dx * uv_per_meter
        v = v_c + dz * uv_per_meter
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
UV_CLEAN_METAL  = (0.580, 0.650, 0.880, 0.880)
UV_BACK_LABEL   = (0.050, 0.050, 0.450, 0.450)
UV_EMISS_BLADE  = (0.520, 0.120, 0.980, 0.380)


# -------------------------------------------------------------
# Enhanced Low-Poly Mesh Builders (~210-230 tris)
# -------------------------------------------------------------

def build_mount_backplate_mesh(mesh, materials):
    """
    Build Mount_Backplate:
    Flush with wall at Y = 0 (Y: 0.000 to 0.003m).
    16-sided perimeter with smooth double-beveled corners.
    Tris count: ~60 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.024, 0.054
    c1, c2, c3 = 0.002, 0.004, 0.006

    pts = [
        (sx - c3, sz), (-sx + c3, sz),
        (-sx + c2, sz - c1), (-sx + c1, sz - c2), (-sx, sz - c3),
        (-sx, -sz + c3), (-sx + c1, -sz + c2), (-sx + c2, -sz + c1), (-sx + c3, -sz),
        (sx - c3, -sz), (sx - c2, -sz + c1), (sx - c1, -sz + c2), (sx, -sz + c3),
        (sx, sz - c3), (sx - c1, sz - c2), (sx - c2, sz - c1)
    ]
    n_pts = len(pts)

    v_back = [bm.verts.new(Vector((x, 0.000, z))) for x, z in pts]
    v_front = [bm.verts.new(Vector((x, 0.003, z))) for x, z in pts]

    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_BACK_LABEL)

    f_front = bm.faces.new(v_front)
    f_front.material_index = 0
    set_face_uv_rect(bm, f_front, UV_CLEAN_METAL)

    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_back[i], v_front[i], v_front[ni], v_back[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_CLEAN_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_reader_housing_mesh(mesh, materials):
    """
    Build Reader_Housing:
    Origin at (0.0, 0.003, 0.0).
    - 16-sided smooth rounded double-chamfered perimeter.
    - Architectural projecting top visor canopy (Y = 0.018m).
    - Recessed central scan tray with beveled frame.
    - Lower chin with Torx screw detail.
    Tris count: ~100 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.024, 0.055
    c1, c2, c3 = 0.002, 0.004, 0.006

    pts_r = [
        (sx - c3, sz), (-sx + c3, sz),
        (-sx + c2, sz - c1), (-sx + c1, sz - c2), (-sx, sz - c3),
        (-sx, -sz + c3), (-sx + c1, -sz + c2), (-sx + c2, -sz + c1), (-sx + c3, -sz),
        (sx - c3, -sz), (sx - c2, -sz + c1), (sx - c1, -sz + c2), (sx, -sz + c3),
        (sx, sz - c3), (sx - c1, sz - c2), (sx - c2, sz - c1)
    ]
    n_pts = len(pts_r)
    v_r = [bm.verts.new(Vector((x, 0.000, z))) for x, z in pts_r]

    f_rcap = bm.faces.new(list(reversed(v_r)))
    f_rcap.material_index = 0
    set_face_uv_rect(bm, f_rcap, UV_CLEAN_METAL)

    # Front rim at Y = 0.0150m (visor projecting to 0.0180m at top)
    sx_f, sz_f = 0.023, 0.054
    c_f1, c_f2, c_f3 = 0.0018, 0.0036, 0.0055
    pts_f = [
        (sx_f - c_f3, sz_f), (-sx_f + c_f3, sz_f),
        (-sx_f + c_f2, sz_f - c_f1), (-sx_f + c_f1, sz_f - c_f2), (-sx_f, sz_f - c_f3),
        (-sx_f, -sz_f + c_f3), (-sx_f + c_f1, -sz_f + c_f2), (-sx_f + c_f2, -sz_f + c_f1), (-sx_f + c_f3, -sz_f),
        (sx_f - c_f3, -sz_f), (sx_f - c_f2, -sz_f + c_f1), (sx_f - c_f1, -sz_f + c_f2), (sx_f, -sz_f + c_f3),
        (sx_f, sz_f - c_f3), (sx_f - c_f1, sz_f - c_f2), (sx_f - c_f2, sz_f - c_f1)
    ]
    v_f = []
    for i, (x, z) in enumerate(pts_f):
        y_proj = 0.0180 if z > 0.040 else 0.0150
        v_f.append(bm.verts.new(Vector((x, y_proj, z))))

    # Side chamfer quads connecting rear to front
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_r[i], v_f[i], v_f[ni], v_r[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_CLEAN_METAL)

    # Scan tray outer rim bounds
    st_x = 0.0205
    st_zt = 0.0220
    st_zb = -0.0380

    # 1. Forehead Panel above scan tray (Z: st_zt to sz_f)
    fh_tl = v_f[1]; fh_tr = v_f[0]
    fh_bl = bm.verts.new(Vector((-st_x, 0.015, st_zt)))
    fh_br = bm.verts.new(Vector(( st_x, 0.015, st_zt)))

    f_forehead = bm.faces.new([fh_tr, fh_tl, fh_bl, fh_br])
    f_forehead.material_index = 0
    set_face_uv_rect(bm, f_forehead, UV_CLEAN_METAL, flip_u=True)

    f_ctl1 = bm.faces.new([v_f[1], v_f[2], v_f[3], fh_bl]); f_ctl1.material_index = 0; set_face_uv_rect(bm, f_ctl1, UV_CLEAN_METAL)
    f_ctr1 = bm.faces.new([v_f[15], v_f[14], v_f[0], fh_br]); f_ctr1.material_index = 0; set_face_uv_rect(bm, f_ctr1, UV_CLEAN_METAL)

    # 2. Side Flanks beside scan tray (Z: st_zb to st_zt)
    st_bl = bm.verts.new(Vector((-st_x, 0.015, st_zb)))
    st_br = bm.verts.new(Vector(( st_x, 0.015, st_zb)))

    f_flank_l = bm.faces.new([fh_bl, v_f[3], v_f[4], v_f[5], st_bl]); f_flank_l.material_index = 0; set_face_uv_rect(bm, f_flank_l, UV_CLEAN_METAL)
    f_flank_r = bm.faces.new([v_f[14], fh_br, st_br, v_f[12], v_f[13]]); f_flank_r.material_index = 0; set_face_uv_rect(bm, f_flank_r, UV_CLEAN_METAL)

    # 3. Lower Chin Panel below scan tray (Z: -sz_f to st_zb)
    ch_bl = v_f[8]; ch_br = v_f[9]
    f_chin = bm.faces.new([st_bl, st_br, ch_br, ch_bl])
    f_chin.material_index = 0
    map_face_uv_uniform(bm, f_chin, uv_center=(448.0 / 512.0, 304.0 / 512.0), world_center=(0.0, -0.046))

    f_cbl = bm.faces.new([v_f[5], v_f[6], v_f[7], ch_bl, st_bl]); f_cbl.material_index = 0; set_face_uv_rect(bm, f_cbl, UV_CLEAN_METAL)
    f_cbr = bm.faces.new([st_br, ch_br, v_f[10], v_f[11], v_f[12]]); f_cbr.material_index = 0; set_face_uv_rect(bm, f_cbr, UV_CLEAN_METAL)

    # 4. Recessed Card Scan Well (recessed 3.0mm to Y = 0.0120m)
    y_rec = 0.0120
    ti_tl = bm.verts.new(Vector((-st_x, y_rec, st_zt)))
    ti_tr = bm.verts.new(Vector(( st_x, y_rec, st_zt)))
    ti_bl = bm.verts.new(Vector((-st_x, y_rec, st_zb)))
    ti_br = bm.verts.new(Vector(( st_x, y_rec, st_zb)))

    f_tj_t = bm.faces.new([fh_br, fh_bl, ti_tl, ti_tr]); f_tj_t.material_index = 0; set_face_uv_rect(bm, f_tj_t, UV_CLEAN_METAL)
    f_tj_b = bm.faces.new([st_bl, st_br, ti_br, ti_bl]); f_tj_b.material_index = 0; set_face_uv_rect(bm, f_tj_b, UV_CLEAN_METAL)
    f_tj_l = bm.faces.new([fh_bl, st_bl, ti_bl, ti_tl]); f_tj_l.material_index = 0; set_face_uv_rect(bm, f_tj_l, UV_CLEAN_METAL)
    f_tj_r = bm.faces.new([st_br, fh_br, ti_tr, ti_br]); f_tj_r.material_index = 0; set_face_uv_rect(bm, f_tj_r, UV_CLEAN_METAL)
    f_t_floor = bm.faces.new([ti_tl, ti_bl, ti_br, ti_tr]); f_t_floor.material_index = 0; set_face_uv_rect(bm, f_t_floor, UV_CLEAN_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_card_scan_area_mesh(mesh, materials):
    """
    Build Card_Scan_Area (Sculpted Contactless Smart Card Plaque):
    Origin at (0.0, 0.0130, -0.008) relative to Reader_Housing.
    - 12-sided rounded beveled optical plaque with metallic collar.
    - Front face mapped ISOTROPICALLY (100% distortion-free) to Quadrant 0.
    Tris count: ~44 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx_b, sz_b = 0.0195, 0.0285
    c1_b, c2_b = 0.0018, 0.0035
    sx_t, sz_t = 0.0185, 0.0275
    c1_t, c2_t = 0.0015, 0.0030
    y_b, y_t = 0.000, 0.0040

    pts_b = [
        (sx_b - c2_b, sz_b), (-sx_b + c2_b, sz_b),
        (-sx_b + c1_b, sz_b - c1_b), (-sx_b, sz_b - c2_b),
        (-sx_b, -sz_b + c2_b), (-sx_b + c1_b, -sz_b + c1_b),
        (-sx_b + c2_b, -sz_b), (sx_b - c2_b, -sz_b),
        (sx_b - c1_b, -sz_b + c1_b), (sx_b, -sz_b + c2_b),
        (sx_b, sz_b - c2_b), (sx_b - c1_b, sz_b - c1_b)
    ]
    pts_t = [
        (sx_t - c2_t, sz_t), (-sx_t + c2_t, sz_t),
        (-sx_t + c1_t, sz_t - c1_t), (-sx_t, sz_t - c2_t),
        (-sx_t, -sz_t + c2_t), (-sx_t + c1_t, -sz_t + c1_t),
        (-sx_t + c2_t, -sz_t), (sx_t - c2_t, -sz_t),
        (sx_t - c1_t, -sz_t + c1_t), (sx_t, -sz_t + c2_t),
        (sx_t, sz_t - c2_t), (sx_t - c1_t, sz_t - c1_t)
    ]
    n_pts = len(pts_b)

    v_b = [bm.verts.new(Vector((x, y_b, z))) for x, z in pts_b]
    v_t = [bm.verts.new(Vector((x, y_t, z))) for x, z in pts_t]

    # Front RFID/NFC Scanning Face (Quadrant 0)
    f_front = bm.faces.new(v_t)
    f_front.material_index = 0
    map_face_uv_uniform(bm, f_front, uv_center=(128.0 / 512.0, 384.0 / 512.0), world_center=(0.0, 0.0))

    # Back face
    f_back = bm.faces.new(list(reversed(v_b)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_CLEAN_METAL)

    # 12 Side chamfer faces
    for i in range(n_pts):
        ni = (i + 1) % n_pts
        f = bm.faces.new([v_b[i], v_t[i], v_t[ni], v_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_CLEAN_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_status_led_mesh(mesh, materials):
    """
    Build Status_LED (Sculpted Upper Light Blade):
    Origin at (0.0, 0.0155, 0.035) relative to Reader_Housing.
    Beveled horizontal light blade nestled beneath visor canopy.
    Tris count: ~20 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx_b, sz_b = 0.0180, 0.0025
    sx_t, sz_t = 0.0170, 0.0020
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
    f_front.material_index = 1  # M_Emission
    set_face_uv_rect(bm, f_front, UV_EMISS_BLADE, flip_u=True)

    f_back = bm.faces.new(list(reversed(v_b)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_CLEAN_METAL)

    for i in range(4):
        ni = (i + 1) % 4
        f = bm.faces.new([v_b[i], v_t[i], v_t[ni], v_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_CLEAN_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Assembly and Hierarchy
# -------------------------------------------------------------

def assemble_sec_rfid_card_reader():
    """
    Hierarchy:
    SEC_RFID_Card_Reader (Root Empty at 0,0,0)
      ├── Mount_Backplate (child of Root)
      └── Reader_Housing (child of Root)
            ├── Card_Scan_Area (child of Housing)
            └── Status_LED (child of Housing)
    """
    setup_clean_scene()
    atlas_img = create_security_atlas_texture()
    materials = create_materials(atlas_img)

    # 1. Root Empty
    root_obj = bpy.data.objects.new("SEC_RFID_Card_Reader", None)
    root_obj.empty_display_type = 'PLAIN_AXES'
    root_obj.empty_display_size = 0.05
    root_obj.location = Vector((0.0, 0.0, 0.0))
    bpy.context.scene.collection.objects.link(root_obj)

    # 2. Mount_Backplate (child of Root)
    mesh_plate = bpy.data.meshes.new("Mount_Backplate")
    build_mount_backplate_mesh(mesh_plate, materials)
    obj_plate = bpy.data.objects.new("Mount_Backplate", mesh_plate)
    obj_plate.location = Vector((0.0, 0.0, 0.0))
    obj_plate.parent = root_obj
    bpy.context.scene.collection.objects.link(obj_plate)

    # 3. Reader_Housing (child of Root)
    mesh_housing = bpy.data.meshes.new("Reader_Housing")
    build_reader_housing_mesh(mesh_housing, materials)
    obj_housing = bpy.data.objects.new("Reader_Housing", mesh_housing)
    obj_housing.location = Vector((0.0, 0.003, 0.0))
    obj_housing.parent = root_obj
    bpy.context.scene.collection.objects.link(obj_housing)

    # 4. Card_Scan_Area (child of Housing)
    mesh_scan = bpy.data.meshes.new("Card_Scan_Area")
    build_card_scan_area_mesh(mesh_scan, materials)
    obj_scan = bpy.data.objects.new("Card_Scan_Area", mesh_scan)
    obj_scan.location = Vector((0.0, 0.0130, -0.008))
    obj_scan.parent = obj_housing
    bpy.context.scene.collection.objects.link(obj_scan)

    # 5. Status_LED (child of Housing)
    mesh_led = bpy.data.meshes.new("Status_LED")
    build_status_led_mesh(mesh_led, materials)
    obj_led = bpy.data.objects.new("Status_LED", mesh_led)
    obj_led.location = Vector((0.0, 0.0155, 0.035))
    obj_led.parent = obj_housing
    bpy.context.scene.collection.objects.link(obj_led)

    # Count initial triangles
    bpy.context.view_layer.update()
    mesh_objs = [obj_plate, obj_housing, obj_scan, obj_led]
    total_tris = 0
    for obj in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        tris = len(bm.faces)
        total_tris += tris
        bm.free()

    print(f"[INFO] Initial Triangulated Triangle Count: {total_tris}")
    assert total_tris <= 280, f"Triangle budget exceeded! {total_tris} > 280 tris"

    return root_obj, mesh_objs, total_tris


def export_and_verify(root_obj, mesh_objs, initial_tris):
    """Export FBX and verify all QA rules."""
    exports_dir = os.path.abspath("exports")
    os.makedirs(exports_dir, exist_ok=True)
    fbx_path = os.path.join(exports_dir, "SEC_RFID_Card_Reader.fbx")
    blend_path = os.path.join(exports_dir, "SEC_RFID_Card_Reader.blend")

    # Select all objects
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
    imp_root = bpy.data.objects.get("SEC_RFID_Card_Reader")
    assert imp_root is not None, "FAILED: Root object SEC_RFID_Card_Reader missing in FBX!"

    # 2. Verify Children Hierarchy
    expected_children = {
        "SEC_RFID_Card_Reader": ["Mount_Backplate", "Reader_Housing"],
        "Reader_Housing": ["Card_Scan_Area", "Status_LED"]
    }
    for parent_name, expected_child_names in expected_children.items():
        parent = bpy.data.objects.get(parent_name)
        assert parent is not None, f"Parent {parent_name} missing!"
        actual_children = [c.name for c in parent.children]
        for ec in expected_child_names:
            assert ec in actual_children, f"Child {ec} missing under {parent_name}! Children found: {actual_children}"

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
    assert verify_tris <= 280, f"FAILED: Verified tris count {verify_tris} > 280!"

    # 4. Verify Materials & UVs
    expected_materials = ["M_Security_Atlas", "M_Emission"]
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            assert len(obj.data.uv_layers) > 0, f"Mesh {obj.name} has no UV layer!"
            slot_names = [slot.material.name for slot in obj.material_slots if slot.material]
            for mat_name in slot_names:
                assert mat_name in expected_materials, f"Unexpected material {mat_name} on {obj.name}!"

    print("[VERIFY] Material slots and UV layers verified across all meshes.")
    print("[VERIFY] ALL QA CHECKS PASSED SUCCESSFULLY.")

    # 5. Update Manifest
    manifest_path = os.path.join(exports_dir, "manifest.json")
    manifest_data = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_RFID_Card_Reader"] = {
        "asset_name": "SEC_RFID_Card_Reader",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "texture_atlas": os.path.join(exports_dir, "T_Security_Atlas.png"),
        "tris_count": verify_tris,
        "max_tris_allowed": 280,
        "mesh_count": len(verified_meshes),
        "meshes": verified_meshes,
        "materials": expected_materials,
        "status": "SUCCESS"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Manifest updated: {manifest_path}")
    return True


if __name__ == "__main__":
    try:
        root_obj, mesh_objs, tris = assemble_sec_rfid_card_reader()
        success = export_and_verify(root_obj, mesh_objs, tris)
        if success:
            print("\n==========================================")
            print("  PROCESS COMPLETED SUCCESSFULLY [SUCCESS]")
            print("==========================================")
            sys.exit(0)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
