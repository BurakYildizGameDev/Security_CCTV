"""
Render <-> atlas karsilastirmasi (Asset 39 QA).

1) GLOBAL YON: On yuz etiketinin dokuya 1:1 oturdugu, sikismadigi ve MIRROR
   OLMADIGI sayisal olarak dogrulanir (duz / ayna / ters / 180 korelasyonu).
2) YEREL (HUCRE) KORELASYON: On yuz 8x6 hucreye bolunur; iki optik pencere ve
   LED yuvasi `covered_mask()` ile olcum disinda birakilir.
3) YER ISARETLERI: Marka plakasi, amber serit, pencere halkasi, govde zemini
   dokuyla; cam ici ve LED ise varlik olarak (3D mesh kaplar) dogrulanir.
4) METIN MUREKKEBI: Baslik, teknik satir ve kirmizi uyari render'da okunur mu?
5) HAREKETLI PARCA: `qa/tilt_minus10.png` ve `qa/tilt_plus10.png` mevcut ve
   hero render'dan farkli olmali (Aim_Pivot gercekten donuyor).

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

COVER_PX = (32, 32, 882, 2016)           # generate_textures.py ile ayni
RES = 900.0
ORTHO = 0.105                            # m (kamera)
PPM = RES / ORTHO                        # px / m
CAM_Z = 0.0
HALF_X, HALF_Z = 0.0180, 0.0420

# 3D parcalarin on yuzde kapladigi alan (generate_SEC_Beam_Detector_Dual.py ile ayni)
WINDOW_X, WINDOW_Z, WINDOW_R = 0.0, 0.0240, 0.0070
LED_X, LED_Z, LED_R = -0.0115, 0.0100, 0.0025

# (etiket, atlas_xy, tip, ornek_yaricapi)
LANDMARKS = [
    # Marka plakasinin bos koyu alani: alt yazi (x<=660) ile IP66 (x>=756) arasi
    ("Marka plakasi (koyu)", (710, 220), "dark", 6),
    ("Amber serit (plaka)", (84, 160), "amber", 3),
    ("Pencere gomme halkasi", (457, 282), "soft", 4),
    ("Govde zemini", (790, 400), "body", 6),
    # 3D kaplanan bolgeler: atlas karsilastirmasi degil, varlik kontrolu
    ("Ust pencere cami", (457, 457), "glass_dark", 10),
    ("Alt pencere cami", (457, 1590), "glass_dark", 10),
    # Lens merkezi beyaz cekirdek; yesil halka ~0.7 yaricapta okunur.
    ("Durum lensi (yesil)", (767, 788), "led_green", 4),
]

# (etiket, atlas_rect, tip, parlak_ust_esik)
INK_CHECKS = [
    ("Baslik 'SEC-BD 220'", (120, 108, 559, 165), "bright_on_dark", 195),
    ("Teknik satir 'RANGE 0 - 60 m'", (112, 752, 350, 771), "bright_on_dark", 170),
    ("Uyari 'DO NOT OBSTRUCT'", (162, 1820, 494, 1845), "red_text", 0),
]


def cover_px_local(x_m, z_m):
    """On yuz (X, Z) konumunu COVER bantinin yerel pikseline cevirir (flip_u)."""
    bw = COVER_PX[2] - COVER_PX[0]
    bh = COVER_PX[3] - COVER_PX[1]
    nx = (x_m + HALF_X) / (2.0 * HALF_X)
    nz = (z_m + HALF_Z) / (2.0 * HALF_Z)
    return (bw - nx * bw, bh - nz * bh)


def covered_mask(size):
    """3D pencere camlari ve LED tarafindan kapatilan bolgeler 0, serbest 255."""
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    mm_to_px = (COVER_PX[2] - COVER_PX[0]) / (HALF_X * 2.0 * 1000.0)
    for sz in (WINDOW_Z, -WINDOW_Z):
        cx, cy = cover_px_local(WINDOW_X, sz)
        r = WINDOW_R * 1000.0 * mm_to_px + 6
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    lcx, lcy = cover_px_local(LED_X, LED_Z)
    # 3D lens + parlamasi + cizilen oturma halkasi birlikte maskelenir; aksi halde
    # lensin isigi hucre ortalamasini yukseltip yanlis "doku kaymasi" uretiyor.
    lr = (LED_R * 1000.0 + 1.0) * mm_to_px
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


def cellwise_ncc(band, shot, mask, nx=8, ny=6, cell=26, inset=0.06,
                 cover_limit=0.25):
    """On yuzu hucrelere bolup her hucrede doku-render korelasyonunu olcer."""
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
                row.append(None)          # 3D cam / LED bu hucreyi kapliyor
                continue
            a = list(band.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            b = list(shot.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            row.append(ncc(a, b))
        rows.append(row)
    return rows


def check_tilt_renders():
    """Hareketli parca: iki limit ucundaki render'lar mevcut ve gercekten farkli mi?"""
    paths = [os.path.join(QA, "tilt_minus10.png"), os.path.join(QA, "tilt_plus10.png")]
    missing = [p for p in paths if not os.path.exists(p)]
    assert not missing, f"FAIL: tilt render eksik -> {missing} (render_qa.py calistir)"
    a = Image.open(paths[0]).convert("L")
    b = Image.open(paths[1]).convert("L")
    assert a.size == b.size, "FAIL: tilt render boyutlari farkli"
    mad = ImageStat.Stat(ImageChops.difference(a, b)).mean[0] / 255.0
    print(f"[QA] tilt -10 vs +10 ortalama fark: {mad * 100:.2f}%")
    assert mad > 0.02, (f"FAIL: -10 ve +10 derece render'lari neredeyse ayni "
                        f"({mad * 100:.2f}%) - Aim_Pivot donmuyor olabilir")
    hero = Image.open(os.path.join(QA, "hero_34.png")).convert("L")
    mad_h = ImageStat.Stat(ImageChops.difference(hero, a)).mean[0] / 255.0
    print(f"[QA] hero vs tilt(-10) ortalama fark: {mad_h * 100:.2f}%")
    assert mad_h > 0.02, "FAIL: tilt render hero'dan farksiz - pivot uygulanmamis"
    print("[PASS] Aim_Pivot her iki limit ucunda da gercekten donuyor (render farki)")


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
        elif kind == "soft":
            ok = 35 < luminance(rr) < 110 and max(rr) - min(rr) < 45
        elif kind == "glass_dark":
            # Gomme cam: koyu IR filtre, atlastan cok daha karanlik
            ok = luminance(rr) < 95
        elif kind == "led_green":
            ok = (rr[1] - max(rr[0], rr[2])) > 30 and luminance(rr) > 70
        else:
            ok = False
        note = ""
        if kind in ("glass_dark", "led_green"):
            note = "  (3D mesh atlas alanini kaplar, sapma beklenen)"
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:24s} "
              f"atlas RGB=({ar[0]:5.1f},{ar[1]:5.1f},{ar[2]:5.1f}) "
              f"render RGB=({rr[0]:5.1f},{rr[1]:5.1f},{rr[2]:5.1f}) sapma={d:4.1f}{note}")
        if not ok:
            problems.append(label)

    for label, rect, kind, hi_min in INK_CHECKS:
        box = (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)
        patch = shot_sized.crop(box)
        if kind == "red_text":
            rgb = patch.tobytes()
            reds = sum(1 for k in range(0, len(rgb), 3)
                       if rgb[k] > 150 and rgb[k + 1] < 110 and rgb[k + 2] < 110)
            ok = reds > 250
            info = f"kirmizi metin pikseli {reds} (>250 bekleniyor)"
        else:
            lums = patch.convert("L").tobytes()
            lo, hi = min(lums), max(lums)
            ok = lo < 110 and hi > hi_min
            info = f"parlaklik {lo}..{hi} (koyu zemin + yazi > {hi_min} bekleniyor)"
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:30s} {info}")
        if not ok:
            problems.append(label)

    if problems:
        raise AssertionError("FAIL: yer isaretleri hatali -> " + ", ".join(problems))
    print("[PASS] Plaka / amber serit / pencere halkasi / govde zemini dogru konumda")
    print("[PASS] Iki cam ve durum lensi render'da dogru (3D kaplama)")
    print("[PASS] Baslik / teknik satir / kirmizi uyari metni okunur durumda (ink)")

    # ------------------------------------------------------------ 4) Hareketli parca
    check_tilt_renders()

    print("[ALL RENDER<->ATLAS CHECKS PASSED]")


if __name__ == "__main__":
    main()


