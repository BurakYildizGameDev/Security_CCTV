"""42 dugme yuzu yon teshisi: atlas BUTTON bandi ile duz/aynali karsilastirma."""
import os
import numpy as np
from PIL import Image, ImageChops, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
ASSET = os.path.dirname(HERE)
QA = os.path.join(ASSET, "qa")
EXPORTS = os.path.join(ASSET, "exports")

RES, ORTHO = 900.0, 0.112
PPM = RES / ORTHO
BTN_R = 0.0220
BAND = (1790, 32, 2016, 258)

render = Image.open(os.path.join(QA, "front_flat.png")).convert("RGB")
atlas = Image.open(os.path.join(EXPORTS, "T_Security_Atlas.png")).convert("RGB")
band = atlas.crop(BAND)

# Dugme yuzu: merkez + BTN_R yaricapinda kare kirpma
half = BTN_R * PPM
cx = cy = RES / 2.0
box = (round(cx - half), round(cy - half), round(cx + half), round(cy + half))
shot = render.crop(box).resize(band.size, Image.LANCZOS)

# Daire maskesi (kare koselerini ele)
mask = Image.new("L", band.size, 0)
from PIL import ImageDraw
d = ImageDraw.Draw(mask)
d.ellipse([2, 2, band.size[0] - 3, band.size[1] - 3], fill=255)

variants = {
    "normal": shot,
    "aynali": shot.transpose(Image.FLIP_LEFT_RIGHT),
    "dikey ters": shot.transpose(Image.FLIP_TOP_BOTTOM),
    "180": shot.transpose(Image.ROTATE_180),
}
print("dugme yuzu <-> atlas BUTTON bandi:")
results = {}
for name, img in variants.items():
    g = img.convert("L")
    b = band.convert("L")
    mad = ImageStat.Stat(ImageChops.difference(g, b), mask=mask).mean[0] / 255.0
    results[name] = mad
    print(f"  {name:12s} ortalama fark: {mad * 100:6.2f}%")

best = min(results, key=results.get)
print(f"\nEn iyi eslesme: {best}")
print("YORUM:", "YAZI TERSTEN COK AYNALI (U ekseni)" if best == "aynali"
      else ("YAZI 180 DONUK" if best == "180" else
            ("YAZI DIKEY TERS" if best == "dikey ters" else "YON DOGRU")))
