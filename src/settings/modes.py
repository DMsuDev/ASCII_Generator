from enum import Enum, auto
from log.logconfig import get_logger


logger = get_logger(__name__)


class Mode(Enum):
    """
    Mode of rendering for the ASCII engine.
    """
    RGB        = auto()
    GRAYSCALE  = auto()
    ASCII      = auto()
    # Add more in the future without breaking almost anything
    # BLOCK      = auto()


def get_mode(name: str) -> Mode:
    """
    Convert a mode name (string) to its enum value.
    
    Returns RGB as a safe fallback if the value is not valid.
    """
    name = name.strip().upper()
    try:
        return Mode[name]
    except KeyError:
        logger.warning(
            "Unrecognized mode: %s. Valid values: %s",
            name,
            ", ".join(m.name for m in Mode),
        )
        return Mode.RGB
    