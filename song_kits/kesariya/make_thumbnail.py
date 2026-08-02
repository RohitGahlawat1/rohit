"""Generate the 1280x720 YouTube thumbnail for "Kesariya"."""

import io
import pathlib
import urllib.request

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN = int(0.05 * WIDTH)
TITLE = "KESARIYA"
SUBTITLE = "Arijit Singh  |  Brahmastra (2022)"
COVER_URL = (
    "https://is1-ssl.mzstatic.com/image/thumb/Music112/v4/9f/13/ca/"
    "9f13ca3b-e533-03e0-f19a-f0aaa774581d/196589311191.jpg/1500x1500bb.jpg"
)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUTPUT = pathlib.Path(__file__).with_name("thumbnail.png")


def gradient_background() -> Image.Image:
    base = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(base)
    top, bottom = (28, 12, 40), (196, 84, 22)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return base


def cover_background() -> Image.Image | None:
    try:
        request = urllib.request.Request(
            COVER_URL, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
    except Exception:
        return None
    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        return None
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.LANCZOS
    )
    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def fit_font(
    path: str, text: str, max_width: int, start_size: int
) -> ImageFont.FreeTypeFont:
    size = start_size
    while size > 12:
        font = ImageFont.truetype(path, size)
        if font.getbbox(text)[2] - font.getbbox(text)[0] <= max_width:
            return font
        size -= 2
    return ImageFont.truetype(path, 12)


def main() -> None:
    background = cover_background() or gradient_background()

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle([(0, 0), (WIDTH, HEIGHT)], fill=(0, 0, 0, 130))

    image = Image.alpha_composite(background.convert("RGBA"), overlay)
    draw = ImageDraw.Draw(image)

    usable = WIDTH - 2 * MARGIN
    title_font = fit_font(FONT_BOLD, TITLE, usable, 190)
    subtitle_font = fit_font(FONT_REGULAR, SUBTITLE, usable, 62)

    title_box = draw.textbbox((0, 0), TITLE, font=title_font)
    subtitle_box = draw.textbbox((0, 0), SUBTITLE, font=subtitle_font)
    gap = 30
    block_height = (
        (title_box[3] - title_box[1]) + gap + (subtitle_box[3] - subtitle_box[1])
    )
    title_y = (HEIGHT - block_height) // 2 - title_box[1]
    subtitle_y = (
        title_y + title_box[1] + (title_box[3] - title_box[1]) + gap - subtitle_box[1]
    )

    draw.text(
        (WIDTH // 2, title_y),
        TITLE,
        font=title_font,
        fill=(255, 214, 140),
        anchor="ma",
        stroke_width=6,
        stroke_fill=(0, 0, 0),
    )
    draw.text(
        (WIDTH // 2, subtitle_y),
        SUBTITLE,
        font=subtitle_font,
        fill=(255, 255, 255),
        anchor="ma",
        stroke_width=3,
        stroke_fill=(0, 0, 0),
    )

    flat = image.convert("RGB").quantize(
        colors=128, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
    )
    flat.save(OUTPUT, "PNG", optimize=True)
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
