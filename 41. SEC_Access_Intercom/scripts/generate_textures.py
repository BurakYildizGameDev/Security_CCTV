"""
=============================================================================
Security CCTV Asset Production Suite - Asset 41
Asset Name: SEC_Access_Intercom (Goruntulu Kapi Interkomu)
Texture Generation Script v1 (2048 x 2048)

ATLAS YERLESIMI (piksel):
    BANT-1 COVER  (32, 32)    - (1032, 1907)  1000 x 1875 -> 80 x 150 mm (12.5 px/mm)
    BANT-2 SCREEN (1160, 32)  - (1960, 407)    800 x  375 -> 64 x 30 mm
    BANT-3 LENS   (1160, 440) - (1660, 940)    500 x  500 -> Ø14 lens
    BANT-4 GRILLE (1700, 440) - (2016, 756)    316 x  316 -> Ø34 izgara
    BANT-5 BUTTON (1160, 970) - (1560, 1370)   400 x  400 -> Ø26 dugme
    BANT-6 RENK   (1600, 970) - (2016, 2016)   duz renk alanlari

ON YUZ KURALI: +Y normaline bakan yuzler flip_u=True ile haritalanir; dunya +X
dokunun SOLUNA duser. cover_px() ayni eslemeyi kullanir.
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
REGION_COVER = (32, 32, 1032, 1907)          # 1000 x 1875 px -> 80 x 150 mm
REGION_SCREEN = (1160, 32, 1960, 407)        # 800 x 375 px  -> 64 x 30 mm
REGION_LENS = (1160, 440, 1660, 940)         # 500 x 500 px  -> Ø14 lens
REGION_GRILLE = (1700, 440, 2016, 756)       # 316 x 316 px  -> Ø34 izgara
REGION_BUTTON = (1160, 970, 1560, 1370)      # 400 x 400 px  -> Ø26 dugme
REGION_DETAIL = (1600, 970, 2016, 2016)      # duz renk alanlari

# ---------------------------------------------------------------- Geometri esleme (m)
COVER_W, COVER_H = 0.0800, 0.1500            # Housing on yuzu (80 x 150 mm)

LENS_X, LENS_Z, LENS_R = -0.0260, 0.0640, 0.0070
SCREEN_X, SCREEN_Z = 0.0, 0.0400
SCREEN_W, SCREEN_H = 0.0640, 0.0300
GRILLE_X, GRILLE_Z, GRILLE_R = 0.0, 0.0020, 0.0170
BTN_X, BTN_Z, BTN_R = 0.0, -0.0340, 0.0130
BEZEL_R_OUT = 0.0162                        # 3D dugme bilezigi (Button_Bezel)

# Duz renk UV noktalari (piksel)
PIX_FLAT_BODY = (1650, 1050)
PIX_FLAT_SIDE = (1900, 1050)
PIX_FLAT_DARK = (1650, 1300)
PIX_FLAT_SLATE = (1900, 1300)

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
    """On yuzdeki (X, Z) konumunu atlas pikseline cevirir (flip_u=True eslemesi)."""
    x0, y0, x1, y1 = REGION_COVER
    nx = (x_m + COVER_W / 2.0) / COVER_W
    nz = (z_m + COVER_H / 2.0) / COVER_H
    return (x1 - nx * (x1 - x0), y1 - nz * (y1 - y0))


def screen_px_rect():
    """Ekran yuvasinin atlas piksel dikdortgeni (sol, ust, sag, alt)."""
    ax, ay = cover_px(SCREEN_X + SCREEN_W / 2.0, SCREEN_Z + SCREEN_H / 2.0)
    bx, by = cover_px(SCREEN_X - SCREEN_W / 2.0, SCREEN_Z - SCREEN_H / 2.0)
    return (ax, ay, bx, by)


def verify_layout():
    """Metin kutularinin bant icinde kaldigini ve ust uste binmedigini dogrular."""
    regions = [REGION_COVER, REGION_SCREEN, REGION_LENS, REGION_GRILLE,
               REGION_BUTTON, REGION_DETAIL]
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
    """Dort 3D parcanin (ekran/lens/izgara/dugme) yuvalarinin cakismadigini dogrular."""
    problems = []
    mm_px = PX_PER_MM
    items = []

    s = screen_px_rect()
    items.append(("Ekran", (s[0], s[1], s[2], s[3]), "rect"))
    lx, ly = cover_px(LENS_X, LENS_Z)
    items.append(("Lens", (lx, ly), LENS_R * 1000.0 * mm_px))
    gx, gy = cover_px(GRILLE_X, GRILLE_Z)
    items.append(("Izgara", (gx, gy), GRILLE_R * 1000.0 * mm_px))
    bx, by = cover_px(BTN_X, BTN_Z)
    items.append(("Dugme bilezigi", (bx, by), BEZEL_R_OUT * 1000.0 * mm_px))

    cx0, cy0, cx1, cy1 = REGION_COVER
    for item in items:
        name = item[0]
        if item[2] == "rect":
            x0, y0, x1, y1 = item[1]
            if x0 < cx0 + 30 or y0 < cy0 + 30 or x1 > cx1 - 30 or y1 > cy1 - 30:
                problems.append(f"{name} on yuz cercevesini asiyor")
        else:
            (px, py), r = item[1], item[2]
            if (px - r < cx0 + 24 or py - r < cy0 + 24 or
                    px + r > cx1 - 24 or py + r > cy1 - 24):
                problems.append(f"{name} on yuz cercevesini asiyor")

    # Dikey sirasi: lens (ust) > ekran > izgara > dugme (alt) ve aralarinda bosluk
    order = [("Lens", ly, LENS_R * 1000.0 * mm_px),
             ("Ekran", s[3], 0),
             ("Izgara", gy, GRILLE_R * 1000.0 * mm_px),
             ("Dugme bilezigi", by, BEZEL_R_OUT * 1000.0 * mm_px)]
    for i in range(len(order) - 1):
        n1, y1, r1 = order[i]
        n2, y2, r2 = order[i + 1]
        gap = (y2 - r2) - (y1 + r1)
        if gap < 12:
            problems.append(f"{n1} ile {n2} arasi bosluk {gap:.0f} px (< 12)")
    # Ekran sol/sag kenari izgara capindan genis olmali (gorsel denge)
    if (s[2] - s[0]) < GRILLE_R * 2000.0 * mm_px:
        problems.append("ekran izgaradan dar")

    if problems:
        for p in problems:
            print("[SOCKET-FAIL] " + p)
        raise AssertionError(f"Yuva yerlesimi hatali: {len(problems)} sorun")
    print(f"[SOCKET-OK] ekran/lens/izgara/dugme yuvalari cakismasiz, dikey sira dogru")


def report_ink_heights():
    """En kucuk murekkep yuksekligini raporlar (render'da okunabilirlik tabani)."""
    if not _TEXT_BOXES:
        return
    heights = sorted((ty1 - ty0, txt) for (tx0, ty0, tx1, ty1, txt) in _TEXT_BOXES)
    print(f"[INK] En kucuk murekkep: {heights[0][0]:.0f} px "
          f"({heights[0][0] / PX_PER_MM:.2f} mm) -> '{heights[0][1]}'")
    print(f"[INK] En buyuk murekkep: {heights[-1][0]:.0f} px "
          f"({heights[-1][0] / PX_PER_MM:.2f} mm) -> '{heights[-1][1]}'")
    render_cover_px = (900.0 / 0.115) * COVER_W
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

    for yy in range(y0 + 4, y1, 9):
        draw.line([(x0, yy), (x1, yy)], fill=BRUSH_LINE)
    draw.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=FRAME_LINE, width=5)
    draw.rectangle([x0 + 24, y0 + 24, x1 - 24, y1 - 24],
                   outline=(210, 219, 230, 255), width=3)

    r_lens = LENS_R * 1000.0 * PX_PER_MM
    r_grille = GRILLE_R * 1000.0 * PX_PER_MM
    r_btn = BTN_R * 1000.0 * PX_PER_MM

    # --- Ust kimlik bandi (sol) --------------------------------------------
    LX = x0 + 52
    f_t = fit_font(draw, "SEC-VI 240", FONT_SANS, 470, 54, 32)
    f_s = fit_font(draw, "VIDEO DOOR INTERCOM", FONT_MONO, 470, 26, 18)
    f_x = load_font(FONT_MONO, 20)
    bb = draw_left_ink(draw, LX, 74, "SEC-VI 240", f_t, INK_DARK)
    bb = draw_left_ink(draw, LX, bb[3] + 12, "VIDEO DOOR INTERCOM", f_s, INK_TEXT)
    draw_left_ink(draw, LX, bb[3] + 10, "12 VDC   PoE CLASS 2", f_x, INK_SOFT)

    # --- Kamera lensi yuvasi (sag ust) -------------------------------------
    lcx, lcy = cover_px(LENS_X, LENS_Z)
    draw.ellipse([lcx - r_lens - 14, lcy - r_lens - 14,
                  lcx + r_lens + 14, lcy + r_lens + 14],
                 fill=GRAPHITE, outline=(206, 216, 228, 255), width=3)
    draw.ellipse([lcx - r_lens + 2, lcy - r_lens + 2,
                  lcx + r_lens - 2, lcy + r_lens - 2], fill=(10, 14, 20, 255))
    f_uv = load_font(FONT_MONO, 20)
    draw_center_ink(draw, lcx, lcy + r_lens + 20, "CAM", f_uv, INK_SOFT)

    # --- Ekran yuvasi ------------------------------------------------------
    rect = screen_px_rect()
    track_rect(rect, "Ekran yuvasi")
    draw.rectangle([rect[0] - 20, rect[1] - 20, rect[2] + 20, rect[3] + 20],
                   fill=PLATE_DARK, outline=(78, 90, 104, 255), width=4)
    # Cam boslugunda hafif ic yansima (3D ekran bu alani kaplar)
    draw.rectangle([rect[0], rect[1], rect[2], rect[3]], fill=(12, 22, 30, 255))

    # --- Izgara yuvasi -----------------------------------------------------
    gcx, gcy = cover_px(GRILLE_X, GRILLE_Z)
    draw.ellipse([gcx - r_grille - 16, gcy - r_grille - 16,
                  gcx + r_grille + 16, gcy + r_grille + 16],
                 fill=GRAPHITE, outline=(206, 216, 228, 255), width=3)
    draw.ellipse([gcx - r_grille + 2, gcy - r_grille + 2,
                  gcx + r_grille - 2, gcy + r_grille - 2], fill=(20, 24, 30, 255))

    # --- Izgaranin iki yanindaki teknik kisa kumeler ----------------------
    # Panelin orta bandi bos kalirsa hucre NCC'si "duz zemin" olup atlanir;
    # bu iki blok hem bilgi verir hem QA kapsamini artirir.
    f_l1 = load_font(FONT_MONO, 22)
    f_l2 = load_font(FONT_MONO, 19)
    left_bb = draw_left_ink(draw, x0 + 34, gcy - 40, "AUDIO", f_l1, INK_DARK)
    draw_left_ink(draw, x0 + 34, left_bb[3] + 8, "1 W / 8 OHM", f_l2, INK_SOFT)
    draw_left_ink(draw, x0 + 34, left_bb[3] + 34, "MEMS MIC", f_l2, INK_SOFT)
    right_bb = draw_right_ink(draw, x1 - 34, gcy - 40, "SUPPLY", f_l1, INK_DARK)
    draw_right_ink(draw, x1 - 34, right_bb[3] + 8, "12-24 VDC", f_l2, INK_SOFT)
    draw_right_ink(draw, x1 - 34, right_bb[3] + 34, "IP54", f_l2, INK_SOFT)

    # --- Dugme yuvasi: bilezik arkasi koyu cep -----------------------------
    # 3D bilezik (Button_Bezel) dugmeyi cevreledigi icin PARLAK oturma halkasi
    # cizilmez; cizilen halka egik bakista dugmeden kaymis gorunuyordu.
    # Cep, bilezik dis yaricapindan genis tutulur ki bilezik egik bakista
    # kaydiginda arkasinda hep koyu zemin kalsin (dikiş gorunmez).
    bcx, bcy = cover_px(BTN_X, BTN_Z)
    r_bez = BEZEL_R_OUT * 1000.0 * PX_PER_MM
    draw.ellipse([bcx - r_bez, bcy - r_bez,
                  bcx + r_bez, bcy + r_bez], fill=(14, 17, 22, 255))
    draw.ellipse([bcx - r_bez + 4, bcy - r_bez + 4,
                  bcx + r_bez - 4, bcy + r_bez - 4],
                 fill=(8, 10, 14, 255), outline=(96, 106, 120, 255), width=2)

    # --- "PUSH TO CALL" yonlendirmesi (dugmenin altinda) -------------------
    f_push = fit_font(draw, "PUSH TO CALL", FONT_SANS, 520, 34, 20)
    f_req = load_font(FONT_MONO, 22)
    bb = draw_center_ink(draw, bcx, bcy + r_bez + 24, "PUSH TO CALL", f_push, INK_DARK)
    draw_center_ink(draw, bcx, bb[3] + 10, "HOLD 1 s", f_req, INK_SOFT)

    # --- Alt kimlik satiri -------------------------------------------------
    f_sn = load_font(FONT_MONO, 22)
    draw_left_ink(draw, x0 + 52, y1 - 76, "SN 41-VI-002184", f_sn, INK_SOFT)
    draw_right_ink(draw, x1 - 52, y1 - 76, "CE  EN 61000-6-1", f_sn, INK_SOFT)
    draw_barcode(draw, x0 + 52, y1 - 62, 300, 30,
                 dark=(150, 162, 178, 255), light=BODY_LIGHT)


# ---------------------------------------------------------------- BANT-2: Ekran
def draw_screen_band(draw):
    """M_Screen dokusu: koyu LCD + kapi onizleme + OSD durum satiri."""
    x0, y0, x1, y1 = REGION_SCREEN
    draw.rectangle([x0, y0, x1, y1], fill=(10, 30, 44, 255))

    # Kapi onizleme cercevesi (yesilimsi gece gorusu tonu)
    draw.rectangle([x0 + 16, y0 + 16, x1 - 16, y1 - 16],
                   fill=(16, 52, 40, 255), outline=(72, 128, 104, 255), width=4)
    draw.rectangle([x0 + 96, y0 + 44, x1 - 96, y1 - 70],
                   outline=(150, 210, 180, 255), width=4)
    draw.line([(x1 // 2, y0 + 44), (x1 // 2, y1 - 70)],
              fill=(110, 170, 145, 255), width=3)
    draw.line([(x0 + 16, y1 - 70), (x1 - 16, y1 - 70)],
              fill=(120, 180, 155, 255), width=3)
    # Tarama cizgileri: 14 px periyot (render olceginde ~9 px) - daha ince
    # desenler yeniden orneklemede aliasing yapip korelasyonu bozar.
    for yy in range(y0 + 20, y1 - 20, 14):
        draw.line([(x0 + 18, yy), (x1 - 18, yy)], fill=(20, 62, 50, 255), width=2)

    # OSD durum satiri
    f = load_font(FONT_MONO, 26)
    draw_left_ink(draw, x0 + 30, y1 - 58, "CALL  00:12", f, (200, 245, 220, 255))
    draw_right_ink(draw, x1 - 30, y1 - 58, "REC", f, (255, 140, 120, 255))


# ---------------------------------------------------------------- BANT-3: Lens
def draw_lens_band(draw):
    x0, y0, x1, y1 = REGION_LENS
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(8, 12, 18, 255))
    for rr, col, wd in ((0.99, (120, 148, 176, 255), 10),
                        (0.86, (56, 78, 100, 255), 6),
                        (0.68, (40, 58, 76, 255), 5),
                        (0.48, (52, 74, 96, 255), 4)):
        draw.ellipse([cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr],
                     outline=col, width=wd)
    draw.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30],
                 fill=(6, 8, 12, 255), outline=(104, 130, 156, 255), width=5)


# ---------------------------------------------------------------- BANT-4: Izgara
def draw_grille_band(draw):
    """Hoparlor izgarasi: es merkezli delik halkalari (perforasyon)."""
    x0, y0, x1, y1 = REGION_GRILLE
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(26, 30, 36, 255))
    draw.ellipse([cx - r * 0.99, cy - r * 0.99, cx + r * 0.99, cy + r * 0.99],
                 outline=(176, 186, 198, 255), width=8)
    draw.ellipse([cx - r * 0.90, cy - r * 0.90, cx + r * 0.90, cy + r * 0.90],
                 outline=(88, 98, 110, 255), width=4)
    hole_r = r * 0.042
    for ring, count in ((0.72, 16), (0.52, 12), (0.32, 8), (0.14, 4)):
        for k in range(count):
            ang = (2.0 * math.pi * k / count) + (ring * 3.0)
            hx = cx + math.cos(ang) * r * ring
            hy = cy + math.sin(ang) * r * ring
            draw.ellipse([hx - hole_r, hy - hole_r, hx + hole_r, hy + hole_r],
                         fill=(8, 10, 13, 255), outline=(104, 114, 126, 255), width=2)
    draw.ellipse([cx - hole_r * 1.2, cy - hole_r * 1.2,
                  cx + hole_r * 1.2, cy + hole_r * 1.2],
                 fill=(8, 10, 13, 255), outline=(104, 114, 126, 255), width=2)


# ---------------------------------------------------------------- BANT-5: Dugme
def draw_button_band(draw):
    """M_Emission: aydinlatilmali cagri dugmesi (zil ikonu + yesil halka)."""
    x0, y0, x1, y1 = REGION_BUTTON
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    r = (x1 - x0) / 2.0
    draw.rectangle([x0, y0, x1, y1], fill=(10, 46, 26, 255))
    draw.ellipse([cx - r * 0.98, cy - r * 0.98, cx + r * 0.98, cy + r * 0.98],
                 fill=(44, 178, 100, 255), outline=(126, 244, 162, 255), width=10)
    draw.ellipse([cx - r * 0.72, cy - r * 0.72, cx + r * 0.72, cy + r * 0.72],
                 fill=(24, 92, 56, 255), outline=(90, 214, 134, 255), width=5)

    # Zil ikonu (beyaz): kubbe + etek + clapper
    bw, bh = r * 0.20, r * 0.26
    draw.pieslice([cx - bw * 2.0, cy - bh * 2.0, cx + bw * 2.0, cy + bh * 1.2],
                  start=180, end=360, fill=(238, 255, 244, 255))
    draw.rectangle([cx - bw * 2.0, cy - bh * 0.4, cx + bw * 2.0, cy + bh * 0.12],
                   fill=(238, 255, 244, 255))
    draw.rectangle([cx - bw * 2.4, cy + bh * 0.12, cx + bw * 2.4, cy + bh * 0.34],
                   fill=(238, 255, 244, 255))
    draw.ellipse([cx - bw * 0.5, cy + bh * 0.44, cx + bw * 0.5, cy + bh * 1.04],
                 fill=(238, 255, 244, 255))

    # Dis isinlar (aktif cagri)
    for sx in (-1, 1):
        for rad in (0.62, 0.78):
            rr = r * rad
            draw.arc([cx - rr, cy - rr, cx + rr, cy + rr],
                     start=(158 if sx < 0 else -22), end=(202 if sx < 0 else 22),
                     fill=(150, 240, 178, 255), width=6)


# ---------------------------------------------------------------- BANT-6: Renk
def draw_detail(draw):
    x0, y0, x1, y1 = REGION_DETAIL
    draw.rectangle([x0, y0, x1, y1], fill=BODY_LIGHT)
    sw = 320
    labels = (("BODY", BODY_LIGHT, INK_TEXT),
              ("SIDE", BODY_MID, INK_TEXT),
              ("SLATE", PLATE_DARK_2, WHITE),
              ("GRILLE", (26, 30, 36, 255), WHITE))
    for i, (lbl, col, ink) in enumerate(labels):
        sy = y0 + 20 + i * 250
        draw.rectangle([x0 + 16, sy, x0 + 16 + sw, sy + 180], fill=col,
                       outline=(132, 144, 158, 255), width=4)
        f = load_font(FONT_MONO, 26)
        draw_center_ink(draw, x0 + 16 + sw / 2.0, sy + 198, lbl, f, ink)


def generate_textures():
    img = Image.new("RGB", (ATLAS_W, ATLAS_H), (128, 132, 140))
    draw = ImageDraw.Draw(img)

    draw_cover(draw)
    draw_screen_band(draw)
    draw_lens_band(draw)
    draw_grille_band(draw)
    draw_button_band(draw)
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





