"""Generate the 1280x720 YouTube thumbnail for "Kesariya"."""

import io
import pathlib
import urllib.request

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN = int(0.05 * WIDTH)
OUT = pathlib.Path(__file__).with_name("thumbnail.png")

# Cover art frame from the official Sony Music India upload of "Kesariya".
SOURCE_IMAGE = "https://i.ytimg.com/vi/BddP6PYo2gs/maxresdefault.jpg"
# Region of the source frame holding the artwork photo (without promo overlays).
SOURCE_CROP = (0, 0, 640, 720)

TITLE = "KESARIYA"
SUBTITLE = "Arijit Singh"
CAPTION = "Brahmastra: Part One - Shiva (2022)"

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def gradient_background() -> Image.Image:
    base = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(base)
    top, bottom = (34, 12, 4), (214, 96, 22)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return base


def fetch_background() -> Image.Image:
    request = urllib.request.Request(
        SOURCE_IMAGE, headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        image = Image.open(io.BytesIO(response.read())).convert("RGB")
    return image.crop(SOURCE_CROP)


def fill_frame(image: Image.Image, vertical_anchor: float = 0.3) -> Image.Image:
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.LANCZOS
    )
    left = (resized.width - WIDTH) // 2
    top = int((resized.height - HEIGHT) * vertical_anchor)
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def darken(image: Image.Image) -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 140))
    shade = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    shade_draw = ImageDraw.Draw(shade)
    for y in range(HEIGHT):
        alpha = int(150 * max(0.0, (y - HEIGHT * 0.35) / (HEIGHT * 0.65)))
        shade_draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(
        Image.alpha_composite(image.convert("RGBA"), overlay), shade
    ).convert("RGB")


def draw_text(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype(BOLD, 150)
    while draw.textlength(TITLE, font=title_font) > WIDTH - 2 * MARGIN:
        title_font = ImageFont.truetype(BOLD, title_font.size - 4)
    subtitle_font = ImageFont.truetype(BOLD, 64)
    caption_font = ImageFont.truetype(REGULAR, 34)

    blocks = [
        (TITLE, title_font, (255, 255, 255)),
        (SUBTITLE, subtitle_font, (255, 176, 59)),
        (CAPTION, caption_font, (235, 235, 235)),
    ]
    heights = [
        font.getbbox(text)[3] - font.getbbox(text)[1] for text, font, _ in blocks
    ]
    gaps = [28, 20]
    total = sum(heights) + sum(gaps)
    y = HEIGHT - MARGIN - total

    for index, (text, font, color) in enumerate(blocks):
        draw.text(
            (MARGIN, y),
            text,
            font=font,
            fill=color,
            anchor="la",
            stroke_width=max(2, font.size // 20),
            stroke_fill=(0, 0, 0),
        )
        y += heights[index] + (gaps[index] if index < len(gaps) else 0)
    return image


def main() -> None:
    try:
        background = fill_frame(fetch_background())
    except Exception as error:  # noqa: BLE001 - fall back to a gradient background
        print(f"Falling back to gradient background: {error}")
        background = gradient_background()
    image = draw_text(darken(background))
    assert image.size == (WIDTH, HEIGHT)
    # Palette-quantised PNG keeps the file well under the repo's 500 KB limit.
    image.quantize(
        colors=256, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
    ).save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KiB)")


if __name__ == "__main__":
    main()
