"""
Render <-> atlas karsilastirmasi (Asset 41 QA).

1) GLOBAL YON: on yuz etiketinin dokuya 1:1 oturdugu, sikismadigi ve MIRROR
   OLMADIGI sayisal olarak dogrulanir.
2) YEREL (HUCRE) KORELASYON: 8x6 hucre; ekran/lens/izgara/dugme `covered_mask()`
   ile olcum disinda birakilir.
3) YER ISARETLERI: govde zemini + dugme/lens/ekran yuvalari dokuyla; ekran,
   izgara ve dugme varlik olarak (3D mesh kaplar).
4) METIN MUREKKEBI: baslik, "PUSH TO CALL", seri no satiri.
5) BASMA KANITI: `qa/button_rest.png` / `qa/button_pressed.png` farkli olmali.

Cikis kodu 0 -> tum kontroller gecti.
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

COVER_PX = (32, 32, 1032, 1907)          # generate_textures.py ile ayni
RES = 900.0
ORTHO = 0.175                            # m (render_qa.py ile ayni)
PPM = RES / ORTHO
HALF_X, HALF_Z = 0.0400, 0.0750          # 80 x 150 mm on yuz

# 3D parcalarin yuzde kapladigi alan
SCREEN_X, SCREEN_Z, SCREEN_HX, SCREEN_HZ = 0.0, 0.0400, 0.0320, 0.0150
LENS_X, LENS_Z, LENS_R = -0.0260, 0.0640, 0.0070
GRILLE_X, GRILLE_Z, GRILLE_R = 0.0, 0.0020, 0.0170
BTN_X, BTN_Z, BTN_R = 0.0, -0.0340, 0.0130
BEZEL_R_OUT = 0.0162                     # 3D dugme bilezigi (Button_Bezel)

LANDMARKS = [
    # (etiket, atlas_xy, tip, ornek_yaricapi)
    ("Govde zemini", (500, 150), "body", 6),
    ("Dugme yuvasi (koyu)", (704, 1394), "dark", 5),
    ("Lens yuvasi halkasi", (762, 170), "dark", 5),
    ("Ekran yuvasi (koyu)", (122, 469), "dark", 4),
    # 3D kaplanan bolgeler: varlik kontrolu
    ("Ekran (LCD)", (532, 469), "screen", 10),
    ("Izgara (perfore)", (532, 944), "grille", 8),
    # Dugme merkezi beyaz zil ikonudur; yesil halka ~0.7 yaricapta okunur.
    ("Dugme (yesil)", (646, 1394), "led_green", 6),
]

INK_CHECKS = [
    ("Baslik 'SEC-VI 240'", (84, 74, 500, 120), "dark_on_light", 60),
    ("'PUSH TO CALL'", (300, 1616, 770, 1655), "dark_on_light", 70),
    ("Seri no 'SN 41-VI'", (84, 1828, 400, 1860), "dark_on_light", 120),
]


def cover_px_local(x_m, z_m):
    bw = COVER_PX[2] - COVER_PX[0]
    bh = COVER_PX[3] - COVER_PX[1]
    nx = (x_m + HALF_X) / (2.0 * HALF_X)
    nz = (z_m + HALF_Z) / (2.0 * HALF_Z)
    return (bw - nx * bw, bh - nz * bh)


def covered_mask(size):
    """Ekran/lens/izgara/dugme tarafindan kapatilan bolgeler 0, serbest 255."""
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    mm_to_px = (COVER_PX[2] - COVER_PX[0]) / (HALF_X * 2.0 * 1000.0)
    cx, cy = cover_px_local(SCREEN_X, SCREEN_Z)
    # Sadece 3D parcanin kapladigi alan + anti-aliasing payi maskelenir; genis
    # maske gereksiz yere hucre atar ve QA kapsamini dusurur.
    hw = SCREEN_HX * 1000.0 * mm_to_px + 6
    hh = SCREEN_HZ * 1000.0 * mm_to_px + 6
    d.rectangle([cx - hw, cy - hh, cx + hw, cy + hh], fill=0)
    for (px, pz, r, pad) in ((LENS_X, LENS_Z, LENS_R, 6),
                             (GRILLE_X, GRILLE_Z, GRILLE_R, 6),
                             (BTN_X, BTN_Z, BEZEL_R_OUT, 16)):
        c, cyy = cover_px_local(px, pz)
        rr = r * 1000.0 * mm_to_px + pad
        d.ellipse([c - rr, cyy - rr, c + rr, cyy + rr], fill=0)
    return mask


def crop_cover(im):
    """On yuzun render uzerindeki dikdortgeni (merkezli)."""
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
                row.append(None)
                continue
            a = list(band.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            b = list(shot.crop(box).resize((cell, cell), Image.LANCZOS).tobytes())
            row.append(ncc(a, b))
        rows.append(row)
    return rows


def check_press_renders():
    """Basma kaniti: dinlenme ve basili render'lar gercekten farkli olmali."""
    rest = os.path.join(QA, "button_rest.png")
    pressed = os.path.join(QA, "button_pressed.png")
    missing = [p for p in (rest, pressed) if not os.path.exists(p)]
    assert not missing, f"FAIL: dugme render eksik -> {missing} (render_qa.py calistir)"
    a = Image.open(rest).convert("L")
    b = Image.open(pressed).convert("L")
    assert a.size == b.size, "FAIL: dugme render boyutlari farkli"
    mad = ImageStat.Stat(ImageChops.difference(a, b)).mean[0] / 255.0
    print(f"[QA] dugme dinlenme vs basili ortalama fark: {mad * 100:.2f}%")
    # Tum kare ortalamasi dugmenin kucuklugunden dolayi zayif bir sinyaldir;
    # asil kanit FARKLILASAN PIKSELLERIN SAYISI ve buyuklugudur.
    import numpy as np
    da = np.abs(np.asarray(a, dtype=np.int16) - np.asarray(b, dtype=np.int16))
    changed = int((da > 8).sum())
    peak = int(da.max())
    print(f"[QA] farklilasan piksel: {changed} (esik >8), en buyuk fark: {peak}/255")
    assert peak >= 40, f"FAIL: basma farki cok zayif (en buyuk fark {peak}/255)"
    assert changed >= 200, \
        f"FAIL: sadece {changed} piksel degisti - basma uygulanmamis olabilir"
    print("[PASS] Button_Pivot 3 mm basma hareketi render'larda dogrulandi")


def check_button_concentric():
    """Flat render'da dugme (yesil) ile bilezik (koyu) es merkezli mi?

    Bildirilen "kayma" hatasinin dogrudan koruma testi: dokuya cizilen halka
    ile 3D dugme ayni merkezde olmali. Bilezik 3D oldugu icin artik dugmeyle
    birlikte hareket eder; bu kontrol merkez kaymasini yakalar.
    """
    import numpy as np

    im = Image.open(RENDER).convert("RGB")
    arr = np.asarray(im).astype(np.int16)
    r_, g_, b_ = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = 0.2126 * r_ + 0.7152 * g_ + 0.0722 * b_

    cx = RES / 2.0
    cy = RES / 2.0 - BTN_Z * PPM
    win = int(BEZEL_R_OUT * PPM + 24)

    green = (g_ - np.maximum(r_, b_) > 30) & (g_ > 70)
    # Bilezik yuzeyi atlas "DARK" tonunu (30,36,44 -> lum ~35) kullanir; cep
    # (8,10,14 -> 10) ve "PUSH TO CALL" metni (18,22,28 -> 21) bu bant disinda
    # kalir. Boylece centroid'e komsu karanlik ogeler karismaz.
    bezel = (lum > 26) & (lum < 55)

    yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
    rad = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    near = rad <= (BEZEL_R_OUT * PPM + 3.0)
    bezel = bezel & near

    def centroid(mask):
        x0, y0 = int(cx - win), int(cy - win)
        x1, y1 = int(cx + win), int(cy + win)
        sub = mask[max(0, y0):y1, max(0, x0):x1]
        ys, xs = np.nonzero(sub)
        if len(xs) < 50:
            return None
        return (x0 + xs.mean(), y0 + ys.mean(), len(xs))

    gc = centroid(green)
    dc = centroid(bezel)
    assert gc is not None, "FAIL: dugme (yesil) flat render'da bulunamadi"
    assert dc is not None, "FAIL: dugme bilezigi (koyu) flat render'da bulunamadi"
    dx = gc[0] - dc[0]
    dy = gc[1] - dc[1]
    print(f"[QA] dugme merkezi=({gc[0]:.1f},{gc[1]:.1f}) n={gc[2]} | "
          f"bilezik merkezi=({dc[0]:.1f},{dc[1]:.1f}) n={dc[2]}")
    print(f"[QA] dugme-bilezik merkez sapmasi: ({dx:+.2f}, {dy:+.2f}) px "
          f"= ({dx * 1000.0 / PPM:+.2f}, {dy * 1000.0 / PPM:+.2f}) mm")
    assert abs(dx) < 1.5 and abs(dy) < 1.5, \
        (f"FAIL: dugme bilezik icinde kaymis ({(dx*dx+dy*dy)**0.5:.2f} px) - "
         f"dugme yuvasindan kaymis gorunur")
    print("[PASS] Dugme ve 3D bilezik es merkezli (kayma yok)")


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
    print("[PASS] Interkom paneli etiketi dogru yonde ve sikismasiz")

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
    print("[PASS] Tum panel bolgeleri dokudan sasmiyor (yerel korelasyon)")

    # ------------------------------------------------------------ 3) Yer isaretleri
    shot_sized = shot_rgb.resize(band.size, Image.LANCZOS)
    ox, oy = COVER_PX[0], COVER_PX[1]
    problems = []
    for label, xy, kind, radius in LANDMARKS:
        local = (xy[0] - ox, xy[1] - oy)
        ar = patch_mean(band_rgb, local, r=radius)
        rr = patch_mean(shot_sized, local, r=radius)
        d = max(abs(ar[i] - rr[i]) for i in range(3))
        if kind == "body":
            ok = luminance(rr) > 175 and d <= 60
        elif kind == "dark":
            ok = luminance(rr) < 95 and d <= 80
        elif kind == "screen":
            ok = luminance(rr) < 110 and rr[1] > rr[0] and rr[1] > rr[2] - 10
        elif kind == "grille":
            ok = luminance(rr) < 110
        elif kind == "led_green":
            ok = (rr[1] - max(rr[0], rr[2])) > 30 and luminance(rr) > 70
        else:
            ok = False
        note = ""
        if kind in ("screen", "grille", "led_green"):
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
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:24s} {info}")
        if not ok:
            problems.append(label)

    if problems:
        raise AssertionError("FAIL: yer isaretleri hatali -> " + ", ".join(problems))
    print("[PASS] Govde zemini + dugme/lens/ekran yuvalari dogru konumda")
    print("[PASS] Ekran / izgara / dugme render'da dogru (3D kaplama)")
    print("[PASS] Baslik / 'PUSH TO CALL' / seri no satiri okunur (ink)")

    # ------------------------------------------------------------ 4) Basma kaniti
    check_press_renders()
    check_button_concentric()

    print("[ALL RENDER<->ATLAS CHECKS PASSED]")


if __name__ == "__main__":
    main()


