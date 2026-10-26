"""
Render <-> atlas karsilastirmasi (Asset 43 QA).

1) GLOBAL YON: on yuz etiketinin dokuya 1:1 oturdugu dogrulanir.
2) YEREL KORELASYON: hucreler arasi NCC (kilit silindiri covered_mask ile haric tutulur).
3) YER ISARETLERI: govde metali + pozisyon renkleri (OFF kirmizi, ON yesil, BYPASS amber).
4) METIN MUREKKEBI: baslik, alt yazi, seri no.
5) DONUS KANITI: -45° ve +45° render'larin piksel farki (rotasyon kaniti).
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

PLATE_PX = (32, 32, 1432, 1432)
RES = 900.0
ORTHO = 0.095                                  # render_qa FLAT_ORTHO
PPM = RES / ORTHO
HALF_X, HALF_Z = 0.0350, 0.0350                # 70 x 70 mm

CYL_R_M = 0.0110

LANDMARKS = [
    # (etiket, atlas_xy, tip, radius)
    ("Govde metali", (250, 250), "body", 8),
    ("OFF pozisyonu (kirmizi)", (732, 404), "red", 8),
    ("ON pozisyonu (yesil)", (969, 506), "green", 8),
    ("BYPASS pozisyonu (amber)", (487, 506), "amber", 8),
]

INK_CHECKS = [
    ("Baslik 'SEC-KS 100'", (84, 82, 450, 134), "dark_on_light", 70),
    ("Alt baslik 'KEY ACCESS'", (84, 144, 450, 170), "dark_on_light", 80),
    ("Seri no 'SN 43-KS'", (84, 1347, 400, 1375), "dark_on_light", 120),
]


def covered_mask(size):
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    cx, cy = size[0] / 2.0, size[1] / 2.0
    mm_to_px = (PLATE_PX[2] - PLATE_PX[0]) / (HALF_X * 2.0 * 1000.0)
    # Silindir ve anahtar basligi alani maskelenir
    r = (CYL_R_M * 1000.0 * mm_to_px) + 24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    # Anahtar basligi dikey uzantisi
    d.rectangle([cx - 40, cy - r - 40, cx + 40, cy + r + 40], fill=0)
    return mask


def crop_plate(im):
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


import math


def cellwise_ncc(band, shot, mask, nx=6, ny=6, cell=26, cover_limit=0.30):
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
            a = list(band.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            b = list(shot.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            row.append(ncc(a, b))
        rows.append(row)
    return rows


def check_rotation_renders():
    neg = os.path.join(QA, "key_turned_neg45.png")
    pos = os.path.join(QA, "key_turned_pos45.png")
    assert os.path.exists(neg) and os.path.exists(pos), "FAIL: rotasyon render'lari eksik"

    im_neg = Image.open(neg).convert("L")
    im_pos = Image.open(pos).convert("L")
    arr_neg = np.asarray(im_neg, dtype=np.int16)
    arr_pos = np.asarray(im_pos, dtype=np.int16)

    diff = np.abs(arr_neg - arr_pos)
    changed = int((diff > 12).sum())
    peak = int(diff.max())
    print(f"[QA] Rotasyon -45° vs +45° farkli piksel: {changed}, tepe fark: {peak}/255")
    assert changed >= 500, f"FAIL: anahtar rotasyon farki cok kucuk ({changed} px)"
    print("[PASS] Key_Rotation_Pivot ±45° rotasyon hareketi render'larda dogrulandi!")


def main():
    render = Image.open(RENDER).convert("RGB")
    atlas = Image.open(ATLAS).convert("RGB")

    band_rgb = atlas.crop(PLATE_PX)
    band = band_rgb.convert("L")
    shot_rgb = crop_plate(render)
    shot = shot_rgb.convert("L").resize(band.size, Image.LANCZOS)
    mask = covered_mask(band.size)

    # 1) Yon testi
    diff = ImageChops.difference(shot, band)
    mad = ImageStat.Stat(diff, mask=mask).mean[0] / 255.0
    print(f"[QA] Duz eslesme ortalama fark: {mad * 100:.2f}%")
    assert mad < 0.12, f"FAIL: doku render ile uyusmuyor ({mad*100:.1f}%)"
    print("[PASS] Anahtarli salter paneli etiketi dogru yonde ve oranda!")

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
    ox, oy = PLATE_PX[0], PLATE_PX[1]
    for label, xy, kind, radius in LANDMARKS:
        local = (xy[0] - ox, xy[1] - oy)
        rr = patch_mean(shot_sized, local, r=radius)
        if kind == "body":
            ok = rr[0] > 180 and rr[1] > 180 and rr[2] > 180
        elif kind == "red":
            ok = rr[0] > rr[1] + 40 and rr[0] > rr[2] + 40
        elif kind == "green":
            ok = rr[1] > rr[0] + 30 and rr[1] > rr[2] + 20
        elif kind == "amber":
            ok = rr[0] > 140 and rr[1] > 90 and rr[2] < rr[1]
        else:
            ok = False
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:26s} render RGB=({rr[0]:.1f}, {rr[1]:.1f}, {rr[2]:.1f})")
        assert ok, f"FAIL: {label} yer isareti dogrulanamadi"
    print("[PASS] Pozisyon renkleri ve govde metali dogrulandi!")

    # 4) Metin murekkebi
    for label, rect, kind, hi_min in INK_CHECKS:
        box = (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)
        patch = shot_sized.crop(box).convert("L")
        lums = patch.tobytes()
        lo, hi = min(lums), max(lums)
        ok = lo < hi_min and hi > 160
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:26s} parlaklik {lo}..{hi} (< {hi_min})")
        assert ok, f"FAIL: {label} metin murekkebi okunamadi"
    print("[PASS] Tum metinler yuksek kontrastla okunur!")

    # 5) Donus kaniti
    check_rotation_renders()
    print("[ALL RENDER<->ATLAS CHECKS PASSED FOR ASSET 43]")


if __name__ == "__main__":
    main()
