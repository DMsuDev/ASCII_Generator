from typing import Union
from cli.questions_manager import QuestionsManager
from cli.banner import Banner

from engine import ImageProcessor, VideoProcessor, Processor, FileValidator

from settings.config import DEFAULT_SETTINGS, GRADIENT, MODE
from data.json_manager import JsonManager

from utils import clear_console, clear_screen, get_source_via_dialog, render_image
from cli.styles import R, Y

# ============================================================
#                     MAIN APPLICATION
# ============================================================

SETTINGS: dict = {}


def main() -> None:
    global SETTINGS

    banner: Banner = Banner()
    menu: QuestionsManager = QuestionsManager()
    data_manager: JsonManager = JsonManager(
        json_name="config.json", default=DEFAULT_SETTINGS, input_func=menu.ask_text
    )

    SETTINGS = load_settings(data_manager)

    ROUTES = {
        "init": lambda: handle_init(menu, banner, SETTINGS),
        "settings": lambda: update_settings(menu, data_manager, banner),
        "exit": lambda: exit_program(),
    }

    while True:
        clear_console()
        show_section(banner=banner, title="ASCII ENGINE", subtitle="GENERATOR")

        answer = menu.get_menu("main")
        if not answer or "option" not in answer:
            print(R + "Entrada inválida, intenta de nuevo.")
            continue

        option = answer["option"]
        if option in ROUTES:
            ROUTES[option]()
        else:
            print(R + f"Opción desconocida: {option}")


# ============================================================
#                     MENU HANDLERS
# ============================================================


@clear_screen
def handle_init(manager: QuestionsManager, banner: Banner, settings: dict = {}):
    show_section(banner, title="ASCII ENGINE", subtitle="MODE INPUT")

    answer = manager.get_menu("init")
    if not answer or "option" not in answer:
        print("Entrada inválida, intenta de nuevo.")
        return

    match answer["option"]:
        case "camera":
            handle_Camera(settings, manager)
        case "image":
            handle_Image(settings, manager)
        case "video":
            handle_Video(settings, manager)
        case "back":
            return


@clear_screen
def handle_settings(
    manager: QuestionsManager, saveManager: JsonManager, banner: Banner
):
    global SETTINGS

    clear_console()
    show_section(banner, title="ASCII ENGINE", subtitle="CONFIGURATION")

    raw_answers = manager.get_menu("settings")
    saveManager.save(data=raw_answers)

    SETTINGS = normalize_settings(saveManager.load())
    print(SETTINGS)

    print("\nConfiguración guardada:")
    input("Presiona ENTER para continuar...")


# ============================================================
#                     CORE HANDLERS
# ============================================================


@clear_screen
def handle_processing(processor: Processor, source: Union[str, int]) -> None:
    ascii_art: str = processor.run(source)
    print(ascii_art)
    input("Presiona ENTER para continuar...")


@clear_screen
def handle_Image(settings, manager: QuestionsManager) -> None:
    validator: FileValidator = FileValidator()
    processor: Processor = ImageProcessor(
        target_width=settings["width"],
        scale=settings["scale_factor"],
        sequence=settings["gradient"],
        mode=settings["mode"],
        invert=False,
        mirror=False,
        validator=validator,
    )
    ascii_art: str = processor.run(get_source_via_dialog(False))
    render_image(ascii_art, ask_Save(manager))
    input("Presiona ENTER para continuar...")


@clear_screen
def handle_Camera(settings: dict, manager: QuestionsManager) -> None:
    validator: FileValidator = FileValidator()
    processor: Processor = VideoProcessor(
        target_width=settings["width"],
        scale=settings["scale_factor"],
        sequence=settings["gradient"],
        mode=settings["mode"],
        invert=False,
        mirror=False,
        validator=validator,
    )
    handle_processing(processor, 0)


@clear_screen
def handle_Video(settings: dict, manager: QuestionsManager) -> None:
    validator: FileValidator = FileValidator()
    processor: Processor = VideoProcessor(
        target_width=settings["width"],
        scale=settings["scale_factor"],
        sequence=settings["gradient"],
        mode=settings["mode"],
        invert=False,
        mirror=False,
        validator=validator,
    )
    handle_processing(processor, get_source_via_dialog(True))


# ============================================================
#                     SETTINGS HELPERS
# ============================================================


def update_settings(menu: QuestionsManager, data: JsonManager, banner: Banner):
    new_settings = handle_settings(menu, data, banner)
    return new_settings


def load_settings(manager: JsonManager) -> dict:
    setting = manager.load()
    setting["mode"] = MODE[setting["mode"]]
    setting["gradient"] = GRADIENT[str(setting["gradient"])]
    return setting


def normalize_settings(settings: dict) -> dict:
    new_dict: dict = settings
    new_dict["mode"] = MODE[new_dict["mode"]]
    new_dict["gradient"] = GRADIENT[new_dict["gradient"]]
    return new_dict


def ask_Save(manager: QuestionsManager) -> bool:
    answer: str = manager.ask_list(
        message="Desea salvar la imagen en un archivo?",
        choices=[(Y + "Si", "1"), (Y + "No", "0")],
        default="No",
    )
    return True if answer == "1" else False


@clear_screen
def show_section(banner: Banner, title: str, subtitle: str):
    banner.show(title, subtitle)


# ============================================================
#                     ENTRY POINT
# ============================================================


def exit_program():
    print("Saliendo...")
    raise SystemExit


if __name__ == "__main__":
    main()
