from src.cli.questions_manager import QuestionsManager
from src.cli.banner import Banner

from src.core.image_handler import ImageProcessor
from src.core.video_handler import VideoProcessor

from src.settings.config import DEFAULT_SETTINGS, GRADIENT, MODE
from src.data.json_manager import JsonManager

from src.utils import clear_console, clear_screen, get_source_via_dialog, save_txt
from src.cli.styles import R

# ============================================================
#                     MAIN APPLICATION
# ============================================================

SETTINGS: dict = {}

def main() -> None:
    global SETTINGS

    banner: Banner = Banner()
    menu: QuestionsManager = QuestionsManager()
    data_manager: JsonManager = JsonManager(json_name="config.json", default=DEFAULT_SETTINGS, input_func=menu.ask_text)

    SETTINGS = load_settings(data_manager)
    
    ROUTES = {
        "init": lambda: handle_init(menu, banner, SETTINGS),
        "settings": lambda: update_settings(menu, data_manager, banner),
        "exit": lambda: exit_program()
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
            handle_Camera(settings)
        case "image": 
            handle_Image(settings)
        case "video": 
            handle_Video(settings)
        case "back":
            return

@clear_screen
def handle_settings(manager: QuestionsManager, saveManager: JsonManager, banner: Banner):
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
#                     PROCESSOR FACTORY
# ============================================================

def create_processor(settings: dict, video: bool) -> ImageProcessor | VideoProcessor:
    cls = VideoProcessor if video else ImageProcessor
    return cls(
        settings["width"],
        settings["gradient"],
        settings["mode"],
        settings["scale_factor"]
    )

# ============================================================
#                     CORE HANDLERS
# ============================================================

@clear_screen
def handle_Image(settings: dict) -> None:
    processor = create_processor(settings, false)
    ascii_art:str = processor.ProcessImage(path=get_source_via_dialog(False))
    print(ascii_art)
    save_txt(ascii_art)
    input("Presiona ENTER para continuar...")

@clear_screen
def handle_Camera(settings: dict) -> None:
    processor: VideoProcessor = create_processor(settings, true)
    processor.ProcessVideo(0)
    input("Presiona ENTER para continuar...")

@clear_screen
def handle_Video(settings: dict) -> None:
    processor: VideoProcessor = create_processor(settings, true)
    processor.ProcessVideo(path=get_source_via_dialog(True))
    input("Presiona ENTER para continuar...")

# ============================================================
#                     SETTINGS HELPERS
# ============================================================

def update_settings(menu: QuestionsManager, data: JsonManager, banner: Banner):
    new_settings = handle_settings(menu, data, banner)
    return new_settings

def load_settings(manager: JsonManager) -> dict:
    setting = manager.load()
    setting['mode'] = MODE[setting['mode']]
    setting['gradient'] = GRADIENT[str(setting['gradient'])]
    return setting

def normalize_settings(settings: dict) -> dict:
    new_dict: dict = settings
    new_dict['mode'] = MODE[new_dict['mode']]
    new_dict['gradient'] = GRADIENT[new_dict['gradient']]
    return new_dict

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