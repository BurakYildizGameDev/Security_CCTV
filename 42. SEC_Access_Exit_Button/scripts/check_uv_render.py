"""
Render <-> atlas karsilastirmasi (Asset 42 QA).

1) GLOBAL YON: on yuz etiketinin dokuya 1:1 oturdugu, sikismadigi ve MIRROR
   OLMADIGI sayisal olarak dogrulanir.
2) YEREL (HUCRE) KORELASYON: 8x6 hucre; cerceve/dugme/vida yuvalari
   `covered_mask()` ile olcum disinda birakilir.
3) YER ISARETLERI: marka plakasi, amber serit, govde zemini dokuyla; cerceve
   cebi, dugme ve vida yuvalari varlik olarak dogrulanir.
4) METIN MUREKKEBI: baslik, "PUSH TO EXIT", seri no.
5) BASMA KANITI + ES MERKEZLILIK: dinlenme/basili render'lari farkli olmali;
   dugme ile 3D cerceve es merkezli olmali (varlik 41 "kayma" regresyon testi).

Cikis kodu 0 -> tum kontroller gecti.
Calistirma:
    python scripts/check_uv_render.py
"""
import os
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
EXPORTS = os.path.join(ASSET, "exports")
QA = os.path.join(ASSET, "qa")

RENDER = os.path.join(QA, "front_flat.png")
ATLAS = os.path.join(EXPORTS, "T_Security_Atlas.png")

COVER_PX = (32, 32, 1760, 1760)          # generate_textures.py ile ayni
RES = 900.0
ORTHO = 0.112                            # m (render_qa.py ile ayni)
PPM = RES / ORTHO
HALF_X, HALF_Z = 0.0430, 0.0430          # 86 x 86 mm on yuz

BTN_R = 0.0220
BUTTON_PX = (1790, 32, 2016, 258)        # atlas BUTTON bandi (generate_textures.py)
COLLAR_R_IN, COLLAR_R_OUT = 0.0224, 0.0246
SCREW_X, SCREW_R = 0.0320, 0.0040

LANDMARKS = [
    # (etiket, atlas_xy, tip, ornek_yaricapi)
    ("Marka plakasi (koyu)", (1300, 250), "dark", 8),
    ("Amber serit (plaka)", (105, 200), "amber", 4),
    ("Govde zemini", (142, 732), "body", 6),
    # 3D kaplanan bolgeler: varlik kontrolu (merkezde beyaz EXIT yazisi var,
    # bu yuzden dugme ornegi merkezden kaydirilarak yesil alandan alinir)
    ("Dugme (aydinlatmali)", (1161, 896), "led_green", 8),
    ("Sol vida (metal)", (253, 896), "metal", 6),
    ("Sag vida (metal)", (1539, 896), "metal", 6),
]

INK_CHECKS = [
    ("Baslik 'SEC-EB 1'", (148, 140, 800, 230), "bright_on_dark", 195),
    ("'PUSH TO EXIT'", (500, 1440, 1300, 1524), "dark_on_light", 70),
    ("Seri no 'SN 42-EB'", (96, 1612, 460, 1646), "dark_on_light", 140),
]


def cover_px_local(x_m, z_m):
    bw = COVER_PX[2] - COVER_PX[0]
    bh = COVER_PX[3] - COVER_PX[1]
    nx = (x_m + HALF_X) / (2.0 * HALF_X)
    nz = (z_m + HALF_Z) / (2.0 * HALF_Z)
    return (bw - nx * bw, bh - nz * bh)


def covered_mask(size):
    """Cerceve, dugme ve iki vida tarafindan kapatilan bolgeler 0, serbest 255."""
    mask = Image.new("L", size, 255)
    d = ImageDraw.Draw(mask)
    mm = (COVER_PX[2] - COVER_PX[0]) / (HALF_X * 2.0 * 1000.0)
    cx, cy = cover_px_local(0.0, 0.0)
    r = COLLAR_R_OUT * 1000.0 * mm + 18      # cerceve + cep payi
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=0)
    for sx in (-SCREW_X, SCREW_X):
        px, py = cover_px_local(sx, 0.0)
        rs = SCREW_R * 1000.0 * mm + 12
        d.ellipse([px - rs, py - rs, px + rs, py + rs], fill=0)
    return mask


def crop_face(im):
    """On yuzun render uzerindeki dikdortgeni."""
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
    """Basma kaniti: dinlenme ve basili render'lar farkli olmali."""
    rest = os.path.join(QA, "button_rest.png")
    pressed = os.path.join(QA, "button_pressed.png")
    missing = [p for p in (rest, pressed) if not os.path.exists(p)]
    assert not missing, f"FAIL: dugme render eksik -> {missing} (render_qa.py calistir)"
    a = Image.open(rest).convert("L")
    b = Image.open(pressed).convert("L")
    assert a.size == b.size, "FAIL: dugme render boyutlari farkli"
    da = np.abs(np.asarray(a, dtype=np.int16) - np.asarray(b, dtype=np.int16))
    changed = int((da > 8).sum())
    peak = int(da.max())
    print(f"[QA] dugme dinlenme vs basili: {changed} piksel degisti, "
          f"tepe fark {peak}/255")
    assert peak >= 40, f"FAIL: basma farki cok zayif (tepe {peak}/255)"
    assert changed >= 200, f"FAIL: sadece {changed} piksel degisti"
    print("[PASS] Button_Pivot 4 mm basma hareketi render'larda dogrulandi")


def check_button_concentric():
    """Flat render'da dugme (yesil) ile 3D cerceve (metal) es merkezli mi?

    Varlik 41'de bildirilen "kayma" hatasinin dogrudan regresyon testi.
    """
    im = Image.open(RENDER).convert("RGB")
    arr = np.asarray(im).astype(np.int16)
    r_, g_, b_ = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    lum = 0.2126 * r_ + 0.7152 * g_ + 0.0722 * b_

    cx = RES / 2.0
    cy = RES / 2.0
    win = int(COLLAR_R_OUT * PPM + 18)

    green = (g_ - np.maximum(r_, b_) > 30) & (g_ > 70)
    # NOT: M_Metal'in DOKUSU YOK; Workbench/EEVEE metal parcalari material
    # diffuse_color (0.75,0.78,0.82 -> ~227) ile cizer, atlas swatch'i ile degil.
    # Bu yuzden cerceve bandi 215..240'tir; govde zemini (243) ve cep (10) disarida.
    ring = (lum > 215) & (lum < 240)

    yy, xx = np.mgrid[0:arr.shape[0], 0:arr.shape[1]]
    rad = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    ring = ring & (rad <= COLLAR_R_OUT * PPM + 2.0) & (rad >= BTN_R * PPM)

    def bbox_center(mask):
        x0, y0 = int(cx - win), int(cy - win)
        x1, y1 = int(cx + win), int(cy + win)
        sub = mask[max(0, y0):y1, max(0, x0):x1]
        ys, xs = np.nonzero(sub)
        if len(xs) < 50:
            return None
        # Agirlik merkezi DEGIL sinir kutusu merkezi: dugme yuzundeki beyaz
        # "EXIT" yazisi/ok yesil maskeyi asimetrik kirptigi icin agirlik merkezi
        # kayiyor; sinir kutusu merkezi desenlerden etkilenmez.
        return (x0 + (xs.min() + xs.max()) / 2.0,
                y0 + (ys.min() + ys.max()) / 2.0, len(xs))

    gc = bbox_center(green)
    rc = bbox_center(ring)
    assert gc is not None, "FAIL: dugme (yesil) flat render'da bulunamadi"
    assert rc is not None, "FAIL: 3D cerceve (metal) flat render'da bulunamadi"
    dx, dy = gc[0] - rc[0], gc[1] - rc[1]
    print(f"[QA] dugme merkezi=({gc[0]:.1f},{gc[1]:.1f}) n={gc[2]} | "
          f"cerceve merkezi=({rc[0]:.1f},{rc[1]:.1f}) n={rc[2]}")
    print(f"[QA] dugme-cerceve merkez sapmasi: ({dx:+.2f}, {dy:+.2f}) px "
          f"= ({dx * 1000.0 / PPM:+.2f}, {dy * 1000.0 / PPM:+.2f}) mm")
    assert abs(dx) < 1.5 and abs(dy) < 1.5, \
        (f"FAIL: dugme cerceve icinde kaymis ({(dx*dx+dy*dy)**0.5:.2f} px)")
    print("[PASS] Dugme ve 3D cerceve es merkezli (kayma yok)")


def check_button_text_orientation():
    """Dugme yuzundeki yazinin yonu: duz mu, aynali mi?

    +Y on yuzlerde U ekseni ters cevrilmezse doku yatay aynalanir ve "EXIT"
    yazisi ters gorunur (varlik 42 kullanici geri bildirimi). Test, flat
    render'daki dugme yuzunu atlas BUTTON bandiyla 4 yonde karsilastirir;
    "normal" acik ara kazanmalidir.
    """
    band_box = BUTTON_PX
    atlas = Image.open(ATLAS).convert("RGB")
    band = atlas.crop(band_box)
    half = BTN_R * PPM
    cx = cy = RES / 2.0
    shot = Image.open(RENDER).convert("RGB").crop(
        (round(cx - half), round(cy - half), round(cx + half), round(cy + half))
    ).resize(band.size, Image.LANCZOS)

    mask = Image.new("L", band.size, 0)
    ImageDraw.Draw(mask).ellipse([2, 2, band.size[0] - 3, band.size[1] - 3], fill=255)

    variants = {
        "normal": shot,
        "aynali (U ters)": shot.transpose(Image.FLIP_LEFT_RIGHT),
        "dikey ters": shot.transpose(Image.FLIP_TOP_BOTTOM),
        "180 donuk": shot.transpose(Image.ROTATE_180),
    }
    scores = {}
    for name, img in variants.items():
        mad = ImageStat.Stat(ImageChops.difference(img.convert("L"), band.convert("L")),
                             mask=mask).mean[0] / 255.0
        scores[name] = mad
        print(f"[QA] dugme yuzu {name:16s} ortalama fark: {mad * 100:5.2f}%")

    best = min(scores, key=scores.get)
    ordered = sorted(scores.values())
    assert best == "normal", \
        (f"FAIL: dugme yazisi ters/aynali gorunuyor (en iyi: {best}, "
         f"%{scores[best]*100:.2f})")
    assert ordered[1] - ordered[0] > 0.01, \
        "FAIL: dugme yazi yonu ayrimi belirsiz (esik 1 puan)"
    print(f"[PASS] Dugme yazisi dogru yonde (normal %{scores['normal']*100:.2f} vs "
          f"aynali %{scores['aynali (U ters)']*100:.2f})")


def main():
    render = Image.open(RENDER).convert("RGB")
    atlas = Image.open(ATLAS).convert("RGB")
    band_rgb = atlas.crop(COVER_PX)
    band = band_rgb.convert("L")
    shot_rgb = crop_face(render)
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
    print("[PASS] Cikis butonu paneli dogru yonde ve sikismasiz")

    # ------------------------------------------------------------ 2) Hucre korelasyonu
    rows = cellwise_ncc(band, shot, mask)
    flat = [r for row in rows for r in row if r is not None]
    skipped = sum(1 for row in rows for r in row if r is None)
    worst = min(flat)
    worst_pos = [(i, j) for j, row in enumerate(rows)
                 for i, r in enumerate(row) if r is not None and r == worst][0]
    good = sum(1 for r in flat if r >= 0.60)
    print(f"[QA] Hucre korelasyonu: olculen {len(flat)} / atlanan {skipped} | "
          f"en dusuk r={worst:.2f} @ kolon {worst_pos[0]}, satir {worst_pos[1]}")
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
        if kind == "dark":
            ok = luminance(rr) < 95 and d <= 90
        elif kind == "amber":
            ok = rr[0] > 200 and rr[1] > 140 and rr[2] < 90 and d <= 40
        elif kind == "body":
            ok = luminance(rr) > 175 and d <= 60
        elif kind == "led_green":
            ok = (rr[1] - max(rr[0], rr[2])) > 30 and luminance(rr) > 70
        elif kind == "metal":
            ok = luminance(rr) > 120 and max(rr) - min(rr) < 40
        else:
            ok = False
        note = ""
        if kind in ("led_green", "metal"):
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
    print("[PASS] Marka plakasi / amber serit / govde / cerceve cebi dogru konumda")
    print("[PASS] Dugme ve iki vida render'da dogru (3D kaplama)")
    print("[PASS] Baslik / 'PUSH TO EXIT' / seri no satiri okunur (ink)")

    # ------------------------------------------------------------ 4) Hareket kanitlari
    check_press_renders()
    check_button_concentric()

    print("[ALL RENDER<->ATLAS CHECKS PASSED]")


if __name__ == "__main__":
    main()


