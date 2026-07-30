"""Generate the 1280x720 YouTube thumbnail for "Kesariya"."""

import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN = int(0.05 * WIDTH)
OUT = Path(__file__).with_name("thumbnail.png")
BACKGROUND_URL = "https://i.ytimg.com/vi/BddP6PYo2gs/maxresdefault.jpg"
TITLE = "KESARIYA"
SUBTITLE = "Arijit Singh  |  Brahmastra (2022)"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def load_background() -> Image.Image:
    try:
        with urllib.request.urlopen(BACKGROUND_URL, timeout=30) as resp:
            img = Image.open(BytesIO(resp.read())).convert("RGB")
    except Exception:
        return gradient_background()
    return fill_frame(img)


def fill_frame(img: Image.Image) -> Image.Image:
    scale = max(WIDTH / img.width, HEIGHT / img.height)
    img = img.resize(
        (round(img.width * scale), round(img.height * scale)), Image.LANCZOS
    )
    left = (img.width - WIDTH) // 2
    top = (img.height - HEIGHT) // 2
    return img.crop((left, top, left + WIDTH, top + HEIGHT))


def gradient_background() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    start, end = (24, 12, 40), (214, 120, 32)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=tuple(round(a + (b - a) * t) for a, b in zip(start, end)),
        )
    return img


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / name), size)


def fit_font(draw, text, name, size, max_width):
    while size > 12:
        f = font(name, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(name, 12)


def main() -> None:
    img = ImageEnhance.Brightness(load_background()).enhance(0.75)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 120))
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(img)

    max_width = WIDTH - 2 * MARGIN
    title_font = fit_font(draw, TITLE, "DejaVuSans-Bold.ttf", 170, max_width)
    sub_font = fit_font(draw, SUBTITLE, "DejaVuSans-Bold.ttf", 60, max_width)

    title_h = draw.textbbox((0, 0), TITLE, font=title_font)[3]
    sub_h = draw.textbbox((0, 0), SUBTITLE, font=sub_font)[3]
    gap = 30
    top = (HEIGHT - (title_h + gap + sub_h)) // 2

    draw.text(
        (WIDTH // 2, top),
        TITLE,
        font=title_font,
        fill=(255, 236, 205),
        anchor="ma",
        stroke_width=6,
        stroke_fill=(0, 0, 0),
    )
    draw.text(
        (WIDTH // 2, top + title_h + gap),
        SUBTITLE,
        font=sub_font,
        fill=(255, 255, 255),
        anchor="ma",
        stroke_width=4,
        stroke_fill=(0, 0, 0),
    )

    # Palette-quantise so the PNG stays well under the repo's 500 KB file limit.
    img.convert("RGB").quantize(
        colors=128, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
    ).save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {img.size}")


if __name__ == "__main__":
    main()
