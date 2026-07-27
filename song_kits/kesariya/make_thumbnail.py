"""Generate the 1280x720 YouTube thumbnail for "Kesariya"."""

import io
import os
import urllib.request

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
MARGIN = int(0.05 * WIDTH)
BACKGROUND_URL = (
    "https://is1-ssl.mzstatic.com/image/thumb/Music112/v4/9f/13/ca/"
    "9f13ca3b-e533-03e0-f19a-f0aaa774581d/196589311191.jpg/2000x2000bb.jpg"
)
FALLBACK_URL = "https://i.ytimg.com/vi/BddP6PYo2gs/maxresdefault.jpg"
TITLE = "KESARIYA"
SUBTITLE = "Arijit Singh  |  Brahmastra (2022)"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "thumbnail.png")


def gradient_background() -> Image.Image:
    base = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(base)
    top = (196, 92, 24)
    bottom = (28, 12, 40)
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return base


def fetch_background() -> Image.Image:
    for url in (BACKGROUND_URL, FALLBACK_URL):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=30) as response:
                image = Image.open(io.BytesIO(response.read())).convert("RGB")
        except Exception:
            continue
        return cover_crop(image)
    return gradient_background()


def cover_crop(image: Image.Image) -> Image.Image:
    scale = max(WIDTH / image.width, HEIGHT / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)), Image.LANCZOS
    )
    left = (resized.width - WIDTH) // 2
    top = (resized.height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


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


def draw_text(draw: ImageDraw.ImageDraw, xy, text, font, fill=(255, 255, 255)) -> None:
    draw.text(xy, text, font=font, fill=fill, stroke_width=6, stroke_fill=(0, 0, 0))


def main() -> None:
    base = fetch_background()

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([(0, 0), (WIDTH, HEIGHT)], fill=(0, 0, 0, 110))
    for i in range(HEIGHT // 2, HEIGHT):
        alpha = int(150 * (i - HEIGHT // 2) / (HEIGHT // 2))
        overlay_draw.line([(0, i), (WIDTH, i)], fill=(0, 0, 0, alpha))
    image = Image.alpha_composite(base.convert("RGBA"), overlay)

    draw = ImageDraw.Draw(image)
    usable = WIDTH - 2 * MARGIN
    title_font = fit_font(TITLE, FONT_BOLD, usable, 190)
    subtitle_font = fit_font(SUBTITLE, FONT_REGULAR, usable, 64)

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

    draw_text(draw, (MARGIN, title_y), TITLE, title_font)
    draw_text(draw, (MARGIN, subtitle_y), SUBTITLE, subtitle_font)

    palette = image.convert("RGB").quantize(
        colors=128, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
    )
    palette.save(OUTPUT, "PNG", optimize=True)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
