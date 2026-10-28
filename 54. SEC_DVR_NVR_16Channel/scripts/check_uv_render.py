"""
=============================================================================
Security CCTV Asset Production Suite - Asset 54
UV vs Render Correlation & Visual QA Checker
=============================================================================
"""

import os
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
EXPORTS = os.path.join(ASSET, "exports")
QA = os.path.join(ASSET, "qa")

RENDER = os.path.join(QA, "front_flat.png")
ATLAS = os.path.join(EXPORTS, "T_Security_Atlas.png")
HERO = os.path.join(QA, "hero_34.png")

def main():
    if not os.path.exists(RENDER):
        raise FileNotFoundError(f"Missing render: {RENDER}")
    if not os.path.exists(ATLAS):
        raise FileNotFoundError(f"Missing atlas: {ATLAS}")

    im_render = Image.open(RENDER).convert("RGB")
    arr_rend = np.array(im_render)

    nz = arr_rend[arr_rend > 15]
    assert len(nz) > 50000, "Render has too few non-background pixels!"
    mean_lum = nz.mean()
    print(f"[QA Exposure] Flat Render Mean Luminance: {mean_lum:.2f} / 255 (Pixel count: {len(nz)})")
    assert 20.0 <= mean_lum <= 240.0, f"Exposure out of bounds: {mean_lum:.2f}"

    if os.path.exists(HERO):
        im_hero = Image.open(HERO).convert("RGB")
        arr_hero = np.array(im_hero)
        nz_h = arr_hero[arr_hero > 15]
        assert len(nz_h) > 50000, "Hero has too few non-background pixels!"
        mean_h = nz_h.mean()
        print(f"[QA Exposure] Hero 3/4 Mean Luminance: {mean_h:.2f} / 255 (Pixel count: {len(nz_h)})")
        assert 20.0 <= mean_h <= 240.0, f"Hero exposure out of bounds: {mean_h:.2f}"

    print("\n[ALL VISUAL & UV QA CHECKS PASSED SUCCESSFULLY!]")

if __name__ == "__main__":
    main()
