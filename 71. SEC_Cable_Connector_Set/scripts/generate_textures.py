import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_rich_connector_texture(output_path):
    WIDTH, HEIGHT = 2048, 2048
    np.random.seed(7171)
    
    # Base Nickel / Steel Surface (218, 222, 226)
    base_metal = np.array([218, 222, 226], dtype=np.float32)
    noise_fine = np.random.normal(0, 3.5, (HEIGHT, WIDTH))
    
    rgb_data = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for c in range(3):
        channel = base_metal[c] + noise_fine * 0.6
        rgb_data[:, :, c] = np.clip(channel, 0, 255).astype(np.uint8)

    # 100% Solid Opaque texture - NO ALPHA SORTING GLITCHES!
    alpha_data = np.full((HEIGHT, WIDTH), 255, dtype=np.uint8)
    rgba = np.dstack([rgb_data, alpha_data])
    img = Image.fromarray(rgba, mode='RGBA')
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("arialbd.ttf", 26)
        font_med = ImageFont.truetype("arialbd.ttf", 19)
        font_small = ImageFont.truetype("arialbd.ttf", 15)
        font_tech = ImageFont.truetype("consola.ttf", 14)
    except:
        font_large = font_med = font_small = font_tech = ImageFont.load_default()

    # -------------------------------------------------------------
    # REGION 0: CLEAN BRUSHED NICKEL METAL (X: 0..512, Y: 0..512)
    # -------------------------------------------------------------

    # -------------------------------------------------------------
    # REGION 1: CLEAN MATTE BLACK RUBBER (X: 0..512, Y: 512..1024)
    # -------------------------------------------------------------
    draw.rectangle([0, 512, 512, 1024], fill=(24, 26, 28, 255))
    for _ in range(600):
        rx = np.random.randint(0, 512)
        ry = np.random.randint(512, 1024)
        draw.point((rx, ry), fill=(34, 36, 40, 255))

    # -------------------------------------------------------------
    # REGION 2: DIAMOND KNURLING SWATCH (X: 0..512, Y: 1024..1536)
    # -------------------------------------------------------------
    draw.rectangle([0, 1024, 512, 1536], fill=(185, 190, 195, 255))
    pitch = 12
    for sx in range(-512, 1024, pitch):
        draw.line([max(0, sx), 1024, min(512, sx + 512), 1536], fill=(110, 115, 120, 255), width=2)
        draw.line([max(0, sx + 2), 1024, min(512, sx + 514), 1536], fill=(245, 250, 255, 255), width=1)
    for sx in range(-512, 1024, pitch):
        draw.line([min(512, sx + 512), 1024, max(0, sx), 1536], fill=(125, 130, 135, 255), width=2)
        draw.line([min(512, sx + 514), 1024, max(0, sx + 2), 1536], fill=(235, 240, 245, 255), width=1)

    # -------------------------------------------------------------
    # REGION 3: CLEAR POLYCARBONATE TINT (X: 0..512, Y: 1536..2048)
    # Smoke / light ice blue polycarbonate body
    # -------------------------------------------------------------
    draw.rectangle([0, 1536, 512, 2048], fill=(205, 218, 226, 255))
    for ly in range(1536, 2048, 20):
        draw.line([0, ly, 512, ly], fill=(180, 195, 205, 255), width=2)
        draw.line([0, ly + 2, 512, ly + 2], fill=(225, 235, 242, 255), width=1)

    # -------------------------------------------------------------
    # REGION 4: BNC TECHNICAL BADGE (X: 550..1950, Y: 100..280)
    # -------------------------------------------------------------
    draw.rectangle([550, 100, 1950, 280], fill=(225, 228, 232, 255), outline=(130, 135, 140, 255), width=2)
    draw.text((580, 118), "SEC-BNC • 75 OHM PRECISION HD-SDI", fill=(25, 28, 32, 255), font=font_large)
    draw.text((580, 160), "4K 12G-SDI / EX-SDI • TEFLON PTFE • MIL-C-39012 • CE", fill=(55, 60, 68, 255), font=font_med)
    draw.text((580, 200), "RG59 / RG6 COAXIAL • 24K GOLD CONTACT PIN • HEX CRIMP 0.255\"", fill=(85, 90, 98, 255), font=font_small)
    # Gold badge block
    draw.rectangle([1650, 116, 1930, 264], fill=(245, 205, 35, 255), outline=(170, 135, 10, 255), width=2)
    draw.text((1670, 140), "24K GOLD", fill=(60, 45, 5, 255), font=font_large)
    draw.text((1670, 178), "PIN CONTACT", fill=(60, 45, 5, 255), font=font_med)
    draw.text((1670, 212), "LOW LOSS <0.1dB", fill=(90, 70, 10, 255), font=font_tech)

    # -------------------------------------------------------------
    # REGION 5: RJ45 CAT6A & T568B WIRING DIAGRAM (X: 550..1950, Y: 340..560)
    # -------------------------------------------------------------
    draw.rectangle([550, 340, 1950, 560], fill=(22, 25, 28, 255), outline=(245, 195, 20, 255), width=2)
    draw.text((575, 355), "CAT6A SHIELDED FTP • 10GbE • PoE++ (90W 802.3bt)", fill=(255, 215, 0, 255), font=font_large)
    
    # 8-color T568B wiring bars
    wire_specs = [
        ((255, 255, 255), (255, 120, 0), "1:W-ORG"),
        ((255, 120, 0), (200, 80, 0), "2:ORG"),
        ((255, 255, 255), (30, 180, 60), "3:W-GRN"),
        ((0, 120, 240), (0, 80, 180), "4:BLU"),
        ((255, 255, 255), (0, 120, 240), "5:W-BLU"),
        ((30, 180, 60), (10, 120, 30), "6:GRN"),
        ((255, 255, 255), (130, 75, 30), "7:W-BRN"),
        ((130, 75, 30), (80, 45, 15), "8:BRN"),
    ]
    w_bar = (1950 - 550 - 40) / 8
    for i, (c_fill, c_stripe, label) in enumerate(wire_specs):
        bx = int(570 + i * w_bar)
        draw.rectangle([bx, 400, int(bx + w_bar - 8), 490], fill=c_fill + (255,), outline=(60, 65, 70, 255), width=2)
        if "W-" in label:
            for sy in range(405, 485, 12):
                draw.line([bx + 2, sy, int(bx + w_bar - 10), sy + 6], fill=c_stripe + (255,), width=4)
        draw.rectangle([bx, 495, int(bx + w_bar - 8), 530], fill=(12, 14, 16, 255))
        draw.text((bx + 4, 502), label[:5], fill=(255, 255, 255, 255), font=font_small)

    # -------------------------------------------------------------
    # REGION 6: DC 12V POLARITY BADGE (X: 550..1950, Y: 620..800)
    # Mapped onto the front flat of the DC barrel body!
    # -------------------------------------------------------------
    draw.rectangle([550, 620, 1950, 800], fill=(20, 22, 26, 255), outline=(220, 40, 40, 255), width=3)
    # Polarity symbol
    # (-) Left
    draw.text((620, 675), "(-)", fill=(245, 250, 255, 255), font=font_large)
    draw.line([665, 692, 700, 692], fill=(245, 250, 255, 255), width=4)
    # Outer Ring
    draw.arc([700, 665, 756, 719], 45, 315, fill=(245, 250, 255, 255), width=5)
    # Center Pin (+)
    draw.ellipse([722, 686, 734, 698], fill=(255, 50, 50, 255))
    draw.line([734, 692, 770, 692], fill=(255, 50, 50, 255), width=4)
    draw.text((780, 675), "(+)", fill=(255, 60, 60, 255), font=font_large)
    
    # Text next to polarity
    draw.text((860, 665), "12V-24V DC • 5A MAX • CENTER POSITIVE", fill=(255, 215, 0, 255), font=font_large)
    draw.text((860, 710), "5.5 x 2.1mm CCTV POWER PLUG • MOLDED STRAIN RELIEF", fill=(210, 215, 220, 255), font=font_med)
    draw.text((860, 745), "POLARITY: INNER SLEEVE (+), OUTER SHELL (-) • CE / RoHS", fill=(170, 175, 180, 255), font=font_small)

    # Master Specifications Bar at bottom
    draw.rectangle([550, 1850, 2000, 1980], fill=(22, 25, 28, 255), outline=(245, 195, 20, 255), width=2)
    draw.text((580, 1875), "SEC-VISION SECURITY CCTV CONNECTOR FIELD SET • BNC 75Ω / RJ45 CAT6A / 12V DC", fill=(255, 215, 0, 255), font=font_large)
    draw.text((580, 1925), "INDUSTRIAL FIELD TERMINATION GRADE • 50μ GOLD CONTACTS • FLAME RETARDANT 94V-0", fill=(220, 225, 230, 255), font=font_small)

    img.save(output_path, "PNG")
    print(f"Rich Cable Connector texture saved to: {output_path}")

if __name__ == "__main__":
    import os
    out_dir = r"C:\Users\Burak\Desktop\Security_CCTV\71. SEC_Cable_Connector_Set\exports"
    os.makedirs(out_dir, exist_ok=True)
    create_rich_connector_texture(os.path.join(out_dir, "T_Security_Atlas.png"))
