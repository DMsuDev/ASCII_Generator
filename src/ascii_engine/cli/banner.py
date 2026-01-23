from os import get_terminal_size
from pyfiglet import Figlet, FontNotFound
from ..utils import COLORS
from ..log import get_logger


class Banner:
    """Generates stylized ASCII banners for the CLI using pyfiglet."""

    def __init__(self, title_font: str = "slant", subtitle_font: str = "small"):
        self.logger = get_logger(__name__)
        self.title_figlet = self._load_font_safe(title_font)
        self.subtitle_figlet = self._load_font_safe(subtitle_font)

    def _load_font_safe(self, font_name: str) -> Figlet:
        """Load figlet font safely with fallback to 'standard'."""
        try:
            return Figlet(font=font_name)
        except FontNotFound:
            self.logger.warning("Font '%s' not found. Falling back to 'standard'.", font_name)
            return Figlet(font="standard")

    def render(self, title: str, subtitle: str | None = None) -> str:
        """Generate banner as string (without printing)."""
        output = COLORS.CYAN.value + self.title_figlet.renderText(title)
        if subtitle:
            output += COLORS.YELLOW.value + self.subtitle_figlet.renderText(subtitle)
        return output

    def show(self, title: str = "ASCII", subtitle: str | None = None) -> None:
        """Print the banner to console."""
        print(self.render(title, subtitle))

    def footer(self) -> None:
        """Print a simple centered footer line."""
        width = get_terminal_size().columns
        line = "=" * min(width, 50)

        print(COLORS.GREEN.value + line)
        print(COLORS.WHITE.value + "      ASCII GENERATOR by DMsuDev      ".center(len(line)))
        print(COLORS.GREEN.value + line + "\n")