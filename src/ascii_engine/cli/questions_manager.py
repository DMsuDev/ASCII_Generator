import inquirer
from typing import Any, Dict, List, Optional, Tuple

from .menus import MENUS

from ..log import get_logger

class QuestionsManager:
    """Handles interactive prompts using the inquirer library."""
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    def build_prompt(self, menu_name: str) -> Optional[List[Any]]:
        """
        Build inquirer prompts based on predefined MENUS configuration.
        Returns None if menu not found.
        """
        menu = MENUS.get(menu_name, None)
        if menu is None:
            self.logger.warning(f"Menu '{menu_name}' not found in MENUS.")
            return None

        menu_type = menu.get("type")
        if menu_type == "list":
            return [
                inquirer.List(
                    name=menu["name"],
                    message=menu["message"],
                    choices=menu["choices"],
                    default=menu.get("default"),
                )
            ]

        elif menu_type == "text":
            return [
                inquirer.Text(
                    name=menu["name"],
                    message=menu["message"],
                    default=menu.get("default", ""),
                )
            ]

        elif menu_type == "form":
            prompts = []
            for field in menu.get("fields", []):
                field_type = field.get("type")
                if field_type == "text":
                    prompts.append(
                        inquirer.Text(
                            name=field["name"],
                            message=field["message"],
                            default=field.get("default", ""),
                        )
                    )
                elif field_type == "list":
                    prompts.append(
                        inquirer.List(
                            name=field["name"],
                            message=field["message"],
                            choices=field["choices"],
                            default=field.get("default"),
                        )
                    )
                else:
                    self.logger.warning(f"Unknown field type in form: {field_type}")
            return prompts

        self.logger.warning(f"Unknown menu type: {menu_type}")
        return None

    # ────────────────────────────────────────────────
    # Convenience methods for simple prompts
    # ────────────────────────────────────────────────

    def ask_cofirmation(self, message: str, default: bool = False) -> bool:
        """Ask a yes/no confirmation question."""
        answer = inquirer.prompt(
            [inquirer.Confirm("value", message=message, default=default)]
        )
        return bool(answer and answer.get("value"))

    def ask_text(self, message: str, default: str = "") -> str:
        """Ask for a single text input."""
        answer = inquirer.prompt(
            [inquirer.Text("value", message=message, default=default)]
        )
        return self._extract_value(answer)

    def ask_list(
        self,
        message: str,
        choices: List[Tuple[str, str]],
        default: Optional[str] = None,
    ) -> str:
        """Ask user to select from a list of (display, value) tuples."""
        answer = inquirer.prompt(
            [inquirer.List("value", message=message, choices=choices, default=default)]
        )
        return self._extract_value(answer)

    def _extract_value(
        self, answer: Optional[Dict[str, Any]], key: str = "value"
    ) -> str:
        """Safely extract string value from inquirer response."""
        value = answer.get(key, None) if answer else None
        return str(value) if value is not None else ""

    # ────────────────────────────────────────────────
    # Main menu handler
    # ────────────────────────────────────────────────

    def run_menu(self, menu_name: str) -> Dict[str, Any]:
        """Show interactive menu and return user's answers."""
        try:
            while True:
                prompts = self.build_prompt(menu_name)
                if not prompts:
                    raise ValueError(f"Not found prompts for menu '{menu_name}'")
            
                answers = inquirer.prompt(prompts)
                
                if answers is None:
                    self.logger.info(f"User cancelled or selected no action in menu '{menu_name}'.")
                    raise KeyboardInterrupt
                
                if all(v is not None for v in answers.values()):
                    return answers
                
                self.logger.warning(f"Invalid answer in menu '{menu_name}': {answers}")
        
        except Exception as exc:
            self.logger.error(f"Error while running menu '{menu_name}': {exc}")
            raise # Re-raise to allow higher-level handling
