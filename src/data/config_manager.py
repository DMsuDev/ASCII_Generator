from typing import Any, Dict, Optional, Callable
from pathlib import Path
import logging
import json
from copy import deepcopy

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Simple and robust JSON configuration manager.

    - Loads defaults if file is missing or corrupted
    - Keeps loaded config in memory (avoids repeated disk reads)
    - Easy save of current state
    - Optional interactive input for missing values
    """

    def __init__(
        self,
        file_name: str = "config.json",
        default_config: Optional[Dict[str, Any]] = None,
        interactive_input: Optional[Callable[[str, Any], Any]] = None,
        validate_func: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        """
        Args:
            file_name: Name or relative path of the JSON file
            default_config: Dictionary with default values
            interactive_input: Custom function to ask user for values (defaults to input())
            validate_func: Optional function to validate loaded config structure/semantics
        """
        self._path = Path(file_name).resolve()
        self._defaults = deepcopy(default_config or {})
        self._data: Dict[str, Any] = {}
        self._is_loaded = False

        self._input_func = interactive_input or self._default_input
        self._validate = validate_func

        # Auto-load on initialization (common pattern)
        self.load()

    def _default_input(self, message: str, default: Any = "") -> str:
        """Default input with visible default value"""
        default_str = f" [{default}]" if default else ""
        return input(f"{message}{default_str}: ").strip() or str(default)

    @property
    def data(self) -> Dict[str, Any]:
        """Read-only access to loaded config"""
        if not self._is_loaded:
            self.load()
        return self._data

    def load(self, force: bool = False) -> Dict[str, Any]:
        """Load (or reload) configuration from disk"""
        if self._is_loaded and not force:
            return self._data.copy()

        if not self._path.exists():
            logger.info("Config file %s not found → using defaults", self._path.name)
            self._data = deepcopy(self._defaults)
            self._is_loaded = True
            self.save()  # Create file with defaults on first run
            return self._data.copy()

        try:
            with self._path.open("r", encoding="utf-8") as f:
                loaded = json.load(f)

            if not isinstance(loaded, dict):
                raise TypeError("JSON content is not a dictionary")

            self._data = loaded
            self._is_loaded = True

            if self._validate:
                try:
                    self._validate(self._data)
                except ValueError as e:
                    logger.warning("Validation failed: %s → restoring defaults", e)
                    self._data = deepcopy(self._defaults)
                    self.save()

            logger.debug("Configuration loaded successfully from %s", self._path)
            return self._data.copy()

        except (json.JSONDecodeError, OSError, TypeError) as e:
            logger.warning(
                "Failed to read %s properly (%s) → restoring defaults", self._path, e
            )
            self._data = deepcopy(self._defaults)
            self._is_loaded = True
            self.save()
            return self._data.copy()

    def save(self, custom_path: Optional[Path | str] = None) -> None:
        """Save current state (self.data) to disk"""
        target = Path(custom_path) if custom_path else self._path

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4, ensure_ascii=False)
            logger.debug("Configuration saved to %s", target)
        except OSError as e:
            logger.error("Error saving config to %s: %s", target, e)
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like .get() with fallback to defaults"""
        return self.data.get(key, self._defaults.get(key, default))

    def set(self, key: str, value: Any, save_immediately: bool = False) -> None:
        """Update a value and optionally save right away"""
        self._data[key] = value
        if save_immediately:
            self.save()

    def update(
        self, new_values: Dict[str, Any], save_immediately: bool = False
    ) -> None:
        """Update multiple values at once"""
        self._data.update(new_values)
        if save_immediately:
            self.save()

    def ask_for_missing(
        self,
        required_keys: list[str],
        custom_messages: Optional[Dict[str, str]] = None,
        save_after: bool = True,
    ) -> None:
        """
        Interactively ask user for missing required keys.
        Useful for first run or when config is incomplete.
        """
        custom_messages = custom_messages or {}
        changed = False

        for key in required_keys:
            if key not in self._data:
                msg = custom_messages.get(key, f"Enter value for {key}")
                default_val = self._defaults.get(key, "")
                value = self._input_func(msg, default_val)
                self._data[key] = value
                changed = True

        if changed and save_after:
            self.save()
