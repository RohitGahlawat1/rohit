"""Generate a 1280x720 YouTube thumbnail for "Kesariya" (Arijit Singh).

Uses the official cover art as the background (falls back to a warm gradient
if the image cannot be downloaded), darkens it with a translucent overlay, and
overlays the song title with the artist name beneath, all within a 5% safe
margin.
"""

from __future__ import annotations

import io
import urllib.request

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN_X = int(WIDTH * 0.05)
MARGIN_Y = int(HEIGHT * 0.05)

TITLE = "KESARIYA"
ARTIST = "Arijit Singh"
OUTPUT = "thumbnail.png"

# Official cover art (Apple Music, high resolution).
COVER_URL = (
    "https://is1-ssl.mzstatic.com/image/thumb/Music112/v4/9f/13/ca/"
    "9f13ca3b-e533-03e0-f19a-f0aaa774581d/196589311191.jpg/1500x1500bb.jpg"
)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def gradient_background() -> Image.Image:
    """Warm saffron gradient used when the cover art is unavailable."""
    base = Image.new("RGB", (WIDTH, HEIGHT))
    top = (196, 78, 16)
    bottom = (28, 12, 4)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        for x in range(WIDTH):
            base.putpixel((x, y), (r, g, b))
    return base


def load_background() -> Image.Image:
    """Download the cover art and scale/crop it to fill the frame."""
    try:
        req = urllib.request.Request(COVER_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as exc:  # noqa: BLE001 - fall back to gradient on any failure
        print(f"Could not download cover art ({exc}); using gradient background.")
        return gradient_background()

    # Scale to cover, then center-crop to 1280x720.
    scale = max(WIDTH / img.width, HEIGHT / img.height)
    new_size = (round(img.width * scale), round(img.height * scale))
    img = img.resize(new_size, Image.LANCZOS)
    left = (img.width - WIDTH) // 2
    top = (img.height - HEIGHT) // 2
    return img.crop((left, top, left + WIDTH, top + HEIGHT))


def fit_font(
    path: str, text: str, max_width: int, start: int
) -> ImageFont.FreeTypeFont:
    """Return the largest font (<= start) whose text fits within max_width."""
    size = start
    while size > 10:
        font = ImageFont.truetype(path, size)
        if font.getlength(text) <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(path, 10)


def draw_text_with_shadow(draw, xy, text, font, fill=(255, 255, 255)):
    x, y = xy
    draw.text((x + 3, y + 3), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=fill)


def main() -> None:
    bg = load_background()

    # Darken the whole image, then add a stronger gradient at the bottom for
    # text legibility.
    bg = ImageEnhance.Brightness(bg).enhance(0.7)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rectangle([0, 0, WIDTH, HEIGHT], fill=(0, 0, 0, 60))
    for y in range(HEIGHT):
        if y > HEIGHT * 0.45:
            t = (y - HEIGHT * 0.45) / (HEIGHT * 0.55)
            odraw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, int(180 * t)))
    img = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")

    draw = ImageDraw.Draw(img)
    max_text_width = WIDTH - 2 * MARGIN_X

    title_font = fit_font(FONT_BOLD, TITLE, max_text_width, 220)
    artist_font = fit_font(FONT_REGULAR, ARTIST, max_text_width, 90)

    title_h = title_font.getbbox(TITLE)[3] - title_font.getbbox(TITLE)[1]
    artist_h = artist_font.getbbox(ARTIST)[3] - artist_font.getbbox(ARTIST)[1]
    gap = 24

    total_h = title_h + gap + artist_h
    y_title = HEIGHT - MARGIN_Y - total_h
    draw_text_with_shadow(
        draw, (MARGIN_X, y_title), TITLE, title_font, fill=(255, 173, 51)
    )
    y_artist = y_title + title_h + gap
    draw_text_with_shadow(
        draw, (MARGIN_X, y_artist), ARTIST, artist_font, fill=(255, 255, 255)
    )

    # Quantize to a 256-color palette to keep the PNG comfortably small
    # (well under both the 2 MB limit and the pre-commit large-file check).
    img = img.quantize(colors=256, method=Image.FASTOCTREE, dither=Image.NONE)
    img.save(OUTPUT, "PNG", optimize=True)
    print(f"Saved {OUTPUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
