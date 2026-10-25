"""
=============================================================================
Security CCTV Asset Production Suite - Asset 40
Asset Name: SEC_Access_Turnstile_Reader (Turnike Kart Okuyucu)
Texture Generation Script v1 (2048 x 2048)

ATLAS YERLESIMI (piksel):
    BANT-1 COVER  (32, 32)    - (1308, 1660)  1276 x 1628 -> 58 x 74 mm (22.0 px/mm)
    BANT-2 RFID   (1330, 32)  - (2030, 599)    700 x  567 -> 42 x 34 mm (RFID plaka)
    BANT-3 LED    (1330, 630) - (1630, 930)    300 x  300 -> LED halkasi
    BANT-4 RENK   (1660, 630) - (2016, 2016)  duz renk alanlari

ON YUZ KURALI: +Y normaline bakan yuzler flip_u=True ile haritalanir; dunya +X
dokunun SOLUNA duser. Govde 28 derece egimli oldugu icin UV'ler EGIMDEN ONCE
(yuz yerel uzayinda) atanir; cover_px() bu yerel uzayi kullanir.
=============================================================================
"""

import math
import os
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.dirname(SCRIPT_DIR)
EXPORTS_DIR = os.path.join(ASSET_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

ATLAS_PATH = os.path.join(EXPORTS_DIR, "T_Security_Atlas.png")

FONT_MONO = r"C:\Windows\Fonts\consolab.ttf"
FONT_SANS = r"C:\Windows\Fonts\arialbd.ttf"

ATLAS_W, ATLAS_H = 2048, 2048

# ---------------------------------------------------------------- UV bantlari
REGION_COVER = (32, 32, 1308, 1660)
REGION_RFID = (1330, 32, 2030, 599)
REGION_LED = (1330, 630, 1630, 930)
REGION_DETAIL = (1660, 630, 2016, 2016)

# ---------------------------------------------------------------- Geometri esleme (m)
COVER_W, COVER_H = 0.0580, 0.0740            # Reader_Housing on yuzu (58 x 74 mm)
TILT_DEG = 28.0                              # govde egimi (UV'yi etkilemez)

RFID_X, RFID_Z = 0.0, -0.0140                # RFID plaka merkezi (yuz yerel)
RFID_W, RFID_H = 0.0420, 0.0340              # 42 x 34 mm

LED_X, LED_Z = 0.0160, 0.0160                # LED halkasi merkezi (yuz yerel)
LED_R_OUT, LED_R_IN = 0.0070, 0.0052         # Ø14 / Ø10.4 mm

# Duz renk UV noktalari (piksel)
PIX_FLAT_BODY = (1700, 700)
PIX_FLAT_SIDE = (1900, 700)
PIX_FLAT_DARK = (1700, 950)
PIX_FLAT_METAL = (1900, 950)

# Renk Paleti (aile dili)
BODY_LIGHT = (243, 246, 250, 255)
BODY_MID = (228, 234, 242, 255)
BRUSH_LINE = (235, 240, 246, 255)
FRAME_LINE = (166, 177, 191, 255)
PLATE_DARK = (18, 22, 28, 255)
PLATE_DARK_2 = (30, 36, 44, 255)
AMBER = (226, 168, 32, 255)
INK_DARK = (18, 22, 28, 255)
INK_TEXT = (46, 54, 66, 255)
INK_SOFT = (98, 110, 124, 255)
WHITE = (255, 255, 255, 255)
COOL_LIGHT = (176, 196, 216, 255)
COOL_SOFT = (146, 168, 192, 255)
ALERT_RED = (196, 40, 32, 255)
GRAPHITE = (44, 50, 58, 255)

_FONT_CACHE = {}
_TEXT_BOXES = []
_GRAPHIC_BOXES = []


def load_font(path, size):
    key = (path, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    try:
        f = ImageFont.truetype(path, size)
    except Exception:
        f = ImageFont.load_default()
    _FONT_CACHE[key] = f
    return f


def text_w(draw, text, font):
    try:
        return draw.textlength(text, font=font)
    except Exception:
        return draw.textlength(text)


def fit_font(draw, text, path, max_width, start_size, min_size=18):
    """Metin kutusuna tasmayacak en buyuk puntoyu secer (tasmasiz tipografi)."""
    size = start_size
    while size > min_size:
        f = load_font(path, size)
        if text_w(draw, text, f) <= max_width:
            return f
        size -= 2
    return load_font(path, min_size)


def _track_text(draw, x, y, text, font):
    """Tipografi QA: her metnin piksel kutusunu kaydeder."""
    if not text.strip():
        return
    try:
        l, t, r, b = draw.textbbox((0, 0), text, font=font)
    except Exception:
        return
    _TEXT_BOXES.append((x + l, y + t, x + r, y + b, text))


def draw_left(draw, x, y, text, font, fill):
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def draw_center(draw, cx, y, text, font, fill):
    x = cx - text_w(draw, text, font) / 2.0
    draw.text((x, y), text, font=font, fill=fill)
    _track_text(draw, x, y, text, font)


def track_rect(box, name):
    """Dekoratif bloklari cerceve QA'si icin kaydeder."""
    x0, y0, x1, y1 = box
    _GRAPHIC_BOXES.append((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), name))


def ink_size(draw, text, font):
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    return (r - l, b - t)


def draw_left_ink(draw, x, ink_top, text, font, fill):
    """Sol kenari x'e, murekkep tepesi ink_top'a gelecek sekilde yazar."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw_left(draw, x - l, ink_top - t, text, font, fill)
    return (x, ink_top, x + (r - l), ink_top + (b - t))


def draw_center_ink(draw, cx, ink_top, text, font, fill):
    """Murekkep kutusunu yatayda cx'e gore ortalar."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    draw_left(draw, cx - (l + r) / 2.0, ink_top - t, text, font, fill)
    return (cx - (r - l) / 2.0, ink_top, cx + (r - l) / 2.0, ink_top + (b - t))


def draw_right_ink(draw, rx, ink_top, text, font, fill):
    """Sag kenari rx'e, murekkep tepesi ink_top'a gelecek sekilde yazar."""
    l, t, r, b = draw.textbbox((0, 0), text, font=font)
    tw = text_w(draw, text, font)
    draw_left(draw, rx - tw, ink_top - t, text, font, fill)
    return (rx - (r - l), ink_top, rx, ink_top + (b - t))


PX_PER_MM = (REGION_COVER[2] - REGION_COVER[0]) / (COVER_W * 1000.0)


def cover_px(x_m, z_m):
    """Yuz yerel (X, Z) konumunu atlas pikseline cevirir (flip_u=True eslemesi).

    Egim UV'den ONCE uygulandigi icin burada egim yok: doku "acilmis" yuzeydir.
    """
    x0, y0, x1, y1 = REGION_COVER
    nx = (x_m + COVER_W / 2.0) / COVER_W
    nz = (z_m + COVER_H / 2.0) / COVER_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))


def rfid_px_rect():
    """RFID plakasinin atlas piksel dikdortgeni (sol, ust, sag, alt)."""
    ax, ay = cover_px(RFID_X + RFID_W / 2.0, RFID_Z + RFID_H / 2.0)
    bx, by = cover_px(RFID_X - RFID_W / 2.0, RFID_Z - RFID_H / 2.0)
    return (ax, ay, bx, by)


def led_px_center():
    return cover_px(LED_X, LED_Z)


def verify_layout():
    """Metin kutularinin bant icinde kaldigini ve ust uste binmedigini dogrular."""
    regions = [REGION_COVER, REGION_RFID, REGION_LED, REGION_DETAIL]
    problems = []
    for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES:
        cx, cy = (tx0 + tx1) / 2.0, (ty0 + ty1) / 2.0
        rx0 = ry0 = rx1 = ry1 = None
        for (ax0, ay0, ax1, ay1) in regions:
            if ax0 <= cx <= ax1 and ay0 <= cy <= ay1:
                rx0, ry0, rx1, ry1 = ax0, ay0, ax1, ay1
                break
        if rx0 is None:
            problems.append(f"'{txt}' hicbir banda ait degil: {(tx0, ty0, tx1, ty1)}")
            continue
        if tx0 < rx0 + 6 or ty0 < ry0 + 4 or tx1 > rx1 - 6 or ty1 > ry1 - 4:
            problems.append(f"'{txt}' bant disina tasiyor: {(tx0, ty0, tx1, ty1)}")

    boxes = sorted(_TEXT_BOXES)
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ax0, ay0, ax1, ay1, at = boxes[i]
            bx0, by0, bx1, by1, bt = boxes[j]
            ox = min(ax1, bx1) - max(ax0, bx0)
            oy = min(ay1, by1) - max(ay0, by0)
            if ox > 4 and oy > 4:
                problems.append(f"'{at}' ile '{bt}' ust uste biniyor ({ox:.0f} x {oy:.0f} px)")

    fx0 = REGION_COVER[0] + 36
    fy0 = REGION_COVER[1] + 36
    fx1 = REGION_COVER[2] - 36
    fy1 = REGION_COVER[3] - 36
    for (gx0, gy0, gx1, gy1, name) in _GRAPHIC_BOXES:
        if gx0 < fx0 or gy0 < fy0 or gx1 > fx1 or gy1 > fy1:
            problems.append(f"'{name}' sus cercevesini kesiyor: {(gx0, gy0, gx1, gy1)}")

    if problems:
        for p in problems:
            print("[LAYOUT-FAIL] " + p)
        raise AssertionError(f"Tipografi yerlesimi hatali: {len(problems)} sorun")
    print(f"[LAYOUT-OK] {len(_TEXT_BOXES)} metin blogu bant sinirlari icinde, cakisma yok")


def verify_sockets():
    """RFID ve LED yuvalarinin on yuz icinde ve birbirine degmedigini dogrular.

    Iki 3D parca (RFID plakasi + LED halkasi) dokunun uzerine oturur; cakisma
    veya yuz disina tasma render'da kirik goruntu uretir.
    """
    problems = []
    rx0, ry0, rx1, ry1 = rfid_px_rect()
    lcx, lcy = led_px_center()
    r_led = LED_R_OUT * 1000.0 * PX_PER_MM
    cx0, cy0, cx1, cy1 = REGION_COVER

    for label, (a, b, c, d) in (("RFID plakasi", (rx0, ry0, rx1, ry1)),):
        if a < cx0 + 30 or b < cy0 + 30 or c > cx1 - 30 or d > cy1 - 30:
            problems.append(f"{label} on yuz cercevesini asiyor: {(a, b, c, d)}")

    # LED halkasi plakanin ustunde ve +X tarafinda (flip_u nedeniyle dokuda SOLDA)
    if not (lcy + r_led < ry0 - 20):
        problems.append(f"LED halkasi RFID plakasina degiyor "
                        f"(led alt {lcy + r_led:.0f} / plaka ust {ry0:.0f})")
    if not (lcx < (rx0 + rx1) / 2.0):
        problems.append(f"LED halkasi +X tarafinda degil (dokuda sol): "
                        f"x={lcx:.0f}, plaka merkezi {(rx0 + rx1) / 2.0:.0f}")

    if problems:
        for p in problems:
            print("[SOCKET-FAIL] " + p)
        raise AssertionError(f"Yuva yerlesimi hatali: {len(problems)} sorun")
    print(f"[SOCKET-OK] RFID plakasi {(rx1 - rx0):.0f}x{(ry1 - ry0):.0f} px yuz icinde, "
          f"LED halkasi ({lcx:.0f},{lcy:.0f}) cakismasiz")


def report_ink_heights():
    """En kucuk murekkep yuksekligini raporlar (render'da okunabilirlik tabani)."""
    if not _TEXT_BOXES:
        return
    heights = sorted((ty1 - ty0, txt) for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES)
    print(f"[INK] En kucuk murekkep: {heights[0][0]:.0f} px "
          f"({heights[0][0] / PX_PER_MM:.2f} mm) -> '{heights[0][1]}'")
    print(f"[INK] En buyuk murekkep: {heights[-1][0]:.0f} px "
          f"({heights[-1][0] / PX_PER_MM:.2f} mm) -> '{heights[-1][1]}'")
    render_cover_px = (900.0 / 0.105) * COVER_W
    scale = render_cover_px / float(REGION_COVER[2] - REGION_COVER[0])
    print(f"[INK] Render'da kapak genisligi {render_cover_px:.1f} px "
          f"(olcek {scale:.4f}) -> en kucuk murekkep ~{heights[0][0] * scale:.1f} px, "
          f"en buyuk ~{heights[-1][0] * scale:.1f} px")


def draw_barcode(draw, x0, y0, width, height, dark=INK_DARK, light=WHITE):
    x = x0
    idx = 0
    while x < x0 + width:
        thick = 3 + (idx * 7) % 5
        col = dark if (idx % 3 == 0 or idx % 7 == 0) else light
        draw.line([(x, y0), (x, y0 + height)], fill=col, width=thick)
        x += 9
        idx += 1


# ---------------------------------------------------------------- BANT-1: On yuz
def draw_cover(draw):
    x0, y0, x1, y1 = REGION_COVER
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)

    # Fircalanmis govde mikro dokusu + cift sus cercevesi
    for yy in range(y0 + 4, y1, 9):
        draw.line([(x0, yy), (x1, yy)], fill=BRUSH_LINE)
    draw.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=FRAME_LINE, width=5)
    draw.rectangle([x0 + 24, y0 + 24, x1 - 24, y1 - 24],
                   outline=(210, 219, 230, 255), width=3)

    r_led = LED_R_OUT * 1000.0 * PX_PER_MM

    # --- Ust marka plakasi -------------------------------------------------
    PT = (x0 + 40, 76, x1 - 40, 316)
    track_rect(PT, "Marka plakasi")
    draw.rectangle([PT[0], PT[1], PT[2], PT[3]], fill=PLATE_DARK,
                   outline=(78, 90, 104, 255), width=4)
    draw.rectangle([PT[0], PT[1], PT[0] + 18, PT[3]], fill=AMBER)

    LX = PT[0] + 48
    RX = PT[2] - 26
    f_title = fit_font(draw, "SEC-TR 150", FONT_SANS, 700, 68, 40)
    f_tag = load_font(FONT_MONO, 26)
    f_sub = fit_font(draw, "TURNSTILE RFID READER", FONT_MONO, RX - LX, 32, 22)
    th = ink_size(draw, "SEC-TR 150", f_title)[1]
    sh = ink_size(draw, "TURNSTILE RFID READER", f_sub)[1]
    gap = 20
    y = PT[1] + (PT[3] - PT[1] - (th + sh + gap)) / 2.0
    bb = draw_left_ink(draw, LX, y, "SEC-TR 150", f_title, WHITE)
    draw_right_ink(draw, RX, y + 4, "IP65", f_tag, AMBER)
    draw_left_ink(draw, LX, bb[3] + gap, "TURNSTILE RFID READER", f_sub, COOL_LIGHT)

    # --- LED halkasi yuvasi ------------------------------------------------
    lcx, lcy = led_px_center()
    draw.ellipse([lcx - r_led - 26, lcy - r_led - 26,
                  lcx + r_led + 26, lcy + r_led + 26],
                 fill=GRAPHITE, outline=(206, 216, 228, 255), width=3)
    draw.ellipse([lcx - r_led + 2, lcy - r_led + 2,
                  lcx + r_led - 2, lcy + r_led - 2], fill=(12, 16, 22, 255))

    # --- "PRESENT CARD" yonlendirmesi (LED ile kart sembolu arasinda) ------
    f_card = fit_font(draw, "PRESENT CARD", FONT_SANS, 420, 50, 28)
    f_hint = load_font(FONT_MONO, 27)
    bb = draw_left_ink(draw, 560, 392, "PRESENT CARD", f_card, INK_DARK)
    draw_left_ink(draw, 560, bb[3] + 14, "HOLD 2 - 5 cm", f_hint, INK_TEXT)
    draw_left_ink(draw, 560, bb[3] + 48, "FROM SURFACE", f_hint, INK_TEXT)
    draw_left_ink(draw, 560, bb[3] + 90, "13.56 MHz", f_hint, INK_SOFT)

    # Kart sembolu (yuvarlatilmis dikdortgen + cip)
    card = (1010, 392, 1268, 592)
    track_rect(card, "Kart sembolu")
    draw.rounded_rectangle([card[0], card[1], card[2], card[3]], radius=18,
                           fill=(226, 232, 240, 255), outline=FRAME_LINE, width=4)
    draw.rectangle([card[0] + 18, card[1] + 34, card[0] + 74, card[1] + 82],
                   fill=AMBER, outline=(150, 108, 12, 255), width=2)
    for k in range(3):
        yy = card[1] + 118 + k * 26
        draw.line([(card[0] + 18, yy), (card[2] - 24, yy)], fill=(150, 160, 172, 255), width=6)

    # --- RFID plaka yuvasi -------------------------------------------------
    rect = rfid_px_rect()
    track_rect(rect, "RFID yuvasi")
    draw.rectangle([rect[0] - 24, rect[1] - 24, rect[2] + 24, rect[3] + 10],
                   fill=GRAPHITE)
    draw.rectangle([rect[0] - 22, rect[1] - 22, rect[2] + 22, rect[3] + 8],
                   outline=(206, 216, 228, 255), width=3)
    draw.rectangle([rect[0], rect[1], rect[2], rect[3]], fill=(14, 18, 24, 255))

    # --- Alt kimlik satiri (iki satir: SN/CE + barkod) ---------------------
    f_sn = load_font(FONT_MONO, 24)
    draw_left_ink(draw, x0 + 60, 1548, "SN 40-TR-000913", f_sn, COOL_SOFT)
    draw_right_ink(draw, x1 - 60, 1548, "CE  EN 61000-6-3  -  RoHS", f_sn, COOL_SOFT)
    draw_barcode(draw, x0 + 60, 1578, 420, 32,
                 dark=(150, 162, 178, 255), light=BODY_LIGHT)


# ---------------------------------------------------------------- BANT-2: RFID plaka
def draw_rfid_band(draw):
    """RFID anten plakasi: es merkezli sarim izleri + cip + kart dalgasi."""
    x0, y0, x1, y1 = REGION_RFID
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(22, 28, 36, 255))

    # Anten sarimi: plakaya oturan es merkezli yuvarlatilmis dikdortgenler
    for i, (inset, col) in enumerate(((18, (188, 200, 214, 255)),
                                      (44, (150, 164, 180, 255)),
                                      (70, (120, 134, 150, 255)),
                                      (96, (96, 110, 126, 255)))):
        draw.rounded_rectangle([x0 + inset, y0 + inset, x1 - inset, y1 - inset],
                               radius=40, outline=col, width=5)

    # Ortada RFID cip blogu
    chip = (cx - 62, cy - 44, cx + 62, cy + 44)
    draw.rounded_rectangle([chip[0], chip[1], chip[2], chip[3]], radius=12,
                           fill=(44, 50, 58, 255), outline=(206, 216, 228, 255), width=4)
    for k in range(3):
        yy = chip[1] + 14 + k * 22
        draw.line([(chip[0] + 12, yy), (chip[2] - 12, yy)], fill=(120, 134, 150, 255), width=3)

    # Kart sembolu (sol ust kose)
    draw.rounded_rectangle([x0 + 132, y0 + 120, x0 + 300, y0 + 250], radius=12,
                           outline=(226, 168, 32, 255), width=5)
    draw.line([(x0 + 132, y0 + 186), (x0 + 300, y0 + 186)], fill=(226, 168, 32, 255), width=5)

    # Yay sembolu (sag ust kose): RFID dalgasi
    for r in (44, 74, 104):
        draw.arc([x1 - 132 - r, y0 + 150 - r, x1 - 132 + r, y0 + 150 + r],
                 start=-58, end=58, fill=(176, 196, 216, 255), width=5)

    f = load_font(FONT_MONO, 30)
    draw_center_ink(draw, cx, y1 - 108, "RFID  13.56 MHz", f, AMBER)
    f2 = load_font(FONT_MONO, 24)
    draw_center_ink(draw, cx, y1 - 64, "ISO/IEC 14443-A", f2, (146, 168, 192, 255))


# ---------------------------------------------------------------- BANT-3: LED halkasi
def draw_led_band(draw):
    """Emission halkasi: yesil Fresnel halkalari, radyal UV ile eslenir."""
    x0, y0, x1, y1 = REGION_LED
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(8, 26, 16, 255))

    # Halkanin okundugu band: 0.74..1.00 yaricap (3D halka orada oturuyor)
    draw.ellipse([cx - r * 0.995, cy - r * 0.995, cx + r * 0.995, cy + r * 0.995],
                 fill=(40, 170, 96, 255), outline=(120, 240, 158, 255), width=8)
    draw.ellipse([cx - r * 0.78, cy - r * 0.78, cx + r * 0.78, cy + r * 0.78],
                 fill=(14, 40, 26, 255), outline=(70, 200, 120, 255), width=6)
    draw.ellipse([cx - r * 0.60, cy - r * 0.60, cx + r * 0.60, cy + r * 0.60],
                 outline=(26, 90, 56, 255), width=5)


# ---------------------------------------------------------------- BANT-4: Renk alanlari
def draw_detail(draw):
    """Duz renk alanlari: dar ve uzun bant oldugu icin dikey dizilir."""
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    sw = 300
    labels = (("BODY", BODY_LIGHT, INK_TEXT),
              ("SIDE", BODY_MID, INK_TEXT),
              ("SLATE", PLATE_DARK_2, WHITE),
              ("METAL", (176, 186, 198, 255), INK_TEXT))
    for i, (lbl, col, ink) in enumerate(labels):
        sy = y0 + 20 + i * 300
        draw.rectangle([x0 + 16, sy, x0 + 16 + sw, sy + 220], fill=col,
                       outline=(132, 144, 158, 255), width=4)
        f = load_font(FONT_MONO, 28)
        draw_center_ink(draw, x0 + 16 + sw / 2.0, sy + 240, lbl, f, ink)


def generate_textures():
    img = Image.new("RGB", (ATLAS_W, ATLAS_H), (128, 132, 140))
    draw = ImageDraw.Draw(img)

    draw_cover(draw)
    draw_rfid_band(draw)
    draw_led_band(draw)
    draw_detail(draw)

    verify_layout()
    verify_sockets()
    report_ink_heights()

    img.save(ATLAS_PATH, "PNG")
    print(f"[OK] Atlas kaydedildi: {ATLAS_PATH} ({ATLAS_W}x{ATLAS_H})")
    print(f"[OK] Cover: {COVER_W * 1000:.0f} x {COVER_H * 1000:.0f} mm -> "
          f"{REGION_COVER[2] - REGION_COVER[0]} x {REGION_COVER[3] - REGION_COVER[1]} px "
          f"({PX_PER_MM:.2f} px/mm)")
    print(f"[OK] Metin bloklari: {len(_TEXT_BOXES)}  |  dekoratif blok: {len(_GRAPHIC_BOXES)}")


if __name__ == "__main__":
    generate_textures()





