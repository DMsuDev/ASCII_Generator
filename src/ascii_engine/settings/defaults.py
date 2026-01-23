from .modes import Mode
from .gradients import Gradient

DEFAULT_RAW_SETTINGS = {
    "fps": 24,
    "width": 120,
    "scale_factor": 0.50,
    "mode": Mode.RGB.name,
    "gradient": Gradient.DETAILED.name,
}
