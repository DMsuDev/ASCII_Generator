from abc import ABC, abstractmethod
from typing import Optional, Union

import cv2
import keyboard
import time
import numpy as np

from .validator import FileValidator
from .resizer import Resizer
from .converter import Converter

from ..utils import clear_console, COLORS
from ..settings import Mode, Gradient, get_gradient_ramp
from ..log import get_logger
from .time_manager import FPSController


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
        resizer: Optional[Resizer] = None,
        ascii_converter: Optional[Converter] = None,
    ):
        self.logger = get_logger(__name__)
        self.target_width = int(target_width)
        self.scale_factor = float(scale)
        self.gradient = get_gradient_ramp(sequence)
        self.mode = mode
        self.invert = invert
        self.mirror = mirror
        self.validator = validator or FileValidator()
        self.resizer = resizer or Resizer()
        self.ascii_converter = ascii_converter or Converter()

    def _validate_source(self, source: Union[str, int]) -> None:
        if not self.validator.validate(source):
            if isinstance(source, str):
                raise FileNotFoundError(f"{COLORS.RED.value}File not found: {source}")
            raise ValueError(f"{COLORS.RED.value}Invalid camera index: {source}")

    @abstractmethod
    def process_frame(self, frame: np.ndarray) -> str:
        """Core ASCII conversion logic for a single frame/image."""

    @abstractmethod
    def start_processing(self, source: Union[str, int]) -> str:
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
        h, w = gray.shape

        new_w, new_h = self.resizer.compute_size(
            self.target_width, w, h, self.scale_factor
        )

        gray = self.resizer.resize(gray, (new_w, new_h))
        color_frame = self.resizer.resize(frame, (new_w, new_h))

        return self.ascii_converter.convert(gray, color_frame, self.gradient, self.mode)

    def start_processing(self, source: Union[str, int]) -> str:
        self._validate_source(source)
        ascii_art: list[str] = []

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"{COLORS.RED.value}Failed to open video/camera source")

        # Get native video FPS; if unavailable don't throttle
        video_fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
        
        # FPS controller for throttling and smoothing
        fps_ctrl = FPSController(video_fps)
        try:
            while True:

                ret, frame = cap.read()
                if not ret:
                    if source == 0: # Camera
                        # For the camera: continue (live), but add small sleep to avoid saturation
                        time.sleep(0.001)  # Avoid CPU to 100% in live
                        continue
                    else:
                        break  # End of video/image sequence
                    
                # Delta time since last frame
                dt = fps_ctrl.begin_frame()

                ascii_art.append(self.process_frame(frame))
                ascii_art_str = ascii_art[-1]
                if fps_ctrl.should_render(dt):
                    # Read next frame

                    clear_console()
                    # Use logger to output rendered ASCII frame (keeps centralized formatting)
                    if ascii_art_str:
                        print(ascii_art_str)
                    else:
                        self.logger.warning("Empty frame received.")

                    # Throttle and update smoothed FPS via FPSController
                    smoothed = fps_ctrl.get_smoothed_fps()
                    if smoothed is not None:
                        print(f"{COLORS.CYAN.value}FPS: {smoothed:.1f}")

                    print(f"{COLORS.YELLOW.value}Press 'q' or ESC to exit...")

                if keyboard.is_pressed("q") or keyboard.is_pressed("esc"):
                    break


        except KeyboardInterrupt:
            self.logger.debug("Processing interrupted by user.")

        finally:
            # Release video capture resources
            cap.release()
            # Ensure any windows are destroyed after capture is released
            cv2.destroyAllWindows()

        return "\n\n".join(ascii_art)