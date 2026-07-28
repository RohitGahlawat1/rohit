"""Generate the 1280x720 YouTube thumbnail for "Kesariya"."""

import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN = int(0.05 * WIDTH)
TITLE = "KESARIYA"
SUBTITLE = "Arijit Singh  |  Brahmastra (2022)"
COVER_URL = "https://img.youtube.com/vi/BddP6PYo2gs/maxresdefault.jpg"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUTPUT = Path(__file__).with_name("thumbnail.png")


def load_background() -> Image.Image:
    try:
        with urllib.request.urlopen(COVER_URL, timeout=30) as response:
            image = Image.open(BytesIO(response.read())).convert("RGB")
    except Exception:
        return gradient_background()
    return fill_frame(image)


def fill_frame(image: Image.Image) -> Image.Image:
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.LANCZOS
    )
    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def gradient_background() -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    start, end = (28, 12, 40), (222, 108, 30)
    for y in range(HEIGHT):
        ratio = y / (HEIGHT - 1)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=tuple(round(s + (e - s) * ratio) for s, e in zip(start, end)),
        )
    return image


def darken(image: Image.Image) -> Image.Image:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 140))
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def fit_font(
    text: str, path: str, max_width: int, start_size: int
) -> ImageFont.FreeTypeFont:
    size = start_size
    while size > 12:
        font = ImageFont.truetype(path, size)
        if font.getbbox(text)[2] - font.getbbox(text)[0] <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(path, 12)


def draw_centered(
    draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, y: int
) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    x = (WIDTH - (box[2] - box[0])) // 2 - box[0]
    for dx, dy in ((-3, 3), (3, 3), (-3, -3), (3, -3)):
        draw.text((x + dx, y + dy), text, font=font, fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=(255, 255, 255))


def main() -> None:
    image = darken(load_background())
    draw = ImageDraw.Draw(image)
    usable = WIDTH - 2 * MARGIN
    title_font = fit_font(TITLE, FONT_BOLD, usable, 190)
    subtitle_font = fit_font(SUBTITLE, FONT_REGULAR, usable, 64)
    draw_centered(draw, TITLE, title_font, 250)
    draw_centered(draw, SUBTITLE, subtitle_font, 250 + title_font.size + 40)
    palette = image.convert("RGB").quantize(
        colors=128, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
    )
    palette.save(OUTPUT, "PNG", optimize=True)


if __name__ == "__main__":
    main()
