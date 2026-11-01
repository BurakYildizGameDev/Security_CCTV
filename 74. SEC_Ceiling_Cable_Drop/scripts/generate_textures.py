import os
import math
import numpy as np
from PIL import Image, ImageDraw

def create_ceiling_cable_drop_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(7474)

    # 1. Base image array (RGBA, 100% solid opaque)
    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)

    # -------------------------------------------------------------
    # REGION 0: Base Satin Galvanized Steel (0..1024, 0..1024)
    # Used for Ceiling_Rosette and Drop_Pipe body
    # -------------------------------------------------------------
    steel_base = np.array([215, 220, 225], dtype=np.float32)
    noise_steel = np.random.normal(0, 3.0, (1024, 1024))
    for c in range(3):
        rgb_data[0:1024, 0:1024, c] = np.clip(steel_base[c] + noise_steel, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------
    # REGION 1: Darkened Hardware Steel / Hex Fitting (1024..2048, 0..1024)
    # Used for Mounting Screws, Gland Body, Threaded Rings
    # -------------------------------------------------------------
    dark_steel_base = np.array([142, 148, 154], dtype=np.float32)
    noise_dark = np.random.normal(0, 4.0, (1024, 1024))
    for c in range(3):
        rgb_data[0:1024, 1024:2048, c] = np.clip(dark_steel_base[c] + noise_dark, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------
    # REGION 2: Industrial EPDM Matte Black Rubber (0..1024, 1024..2048)
    # Used for Cable_Segment jacket and inner gland seal
    # -------------------------------------------------------------
    rubber_base = np.array([36, 38, 42], dtype=np.float32)
    noise_rubber = np.random.normal(0, 2.5, (1024, 1024))
    for c in range(3):
        rgb_data[1024:2048, 0:1024, c] = np.clip(rubber_base[c] + noise_rubber, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------
    # REGION 3: Molded Ribbed Rubber for Connector Boot (1024..2048, 1024..1600)
    # -------------------------------------------------------------
    boot_base = np.array([48, 52, 56], dtype=np.float32)
    noise_boot = np.random.normal(0, 3.0, (576, 1024))
    for c in range(3):
        rgb_data[1024:1600, 1024:2048, c] = np.clip(boot_base[c] + noise_boot, 0, 255).astype(np.uint8)

    # -------------------------------------------------------------
    # REGION 4: Polished Nickel / BNC Bayonet Metal (1024..2048, 1600..2048)
    # -------------------------------------------------------------
    nickel_base = np.array([228, 232, 236], dtype=np.float32)
    noise_nickel = np.random.normal(0, 2.5, (448, 1024))
    for c in range(3):
        rgb_data[1600:2048, 1024:2048, c] = np.clip(nickel_base[c] + noise_nickel, 0, 255).astype(np.uint8)

    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)

    # Add fine structural details (NO text, NO barcodes)
    # 1. Fine subtle brush lines on galvanized steel
    for _ in range(60):
        sy = np.random.randint(0, 1024)
        draw.line([0, sy, 1024, sy + np.random.randint(-4, 4)], fill=(195, 200, 206, 255), width=1)

    # 2. Thread ridges in dark hardware region
    for ty in range(20, 1000, 32):
        draw.line([1024, ty, 2048, ty + 8], fill=(95, 100, 106, 255), width=3)
        draw.line([1024, ty + 8, 2048, ty + 16], fill=(180, 186, 192, 255), width=2)

    # 3. Longitudinal extrusion ribs on cable rubber
    for rx in range(40, 1000, 48):
        draw.line([rx, 1024, rx, 2048], fill=(28, 30, 33, 255), width=2)
        draw.line([rx + 2, 1024, rx + 2, 2048], fill=(46, 49, 54, 255), width=1)

    # 4. Molded boot ridges in connector boot region
    for by in range(1040, 1580, 40):
        draw.rectangle([1024, by, 2048, by + 12], fill=(32, 35, 38, 255))
        draw.rectangle([1024, by + 12, 2048, by + 24], fill=(62, 66, 72, 255))

    # 5. Knurled grip pattern and bayonet slots in polished nickel region
    for kx in range(1040, 2040, 32):
        draw.line([kx, 1600, kx, 2048], fill=(175, 180, 186, 255), width=3)
        draw.line([kx + 3, 1600, kx + 3, 2048], fill=(250, 252, 255, 255), width=2)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG")
    print(f"[OK] Clean Atlas Texture generated: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\Burak\Desktop\Security_CCTV\74. SEC_Ceiling_Cable_Drop\exports"
    target = os.path.join(out_dir, "T_Security_Atlas.png")
    create_ceiling_cable_drop_texture(target)
