"""
Render <-> atlas karsilastirmasi (Asset 44 QA).

1) GLOBAL YON: on yuz etiketinin dokuya 1:1 oturdugu dogrulanir.
2) YEREL KORELASYON: hucreler arasi NCC (Card_Area ve LED'ler covered_mask ile haric tutulur).
3) YER ISARETLERI: antrasit govde + yesil/kirmizi LED varligi.
4) METIN MUREKKEBI: baslik, alt yazi, seri no.
"""

import os
from PIL import Image, ImageChops, ImageDraw, ImageStat
import numpy as np
import math

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
EXPORTS = os.path.join(ASSET, "exports")
QA = os.path.join(ASSET, "qa")

RENDER = os.path.join(QA, "front_flat.png")
ATLAS = os.path.join(EXPORTS, "T_Security_Atlas.png")

HOUSING_PX = (32, 32, 1032, 2016)
RES = 900.0
ORTHO = 0.145                                  # render_qa FLAT_ORTHO
PPM = RES / ORTHO
HALF_X, HALF_Z = 0.0265, 0.0565                # 53 x 113 mm etiket on yuzu

LED_X_M = 0.0130
LED_Z_M = 0.0380
CARD_Z_M = -0.0060

LANDMARKS = [
    # (etiket, atlas_xy, tip, radius)
    ("Govde antrasit", (200, 200), "body_dark", 8),
    ("LED_Red (kirmizi)", (300, 362), "led_red", 6),
    ("LED_Green (yesil)", (764, 362), "led_green", 6),
    ("Kart alani cebi", (532, 1100), "card_pocket", 10),
]

INK_CHECKS = [
    ("Baslik 'SEC-CR 440'", (76, 75, 450, 125), "bright_on_dark", 120),
    ("Alt baslik 'RUGGED RFID'", (76, 130, 450, 160), "bright_on_dark", 100),
    ("Seri no 'SN 44-CR'", (76, 1920, 380, 1955), "bright_on_dark", 100),
]


def covered_mask(size):
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    bw, bh = size
    mm_to_px = bw / (HALF_X * 2.0 * 1000.0)

    # Card_Area (46 x 52 mm @ Z = -0.0060)
    cx = bw / 2.0
    nz = (CARD_Z_M + HALF_Z) / (2.0 * HALF_Z)
    cy = bh - nz * bh
    hw = (0.0460 * 1000.0 * mm_to_px) / 2.0 + 8
    hh = (0.0520 * 1000.0 * mm_to_px) / 2.0 + 8
    d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=0)

    # LED'ler
    for lx_m in (-LED_X_M, LED_X_M):
        nx = (lx_m + HALF_X) / (2.0 * HALF_X)
        lx = bw - nx * bw
        nz_led = (LED_Z_M + HALF_Z) / (2.0 * HALF_Z)
        ly = bh - nz_led * bh
        d.ellipse([lx - 30, ly - 30, lx + 30, ly + 30], fill=0)

    return mask


def crop_housing(im):
    x0 = RES / 2.0 - HALF_X * PPM
    x1 = RES / 2.0 + HALF_X * PPM
    y0 = RES / 2.0 - HALF_Z * PPM
    y1 = RES / 2.0 + HALF_Z * PPM
    return im.crop((round(x0), round(y0), round(x1), round(y1)))


def patch_mean(im, xy, r=6):
    x, y = int(xy[0]), int(xy[1])
    box = (max(0, x - r), max(0, y - r), min(im.width, x + r + 1), min(im.height, y + r + 1))
    return ImageStat.Stat(im.crop(box)).mean[:3]


def ncc(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    da = [x - ma for x in a]
    db = [y - mb for y in b]
    num = sum(x * y for x, y in zip(da, db))
    den = math.sqrt(sum(x * x for x in da) * sum(y * y for y in db))
    return (num / den) if den > 1e-9 else 0.0


def cellwise_ncc(band, shot, mask, nx=6, ny=8, cell=26, cover_limit=0.30):
    bw, bh = band.size
    cw, ch = bw / float(nx), bh / float(ny)
    rows = []
    for j in range(ny):
        row = []
        for i in range(nx):
            box = (int(i * cw), int(j * ch), int((i + 1) * cw), int((j + 1) * ch))
            mc = ImageStat.Stat(mask.crop(box)).mean[0] / 255.0
            if (1.0 - mc) > cover_limit:
                row.append(None)
                continue
            st_a = ImageStat.Stat(band.crop(box)).stddev[0]
            if st_a < 12.0:
                row.append(None)
                continue
            a = list(band.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            b = list(shot.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            row.append(ncc(a, b))
        rows.append(row)
    return rows


def main():
    render = Image.open(RENDER).convert("RGB")
    atlas = Image.open(ATLAS).convert("RGB")

    band_rgb = atlas.crop(HOUSING_PX)
    band = band_rgb.convert("L")
    shot_rgb = crop_housing(render)
    shot = shot_rgb.convert("L").resize(band.size, Image.LANCZOS)
    mask = covered_mask(band.size)

    # 1) Yon testi
    diff = ImageChops.difference(shot, band)
    mad = ImageStat.Stat(diff, mask=mask).mean[0] / 255.0
    print(f"[QA] Duz eslesme ortalama fark: {mad * 100:.2f}%")
    assert mad < 0.12, f"FAIL: doku render ile uyusmuyor ({mad*100:.1f}%)"
    print("[PASS] RFID okuyucu paneli etiketi dogru yonde ve oranda!")

    # 2) Hucre korelasyonu
    rows = cellwise_ncc(band, shot, mask)
    flat = [r for row in rows for r in row if r is not None]
    good = sum(1 for r in flat if r >= 0.60)
    worst = min(flat)
    print(f"[QA] Hucre korelasyonu: olculen {len(flat)}, en dusuk r={worst:.2f}, r>=0.60 orani: {100.0 * good / len(flat):.1f}%")
    assert good / len(flat) >= 0.85, "FAIL: hucre korelasyonu dusuk"
    print("[PASS] Panel bolgeleri dokudan sasmiyor!")

    # 3) Yer isaretleri
    shot_sized = shot_rgb.resize(band.size, Image.LANCZOS)
    ox, oy = HOUSING_PX[0], HOUSING_PX[1]
    for label, xy, kind, radius in LANDMARKS:
        local = (xy[0] - ox, xy[1] - oy)
        rr = patch_mean(shot_sized, local, r=radius)
        if kind == "body_dark":
            ok = rr[0] < 60 and rr[1] < 65 and rr[2] < 70
        elif kind == "led_green":
            ok = rr[1] > rr[0] + 30 and rr[1] > rr[2] + 20
        elif kind == "led_red":
            ok = rr[0] > rr[1] + 40 and rr[0] > rr[2] + 40
        elif kind == "card_pocket":
            ok = rr[0] < 50 and rr[1] < 55 and rr[2] < 65
        else:
            ok = False
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:26s} render RGB=({rr[0]:.1f}, {rr[1]:.1f}, {rr[2]:.1f})")
        assert ok, f"FAIL: {label} yer isareti dogrulanamadi"
    print("[PASS] Govde ve LED yer isaretleri dogrulandi!")

    # 4) Metin murekkebi
    for label, rect, kind, hi_min in INK_CHECKS:
        box = (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)
        patch = shot_sized.crop(box).convert("L")
        lums = patch.tobytes()
        lo, hi = min(lums), max(lums)
        ok = hi > hi_min and lo < 60
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:26s} parlaklik {lo}..{hi} (> {hi_min})")
        assert ok, f"FAIL: {label} metin murekkebi okunamadi"
    print("[PASS] Tum metinler yuksek kontrastla okunur!")
    print("[ALL RENDER<->ATLAS CHECKS PASSED FOR ASSET 44]")


if __name__ == "__main__":
    main()
