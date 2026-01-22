import inquirer
from typing import Any, Dict, List, Optional

from cli.menus import MENUS
from cli.styles import R


class QuestionsManager:
    # ---------------------------------------------------------
    #               PROMPT BUILDER
    # ---------------------------------------------------------
    def build_prompt(self, menu_name: str) -> Optional[List[Any]]:
        """Construye prompts de Inquirer basados en MENUS."""

        menu = MENUS.get(menu_name)
        if menu is None:
            print(R + f"Menú '{menu_name}' no encontrado.")
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
                    default=menu.get("default"),
                )
            ]

        elif menu_type == "form":
            prompts = []
            for field in menu["fields"]:
                if field["type"] == "text":
                    prompts.append(
                        inquirer.Text(
                            name=field["name"],
                            message=field["message"],
                            default=field.get("default"),
                        )
                    )
                elif field["type"] == "list":
                    prompts.append(
                        inquirer.List(
                            name=field["name"],
                            message=field["message"],
                            choices=field["choices"],
                            default=field.get("default"),
                        )
                    )
                else:
                    print(R + f"Tipo de campo desconocido en formulario: {type}")

            return prompts

    # -----------------------------
    # MÉTODOS DIRECTOS
    # -----------------------------

    def ask_text(self, message: str = "message", default: str = "") -> str:
        answer = inquirer.prompt(
            [inquirer.Text("value", message=message, default=default)]
        )
        return self._normalize_str(answer)

    def ask_list(
        self, message: str, choices: list[tuple[str, str]], default=None
    ) -> str:
        answer: dict | None = inquirer.prompt(
            [inquirer.List("value", message=message, choices=choices, default=default)]
        )
        return self._normalize_str(answer)

    # -----------------------------
    #  USEFULL
    # -----------------------------

    def _normalize_str(self, answer: dict | None, key: str = "value") -> str:
        if not answer:
            return ""
        value = answer.get(key)
        return value if isinstance(value, str) else ""

    # -----------------------------
    # MODO MENÚ
    # -----------------------------

    def get_menu(self, menu_name: str):
        prompts = self.build_prompt(menu_name)
        answers = inquirer.prompt(prompts)

        if not answers:
            print(R + "No se seleccionó ninguna acción.")
            return None

        return answers
