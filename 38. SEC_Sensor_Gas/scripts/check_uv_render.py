"""
Render <-> atlas karsilastirmasi (Asset 38 QA).

1) GLOBAL YON: On yuz etiketinin dokuya 1:1 oturdugu, sikismadigi ve MIRROR
   OLMADIGI sayisal olarak dogrulanir (duz / ayna / ters / 180 korelasyonu).
2) YEREL (HUCRE) KORELASYON: On yuz 8x6 hucreye bolunur; her hucrenin doku ile
   korelasyonu olculur. 3D kubbe kapak ve LED lensi hucreleri `covered_mask()`
   ile olcum disinda birakilir (kaplanmis doku render'da gorunmez).
3) YER ISARETLERI (landmark): Etiket plakasi, amber serit, kubbe gomme halkasi,
   govde zemini ve alarm lensi render'da BEKLENEN konumda mi?
4) METIN MUREKKEBI (ink): Baslik ve teknik satirlar render'da gercekten okunur
   durumda mi (koyu plaka + parlak yazi kontrasti)?

Cikis kodu 0 -> tum kontroller gecti, 1 -> assert/FAIL.
Render yoksa once scripts/render_qa.py calistirilmalidir.

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

COVER_PX = (32, 32, 1832, 1688)          # generate_textures.py ile ayni
RES = 900.0
ORTHO = 0.105                            # m (kamera)
PPM = RES / ORTHO                        # px / m
CAM_Z = 0.0
HALF_X, HALF_Z = 0.0250, 0.0230

# 3D parcalarin on yuzde kapladigi alan (generate_SEC_Sensor_Gas.py ile ayni)
VENT_X, VENT_Z, VENT_R = 0.0, 0.0060, 0.0140
LED_X, LED_Z, LED_R = 0.0195, 0.0160, 0.0030

# Landmark konumlari (ATLAS pikseli) ve beklenen gorunum
LANDMARKS = [
    # Plakanin sag-orta bos koyu alani: alt yazi (x<=538) ile barkod (x>=1400) arasi.
    ("Etiket plakasi (koyu)", (700, 1600), "dark", 8),
    ("Amber serit", (128, 1400), "amber", 3),
    ("Kubbe gomme halkasi", (932, 122), "dark", 6),
    ("Govde zemini", (1700, 400), "body", 6),
    # 3D lens atlasin bu bolgesini kaplar; renk kontrolu lensin kendi uzerinde
    ("Alarm lensi (kirmizi)", (291, 345), "led_red", 6),
]

# Doku uzerinde metin/grafik gorunuyor mu? (kirpilma / bos alan kontrolu)
# (etiket, atlas_rect, tip, parlak_ust_esik): teknik satirlar COOL_LIGHT tonunda
# yazildigi icin (luminans ~193) beyaz baslikla ayni esik kullanilamaz.
INK_CHECKS = [
    ("Baslik 'SEC-GD 400'", (170, 1225, 950, 1312), "bright_on_dark", 195),
    ("Teknik satir 'CH4 0-100 %LEL'", (170, 1368, 900, 1406), "bright_on_dark", 170),
]


def cover_px_local(x_m, z_m):
    """On yuz (X, Z) konumunu COVER bantinin yerel pikseline cevirir (flip_u)."""
    bw = COVER_PX[2] - COVER_PX[0]
    bh = COVER_PX[3] - COVER_PX[1]
    nx = (x_m + HALF_X) / (2.0 * HALF_X)
    nz = (z_m + HALF_Z) / (2.0 * HALF_Z)
    return (bw - nx * bw, bh - nz * bh)


def covered_mask(size):
    """3D kubbe/LED tarafindan kapatilan bolgeler 0, serbest doku 255."""
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    mm_to_px = (COVER_PX[2] - COVER_PX[0]) / (HALF_X * 2.0 * 1000.0)
    cx, cy = cover_px_local(VENT_X, VENT_Z)
    r = VENT_R * 1000.0 * mm_to_px + 6
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    lcx, lcy = cover_px_local(LED_X, LED_Z)
    lr = LED_R * 1000.0 * mm_to_px + 6
    d.ellipse([lcx - lr, lcy - lr, lcx + lr, lcy + lr], fill=0)
    return mask


def crop_cover(im):
    """On yuzun render uzerindeki piksel dikdortgeni."""
    x0 = RES / 2.0 - HALF_X * PPM
    x1 = RES / 2.0 + HALF_X * PPM
    y0 = RES / 2.0 - (HALF_Z - CAM_Z) * PPM
    y1 = RES / 2.0 - (-HALF_Z - CAM_Z) * PPM
    return im.crop((round(x0), round(y0), round(x1), round(y1)))


def patch_mean(im, xy, r=8):
    """Kucuk bir kare pencerenin ortalama RGB degerini verir."""
    x, y = int(xy[0]), int(xy[1])
    box = (max(0, x - r), max(0, y - r),
           min(im.size[0], x + r), min(im.size[1], y + r))
    return ImageStat.Stat(im.crop(box)).mean[:3]


def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ncc(pa, pb):
    """Normalize edilmis korelasyon katsayisi (duz zeminlerde None)."""
    n = len(pa)
    ma = sum(pa) / float(n)
    mb = sum(pb) / float(n)
    va = sum((v - ma) ** 2 for v in pa)
    vb = sum((v - mb) ** 2 for v in pb)
    if va < 1e-6 or vb < 1e-6:
        return None
    cov = sum((pa[i] - ma) * (pb[i] - mb) for i in range(n))
    return cov / ((va * vb) ** 0.5)


def cellwise_ncc(band, shot, mask, nx=8, ny=6, cell=26, inset=0.06,
                 cover_limit=0.25):
    """
    On yuzu hucrelere bolup her hucrede doku-render korelasyonunu olcer.
    inset: pah kirpilmis kenarlari (dis bandi) olcum disinda birakir.
    cover_limit: hucrenin bu oranindan fazlasi 3D parca ile kapliysa atlanir.
    """
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
                row.append(None)          # 3D kubbe / LED bu hucreyi kapliyor
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
    print("[PASS] On yuz etiketi dogru yonde ve sikismasiz (global korelasyon)")

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
    print("[PASS] Tum on yuz bolgeleri dokudan sasmiyor (yerel korelasyon)")

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
        elif kind == "led_red":
            ok = (rr[0] - max(rr[1], rr[2])) > 60 and luminance(rr) > 40
        else:
            ok = False
        note = "  (3D lens atlas alanini kaplar, sapma beklenen)" if kind == "led_red" else ""
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:24s} "
              f"atlas RGB=({ar[0]:5.1f},{ar[1]:5.1f},{ar[2]:5.1f}) "
              f"render RGB=({rr[0]:5.1f},{rr[1]:5.1f},{rr[2]:5.1f}) sapma={d:4.1f}{note}")
        if not ok:
            problems.append(label)

    for label, rect, kind, hi_min in INK_CHECKS:
        box = (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)
        patch = shot_sized.crop(box)
        lums = patch.convert("L").tobytes()
        lo, hi = min(lums), max(lums)
        ok = lo < 110 and hi > hi_min
        info = f"parlaklik {lo}..{hi} (koyu zemin + yazi > {hi_min} bekleniyor)"
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:30s} {info}")
        if not ok:
            problems.append(label)

    if problems:
        raise AssertionError("FAIL: yer isaretleri hatali -> " + ", ".join(problems))
    print("[PASS] Plaka / amber serit / kubbe halkasi / govde zemini dogru konumda (landmark)")
    print("[PASS] Alarm lensi render'da kirmizi yaniyor (3D kaplama)")
    print("[PASS] Baslik ve teknik satirlar render'da okunur durumda (ink)")
    print("[ALL RENDER<->ATLAS CHECKS PASSED]")


if __name__ == "__main__":
    main()


