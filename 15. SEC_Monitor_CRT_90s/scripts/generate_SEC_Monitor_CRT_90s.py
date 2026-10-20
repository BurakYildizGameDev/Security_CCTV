"""
SEC_Monitor_CRT_90s Generator Script (Master Quality Revision 2)
Industrial Low-Poly Security & CCTV Asset Pack
Upper Budget Limit: 650 triangles

Hierarchy:
SEC_Monitor_CRT_90s (Root Empty at 0, 0, 0)
 └── CRT_Housing (Mesh, child of Root)
      ├── Screen_Bezel (Mesh, child of CRT_Housing)
      ├── Screen_Surface (Mesh, child of CRT_Housing, Material M_Screen)
      ├── Control_Button_Array (Mesh, child of CRT_Housing)
      └── Vent_Grille (Mesh, child of CRT_Housing)

Materials:
    Slot 0: M_Security_Atlas
    Slot 1: M_Screen
    Slot 2: M_Metal
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


def load_or_create_textures():
    """Ensure T_Security_Atlas.png and T_Screen.png exist in exports/ and load them into Blender."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    atlas_path = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
    screen_path = os.path.join(EXPORTS_DIR, "T_Screen.png")

    if os.path.exists(atlas_path):
        atlas_img = bpy.data.images.load(atlas_path, check_existing=True)
    else:
        atlas_img = bpy.data.images.new("T_Security_Atlas", width=512, height=512, alpha=True)

    if os.path.exists(screen_path):
        screen_img = bpy.data.images.load(screen_path, check_existing=True)
    else:
        screen_img = bpy.data.images.new("T_Screen", width=512, height=512, alpha=True)

    return atlas_img, screen_img


def create_materials(atlas_img, screen_img):
    """
    Create exact 3 materials required by prompt:
    Slot 0: M_Security_Atlas
    Slot 1: M_Screen
    Slot 2: M_Metal
    """
    materials = {}

    # 1. Slot 0: M_Security_Atlas (Dark CRT casing plastic, chin strip, vents, rear labels)
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

    bsdf0.inputs['Roughness'].default_value = 0.45
    bsdf0.inputs['Metallic'].default_value = 0.05
    mat_atlas.diffuse_color = (0.16, 0.17, 0.19, 1.0)
    materials["M_Security_Atlas"] = mat_atlas

    # 2. Slot 1: M_Screen (Cathode ray tube glass with phosphor glow & scanlines)
    mat_screen = bpy.data.materials.get("M_Screen")
    if not mat_screen:
        mat_screen = bpy.data.materials.new(name="M_Screen")
    mat_screen.use_nodes = True
    nodes1 = mat_screen.node_tree.nodes
    links1 = mat_screen.node_tree.links
    nodes1.clear()

    out1 = nodes1.new(type='ShaderNodeOutputMaterial')
    out1.location = (300, 0)
    bsdf1 = nodes1.new(type='ShaderNodeBsdfPrincipled')
    bsdf1.location = (0, 0)
    links1.new(bsdf1.outputs['BSDF'], out1.inputs['Surface'])

    tex1 = nodes1.new(type='ShaderNodeTexImage')
    tex1.location = (-300, 0)
    tex1.image = screen_img
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Base Color'])
    links1.new(tex1.outputs['Color'], bsdf1.inputs['Emission Color'])

    bsdf1.inputs['Emission Strength'].default_value = 1.25
    bsdf1.inputs['Roughness'].default_value = 0.08
    bsdf1.inputs['Metallic'].default_value = 0.02
    mat_screen.diffuse_color = (0.15, 0.40, 0.22, 1.0)
    materials["M_Screen"] = mat_screen

    # 3. Slot 2: M_Metal (BNC connectors, chrome screws, hardware)
    mat_metal = bpy.data.materials.get("M_Metal")
    if not mat_metal:
        mat_metal = bpy.data.materials.new(name="M_Metal")
    mat_metal.use_nodes = True
    nodes2 = mat_metal.node_tree.nodes
    links2 = mat_metal.node_tree.links
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

    bsdf2.inputs['Roughness'].default_value = 0.22
    bsdf2.inputs['Metallic'].default_value = 0.95
    mat_metal.diffuse_color = (0.80, 0.82, 0.86, 1.0)
    materials["M_Metal"] = mat_metal

    return materials


def attach_standard_materials(mesh, materials):
    """Attach the 3 standard materials in strict order [M_Security_Atlas, M_Screen, M_Metal]."""
    mesh.materials.clear()
    mesh.materials.append(materials["M_Security_Atlas"])  # Slot 0
    mesh.materials.append(materials["M_Screen"])          # Slot 1
    mesh.materials.append(materials["M_Metal"])           # Slot 2


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


# Constant UV coordinates with clean, non-overlapping zones based on T_Security_Atlas
# PIL Y vs UV V: v = (512 - y) / 512.0
UV_CASING_PLASTIC   = (0.020, 0.020, 0.480, 0.480)   # Clean dark charcoal CRT plastic
UV_CHIN_PANEL       = (0.000, 0.500, 1.000, 0.625)   # Full chin control strip (512x64)
UV_REAR_BAY         = (0.000, 0.625, 0.566, 0.8125)  # Recessed metal I/O connector panel
UV_SPEC_LABEL       = (0.570, 0.625, 0.990, 0.8125)  # Rating plate sticker
UV_LOUVERS          = (0.010, 0.815, 0.490, 0.990)   # Molded ventilation slots
UV_HARDWARE_CHROME  = (0.505, 0.815, 0.745, 0.990)  # Brushed BNC metal & screws
UV_BUTTON_CAPS      = (0.755, 0.815, 0.990, 0.990)  # Numbered channel button tops


# -------------------------------------------------------------
# High-Density Low-Poly Mesh Builders
# -------------------------------------------------------------

def build_crt_housing_mesh(mesh, materials):
    """
    Build CRT_Housing:
    Heavy 1990s retro CRT monitor chassis:
    - Front collar box (Width 360mm, Height 330mm, Depth Y: -0.040 to +0.070m)
    - Tapered rear electron gun bell cone (Width 240mm, Height 230mm, Y: -0.040 to -0.260m)
    - Recessed rear I/O connector bay (Y: -0.245 to -0.260m) with 4 BNC ports and IEC AC socket
    - Specification rating label quad & rear louver zone
    - 4 molded bottom rubber feet resting at Z = 0.000m
    - 2 side recessed carrying handles on left and right
    Tris count: ~240 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_fc = 0.180      # Front width half: 360mm
    z_bot = 0.015     # Bottom of main body (feet extend to 0.000)
    z_top = 0.330     # Top of body: 330mm height
    y_front = 0.070   # Front collar seam where bezel joins
    y_mid = -0.040    # Transition where rear taper begins
    y_rear = -0.260   # Rear outer panel

    x_rc = 0.120      # Rear width half: 240mm
    z_r_bot = 0.035   # Rear bottom
    z_r_top = 0.300   # Rear top

    # 1. Front Collar (Y: -0.040 to +0.070)
    v_fc_f = [
        bm.verts.new(Vector((-x_fc, y_front, z_bot))),
        bm.verts.new(Vector(( x_fc, y_front, z_bot))),
        bm.verts.new(Vector(( x_fc, y_front, z_top))),
        bm.verts.new(Vector((-x_fc, y_front, z_top)))
    ]
    v_fc_m = [
        bm.verts.new(Vector((-x_fc, y_mid, z_bot))),
        bm.verts.new(Vector(( x_fc, y_mid, z_bot))),
        bm.verts.new(Vector(( x_fc, y_mid, z_top))),
        bm.verts.new(Vector((-x_fc, y_mid, z_top)))
    ]

    f_fc_b = bm.faces.new([v_fc_f[0], v_fc_f[1], v_fc_m[1], v_fc_m[0]]); f_fc_b.material_index = 0; set_face_uv_rect(bm, f_fc_b, UV_CASING_PLASTIC)
    f_fc_r = bm.faces.new([v_fc_f[1], v_fc_f[2], v_fc_m[2], v_fc_m[1]]); f_fc_r.material_index = 0; set_face_uv_rect(bm, f_fc_r, UV_CASING_PLASTIC)
    f_fc_t = bm.faces.new([v_fc_f[2], v_fc_f[3], v_fc_m[3], v_fc_m[2]]); f_fc_t.material_index = 0; set_face_uv_rect(bm, f_fc_t, UV_CASING_PLASTIC)
    f_fc_l = bm.faces.new([v_fc_f[3], v_fc_f[0], v_fc_m[0], v_fc_m[3]]); f_fc_l.material_index = 0; set_face_uv_rect(bm, f_fc_l, UV_CASING_PLASTIC)

    # 2. Tapered Rear Bell Housing (Y: -0.040 to -0.260)
    v_rear = [
        bm.verts.new(Vector((-x_rc, y_rear, z_r_bot))),
        bm.verts.new(Vector(( x_rc, y_rear, z_r_bot))),
        bm.verts.new(Vector(( x_rc, y_rear, z_r_top))),
        bm.verts.new(Vector((-x_rc, y_rear, z_r_top)))
    ]

    f_tp_b = bm.faces.new([v_fc_m[0], v_fc_m[1], v_rear[1], v_rear[0]]); f_tp_b.material_index = 0; set_face_uv_rect(bm, f_tp_b, UV_CASING_PLASTIC)
    f_tp_r = bm.faces.new([v_fc_m[1], v_fc_m[2], v_rear[2], v_rear[1]]); f_tp_r.material_index = 0; set_face_uv_rect(bm, f_tp_r, UV_CASING_PLASTIC)
    f_tp_t = bm.faces.new([v_fc_m[2], v_fc_m[3], v_rear[3], v_rear[2]]); f_tp_t.material_index = 0; set_face_uv_rect(bm, f_tp_t, UV_CASING_PLASTIC)
    f_tp_l = bm.faces.new([v_fc_m[3], v_fc_m[0], v_rear[0], v_rear[3]]); f_tp_l.material_index = 0; set_face_uv_rect(bm, f_tp_l, UV_CASING_PLASTIC)

    # 3. Rear Backplate Framing with Recessed I/O Bay
    # Lower Recessed Connector Bay (Z: 0.045 to 0.155, X: -0.095 to +0.095, Y: -0.246 recessed)
    z_bay_b = 0.045
    z_bay_t = 0.155
    x_bay = 0.095
    y_bay_in = -0.246

    v_bay_rim = [
        bm.verts.new(Vector((-x_bay, y_rear, z_bay_b))),
        bm.verts.new(Vector(( x_bay, y_rear, z_bay_b))),
        bm.verts.new(Vector(( x_bay, y_rear, z_bay_t))),
        bm.verts.new(Vector((-x_bay, y_rear, z_bay_t)))
    ]
    v_bay_in = [
        bm.verts.new(Vector((-x_bay, y_bay_in, z_bay_b))),
        bm.verts.new(Vector(( x_bay, y_bay_in, z_bay_b))),
        bm.verts.new(Vector(( x_bay, y_bay_in, z_bay_t))),
        bm.verts.new(Vector((-x_bay, y_bay_in, z_bay_t)))
    ]

    for i in range(4):
        ni = (i + 1) % 4
        f_bw = bm.faces.new([v_bay_rim[i], v_bay_rim[ni], v_bay_in[ni], v_bay_in[i]])
        f_bw.material_index = 0
        set_face_uv_rect(bm, f_bw, UV_CASING_PLASTIC)

    # Recessed bay backplate: Mapped to UV_REAR_BAY with flip_u=False!
    # Looking from behind (+Y direction), -X is left, +X is right, matching texture!
    f_bay_back = bm.faces.new(list(reversed(v_bay_in)))
    f_bay_back.material_index = 0
    set_face_uv_rect(bm, f_bay_back, UV_REAR_BAY, flip_u=False)

    # Rear framing quads surrounding the bay
    f_rm_b = bm.faces.new([v_rear[0], v_rear[1], v_bay_rim[1], v_bay_rim[0]])
    f_rm_b.material_index = 0; set_face_uv_rect(bm, f_rm_b, UV_CASING_PLASTIC)

    v_mid_l = bm.verts.new(Vector((-x_rc, y_rear, z_bay_t)))
    v_mid_r = bm.verts.new(Vector(( x_rc, y_rear, z_bay_t)))

    f_rm_l = bm.faces.new([v_rear[0], v_bay_rim[0], v_bay_rim[3], v_mid_l])
    f_rm_l.material_index = 0; set_face_uv_rect(bm, f_rm_l, UV_CASING_PLASTIC)

    f_rm_r = bm.faces.new([v_bay_rim[1], v_rear[1], v_mid_r, v_bay_rim[2]])
    f_rm_r.material_index = 0; set_face_uv_rect(bm, f_rm_r, UV_CASING_PLASTIC)

    # Horizontal divider strip above bay
    z_up_b = 0.170
    v_mid2_l = bm.verts.new(Vector((-x_rc, y_rear, z_up_b)))
    v_mid2_r = bm.verts.new(Vector(( x_rc, y_rear, z_up_b)))

    f_div_h = bm.faces.new([v_mid_l, v_bay_rim[3], v_bay_rim[2], v_mid_r])
    f_div_h.material_index = 0; set_face_uv_rect(bm, f_div_h, UV_CASING_PLASTIC)

    f_div_h2 = bm.faces.new([v_mid_l, v_mid_r, v_mid2_r, v_mid2_l])
    f_div_h2.material_index = 0; set_face_uv_rect(bm, f_div_h2, UV_CASING_PLASTIC)

    # Upper rear division:
    # - Left: Molded Cooling Louvers (X: -0.100 to -0.010, Z: 0.175 to 0.285)
    # - Right: Spec Rating Label Quad (X: +0.005 to +0.095, Z: 0.190 to 0.245) - 2.2:1 aspect ratio!
    # - Surrounding casing quads
    z_spec_b = 0.195
    z_spec_t = 0.245
    x_spec_l = 0.005
    x_spec_r = 0.100

    v_lv_b = bm.verts.new(Vector((-0.010, y_rear, z_up_b)))
    v_lv_t = bm.verts.new(Vector((-0.010, y_rear, 0.285)))
    v_lv_lt = bm.verts.new(Vector((-x_rc, y_rear, 0.285)))

    # Left louver quad
    f_lv = bm.faces.new([v_mid2_l, v_lv_b, v_lv_t, v_lv_lt])
    f_lv.material_index = 0
    set_face_uv_rect(bm, f_lv, UV_LOUVERS)

    # Right side:
    v_sp_bl = bm.verts.new(Vector((x_spec_l, y_rear, z_spec_b)))
    v_sp_br = bm.verts.new(Vector((x_spec_r, y_rear, z_spec_b)))
    v_sp_tr = bm.verts.new(Vector((x_spec_r, y_rear, z_spec_t)))
    v_sp_tl = bm.verts.new(Vector((x_spec_l, y_rear, z_spec_t)))

    # Rating spec plate sticker quad (flip_u=False for natural text!)
    f_spec = bm.faces.new([v_sp_bl, v_sp_br, v_sp_tr, v_sp_tl])
    f_spec.material_index = 0
    set_face_uv_rect(bm, f_spec, UV_SPEC_LABEL, flip_u=False)

    # Quads surrounding the sticker
    v_mid2_cx = bm.verts.new(Vector((x_spec_l, y_rear, z_up_b)))
    f_gap_mid = bm.faces.new([v_lv_b, v_mid2_cx, v_sp_bl, v_lv_t]) # between left louver and sticker
    f_gap_mid.material_index = 0; set_face_uv_rect(bm, f_gap_mid, UV_CASING_PLASTIC)

    v_rc_sp_b = bm.verts.new(Vector((x_rc, y_rear, z_spec_b)))
    v_rc_sp_t = bm.verts.new(Vector((x_rc, y_rear, z_spec_t)))
    v_rc_upt = bm.verts.new(Vector((x_rc, y_rear, 0.285)))

    # Right side margin
    f_sp_r = bm.faces.new([v_sp_br, v_rc_sp_b, v_rc_sp_t, v_sp_tr])
    f_sp_r.material_index = 0; set_face_uv_rect(bm, f_sp_r, UV_CASING_PLASTIC)

    # Under sticker margin
    f_sp_under = bm.faces.new([v_mid2_cx, v_mid2_r, v_rc_sp_b, v_sp_bl])
    f_sp_under.material_index = 0; set_face_uv_rect(bm, f_sp_under, UV_CASING_PLASTIC)

    # Above sticker louver/casing quad
    v_sp_top_c = bm.verts.new(Vector((x_spec_l, y_rear, 0.285)))
    f_sp_top = bm.faces.new([v_sp_tl, v_sp_tr, v_rc_upt, v_sp_top_c])
    f_sp_top.material_index = 0
    set_face_uv_rect(bm, f_sp_top, UV_LOUVERS)

    f_sp_c_fill = bm.faces.new([v_lv_t, v_sp_tl, v_sp_top_c])
    f_sp_c_fill.material_index = 0; set_face_uv_rect(bm, f_sp_c_fill, UV_CASING_PLASTIC)

    # Top forehead strip above panels
    f_top_strip = bm.faces.new([v_lv_lt, v_rc_upt, v_rear[2], v_rear[3]])
    f_top_strip.material_index = 0; set_face_uv_rect(bm, f_top_strip, UV_CASING_PLASTIC)

    # 4. Four Rear BNC Coaxial Connectors Inside the Bay (VIDEO A IN, OUT, B IN, OUT)
    r_bnc = 0.0055
    z_bnc = 0.100
    y_bnc_base = y_bay_in
    y_bnc_tip = y_rear - 0.008

    # Aligned with UV targets in UV_REAR_BAY (flip_u=False)
    # Target centers in bay: X = -0.074, -0.0315, +0.011, +0.054
    bnc_xs = [-0.074, -0.0315, 0.011, 0.054]
    for b_idx, sx_b in enumerate(bnc_xs):
        v_bb = []
        v_bt = []
        for i in range(6):
            ang = 2.0 * math.pi * i / 6
            xb = sx_b + r_bnc * math.cos(ang)
            zb = z_bnc + r_bnc * math.sin(ang)
            v_bb.append(bm.verts.new(Vector((xb, y_bnc_base, zb))))
            v_bt.append(bm.verts.new(Vector((xb, y_bnc_tip, zb))))

        for i in range(6):
            ni = (i + 1) % 6
            fb = bm.faces.new([v_bb[i], v_bb[ni], v_bt[ni], v_bt[i]])
            fb.material_index = 2  # M_Metal
            set_face_uv_rect(bm, fb, UV_HARDWARE_CHROME)

        f_btop = bm.faces.new(list(reversed(v_bt)))
        f_btop.material_index = 2
        set_face_uv_rect(bm, f_btop, UV_HARDWARE_CHROME)

    # 4b. Rear AC Power Socket (IEC 3-prong socket block on far right of bay, X = +0.078, Z = 0.075)
    w_pwr, h_pwr = 0.010, 0.008
    x_ac = 0.076
    z_ac = 0.075
    v_pb = [
        bm.verts.new(Vector((x_ac - w_pwr, y_bay_in, z_ac - h_pwr))),
        bm.verts.new(Vector((x_ac + w_pwr, y_bay_in, z_ac - h_pwr))),
        bm.verts.new(Vector((x_ac + w_pwr, y_bay_in, z_ac + h_pwr))),
        bm.verts.new(Vector((x_ac - w_pwr, y_bay_in, z_ac + h_pwr)))
    ]
    v_pt = [
        bm.verts.new(Vector((x_ac - w_pwr, y_rear - 0.002, z_ac - h_pwr))),
        bm.verts.new(Vector((x_ac + w_pwr, y_rear - 0.002, z_ac - h_pwr))),
        bm.verts.new(Vector((x_ac + w_pwr, y_rear - 0.002, z_ac + h_pwr))),
        bm.verts.new(Vector((x_ac - w_pwr, y_rear - 0.002, z_ac + h_pwr)))
    ]
    for i in range(4):
        ni = (i + 1) % 4
        f = bm.faces.new([v_pb[i], v_pb[ni], v_pt[ni], v_pt[i]])
        f.material_index = 0; set_face_uv_rect(bm, f, UV_CASING_PLASTIC)
    f_pwr_top = bm.faces.new(list(reversed(v_pt)))
    f_pwr_top.material_index = 0; set_face_uv_rect(bm, f_pwr_top, UV_CASING_PLASTIC)

    # 5. Four Bottom Molded Rubber Feet (Resting at Z = 0.000m)
    r_foot = 0.014
    for sx_f in [-0.140, 0.140]:
        for sy_f in [0.040, -0.020]:
            v_fb = []
            v_ft = []
            for i in range(6):
                ang = 2.0 * math.pi * i / 6
                xf = sx_f + r_foot * math.cos(ang)
                yf = sy_f + r_foot * math.sin(ang)
                v_fb.append(bm.verts.new(Vector((xf, yf, 0.000))))
                v_ft.append(bm.verts.new(Vector((xf, yf, z_bot))))

            for i in range(6):
                ni = (i + 1) % 6
                f = bm.faces.new([v_fb[i], v_ft[i], v_ft[ni], v_fb[ni]])
                f.material_index = 0
                set_face_uv_rect(bm, f, UV_CASING_PLASTIC)

            f_fbot = bm.faces.new(list(reversed(v_fb)))
            f_fbot.material_index = 0
            set_face_uv_rect(bm, f_fbot, UV_CASING_PLASTIC)

    # 6. Two Side Recessed Carrying Handles on Left and Right (X = ±0.180m, Y = 0.015m, Z = 0.170m)
    for s_x in [-0.180, 0.180]:
        sign = -1.0 if s_x < 0 else 1.0
        hw = 0.035
        hh = 0.018
        v_h_out = [
            bm.verts.new(Vector((s_x, 0.015 - hw, 0.170 - hh))),
            bm.verts.new(Vector((s_x, 0.015 + hw, 0.170 - hh))),
            bm.verts.new(Vector((s_x, 0.015 + hw, 0.170 + hh))),
            bm.verts.new(Vector((s_x, 0.015 - hw, 0.170 + hh)))
        ]
        v_h_in = [
            bm.verts.new(Vector((s_x - sign * 0.012, 0.015 - hw + 0.005, 0.170 - hh + 0.004))),
            bm.verts.new(Vector((s_x - sign * 0.012, 0.015 + hw - 0.005, 0.170 - hh + 0.004))),
            bm.verts.new(Vector((s_x - sign * 0.012, 0.015 + hw - 0.005, 0.170 + hh - 0.004))),
            bm.verts.new(Vector((s_x - sign * 0.012, 0.015 - hw + 0.005, 0.170 + hh - 0.004)))
        ]
        for i in range(4):
            ni = (i + 1) % 4
            f = bm.faces.new([v_h_out[i], v_h_out[ni], v_h_in[ni], v_h_in[i]] if sign > 0 else [v_h_out[ni], v_h_out[i], v_h_in[i], v_h_in[ni]])
            f.material_index = 0; set_face_uv_rect(bm, f, UV_CASING_PLASTIC)
        f_h_floor = bm.faces.new(list(reversed(v_h_in)) if sign > 0 else v_h_in)
        f_h_floor.material_index = 0; set_face_uv_rect(bm, f_h_floor, UV_CASING_PLASTIC)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_screen_bezel_mesh(mesh, materials):
    """
    Build Screen_Bezel:
    Iconic 1990s curved front monitor bezel framing the CRT glass tube:
    - 45° outer chamfers around outer front edges
    - Deep picture-frame inner bezel that slopes inward to meet the glass tube
    - Lower chin control shelf (Z: 0.023 to 0.075m, Y = 0.092m) mapped to UV_CHIN_PANEL
    - 4:3 aperture window for the CRT screen (Width 280mm, Height 210mm)
    Tris count: ~46 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_out = 0.180
    z_bot = 0.015
    z_top = 0.330
    y_seam = 0.070
    y_front = 0.092
    c_rim = 0.008

    # Outer front rim vertices
    v_rim_b = [
        bm.verts.new(Vector((-x_out, y_seam, z_bot))),
        bm.verts.new(Vector(( x_out, y_seam, z_bot))),
        bm.verts.new(Vector(( x_out, y_seam, z_top))),
        bm.verts.new(Vector((-x_out, y_seam, z_top)))
    ]
    v_rim_f = [
        bm.verts.new(Vector((-x_out + c_rim, y_front, z_bot + c_rim))),
        bm.verts.new(Vector(( x_out - c_rim, y_front, z_bot + c_rim))),
        bm.verts.new(Vector(( x_out - c_rim, y_front, z_top - c_rim))),
        bm.verts.new(Vector((-x_out + c_rim, y_front, z_top - c_rim)))
    ]

    f_ob_b = bm.faces.new([v_rim_b[0], v_rim_b[1], v_rim_f[1], v_rim_f[0]]); f_ob_b.material_index = 0; set_face_uv_rect(bm, f_ob_b, UV_CASING_PLASTIC)
    f_ob_r = bm.faces.new([v_rim_b[1], v_rim_b[2], v_rim_f[2], v_rim_f[1]]); f_ob_r.material_index = 0; set_face_uv_rect(bm, f_ob_r, UV_CASING_PLASTIC)
    f_ob_t = bm.faces.new([v_rim_b[2], v_rim_b[3], v_rim_f[3], v_rim_f[2]]); f_ob_t.material_index = 0; set_face_uv_rect(bm, f_ob_t, UV_CASING_PLASTIC)
    f_ob_l = bm.faces.new([v_rim_b[3], v_rim_b[0], v_rim_f[0], v_rim_f[3]]); f_ob_l.material_index = 0; set_face_uv_rect(bm, f_ob_l, UV_CASING_PLASTIC)

    # 2. Lower Chin Control Shelf (Z: 0.023 to 0.075m, Y = 0.092m)
    z_chin_top = 0.075
    v_chin_tl = bm.verts.new(Vector((-x_out + c_rim, y_front, z_chin_top)))
    v_chin_tr = bm.verts.new(Vector(( x_out - c_rim, y_front, z_chin_top)))

    f_chin = bm.faces.new([v_rim_f[0], v_rim_f[1], v_chin_tr, v_chin_tl])
    f_chin.material_index = 0
    # flip_u=True so Left on monitor (+X) matches Left on texture (U=0)!
    set_face_uv_rect(bm, f_chin, UV_CHIN_PANEL, flip_u=True)

    # 3. Inner Sloping CRT Tube Bezel Frame
    x_in = 0.140
    z_in_b = 0.095
    z_in_t = 0.310
    y_glass_rim = 0.076

    v_ap_b = [
        bm.verts.new(Vector((-x_in, y_glass_rim, z_in_b))),
        bm.verts.new(Vector(( x_in, y_glass_rim, z_in_b))),
        bm.verts.new(Vector(( x_in, y_glass_rim, z_in_t))),
        bm.verts.new(Vector((-x_in, y_glass_rim, z_in_t)))
    ]

    # Inward bevel slopes
    f_sl_b = bm.faces.new([v_chin_tl, v_chin_tr, v_ap_b[1], v_ap_b[0]])
    f_sl_b.material_index = 0; set_face_uv_rect(bm, f_sl_b, UV_CASING_PLASTIC)

    f_sl_r = bm.faces.new([v_chin_tr, v_rim_f[2], v_ap_b[2], v_ap_b[1]])
    f_sl_r.material_index = 0; set_face_uv_rect(bm, f_sl_r, UV_CASING_PLASTIC)

    f_sl_t = bm.faces.new([v_rim_f[2], v_rim_f[3], v_ap_b[3], v_ap_b[2]])
    f_sl_t.material_index = 0; set_face_uv_rect(bm, f_sl_t, UV_CASING_PLASTIC)

    f_sl_l = bm.faces.new([v_rim_f[3], v_chin_tl, v_ap_b[0], v_ap_b[3]])
    f_sl_l.material_index = 0; set_face_uv_rect(bm, f_sl_l, UV_CASING_PLASTIC)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_screen_surface_mesh(mesh, materials):
    """
    Build Screen_Surface:
    Iconic curved CRT vacuum glass tube face:
    - Separate mesh assigned strictly to Slot 1: M_Screen!
    - Non-flat curved geometry: authentic spherical bulge
    - 8x7 curved quad grid (56 quads = 112 tris)
    - Full 1:1 UV mapping displaying CRT surveillance scanlines, camera timecode, OSD
    Tris count: ~112 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    x_min, x_max = -0.140, 0.140
    z_min, z_max =  0.095, 0.310
    y_base = 0.076  # Rim depth
    y_bulge = 0.0075 # 7.5mm organic convex bulge in center

    nx = 8
    nz = 7
    grid_verts = []

    for j in range(nz + 1):
        row = []
        vz = z_min + (z_max - z_min) * (j / nz)
        v_fac = (j / nz - 0.5) * 2.0
        for i in range(nx + 1):
            vx = x_min + (x_max - x_min) * (i / nx)
            u_fac = (i / nx - 0.5) * 2.0

            dist_sq = (u_fac * 0.9)**2 + (v_fac * 0.8)**2
            vy = y_base + y_bulge * max(0.0, 1.0 - dist_sq)
            row.append(bm.verts.new(Vector((vx, vy, vz))))
        grid_verts.append(row)

    uv_lay = bm.loops.layers.uv.verify()
    for j in range(nz):
        for i in range(nx):
            v0 = grid_verts[j][i]
            v1 = grid_verts[j][i+1]
            v2 = grid_verts[j+1][i+1]
            v3 = grid_verts[j+1][i]

            f = bm.faces.new([v0, v1, v2, v3])
            f.material_index = 1  # M_Screen!

            # Flip U so OSD reads left to right looking from front!
            u_coords = [1.0 - (i / nx), 1.0 - ((i + 1) / nx), 1.0 - ((i + 1) / nx), 1.0 - (i / nx)]
            v_coords = [j / nz, j / nz, (j + 1) / nz, (j + 1) / nz]

            for k, loop in enumerate(f.loops):
                loop[uv_lay].uv = (u_coords[k], v_coords[k])

    for edge in bm.edges:
        edge.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_control_button_array_mesh(mesh, materials):
    """
    Build Control_Button_Array:
    Physical tactile 1990s pushbuttons, rotary potentiometer dials & power switch:
    - Power rocker switch (far right looking from front: X = -0.149m, Z = 0.038m)
    - 3D Status LED (X = -0.149m, Z = 0.056m)
    - 3 Rotary Potentiometer Dials (BRIGHT, CONTR, COLOR at X = +0.048, +0.011, -0.026m)
    - 4 Camera Channel Selector Buttons (CH 1..4 at X = -0.066, -0.084, -0.101, -0.119m)
    All precisely aligned with the graphics on T_Security_Atlas.
    Tris count: ~118 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    y_chin = 0.092
    y_knob_top = 0.102
    y_btn_out = 0.098

    # 1. Power Rocker Switch (far right looking from front: X = -0.149, Z = 0.038)
    pw_half_w = 0.009
    pw_half_h = 0.006
    px_pwr = -0.149
    pz_pwr = 0.038

    v_pb = [
        bm.verts.new(Vector((px_pwr - pw_half_w, y_chin, pz_pwr - pw_half_h))),
        bm.verts.new(Vector((px_pwr + pw_half_w, y_chin, pz_pwr - pw_half_h))),
        bm.verts.new(Vector((px_pwr + pw_half_w, y_chin, pz_pwr + pw_half_h))),
        bm.verts.new(Vector((px_pwr - pw_half_w, y_chin, pz_pwr + pw_half_h)))
    ]
    v_pt = [
        bm.verts.new(Vector((px_pwr - pw_half_w, y_btn_out, pz_pwr - pw_half_h))),
        bm.verts.new(Vector((px_pwr + pw_half_w, y_btn_out, pz_pwr - pw_half_h))),
        bm.verts.new(Vector((px_pwr + pw_half_w, y_btn_out, pz_pwr + pw_half_h))),
        bm.verts.new(Vector((px_pwr - pw_half_w, y_btn_out, pz_pwr + pw_half_h)))
    ]
    for i in range(4):
        ni = (i + 1) % 4
        f = bm.faces.new([v_pb[i], v_pb[ni], v_pt[ni], v_pt[i]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_CASING_PLASTIC)
    f_ptop = bm.faces.new(list(reversed(v_pt)))
    f_ptop.material_index = 0
    set_face_uv_rect(bm, f_ptop, UV_BUTTON_CAPS, flip_u=True)

    # 1b. 3D Status LED (X = -0.149, Z = 0.056)
    r_led = 0.003
    v_lb = []
    v_lt = []
    for i in range(6):
        ang = 2.0 * math.pi * i / 6
        xl = px_pwr + r_led * math.cos(ang)
        zl = 0.056 + r_led * math.sin(ang)
        v_lb.append(bm.verts.new(Vector((xl, y_chin, zl))))
        v_lt.append(bm.verts.new(Vector((xl, y_chin + 0.0035, zl))))

    for i in range(6):
        ni = (i + 1) % 6
        f = bm.faces.new([v_lb[i], v_lb[ni], v_lt[ni], v_lt[i]])
        f.material_index = 0
        set_face_uv_rect(bm, f, UV_CHIN_PANEL)
    f_ltop = bm.faces.new(list(reversed(v_lt)))
    f_ltop.material_index = 0
    set_face_uv_rect(bm, f_ltop, UV_CHIN_PANEL)

    # 2. Three Rotary Potentiometers (BRIGHT, CONTR, COLOR)
    # Aligned with circular tick graphics: X = +0.048, +0.011, -0.026
    r_knob = 0.0075
    z_knob = 0.049
    knob_xs = [0.048, 0.011, -0.026]

    for sx_k in knob_xs:
        v_kb = []
        v_kt = []
        for i in range(8):
            ang = 2.0 * math.pi * i / 8
            xk = sx_k + r_knob * math.cos(ang)
            zk = z_knob + r_knob * math.sin(ang)
            v_kb.append(bm.verts.new(Vector((xk, y_chin, zk))))
            v_kt.append(bm.verts.new(Vector((xk, y_knob_top, zk))))

        for i in range(8):
            ni = (i + 1) % 8
            f = bm.faces.new([v_kb[i], v_kb[ni], v_kt[ni], v_kt[i]])
            f.material_index = 0
            set_face_uv_rect(bm, f, UV_CASING_PLASTIC)

        f_ktop = bm.faces.new(list(reversed(v_kt)))
        f_ktop.material_index = 0
        set_face_uv_rect(bm, f_ktop, UV_BUTTON_CAPS, flip_u=True)

    # 3. Four Camera Channel Selector Buttons (CH 1..4)
    # Aligned with CH 1..4 outlines on texture: X = -0.066, -0.084, -0.101, -0.119
    bw_half = 0.0065
    bh_half = 0.0055
    btn_xs = [-0.066, -0.084, -0.101, -0.119]

    for sx_c in btn_xs:
        v_cb = [
            bm.verts.new(Vector((sx_c - bw_half, y_chin, z_knob - bh_half))),
            bm.verts.new(Vector((sx_c + bw_half, y_chin, z_knob - bh_half))),
            bm.verts.new(Vector((sx_c + bw_half, y_chin, z_knob + bh_half))),
            bm.verts.new(Vector((sx_c - bw_half, y_chin, z_knob + bh_half)))
        ]
        v_ct = [
            bm.verts.new(Vector((sx_c - bw_half, y_btn_out, z_knob - bh_half))),
            bm.verts.new(Vector((sx_c + bw_half, y_btn_out, z_knob - bh_half))),
            bm.verts.new(Vector((sx_c + bw_half, y_btn_out, z_knob + bh_half))),
            bm.verts.new(Vector((sx_c - bw_half, y_btn_out, z_knob + bh_half)))
        ]

        for i in range(4):
            ni = (i + 1) % 4
            f = bm.faces.new([v_cb[i], v_cb[ni], v_ct[ni], v_ct[i]])
            f.material_index = 0
            set_face_uv_rect(bm, f, UV_CASING_PLASTIC)

        f_ctop = bm.faces.new(list(reversed(v_ct)))
        f_ctop.material_index = 0
        set_face_uv_rect(bm, f_ctop, UV_BUTTON_CAPS, flip_u=True)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_vent_grille_mesh(mesh, materials):
    """
    Build Vent_Grille:
    Industrial CRT heat dissipation ventilation louvers:
    - Top cooling vent bank (Z = 0.330m, 5 raised louvers)
    Tris count: ~50 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    z_top = 0.330
    x_half = 0.130

    # Top Cooling Vent Slats (5 louvers along top surface)
    for sy_v in [0.035, 0.015, -0.005, -0.025, -0.045]:
        v_vb = [
            bm.verts.new(Vector((-x_half, sy_v - 0.006, z_top))),
            bm.verts.new(Vector(( x_half, sy_v - 0.006, z_top))),
            bm.verts.new(Vector(( x_half, sy_v + 0.006, z_top))),
            bm.verts.new(Vector((-x_half, sy_v + 0.006, z_top)))
        ]
        v_vt = [
            bm.verts.new(Vector((-x_half, sy_v - 0.004, z_top + 0.0035))),
            bm.verts.new(Vector(( x_half, sy_v - 0.004, z_top + 0.0035))),
            bm.verts.new(Vector(( x_half, sy_v + 0.004, z_top + 0.0035))),
            bm.verts.new(Vector((-x_half, sy_v + 0.004, z_top + 0.0035)))
        ]

        for i in range(4):
            ni = (i + 1) % 4
            f = bm.faces.new([v_vb[i], v_vb[ni], v_vt[ni], v_vt[i]])
            f.material_index = 0
            set_face_uv_rect(bm, f, UV_LOUVERS)

        f_vtop = bm.faces.new(list(reversed(v_vt)))
        f_vtop.material_index = 0
        set_face_uv_rect(bm, f_vtop, UV_LOUVERS)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, 35.0)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Main Assembly & Rigorous QA Pipeline
# -------------------------------------------------------------

def assemble_and_export():
    """Assemble the complete asset, apply hierarchy, export FBX and run automated QA."""
    setup_clean_scene()
    atlas_img, screen_img = load_or_create_textures()
    materials = create_materials(atlas_img, screen_img)

    # 1. Create Root Empty
    root_empty = bpy.data.objects.new("SEC_Monitor_CRT_90s", None)
    root_empty.empty_display_type = 'PLAIN_AXES'
    root_empty.empty_display_size = 0.20
    root_empty.location = Vector((0.0, 0.0, 0.0))
    bpy.context.collection.objects.link(root_empty)

    # 2. CRT_Housing (child of Root)
    mesh_housing = bpy.data.meshes.new("CRT_Housing")
    obj_housing = bpy.data.objects.new("CRT_Housing", mesh_housing)
    build_crt_housing_mesh(mesh_housing, materials)
    bpy.context.collection.objects.link(obj_housing)
    obj_housing.parent = root_empty

    # 3. Screen_Bezel (child of CRT_Housing)
    mesh_bezel = bpy.data.meshes.new("Screen_Bezel")
    obj_bezel = bpy.data.objects.new("Screen_Bezel", mesh_bezel)
    build_screen_bezel_mesh(mesh_bezel, materials)
    bpy.context.collection.objects.link(obj_bezel)
    obj_bezel.parent = obj_housing

    # 4. Screen_Surface (child of CRT_Housing)
    mesh_screen = bpy.data.meshes.new("Screen_Surface")
    obj_screen = bpy.data.objects.new("Screen_Surface", mesh_screen)
    build_screen_surface_mesh(mesh_screen, materials)
    bpy.context.collection.objects.link(obj_screen)
    obj_screen.parent = obj_housing

    # 5. Control_Button_Array (child of CRT_Housing)
    mesh_buttons = bpy.data.meshes.new("Control_Button_Array")
    obj_buttons = bpy.data.objects.new("Control_Button_Array", mesh_buttons)
    build_control_button_array_mesh(mesh_buttons, materials)
    bpy.context.collection.objects.link(obj_buttons)
    obj_buttons.parent = obj_housing

    # 6. Vent_Grille (child of CRT_Housing)
    mesh_vents = bpy.data.meshes.new("Vent_Grille")
    obj_vents = bpy.data.objects.new("Vent_Grille", mesh_vents)
    build_vent_grille_mesh(mesh_vents, materials)
    bpy.context.collection.objects.link(obj_vents)
    obj_vents.parent = obj_housing

    # Update scene
    bpy.context.view_layer.update()

    # Save Blend file
    blend_path = os.path.join(EXPORTS_DIR, "SEC_Monitor_CRT_90s.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[INFO] Saved blend file: {blend_path}")

    # Select all objects for FBX export
    bpy.ops.object.select_all(action='DESELECT')
    root_empty.select_set(True)
    for obj in [obj_housing, obj_bezel, obj_screen, obj_buttons, obj_vents]:
        obj.select_set(True)

    fbx_path = os.path.join(EXPORTS_DIR, "SEC_Monitor_CRT_90s.fbx")
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

    # Automated Re-Import QA
    print("\n--- RUNNING AUTOMATED QA ON FBX ---")
    setup_clean_scene()
    bpy.ops.import_scene.fbx(filepath=fbx_path)

    qa_objects = {obj.name: obj for obj in bpy.context.scene.objects}
    print(f"[QA] Imported objects: {list(qa_objects.keys())}")

    # Validate Root
    assert "SEC_Monitor_CRT_90s" in qa_objects, "Root empty missing!"
    root_qa = qa_objects["SEC_Monitor_CRT_90s"]
    assert root_qa.location.length < 1e-4, f"Root location not at origin: {root_qa.location}"

    # Validate Children
    expected_meshes = ["CRT_Housing", "Screen_Bezel", "Screen_Surface", "Control_Button_Array", "Vent_Grille"]
    total_tris = 0

    for m_name in expected_meshes:
        assert m_name in qa_objects, f"Mesh {m_name} missing from FBX!"
        m_obj = qa_objects[m_name]
        
        # Calculate real triangles
        bm_qa = bmesh.new()
        bm_qa.from_mesh(m_obj.data)
        bmesh.ops.triangulate(bm_qa, faces=bm_qa.faces)
        tris = len(bm_qa.faces)
        total_tris += tris
        bm_qa.free()

        # Validate UV layer
        assert len(m_obj.data.uv_layers) > 0, f"Mesh {m_name} has no UV layer!"

        # Validate Material Slots
        mat_names = [slot.name for slot in m_obj.material_slots]
        assert "M_Security_Atlas" in mat_names, f"Mesh {m_name} missing M_Security_Atlas!"
        assert "M_Screen" in mat_names, f"Mesh {m_name} missing M_Screen!"
        assert "M_Metal" in mat_names, f"Mesh {m_name} missing M_Metal!"

    print(f"[QA] TOTAL TRIANGLES: {total_tris} (Budget limit: 650)")
    assert total_tris <= 650, f"Triangle budget exceeded: {total_tris} > 650!"

    manifest_data = {
        "SEC_Monitor_CRT_90s": {
            "asset_name": "SEC_Monitor_CRT_90s",
            "fbx_path": "exports/SEC_Monitor_CRT_90s.fbx",
            "tris_count": total_tris,
            "mesh_count": len(expected_meshes),
            "empty_count": 1,
            "materials": ["M_Security_Atlas", "M_Screen", "M_Metal"],
            "status": "SUCCESS"
        }
    }
    manifest_path = os.path.join(EXPORTS_DIR, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[QA] Manifest written to {manifest_path}")
    print("[QA] ALL CHECKS PASSED SUCCESSFULLY!\n")


if __name__ == "__main__":
    assemble_and_export()
