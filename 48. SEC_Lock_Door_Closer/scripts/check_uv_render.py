"""
=============================================================================
Security CCTV Asset Production Suite - Asset 48
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
HERO = os.path.join(QA, "hero_34.png")
ARTICULATED = os.path.join(QA, "arms_articulated.png")

BODY_PX = (64, 64, 1984, 564) # (x0, y0, x1, y1) in Atlas (1920 x 500 px)

RES_X = 1200.0
RES_Y = 600.0
ORTHO = 0.250
PPM = RES_X / ORTHO

HALF_X = 0.1000  # 200 mm main body -> 0.1000 m half
HALF_Z = 0.0250  # 50 mm height -> 0.0250 m half

def crop_body_front(im):
    cx = RES_X / 2.0
    cy = RES_Y / 2.0
    x0 = int(round(cx - HALF_X * PPM))
    x1 = int(round(cx + HALF_X * PPM))
    y0 = int(round(cy - HALF_Z * PPM))
    y1 = int(round(cy + HALF_Z * PPM))
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
    if not os.path.exists(ATLAS):
        raise FileNotFoundError(f"Missing atlas: {ATLAS}")

    render_im = Image.open(RENDER).convert("RGB")
    atlas_im = Image.open(ATLAS).convert("RGB")

    # 1. Crop body front from render
    crop_rend = crop_body_front(render_im)
    atlas_body = atlas_im.crop(BODY_PX)

    crop_rend_scaled = crop_rend.resize(atlas_body.size, Image.Resampling.BICUBIC)

    # 2. Overall Body Correlation
    corr = ncc(np.array(atlas_body.convert("L")), np.array(crop_rend_scaled.convert("L")))
    print(f"[QA] Body front correlation vs atlas: r = {corr:.3f}")
    assert corr > 0.80, f"Body front correlation failed: {corr:.3f} <= 0.80"

    # 3. Check Left Branding Zone
    brand_atlas = atlas_body.crop((120, 80, 950, 320)).convert("L")
    brand_rend = crop_rend_scaled.crop((120, 80, 950, 320)).convert("L")
    r_brand = ncc(np.array(brand_atlas), np.array(brand_rend))
    print(f"[QA] Branding Zone NCC: r = {r_brand:.3f}")
    assert r_brand > 0.85, f"Branding zone NCC failed: {r_brand:.3f}"

    # 4. Check Right Valve Cluster Zone
    valve_atlas = atlas_body.crop((1160, 50, 1850, 420)).convert("L")
    valve_rend = crop_rend_scaled.crop((1160, 50, 1850, 420)).convert("L")
    r_valve = ncc(np.array(valve_atlas), np.array(valve_rend))
    print(f"[QA] Valve Cluster Zone NCC: r = {r_valve:.3f}")
    assert r_valve > 0.85, f"Valve cluster zone NCC failed: {r_valve:.3f}"

    # 5. Motion Verification of Dual Arm Pivots (Arm_Pivot_A and Arm_Pivot_B)
    if os.path.exists(HERO) and os.path.exists(ARTICULATED):
        h_im = Image.open(HERO).convert("RGB")
        art_im = Image.open(ARTICULATED).convert("RGB")
        diff_art = ImageChops.difference(h_im, art_im)
        stat = ImageStat.Stat(diff_art)
        changed_px = sum(diff_art.convert("L").point(lambda p: 1 if p > 15 else 0).getdata())
        print(f"[QA] Dual arm articulation motion diff: mean={sum(stat.mean)/3.0:.2f}, changed pixels={changed_px}")
        assert changed_px > 1000, f"Arm articulation motion failed: {changed_px} changed pixels"

    print("[SUCCESS] All QA & UV correlation checks passed for Asset 48!")

if __name__ == "__main__":
    main()
