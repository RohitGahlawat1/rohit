"""Generate a 1280x720 YouTube thumbnail for "Kesariya" (Arijit Singh).

Downloads the official Sony Music India promo still, crops it to focus on the
couple (avoiding the promo's own baked-in text), darkens it, and overlays the
song title and artist. Falls back to a saffron gradient if the image cannot be
downloaded.
"""

from __future__ import annotations

import io
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN = int(WIDTH * 0.05)  # 5% safe margin (64 px)
OUT = "thumbnail.png"

TITLE = "KESARIYA"
ARTIST = "Arijit Singh"

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Official Sony Music India upload still (high-resolution promo image).
IMAGE_URL = "https://i.ytimg.com/vi/BddP6PYo2gs/maxresdefault.jpg"


def load_background() -> Image.Image:
    """Return a 1280x720 RGB background, cover-cropped to the couple."""
    try:
        req = urllib.request.Request(IMAGE_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            src = Image.open(io.BytesIO(resp.read())).convert("RGB")
        return crop_cover(src)
    except Exception as exc:  # noqa: BLE001 - any failure -> gradient fallback
        print(f"Image download failed ({exc}); using gradient fallback.")
        return gradient_background()


def crop_cover(src: Image.Image) -> Image.Image:
    """Crop the left portion (the couple) to a 16:9 box, then scale to fill.

    The promo still bakes in title/credit/view-count text on the right half, so
    we anchor the crop to the left where the artists' faces are.
    """
    sw, sh = src.size
    target_ratio = WIDTH / HEIGHT
    # Focus box: left ~52% of the frame, anchored near the top (faces).
    box_w = int(sw * 0.52)
    box_h = int(box_w / target_ratio)
    left = int(sw * 0.02)
    top = int(sh * 0.03)
    if top + box_h > sh:
        top = sh - box_h
    if left + box_w > sw:
        left = sw - box_w
    cropped = src.crop((left, top, left + box_w, top + box_h))
    return cropped.resize((WIDTH, HEIGHT), Image.LANCZOS)


def gradient_background() -> Image.Image:
    """Saffron -> deep maroon vertical gradient fallback."""
    top_color = (255, 140, 30)
    bottom_color = (90, 20, 10)
    base = Image.new("RGB", (WIDTH, HEIGHT))
    px = base.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        for x in range(WIDTH):
            px[x, y] = (r, g, b)
    return base


def darken(img: Image.Image) -> Image.Image:
    """Lower brightness and lay a translucent dark overlay + bottom gradient."""
    img = ImageEnhance.Brightness(img).enhance(0.75)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 90))
    # Stronger darkening toward the bottom-left where the text sits.
    grad = Image.new("L", (1, HEIGHT), 0)
    gp = grad.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        gp[0, y] = int(150 * (t**1.5))
    grad = grad.resize((WIDTH, HEIGHT))
    bottom = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    bottom.putalpha(grad)
    out = img.convert("RGBA")
    out = Image.alpha_composite(out, overlay)
    out = Image.alpha_composite(out, bottom)
    return out.convert("RGB")


def fit_font(text: str, target_w: int, start: int, path: str) -> ImageFont.FreeTypeFont:
    """Largest font size at which `text` fits within target_w."""
    size = start
    while size > 10:
        font = ImageFont.truetype(path, size)
        if font.getlength(text) <= target_w:
            return font
        size -= 2
    return ImageFont.truetype(path, 10)


def draw_text(img: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(img)
    max_w = WIDTH - 2 * MARGIN

    title_font = fit_font(TITLE, max_w, 200, FONT_BOLD)
    artist_font = fit_font(ARTIST, max_w, 78, FONT_BOLD)

    tb = draw.textbbox((0, 0), TITLE, font=title_font)
    ab = draw.textbbox((0, 0), ARTIST, font=artist_font)
    title_h = tb[3] - tb[1]
    artist_h = ab[3] - ab[1]
    gap = 24

    block_h = title_h + gap + artist_h
    y = HEIGHT - MARGIN - block_h - (tb[1])  # anchor block bottom to safe margin
    x = MARGIN

    # Title with an accent bar above it.
    bar_y = y - 26
    draw.rectangle([x, bar_y, x + int(max_w * 0.28), bar_y + 10], fill=(255, 150, 40))

    _text_with_shadow(draw, (x, y), TITLE, title_font, (255, 255, 255))
    artist_y = y + title_h + gap
    _text_with_shadow(draw, (x, artist_y), ARTIST, artist_font, (255, 190, 120))
    return img


def _text_with_shadow(draw, pos, text, font, fill):
    x, y = pos
    for dx, dy in ((3, 3), (2, 2)):
        draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


def main() -> None:
    bg = load_background()
    bg = darken(bg)
    bg = draw_text(bg)
    assert bg.size == (WIDTH, HEIGHT)
    bg.save(OUT, "PNG", optimize=True)
    print(f"Saved {OUT} ({bg.size[0]}x{bg.size[1]})")


if __name__ == "__main__":
    main()
