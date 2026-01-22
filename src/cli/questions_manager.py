import inquirer
from typing import Any, Dict, List, Optional, Tuple

from cli.menus import MENUS
from cli.styles import R


class QuestionsManager:
    """Handles interactive prompts using the inquirer library."""

    def build_prompt(self, menu_name: str) -> Optional[List[Any]]:
        """
        Build inquirer prompts based on predefined MENUS configuration.
        Returns None if menu not found.
        """
        menu = MENUS.get(menu_name)
        if menu is None:
            print(R + f"Menu '{menu_name}' not found.")
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
                    print(R + f"Unknown field type in form: {field_type}")
            return prompts

        print(R + f"Unknown menu type: {menu_type}")
        return None

    # ────────────────────────────────────────────────
    # Convenience methods for simple prompts
    # ────────────────────────────────────────────────

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
        if not answer:
            return ""
        value = answer.get(key)
        return str(value) if value is not None else ""

    # ────────────────────────────────────────────────
    # Main menu handler
    # ────────────────────────────────────────────────

    def get_menu(self, menu_name: str) -> Optional[Dict[str, Any]]:
        """Show interactive menu and return user's answers."""
        prompts = self.build_prompt(menu_name)
        if not prompts:
            return None

        answers = inquirer.prompt(prompts)
        if not answers:
            print(R + "No action selected.")
            return None

        return answers
