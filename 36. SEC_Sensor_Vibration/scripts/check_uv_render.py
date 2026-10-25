"""
Render <-> atlas karsilastirmasi (Asset 36 QA).

1) GLOBAL YON: Kapak etiketinin dokuya 1:1 oturdugu, sikismadigi ve MIRROR
   OLMADIGI sayisal olarak dogrulanir (duz / ayna / ters / 180 korelasyonu).
2) YEREL (HUCRE) KORELASYON: Kapak 8x6 hucreye bolunur; her hucrenin doku ile
   korelasyonu olculur. Global ortalama iyi olsa bile tek bir bandin kaymasi
   veya gerilmesi burada yakalanir.
3) YER ISARETLERI (landmark): Marka plakasi, sertifika kutusu, uyari bandi ve
   LED yuvasi render'da BEKLENEN konumda mi? Renk degerleri atlas ile
   karsilastirilir -> doku gercekten geometrinin uzerine dusuyor mu?
4) METIN MUREKKEBI (ink): Baslik ve uyari metni render'da gercekten okunur
   durumda mi (koyu zemin + parlak yazi / kirmizi metin piksel sayisi)?

Cikis kodu 0 -> tum kontroller gecti, 1 -> assert/FAIL.
Render yoksa once scripts/render_qa.py calistirilmalidir.

Calistirma:
    python scripts/check_uv_render.py
"""
import os
from PIL import Image, ImageChops, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
EXPORTS = os.path.join(ASSET, "exports")
QA = os.path.join(ASSET, "qa")

RENDER = os.path.join(QA, "front_flat.png")
ATLAS = os.path.join(EXPORTS, "T_Security_Atlas.png")

COVER_PX = (32, 32, 2016, 1416)          # generate_textures.py ile ayni
RES = 900.0
ORTHO = 0.105                            # m (kamera)
PPM = RES / ORTHO                        # px / m
CAM_Z = -0.004
HALF_X, HALF_Z = 0.0215, 0.0150

# Landmark konumlari (ATLAS pikseli) ve beklenen gorunum
# (etiket, atlas_xy, tip, ornek_yaricapi) - dar seritlerde kucuk yaricap sart,
# aksi halde komsu renklerle karisip sahte sapma uretir.
LANDMARKS = [
    # Bos/koyu plaka alani: spec satirlari (alt 495) ile barkod (ust 540) arasi.
    ("Marka plakasi (koyu)", (1120, 500), "dark", 8),
    ("Sertifika kutusu CE", (1390, 618), "light_box", 8),
    ("Uyari bandi amber", (588, 1346), "amber", 4),
    ("LED lensi (kirmizi)", (401, 1116), "led_red", 8),
    ("LED yuvasi halkasi", (276, 1116), "ring", 6),
    ("Govde zemini", (500, 1200), "body", 6),
]

# Doku uzerinde metin/grafik gorunuyor mu? (kirpilma / bos alan kontrolu)
INK_CHECKS = [
    ("Baslik 'SEC-VS 200'", (192, 172, 900, 280), "bright_on_dark"),
    ("Uyari metni 'TORQUE'", (752, 1278, 1740, 1326), "red_text"),
]


def crop_cover(im):
    """Kapak on yuzunun render uzerindeki piksel dikdortgeni."""
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


def cellwise_ncc(band, shot, nx=8, ny=6, cell=26, inset=0.06):
    """
    Kapagi hucrelere bolup her hucrede doku-render korelasyonunu olcer.
    inset: pah kirpilmis kenarlari (dis bandi) olcum disinda birakir.
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

    variants = {
        "duz (dogru)": shot,
        "yatay ayna": shot.transpose(Image.FLIP_LEFT_RIGHT),
        "dikey ters": shot.transpose(Image.FLIP_TOP_BOTTOM),
        "180 donuk": shot.transpose(Image.ROTATE_180),
    }
    scores = {}
    for name, img in variants.items():
        mad = sum(ImageStat.Stat(ImageChops.difference(img, band)).mean) / 255.0
        scores[name] = mad
        print(f"[QA] {name:14s} ortalama fark: {mad * 100:5.2f}%")

    best = min(scores, key=scores.get)
    ordered = sorted(scores.values())
    print(f"[QA] En iyi eslesme: {best}")
    assert best == "duz (dogru)", f"FAIL: doku yonu hatali (en iyi: {best})"
    assert ordered[0] < 0.12, f"FAIL: render ile atlas uyusmuyor ({ordered[0]*100:.1f}%)"
    assert ordered[1] - ordered[0] > 0.01, "FAIL: yon ayrimi belirsiz"
    print("[PASS] Kapak etiketi dogru yonde ve sikismasiz (global korelasyon)")

    # ------------------------------------------------------------ 2) Hucre korelasyonu
    rows = cellwise_ncc(band, shot)
    flat = [r for row in rows for r in row if r is not None]
    skipped = sum(1 for row in rows for r in row if r is None)
    worst = min(flat)
    worst_pos = [(i, j) for j, row in enumerate(rows)
                 for i, r in enumerate(row) if r is not None and r == worst][0]
    good = sum(1 for r in flat if r >= 0.60)
    print(f"[QA] Hucre korelasyonu: olculen {len(flat)} / atlanan {skipped} (duz zemin) | "
          f"en dusuk r={worst:.2f} @ kolon {worst_pos[0]}, satir {worst_pos[1]}")
    print(f"[QA] r>=0.60 hucre orani: {100.0 * good / len(flat):.1f}%")
    for row in rows:
        print("     " + " ".join("  --" if r is None else f"{r:+.2f}" for r in row))
    assert worst >= 0.35, f"FAIL: yerel doku kaymasi (en dusuk hucre korelasyonu {worst:.2f})"
    assert good / len(flat) >= 0.85, "FAIL: hucrelerin %15'inden fazlasi dokudan sapiyor"
    print("[PASS] Tum kapak bolgeleri dokudan sasmiyor (yerel korelasyon)")

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
        elif kind == "light_box":
            ok = luminance(rr) > 175 and d <= 70
        elif kind == "amber":
            ok = rr[0] > 200 and rr[1] > 140 and rr[2] < 90 and d <= 40
        elif kind == "led_red":
            ok = (rr[0] - max(rr[1], rr[2])) > 80 and luminance(rr) > 55
        elif kind == "ring":
            ok = (luminance(rr) > 165 and max(rr) - min(rr) < 45)
        else:  # body
            ok = luminance(rr) > 175 and d <= 60
        note = ("  (3D lens meshi atlas cukurini kaplar, sapma beklenen)"
                if kind == "led_red" else "")
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:22s} "
              f"atlas RGB=({ar[0]:5.1f},{ar[1]:5.1f},{ar[2]:5.1f}) "
              f"render RGB=({rr[0]:5.1f},{rr[1]:5.1f},{rr[2]:5.1f}) sapma={d:4.1f}{note}")
        if not ok:
            problems.append(label)

    for label, rect, kind in INK_CHECKS:
        box = (rect[0] - ox, rect[1] - oy, rect[2] - ox, rect[3] - oy)
        patch = shot_sized.crop(box)
        lums = patch.convert("L").tobytes()
        lo, hi = min(lums), max(lums)
        if kind == "bright_on_dark":
            ok = lo < 110 and hi > 195
            info = f"parlaklik {lo}..{hi} (koyu zemin + beyaz yazi bekleniyor)"
        else:
            rgb = patch.tobytes()
            reds = sum(1 for k in range(0, len(rgb), 3)
                       if rgb[k] > 150 and rgb[k + 1] < 110 and rgb[k + 2] < 110)
            ok = reds > 300
            info = f"kirmizi metin pikseli {reds} (>300 bekleniyor)"
        print(f"[QA] {'OK  ' if ok else 'HATA'} {label:24s} {info}")
        if not ok:
            problems.append(label)

    if problems:
        raise AssertionError("FAIL: yer isaretleri hatali -> " + ", ".join(problems))
    print("[PASS] Plaka / sertifika / uyari bandi / LED yuvasi dogru konumda (landmark)")
    print("[PASS] Baslik ve uyari metinleri render'da okunur durumda (ink)")
    print("[ALL RENDER<->ATLAS CHECKS PASSED]")


if __name__ == "__main__":
    main()
