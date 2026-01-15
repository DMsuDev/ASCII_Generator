import json
import os


class JsonManager:
    """
    Gestor simple para cargar y guardar archivos JSON con valores por defecto.
    """

    def __init__(
        self,
        json_name: str = "config.json",
        default: dict | None = None,
        input_func=None,
    ):
        self._name = json_name
        self._default = default or {}

        # Función para pedir texto (Inquirer.Text o input)
        self._input_func = input_func or (lambda msg, default="": input(msg))

    def load(self) -> dict:
        """Carga el JSON. Si no existe o está corrupto, restaura los valores por defecto."""
        if not os.path.exists(self._name):
            print(f"{self._name} not found. Creating with defaults.")

            # new_name = self._input_func("Introduce el nombre del nuevo archivo JSON", "config.json")
            # if not new_name.endswith(".json"):
            #    new_name += ".json"
            # self._name = new_name

            self.save(data=self._default)
            return self._default

        try:
            with open(self._name, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"{self._name} is corrupted. Restoring defaults.")
            self.save(data=self._default)
            return self._default

    def save(self, name: str | None = None, data: dict | None = None) -> None:
        """
        Guarda un diccionario en un archivo JSON.
        Si no se pasa 'data', se guardan los valores por defecto.
        """

        _data: dict = data or self._default
        _json_name: str = name if name else self._name

        if not isinstance(_data, dict):
            raise TypeError("Solo se pueden guardar diccionarios en JSON.")

        with open(_json_name, "w") as file:
            json.dump(_data, file, indent=4)
