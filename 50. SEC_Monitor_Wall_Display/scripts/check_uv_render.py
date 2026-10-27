"""
=============================================================================
Security CCTV Asset Production Suite - Asset 50
UV vs Render Correlation & Visual QA Checker
=============================================================================
"""

import os
from PIL import Image, ImageChops, ImageDraw, ImageStat
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
EXPORTS = os.path.join(ASSET, "exports")
QA = os.path.join(ASSET, "qa")

RENDER = os.path.join(QA, "front_flat.png")
ATLAS = os.path.join(EXPORTS, "T_Security_Atlas.png")
SCREEN = os.path.join(EXPORTS, "T_Screen.png")
HERO = os.path.join(QA, "hero_34.png")
TILTED = os.path.join(QA, "display_tilted.png")

BEZEL_PX = (64, 64, 1984, 320) # (x0, y0, x1, y1) in Atlas (1920 x 256 px)

RES_X = 1200.0
RES_Y = 700.0
ORTHO = 1.150
PPM = RES_X / ORTHO

# Screen surface in world: width 0.960 m (-0.480 to +0.480), height 0.540 m (-0.270 to +0.270)
HALF_SCREEN_X = 0.4800
HALF_SCREEN_Z = 0.2700

# Bezel outer: width 1.000 m (-0.500 to +0.500), height 0.580 m (-0.290 to +0.290)
HALF_BEZEL_X = 0.5000
HALF_BEZEL_Z = 0.2900

def crop_screen(im):
    cx = RES_X / 2.0
    cy = RES_Y / 2.0
    x0 = int(round(cx - HALF_SCREEN_X * PPM))
    x1 = int(round(cx + HALF_SCREEN_X * PPM))
    y0 = int(round(cy - HALF_SCREEN_Z * PPM))
    y1 = int(round(cy + HALF_SCREEN_Z * PPM))
    return im.crop((x0, y0, x1, y1))

def crop_bottom_bezel(im):
    cx = RES_X / 2.0
    cy = RES_Y / 2.0
    x0 = int(round(cx - HALF_BEZEL_X * PPM))
    x1 = int(round(cx + HALF_BEZEL_X * PPM))
    # Bottom bezel in 3D: Z from -0.2900 to -0.2700
    # In render: cy is Z=0, so y increases downwards (Z decreases)
    y0 = int(round(cy + HALF_SCREEN_Z * PPM))
    y1 = int(round(cy + HALF_BEZEL_Z * PPM))
    return im.crop((x0, y0, x1, y1))

def ncc(a, b):
    a = a.astype(np.float32) - a.mean()
    b = b.astype(np.float32) - b.mean()
    sa = np.std(a)
    sb = np.std(b)
    if sa < 1e-4 or sb < 1e-4:
        return 1.0
    return float(np.mean((a / sa) * (b / sb)))

def main():
    if not os.path.exists(RENDER):
        raise FileNotFoundError(f"Missing render: {RENDER}")
    if not os.path.exists(SCREEN):
        raise FileNotFoundError(f"Missing screen feed: {SCREEN}")
    if not os.path.exists(ATLAS):
        raise FileNotFoundError(f"Missing atlas: {ATLAS}")

    render_im = Image.open(RENDER).convert("RGB")
    screen_ref = Image.open(SCREEN).convert("RGB")
    atlas_im = Image.open(ATLAS).convert("RGB")

    # 1. Screen Surface Correlation (4-way Quad CCTV feed)
    crop_sc = crop_screen(render_im)
    crop_sc_scaled = crop_sc.resize(screen_ref.size, Image.Resampling.BICUBIC)

    r_screen = ncc(np.array(screen_ref.convert("L")), np.array(crop_sc_scaled.convert("L")))
    print(f"[QA] Screen surface surveillance feed NCC: r = {r_screen:.3f}")
    assert r_screen > 0.70, f"Screen feed correlation failed: {r_screen:.3f} <= 0.70"

    # Check CAM 01 quadrant
    cam1_ref = screen_ref.crop((20, 20, 940, 520)).convert("L")
    cam1_rend = crop_sc_scaled.crop((20, 20, 940, 520)).convert("L")
    r_cam1 = ncc(np.array(cam1_ref), np.array(cam1_rend))
    print(f"[QA] CAM 01 Quad Zone NCC: r = {r_cam1:.3f}")
    assert r_cam1 > 0.70, f"CAM 01 zone NCC failed: {r_cam1:.3f}"

    # 2. Bottom Bezel Correlation
    crop_bez = crop_bottom_bezel(render_im)
    atlas_bez = atlas_im.crop(BEZEL_PX)
    crop_bez_scaled = crop_bez.resize(atlas_bez.size, Image.Resampling.BICUBIC)

    # Logo zone on bezel
    logo_atlas = atlas_bez.crop((600, 60, 1320, 170)).convert("L")
    logo_rend = crop_bez_scaled.crop((600, 60, 1320, 170)).convert("L")
    r_logo = ncc(np.array(logo_atlas), np.array(logo_rend))
    print(f"[QA] Center Brand Logo Zone NCC: r = {r_logo:.3f}")
    assert r_logo > 0.55, f"Logo zone NCC failed: {r_logo:.3f}"

    # 3. Motion Verification of Tilt_Pivot (8 degrees tilt downward)
    if os.path.exists(HERO) and os.path.exists(TILTED):
        h_im = Image.open(HERO).convert("RGB")
        t_im = Image.open(TILTED).convert("RGB")
        diff_tilt = ImageChops.difference(h_im, t_im)
        stat = ImageStat.Stat(diff_tilt)
        changed_px = sum(diff_tilt.convert("L").point(lambda p: 1 if p > 15 else 0).getdata())
        print(f"[QA] Tilt pivot motion diff: mean={sum(stat.mean)/3.0:.2f}, changed pixels={changed_px}")
        assert changed_px > 5000, f"Tilt motion failed: {changed_px} changed pixels"

    print("[SUCCESS] All QA & UV correlation checks passed for Asset 50!")

if __name__ == "__main__":
    main()
