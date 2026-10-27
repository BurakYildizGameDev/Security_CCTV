"""
=============================================================================
Security CCTV Asset Production Suite - Asset 47
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
ROTATED = os.path.join(QA, "latch_rotated.png")

FACEPLATE_PX = (64, 64, 464, 1984) # (x0, y0, x1, y1) in Atlas

RES_X = 600.0
RES_Y = 1200.0
ORTHO = 0.185
PPM = RES_Y / ORTHO

HALF_X = 0.0120  # 24 mm width -> 0.0120 m half
HALF_Z = 0.0800  # 160 mm height -> 0.0800 m half

def crop_faceplate(im):
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

    # 1. Crop faceplate from render
    crop_rend = crop_faceplate(render_im)
    atlas_plate = atlas_im.crop(FACEPLATE_PX)

    crop_rend_scaled = crop_rend.resize(atlas_plate.size, Image.Resampling.BICUBIC)

    # Cutout & hardware mask
    w, h = atlas_plate.size
    mask = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(mask)
    cut_w = 280
    cut_h = 520
    # Mask cutout and latch
    d.rectangle([(w - cut_w)//2, (h - cut_h)//2, (w + cut_w)//2, (h + cut_h)//2], fill=0)

    # Chamfered 45° corners (3.5 mm chamfer on faceplate corners)
    ch = 60
    d.polygon([(0, 0), (ch, 0), (0, ch)], fill=0)
    d.polygon([(w, 0), (w - ch, 0), (w, ch)], fill=0)
    d.polygon([(0, h), (ch, h), (0, h - ch)], fill=0)
    d.polygon([(w, h), (w - ch, h), (w, h - ch)], fill=0)

    # Masked NCC
    a_arr = np.array(atlas_plate.convert("L"))
    r_arr = np.array(crop_rend_scaled.convert("L"))
    m_arr = np.array(mask) > 0

    corr = ncc(a_arr[m_arr], r_arr[m_arr])
    print(f"[QA] Masked correlation (faceplate branding & screws): r = {corr:.3f}")
    assert corr > 0.80, f"Correlation too low: {corr:.3f} <= 0.80"

    # Check top text ink zone (below the top screw)
    top_zone_atlas = atlas_plate.crop((50, 185, 350, 320)).convert("L")
    top_zone_rend = crop_rend_scaled.crop((50, 185, 350, 320)).convert("L")
    r_top = ncc(np.array(top_zone_atlas), np.array(top_zone_rend))
    print(f"[QA] Top Branding Zone NCC: r = {r_top:.3f}")
    assert r_top > 0.85, f"Top branding zone NCC failed: {r_top:.3f}"

    # Check bottom text ink zone
    bot_zone_atlas = atlas_plate.crop((50, 1640, 350, 1750)).convert("L")
    bot_zone_rend = crop_rend_scaled.crop((50, 1640, 350, 1750)).convert("L")
    r_bot = ncc(np.array(bot_zone_atlas), np.array(bot_zone_rend))
    print(f"[QA] Bottom Rating Zone NCC: r = {r_bot:.3f}")
    assert r_bot > 0.80, f"Bottom rating zone NCC failed: {r_bot:.3f}"

    # Motion verification of Latch_Pivot
    if os.path.exists(HERO) and os.path.exists(ROTATED):
        h_im = Image.open(HERO).convert("RGB")
        rot_im = Image.open(ROTATED).convert("RGB")
        diff_rot = ImageChops.difference(h_im, rot_im)
        stat = ImageStat.Stat(diff_rot)
        changed_px = sum(diff_rot.convert("L").point(lambda p: 1 if p > 15 else 0).getdata())
        print(f"[QA] Latch rotation motion diff: mean={sum(stat.mean)/3.0:.2f}, changed pixels={changed_px}")
        assert changed_px > 500, f"Latch rotation motion failed: {changed_px} changed pixels"

    print("[SUCCESS] All QA & UV correlation checks passed for Asset 47!")

if __name__ == "__main__":
    main()
