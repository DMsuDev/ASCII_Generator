from pathlib import Path
from typing import Any, Callable, Dict, List

from .cli.questions_manager import QuestionsManager
from .cli.banner import Banner
from .core import FrameProcessor
from .core import FileValidator

from .settings import DEFAULT_RAW_SETTINGS
from .settings import AppSettings
from .settings.manager import SettingsManager

from .utils import clear_console, clear_screen, get_source_via_dialog
from .media.media import frame_to_text, frames_to_images, images_to_video

from .utils import init_colors, COLORS
from .log import get_logger


class AppEngine:
    """
    Main application engine for the ASCII Generator.
    Orchestrates menu navigation and settings management.
    """

    def __init__(self) -> None:
        self.logger = get_logger("app")

        self.banner: Banner = Banner()
        self.menu: QuestionsManager = QuestionsManager()

        self.settings: AppSettings
        self.config_manager: SettingsManager = SettingsManager(
            file_name="config.json",
            default_config=DEFAULT_RAW_SETTINGS,
            interactive_input=self.menu.ask_text,
        )
        self.routes: Dict[str, Callable] = {
            "init": self.run_init_menu,
            "settings": self.run_settings_menu,
            "exit": self.exit_program,
        }

    def run(self) -> None:
        """
        Main loop logic for the application.
        Handles menu navigation and user input.
        """

        init_colors()
        self.logger.debug("Starting ASCII Generator application.")

        try:
            while True:
                clear_console()
                self.banner.show("ASCII ENGINE", "GENERATOR")
                try:
                    answers = self.menu.run_menu("main")
                except ValueError:
                    return

                if not answers or "option" not in answers:
                    self.logger.warning(f"Empty or invalid selection: {answers}")
                    continue

                handler = self.routes.get(answers["option"], None)
                if handler:
                    handler()
                else:
                    self.logger.warning(f"Unknown option: {answers['option']}")
                    continue
        except KeyboardInterrupt:
            self.exit_program()

        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            raise

    def _create_handler(self, source: str | int, is_video: bool) -> None:
        """Create and run the appropriate processor based on source type."""
        self.logger.debug("Creating handler for source: %s", source)

        common_params: dict[str, Any] = {
            "target_width": self.settings.width,
            "scale": self.settings.scale_factor,
            "sequence": self.settings.gradient,
            "mode": self.settings.mode,
            "invert": False,  # can be made configurable later
            "mirror": False,  # can be made configurable later
            "validator": FileValidator(),
        }

        processor: FrameProcessor = FrameProcessor(**common_params)

        frames: list[str] = self.extract_frames(processor.start_processing(source))
        if not frames:
            self.logger.warning("No frames were processed.")
            return

        output_path: Path = Path("output").resolve()
        font_path: Path = Path("assets/fonts/JetBrainsMonoNerdFont-Bold.ttf").resolve()

        if is_video:
            message: str = "Do you want to save the output as a video file?"
            if self.menu.ask_cofirmation(message, default=True):
                images: List[str] = frames_to_images(
                    frames,
                    out_dir=output_path/"frames",
                    font_path=font_path.as_posix(),
                )
                images_to_video(
                    images,
                    output_path=output_path/"output_video.mp4",
                    fps=self.settings.fps,
                )

        else:
            message: str = "Do you want to save the output as image files?"
            if self.menu.ask_cofirmation(message, default=True):
                frames_to_images(
                    frames,
                    out_dir=output_path/"static_images",
                    font_path=font_path.as_posix(),
                )

            if self.menu.ask_cofirmation(message, default=True):
                frame_to_text(
                    frames[0],
                    out_path=output_path/"static_texts",
                )

        input("\nPress ENTER to continue...")

    @clear_screen
    def handle_image(self) -> None:
        """Process a single image file."""
        self._create_handler(get_source_via_dialog(is_video=False), is_video=False)

    @clear_screen
    def handle_video(self) -> None:
        """Process a single video file."""
        self._create_handler(get_source_via_dialog(is_video=True), is_video=True)

    @clear_screen
    def handle_camera(self) -> None:
        """Process live webcam feed."""
        self._create_handler(0, is_video=True)

    def extract_frames(self, ascii_art: str) -> list[str]:
        if isinstance(ascii_art, str):
            return ascii_art.split("\n\n") if ascii_art else []
        try:
            return list(ascii_art)
        except Exception:
            self.logger.error("Failed to extract frames from ASCII art.")
            return []

    @clear_screen
    def run_init_menu(self) -> None:
        """Run the initialization menu."""
        # Reload runtime settings each time user enters the Init menu
        self.settings = self.config_manager.load_normalized()
        self.banner.show("ASCII ENGINE", "INPUT MODE")

        answers = self.menu.run_menu("init")
        if not answers or "option" not in answers:
            self.logger.warning("Invalid selection, returning to main menu.")
            return

        mode = answers["option"]
        match mode:
            case "camera":
                self.handle_camera()
            case "image":
                self.handle_image()
            case "video":
                self.handle_video()
            case "back":
                return
            case _:
                self.logger.warning(f"Unknown mode: {mode}")

    @clear_screen
    def run_settings_menu(self) -> None:
        """Run the settings menu."""
        try:
            self.banner.show("ASCII ENGINE", "SETTINGS")
            new_answers = self.menu.run_menu("settings")
            if not new_answers:
                self.logger.info("No settings changes made.")
                return

            # Other approach:
            # for key, value in new_answers.items():
            #     self.config_manager.set(key, value)
            # self.config_manager.save()
            self.config_manager.update(new_answers, save_immediately=True)
            self.logger.info("Settings updated successfully.")

            # Reload runtime settings after update
            self.settings = self.config_manager.load_normalized()

            # Print updated settings for user confirmation
            print("\nUpdated Settings:")
            for key, value in new_answers.items():
                print(f" - {COLORS.YELLOW.value + key}{COLORS.RESET.value}: {COLORS.CYAN.value + value}")

        except KeyboardInterrupt:
            self.logger.info("Settings update cancelled by user.")
            input("\nPress ENTER to continue...\n")
            return

        except Exception as exc:
            self.logger.error(f"Failed to update settings: {exc}")

        input("\nPress ENTER to continue...\n")

    def exit_program(self) -> None:
        """Exit the application."""
        self.logger.info("Exiting application as per user request.")
        raise SystemExit(0)
