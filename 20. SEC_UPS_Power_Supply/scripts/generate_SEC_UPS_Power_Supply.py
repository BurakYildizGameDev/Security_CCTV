"""
=============================================================================
Security CCTV Asset Production Suite - Asset 20
Asset Name: SEC_UPS_Power_Supply
Category: Industrial Uninterruptible Power Supply (Tower UPS)
Target Polycount Budget: <= 450 Triangles
Hierarchy & Pivot:
    SEC_UPS_Power_Supply (Root Empty at (0, 0, 0) bottom center on floor)
     └── Main_Housing (Mesh, root child, Slot 0, Slot 1, Slot 2, Slot 3)
          ├── Front_Panel (Mesh, housing child, Slot 0, Slot 1, Slot 2, Slot 3)
          │    ├── Status_Display (Mesh, Front_Panel child, Slot 1)
          │    └── Power_Button (Mesh, Front_Panel child, Slot 0 & Slot 2)
          └── Vent_Grille (Mesh, housing child, Slot 0)
Material Slots:
    Slot 0: M_Security_Atlas (Dark graphite casing, rear I/O, front fascia)
    Slot 1: M_Screen (Backlit LCD telemetry display)
    Slot 2: M_Emission (Front status LEDs, illuminated power standby ring)
    Slot 3: M_Metal (Chassis steel plates, bottom rubber feet)
Output:
    - exports/SEC_UPS_Power_Supply.fbx
    - exports/SEC_UPS_Power_Supply.blend
    - exports/T_Security_Atlas.png
    - exports/T_Screen.png
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")
SCREEN_PATH = os.path.join(EXPORTS_DIR, "T_Screen.png")
FBX_OUT = os.path.join(EXPORTS_DIR, "SEC_UPS_Power_Supply.fbx")
BLEND_OUT = os.path.join(EXPORTS_DIR, "SEC_UPS_Power_Supply.blend")
MANIFEST_PATH = os.path.join(EXPORTS_DIR, "manifest.json")

# UV Zones Normalized
UV_SAFE_NEUTRAL = Vector((1890.0 / 2048.0, 1.0 - 1200.0 / 2048.0))

# Front Fascia UV Box (Zone 0) - Width 820 px, Height 1750 px (matches 3D W=0.100m, H=0.214m)
UV_FRONT_U0 = 40.0 / 2048.0
UV_FRONT_U1 = 860.0 / 2048.0
UV_FRONT_V0 = 1.0 - 1790.0 / 2048.0
UV_FRONT_V1 = 1.0 - 40.0 / 2048.0

# Rear I/O UV Box (Zone 2) - Width 790 px, Height 1750 px (matches 3D W=0.092m, H=0.204m)
UV_REAR_U0 = 890.0 / 2048.0
UV_REAR_U1 = 1680.0 / 2048.0
UV_REAR_V0 = 1.0 - 1790.0 / 2048.0
UV_REAR_V1 = 1.0 - 40.0 / 2048.0

# Rating Plate UV Box (Zone 3) - Width 640 px, Height 228 px (matches 3D W=0.140m, H=0.050m)
UV_RATING_U0 = 40.0 / 2048.0
UV_RATING_U1 = 680.0 / 2048.0
UV_RATING_V0 = 1.0 - 2038.0 / 2048.0
UV_RATING_V1 = 1.0 - 1810.0 / 2048.0

# Side Louvers UV Box (Zone 4)
UV_LOUVER_U0 = 720.0 / 2048.0
UV_LOUVER_U1 = 1720.0 / 2048.0
UV_LOUVER_V0 = 1.0 - 2038.0 / 2048.0
UV_LOUVER_V1 = 1.0 - 1810.0 / 2048.0

# Power Button Face UV Box (Zone 1) - Center (1870, 190), Rad 140
UV_BTN_CX = 1870.0 / 2048.0
UV_BTN_CY = 1.0 - 190.0 / 2048.0
UV_BTN_RAD = 140.0 / 2048.0


def reset_scene():
    """Clear all objects, meshes, materials, and textures."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    bpy.context.scene.unit_settings.length_unit = 'METERS'


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


def create_materials():
    """Create the 4 standard materials with matching diffuse_color for Solid Mode."""
    mats = []

    # Slot 0: M_Security_Atlas (Dark Charcoal/Graphite)
    m_atlas = bpy.data.materials.new(name="M_Security_Atlas")
    m_atlas.use_nodes = True
    m_atlas.diffuse_color = (0.10, 0.11, 0.13, 1.0) # Solid mode color
    nodes0 = m_atlas.node_tree.nodes
    nodes0.clear()
    bsdf0 = nodes0.new(type="ShaderNodeBsdfPrincipled")
    bsdf0.location = (0, 0)
    bsdf0.inputs["Roughness"].default_value = 0.40
    bsdf0.inputs["Metallic"].default_value = 0.15
    out0 = nodes0.new(type="ShaderNodeOutputMaterial")
    out0.location = (300, 0)
    m_atlas.node_tree.links.new(bsdf0.outputs["BSDF"], out0.inputs["Surface"])

    if os.path.exists(ATLAS_PATH):
        img_atlas = bpy.data.images.load(ATLAS_PATH)
        tex_node0 = nodes0.new(type="ShaderNodeTexImage")
        tex_node0.location = (-350, 0)
        tex_node0.image = img_atlas
        m_atlas.node_tree.links.new(tex_node0.outputs["Color"], bsdf0.inputs["Base Color"])
    mats.append(m_atlas)

    # Slot 1: M_Screen (Deep Cyan-Teal Backlit LCD Glass)
    m_screen = bpy.data.materials.new(name="M_Screen")
    m_screen.use_nodes = True
    m_screen.diffuse_color = (0.01, 0.16, 0.26, 1.0) # Solid mode color
    nodes1 = m_screen.node_tree.nodes
    nodes1.clear()
    bsdf1 = nodes1.new(type="ShaderNodeBsdfPrincipled")
    bsdf1.location = (0, 0)
    bsdf1.inputs["Roughness"].default_value = 0.10
    bsdf1.inputs["Metallic"].default_value = 0.05
    out1 = nodes1.new(type="ShaderNodeOutputMaterial")
    out1.location = (300, 0)
    m_screen.node_tree.links.new(bsdf1.outputs["BSDF"], out1.inputs["Surface"])

    if os.path.exists(SCREEN_PATH):
        img_screen = bpy.data.images.load(SCREEN_PATH)
        tex_node1 = nodes1.new(type="ShaderNodeTexImage")
        tex_node1.location = (-350, 0)
        tex_node1.image = img_screen
        m_screen.node_tree.links.new(tex_node1.outputs["Color"], bsdf1.inputs["Base Color"])
        m_screen.node_tree.links.new(tex_node1.outputs["Color"], bsdf1.inputs["Emission Color"])
        bsdf1.inputs["Emission Strength"].default_value = 1.80
    mats.append(m_screen)

    # Slot 2: M_Emission (Bright Neon Cyan / Turquoise Glow)
    m_emission = bpy.data.materials.new(name="M_Emission")
    m_emission.use_nodes = True
    m_emission.diffuse_color = (0.0, 0.95, 1.0, 1.0) # Solid mode color
    nodes2 = m_emission.node_tree.nodes
    nodes2.clear()
    bsdf2 = nodes2.new(type="ShaderNodeBsdfPrincipled")
    bsdf2.location = (0, 0)
    bsdf2.inputs["Base Color"].default_value = (0.0, 0.95, 1.0, 1.0)
    bsdf2.inputs["Emission Color"].default_value = (0.0, 0.95, 1.0, 1.0)
    bsdf2.inputs["Emission Strength"].default_value = 6.0
    out2 = nodes2.new(type="ShaderNodeOutputMaterial")
    out2.location = (300, 0)
    m_emission.node_tree.links.new(bsdf2.outputs["BSDF"], out2.inputs["Surface"])
    mats.append(m_emission)

    # Slot 3: M_Metal (Dark Anodized Gunmetal / Rubber Footing)
    m_metal = bpy.data.materials.new(name="M_Metal")
    m_metal.use_nodes = True
    m_metal.diffuse_color = (0.22, 0.24, 0.28, 1.0) # Solid mode color
    nodes3 = m_metal.node_tree.nodes
    nodes3.clear()
    bsdf3 = nodes3.new(type="ShaderNodeBsdfPrincipled")
    bsdf3.location = (0, 0)
    bsdf3.inputs["Base Color"].default_value = (0.16, 0.17, 0.20, 1.0)
    bsdf3.inputs["Roughness"].default_value = 0.25
    bsdf3.inputs["Metallic"].default_value = 0.85
    out3 = nodes3.new(type="ShaderNodeOutputMaterial")
    out3.location = (300, 0)
    m_metal.node_tree.links.new(bsdf3.outputs["BSDF"], out3.inputs["Surface"])
    mats.append(m_metal)

    return mats


def assign_material_slots(obj, materials, primary_slot=0):
    """Assign the full material list in standard slot order (0 to 3)."""
    for mat in materials:
        obj.data.materials.append(mat)
    obj.active_material_index = primary_slot


# =============================================================================
# MESH BUILDERS
# =============================================================================

def build_main_housing(materials):
    """Build the steel tower chassis box, recessed rear I/O cavity, rating badge, and bottom feet."""
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    hw = 0.050        # Half-width (X: -0.050 to +0.050)
    ch = 0.003        # Top chamfer (X: +/-0.047)
    z_bot = 0.006     # Bottom above feet
    z_top = 0.220     # Top surface
    z_ch = z_top - ch # Chamfer start height (0.217)

    y_back_rim = -0.165
    y_back_io  = -0.153 # Recessed rear cavity (12mm recess)
    y_front_flange = +0.135

    # --- 1. CHASSIS OUTER SHELL ---
    v_top_fl = bm.verts.new((-hw + ch, y_front_flange, z_top))
    v_top_fr = bm.verts.new((+hw - ch, y_front_flange, z_top))
    v_top_br = bm.verts.new((+hw - ch, y_back_rim, z_top))
    v_top_bl = bm.verts.new((-hw + ch, y_back_rim, z_top))
    f_top = bm.faces.new([v_top_fl, v_top_fr, v_top_br, v_top_bl])
    f_top.material_index = 0
    for l in f_top.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    v_side_tfl = bm.verts.new((-hw, y_front_flange, z_ch))
    v_side_tbl = bm.verts.new((-hw, y_back_rim, z_ch))
    f_ch_l = bm.faces.new([v_top_bl, v_side_tbl, v_side_tfl, v_top_fl])
    f_ch_l.material_index = 0
    for l in f_ch_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    v_side_tfr = bm.verts.new((+hw, y_front_flange, z_ch))
    v_side_tbr = bm.verts.new((+hw, y_back_rim, z_ch))
    f_ch_r = bm.faces.new([v_top_fr, v_side_tfr, v_side_tbr, v_top_br])
    f_ch_r.material_index = 0
    for l in f_ch_r.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    v_bot_fl = bm.verts.new((-hw, y_front_flange, z_bot))
    v_bot_fr = bm.verts.new((+hw, y_front_flange, z_bot))
    v_bot_br = bm.verts.new((+hw, y_back_rim, z_bot))
    v_bot_bl = bm.verts.new((-hw, y_back_rim, z_bot))
    f_bot = bm.faces.new([v_bot_bl, v_bot_br, v_bot_fr, v_bot_fl])
    f_bot.material_index = 0
    for l in f_bot.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Left side wall (-X = -0.050):
    f_side_l = bm.faces.new([v_side_tbl, v_side_tfl, v_bot_fl, v_bot_bl])
    f_side_l.material_index = 0
    for l in f_side_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Right side wall (+X = +0.050):
    # Technical Rating Plate (140mm x 50mm, 2.8:1 aspect ratio)
    y_rb_0 = -0.070
    y_rb_1 = +0.070
    z_rb_0 = 0.035
    z_rb_1 = 0.085

    v_rb_bl = bm.verts.new((+hw, y_rb_0, z_rb_0))
    v_rb_br = bm.verts.new((+hw, y_rb_1, z_rb_0))
    v_rb_tr = bm.verts.new((+hw, y_rb_1, z_rb_1))
    v_rb_tl = bm.verts.new((+hw, y_rb_0, z_rb_1))

    f_badge = bm.faces.new([v_rb_bl, v_rb_br, v_rb_tr, v_rb_tl])
    f_badge.material_index = 0
    for l in f_badge.loops:
        vx, vy, vz = l.vert.co
        # Looking from +X: -Y is viewport left (U0), +Y is viewport right (U1)
        u = (vy - y_rb_0) / (y_rb_1 - y_rb_0) * (UV_RATING_U1 - UV_RATING_U0) + UV_RATING_U0
        v = (vz - z_rb_0) / (z_rb_1 - z_rb_0) * (UV_RATING_V1 - UV_RATING_V0) + UV_RATING_V0
        l[uv_lay].uv = Vector((u, v))

    v_rs_m1 = bm.verts.new((+hw, y_back_rim, z_rb_1))
    v_rs_m2 = bm.verts.new((+hw, y_front_flange, z_rb_1))
    f_rs_upper = bm.faces.new([v_side_tbr, v_side_tfr, v_rs_m2, v_rs_m1])
    f_rs_upper.material_index = 0
    for l in f_rs_upper.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    v_rs_b1 = bm.verts.new((+hw, y_back_rim, z_rb_0))
    v_rs_b2 = bm.verts.new((+hw, y_front_flange, z_rb_0))
    f_rs_lower = bm.faces.new([v_rs_b1, v_rs_b2, v_bot_fr, v_bot_br])
    f_rs_lower.material_index = 0
    for l in f_rs_lower.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_rs_ml = bm.faces.new([v_rs_m1, v_rb_tl, v_rb_bl, v_rs_b1])
    f_rs_ml.material_index = 0
    for l in f_rs_ml.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_rs_mr = bm.faces.new([v_rb_tr, v_rs_m2, v_rs_b2, v_rb_br])
    f_rs_mr.material_index = 0
    for l in f_rs_mr.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # --- 2. RECESSED REAR I/O CAVITY ---
    hw_io = hw - 0.004
    z_io_bot = z_bot + 0.004
    z_io_top = z_top - 0.006

    v_io_bl = bm.verts.new((-hw_io, y_back_io, z_io_bot))
    v_io_br = bm.verts.new((+hw_io, y_back_io, z_io_bot))
    v_io_tr = bm.verts.new((+hw_io, y_back_io, z_io_top))
    v_io_tl = bm.verts.new((-hw_io, y_back_io, z_io_top))

    f_io = bm.faces.new([v_io_bl, v_io_br, v_io_tr, v_io_tl])
    f_io.material_index = 0
    for l in f_io.loops:
        vx, vy, vz = l.vert.co
        u = (vx - (-hw_io)) / (2.0 * hw_io) * (UV_REAR_U1 - UV_REAR_U0) + UV_REAR_U0
        v = (vz - z_io_bot) / (z_io_top - z_io_bot) * (UV_REAR_V1 - UV_REAR_V0) + UV_REAR_V0
        l[uv_lay].uv = Vector((u, v))

    v_rim_tl = bm.verts.new((-hw_io, y_back_rim, z_io_top))
    v_rim_tr = bm.verts.new((+hw_io, y_back_rim, z_io_top))
    f_step_t = bm.faces.new([v_rim_tl, v_rim_tr, v_io_tr, v_io_tl])
    f_step_t.material_index = 0
    for l in f_step_t.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    v_rim_bl = bm.verts.new((-hw_io, y_back_rim, z_io_bot))
    v_rim_br = bm.verts.new((+hw_io, y_back_rim, z_io_bot))
    f_step_b = bm.faces.new([v_io_bl, v_io_br, v_rim_br, v_rim_bl])
    f_step_b.material_index = 0
    for l in f_step_b.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_step_l = bm.faces.new([v_rim_bl, v_io_bl, v_io_tl, v_rim_tl])
    f_step_l.material_index = 0
    for l in f_step_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_step_r = bm.faces.new([v_io_br, v_rim_br, v_rim_tr, v_io_tr])
    f_step_r.material_index = 0
    for l in f_step_r.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_rim_t = bm.faces.new([v_top_bl, v_top_br, v_rim_tr, v_rim_tl])
    f_rim_t.material_index = 0
    for l in f_rim_t.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_rim_b = bm.faces.new([v_rim_bl, v_rim_br, v_bot_br, v_bot_bl])
    f_rim_b.material_index = 0
    for l in f_rim_b.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_rim_l = bm.faces.new([v_side_tbl, v_top_bl, v_rim_tl, v_rim_bl, v_bot_bl])
    f_rim_l.material_index = 0
    for l in f_rim_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_rim_r = bm.faces.new([v_top_br, v_side_tbr, v_bot_br, v_rim_br, v_rim_tr])
    f_rim_r.material_index = 0
    for l in f_rim_r.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # --- 3. FOUR RUBBER BOTTOM FEET ---
    foot_coords = [
        (-0.038, +0.105), # Front Left
        (+0.038, +0.105), # Front Right
        (-0.038, -0.135), # Rear Left
        (+0.038, -0.135), # Rear Right
    ]
    fw = 0.008
    fl = 0.014
    for fx, fy in foot_coords:
        fv_b = [
            bm.verts.new((fx - fw, fy - fl, 0.000)),
            bm.verts.new((fx + fw, fy - fl, 0.000)),
            bm.verts.new((fx + fw, fy + fl, 0.000)),
            bm.verts.new((fx - fw, fy + fl, 0.000)),
        ]
        fv_t = [
            bm.verts.new((fx - fw, fy - fl, z_bot)),
            bm.verts.new((fx + fw, fy - fl, z_bot)),
            bm.verts.new((fx + fw, fy + fl, z_bot)),
            bm.verts.new((fx - fw, fy + fl, z_bot)),
        ]
        fb = bm.faces.new(fv_b)
        fb.material_index = 3 # M_Metal
        for l in fb.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL
        for i in range(4):
            i_next = (i + 1) % 4
            fs = bm.faces.new([fv_b[i], fv_b[i_next], fv_t[i_next], fv_t[i]])
            fs.material_index = 3
            for l in fs.loops:
                l[uv_lay].uv = UV_SAFE_NEUTRAL

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new("Main_Housing_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Main_Housing", mesh)
    assign_material_slots(obj, materials, primary_slot=0)
    return obj


def build_front_panel(materials):
    """Build sculpted molded polymer front fascia with architectural shadow lines and beveled bezel."""
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    hw = 0.050        # Width: -0.050 to +0.050
    ch = 0.003        # Matches housing chamfer 3mm
    y_attach = +0.135 # Mating plane with housing
    y_front  = +0.165 # Front-most fascia surface

    z_bot = 0.006
    z_top = 0.220
    z_ch  = z_top - ch # 0.217

    # Top plate of front panel
    v_tf_l = bm.verts.new((-hw + ch, y_attach, z_top))
    v_tf_r = bm.verts.new((+hw - ch, y_attach, z_top))
    v_tc_r = bm.verts.new((+hw - ch, y_front - 0.008, z_top))
    v_tc_l = bm.verts.new((-hw + ch, y_front - 0.008, z_top))

    f_top_fl = bm.faces.new([v_tf_l, v_tf_r, v_tc_r, v_tc_l])
    f_top_fl.material_index = 0
    for l in f_top_fl.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Front top angled brow slope
    v_ff_tl = bm.verts.new((-hw + ch, y_front, z_ch))
    v_ff_tr = bm.verts.new((+hw - ch, y_front, z_ch))

    f_top_slope = bm.faces.new([v_tc_l, v_tc_r, v_ff_tr, v_ff_tl])
    f_top_slope.material_index = 0
    for l in f_top_slope.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Top side chamfers on front panel
    v_att_tl = bm.verts.new((-hw, y_attach, z_ch))
    v_att_tr = bm.verts.new((+hw, y_attach, z_ch))
    v_side_f_tl = bm.verts.new((-hw, y_front, z_ch))
    v_side_f_tr = bm.verts.new((+hw, y_front, z_ch))

    f_fch_l = bm.faces.new([v_tf_l, v_tc_l, v_side_f_tl, v_att_tl])
    f_fch_l.material_index = 0
    for l in f_fch_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_fch_r = bm.faces.new([v_tf_r, v_att_tr, v_side_f_tr, v_tc_r])
    f_fch_r.material_index = 0
    for l in f_fch_r.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_fch_slope_l = bm.faces.new([v_tc_l, v_ff_tl, v_side_f_tl])
    f_fch_slope_l.material_index = 0
    for l in f_fch_slope_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_fch_slope_r = bm.faces.new([v_tc_r, v_side_f_tr, v_ff_tr])
    f_fch_slope_r.material_index = 0
    for l in f_fch_slope_r.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Front bottom corners
    v_ff_br = bm.verts.new((+hw - ch, y_front, z_bot))
    v_ff_bl = bm.verts.new((-hw + ch, y_front, z_bot))

    z_disp_top = 0.192
    z_disp_bot = 0.135
    w_disp = 0.035

    z_vent_top = 0.088
    z_vent_bot = 0.018
    w_vent = 0.040

    # Display window recess vertices (depth 3mm behind front face)
    y_disp_rec = y_front - 0.003
    v_d_tl = bm.verts.new((-w_disp, y_disp_rec, z_disp_top))
    v_d_tr = bm.verts.new((+w_disp, y_disp_rec, z_disp_top))
    v_d_br = bm.verts.new((+w_disp, y_disp_rec, z_disp_bot))
    v_d_bl = bm.verts.new((-w_disp, y_disp_rec, z_disp_bot))

    # Outer bezel boundary for display on front surface
    v_bo_tl = bm.verts.new((-w_disp, y_front, z_disp_top))
    v_bo_tr = bm.verts.new((+w_disp, y_front, z_disp_top))
    v_bo_br = bm.verts.new((+w_disp, y_front, z_disp_bot))
    v_bo_bl = bm.verts.new((-w_disp, y_front, z_disp_bot))

    f_d_step_t = bm.faces.new([v_bo_tl, v_bo_tr, v_d_tr, v_d_tl])
    f_d_step_b = bm.faces.new([v_d_bl, v_d_br, v_bo_br, v_bo_bl])
    f_d_step_l = bm.faces.new([v_bo_bl, v_bo_tl, v_d_tl, v_d_bl])
    f_d_step_r = bm.faces.new([v_d_br, v_d_tr, v_bo_tr, v_bo_br])
    for f in [f_d_step_t, f_d_step_b, f_d_step_l, f_d_step_r]:
        f.material_index = 0
        for l in f.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_d_back = bm.faces.new([v_d_bl, v_d_br, v_d_tr, v_d_tl])
    f_d_back.material_index = 0
    for l in f_d_back.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Horizontal architectural dividing shadow groove (Z: 0.091 to 0.095, depth 2.5mm)
    y_groove = y_front - 0.0025
    z_grv_t = 0.095
    z_grv_b = 0.091
    w_grv = hw - ch

    v_grv_otl = bm.verts.new((-w_grv, y_front, z_grv_t))
    v_grv_otr = bm.verts.new((+w_grv, y_front, z_grv_t))
    v_grv_obl = bm.verts.new((-w_grv, y_front, z_grv_b))
    v_grv_obr = bm.verts.new((+w_grv, y_front, z_grv_b))

    v_grv_itl = bm.verts.new((-w_grv, y_groove, z_grv_t))
    v_grv_itr = bm.verts.new((+w_grv, y_groove, z_grv_t))
    v_grv_ibl = bm.verts.new((-w_grv, y_groove, z_grv_b))
    v_grv_ibr = bm.verts.new((+w_grv, y_groove, z_grv_b))

    f_grv_t = bm.faces.new([v_grv_otl, v_grv_otr, v_grv_itr, v_grv_itl])
    f_grv_b = bm.faces.new([v_grv_ibl, v_grv_ibr, v_grv_obr, v_grv_obl])
    f_grv_back = bm.faces.new([v_grv_ibl, v_grv_itl, v_grv_itr, v_grv_ibr])
    for f in [f_grv_t, f_grv_b, f_grv_back]:
        f.material_index = 3 # M_Metal dark groove
        for l in f.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Vent grille intake recess cavity vertices (depth 8mm behind front face)
    y_vent_rec = y_front - 0.008
    v_v_tl = bm.verts.new((-w_vent, y_vent_rec, z_vent_top))
    v_v_tr = bm.verts.new((+w_vent, y_vent_rec, z_vent_top))
    v_v_br = bm.verts.new((+w_vent, y_vent_rec, z_vent_bot))
    v_v_bl = bm.verts.new((-w_vent, y_vent_rec, z_vent_bot))

    v_vo_tl = bm.verts.new((-w_vent, y_front, z_vent_top))
    v_vo_tr = bm.verts.new((+w_vent, y_front, z_vent_top))
    v_vo_br = bm.verts.new((+w_vent, y_front, z_vent_bot))
    v_vo_bl = bm.verts.new((-w_vent, y_front, z_vent_bot))

    f_v_step_t = bm.faces.new([v_vo_tl, v_vo_tr, v_v_tr, v_v_tl])
    f_v_step_b = bm.faces.new([v_v_bl, v_v_br, v_vo_br, v_vo_bl])
    f_v_step_l = bm.faces.new([v_vo_bl, v_vo_tl, v_v_tl, v_v_bl])
    f_v_step_r = bm.faces.new([v_v_br, v_v_tr, v_vo_tr, v_vo_br])
    for f in [f_v_step_t, f_v_step_b, f_v_step_l, f_v_step_r]:
        f.material_index = 0
        for l in f_v_step_l.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_v_back = bm.faces.new([v_v_bl, v_v_br, v_v_tr, v_v_tl])
    f_v_back.material_index = 0
    for l in f_v_back.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Boundary Vertices on front edges
    v_e_dtl = bm.verts.new((-hw + ch, y_front, z_disp_top))
    v_e_dtr = bm.verts.new((+hw - ch, y_front, z_disp_top))
    v_e_dbl = bm.verts.new((-hw + ch, y_front, z_disp_bot))
    v_e_dbr = bm.verts.new((+hw - ch, y_front, z_disp_bot))

    v_e_vtl = bm.verts.new((-hw + ch, y_front, z_vent_top))
    v_e_vtr = bm.verts.new((+hw - ch, y_front, z_vent_top))
    v_e_vbl = bm.verts.new((-hw + ch, y_front, z_vent_bot))
    v_e_vbr = bm.verts.new((+hw - ch, y_front, z_vent_bot))

    def uv_map_front_face(face):
        face.material_index = 0
        for loop in face.loops:
            vx, vy, vz = loop.vert.co
            u = (hw - vx) / (2.0 * hw) * (UV_FRONT_U1 - UV_FRONT_U0) + UV_FRONT_U0
            v = (vz - z_bot) / (z_top - z_bot) * (UV_FRONT_V1 - UV_FRONT_V0) + UV_FRONT_V0
            loop[uv_lay].uv = Vector((u, v))

    # Front planar panels:
    # 1. Top panel (above display)
    f_fp_top = bm.faces.new([v_ff_tl, v_ff_tr, v_e_dtr, v_bo_tr, v_bo_tl, v_e_dtl])
    uv_map_front_face(f_fp_top)

    # 2. Display left cheek
    f_fp_dl = bm.faces.new([v_e_dtl, v_bo_tl, v_bo_bl, v_e_dbl])
    uv_map_front_face(f_fp_dl)

    # 3. Display right cheek
    f_fp_dr = bm.faces.new([v_bo_tr, v_e_dtr, v_e_dbr, v_bo_br])
    uv_map_front_face(f_fp_dr)

    # 4. Center mid panel (between display and shadow groove)
    f_fp_mid = bm.faces.new([v_e_dbl, v_bo_bl, v_bo_br, v_e_dbr, v_grv_otr, v_grv_otl])
    uv_map_front_face(f_fp_mid)

    # 5. Panel between shadow groove and vent
    f_fp_sub = bm.faces.new([v_grv_obl, v_grv_obr, v_e_vtr, v_vo_tr, v_vo_tl, v_e_vtl])
    uv_map_front_face(f_fp_sub)

    # 6. Vent left cheek
    f_fp_vl = bm.faces.new([v_e_vtl, v_vo_tl, v_vo_bl, v_e_vbl])
    uv_map_front_face(f_fp_vl)

    # 7. Vent right cheek
    f_fp_vr = bm.faces.new([v_vo_tr, v_e_vtr, v_e_vbr, v_vo_br])
    uv_map_front_face(f_fp_vr)

    # 8. Bottom chin
    f_fp_bot = bm.faces.new([v_e_vbl, v_vo_bl, v_vo_br, v_e_vbr, v_ff_br, v_ff_bl])
    uv_map_front_face(f_fp_bot)

    # Side returns
    v_att_bl = bm.verts.new((-hw, y_attach, z_bot))
    v_side_f_bl = bm.verts.new((-hw, y_front, z_bot))
    f_ret_l = bm.faces.new([v_att_tl, v_side_f_tl, v_side_f_bl, v_att_bl])
    f_ret_l.material_index = 0
    for l in f_ret_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    v_att_br = bm.verts.new((+hw, y_attach, z_bot))
    v_side_f_br = bm.verts.new((+hw, y_front, z_bot))
    f_ret_r = bm.faces.new([v_side_f_tr, v_att_tr, v_att_br, v_side_f_br])
    f_ret_r.material_index = 0
    for l in f_ret_r.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Front side vertical chamfers
    f_side_ch_l = bm.faces.new([v_side_f_tl, v_ff_tl, v_ff_bl, v_side_f_bl])
    f_side_ch_l.material_index = 0
    for l in f_side_ch_l.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    f_side_ch_r = bm.faces.new([v_ff_tr, v_side_f_tr, v_side_f_br, v_ff_br])
    f_side_ch_r.material_index = 0
    for l in f_side_ch_r.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Bottom return
    f_ret_b = bm.faces.new([v_att_bl, v_side_f_bl, v_side_f_br, v_att_br])
    f_ret_b.material_index = 0
    for l in f_ret_b.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL

    # 3D Tactile Flanking Push Buttons (Mute / Select) as part of front panel
    # Left button (MUTE): X = +0.024 (observer's left), Z = 0.114, size: 10mm x 7mm, height: 2.0mm
    btn_m_x = +0.024
    btn_m_z = 0.114
    bw, bh, bth = 0.005, 0.0035, 0.0020
    v_bm_b = [
        bm.verts.new((btn_m_x - bw, y_front, btn_m_z - bh)),
        bm.verts.new((btn_m_x + bw, y_front, btn_m_z - bh)),
        bm.verts.new((btn_m_x + bw, y_front, btn_m_z + bh)),
        bm.verts.new((btn_m_x - bw, y_front, btn_m_z + bh)),
    ]
    v_bm_t = [
        bm.verts.new((btn_m_x - bw*0.85, y_front + bth, btn_m_z - bh*0.85)),
        bm.verts.new((btn_m_x + bw*0.85, y_front + bth, btn_m_z - bh*0.85)),
        bm.verts.new((btn_m_x + bw*0.85, y_front + bth, btn_m_z + bh*0.85)),
        bm.verts.new((btn_m_x - bw*0.85, y_front + bth, btn_m_z + bh*0.85)),
    ]
    f_bm_top = bm.faces.new(v_bm_t)
    f_bm_top.material_index = 3 # M_Metal button
    for l in f_bm_top.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL
    for i in range(4):
        i_n = (i + 1) % 4
        fs = bm.faces.new([v_bm_b[i], v_bm_b[i_n], v_bm_t[i_n], v_bm_t[i]])
        fs.material_index = 3
        for l in fs.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

    # Right button (DISP): X = -0.024 (observer's right), Z = 0.114
    btn_d_x = -0.024
    v_bd_b = [
        bm.verts.new((btn_d_x - bw, y_front, btn_m_z - bh)),
        bm.verts.new((btn_d_x + bw, y_front, btn_m_z - bh)),
        bm.verts.new((btn_d_x + bw, y_front, btn_m_z + bh)),
        bm.verts.new((btn_d_x - bw, y_front, btn_m_z + bh)),
    ]
    v_bd_t = [
        bm.verts.new((btn_d_x - bw*0.85, y_front + bth, btn_m_z - bh*0.85)),
        bm.verts.new((btn_d_x + bw*0.85, y_front + bth, btn_m_z - bh*0.85)),
        bm.verts.new((btn_d_x + bw*0.85, y_front + bth, btn_m_z + bh*0.85)),
        bm.verts.new((btn_d_x - bw*0.85, y_front + bth, btn_m_z + bh*0.85)),
    ]
    f_bd_top = bm.faces.new(v_bd_t)
    f_bd_top.material_index = 3 # M_Metal button
    for l in f_bd_top.loops:
        l[uv_lay].uv = UV_SAFE_NEUTRAL
    for i in range(4):
        i_n = (i + 1) % 4
        fs = bm.faces.new([v_bd_b[i], v_bd_b[i_n], v_bd_t[i_n], v_bd_t[i]])
        fs.material_index = 3
        for l in fs.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new("Front_Panel_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Front_Panel", mesh)
    assign_material_slots(obj, materials, primary_slot=0)
    return obj


def build_vent_grille(materials):
    """Build 5 heavy-duty horizontal louver intake slats angled downward at 35 degrees."""
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    w_vent = 0.038
    z_vent_top = 0.085
    z_vent_bot = 0.021
    y_front = +0.165
    y_back  = +0.158

    num_slats = 5
    slat_h = (z_vent_top - z_vent_bot) / num_slats

    for i in range(num_slats):
        z_base = z_vent_bot + i * slat_h
        z_tip  = z_base - 0.0038

        v_b_l = bm.verts.new((-w_vent, y_back, z_base + 0.007))
        v_b_r = bm.verts.new((+w_vent, y_back, z_base + 0.007))
        v_f_r = bm.verts.new((+w_vent, y_front, z_tip + 0.007))
        v_f_l = bm.verts.new((-w_vent, y_front, z_tip + 0.007))

        f_slat_t = bm.faces.new([v_b_l, v_b_r, v_f_r, v_f_l])
        f_slat_t.material_index = 0
        for l in f_slat_t.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

        v_u_l = bm.verts.new((-w_vent, y_back + 0.001, z_base + 0.005))
        v_u_r = bm.verts.new((+w_vent, y_back + 0.001, z_base + 0.005))
        f_slat_b = bm.faces.new([v_f_l, v_f_r, v_u_r, v_u_l])
        f_slat_b.material_index = 0
        for l in f_slat_b.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new("Vent_Grille_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Vent_Grille", mesh)
    assign_material_slots(obj, materials, primary_slot=0)
    return obj


def build_status_display(materials):
    """Build the backlit LCD display quad sitting inside the front panel bezel."""
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    w_disp = 0.033
    z_disp_top = 0.188
    z_disp_bot = 0.138
    y_screen = +0.1636

    v_bl = bm.verts.new((-w_disp, y_screen, z_disp_bot))
    v_br = bm.verts.new((+w_disp, y_screen, z_disp_bot))
    v_tr = bm.verts.new((+w_disp, y_screen, z_disp_top))
    v_tl = bm.verts.new((-w_disp, y_screen, z_disp_top))

    f_disp = bm.faces.new([v_bl, v_br, v_tr, v_tl])
    f_disp.material_index = 1 # Slot 1: M_Screen

    # Standing at +Y looking toward -Y: Left is +X, Right is -X.
    # To read left-to-right (from +X to -X):
    for l in f_disp.loops:
        vx, vy, vz = l.vert.co
        u = (w_disp - vx) / (2.0 * w_disp)
        v = (vz - z_disp_bot) / (z_disp_top - z_disp_bot)
        l[uv_lay].uv = Vector((u, v))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new("Status_Display_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Status_Display", mesh)
    assign_material_slots(obj, materials, primary_slot=1)
    return obj


def build_power_button(materials):
    """Build 10-sided beveled cylindrical power push button with illuminated standby emblem."""
    bm = bmesh.new()
    uv_lay = bm.loops.layers.uv.new("UVMap")

    cz = 0.114
    cx = 0.0
    y_base = +0.1645
    y_cap  = +0.1685 # Protrudes 3.5mm proud of front panel
    r_outer = 0.0080 # 16mm diameter
    r_inner = 0.0055 # 11mm illuminated core

    segments = 10
    verts_base = []
    verts_outer = []
    verts_inner = []

    for i in range(segments):
        ang = 2.0 * math.pi * i / segments
        ca = math.cos(ang)
        sa = math.sin(ang)

        verts_base.append(bm.verts.new((cx + r_outer * ca, y_base, cz + r_outer * sa)))
        verts_outer.append(bm.verts.new((cx + r_outer * ca, y_cap, cz + r_outer * sa)))
        verts_inner.append(bm.verts.new((cx + r_inner * ca, y_cap + 0.0004, cz + r_inner * sa)))

    for i in range(segments):
        i_next = (i + 1) % segments
        f_side = bm.faces.new([verts_base[i], verts_base[i_next], verts_outer[i_next], verts_outer[i]])
        f_side.material_index = 3 # M_Metal ring
        for l in f_side.loops:
            l[uv_lay].uv = UV_SAFE_NEUTRAL

    for i in range(segments):
        i_next = (i + 1) % segments
        f_rim = bm.faces.new([verts_outer[i], verts_outer[i_next], verts_inner[i_next], verts_inner[i]])
        f_rim.material_index = 3 # M_Metal outer bevel
        for l in f_rim.loops:
            vx, vy, vz = l.vert.co
            u = UV_BTN_CX - (vx - cx) / r_outer * UV_BTN_RAD
            v = UV_BTN_CY + (vz - cz) / r_outer * UV_BTN_RAD
            l[uv_lay].uv = Vector((u, v))

    f_cap = bm.faces.new(verts_inner)
    f_cap.material_index = 2 # Slot 2: M_Emission illuminated core
    for l in f_cap.loops:
        vx, vy, vz = l.vert.co
        u = UV_BTN_CX - (vx - cx) / r_outer * UV_BTN_RAD
        v = UV_BTN_CY + (vz - cz) / r_outer * UV_BTN_RAD
        l[uv_lay].uv = Vector((u, v))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mark_sharp_edges_by_angle(bm, threshold_deg=35.0)
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    mesh = bpy.data.meshes.new("Power_Button_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("Power_Button", mesh)
    assign_material_slots(obj, materials, primary_slot=0)

    obj["press_axis"] = "Y"
    obj["travel_m"] = 0.003
    obj["action"] = "POWER_TOGGLE"

    return obj


# =============================================================================
# SCENE ASSEMBLY & EXPORT
# =============================================================================

def build_asset():
    """Build the entire SEC_UPS_Power_Supply hierarchy, materials, and root empty."""
    reset_scene()
    materials = create_materials()

    # 1. Root Empty at (0, 0, 0)
    root_empty = bpy.data.objects.new("SEC_UPS_Power_Supply", None)
    root_empty.empty_display_type = 'PLAIN_AXES'
    root_empty.empty_display_size = 0.15
    root_empty.location = (0.0, 0.0, 0.0)
    bpy.context.scene.collection.objects.link(root_empty)

    # 2. Main_Housing (root child)
    obj_housing = build_main_housing(materials)
    bpy.context.scene.collection.objects.link(obj_housing)
    obj_housing.parent = root_empty

    # 3. Front_Panel (housing child)
    obj_front = build_front_panel(materials)
    bpy.context.scene.collection.objects.link(obj_front)
    obj_front.parent = obj_housing

    # 4. Vent_Grille (housing child)
    obj_vent = build_vent_grille(materials)
    bpy.context.scene.collection.objects.link(obj_vent)
    obj_vent.parent = obj_housing

    # 5. Status_Display (Front_Panel child)
    obj_disp = build_status_display(materials)
    bpy.context.scene.collection.objects.link(obj_disp)
    obj_disp.parent = obj_front

    # 6. Power_Button (Front_Panel child)
    obj_btn = build_power_button(materials)
    bpy.context.scene.collection.objects.link(obj_btn)
    obj_btn.parent = obj_front

    # Select all and apply smooth normals with auto-smooth
    bpy.context.view_layer.update()
    for obj in [obj_housing, obj_front, obj_vent, obj_disp, obj_btn]:
        for p in obj.data.polygons:
            p.use_smooth = True
        wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        wn.keep_sharp = True

    # Save Blend file
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
    print(f"[OK] Saved Blend file: {BLEND_OUT}")

    return root_empty, [obj_housing, obj_front, obj_vent, obj_disp, obj_btn]


def export_fbx(root_empty, mesh_objs):
    """Export standard Unity FBX with exact specifications."""
    bpy.ops.object.select_all(action='DESELECT')
    root_empty.select_set(True)
    for m in mesh_objs:
        m.select_set(True)

    bpy.context.view_layer.objects.active = root_empty

    bpy.ops.export_scene.fbx(
        filepath=FBX_OUT,
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
    print(f"[OK] Exported FBX: {FBX_OUT}")


def run_qa_verification():
    """Import exported FBX into a pristine scene and verify all specs."""
    print("\n--- RUNNING AUTOMATED QA RE-IMPORT VERIFICATION ---")
    reset_scene()

    bpy.ops.import_scene.fbx(filepath=FBX_OUT)

    all_objs = list(bpy.context.scene.objects)
    root = bpy.data.objects.get("SEC_UPS_Power_Supply")
    mesh_objs = [o for o in all_objs if o.type == 'MESH']
    empty_objs = [o for o in all_objs if o.type == 'EMPTY']

    print(f"Total Objects Imported: {len(all_objs)}")
    print(f"Mesh Count: {len(mesh_objs)}")
    print(f"Empty Count: {len(empty_objs)}")

    # 1. Check Root
    assert root is not None, "FAIL: Root Empty 'SEC_UPS_Power_Supply' not found!"
    print("[PASS] Root object found with exact name 'SEC_UPS_Power_Supply'")

    # 2. Triangle Count
    total_tris = 0
    for m in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(m.data)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        tris = len(bm.faces)
        total_tris += tris
        print(f"  - Mesh '{m.name}': {tris} tris")
        bm.free()

    print(f"Total Triangles: {total_tris} (Budget <= 450)")
    assert total_tris <= 450, f"FAIL: Triangle count {total_tris} exceeds budget 450!"
    print("[PASS] Triangle budget satisfied!")

    # 3. Check Materials
    expected_mats = ["M_Security_Atlas", "M_Screen", "M_Emission", "M_Metal"]
    imported_mats = sorted(list(bpy.data.materials.keys()))
    print(f"Imported Materials: {imported_mats}")
    for em in expected_mats:
        found = any(m.startswith(em) for m in imported_mats)
        assert found, f"FAIL: Expected material '{em}' not found in imported asset!"
    print("[PASS] All required materials present!")

    # 4. Check UVs
    for m in mesh_objs:
        assert len(m.data.uv_layers) > 0, f"FAIL: Mesh '{m.name}' has no UV layers!"
    print("[PASS] All meshes have valid UV coordinates!")

    # 5. Check Hierarchy
    housing = bpy.data.objects.get("Main_Housing")
    front = bpy.data.objects.get("Front_Panel")
    vent = bpy.data.objects.get("Vent_Grille")
    disp = bpy.data.objects.get("Status_Display")
    btn = bpy.data.objects.get("Power_Button")

    assert housing and housing.parent == root, "FAIL: Main_Housing parent != root!"
    assert front and front.parent == housing, "FAIL: Front_Panel parent != Main_Housing!"
    assert vent and vent.parent == housing, "FAIL: Vent_Grille parent != Main_Housing!"
    assert disp and disp.parent == front, "FAIL: Status_Display parent != Front_Panel!"
    assert btn and btn.parent == front, "FAIL: Power_Button parent != Front_Panel!"
    print("[PASS] Hierarchy and parent relationships strictly verified!")

    # Update manifest.json
    manifest_data = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    manifest_data["SEC_UPS_Power_Supply"] = {
        "asset_name": "SEC_UPS_Power_Supply",
        "fbx_path": "exports/SEC_UPS_Power_Supply.fbx",
        "blend_path": "exports/SEC_UPS_Power_Supply.blend",
        "tris_count": total_tris,
        "mesh_count": len(mesh_objs),
        "empty_count": len(empty_objs),
        "materials": [m.name for m in bpy.data.materials],
        "status": "SUCCESS"
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"[OK] Updated manifest: {MANIFEST_PATH}")
    print("[ALL QA CHECKS PASSED SUCCESSFULLY]\n")


def clean_backup_files():
    """Remove any temporary .blend1 backup files."""
    for root, dirs, files in os.walk(EXPORTS_DIR):
        for file in files:
            if file.endswith(".blend1"):
                try:
                    os.remove(os.path.join(root, file))
                    print(f"[CLEAN] Removed backup: {file}")
                except Exception:
                    pass


if __name__ == "__main__":
    root, meshes = build_asset()
    export_fbx(root, meshes)
    run_qa_verification()
    clean_backup_files()
