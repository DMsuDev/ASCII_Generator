# src/ascii_generator/config/settings.py
from dataclasses import dataclass, asdict
from .modes import Mode, get_mode
from .gradients import Gradient, get_gradient
from .defaults import DEFAULT_RAW_SETTINGS

from typing import Any

# Mutable settings at runtime
@dataclass(frozen=False) 
class AppSettings:
    """Normalized application settings with validation and conversion."""
    fps: int
    width: int
    scale_factor: float
    mode: Mode
    gradient: Gradient

    @classmethod
    def default(cls) -> 'AppSettings':
        """Create instance with default values"""
        return cls(
            fps=DEFAULT_RAW_SETTINGS["fps"],
            width=DEFAULT_RAW_SETTINGS["width"],
            scale_factor=DEFAULT_RAW_SETTINGS["scale_factor"],
            mode=Mode.RGB,
            gradient=Gradient.DETAILED,
        )
    
    @classmethod
    def from_raw(cls, raw: dict[str, Any]) -> 'AppSettings':
        """Create normalized instance from raw dict (JSON)"""
        data = DEFAULT_RAW_SETTINGS.copy()
        data.update(raw)

        return cls(
            fps=int(data["fps"]),
            width=int(data["width"]),
            scale_factor=float(data["scale_factor"]),
            mode=get_mode(data["mode"]),
            gradient=get_gradient(data["gradient"]),
        )

    def update(self, updates: dict[str, Any]) -> None:
        """Update specific fields (for runtime changes)"""
        for key, value in updates.items():
            if hasattr(self, key):
                if key == "mode":
                    setattr(self, key, get_mode(value))
                elif key == "gradient":
                    setattr(self, key, get_gradient(value))
                elif key == "fps":
                    setattr(self, key, int(value))
                elif key == "width":
                    setattr(self, key, int(value))
                elif key == "scale_factor":
                    setattr(self, key, float(value))
                else:
                    setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        """To save back to JSON (uses .name of enums)"""
        d = asdict(self)
        d["mode"] = self.mode.name
        d["gradient"] = self.gradient.name
        return d