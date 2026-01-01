from os import get_terminal_size
from pyfiglet import Figlet, FontNotFound
from src.cli.styles import C, Y, G, W  # Colores que definiste en styles.py

class Banner:
    """Genera banners ASCII estilizados para la CLI."""

    def __init__(self, font_title: str = "slant", font_sub: str = "small"):
        self.title_font = self._safe_font(font_title)
        self.sub_font = self._safe_font(font_sub)

    # ---------------------------------------------------------
    #               FONT VALIDATION
    # ---------------------------------------------------------
    def _safe_font(self, font_name: str) -> Figlet:
        """Carga una fuente de forma segura, usando fallback si falla."""
        try:
            return Figlet(font=font_name)
        except FontNotFound:
            print(W + f"[WARN] Fuente '{font_name}' no encontrada. Usando 'standard'.")
            return Figlet(font="standard")


    # ---------------------------------------------------------
    #               RENDER METHODS
    # ---------------------------------------------------------
    def render(self, title: str, subtitle: str | None = None) -> str:
        """Devuelve el banner como string sin imprimirlo."""
        output = C + self.title_font.renderText(title)
        if subtitle:
            output += Y + self.sub_font.renderText(subtitle)
        return output

    def show(self, title: str = "Main Title", subtitle: str | None = None):
        """Imprime un banner con título y subtítulo opcional."""
        print(self.render(title, subtitle))

    
    def footer(self):
        width = get_terminal_size().columns
        line = "=" * min(width, 46)

        print(G + line)
        print(W + "           ASCII GENERATOR by D*****          ")
        print(G + line + "\n")