"""Generate the 1280x720 YouTube thumbnail for "Kesariya".

Background: artwork from the official Sony Music India upload
(https://i.ytimg.com/vi/BddP6PYo2gs/maxresdefault.jpg), cropped to the
photographic left portion, scaled to fill the frame and darkened. Falls back to
a saffron gradient if the image cannot be downloaded.
"""

from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN = int(0.05 * WIDTH)
SOURCE_IMAGE = "https://i.ytimg.com/vi/BddP6PYo2gs/maxresdefault.jpg"
SOURCE_CROP = (20, 40, 655, 397)
TITLE = "KESARIYA"
SUBTITLE = "Arijit Singh"
CAPTION = "Brahmastra: Part One - Shiva  |  2022"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
OUTPUT = Path(__file__).with_name("thumbnail.png")
PALETTE_COLORS = 256


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size)


def gradient_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    top, bottom = (232, 122, 24), (54, 12, 44)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=tuple(round(t + (b - t) * ratio) for t, b in zip(top, bottom)),
        )
    return image


def scale_to_fill(image: Image.Image) -> Image.Image:
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.LANCZOS
    )
    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def background() -> Image.Image:
    try:
        request = urllib.request.Request(
            SOURCE_IMAGE, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            source = Image.open(io.BytesIO(response.read())).convert("RGB")
    except Exception as error:  # noqa: BLE001 - any failure falls back to gradient
        print(f"Falling back to gradient background: {error}")
        return gradient_background()
    return scale_to_fill(source.crop(SOURCE_CROP))


def draw_text(image: Image.Image) -> None:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 150))
    image.alpha_composite(overlay)

    draw = ImageDraw.Draw(image)
    title_font = load_font("DejaVuSans-Bold.ttf", 150)
    subtitle_font = load_font("DejaVuSans-Bold.ttf", 76)
    caption_font = load_font("DejaVuSans.ttf", 40)

    blocks = [
        (TITLE, title_font, (255, 255, 255, 255)),
        (SUBTITLE, subtitle_font, (255, 190, 92, 255)),
        (CAPTION, caption_font, (235, 235, 235, 255)),
    ]
    gaps = (28, 22)
    heights = [
        draw.textbbox((0, 0), text, font=font)[3]
        - draw.textbbox((0, 0), text, font=font)[1]
        for text, font, _ in blocks
    ]
    total = sum(heights) + sum(gaps)
    y = (HEIGHT - total) // 2

    for index, (text, font, fill) in enumerate(blocks):
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2 - bbox[0]
        draw.text(
            (x, y - bbox[1]),
            text,
            font=font,
            fill=fill,
            stroke_width=6 if index == 0 else 4,
            stroke_fill=(0, 0, 0, 210),
        )
        assert x >= MARGIN, f"'{text}' breaks the 5% safe margin"
        y += heights[index] + (gaps[index] if index < len(gaps) else 0)

    assert y <= HEIGHT - MARGIN, "text block breaks the bottom safe margin"


def main() -> None:
    image = background().convert("RGBA")
    draw_text(image)
    # A 256-colour palette keeps the PNG well under the repo's 500 KB file limit.
    palette = image.convert("RGB").quantize(
        colors=PALETTE_COLORS, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
    )
    palette.save(OUTPUT, format="PNG", optimize=True)
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KiB)")


if __name__ == "__main__":
    main()
