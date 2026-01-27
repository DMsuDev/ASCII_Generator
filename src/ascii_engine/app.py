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

        init_colors()
        self.logger.debug("Starting ASCII Generator application.")

    def run(self) -> None:
        """
        Main loop logic for the application.
        Handles menu navigation and user input.
        """

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

    def run_headless(
        self,
        input_source: str | int,
        output_path: str | Path = "results/",
        dry_run: bool = False,
        source_type: str = "image",
    ) -> None:
        """Run processing in non-interactive (headless) mode.

        input_source: path-like or 'camera' or integer index for camera
        source_type: one of 'image', 'video', 'camera'
        """
        self.settings = self.config_manager.load_normalized()
        self.logger.debug("Running in headless mode. dry_run=%s", dry_run)

        # Determine source and whether it's a video
        if source_type == "camera":
            source = 0
            is_video = True
        else:
            if isinstance(input_source, str) and input_source.isdigit():
                # treat numeric string as camera index
                source = int(input_source)
                is_video = True
            elif isinstance(input_source, str):
                source = input_source
                is_video = source_type == "video"
            else:
                self.logger.error("Invalid input_source type for headless mode.")
                return

        if dry_run:
            self.logger.debug(
                "Dry run: would process %s (is_video=%s) and save to %s",
                source,
                is_video,
                output_path,
            )
            return

        self._create_handler(source, is_video, output_path)

    def _create_handler(
        self, source: str | int, is_video: bool, output_path: str | Path = "output"
    ) -> None:
        """Create and run the appropriate processor based on source type."""
        self.logger.debug("Creating handler for source: %s", source)

        try:
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

            ascii_art: str = processor.start_processing(source)
        except Exception as exc:
            self.logger.error(f"Processing failed: {exc}")
            input("\nPress ENTER to continue...")
            return

        frames: list[str] = self.extract_frames(ascii_art)
        if not frames:
            self.logger.warning("No frames were produced from the source.")
            return

        output_dir: Path = Path(output_path).resolve()
        font_path: Path = Path("assets/fonts/JetBrainsMonoNerdFont-Bold.ttf").resolve()

        if is_video:
            message: str = "Do you want to save the output as a video file?"
            if self.menu.ask_cofirmation(message, default=True):
                self.save_video(
                    frames,
                    output_path=output_dir,
                    fps=self.settings.fps,
                    font_path=font_path,
                )

        else:
            message: str = "Do you want to save the output as image files?"
            if self.menu.ask_cofirmation(message, default=True):
                self.save_image(
                    frames,
                    output_path=output_dir / "static_images",
                    font_path=font_path,
                )
            message = "Do you want to save the output as text files?"
            if self.menu.ask_cofirmation(message, default=True):
                self.save_text(
                    frames,
                    output_path=output_dir,
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
                print(
                    f" - {COLORS.YELLOW.value + key}{COLORS.RESET.value}: {COLORS.CYAN.value + value}"
                )

        except KeyboardInterrupt:
            self.logger.debug("Settings update cancelled by user.")
            input("\nPress ENTER to continue...\n")
            return

        except Exception as exc:
            self.logger.error(f"Failed to update settings: {exc}")

        input("\nPress ENTER to continue...\n")

    def extract_frames(self, ascii_art: str) -> list[str]:
        """Extract individual frames from ASCII art output."""
        if not ascii_art:
            return []
        
        # Separated frames by blank lines (two \n)
        raw_frames: List[str] = ascii_art.split("\n\n")
        # Remove completely empty entries
        return [f.strip() for f in raw_frames if f.strip()]

    def save_image(
        self, frames: List[str], output_path: Path, font_path: Path
    ) -> List[str]:
        """Save frames as image files."""
        frames_list: List[str] = frames_to_images(
            frames,
            out_dir=output_path,
            font_path=font_path.resolve().as_posix(),
        )
        return frames_list

    def save_text(self, frames: List[str], output_path: Path) -> None:
        """Save frames as text files."""
        frame_to_text(frames, output_path)

    def save_video(
        self,
        frames: List[str],
        output_path: Path,
        fps: int,
        font_path: Path = Path("assets/fonts/JetBrainsMonoNerdFont-Bold.ttf"),
    ) -> None:
        """Save frames as a video file."""
        images: List[str] = self.save_image(
            frames,
            output_path=output_path / "frames",
            font_path=font_path,
        )
        images_to_video(
            images,
            output_path=output_path / "output_video.mp4",
            fps=fps,
        )

    def exit_program(self) -> None:
        """Exit the application."""
        self.logger.info("Exiting application as per user request.")
        raise SystemExit(0)
