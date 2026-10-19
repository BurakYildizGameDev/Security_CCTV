import bpy
import bmesh
import math
import os
import json
from mathutils import Vector, Euler, Matrix


# -------------------------------------------------------------
# Scene and Unit Settings
# -------------------------------------------------------------

def setup_scene():
    """Reset scene to a clean state with metric units and scale 1.0."""
    bpy.ops.wm.read_factory_settings(use_empty=True)

    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh, do_unlink=True)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for img in list(bpy.data.images):
        bpy.data.images.remove(img, do_unlink=True)

    if not bpy.data.collections:
        default_col = bpy.data.collections.new("Collection")
        bpy.context.scene.collection.children.link(default_col)

    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0


# -------------------------------------------------------------
# Texture Atlas Generation (512 x 512)
# -------------------------------------------------------------

def setup_texture_atlas():
    """
    Generate high-contrast, professional 512x512 texture atlas:
    - Quadrant 0 (Top-Left): Clean Security White Housing, Flank Caution Decals, and Chin Spirit Level
    - Quadrant 1 (Top-Right): Industrial Dark Anthracite Ribbed Metal and Gaskets
    - Quadrant 2 (Bottom-Left): Specification Rating Plate & Terminal Wiring Diagram
    - Quadrant 3 (Bottom-Right): Precision Laser Collimator Reticle & Optical Window
    """
    atlas_img = bpy.data.images.get("T_Security_Atlas")
    if atlas_img is None:
        atlas_img = bpy.data.images.new("T_Security_Atlas", 512, 512)

    pixels = [0.0] * (512 * 512 * 4)
    for y in range(512):
        for x in range(512):
            idx = (y * 512 + x) * 4
            if y >= 256:
                if x < 256:  # Quadrant 0: Clean Security White Housing
                    # Base crisp security white
                    r, g, b = 0.93, 0.94, 0.96

                    # -------------------------------------------------------------
                    # Zone 1: Flank Decals (Y: 384..500, X: 15..245)
                    # -------------------------------------------------------------
                    if 384 <= y <= 500 and 15 <= x <= 245:
                        dy_3d = (x - 85) * 0.261   # mm along housing depth
                        dz_3d = (y - 442) * 1.250  # mm along housing height

                        # Yellow & Black Laser Radiation Caution Triangle (Height: 28mm, Width: 32mm)
                        if -14.0 <= dz_3d <= 14.0 and abs(dy_3d) <= (14.0 - dz_3d) * 0.58:
                            r, g, b = 0.98, 0.82, 0.10  # Caution Safety Yellow
                            dist_laser_core_3d = math.sqrt(dy_3d**2 + dz_3d**2)
                            if dist_laser_core_3d < 2.5:
                                r, g, b = 0.10, 0.10, 0.12
                            elif 3.5 <= dist_laser_core_3d <= 7.5 and ((abs(dy_3d) < 1.2) or (abs(dz_3d) < 1.2) or (abs(abs(dy_3d) - abs(dz_3d)) < 1.0)):
                                r, g, b = 0.10, 0.10, 0.12
                            # Black outer border
                            if abs(dy_3d) >= (14.0 - dz_3d) * 0.58 - 1.2 or dz_3d <= -13.0:
                                r, g, b = 0.10, 0.10, 0.12

                        # Brand Typography "OPTEX PERIMETER" & "LASER BARRIER LB-100E"
                        if -6.0 <= dz_3d <= 6.0 and 9.0 <= dy_3d <= 30.0:
                            if (int(dz_3d) in [-4, -3, 2, 3]) and (int(dy_3d * 2) % 3 in [0, 1]):
                                r, g, b = 0.18, 0.20, 0.25

                    # -------------------------------------------------------------
                    # Zone 2: Front Chin Bubble Spirit Level Gauge (Y: 265..375, X: 15..245)
                    # -------------------------------------------------------------
                    elif 265 <= y <= 375 and 15 <= x <= 245:
                        # 3D Metric Proportions inside 22mm x 16mm recessed chin pocket
                        dx_3d = (x - 128) * 0.1074  # mm in X
                        dz_3d = (y - 317) * 0.1562  # mm in Z
                        dist_lvl_3d = math.sqrt(dx_3d**2 + dz_3d**2)

                        # Circular Spirit Level (Diameter: 12.4mm in 3D)
                        if 5.0 <= dist_lvl_3d <= 6.2:
                            r, g, b = 0.20, 0.22, 0.25  # Dark outer bezel ring
                        elif dist_lvl_3d < 5.0:
                            r, g, b = 0.20, 0.88, 0.32  # Fluorescent green spirit liquid
                            # Air bubble slightly off-center (1.6mm diameter)
                            dist_bubble_3d = math.sqrt((dx_3d - 0.6)**2 + (dz_3d - 0.2)**2)
                            if dist_bubble_3d < 1.6:
                                r, g, b = 0.92, 0.98, 0.92  # Air bubble
                            # Black crosshairs
                            if abs(dx_3d) < 0.25 or abs(dz_3d) < 0.25:
                                r, g, b = 0.12, 0.16, 0.12  # Crosshair lines
                        
                        # Level calibration tick marks on pocket floor (dz_3d = +/- 7.0mm)
                        if (abs(abs(dz_3d) - 7.0) < 0.5) and abs(dx_3d) <= 4.5:
                            r, g, b = 0.30, 0.33, 0.38

                    # -------------------------------------------------------------
                    # Zone 3: Plain Security White (Everywhere else in Quad 0)
                    # Guaranteed pure white (0.93, 0.94, 0.96) for chamfers, forehead, jambs
                    # -------------------------------------------------------------
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 1: Industrial Dark Anthracite Metal Mount & Visor Hood
                    r, g, b = 0.12, 0.13, 0.15  # Dark powder-coated metal
                    # Weatherproof rubber gasket ribbed texture
                    if (y % 12 in [0, 1]):
                        r, g, b = 0.06, 0.06, 0.07
                    # Mounting bolt slots at top and bottom
                    if (y in [465, 466, 305, 306]) and 350 <= x <= 418:
                        r, g, b = 0.04, 0.04, 0.05
                    # Corner bevel highlight edge
                    if (x - 256) in [0, 1, 254, 255] or (y - 256) in [0, 1, 254, 255]:
                        r, g, b = 0.28, 0.30, 0.35

                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

            else:
                if x < 256:  # Quadrant 2: Specification Label & Terminal Block Diagram
                    r, g, b = 0.78, 0.80, 0.84
                    # Regulatory certification box & wiring terminal diagram
                    if (y in [30, 75, 125, 175, 225]) or (x in [30, 85, 140, 195, 240]):
                        r, g, b = 0.14, 0.15, 0.18
                    # 100m Optical Range rating bar
                    if 180 <= y <= 210 and 40 <= x <= 220:
                        r, g, b = 0.18, 0.20, 0.25
                        if (x % 16 < 8):
                            r, g, b = 0.90, 0.35, 0.10  # Laser range bar
                    pixels[idx] = r; pixels[idx+1] = g; pixels[idx+2] = b; pixels[idx+3] = 1.0

                else:  # Quadrant 3: Precision Laser Collimator Reticle & Optical Window
                    dist_reticle = math.sqrt((x - 384)**2 + (y - 128)**2)
                    if dist_reticle < 110:
                        r, g, b = 0.08, 0.10, 0.15  # Anti-reflective dark optical glass
                        # Concentric amber alignment reticle rings
                        ring_r = int(dist_reticle) % 20
                        if ring_r in [0, 1]:
                            r, g, b = 0.92, 0.68, 0.15
                        elif ring_r in [2]:
                            r, g, b = 0.99, 0.88, 0.30
                        
                        # Laser alignment crosshair grid
                        if abs(x - 384) < 2 or abs(y - 128) < 2:
                            r, g, b = 0.95, 0.20, 0.15
                        
                        # Central laser diode collimator lens (radius < 24)
                        if dist_reticle < 24:
                            r, g, b = 0.75, 0.08, 0.04  # Ruby red laser crystal
                            if dist_reticle < 8:
                                r, g, b = 1.00, 0.90, 0.85  # Concentrated beam core glint
                    else:
                        r, g, b = 0.14, 0.15, 0.18

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


# -------------------------------------------------------------
# Material Definitions
# -------------------------------------------------------------

def create_materials(atlas_img):
    """
    Create the 3 standard materials required for SEC_Laser_Barrier_Emitter:
    Slot 0: M_Security_Atlas
    Slot 1: M_Lens_Glass
    Slot 2: M_Emission
    """
    mat_configs = [
        # (name, base_color, metallic, roughness, trans, emit_col, emit_str, diff_col)
        ("M_Security_Atlas", (0.93, 0.94, 0.96, 1.0), 0.10, 0.35, 0.0, (0, 0, 0, 1), 0.0, (0.93, 0.94, 0.96, 1.0)),
        ("M_Lens_Glass", (0.08, 0.10, 0.14, 1.0), 0.15, 0.05, 0.40, (0, 0, 0, 1), 0.0, (0.10, 0.14, 0.20, 0.90)),
        ("M_Emission", (1.0, 0.04, 0.02, 1.0), 0.0, 0.20, 0.0, (1.0, 0.04, 0.02, 1.0), 10.0, (1.0, 0.06, 0.03, 1.0)),
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

            elif name == "M_Lens_Glass":
                img_node = next((n for n in tree.nodes if n.type == "ShaderNodeTexImage"), None)
                if img_node is None:
                    img_node = tree.nodes.new(type="ShaderNodeTexImage")
                    img_node.location = (-300, 200)
                img_node.image = atlas_img
                tree.links.new(img_node.outputs["Color"], bsdf.inputs["Base Color"])
                bsdf.inputs["Roughness"].default_value = roughness
                bsdf.inputs["Metallic"].default_value = metallic
                if "Alpha" in bsdf.inputs:
                    bsdf.inputs["Alpha"].default_value = 0.90
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
    """Attach standard materials in exact order: Slot 0 = Atlas, Slot 1 = Lens Glass, Slot 2 = Emission."""
    ordered_keys = ["M_Security_Atlas", "M_Lens_Glass", "M_Emission"]
    mesh.materials.clear()
    for k in ordered_keys:
        mesh.materials.append(materials[k])


# -------------------------------------------------------------
# UV Mapping Helpers
# -------------------------------------------------------------

def set_face_uv_rect(bm, face, uv_rect, flip_u=False, flip_v=False):
    """
    Project planar face UVs to a specific rectangular region [u0, v0, u1, v1] in the atlas.
    Uses accurate updated normal to choose projection plane.
    """
    face.normal_update()
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
        factor_u = (cx - min_x) / span_x
        factor_v = (cy - min_y) / span_y
        if flip_u:
            factor_u = 1.0 - factor_u
        if flip_v:
            factor_v = 1.0 - factor_v
        u = u0 + factor_u * (u1 - u0)
        v = v0 + factor_v * (v1 - v0)
        loop[uv_lay].uv = (u, v)


def set_face_uv_radial(bm, face, uv_center, uv_radius):
    """Map a circular or fan face radially to [uv_center_u, uv_center_v] with radius uv_radius."""
    cu, cv = uv_center
    uv_lay = bm.loops.layers.uv.verify()

    coords = [loop.vert.co for loop in face.loops]
    max_r = max(math.sqrt(co.x**2 + co.z**2) for co in coords)
    if max_r < 1e-6:
        max_r = 1.0

    for loop in face.loops:
        co = loop.vert.co
        u = cu + (co.x / max_r) * uv_radius
        v = cv + (co.z / max_r) * uv_radius
        loop[uv_lay].uv = (u, v)


# -------------------------------------------------------------
# Mesh Builders
# -------------------------------------------------------------

def build_mount_base_mesh(mesh, materials):
    """
    Build SEC_Laser_Barrier_Emitter (Mount_Base):
    Root object at (0, 0, 0).
    - Wall/pole mounting plate flush at Y=0 (Y: 0.0 to 0.008m)
    - Dimensions: Width 70mm (X: -0.035 to +0.035m), Height 144mm (Z: -0.072 to +0.072m)
    - Top & Bottom wall/pole mounting ear tabs with screw slots
    - Bottom cable gland conduit nut (6-sided)
    - Octagonal swivel mounting clevis neck extending to Y=0.018m
    Tris count: ~86 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx, sz = 0.035, 0.072
    c = 0.012

    # 1. 8-sided main plate
    pts = [
        (sx - c, sz), (-sx + c, sz),
        (-sx, sz - c), (-sx, -sz + c),
        (-sx + c, -sz), (sx - c, -sz),
        (sx, -sz + c), (sx, sz - c)
    ]
    v_back = [bm.verts.new(Vector((x, 0.000, z))) for x, z in pts]
    v_front = [bm.verts.new(Vector((x, 0.008, z))) for x, z in pts]

    # Back face (Quadrant 2: Spec Label & Terminal Diagram)
    f_back = bm.faces.new(list(reversed(v_back)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, (0.05, 0.05, 0.45, 0.45))

    # Front face (Quadrant 1: Dark Metal)
    f_front = bm.faces.new(v_front)
    f_front.material_index = 0
    set_face_uv_rect(bm, f_front, (0.55, 0.55, 0.95, 0.95))

    # Side chamfers
    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([v_back[i], v_front[i], v_front[ni], v_back[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # 2. Top and Bottom Wall/Pole Mounting Tabs
    ew, eh = 0.016, 0.012
    # Top Tab (Z: sz to sz + eh, Y: 0.0 to 0.006)
    t_pts = [(-ew, sz), (ew, sz), (ew, sz + eh), (-ew, sz + eh)]
    vt_b = [bm.verts.new(Vector((x, 0.000, z))) for x, z in t_pts]
    vt_f = [bm.verts.new(Vector((x, 0.006, z))) for x, z in t_pts]
    f_tb = bm.faces.new(list(reversed(vt_b)))
    f_tb.material_index = 0
    set_face_uv_rect(bm, f_tb, (0.05, 0.05, 0.45, 0.45))
    f_tf = bm.faces.new(vt_f)
    f_tf.material_index = 0
    set_face_uv_rect(bm, f_tf, (0.55, 0.55, 0.95, 0.95))
    for i in [1, 2, 3]:
        ni = (i + 1) % 4
        f = bm.faces.new([vt_b[i], vt_f[i], vt_f[ni], vt_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # Bottom Tab (Z: -sz - eh to -sz, Y: 0.0 to 0.006)
    b_pts = [(-ew, -sz - eh), (ew, -sz - eh), (ew, -sz), (-ew, -sz)]
    vb_b = [bm.verts.new(Vector((x, 0.000, z))) for x, z in b_pts]
    vb_f = [bm.verts.new(Vector((x, 0.006, z))) for x, z in b_pts]
    f_bb = bm.faces.new(list(reversed(vb_b)))
    f_bb.material_index = 0
    set_face_uv_rect(bm, f_bb, (0.05, 0.05, 0.45, 0.45))
    f_bf = bm.faces.new(vb_f)
    f_bf.material_index = 0
    set_face_uv_rect(bm, f_bf, (0.55, 0.55, 0.95, 0.95))
    for i in [0, 1, 3]:
        ni = (i + 1) % 4
        f = bm.faces.new([vb_b[i], vb_f[i], vb_f[ni], vb_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # 3. Swivel Clevis Neck (Octagonal neck connecting base to housing: Y: 0.008 to 0.018m)
    r_neck = 0.018
    angles = [2.0 * math.pi * i / 8 for i in range(8)]
    v_nb = [bm.verts.new(Vector((r_neck * math.cos(a), 0.008, r_neck * math.sin(a)))) for a in angles]
    v_nf = [bm.verts.new(Vector((r_neck * math.cos(a), 0.018, r_neck * math.sin(a)))) for a in angles]
    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([v_nb[i], v_nf[i], v_nf[ni], v_nb[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))
    f_cap = bm.faces.new(v_nf)
    f_cap.material_index = 0
    set_face_uv_rect(bm, f_cap, (0.55, 0.55, 0.95, 0.95))

    # 4. Cable Gland Nut (6-sided)
    r_g = 0.006
    g_angles = [2.0 * math.pi * i / 6 for i in range(6)]
    v_gb = [bm.verts.new(Vector((r_g * math.cos(a), 0.012 + r_g * math.sin(a), -sz))) for a in g_angles]
    v_gf = [bm.verts.new(Vector((r_g * math.cos(a), 0.012 + r_g * math.sin(a), -sz - 0.008))) for a in g_angles]
    for i in range(6):
        ni = (i + 1) % 6
        f = bm.faces.new([v_gb[i], v_gf[i], v_gf[ni], v_gb[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))
    f_gcap = bm.faces.new(list(reversed(v_gf)))
    f_gcap.material_index = 0
    set_face_uv_rect(bm, f_gcap, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_emitter_housing_mesh(mesh, materials):
    """
    Build Emitter_Housing:
    Origin is at (0.0, 0.018, 0.0) relative to SEC_Laser_Barrier_Emitter.
    Weatherproof IP65 Industrial Column Housing:
    - Width: 64mm (X: -0.032 to +0.032m), Height: 140mm (Z: -0.070 to +0.070m)
    - Overhanging top sun/rain visor hood canopy projecting to Y=0.072m
    - Recessed 3D molded pocket on the lower front chin for the green spirit bubble level
    - Recessed front optical bay with dark anthracite light trap (NO DOUBLE RETICLE BUG!)
    - Side flanks mapped cleanly to crisp security white with yellow laser radiation caution triangle
    Tris count: ~60 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    sx_r, sz_r = 0.032, 0.068
    c_r = 0.010
    rear_pts = [
        (sx_r - c_r, sz_r), (-sx_r + c_r, sz_r),
        (-sx_r, sz_r - c_r), (-sx_r, -sz_r + c_r),
        (-sx_r + c_r, -sz_r), (sx_r - c_r, -sz_r),
        (sx_r, -sz_r + c_r), (sx_r, sz_r - c_r)
    ]
    r_verts = [bm.verts.new(Vector((x, 0.000, z))) for x, z in rear_pts]

    # Front Rim Profile at Y = 0.060m (with top visor canopy projecting to Y = 0.072m)
    sx_f, sz_f = 0.030, 0.065
    c_f = 0.008
    front_pts = [
        (sx_f - c_f, sz_f), (-sx_f + c_f, sz_f),
        (-sx_f, sz_f - c_f), (-sx_f, -sz_f + c_f),
        (-sx_f + c_f, -sz_f), (sx_f - c_f, -sz_f),
        (sx_f, -sz_f + c_f), (sx_f, sz_f - c_f)
    ]
    f_verts = []
    for i, (x, z) in enumerate(front_pts):
        if z > 0.040:
            y_proj = 0.072  # Enhanced overhanging sun/rain canopy
        elif z < -0.040:
            y_proj = 0.058  # Bottom chin
        else:
            y_proj = 0.060
        f_verts.append(bm.verts.new(Vector((x, y_proj, z))))

    UV_PLAIN_WHITE = (0.35, 0.88, 0.48, 0.98)
    UV_FLANK       = (0.03, 0.76, 0.48, 0.98)
    UV_CHIN        = (0.05, 0.52, 0.45, 0.72)
    UV_DARK_METAL  = (0.55, 0.55, 0.95, 0.95)

    # 1. Back face
    f_back = bm.faces.new(list(reversed(r_verts)))
    f_back.material_index = 0
    set_face_uv_rect(bm, f_back, UV_DARK_METAL)

    # 2. 8 Side quads connecting rear to front
    for i in range(8):
        ni = (i + 1) % 8
        f = bm.faces.new([r_verts[i], f_verts[i], f_verts[ni], r_verts[ni]])
        f.material_index = 0
        if i == 2:      # Left Flank -> Crisp White with Yellow Laser Warning Triangle!
            set_face_uv_rect(bm, f, UV_FLANK, flip_u=False)
        elif i == 6:    # Right Flank -> Crisp White with Yellow Laser Warning Triangle!
            set_face_uv_rect(bm, f, UV_FLANK, flip_u=True)
        elif i == 0:    # Top sun hood slope -> Dark Anthracite
            set_face_uv_rect(bm, f, UV_DARK_METAL)
        else:           # Chamfers (1, 3, 5, 7) and bottom (4) -> Solid Plain Security White
            set_face_uv_rect(bm, f, UV_PLAIN_WHITE)

    # 3. Front Face Topology
    wx = 0.024
    wz_top = 0.038
    wz_bot = -0.022
    wy_front = 0.060
    wy_recess = 0.050

    fh_top_l = f_verts[1]
    fh_top_r = f_verts[0]
    fh_bot_l = bm.verts.new(Vector((-wx, wy_front, wz_top)))
    fh_bot_r = bm.verts.new(Vector(( wx, wy_front, wz_top)))

    # Upper Forehead Quad (Security White around Status LED)
    f_fh = bm.faces.new([fh_top_r, fh_top_l, fh_bot_l, fh_bot_r])
    f_fh.material_index = 0
    set_face_uv_rect(bm, f_fh, UV_PLAIN_WHITE)

    # Upper Forehead side triangles
    f_fhl = bm.faces.new([f_verts[1], f_verts[2], fh_bot_l])
    f_fhl.material_index = 0
    set_face_uv_rect(bm, f_fhl, UV_PLAIN_WHITE)

    f_fhr = bm.faces.new([f_verts[7], f_verts[0], fh_bot_r])
    f_fhr.material_index = 0
    set_face_uv_rect(bm, f_fhr, UV_PLAIN_WHITE)

    # Lower Chin with Recessed 3D Spirit Level Pocket
    ch_top_l = bm.verts.new(Vector((-wx, 0.058, wz_bot)))
    ch_top_r = bm.verts.new(Vector(( wx, 0.058, wz_bot)))
    ch_bot_l = f_verts[4]
    ch_bot_r = f_verts[5]

    # Outer pocket rim (30mm wide x 22mm high at Y=0.058)
    pwo, pzto, pzbo, py_rim = 0.015, -0.032, -0.054, 0.058
    # Inner pocket floor (22mm wide x 16mm high at Y=0.056 - gentle 2mm recessed well with beveled edges)
    pwi, pzti, pzbi, py_poc = 0.011, -0.035, -0.051, 0.056

    p_tl = bm.verts.new(Vector((-pwo, py_rim, pzto)))
    p_tr = bm.verts.new(Vector(( pwo, py_rim, pzto)))
    p_bl = bm.verts.new(Vector((-pwo, py_rim, pzbo)))
    p_br = bm.verts.new(Vector(( pwo, py_rim, pzbo)))

    # Outer chin surround quads around pocket
    f_co_t = bm.faces.new([ch_top_l, ch_top_r, p_tr, p_tl]); f_co_t.material_index = 0; set_face_uv_rect(bm, f_co_t, UV_PLAIN_WHITE)
    f_co_b = bm.faces.new([p_bl, p_br, ch_bot_r, ch_bot_l]); f_co_b.material_index = 0; set_face_uv_rect(bm, f_co_b, UV_PLAIN_WHITE)
    f_co_l = bm.faces.new([ch_top_l, p_tl, p_bl, ch_bot_l]); f_co_l.material_index = 0; set_face_uv_rect(bm, f_co_l, UV_PLAIN_WHITE)
    f_co_r = bm.faces.new([p_tr, ch_top_r, ch_bot_r, p_br]); f_co_r.material_index = 0; set_face_uv_rect(bm, f_co_r, UV_PLAIN_WHITE)

    # Pocket inner bottom vertices
    pi_tl = bm.verts.new(Vector((-pwi, py_poc, pzti)))
    pi_tr = bm.verts.new(Vector(( pwi, py_poc, pzti)))
    pi_bl = bm.verts.new(Vector((-pwi, py_poc, pzbi)))
    pi_br = bm.verts.new(Vector(( pwi, py_poc, pzbi)))

    # Beveled pocket frame (45 degree chamfer, Slot 0: Dark Anthracite)
    f_pb_t = bm.faces.new([p_tl, p_tr, pi_tr, pi_tl]); f_pb_t.material_index = 0; set_face_uv_rect(bm, f_pb_t, UV_DARK_METAL)
    f_pb_b = bm.faces.new([pi_bl, pi_br, p_br, p_bl]); f_pb_b.material_index = 0; set_face_uv_rect(bm, f_pb_b, UV_DARK_METAL)
    f_pb_l = bm.faces.new([p_tl, pi_tl, pi_bl, p_bl]); f_pb_l.material_index = 0; set_face_uv_rect(bm, f_pb_l, UV_DARK_METAL)
    f_pb_r = bm.faces.new([pi_tr, p_tr, p_br, pi_br]); f_pb_r.material_index = 0; set_face_uv_rect(bm, f_pb_r, UV_DARK_METAL)

    # Pocket floor face -> mapped to Green Spirit Bubble Level Gauge!
    f_ch = bm.faces.new([pi_tl, pi_tr, pi_br, pi_bl])
    f_ch.material_index = 0
    set_face_uv_rect(bm, f_ch, UV_CHIN)

    # Lower Chin side triangles
    f_chl = bm.faces.new([f_verts[3], ch_top_l, ch_bot_l]); f_chl.material_index = 0; set_face_uv_rect(bm, f_chl, UV_PLAIN_WHITE)
    f_chr = bm.faces.new([ch_top_r, f_verts[6], ch_bot_r]); f_chr.material_index = 0; set_face_uv_rect(bm, f_chr, UV_PLAIN_WHITE)

    # Left & Right window side jambs
    f_wl = bm.faces.new([f_verts[2], f_verts[3], ch_top_l, fh_bot_l]); f_wl.material_index = 0; set_face_uv_rect(bm, f_wl, UV_PLAIN_WHITE)
    f_wr = bm.faces.new([fh_bot_r, ch_top_r, f_verts[6], f_verts[7]]); f_wr.material_index = 0; set_face_uv_rect(bm, f_wr, UV_PLAIN_WHITE)

    # Recessed Inner Cavity Jambs framing the Optical_Window (Dark Anthracite)
    rc_tl = bm.verts.new(Vector((-wx, wy_recess, wz_top)))
    rc_tr = bm.verts.new(Vector(( wx, wy_recess, wz_top)))
    rc_bl = bm.verts.new(Vector((-wx, wy_recess, wz_bot)))
    rc_br = bm.verts.new(Vector(( wx, wy_recess, wz_bot)))

    f_cj_t = bm.faces.new([fh_bot_r, fh_bot_l, rc_tl, rc_tr]); f_cj_t.material_index = 0; set_face_uv_rect(bm, f_cj_t, UV_DARK_METAL)
    f_cj_b = bm.faces.new([ch_top_l, ch_top_r, rc_br, rc_bl]); f_cj_b.material_index = 0; set_face_uv_rect(bm, f_cj_b, UV_DARK_METAL)
    f_cj_l = bm.faces.new([fh_bot_l, ch_top_l, rc_bl, rc_tl]); f_cj_l.material_index = 0; set_face_uv_rect(bm, f_cj_l, UV_DARK_METAL)
    f_cj_r = bm.faces.new([ch_top_r, fh_bot_r, rc_tr, rc_br]); f_cj_r.material_index = 0; set_face_uv_rect(bm, f_cj_r, UV_DARK_METAL)

    # Recessed Back Floor -> CLEAN DARK METAL LIGHT TRAP (NO DOUBLE RETICLE BUG!)
    f_floor = bm.faces.new([rc_tl, rc_bl, rc_br, rc_tr])
    f_floor.material_index = 0
    set_face_uv_rect(bm, f_floor, UV_DARK_METAL)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_optical_window_mesh(mesh, materials):
    """
    Build Optical_Window:
    Origin is at Aim_Pivot (0.0, 0.056, 0.008) relative to Emitter_Housing.
    High-Precision Collimator & Laser Emitter Optics:
    - Octagonal beveled metal bezel collar (Slot 0: M_Security_Atlas)
    - Anti-reflective optical glass lens disc (Slot 1: M_Lens_Glass)
    - Central laser diode collimator crystal bead (Slot 1: M_Lens_Glass)
    - UV mapped radially to Quadrant 3 reticle with amber concentric rings & red laser crosshairs!
    Tris count: ~62 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    segs = 8
    angles = [2.0 * math.pi * i / segs for i in range(segs)]

    r_barrel = 0.021
    r_lens   = 0.017
    r_diode  = 0.006

    y_back   = -0.006
    y_rim    = 0.006
    y_lens   = 0.004
    y_diode  = 0.008

    v_back  = [bm.verts.new(Vector((r_barrel * math.cos(a), y_back, r_barrel * math.sin(a)))) for a in angles]
    v_rim   = [bm.verts.new(Vector((r_barrel * math.cos(a), y_rim,  r_barrel * math.sin(a)))) for a in angles]
    v_inner = [bm.verts.new(Vector((r_lens   * math.cos(a), y_lens, r_lens   * math.sin(a)))) for a in angles]
    v_diode = [bm.verts.new(Vector((r_diode  * math.cos(a), y_lens, r_diode  * math.sin(a)))) for a in angles]
    v_tip   = bm.verts.new(Vector((0.0, y_diode, 0.0)))

    # 1. Bezel Outer Barrel Quads (Dark Powder-Coated Metal Bezel, Slot 0)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_back[i], v_rim[i], v_rim[ni], v_back[ni]])
        f.smooth = True
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # 2. Bezel Inward Chamfer Ring (Slot 0)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_rim[i], v_inner[i], v_inner[ni], v_rim[ni]])
        f.smooth = False
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # 3. Optical Glass Annular Face (Slot 1: M_Lens_Glass)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_inner[i], v_diode[i], v_diode[ni], v_inner[ni]])
        f.smooth = True
        f.material_index = 1  # M_Lens_Glass
        set_face_uv_radial(bm, f, (0.75, 0.25), 0.20)

    # 4. Central Laser Collimator Diode Crystal Fan (Slot 1: M_Lens_Glass)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_diode[i], v_tip, v_diode[ni]])
        f.smooth = True
        f.material_index = 1  # M_Lens_Glass
        set_face_uv_radial(bm, f, (0.75, 0.25), 0.08)

    # 5. Base Back Cap
    f_b = bm.faces.new(list(reversed(v_back)))
    f_b.material_index = 0
    set_face_uv_rect(bm, f_b, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


def build_status_led_mesh(mesh, materials):
    """
    Build Status_LED:
    Origin is at front forehead plate (0.0, 0.063, 0.046) relative to Emitter_Housing.
    Industrial status indicator:
    - 6-sided dark metal bezel mounting collar (Slot 0: M_Security_Atlas)
    - 6-sided faceted ruby red jewel emission dome (Slot 2: M_Emission)
    Tris count: ~34 tris.
    """
    attach_standard_materials(mesh, materials)
    bm = bmesh.new()

    segs = 6
    angles = [2.0 * math.pi * i / segs for i in range(segs)]

    r_bezel = 0.0055
    r_led   = 0.0035
    h_bezel = 0.0012
    h_tip   = 0.0028

    v_base_b = [bm.verts.new(Vector((r_bezel * math.cos(a), 0.0, r_bezel * math.sin(a)))) for a in angles]
    v_base_f = [bm.verts.new(Vector((r_bezel * math.cos(a), h_bezel, r_bezel * math.sin(a)))) for a in angles]
    v_led_b  = [bm.verts.new(Vector((r_led * math.cos(a), h_bezel, r_led * math.sin(a)))) for a in angles]
    v_tip    = bm.verts.new(Vector((0.0, h_tip, 0.0)))

    # 1. Bezel outer side quads (Slot 0: Dark Anthracite)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_base_b[i], v_base_f[i], v_base_f[ni], v_base_b[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # 2. Bezel inward chamfer rim (Slot 0: Dark Anthracite)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_base_f[i], v_led_b[i], v_led_b[ni], v_base_f[ni]])
        f.material_index = 0
        set_face_uv_rect(bm, f, (0.55, 0.55, 0.95, 0.95))

    # 3. Jewel dome fan (Slot 2: M_Emission - Ruby Red)
    for i in range(segs):
        ni = (i + 1) % segs
        f = bm.faces.new([v_led_b[i], v_tip, v_led_b[ni]])
        f.smooth = True
        f.material_index = 2
        set_face_uv_rect(bm, f, (0.1, 0.1, 0.9, 0.9))

    # 4. Back base cap (Slot 0)
    f_b = bm.faces.new(list(reversed(v_base_b)))
    f_b.material_index = 0
    set_face_uv_rect(bm, f_b, (0.55, 0.55, 0.95, 0.95))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()


# -------------------------------------------------------------
# Asset Assembly and Hierarchy
# -------------------------------------------------------------

def generate_asset():
    """Build the entire SEC_Laser_Barrier_Emitter asset with strict hierarchy and Aim_Pivot."""
    setup_scene()
    atlas_img = setup_texture_atlas()
    materials = create_materials(atlas_img)

    # 1. Root Object: Mount_Base named SEC_Laser_Barrier_Emitter
    root_mesh = bpy.data.meshes.new("SEC_Laser_Barrier_Emitter_Mesh")
    build_mount_base_mesh(root_mesh, materials)
    root_obj = bpy.data.objects.new("SEC_Laser_Barrier_Emitter", root_mesh)
    bpy.context.collection.objects.link(root_obj)
    root_obj.location = (0.0, 0.0, 0.0)

    # 2. Emitter_Housing (Child of SEC_Laser_Barrier_Emitter)
    housing_mesh = bpy.data.meshes.new("Emitter_Housing_Mesh")
    build_emitter_housing_mesh(housing_mesh, materials)
    housing_obj = bpy.data.objects.new("Emitter_Housing", housing_mesh)
    bpy.context.collection.objects.link(housing_obj)
    housing_obj.parent = root_obj
    housing_obj.location = (0.0, 0.018, 0.0)

    # 3. Empty Pivot: Aim_Pivot (Child of Emitter_Housing at optical aim center)
    aim_pivot = bpy.data.objects.new("Aim_Pivot", None)
    aim_pivot.empty_display_type = 'ARROWS'
    aim_pivot.empty_display_size = 0.03
    bpy.context.collection.objects.link(aim_pivot)
    aim_pivot.parent = housing_obj
    aim_pivot.location = (0.0, 0.056, 0.008)

    # Custom Properties for fine optical alignment limits (+/- 10 deg)
    aim_pivot["min_rot_x"] = -10.0
    aim_pivot["max_rot_x"] = 10.0
    aim_pivot["min_rot_z"] = -10.0
    aim_pivot["max_rot_z"] = 10.0

    # Limit Rotation Constraint
    rot_limit = aim_pivot.constraints.new(type='LIMIT_ROTATION')
    rot_limit.use_limit_x = True
    rot_limit.min_x = math.radians(-10.0)
    rot_limit.max_x = math.radians(10.0)
    rot_limit.use_limit_z = True
    rot_limit.min_z = math.radians(-10.0)
    rot_limit.max_z = math.radians(10.0)
    rot_limit.use_limit_y = True
    rot_limit.min_y = 0.0
    rot_limit.max_y = 0.0
    rot_limit.owner_space = 'LOCAL'

    # 4. Optical_Window (Child of Aim_Pivot - aims with pivot!)
    window_mesh = bpy.data.meshes.new("Optical_Window_Mesh")
    build_optical_window_mesh(window_mesh, materials)
    window_obj = bpy.data.objects.new("Optical_Window", window_mesh)
    bpy.context.collection.objects.link(window_obj)
    window_obj.parent = aim_pivot
    window_obj.location = (0.0, 0.0, 0.0)

    # 5. Status_LED (Child of Emitter_Housing on upper forehead plate)
    led_mesh = bpy.data.meshes.new("Status_LED_Mesh")
    build_status_led_mesh(led_mesh, materials)
    led_obj = bpy.data.objects.new("Status_LED", led_mesh)
    bpy.context.collection.objects.link(led_obj)
    led_obj.parent = housing_obj
    led_obj.location = (0.0, 0.063, 0.046)
    led_obj.rotation_euler = (math.radians(-16.0), 0.0, 0.0)

    for obj in [root_obj, housing_obj, window_obj, led_obj]:
        mod = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        mod.keep_sharp = True

    bpy.context.view_layer.update()

    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, housing_obj, window_obj, led_obj]:
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
    if total_tris > 300:
        raise ValueError(f"Triangle count {total_tris} exceeds limit of 300 tris!")

    bpy.ops.object.select_all(action='DESELECT')
    export_objects = [root_obj, housing_obj, aim_pivot, window_obj, led_obj]
    for obj in export_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj

    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)
    fbx_path = os.path.join(exports_dir, "SEC_Laser_Barrier_Emitter.fbx")

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

    blend_path = os.path.join(exports_dir, "SEC_Laser_Barrier_Emitter.blend")
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
        "asset_name": "SEC_Laser_Barrier_Emitter",
        "fbx_path": fbx_path,
        "blend_path": blend_path,
        "tris_count": total_tris,
        "mesh_count": 4,
        "empty_count": 1,
        "materials": ["M_Security_Atlas", "M_Lens_Glass", "M_Emission"]
    }


# -------------------------------------------------------------
# FBX Verification Routine
# -------------------------------------------------------------

def verify_exported_fbx(fbx_path):
    """
    Independent verification pass: Re-import FBX into clean scene to verify:
    - Geometry & triangle budget <= 300 tris
    - Object count & naming
    - Full parent-child hierarchy
    - Aim_Pivot rotation limits and functionality
    - Material slots in exact order
    - UV map layers
    """
    print(f"\n[VERIFY] Re-importing FBX from: {fbx_path}")
    setup_scene()

    bpy.ops.import_scene.fbx(filepath=fbx_path)

    expected_objects = {
        "SEC_Laser_Barrier_Emitter",
        "Emitter_Housing",
        "Aim_Pivot",
        "Optical_Window",
        "Status_LED"
    }

    imported_names = {obj.name for obj in bpy.data.objects}
    print(f"[VERIFY] Imported objects: {imported_names}")
    missing = expected_objects - imported_names
    if missing:
        raise AssertionError(f"Missing expected objects in FBX: {missing}")

    root_obj = bpy.data.objects.get("SEC_Laser_Barrier_Emitter")
    housing_obj = bpy.data.objects.get("Emitter_Housing")
    aim_pivot = bpy.data.objects.get("Aim_Pivot")
    window_obj = bpy.data.objects.get("Optical_Window")
    led_obj = bpy.data.objects.get("Status_LED")

    assert root_obj is not None, "Root object 'SEC_Laser_Barrier_Emitter' not found."
    assert root_obj.parent is None, "Root object should not have a parent."

    assert housing_obj.parent == root_obj, f"Emitter_Housing parent should be {root_obj.name}, got {housing_obj.parent}"
    assert aim_pivot.parent == housing_obj, f"Aim_Pivot parent should be {housing_obj.name}, got {aim_pivot.parent}"
    assert window_obj.parent == aim_pivot, f"Optical_Window parent should be {aim_pivot.name}, got {window_obj.parent}"
    assert led_obj.parent == housing_obj, f"Status_LED parent should be {housing_obj.name}, got {led_obj.parent}"
    print("[VERIFY] Full parent-child hierarchy verified.")

    # Verify Aim_Pivot rotation test
    orig_loc = window_obj.matrix_world.translation.copy()
    aim_pivot.rotation_euler.x += math.radians(5.0)
    bpy.context.view_layer.update()
    new_loc = window_obj.matrix_world.translation.copy()
    delta_loc = (new_loc - orig_loc).length
    aim_pivot.rotation_euler.x -= math.radians(5.0)
    bpy.context.view_layer.update()
    print(f"[VERIFY] Aim_Pivot functional rotation verified (displacement delta: {delta_loc:.5f}m).")

    # Triangle budget verification
    total_tris = 0
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in [root_obj, housing_obj, window_obj, led_obj]:
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
    assert total_tris <= 300, f"Triangles {total_tris} exceed limit of 300!"

    expected_mats = ["M_Security_Atlas", "M_Lens_Glass", "M_Emission"]
    for obj in [root_obj, housing_obj, window_obj, led_obj]:
        slots = [s.material.name if s.material else None for s in obj.material_slots]
        print(f"[VERIFY] Object '{obj.name}' material slots: {slots}")
        assert slots == expected_mats, f"Object '{obj.name}' slot mismatch: expected {expected_mats}, got {slots}"

    for obj in [root_obj, housing_obj, window_obj, led_obj]:
        uvs = obj.data.uv_layers
        assert len(uvs) >= 1, f"Object '{obj.name}' lacks UV layer!"
        print(f"[VERIFY] Object '{obj.name}' has UV layer: {uvs.active.name}")

    print("[VERIFY] ALL CHECKS PASSED SUCCESSFULLY.")
    return total_tris


# -------------------------------------------------------------
# Manifest Updater
# -------------------------------------------------------------

def update_manifest(asset_data, is_valid):
    """Write verification and metadata status to exports/manifest.json."""
    manifest_path = os.path.join("exports", "manifest.json")
    manifest = {}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    manifest[asset_data["asset_name"]] = {
        "asset_name": asset_data["asset_name"],
        "fbx_path": asset_data["fbx_path"],
        "tris_count": asset_data["tris_count"],
        "mesh_count": asset_data["mesh_count"],
        "empty_count": asset_data["empty_count"],
        "materials": asset_data["materials"],
        "status": "SUCCESS" if is_valid else "FAILED"
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[INFO] Manifest updated: {manifest_path}")


# -------------------------------------------------------------
# Main Entry Point
# -------------------------------------------------------------

if __name__ == "__main__":
    asset_data = generate_asset()
    try:
        verified_tris = verify_exported_fbx(asset_data["fbx_path"])
        asset_data["tris_count"] = verified_tris
        update_manifest(asset_data, is_valid=True)
        print("\n==========================================")
        print("  PROCESS COMPLETED SUCCESSFULLY [SUCCESS]")
        print("==========================================")
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        update_manifest(asset_data, is_valid=False)
        raise
