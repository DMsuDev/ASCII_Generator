import time
import cv2

from src.utils import (
    get_index_ascii,
    rgb_to_ansi,
    gray_to_ansi,
    scale_height,
    limit_fps,
    clear_console,
    get_terminal_size
)
from src.settings.config import MODE, GRADIENT
from src.cli.styles import R


class VideoProcessor:
    def __init__(
        self,
        target_width: int = 120,
        sequence: GRADIENT = GRADIENT.BASIC,
        mode: MODE = MODE.RGB,
        scale: float = 0.55,
        invert: bool = False,
        mirror: bool = False
    ):
        self._target_width = int(target_width)
        self._gradient = sequence.value
        self._mode = mode
        self._scale_factor = float(scale)

        self._invert = invert
        self._mirror = mirror

    # ---------------------------------------------------------
    #                   FRAME → ASCII
    # ---------------------------------------------------------
    def Convert_Video(self, frame) -> str:
        # Invertir o espejar si corresponde
        if self._invert:
            frame = cv2.bitwise_not(frame)

        if self._mirror:
            frame = cv2.flip(frame, 1)

        # Convertir a escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Ajustar al ancho de la terminal
        term_width, _ = get_terminal_size()
        new_width = min(self._target_width, term_width)

        # Calcular nueva altura proporcional
        h, w = gray.shape
        new_height = scale_height(
            target_width=new_width,
            original_w=w,
            original_h=h,
            scale_factor=self._scale_factor
        )

        # Redimensionar (rápido)
        gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_AREA)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

        # Conversión a ASCII
        ascii_lines = []
        gradient = self._gradient
        mode = self._mode

        for y in range(new_height):
            row_chars = []
            for x in range(new_width):
                pixel = gray[y, x]
                ascii_char = get_index_ascii(pixel, gradient)

                match mode:
                    case MODE.RGB:
                        # OpenCV usa BGR, así que extraemos en ese orden.
                        b, g, r = frame[y, x]
                        # Convertimos el carácter a un código ANSI RGB:
                        # ESC[38;2;R;G;Bm
                        row_chars.append(rgb_to_ansi(r, g, b, ascii_char))

                    case MODE.GRAYSCALE:
                        # Si no usamos RGB, usamos escala ANSI de grises.
                        # Se cuantiza el gris a 24 niveles (232–255).
                        row_chars.append(gray_to_ansi(pixel, ascii_char))

                    case MODE.ASCII:
                        row_chars.append(ascii_char)

            ascii_lines.append("".join(row_chars))

        return "\n".join(ascii_lines)

    # ---------------------------------------------------------
    #                   VIDEO LOOP
    # ---------------------------------------------------------
    def ProcessVideo(self, path: str | int = 0) -> None:
        # cv2.VideoCapture puede recibir un índice de cámara o un archivo.
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(R + "No se pudo abrir la fuente de vídeo.")
            return

        # Variables para calcular FPS manualmente.
        last_time = time.time()   # Marca de tiempo del último segundo
        frames = 0                # Contador de frames procesados
        fps = 0.0

        try:
            while True:
                # Read the frame from the camera
                ret, frame = cap.read()
                if not ret:
                    break

                frames += 1
                now = time.time()
                elapsed = now - last_time

                # Si ha pasado 1 segundo, calculamos FPS:
                # FPS = frames procesados / tiempo transcurrido
                if elapsed >= 1:
                    fps = frames / elapsed
                    frames = 0
                    last_time = now

                ascii_art = self.Convert_Video(frame)

                clear_console()
                print(ascii_art)

                if fps:
                    print(f"\nFPS: {fps:.2f}")

                # Salir con 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\nSaliendo...")

        # Liberamos la cámara y cerramos ventanas de OpenCV.
        cap.release()
        cv2.destroyAllWindows()

"""
import time

from src.utils import (
    get_index_ascii, 
    rgb_to_ansi, 
    gray_to_ansi,
    scale_height
)
from src.settings.config import MODE, GRADIENT
from src.utils import limit_fps, clear_console, get_terminal_size
from src.cli.styles import R

# OpenCV for video capture and processing
import cv2

class VideoProcessor():
    def __init__(self, 
            target_width: int = 120, 
            sequence: GRADIENT = GRADIENT.BASIC, mode: MODE = MODE.RGB, 
            scale: float = 0.55, 
            invert: bool = False, mirror: bool = False
        ):
        self._target_width: int = int(target_width)
        self._gradient: str = str(sequence.value)
        self._mode: MODE = mode
        self._scale_factor: float = float(scale)

        self._invert = invert
        self._mirror = mirror
    
    def Convert_Video(self, frame) -> str:
        # ============================
        # PROCESAMIENTO DEL FRAME
        # ============================
        if self._invert:
            frame = cv2.bitwise_not(frame)

        if self._mirror:
            frame = cv2.flip(frame, 1)

        # Convertir a escala de grises
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        term_width, _ = get_terminal_size()
        new_witdh = min(self._target_width, term_width)

        # Redimensionar la imagen manteniendo la relación de aspecto
        h, w = gray_image.shape
        new_height = scale_height(
            target_width=new_witdh, 
            original_h=h,
            original_w=w,
            scale_factor=self._scale_factor
        )

        gray_image = cv2.resize(gray_image, (new_witdh, new_height))
        frame = cv2.resize(frame, (new_witdh, new_height))

        # Obtener nuevas dimensiones
        height, width = gray_image.shape
        ascii_frame = []

        num_cells_x = int(width)
        num_cells_y = int(height)
            
        # ============================
        # CONVERSIÓN A ASCII
        # ============================
        for y in range(num_cells_y):
            row = ""
            for x in range(num_cells_x):
                px_y, px_x = y, x
                pixel = gray_image[px_y, px_x]

                # Get index from ASCII CHARS GRADIENT
                ascii_char = get_index_ascii(value = pixel, ascii_chars = self._gradient)

                match self._mode:
                # Si usamos color RGB real (TrueColor):
                    case MODE.RGB:
                        # OpenCV usa BGR, así que extraemos en ese orden.
                        b, g2, r = frame[px_y, px_x]

                        # Convertimos el carácter a un código ANSI RGB:
                        # ESC[38;2;R;G;Bm
                        row += rgb_to_ansi(r, g2, b, ascii_char)
                    case MODE.GRAYSCALE:
                        # Si no usamos RGB, usamos escala ANSI de grises.
                        # Se cuantiza el gris a 24 niveles (232–255).
                        row += gray_to_ansi(pixel, ascii_char)
                    case MODE.ASCII:
                        # Se usan los caracteres ACII calculados
                        row += ascii_char

            ascii_frame.append(row)

        # Unimos todas las líneas en un único string separado por saltos de línea.
        return "\n".join(ascii_frame)

    def ProcessVideo(self, path: str | int = 0):
        # Abrimos la fuente de vídeo.
        # cv2.VideoCapture puede recibir un índice de cámara o un archivo.
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            print(R + "No se pudo abrir la fuente de vídeo.")
            return
        
        # Variables para calcular FPS manualmente.
        last_time = time.time()   # Marca de tiempo del último segundo
        frames = 0                # Contador de frames procesados
        fps = 0.0
        
        try:
            while True:
                # Read the frame from the camera
                ret, frame = cap.read()
                if not ret:
                    break

                frames += 1
                now = time.time()
                elapsed = now - last_time

                # Si ha pasado 1 segundo, calculamos FPS:
                # FPS = frames procesados / tiempo transcurrido
                if elapsed >= 1:
                    fps = frames / elapsed
                    frames = 0
                    last_time = now


                #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ascii_art = self.Convert_Video(frame)

                clear_console()
                print(ascii_art)

                if fps:
                    print(f"\nFPS: {fps:.2f}")

                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\nSaliendo...")

        # Liberamos la cámara y cerramos ventanas de OpenCV.
        cap.release()
        cv2.destroyAllWindows()

"""