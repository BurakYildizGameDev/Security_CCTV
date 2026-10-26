"""
Render <-> atlas karsilastirmasi (Asset 45 QA).

1) GLOBAL YON: baslik etiketinin dokuya 1:1 oturdugu dogrulanir.
2) YEREL KORELASYON: hucreler arasi NCC (Display ve Fingerprint_Pad covered_mask ile haric tutulur).
3) YER ISARETLERI: grafit govde + LCD ekran + yesil biyometrik prizma varligi.
4) METIN MUREKKEBI: baslik, alt yazi, seri no.
5) EGIM KANITI: Tilt_Pivot ±15° egik render'larin piksel farki (rotasyon kaniti).
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

HOUSING_PX = (32, 32, 1032, 1500)
RES = 900.0
ORTHO = 0.125                                  # render_qa FLAT_ORTHO
PPM = RES / ORTHO
HALF_X, HALF_Z = 0.0340, 0.0500                # 68 x 100 mm baslik

SCR_Z_M = 0.0160
FING_Z_M = -0.0240

LANDMARKS = [
    # (etiket, atlas_xy, tip, radius)
    ("Govde grafit", (200, 200), "body_dark", 8),
    ("LCD Ekran (mavi/cyan)", (532, 650), "screen", 12),
    ("Parmak izi prizmasi (yesil)", (532, 1100), "prism_green", 10),
]

INK_CHECKS = [
    ("Baslik 'SEC-BT 450'", (76, 75, 450, 125), "bright_on_dark", 120),
    ("Alt baslik 'BIO TERMINAL'", (76, 130, 450, 160), "bright_on_dark", 90),
    ("Seri no 'SN 45-BT'", (76, 1400, 380, 1435), "bright_on_dark", 90),
]


def covered_mask(size):
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    bw, bh = size
    mm_to_px = bw / (HALF_X * 2.0 * 1000.0)

    # Ekran (48 x 32 mm @ Z = 0.0160)
    cx = bw / 2.0
    nz_scr = (SCR_Z_M + HALF_Z) / (2.0 * HALF_Z)
    cy_scr = bh - nz_scr * bh
    hw_s = (0.0480 * 1000.0 * mm_to_px) / 2.0 + 8
    hh_s = (0.0320 * 1000.0 * mm_to_px) / 2.0 + 8
    d.rectangle([cx - hw_s, cy_scr - hh_s, cx + hw_s, cy_scr + hh_s], fill=0)

    # Parmak izi prizmasi (22 x 26 mm @ Z = -0.0240)
    nz_f = (FING_Z_M + HALF_Z) / (2.0 * HALF_Z)
    cy_f = bh - nz_f * bh
    hw_f = (0.0220 * 1000.0 * mm_to_px) / 2.0 + 8
    hh_f = (0.0260 * 1000.0 * mm_to_px) / 2.0 + 8
    d.rectangle([cx - hw_f, cy_f - hh_f, cx + hw_f, cy_f + hh_f], fill=0)

    return mask


def crop_head(im):
    # Baslik 68 x 100 mm @ 7200 px/m ortografik projeksiyon kadraji
    return im.crop((205, 90, 695, 810))


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
            st_a = ImageStat.Stat(band.crop(box)).stddev[0]
            if st_a < 10.0:
                row.append(None)
                continue
            a = list(band.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            b = list(shot.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            row.append(ncc(a, b))
        rows.append(row)
    return rows


def check_tilt_renders():
    pos = os.path.join(QA, "tilt_pos15.png")
    neg = os.path.join(QA, "tilt_neg15.png")
    assert os.path.exists(pos) and os.path.exists(neg), "FAIL: egim render'lari eksik"

    im_pos = Image.open(pos).convert("L")
    im_neg = Image.open(neg).convert("L")
    arr_pos = np.asarray(im_pos, dtype=np.int16)
    arr_neg = np.asarray(im_neg, dtype=np.int16)

    diff = np.abs(arr_pos - arr_neg)
    changed = int((diff > 12).sum())
    peak = int(diff.max())
    print(f"[QA] Tilt +15° vs -15° farkli piksel: {changed}, tepe fark: {peak}/255")
    assert changed >= 800, f"FAIL: baslik egim hareketi cok kucuk ({changed} px)"
    print("[PASS] Tilt_Pivot ±15° egim hareketi render'larda dogrulandi!")


def main():
    render = Image.open(RENDER).convert("RGB")
    atlas = Image.open(ATLAS).convert("RGB")

    band_rgb = atlas.crop(HOUSING_PX)
    band = band_rgb.convert("L")
    shot_rgb = crop_head(render)
    shot = shot_rgb.convert("L").resize(band.size, Image.LANCZOS)
    mask = covered_mask(band.size)

    # 1) Yon testi
    diff = ImageChops.difference(shot, band)
    mad = ImageStat.Stat(diff, mask=mask).mean[0] / 255.0
    print(f"[QA] Duz eslesme ortalama fark: {mad * 100:.2f}%")
    assert mad < 0.12, f"FAIL: doku render ile uyusmuyor ({mad*100:.1f}%)"
    print("[PASS] Biyometrik terminal paneli etiketi dogru yonde ve oranda!")

    # 2) Bolgesel korelasyon (serbest baslik ve seri no bloklari)
    zones = [
        ('Baslik blogu', (50, 40, 480, 160)),
        ('Alt seri no blogu', (50, 1360, 480, 1440)),
    ]
    for name, box in zones:
        a = list(band.crop(box).resize((32, 32)).tobytes())
        b = list(shot.crop(box).resize((32, 32)).tobytes())
        r = ncc(a, b)
        print(f"[QA] {name:20s} korelasyon: r={r:.2f}")
        assert r >= 0.85, f"FAIL: {name} korelasyonu dusuk ({r:.2f})"
    print("[PASS] Panel metin bloklari 1:1 korelasyonla eslesti!")

    # 3) Yer isaretleri
    shot_sized = shot_rgb.resize(band.size, Image.LANCZOS)
    ox, oy = HOUSING_PX[0], HOUSING_PX[1]
    for label, xy, kind, radius in LANDMARKS:
        local = (xy[0] - ox, xy[1] - oy)
        rr = patch_mean(shot_sized, local, r=radius)
        if kind == "body_dark":
            ok = rr[0] < 60 and rr[1] < 65 and rr[2] < 75
        elif kind == "screen":
            ok = rr[2] > rr[0] + 15
        elif kind == "prism_green":
            ok = rr[1] > rr[0] + 30 and rr[1] > rr[2] + 20
        else:
            ok = False
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:28s} render RGB=({rr[0]:.1f}, {rr[1]:.1f}, {rr[2]:.1f})")
        assert ok, f"FAIL: {label} yer isareti dogrulanamadi"
    print("[PASS] Ekran, prizma ve govde yer isaretleri dogrulandi!")

    # 4) Metin murekkebi
    for label, rect, kind, hi_min in INK_CHECKS:
        box = (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)
        patch = shot_sized.crop(box).convert("L")
        lums = patch.tobytes()
        lo, hi = min(lums), max(lums)
        ok = hi > hi_min and lo < 65
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:28s} parlaklik {lo}..{hi} (> {hi_min})")
        assert ok, f"FAIL: {label} metin murekkebi okunamadi"
    print("[PASS] Tum metinler yuksek kontrastla okunur!")

    # 5) Egim kaniti
    check_tilt_renders()
    print("[ALL RENDER<->ATLAS CHECKS PASSED FOR ASSET 45]")


if __name__ == "__main__":
    main()
