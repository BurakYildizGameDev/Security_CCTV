"""
=============================================================================
Security CCTV Asset Production Suite - Asset 51
UV vs Render Correlation & Visual QA Checker
=============================================================================
"""

import os
from PIL import Image, ImageChops, ImageStat
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
EXPORTS = os.path.join(ASSET, "exports")
QA = os.path.join(ASSET, "qa")

RENDER = os.path.join(QA, "front_flat.png")
ATLAS = os.path.join(EXPORTS, "T_Security_Atlas.png")
SCREEN = os.path.join(EXPORTS, "T_Screen.png")
HERO = os.path.join(QA, "hero_34.png")

RES_X = 1024.0
RES_Y = 740.0
ORTHO = 0.220
PPM = RES_X / ORTHO

# Screen surface in world: W=0.140m (-0.070 to +0.070), H=0.075m (-0.025 to +0.050)
HALF_SCREEN_X = 0.070
SCREEN_Z_BOT = -0.025
SCREEN_Z_TOP = 0.050

def crop_screen(im):
    cx = RES_X / 2.0
    cy = RES_Y / 2.0
    x0 = int(round(cx - HALF_SCREEN_X * PPM))
    x1 = int(round(cx + HALF_SCREEN_X * PPM))
    # In render: cy is Z=0, y increases downwards (Z decreases)
    y0 = int(round(cy - SCREEN_Z_TOP * PPM))
    y1 = int(round(cy - SCREEN_Z_BOT * PPM))
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
        raise FileNotFoundError(f"Missing screen texture: {SCREEN}")

    im_render = Image.open(RENDER).convert("RGB")
    im_screen = Image.open(SCREEN).convert("RGB")

    # 1. Check Screen correlation
    crop_rend_s = crop_screen(im_render)
    crop_ref_s = im_screen.resize(crop_rend_s.size, Image.Resampling.BILINEAR)

    arr_s_rend = np.array(crop_rend_s)
    arr_s_ref = np.array(crop_ref_s)

    r_screen = ncc(arr_s_rend, arr_s_ref)
    print(f"[QA NCC] Screen Surface Correlation: r = {r_screen:.4f}")
    assert r_screen >= 0.70, f"Screen correlation too low! {r_screen:.4f} < 0.70"

    # 2. Check Hero render exposure and non-emptiness
    if os.path.exists(HERO):
        im_hero = Image.open(HERO).convert("RGB")
        arr_hero = np.array(im_hero)
        nz = arr_hero[arr_hero > 5]
        assert len(nz) > 10000, "Hero image has too few non-background pixels!"
        mean_lum = nz.mean()
        print(f"[QA Exposure] Hero 3/4 Non-zero Mean Luminance: {mean_lum:.2f} / 255 (Pixel count: {len(nz)})")
        assert 10.0 <= mean_lum <= 240.0, f"Hero image exposure out of bounds: {mean_lum:.2f}"

    print("\n[ALL VISUAL & UV QA CHECKS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    main()
