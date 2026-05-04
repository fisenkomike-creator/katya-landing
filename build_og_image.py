"""
Generates og-image.png (1200x630) matching the site's aesthetic:
deep navy gradient background, blue/silver accents, Vologda-lace-inspired
ornaments, elegant italic serif "Катя" wordmark, soft subtitle.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os

W, H = 1200, 630
OUT = os.path.join(os.path.dirname(__file__), "og-image.png")

# --- palette (mirrors site) ---
INK_DEEP   = (11, 15, 22)       # #0B0F16
INK_MID    = (20, 26, 36)       # #141A24
INK_RISE   = (30, 42, 58)       # #1E2A3A
BLUE_SOFT  = (232, 240, 248)    # #E8F0F8
BLUE       = (168, 197, 224)    # #A8C5E0
BLUE_DEEP  = (110, 148, 184)    # #6E94B8
SILVER     = (201, 205, 211)    # #C9CDD3

def rgba(c, a):
    return (c[0], c[1], c[2], a)

# --- radial gradient background (like favicon) ---
img = Image.new("RGB", (W, H), INK_DEEP)
px = img.load()
cx, cy = W // 2, int(H * 0.40)
maxR = math.hypot(max(cx, W - cx), max(cy, H - cy))
for y in range(H):
    for x in range(W):
        r = math.hypot(x - cx, y - cy) / maxR
        # piecewise blend: INK_RISE -> INK_MID -> INK_DEEP
        if r < 0.55:
            t = r / 0.55
            c0, c1 = INK_RISE, INK_MID
        else:
            t = min(1.0, (r - 0.55) / 0.45)
            c0, c1 = INK_MID, INK_DEEP
        px[x, y] = (
            int(c0[0] + (c1[0] - c0[0]) * t),
            int(c0[1] + (c1[1] - c0[1]) * t),
            int(c0[2] + (c1[2] - c0[2]) * t),
        )

# --- soft glow behind the title ---
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r, a in [(380, 28), (260, 36), (160, 42)]:
    gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=rgba(BLUE, a))
glow = glow.filter(ImageFilter.GaussianBlur(60))
img = Image.alpha_composite(img.convert("RGBA"), glow)

draw = ImageDraw.Draw(img, "RGBA")

# --- decorative outer frame (lace-inspired thin double border) ---
M = 28
draw.rectangle([M, M, W - M - 1, H - M - 1], outline=rgba(BLUE, 70), width=1)
M2 = 38
draw.rectangle([M2, M2, W - M2 - 1, H - M2 - 1], outline=rgba(BLUE, 35), width=1)

# --- Vologda-lace inspired side ornaments (vertical chains of arcs + dots) ---
def lace_column(x_center, color=BLUE, alpha=120):
    # repeating motif: dot — arc — diamond — arc — dot
    spacing = 36
    y = 70
    while y < H - 70:
        # tiny diamond
        d = 4
        draw.polygon(
            [(x_center, y - d), (x_center + d, y), (x_center, y + d), (x_center - d, y)],
            fill=rgba(color, alpha),
        )
        # short arc above (open ring half)
        draw.arc(
            [x_center - 9, y - 22, x_center + 9, y - 4],
            start=200, end=340, fill=rgba(color, int(alpha * 0.85)), width=1,
        )
        # short arc below
        draw.arc(
            [x_center - 9, y + 4, x_center + 9, y + 22],
            start=20, end=160, fill=rgba(color, int(alpha * 0.85)), width=1,
        )
        # tiny dots flanking
        draw.ellipse([x_center - 16, y - 1, x_center - 14, y + 1], fill=rgba(color, alpha))
        draw.ellipse([x_center + 14, y - 1, x_center + 16, y + 1], fill=rgba(color, alpha))
        y += spacing

lace_column(70, BLUE, 110)
lace_column(W - 70, BLUE, 110)

# --- top + bottom finial: small lace medallion ---
def medallion(cx_, cy_, R=22, color=BLUE, alpha=130):
    # outer ring
    draw.ellipse([cx_ - R, cy_ - R, cx_ + R, cy_ + R],
                 outline=rgba(color, alpha), width=1)
    # inner ring
    draw.ellipse([cx_ - R + 7, cy_ - R + 7, cx_ + R - 7, cy_ + R - 7],
                 outline=rgba(color, int(alpha * 0.8)), width=1)
    # 8 spokes
    for k in range(8):
        a = k * math.pi / 4
        x1 = cx_ + math.cos(a) * (R - 7)
        y1 = cy_ + math.sin(a) * (R - 7)
        x2 = cx_ + math.cos(a) * (R + 6)
        y2 = cy_ + math.sin(a) * (R + 6)
        draw.line([x1, y1, x2, y2], fill=rgba(color, int(alpha * 0.9)), width=1)
    # center dot
    draw.ellipse([cx_ - 2, cy_ - 2, cx_ + 2, cy_ + 2], fill=rgba(BLUE_SOFT, 220))

medallion(W // 2, 80, R=20)
medallion(W // 2, H - 80, R=20)

# --- horizontal hairlines flanking eyebrow text ---
def hairline(y, x_from, x_to, color=BLUE, alpha=120):
    draw.line([(x_from, y), (x_to, y)], fill=rgba(color, alpha), width=1)

# --- typography ---
FONTS = r"C:\Windows\Fonts"
font_title   = ImageFont.truetype(os.path.join(FONTS, "cambriai.ttf"), 240)
font_eyebrow = ImageFont.truetype(os.path.join(FONTS, "cambria.ttc"),  22)
font_sub     = ImageFont.truetype(os.path.join(FONTS, "georgiai.ttf"), 28)
font_url     = ImageFont.truetype(os.path.join(FONTS, "cambria.ttc"),  18)

# Eyebrow label
eyebrow = "РУССКОЕ  ИМЯ"
eb_bbox = draw.textbbox((0, 0), eyebrow, font=font_eyebrow)
eb_w = eb_bbox[2] - eb_bbox[0]
eb_y = 150
draw.text(((W - eb_w) // 2, eb_y), eyebrow, font=font_eyebrow,
          fill=rgba(BLUE, 220))
# flanking hairlines
hairline(eb_y + 16, (W - eb_w) // 2 - 90, (W - eb_w) // 2 - 14, BLUE, 140)
hairline(eb_y + 16, (W + eb_w) // 2 + 14, (W + eb_w) // 2 + 90, BLUE, 140)

# Title "Катя" with vertical gradient fill (BLUE_SOFT -> BLUE -> BLUE_DEEP)
title_text = "Катя"
tb = draw.textbbox((0, 0), title_text, font=font_title)
tw, th = tb[2] - tb[0], tb[3] - tb[1]
tx = (W - tw) // 2 - tb[0]
ty = 200 - tb[1]

# render title to a mask then apply vertical gradient
mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).text((tx, ty), title_text, font=font_title, fill=255)

grad = Image.new("RGB", (W, H), BLUE)
gpx = grad.load()
y0 = ty + tb[1]
y1 = ty + tb[3]
for y in range(y0, y1 + 1):
    t = (y - y0) / max(1, (y1 - y0))
    if t < 0.55:
        u = t / 0.55
        c0, c1 = BLUE_SOFT, BLUE
    else:
        u = (t - 0.55) / 0.45
        c0, c1 = BLUE, BLUE_DEEP
    color = (
        int(c0[0] + (c1[0] - c0[0]) * u),
        int(c0[1] + (c1[1] - c0[1]) * u),
        int(c0[2] + (c1[2] - c0[2]) * u),
    )
    for x in range(W):
        gpx[x, y] = color

# soft glow behind glyphs
glow_mask = mask.filter(ImageFilter.GaussianBlur(14))
glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
glow_layer.paste((BLUE[0], BLUE[1], BLUE[2], 110), mask=glow_mask)
img = Image.alpha_composite(img, glow_layer)

# composite the gradient-filled title onto img
title_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
title_layer.paste(grad, mask=mask)
img = Image.alpha_composite(img, title_layer)

draw = ImageDraw.Draw(img, "RGBA")

# Subtitle (italic, two lines centered)
sub_lines = [
    "Небо первого снега, шёпот свечи",
    "и сталь императорской воли.",
]
sy = ty + tb[3] + 36
for line in sub_lines:
    sb = draw.textbbox((0, 0), line, font=font_sub)
    sw = sb[2] - sb[0]
    draw.text(((W - sw) // 2, sy), line, font=font_sub, fill=rgba(BLUE_SOFT, 230))
    sy += 40

# small floating sparks (matches favicon dots)
draw.ellipse([170, 110, 174, 114], fill=rgba(BLUE_SOFT, 220))
draw.ellipse([W - 200, H - 150, W - 196, H - 146], fill=rgba(BLUE, 200))
draw.ellipse([W - 240, 130, W - 237, 133], fill=rgba(BLUE_SOFT, 180))
draw.ellipse([200, H - 180, 203, H - 177], fill=rgba(BLUE, 180))

img.convert("RGB").save(OUT, "PNG", optimize=True)
print(f"wrote {OUT}  ({os.path.getsize(OUT)} bytes)")
