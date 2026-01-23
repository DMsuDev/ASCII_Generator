"""Utilities to convert ASCII/ANSI frames into images and images into video.

This module provides two main helpers used by the CLI:
- `frames_to_images(frames, out_dir, ...)` converts a list of ASCII/ANSI frames
  (each frame is a multiline string) into PNG images.
- `images_to_video(img_dir_or_list, output_path, fps)` packs images into an MP4
  using imageio (ffmpeg backend).

The ANSI parser implemented is conservative but supports TrueColor SGR
(`38;2;R;G;B`) and 256-color SGR (`38;5;N`) as foreground and background.
"""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from tqdm import tqdm

import colorsys
import imageio
import time
import re
from log.logconfig import get_logger


logger = get_logger(__name__)

ESC_SGR = re.compile(r"\x1b\[([^m]*)m")


def _xterm_256_to_rgb(code: int) -> Tuple[int, int, int]:
    """Convert xterm-256 color code to an RGB tuple.

    Implements the standard 256-color mapping (16 + 6*6*6 + 24 grayscale).
    """
    if code < 16:
        # approximate 16-color palette
        base = [
            (0, 0, 0),
            (128, 0, 0),
            (0, 128, 0),
            (128, 128, 0),
            (0, 0, 128),
            (128, 0, 128),
            (0, 128, 128),
            (192, 192, 192),
            (128, 128, 128),
            (255, 0, 0),
            (0, 255, 0),
            (255, 255, 0),
            (0, 0, 255),
            (255, 0, 255),
            (0, 255, 255),
            (255, 255, 255),
        ]
        return base[code]
    if 16 <= code <= 231:
        c = code - 16
        r = (c // 36) % 6
        g = (c // 6) % 6
        b = c % 6
        scale = [0, 95, 135, 175, 215, 255]
        return (scale[r], scale[g], scale[b])
    if 232 <= code <= 255:
        v = 8 + (code - 232) * 10
        return (v, v, v)
    return (255, 255, 255)


def _parse_sgr_segment(
    segment: str, cur_fg: Tuple[int, int, int], cur_bg: Tuple[int, int, int]
):
    """Parse an SGR segment like '38;2;R;G;B' and update fg/bg colors.

    Returns a tuple (fg, bg).
    """
    parts = [p for p in segment.split(";") if p != ""]
    if not parts:
        return cur_fg, cur_bg

    i = 0
    try:
        while i < len(parts):
            code = int(parts[i])
            if code == 0:
                cur_fg = (255, 255, 255)
                cur_bg = (0, 0, 0)
                i += 1
            elif code == 38 and i + 1 < len(parts):
                # foreground extended
                kind = int(parts[i + 1])
                if kind == 2 and i + 4 < len(parts):
                    r = int(parts[i + 2])
                    g = int(parts[i + 3])
                    b = int(parts[i + 4])
                    cur_fg = (r, g, b)
                    i += 5
                elif kind == 5 and i + 2 < len(parts):
                    idx = int(parts[i + 2])
                    cur_fg = _xterm_256_to_rgb(idx)
                    i += 3
                else:
                    i += 2
            elif code == 48 and i + 1 < len(parts):
                # background extended
                kind = int(parts[i + 1])
                if kind == 2 and i + 4 < len(parts):
                    r = int(parts[i + 2])
                    g = int(parts[i + 3])
                    b = int(parts[i + 4])
                    cur_bg = (r, g, b)
                    i += 5
                elif kind == 5 and i + 2 < len(parts):
                    idx = int(parts[i + 2])
                    cur_bg = _xterm_256_to_rgb(idx)
                    i += 3
                else:
                    i += 2
            else:
                # unsupported/ignored codes (like 1=bold, 30-37 simple colors)
                i += 1
    except Exception:
        # ignore parse problems and keep current colors
        pass

    return cur_fg, cur_bg


def _parse_ansi_to_grid(text: str, default_fg=(255, 255, 255), default_bg=(0, 0, 0)):
    """Convert an ANSI-coded multiline string into a grid of (char, fg, bg).

    Returns: list[list[tuple(char, (r,g,b), (r,g,b))]]
    """
    grid = []
    for raw_line in text.splitlines():
        row = []
        pos = 0
        fg = default_fg
        bg = default_bg
        line = raw_line
        while pos < len(line):
            if line[pos] == "\x1b" and pos + 1 < len(line) and line[pos + 1] == "[":
                m = ESC_SGR.match(line, pos)
                if not m:
                    pos += 1
                    continue
                segment = m.group(1)
                fg, bg = _parse_sgr_segment(segment, fg, bg)
                pos = m.end()
                continue
            ch = line[pos]
            row.append((ch, fg, bg))
            pos += 1
        grid.append(row)
    return grid


def _boost_rgb(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Increase perceived color saturation by `factor` (1.0 = no change)."""
    try:
        r, g, b = rgb
        # normalize to 0..1
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        s = max(0.0, min(1.0, s * factor))
        nr, ng, nb = colorsys.hls_to_rgb(h, l, s)
        return (int(nr * 255), int(ng * 255), int(nb * 255))
    except Exception:
        return rgb


def frame_to_text(
        frame: str, 
        out_dir: Union[str, Path] = "output_texts"
) -> None:
    """
    Save frame to a text file.
    Only work with plain ASCII (no ANSI/Grayscale colors).
    """

    output_file = f"{out_dir}/frame_{int(time.time())}.txt"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(frame)
        logger.info("Saved to: %s", output_file)
    except Exception as e:
        logger.error("Failed to save file: %s", e)


def frames_to_images(
    frames: Sequence[str],
    out_dir: Union[str, Path] = "output_frames",
    font_path: Optional[str] = None,
    font_size: int = 14,
    default_fg=(255, 255, 255),
    default_bg=(0, 0, 0),
    color_boost: float = 1.0,
) -> List[str]:
    """Convert a sequence of ASCII/ANSI frames into PNG images.

    - `frames`: iterable of multiline strings (each frame).
    - `out_dir`: directory where PNGs will be written (created if missing).
    - `font_path`: optional TTF font path. Falls back to Pillow's default.
    - `font_size`: size used when `font_path` is provided; ignored for default font.

    Returns the list of written image file paths.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # load font
    font = None
    try:
        if font_path and Path(font_path).exists():
            font = ImageFont.truetype(str(font_path), font_size)
        else:
            logger.warning("Font path not found, using default font.")
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    bar_format="{l_bar}{bar} | {percentage:3.0f}% | {n_fmt}/{total_fmt} | {elapsed} → {remaining}"

    created: List[str] = []
    for i, frame in tqdm(
        enumerate(frames),
        bar_format=bar_format,
        total=len(frames),
        desc="Converting frames to images",
    ):
        grid = _parse_ansi_to_grid(frame, default_fg, default_bg)

        if not grid:
            # empty image guard
            img = Image.new("RGB", (10, 10), color=default_bg)
            p = out_dir / f"frame_{i:05d}.png"
            img.save(p)
            created.append(str(p))
            continue

        cols = max((len(r) for r in grid), default=0)
        rows = len(grid)

        # fallback conservative sizes
        char_w, char_h = (8, 16)

        img_w = max(1, cols * char_w)
        img_h = max(1, rows * char_h)

        img = Image.new("RGB", (img_w, img_h), color=default_bg)
        draw = ImageDraw.Draw(img)

        for y, row in enumerate(grid):
            for x, (ch, fg, bg) in enumerate(row):
                px = x * char_w
                py = y * char_h
                if bg != default_bg:
                    draw.rectangle([px, py, px + char_w, py + char_h], fill=bg)
                draw_fg = fg
                if color_boost and color_boost != 1.0:
                    draw_fg = _boost_rgb(fg, color_boost)
                draw.text((px, py), ch, font=font, fill=draw_fg)

        p = out_dir / f"frame_{i:05d}.png"
        img.save(p)
        created.append(str(p))

    logger.info("Saved %d images to: %s", len(created), out_dir)
    return created


def images_to_video(
    img_dir_or_list: Union[str, Path, Sequence[str]],
    output_path: str = "out.mp4",
    fps: int = 12,
) -> str:
    """Create a video (mp4) from images using imageio.

    - `img_dir_or_list`: directory path or a sequence of image file paths.
    - `output_path`: resulting video path.
    - `fps`: frames per second.

    Returns the `output_path` on success.
    """
    if isinstance(img_dir_or_list, (str, Path)):
        p = Path(img_dir_or_list)
        files = sorted(
            [
                str(x)
                for x in p.iterdir()
                if x.suffix.lower() in (".png", ".jpg", ".jpeg")
            ]
        )
    else:
        files = list(img_dir_or_list)

    if not files:
        raise FileNotFoundError("No image files found for video creation")

    writer = imageio.get_writer(output_path, fps=fps)
    try:
        for f in files:
            img = imageio.imread(f)
            writer.append_data(img)
    finally:
        writer.close()

    logger.info("Video saved to: %s", output_path)
    return output_path
