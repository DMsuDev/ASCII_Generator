import time
import shutil
from colorama import Fore, Style
from tkinter import filedialog, Tk
from pathlib import Path
from functools import wraps

# ============================
#   LIMPIEZA DE CONSOLA
# ============================

def clear_screen(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        clear_console()
        return func(*args, **kwargs)
    return wrapper


def clear_console() -> None:
    """Limpia la consola de forma multiplataforma."""
    print("\033c", end="")


# ============================
#   DIÁLOGO DE ARCHIVOS
# ============================

def get_source_via_dialog(isVideo: bool = True) -> str:
    """Abre un diálogo para seleccionar un archivo y devuelve su ruta."""
    root = Tk()
    root.withdraw()  # Ocultar ventana principal

    if isVideo:
        file_types = "*.mp4 *.avi *.mov *.mkv"
        label = "Video Files"
    else:
        file_types = "*.png *.jpg *.jpeg *.bmp"
        label = "Image Files"

    file_path = filedialog.askopenfilename(
        parent=root,
        title="Select File",
        filetypes=[(label, file_types), ("All Files", "*.*")],
        initialdir=str(Path.cwd())
    )
    return file_path


# ============================
#   TERMINAL
# ============================

def get_terminal_size():
    """Devuelve el tamaño actual de la terminal (cols, rows)."""
    size = shutil.get_terminal_size()
    return size.columns, size.lines


# ============================
#   TIEMPO Y FPS
# ============================

def limit_fps(start_time: float, fps: int):
    """Limita la velocidad de refresco para videos ASCII."""
    frame_duration = 1 / fps
    elapsed = time.time() - start_time
    if elapsed < frame_duration:
        time.sleep(frame_duration - elapsed)


# ============================
#           LOGS
# ============================

def log_info(msg: str):
    print(Fore.CYAN + "[INFO] " + Style.RESET_ALL + msg)


def log_warning(msg: str):
    print(Fore.YELLOW + "[WARN] " + Style.RESET_ALL + msg)


def log_error(msg: str):
    print(Fore.RED + "[ERROR] " + Style.RESET_ALL + msg)


# ============================
#   ASCII UTILITIES
# ============================

def scale_height(target_width: int, original_w: int, original_h: int, scale_factor: float = 0.55) -> int:
    """Calcula la altura proporcional manteniendo la relación de aspecto."""
    ratio = original_h / original_w
    return int(ratio * target_width * scale_factor)


def scale_height_not_ratio(target_width: int, scale_factor: float = 0.55) -> int:
    """Calcula la altura sin mantener relación de aspecto."""
    return int(target_width * scale_factor)


def calc_avg_brightness(red: int, green: int, blue: int) -> int:
    """Calcula luminancia usando la fórmula NTSC."""
    return int(0.299 * red + 0.587 * green + 0.114 * blue)


def get_index_ascii(value: int, ascii_chars: str) -> str:
    """Mapeo lineal de luminancia → índice del gradiente ASCII."""
    return ascii_chars[int(value / 255 * (len(ascii_chars) - 1))]


# ============================
#   CONVERSIÓN DE COLORES
# ============================


def rgb_to_ansi(r, g, b, char) -> str:
    """Convierte un color RGB en un código ANSI TrueColor.

    Explicación técnica:
    --------------------
    - Los terminales modernos soportan colores en formato RGB real (TrueColor).
    - El formato ANSI para colorear texto es:
          \033[38;2;R;G;Bm
      donde:
        38  → indica que se cambia el color del texto
        2   → indica que se usarán valores RGB reales
        R,G,B → valores entre 0 y 255

    - Esta función simplemente inserta los valores RGB tal cual.
      No hay transformación matemática: es un mapeo directo del vector de color:
          c = (r, g, b) ∈ ℝ³

    - Se añade "\033[0m" al final para resetear el color del terminal.
    """

    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"

def gray_to_ansi(gray, char) -> str:
    """
    Convierte un valor de gris (0–255) en un color ANSI de la paleta de grises (232–255).

    Explicación matemática:
    -----------------------
    Los terminales ANSI tienen una paleta fija de 24 tonos de gris:
        {232, 233, ..., 255}

    Para mapear un valor de gris (0–255) a ese rango discreto se hace:

        1) Normalización:
            n = gray / 255
           (convierte el gris a un valor entre 0 y 1)

        2) Escalado al rango de 24 niveles:
            i = n * 23
           (23 porque hay 24 tonos: 0–23)

        3) Cuantización por truncamiento:
            i = floor(i)

        4) Desplazamiento al rango ANSI real:
            color_code = 232 + i

    Fórmula final:
        color_code = 232 + floor( (gray / 255) * 23 )

    Esto implementa una transformación afín + cuantización,
    equivalente a un shader de luminancia discreta.
    """
    color_code = 232 + int(gray / 255 * 23)
    return f"\033[38;5;{color_code}m{char}\033[0m"


def render_image(frame_ascii: str, save: bool = False) -> None:
    print(frame_ascii)
    if save:
        with open("frame.txt", "w", encoding="utf-8") as f:
            f.write(frame_ascii)