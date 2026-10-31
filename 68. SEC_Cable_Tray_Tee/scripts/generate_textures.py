import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_tee_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(44)
    
    # 1. Galvanized Zinc Base with Spangle Flakes
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
        font_med = ImageFont.truetype("arialbd.ttf", 18)
        font_small = ImageFont.truetype("arialbd.ttf", 14)
        font_banner = ImageFont.truetype("arialbd.ttf", 16)
        font_tech = ImageFont.truetype("consola.ttf", 14)
    except:
        font_large = font_med = font_small = font_banner = font_tech = ImageFont.load_default()

    def draw_hazard_stripes(x0, y0, x1, y1, stripe_w=22):
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

    # ==============================================================
    # REGION 1: TEE BASE FLOOR (PIL Y: 82..983, X: 64..1984)
    # ==============================================================
    # Top flange hazard stripe (PIL Y ~150..180)
    draw_hazard_stripes(64, 150, 1984, 180, stripe_w=20)
    for rx in [500, 1500]:
        draw.text((rx - 160, 120), "SEC-VISION TEE JUNCTION • EN 61537", fill=(20, 20, 20, 255), font=font_small)

    # Bottom flange hazard stripe (PIL Y ~885..915)
    draw_hazard_stripes(64, 885, 1984, 915, stripe_w=20)
    for lx in [500, 1500]:
        draw.text((lx - 160, 925), "HEAVY DUTY HDG STEEL • 200x50mm • CE", fill=(20, 20, 20, 255), font=font_small)

    # Slotted rungs:
    num_cols = 12
    col_w = (1984 - 128) / num_cols
    for c in range(num_cols):
        cx = int(128 + c * col_w + col_w / 2)
        draw_stamped_slot(cx - 18, 230, cx + 18, 370, r=8)
        draw_stamped_slot(cx - 18, 690, cx + 18, 830, r=8)

    # Grounding decals
    for gx in [512, 1024, 1536]:
        draw.ellipse([gx - 18, 515, gx + 18, 551], fill=(35, 145, 45, 255), outline=(15, 15, 15, 255), width=2)
        draw.line([gx, 520, gx, 532], fill=(255, 255, 255, 255), width=3)
        draw.line([gx - 10, 532, gx + 10, 532], fill=(255, 255, 255, 255), width=3)
        draw.line([gx - 7, 537, gx + 7, 537], fill=(255, 255, 255, 255), width=3)
        draw.line([gx - 3, 542, gx + 3, 542], fill=(255, 255, 255, 255), width=3)

    # ==============================================================
    # REGION 2: SIDE WALLS
    # Strip 1 (Main Back Wall): PIL Y: 1024..1270
    # ==============================================================
    # 1. Top rolled hem
    draw.rectangle([64, 1024, 1984, 1045], fill=(240, 245, 250, 255), outline=(110, 115, 120, 255), width=2)
    # 2. Hazard stripe: Y in [1048, 1076]
    draw_hazard_stripes(64, 1048, 1984, 1076, stripe_w=22)
    # 3. Perfectly Centered Banner
    draw_centered_banner(1084, 1114, "SEC-VISION CABLE TRAY • HORIZONTAL TEE 200x50mm • CE", font_banner)
    # 4. Clean buffer: Y in [1115, 1144]
    # 5. Stamped slots: Y in [1145, 1205]
    for c in range(num_cols):
        cx = int(128 + c * col_w + col_w / 2)
        draw_stamped_slot(cx - 28, 1145, cx + 28, 1205, r=8)
    for bx in [95, 145, 1905, 1955]:
        draw_stamped_slot(bx - 10, 1135, bx + 10, 1215, r=8)

    # ==============================================================
    # Strip 2 (Branch & Corner Walls): PIL Y: 1270..1515
    # ==============================================================
    # 1. Top rolled hem
    draw.rectangle([64, 1270, 1984, 1291], fill=(240, 245, 250, 255), outline=(110, 115, 120, 255), width=2)
    # 2. Hazard stripe: Y in [1294, 1322]
    draw_hazard_stripes(64, 1294, 1984, 1322, stripe_w=22)
    # 3. Perfectly Centered Banner
    draw_centered_banner(1330, 1360, "SEC-VISION CABLE TRAY • T-BRANCH 200x50mm • HDG STEEL", font_banner)
    # 4. Clean buffer: Y in [1361, 1389]
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

    for bx in [200, 400, 640, 840]:
        draw_heavy_bolt(bx, 1750, 38)

    # ==============================================================
    # REGION 4: SPECIFICATION PLATE (PIL Y: 1520..1984, X: 1024..1984)
    # ==============================================================
    draw.rectangle([1040, 1540, 1960, 1960], fill=(24, 26, 30, 255), outline=(245, 195, 20, 255), width=3)
    draw.rectangle([1060, 1560, 1940, 1610], fill=(245, 195, 20, 255))
    draw.text((1220, 1572), "SEC-VISION TEE JUNCTION SPECIFICATION", fill=(20, 20, 20, 255), font=font_med)
    draw.text((1080, 1640), "MODEL: SEC-CT-TEE-200-HDG", fill=(255, 255, 255, 255), font=font_small)
    draw.text((1080, 1680), "MAIN CHANNEL: 200x50mm  |  BRANCH CHANNEL: 200x50mm", fill=(200, 205, 210, 255), font=font_tech)
    draw.text((1080, 1720), "FINISH: HOT-DIP GALVANIZED (HDG) ACCORDING TO ISO 1461", fill=(200, 205, 210, 255), font=font_tech)
    draw.text((1080, 1760), "STANDARD: EN 61537 / NEMA VE 1 CABLE MANAGEMENT", fill=(200, 205, 210, 255), font=font_tech)
    draw.text((1080, 1800), "LOAD RATING: HEAVY INDUSTRIAL / GRADE 3 / CE / RoHS", fill=(245, 195, 20, 255), font=font_tech)
    draw.text((1080, 1840), "SERIAL: *SEC-CTT-202688921-D*", fill=(170, 175, 180, 255), font=font_tech)

    img.save(output_path, "PNG")
    print(f"Asset 68 Tee Texture saved to: {output_path}")

if __name__ == "__main__":
    import os
    out_dir = r"68. SEC_Cable_Tray_Tee\exports"
    os.makedirs(out_dir, exist_ok=True)
    create_tee_texture(os.path.join(out_dir, "T_Security_Atlas.png"))
