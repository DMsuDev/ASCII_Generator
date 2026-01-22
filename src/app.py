from typing import Any, Callable, Dict
from cli.questions_manager import QuestionsManager
from cli.banner import Banner

from processor import FrameProcessor, Processor, FileValidator

from settings.config import DEFAULT_SETTINGS, normalize_runtime_settings
from data.config_manager import ConfigManager

from utils import clear_console, clear_screen, get_source_via_dialog
from cli.styles import R, Y
from media import frame_to_text, frames_to_images, images_to_video

# ============================================================
#                     MAIN APPLICATION
# ============================================================


def main() -> None:
    """
    Entry point of the ASCII Generator application.
    Orchestrates menu navigation and settings management.
    """

    banner: Banner = Banner()
    menu: QuestionsManager = QuestionsManager()

    # Initialize config manager with defaults and custom input handler
    config_manager: ConfigManager = ConfigManager(
        file_name="config.json",
        default_config=DEFAULT_SETTINGS,
        interactive_input=menu.ask_text,
    )

    routes: Dict[str, Callable] = {
        "init": lambda: handle_init(menu, banner, config_manager),
        "settings": lambda: handle_settings_update(menu, config_manager, banner),
        "exit": exit_program,
    }

    while True:
        clear_console()
        show_section(banner=banner, title="ASCII ENGINE", subtitle="GENERATOR")

        answer = menu.get_menu("main")
        if not answer or "option" not in answer:
            print(R + "Invalid input, try again.")
            continue

        option = answer["option"]
        handler = routes.get(option)

        if handler:
            handler()
        else:
            print(R + f"Unknown option: {option}")


# ============================================================
#                     MENU HANDLERS
# ============================================================


@clear_screen
def handle_init(
    menu: QuestionsManager,
    banner: Banner,
    config_manager: ConfigManager,
) -> None:
    """Handle selection of input source mode (loads settings at call time)."""
    # Reload runtime settings each time user enters the Init menu
    settings = load_and_normalize_settings(config_manager)

    show_section(banner, title="ASCII ENGINE", subtitle="INPUT MODE")

    answer = menu.get_menu("init")
    if not answer or "option" not in answer:
        print(R + "Invalid selection, returning to main menu.")
        return

    mode = answer["option"]
    match mode:
        case "camera":
            handle_camera(settings)
        case "image":
            handle_image(settings, menu)
        case "video":
            handle_video(settings, menu)
        case "back":
            return
        case _:
            print(R + f"Unknown mode: {mode}")


@clear_screen
def handle_settings_update(
    menu: QuestionsManager,
    config_manager: ConfigManager,
    banner: Banner,
) -> None:
    """Update settings interactively and save them."""
    show_section(banner, title="ASCII ENGINE", subtitle="SETTINGS")

    print("Current settings:")
    for key, value in config_manager.data.items():
        print(f"  {key}: {value}")

    new_answers = menu.get_menu("settings")
    if new_answers:
        config_manager.update(new_answers, save_immediately=True)
        print("\nSettings updated and saved.")

    # Reload normalized settings (though not strictly needed here)
    updated = load_and_normalize_settings(config_manager)
    print("Runtime values:", updated)

    input("\nPress ENTER to return...")


# ============================================================
#                     CORE PROCESSING HANDLERS
# ============================================================


def create_processor(settings: Dict[str, Any]) -> Processor:
    """
    Factory function to create the appropriate processor
    based on shared settings (avoids duplication).
    """
    validator = FileValidator()

    common_params = {
        "target_width": settings["width"],
        "scale": settings["scale_factor"],
        "sequence": settings["gradient"],
        "mode": settings["mode"],
        "invert": False,  # can be made configurable later
        "mirror": False,  # can be made configurable later
        "validator": validator,
    }

    # For now we use VideoProcessor for both camera and video
    # (since camera is just video source=0)
    return FrameProcessor(**common_params)


@clear_screen
def handle_image(settings: Dict[str, Any], menu: QuestionsManager) -> None:
    """Process a single static image."""
    processor = create_processor(settings)
    source = get_source_via_dialog(is_video=False)

    if not source:
        print(Y + "No file selected.")
        return

    ascii_art = processor.start(source)
    if ask_save(menu):
        # TODO: allow user to choose filename/path
        frame_to_text(ascii_art, filename="ascii_image_output.txt")

    input("\nPress ENTER to continue...")


@clear_screen
def handle_camera(settings: Dict[str, Any]) -> None:
    """Process live webcam feed."""
    processor = create_processor(settings)
    processor.start(0)  # 0 = default camera


@clear_screen
def handle_video(settings: Dict[str, Any], menu: QuestionsManager) -> None:
    """Process a video file."""
    processor = create_processor(settings)
    source = get_source_via_dialog(is_video=True)

    if not source:
        print(Y + "No video selected.")
        return

    ascii_art: str = processor.start(source)
    # try to recover list of frames (processor returns joined string separated by blank line)
    frames_list: list[str] = []
    if isinstance(ascii_art, str):
        frames_list = ascii_art.split("\n\n") if ascii_art else []
    else:
        try:
            frames_list = list(ascii_art)
        except Exception:
            frames_list = []

    message = f"Save the {len(frames_list)} frames as images and video?"
    if ask_save(menu, message=message):
        # Export frames to images
        out_dir = "output/frames"
        frames_to_images(frames_list, out_dir, font_path="assets/fonts/JetBrainsMonoNerdFont-Bold.ttf")

        print(Y + f"Saved frames to directory: {out_dir}")

        # Create video from images
        video_path = "output/output_video.mp4"
        images_to_video(out_dir, video_path, fps=settings.get("fps", 12))
        print(Y + f"Saved video: {video_path}")

    input("\nPress ENTER to continue...")


# ============================================================
#                     SETTINGS & UTILITY HELPERS
# ============================================================


def load_and_normalize_settings(config_manager: ConfigManager) -> Dict[str, Any]:
    """Load config and convert to runtime-ready format with enums."""
    raw = config_manager.load()
    return normalize_runtime_settings(raw)


def ask_save(
    menu: QuestionsManager, message: str = "Save the ASCII art to a file?"
) -> bool:
    """Ask if user wants to save the generated source."""
    answer = menu.ask_list(
        message=message,
        choices=[(Y + "Yes", "1"), (Y + "No", "0")],
        default="0",
    )
    return answer == "1"


@clear_screen
def show_section(banner: Banner, title: str, subtitle: str) -> None:
    """Display section header with banner."""
    banner.show(title, subtitle)
    # banner.footer()  # opcional, si quieres el footer en cada sección


@clear_screen
def exit_program() -> None:
    """Exit the application."""
    raise SystemExit(0)


# ============================================================
#                     ENTRY POINT
# ============================================================


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
    except Exception as e:
        print(R + f"Unexpected error: {str(e)}")
        raise
