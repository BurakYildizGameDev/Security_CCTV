import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_texture_66(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(42)
    
    # 1. Galvanized Zinc Base
    base_color = np.array([210, 215, 220], dtype=np.float32)
    noise_fine = np.random.normal(0, 10, (HEIGHT, WIDTH))
    
    num_flakes = 900
    fx = np.random.randint(0, WIDTH, num_flakes)
    fy = np.random.randint(0, HEIGHT, num_flakes)
    f_val = np.random.uniform(-30, 30, num_flakes)
    
    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for c in range(3):
        channel = base_color[c] + noise_fine * 0.8
        brush = np.sin(np.linspace(0, 260 * math.pi, HEIGHT))[:, None] * 3.0
        channel += brush
        rgb_data[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)

    from scipy.ndimage import gaussian_filter
    flake_grid = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    flake_grid[fy, fx] = f_val
    flake_map = gaussian_filter(flake_grid, sigma=12) * 5.5
    for c in range(3):
        rgb_data[:, :, c] = np.clip(rgb_data[:, :, c].astype(np.float32) + flake_map, 0, 255).astype(np.uint8)

    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)
    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("arialbd.ttf", 26)
        font_med = ImageFont.truetype("arialbd.ttf", 19)
        font_small = ImageFont.truetype("arialbd.ttf", 14)
        font_tech = ImageFont.truetype("consola.ttf", 14)
    except:
        font_large = font_med = font_small = font_tech = ImageFont.load_default()

    def draw_hazard_stripes(x0, y0, x1, y1, stripe_w=24):
        draw.rectangle([x0, y0, x1, y1], fill=(245, 195, 20, 255))
        w = x1 - x0
        h = y1 - y0
        for sx in range(-h, w + h, stripe_w * 2):
            pts = [
                (max(x0, x0 + sx), y0),
                (min(x1, x0 + sx + stripe_w), y0),
                (min(x1, x0 + sx + stripe_w + h), y1),
                (max(x0, x0 + sx + h), y1),
            ]
            draw.polygon(pts, fill=(20, 20, 20, 255))
        draw.rectangle([x0, y0, x1, y1], outline=(15, 15, 15, 255), width=2)

    def draw_stamped_slot(x0, y0, x1, y1, r=8):
        draw.rounded_rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], radius=r+3, fill=(110, 115, 120, 255))
        draw.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], radius=r+1, fill=(245, 250, 255, 255))
        draw.rounded_rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], radius=r, fill=(35, 40, 45, 255))
        draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=(0, 0, 0, 0))

    # ==============================================================
    # REGION 1: TRAY BASE FLOOR (PIL Y: 82..983, X: 64..1984)
    # ==============================================================
    # Side flanges of floor:
    # Left flange hazard stripe
    draw_hazard_stripes(64, 885, 1984, 915, stripe_w=20)
    for lx in [450, 1450]:
        draw.text((lx - 150, 925), "HEAVY DUTY CABLE TRAY • 65 KG/M MAX", fill=(20, 20, 20, 255), font=font_small)

    # Right flange hazard stripe
    draw_hazard_stripes(64, 150, 1984, 180, stripe_w=20)
    for rx in [450, 1450]:
        draw.text((rx - 150, 120), "SEC-VISION INFRASTRUCTURE • EN 61537", fill=(20, 20, 20, 255), font=font_small)

    # Center slotted rungs:
    num_cols = 16
    col_w = (1984 - 128) / num_cols
    for c in range(num_cols):
        cx = int(128 + c * col_w + col_w / 2)
        draw_stamped_slot(cx - 16, 230, cx + 16, 370, r=8)
        draw_stamped_slot(cx - 16, 690, cx + 16, 830, r=8)

    # Grounding decals
    for gx in [500, 1024, 1550]:
        draw.ellipse([gx - 18, 515, gx + 18, 551], fill=(35, 145, 45, 255), outline=(15, 15, 15, 255), width=2)
        draw.line([gx, 520, gx, 532], fill=(255, 255, 255, 255), width=3)
        draw.line([gx - 10, 532, gx + 10, 532], fill=(255, 255, 255, 255), width=3)
        draw.line([gx - 7, 537, gx + 7, 537], fill=(255, 255, 255, 255), width=3)
        draw.line([gx - 3, 542, gx + 3, 542], fill=(255, 255, 255, 255), width=3)

    # ==============================================================
    # REGION 2: SIDE WALLS - PRECISE NON-OVERLAPPING LAYOUT
    # Left Wall: PIL Y: 1024..1270
    # ==============================================================
    def draw_centered_banner(y0, y1, text, font, border_pad=35):
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        bw = tw + border_pad * 2
        bx0 = 1024 - bw // 2
        bx1 = bx0 + bw
        draw.rectangle([bx0, y0, bx1, y1], fill=(22, 24, 28, 255), outline=(245, 195, 20, 255), width=2)
        tx = bx0 + border_pad
        ty = y0 + (y1 - y0 - th) // 2 - bbox[1]
        draw.text((tx, ty), text, fill=(255, 215, 0, 255), font=font)

    font_banner = ImageFont.truetype("arialbd.ttf", 16) if "arialbd.ttf" in globals().get("__file__", "") or True else font_small

    # 1. Top rolled hem
    draw.rectangle([64, 1024, 1984, 1045], fill=(240, 245, 250, 255), outline=(110, 115, 120, 255), width=2)
    # 2. Hazard stripe: Y in [1048, 1076] (height 28px)
    draw_hazard_stripes(64, 1048, 1984, 1076, stripe_w=22)
    
    # 3. Text Band: Y in [1084, 1114] (height 30px) - PERFECTLY CENTERED, NO SHIFT / KAYMA!
    draw_centered_banner(1084, 1114, "SEC-VISION CABLE TRAY • HEAVY DUTY HDG STEEL • 200x50mm • CE", font_banner)

    # 4. Clean metal buffer: Y in [1115, 1144] (30 pixels empty margin!)

    # 5. Stamped slots: Y in [1145, 1205] (height 60px)
    for c in range(num_cols):
        cx = int(128 + c * col_w + col_w / 2)
        draw_stamped_slot(cx - 28, 1145, cx + 28, 1205, r=8)
    for bx in [95, 145, 1905, 1955]:
        draw_stamped_slot(bx - 10, 1135, bx + 10, 1215, r=8)

    # ==============================================================
    # Right Wall: PIL Y: 1270..1515
    # ==============================================================
    # 1. Top rolled hem
    draw.rectangle([64, 1270, 1984, 1291], fill=(240, 245, 250, 255), outline=(110, 115, 120, 255), width=2)
    # 2. Hazard stripe: Y in [1294, 1322]
    draw_hazard_stripes(64, 1294, 1984, 1322, stripe_w=22)
    # 3. Text band: Y in [1330, 1360] - PERFECTLY CENTERED, NO SHIFT / KAYMA!
    draw_centered_banner(1330, 1360, "SEC-VISION CABLE TRAY • HEAVY DUTY HDG STEEL • 200x50mm • CE", font_banner)
    # 4. Clean metal buffer: Y in [1361, 1389]
    # 5. Stamped slots: Y in [1390, 1450]
    for c in range(num_cols):
        cx = int(128 + c * col_w + col_w / 2)
        draw_stamped_slot(cx - 28, 1390, cx + 28, 1450, r=8)
    for bx in [95, 145, 1905, 1955]:
        draw_stamped_slot(bx - 10, 1380, bx + 10, 1460, r=8)

    # ==============================================================
    # REGION 3: COUPLERS (PIL Y: 1520..1984, X: 64..980)
    # ==============================================================
    draw.rectangle([64, 1520, 980, 1984], fill=(185, 190, 195, 255), outline=(70, 75, 80, 255), width=3)
    def draw_heavy_bolt(cx, cy, radius):
        pts = []
        for a in range(6):
            ang = math.radians(a * 60 + 30)
            pts.append((cx + radius * math.cos(ang), cy + radius * math.sin(ang)))
        draw.polygon([(x+3, y+3) for x, y in pts], fill=(40, 45, 50, 255))
        draw.polygon(pts, fill=(235, 240, 245, 255), outline=(30, 35, 40, 255), width=3)
        draw.ellipse([cx - radius*0.5, cy - radius*0.5, cx + radius*0.5, cy + radius*0.5], fill=(160, 165, 170, 255), outline=(60, 65, 70, 255))
        draw.ellipse([cx - radius*0.3, cy - radius*0.3, cx + radius*0.3, cy + radius*0.3], fill=(255, 255, 255, 255))

    for bx in [200, 380, 660, 840]:
        draw_heavy_bolt(bx, 1750, 44)

    # ==============================================================
    # REGION 4: CAUTION PLACARD (PIL Y: 1520..1984, X: 1040..1984)
    # ==============================================================
    draw.rectangle([1060, 1540, 1960, 1960], fill=(240, 195, 20, 255), outline=(15, 15, 15, 255), width=5)
    draw.rectangle([1075, 1555, 1945, 1945], fill=(250, 205, 25, 255), outline=(35, 35, 35, 255), width=2)
    draw.rectangle([1095, 1575, 1925, 1665], fill=(15, 15, 15, 255))
    draw.text((1330, 1595), "CAUTION / DANGER", fill=(255, 215, 0, 255), font=font_large)
    
    tri_pts = [(1200, 1650), (1155, 1590), (1245, 1590)]
    draw.polygon(tri_pts, fill=(255, 215, 0, 255), outline=(20, 20, 20, 255), width=3)
    draw.text((1193, 1600), "!", fill=(20, 20, 20, 255), font=font_large)
    
    draw.text((1120, 1695), "HEAVY INDUSTRIAL CABLE TRAY SYSTEM - EN 61537", fill=(20, 20, 20, 255), font=font_med)
    draw.text((1120, 1740), "MAXIMUM DISTRIBUTED LOAD: 65 kg / LINEAR METER", fill=(20, 20, 20, 255), font=font_small)
    draw.text((1120, 1780), "MANDATORY BONDING TO GROUND - DO NOT USE AS WALKWAY", fill=(20, 20, 20, 255), font=font_small)
    draw.text((1120, 1825), "PART NO: SEC-CT-1000-200-HDG   |   BATCH: 2026-L4-9921B", fill=(40, 40, 40, 255), font=font_tech)
    draw.text((1120, 1870), "ANTIGRAVITY SECURITY INFRASTRUCTURE LTD. | CE", fill=(40, 40, 40, 255), font=font_tech)

    img.save(output_path, "PNG")
    print(f"Asset 66 Non-overlapping Texture saved to: {output_path}")

if __name__ == "__main__":
    import os
    out_path = r"66. SEC_Cable_Tray_Straight\exports\T_Security_Atlas.png"
    create_texture_66(out_path)
