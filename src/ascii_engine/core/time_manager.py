import time
from typing import Optional


class FPSController:
    """Delta-time FPS controller without sleep, with frame skipping and EMA smoothing."""

    def __init__(
        self, target_fps: Optional[float] = None, smoothing_alpha: float = 0.2
    ):
        self.target_fps = target_fps
        self.frame_interval = 1.0 / target_fps if target_fps else None

        self.prev_time = time.perf_counter()
        self.accumulator = 0.0

        self.smoothed_fps = None
        self.alpha = smoothing_alpha

    def begin_frame(self) -> float:
        """Return delta time since last frame."""
        now = time.perf_counter()
        dt = now - self.prev_time
        self.prev_time = now

        # Update smoothed FPS
        if dt > 0:
            # Calculate instantaneous FPS
            inst_fps = 1.0 / dt
            # Update EMA (Exponential Moving Average) smoothed FPS
            if self.smoothed_fps is None:
                self.smoothed_fps = inst_fps
            else:
                self.smoothed_fps = (self.alpha * inst_fps + (1 - self.alpha) * self.smoothed_fps)

        return dt

    def should_render(self, dt: float) -> bool:
        """Return True only when enough time has passed to render a frame."""
        if self.frame_interval is None:
            return True  # unlimited FPS

        self.accumulator += dt

        if self.accumulator >= self.frame_interval:
            self.accumulator -= self.frame_interval
            return True

        return False
        
    def get_smoothed_fps(self) -> Optional[float]:
        """Return the current smoothed FPS value."""
        return self.smoothed_fps
    
    def set_target_fps(self, fps: Optional[float]):
        """Set a new target FPS and update frame interval."""
        self.target_fps = fps
        self.frame_interval = 1.0 / fps if fps else None