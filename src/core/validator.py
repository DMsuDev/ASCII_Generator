import os
from typing import Union

class FileValidator:
    """Validates input sources (file paths or camera indices)."""

    def validate(self, source: Union[str, int]) -> bool:
        if isinstance(source, str):
            return os.path.exists(source)
        if isinstance(source, int):
            return source == 0  # only default camera allowed for simplicity
        raise TypeError(f"Invalid source type: {type(source)}")