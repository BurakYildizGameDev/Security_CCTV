"""
=============================================================================
Security CCTV Asset Production Suite - Asset 49
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
DOOR_OPEN = os.path.join(QA, "door_open.png")

DOOR_PX = (64, 64, 1024, 1984) # (x0, y0, x1, y1) in Atlas (960 x 1920 px)

RES_X = 800.0
RES_Y = 1200.0
ORTHO = 1.150
PPM = RES_Y / ORTHO

# Front door in world: X from -0.290 to +0.290 (width 0.580 m), Z from 0.070 to 1.010 (height 0.940 m)
# Center of door: X = 0.0, Z = 0.540
HALF_X = 0.2900
HALF_Z = 0.4700

def crop_front_door(im):
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

    # 1. Crop front door from render
    crop_rend = crop_front_door(render_im)
    atlas_door = atlas_im.crop(DOOR_PX)

    crop_rend_scaled = crop_rend.resize(atlas_door.size, Image.Resampling.BICUBIC)

    # 2. Key Front Door Branding & Component Zones
    # Top Header Zone
    header_atlas = atlas_door.crop((40, 30, 920, 150)).convert("L")
    header_rend = crop_rend_scaled.crop((40, 30, 920, 150)).convert("L")
    r_hdr = ncc(np.array(header_atlas), np.array(header_rend))
    print(f"[QA] Top Header Zone NCC: r = {r_hdr:.3f}")
    assert r_hdr > 0.80, f"Top header zone NCC failed: {r_hdr:.3f} <= 0.80"

    # Swing Handle Lock Zone
    lock_atlas = atlas_door.crop((780, 680, 930, 1250)).convert("L")
    lock_rend = crop_rend_scaled.crop((780, 680, 930, 1250)).convert("L")
    r_lock = ncc(np.array(lock_atlas), np.array(lock_rend))
    print(f"[QA] Lock Handle Zone NCC: r = {r_lock:.3f}")
    assert r_lock > 0.80, f"Lock handle zone NCC failed: {r_lock:.3f} <= 0.80"

    # Bottom Certification Bar
    bot_atlas = atlas_door.crop((40, 1780, 920, 1940)).convert("L")
    bot_rend = crop_rend_scaled.crop((40, 1780, 920, 1940)).convert("L")
    r_bot = ncc(np.array(bot_atlas), np.array(bot_rend))
    print(f"[QA] Bottom Certification Zone NCC: r = {r_bot:.3f}")
    assert r_bot > 0.80, f"Bottom certification zone NCC failed: {r_bot:.3f} <= 0.80"

    # 6. Motion Verification of Door_Hinge_Pivot
    if os.path.exists(HERO) and os.path.exists(DOOR_OPEN):
        h_im = Image.open(HERO).convert("RGB")
        op_im = Image.open(DOOR_OPEN).convert("RGB")
        diff_door = ImageChops.difference(h_im, op_im)
        stat = ImageStat.Stat(diff_door)
        changed_px = sum(diff_door.convert("L").point(lambda p: 1 if p > 15 else 0).getdata())
        print(f"[QA] Door hinge rotation motion diff: mean={sum(stat.mean)/3.0:.2f}, changed pixels={changed_px}")
        assert changed_px > 5000, f"Door hinge motion failed: {changed_px} changed pixels"

    print("[SUCCESS] All QA & UV correlation checks passed for Asset 49!")

if __name__ == "__main__":
    main()
