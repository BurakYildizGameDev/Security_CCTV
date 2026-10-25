"""
Render <-> atlas karsilastirmasi (Asset 40 QA).

EGIMLI YUZ NOTU: Govde 28 derece egimli. `render_qa.py` flat kamerayi YUZ
NORMALI boyunca yerlestirdigi icin fore-shortening yoktur ve yuz merkezi tam
goruntu merkezine duser; bu sayede 1:1 karsilastirma gecerli kalir.

1) GLOBAL YON: duz / ayna / ters / 180 korelasyonu.
2) YEREL (HUCRE) KORELASYON: 8x6 hucre; RFID plakasi ve LED halkasi
   `covered_mask()` ile olcum disinda birakilir.
3) YER ISARETLERI: marka plakasi, amber serit, RFID yuvasi halkasi, govde
   zemini dokuyla; RFID plakasi ve LED halkasi varlik olarak dogrulanir.
4) METIN MUREKKEBI: baslik, "PRESENT CARD" ve alt kimlik satiri.

Cikis kodu 0 -> tum kontroller gecti, 1 -> assert/FAIL.
Calistirma:
    python scripts/check_uv_render.py
"""
import os
from PIL import Image, ImageChops, ImageDraw, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
EXPORTS = os.path.join(ASSET, "exports")
QA = os.path.join(ASSET, "qa")

RENDER = os.path.join(QA, "front_flat.png")
ATLAS = os.path.join(EXPORTS, "T_Security_Atlas.png")

COVER_PX = (32, 32, 1308, 1660)          # generate_textures.py ile ayni
RES = 900.0
ORTHO = 0.115                            # m (render_qa.py ile ayni)
PPM = RES / ORTHO                        # px / m
HALF_X, HALF_Z = 0.0290, 0.0370          # 58 x 74 mm okuma yuzu

# 3D parcalarin yuzde kapladigi alan (generate_SEC_Access_Turnstile_Reader.py)
RFID_X, RFID_Z, RFID_HX, RFID_HZ = 0.0, -0.0140, 0.0210, 0.0170
LED_X, LED_Z, LED_R_OUT = 0.0160, 0.0160, 0.0070

LANDMARKS = [
    # Marka plakasinin bos koyu alani: alt yazi (x<=...) ile IP66 arasi
    ("Marka plakasi (koyu)", (500, 240), "dark", 6),
    ("Amber serit (plaka)", (81, 200), "amber", 3),
    ("RFID yuvasi halkasi", (190, 1154), "soft", 4),
    ("Govde zemini", (1240, 620), "body", 6),
    # 3D kaplanan bolgeler: varlik kontrolu
    ("RFID plakasi", (670, 1154), "rfid_dark", 10),
    # Halka annulus oldugu icin MERKEZ bosluktur; yesil halka ~0.87 yaricapta
    ("LED halkasi (yesil)", (452, 494), "led_green", 4),
]

INK_CHECKS = [
    ("Baslik 'SEC-TR 150'", (120, 108, 620, 190), "bright_on_dark", 195),
    ("'PRESENT CARD'", (560, 392, 980, 450), "dark_on_light", 60),
    ("Alt satir 'SN 40-TR'", (90, 1545, 420, 1572), "dark_on_light", 175),
]


def cover_px_local(x_m, z_m):
    """Yuz yerel (X, Z) konumunu COVER bantinin yerel pikseline cevirir."""
    bw = COVER_PX[2] - COVER_PX[0]
    bh = COVER_PX[3] - COVER_PX[1]
    nx = (x_m + HALF_X) / (2.0 * HALF_X)
    nz = (z_m + HALF_Z) / (2.0 * HALF_Z)
    return (bw - nx * bw, bh - nz * bh)


def covered_mask(size):
    """RFID plakasi ve LED halkasi tarafindan kapatilan bolgeler 0, serbest 255."""
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    mm_to_px = (COVER_PX[2] - COVER_PX[0]) / (HALF_X * 2.0 * 1000.0)
    cx, cy = cover_px_local(RFID_X, RFID_Z)
    hw = RFID_HX * 1000.0 * mm_to_px + 12
    hh = RFID_HZ * 1000.0 * mm_to_px + 12
    d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=0)
    lcx, lcy = cover_px_local(LED_X, LED_Z)
    lr = (LED_R_OUT * 1000.0 + 1.2) * mm_to_px
    d.ellipse([lcx - lr, lcy - lr, lcx + lr, lcy + lr], fill=0)
    return mask


def crop_cover(im):
    """Okuma yuzunun render uzerindeki dikdortgeni (merkezli, fore-shortening yok)."""
    x0 = RES / 2.0 - HALF_X * PPM
    x1 = RES / 2.0 + HALF_X * PPM
    y0 = RES / 2.0 - HALF_Z * PPM
    y1 = RES / 2.0 + HALF_Z * PPM
    return im.crop((round(x0), round(y0), round(x1), round(y1)))


def patch_mean(im, xy, r=8):
    x, y = int(xy[0]), int(xy[1])
    box = (max(0, x - r), max(0, y - r),
           min(im.size[0], x + r), min(im.size[1], y + r))
    return ImageStat.Stat(im.crop(box)).mean[:3]


def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ncc(pa, pb):
    n = len(pa)
    ma = sum(pa) / float(n)
    mb = sum(pb) / float(n)
    va = sum((v - ma) ** 2 for v in pa)
    vb = sum((v - mb) ** 2 for v in pb)
    if va < 1e-6 or vb < 1e-6:
        return None
    cov = sum((pa[i] - ma) * (pb[i] - mb) for i in range(n))
    return cov / ((va * vb) ** 0.5)


def cellwise_ncc(band, shot, mask, nx=8, ny=6, cell=26, inset=0.05,
                 cover_limit=0.25):
    """Yuzu hucrelere bolup her hucrede doku-render korelasyonunu olcer."""
    bw, bh = band.size
    ix, iy = bw * inset, bh * inset
    cw, ch = (bw - 2 * ix) / float(nx), (bh - 2 * iy) / float(ny)
    rows = []
    for j in range(ny):
        row = []
        for i in range(nx):
            box = (int(round(ix + i * cw)), int(round(iy + j * ch)),
                   int(round(ix + (i + 1) * cw)), int(round(iy + (j + 1) * ch)))
            mc = ImageStat.Stat(mask.crop(box)).mean[0] / 255.0
            if (1.0 - mc) > cover_limit:
                row.append(None)          # 3D RFID plakasi / LED bu hucreyi kapliyor
                continue
            a = list(band.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            b = list(shot.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            row.append(ncc(a, b))
        rows.append(row)
    return rows


def main():
    render = Image.open(RENDER).convert("RGB")
    atlas = Image.open(ATLAS).convert("RGB")
    band_rgb = atlas.crop(COVER_PX)
    band = band_rgb.convert("L")
    shot_rgb = crop_cover(render)
    shot = shot_rgb.convert("L").resize(band.size, Image.LANCZOS)
    mask = covered_mask(band.size)

    variants = {
        "duz (dogru)": shot,
        "yatay ayna": shot.transpose(Image.FLIP_LEFT_RIGHT),
        "dikey ters": shot.transpose(Image.FLIP_TOP_BOTTOM),
        "180 donuk": shot.transpose(Image.ROTATE_180),
    }
    scores = {}
    for name, img in variants.items():
        diff = ImageChops.difference(img, band)
        mad = ImageStat.Stat(diff, mask=mask).mean[0] / 255.0
        scores[name] = mad
        print(f"[QA] {name:14s} ortalama fark: {mad * 100:5.2f}%  (3D kaplama haric)")

    best = min(scores, key=scores.get)
    ordered = sorted(scores.values())
    print(f"[QA] En iyi eslesme: {best}")
    assert best == "duz (dogru)", f"FAIL: doku yonu hatali (en iyi: {best})"
    assert ordered[0] < 0.12, f"FAIL: render ile atlas uyusmuyor ({ordered[0]*100:.1f}%)"
    assert ordered[1] - ordered[0] > 0.01, "FAIL: yon ayrimi belirsiz"
    print("[PASS] Egimli okuma yuzu etiketi dogru yonde ve sikismasiz")

    # ------------------------------------------------------------ 2) Hucre korelasyonu
    rows = cellwise_ncc(band, shot, mask)
    flat = [r for row in rows for r in row if r is not None]
    skipped = sum(1 for row in rows for r in row if r is None)
    worst = min(flat)
    worst_pos = [(i, j) for j, row in enumerate(rows)
                 for i, r in enumerate(row) if r is not None and r == worst][0]
    good = sum(1 for r in flat if r >= 0.60)
    print(f"[QA] Hucre korelasyonu: olculen {len(flat)} / atlanan {skipped} "
          f"(3D kaplama veya duz zemin) | en dusuk r={worst:.2f} "
          f"@ kolon {worst_pos[0]}, satir {worst_pos[1]}")
    print(f"[QA] r>=0.60 hucre orani: {100.0 * good / len(flat):.1f}%")
    for row in rows:
        print("     " + " ".join("  ---" if r is None else f"{r:+.2f}" for r in row))
    assert worst >= 0.35, f"FAIL: yerel doku kaymasi (en dusuk hucre korelasyonu {worst:.2f})"
    assert good / len(flat) >= 0.85, "FAIL: hucrelerin %15'inden fazlasi dokudan sapiyor"
    print("[PASS] Tum yuz bolgeleri dokudan sasmiyor (yerel korelasyon)")

    # ------------------------------------------------------------ 3) Yer isaretleri
    shot_sized = shot_rgb.resize(band.size, Image.LANCZOS)
    ox, oy = COVER_PX[0], COVER_PX[1]
    problems = []
    for label, xy, kind, radius in LANDMARKS:
        local = (xy[0] - ox, xy[1] - oy)
        ar = patch_mean(band_rgb, local, r=radius)
        rr = patch_mean(shot_sized, local, r=radius)
        d = max(abs(ar[i] - rr[i]) for i in range(3))
        if kind == "dark":
            ok = luminance(rr) < 90 and d <= 70
        elif kind == "amber":
            ok = rr[0] > 200 and rr[1] > 140 and rr[2] < 90 and d <= 40
        elif kind == "body":
            ok = luminance(rr) > 175 and d <= 60
        elif kind == "soft":
            ok = 35 < luminance(rr) < 115 and max(rr) - min(rr) < 50
        elif kind == "rfid_dark":
            ok = luminance(rr) < 100
        elif kind == "led_green":
            ok = (rr[1] - max(rr[0], rr[2])) > 30 and luminance(rr) > 70
        else:
            ok = False
        note = ""
        if kind in ("rfid_dark", "led_green"):
            note = "  (3D mesh atlas alanini kaplar, sapma beklenen)"
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:22s} "
              f"atlas RGB=({ar[0]:5.1f},{ar[1]:5.1f},{ar[2]:5.1f}) "
              f"render RGB=({rr[0]:5.1f},{rr[1]:5.1f},{rr[2]:5.1f}) sapma={d:4.1f}{note}")
        if not ok:
            problems.append(label)

    for label, rect, kind, hi_min in INK_CHECKS:
        box = (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)
        patch = shot_sized.crop(box)
        lums = patch.convert("L").tobytes()
        lo, hi = min(lums), max(lums)
        if kind == "bright_on_dark":
            ok = lo < 110 and hi > hi_min
            info = f"parlaklik {lo}..{hi} (koyu zemin + yazi > {hi_min})"
        else:
            ok = lo < hi_min and hi > 150
            info = f"parlaklik {lo}..{hi} (acik zemin + koyu yazi < {hi_min})"
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:26s} {info}")
        if not ok:
            problems.append(label)

    if problems:
        raise AssertionError("FAIL: yer isaretleri hatali -> " + ", ".join(problems))
    print("[PASS] Plaka / amber serit / RFID halkasi / govde zemini dogru konumda")
    print("[PASS] RFID plakasi ve LED halkasi render'da dogru (3D kaplama)")
    print("[PASS] Baslik / 'PRESENT CARD' / alt kimlik satiri okunur (ink)")
    print("[ALL RENDER<->ATLAS CHECKS PASSED]")


if __name__ == "__main__":
    main()

