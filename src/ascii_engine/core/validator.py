import os
from typing import Union
from ..log import get_logger


logger = get_logger(__name__)


class FileValidator:
    """Validates input sources (file paths or camera indices)."""

    def validate(self, source: Union[str, int]) -> bool:
        if isinstance(source, str):
            exists = os.path.exists(source)
            if not exists:
                logger.warning("File not found: %s", source)
            return exists
        if isinstance(source, int):
            ok = source == 0  # only default camera allowed for simplicity
            if not ok:
                logger.warning("Invalid camera index: %s (only 0 allowed)", source)
            return ok
        raise TypeError(f"Invalid source type: {type(source)}")
