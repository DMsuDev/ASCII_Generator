from abc import ABC, abstractmethod
from enum import Enum
import time
from typing import Optional, Union

import cv2
import keyboard
import numpy as np
from colorama import Fore, Style

from core.validator import FileValidator
from utils import (
    clear_console,
    get_index_ascii,
    rgb_to_ansi,
    gray_to_ansi,
    scale_height,
    get_terminal_size,
)
from settings.modes import Mode
from settings.gradients import Gradient, get_gradient_ramp

from cli.styles import R

# ============================================================
#                  INTERPOLATION ENUM & HELPERS
# ============================================================


class INTERPOLATION(Enum):
    """Available interpolation methods for resizing."""

    NEAREST = cv2.INTER_NEAREST  # Fast, pixelated (good for ASCII precision)
    LINEAR = cv2.INTER_LINEAR  # Default, smooth
    CUBIC = cv2.INTER_CUBIC  # Slower, higher quality
    AREA = cv2.INTER_AREA  # Good for downscaling
    LANCZOS4 = cv2.INTER_LANCZOS4  # Best quality for images


def get_interpolation_method(method_name: str) -> int:
    """Convert string interpolation name to OpenCV constant."""
    try:
        return INTERPOLATION[method_name.upper()].value
    except KeyError:
        print(f"Unknown interpolation '{method_name}', using LINEAR")
        return cv2.INTER_LINEAR

class Processor(ABC):
    """Handles frame transformations before ASCII conversion."""
    
    def __init__(
        self,
        target_width: int,
        scale: float,
        sequence: Gradient,
        mode: Mode,
        invert: bool = False,
        mirror: bool = False,
        validator: Optional[FileValidator] = None,
    ):
        self.target_width = int(target_width)
        self.scale_factor = float(scale)
        self.gradient = get_gradient_ramp(sequence)
        self.mode = mode
        self.invert = invert
        self.mirror = mirror
        self.validator = validator or FileValidator()

    def _validate_source(self, source: Union[str, int]) -> None:
        if not self.validator.validate(source):
            if isinstance(source, str):
                raise FileNotFoundError(R + f"File not found: {source}")
            raise ValueError(R + f"Invalid camera index: {source}")

    @abstractmethod
    def process_frame(self, frame: np.ndarray) -> str:
        """Core ASCII conversion logic for a single frame/image."""

    @abstractmethod
    def start(self, source: Union[str, int]) -> str:
        """Main entry point to process source and return or display result."""


class FrameProcessor(Processor):
    """Processor for video files and live camera."""

    def process_frame(self, frame: np.ndarray) -> str:
        if frame is None or frame.size == 0:
            return ""
        
        if len(frame.shape) != 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif frame.shape[2] == 4:
            # Remove alpha channel (common in PNGs)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        elif frame.shape[2] != 3:
            raise ValueError(f"Unsupported frame format: {frame.shape}")
        
        if self.invert:
            frame = cv2.bitwise_not(frame)
        if self.mirror:
            frame = cv2.flip(frame, 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        term_w, _ = get_terminal_size()
        new_w = min(self.target_width, term_w)
        h, w = gray.shape
        new_h = scale_height(new_w, w, h, self.scale_factor)

        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
        color_frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        ascii_lines = []
        for y in range(new_h):
            row = []
            for x in range(new_w):
                pixel_val = gray[y, x]
                char = get_index_ascii(pixel_val, self.gradient)

                if self.mode == Mode.RGB:
                    b, g, r = color_frame[y, x]
                    row.append(rgb_to_ansi(r, g, b, char))
                elif self.mode == Mode.GRAYSCALE:
                    row.append(gray_to_ansi(pixel_val, char))
                else:
                    row.append(char)
            ascii_lines.append("".join(row))

        return "\n".join(ascii_lines)

    def start(self, source: Union[str, int]) -> str:
        self._validate_source(source)
        ascii_art: list[str] = []
        
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(R + "Failed to open video/camera source")

        # Get native video FPS; if unavailable don't throttle
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 0.0

        # If video_fps is valid, compute the target time per frame. If it's
        # invalid or too small, keep `frame_interval` as None
        frame_interval = 1.0 / video_fps if video_fps and video_fps > 0.001 else None

        # Monotonic timer for measuring display intervals
        prev_display_time = time.perf_counter()

        # Exponential moving average value shown to the user
        smoothed_fps: Optional[float] = None

        # EMA alpha (0..1): higher = more responsive, lower = smoother
        fps_smoothing_alpha = 0.2
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # end of video

                # Iteration start to compute processing+render time
                iter_start = time.perf_counter()

                ascii_art.append(self.process_frame(frame))
                ascii_art_str = ascii_art[-1]

                clear_console()
                print(ascii_art_str if ascii_art_str else "Error: No ASCII frame to render.")

                # Update/display smoothed FPS. If we have a target
                # `frame_interval`, sleep the remaining time to match it.
                if smoothed_fps is None:
                    now_display = time.perf_counter()
                    dt = now_display - prev_display_time
                    smoothed_fps = 1.0 / dt if dt > 0 else 0.0
                    prev_display_time = now_display
                else:
                    # Throttle to native FPS when available
                    if frame_interval is not None:
                        elapsed = time.perf_counter() - iter_start
                        to_sleep = frame_interval - elapsed
                        if to_sleep > 0:
                            time.sleep(to_sleep)

                    now_display = time.perf_counter()
                    dt = now_display - prev_display_time
                    if dt > 0:
                        inst_fps = 1.0 / dt
                        smoothed_fps = fps_smoothing_alpha * inst_fps + (1 - fps_smoothing_alpha) * smoothed_fps
                    prev_display_time = now_display

                # Print the (possibly smoothed) FPS value for user feedback.
                if smoothed_fps is not None:
                    print(f"{Fore.CYAN}{Style.BRIGHT}FPS: {smoothed_fps:.1f}")

                print(f"{Fore.YELLOW}{Style.BRIGHT}Press 'q' or ESC to exit...")

                if keyboard.is_pressed("q") or keyboard.is_pressed("esc"):
                    break

                # Optional: respect target FPS (simple sleep)
                # time.sleep(max(0, 1.0 / 30 - (time.time() - now)))

        except KeyboardInterrupt:
            print(f"{Fore.RED}Interrupted by user.")

        finally:
            cap.release()
            cv2.destroyAllWindows()

        return "\n\n".join(ascii_art)
