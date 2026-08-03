"""Generate a mock-up demo GIF from a scripted scenario.

`embedded-iot-mentor-demo.gif` at the repository root is a real screen
recording of the skill and stays the one linked from the README. This script
exists for the case that recording isn't available -- a fresh contributor
without a live Claude session, a quick illustration for an issue or the
landing page -- and produces a synthetic mock-up instead, built from the
sheep-farmer scenario in
`embedded-iot-mentor/examples/worked-examples.md#scenario-d`. It has no
bearing on the skill's behaviour; it only draws a picture of it.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 640
OUTPUT = Path("assets/skill-demo-mockup.gif")


def get_font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


TITLE_FONT = get_font(36)
SUBTITLE_FONT = get_font(24)
BODY_FONT = get_font(22)
SMALL_FONT = get_font(18)


def draw_background(draw: ImageDraw.ImageDraw, step: int) -> None:
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill="#07111f")
    draw.rectangle((30, 30, WIDTH - 30, HEIGHT - 30), outline="#1e293b", width=4)
    for y in range(60, HEIGHT - 60, 80):
        draw.line((40, y, WIDTH - 40, y), fill=(255, 255, 255, 20), width=1)

    bar_width = 180 + step * 90
    draw.rounded_rectangle((70, 118, 70 + bar_width, 138), radius=10, fill="#22c55e")


def draw_frame(step: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#07111f")
    draw = ImageDraw.Draw(img)
    draw_background(draw, step)

    draw.text((80, 40), "Embedded / IoT Mentor", font=TITLE_FONT, fill="#f8fafc")
    draw.text((80, 80), "MVP-first guidance from idea to breadboard", font=SUBTITLE_FONT, fill="#94a3b8")

    # left speech bubble — the farmer's brief
    draw.rounded_rectangle((80, 155, 560, 300), radius=24, fill="#e2e8f0", outline="#94a3b8", width=2)
    draw.text((110, 180), "User", font=BODY_FONT, fill="#0f172a")
    draw.text((110, 215), "\u201cSix sensing points across a meadow,", font=SMALL_FONT, fill="#334155")
    draw.text((110, 241), "soil moisture and nitrogen, furthest one", font=SMALL_FONT, fill="#334155")
    draw.text((110, 267), "is 400 m out. No coding experience.\u201d", font=SMALL_FONT, fill="#334155")

    # right speech bubble — the skill's reply
    draw.rounded_rectangle((640, 155, 1120, 335), radius=24, fill="#1d4ed8", outline="#38bdf8", width=2)
    draw.text((670, 180), "Mentor", font=BODY_FONT, fill="#f8fafc")
    draw.text((670, 215), "No cheap probe measures nitrogen honestly", font=SMALL_FONT, fill="#dbeafe")
    draw.text((670, 241), "400 m out picks LoRa over Wi-Fi", font=SMALL_FONT, fill="#dbeafe")
    draw.text((670, 267), "\"No code\" picks ready-made firmware", font=SMALL_FONT, fill="#dbeafe")
    draw.text((670, 293), "Wet meadow picks the enclosure", font=SMALL_FONT, fill="#dbeafe")

    # recommendation strip
    draw.rounded_rectangle((80, 380, 1120, 560), radius=24, fill="#0f172a", outline="#334155", width=2)
    draw.text((110, 410), "MVP plan", font=BODY_FONT, fill="#f8fafc")

    steps = [
        ("6x LoRa soil-moisture node", "Ready-made firmware, no code"),
        ("LoRaWAN gateway at the house", "Covers the 400 m node"),
        ("Home Assistant dashboard", "History + moisture alert"),
    ]

    box_x, box_y, box_w, box_h = 110, 445, 300, 80
    for index, (title, subtitle) in enumerate(steps):
        x = box_x + index * 320
        draw.rounded_rectangle((x, box_y, x + box_w, box_y + box_h), radius=16, fill="#111827", outline="#475569", width=2)
        draw.text((x + 18, box_y + 16), title, font=SMALL_FONT, fill="#f8fafc")
        draw.text((x + 18, box_y + 44), subtitle, font=ImageFont.load_default(), fill="#94a3b8")

    if step >= 2:
        highlight = 110 + min(step - 2, 2) * 320
        draw.rounded_rectangle((highlight, 445, highlight + 300, 525), radius=16, fill="#14532d", outline="#4ade80", width=3)

    if step <= 2:
        draw.text((100, 575), "Nitrogen half of the brief is declined up front.", font=SMALL_FONT, fill="#cbd5e1")
    elif step <= 4:
        draw.text((100, 575), "The board is the last thing decided, not the first.", font=SMALL_FONT, fill="#cbd5e1")
    else:
        draw.text((100, 575), "Stops at a working breadboard MVP by design.", font=SMALL_FONT, fill="#cbd5e1")

    return img


def build_gif() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [draw_frame(step) for step in range(8)]
    frames[0].save(
        OUTPUT,
        save_all=True,
        append_images=frames[1:],
        duration=700,
        loop=0,
        optimize=False,
    )


if __name__ == "__main__":
    build_gif()
    print(f"Created {OUTPUT}")
