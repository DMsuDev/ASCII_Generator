from PIL import Image
import cv2
import keyboard

from colorama import Fore, Style, init

from typing import Optional, Union
from abc import ABC, abstractmethod

import time
import numpy as np
import os

from utils import (
    clear_console,
    get_index_ascii,
    calc_avg_brightness,
    rgb_to_ansi,
    gray_to_ansi,
    scale_height,
    get_terminal_size,
)
from settings.config import MODE, GRADIENT
from cli.styles import R


class FileValidator:
    def exists(self, source: Union[str, int]) -> bool:
        # Caso 1: si es string, comprobamos que el fichero exista
        if isinstance(source, str):
            return os.path.exists(source)

        # Caso 2: si es entero
        if isinstance(source, int):
            if source == 0:
                return True  # cámara por defecto
            else:
                raise ValueError(f"Solo se admite 0 como índice de cámara, no {source}")

        # Caso 3: cualquier otro tipo
        raise TypeError(f"Tipo de fuente no válido: {type(source)}")


class Processor(ABC):
    def __init__(
        self,
        target_width: int,
        scale: float,
        sequence: GRADIENT,
        mode: MODE,
        invert: bool,
        mirror: bool,
        validator: FileValidator,
    ):
        self._target_width: int = int(target_width)
        self._scale_factor: float = float(scale)

        self._gradient: str = str(sequence.value)
        self._mode: MODE = mode

        self._invert: bool = invert
        self._mirror: bool = mirror

        self._validator: FileValidator = validator

    @abstractmethod
    def _execute_core(self, frame: Optional[np.ndarray] = None) -> str:
        pass

    @abstractmethod
    def run(self, source: Union[str, int]) -> str:
        if isinstance(source, str) and not self._validator.exists(source):
            raise FileNotFoundError(R + "El fichero no existe")


class ImageProcessor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._image: Optional[Image.Image] = None

    def _execute_core(self, frame: Optional[np.ndarray] = None) -> str:
        if self._image is None:
            raise ValueError(R + "No image loaded. Call ProcessImage() first.")

        pixels = self._image.load()  # MUCH faster than getpixel()
        assert pixels is not None, R + "Error al obtener los pixeles de la imagen."

        ascii_art: list[str] = []
        w, h = self._image.size

        for y in range(h):
            row = []
            for x in range(w):
                pixel = pixels[x, y]
                # Handle different image modes
                if isinstance(pixel, (tuple, list)):
                    r, g, b = pixel[:3]
                else:
                    # Grayscale image, single value
                    r = g = b = pixel

                brightness = calc_avg_brightness(int(r), int(g), int(b))
                ascii_char = get_index_ascii(brightness, self._gradient)

                if self._mode == MODE.RGB:
                    row.append(rgb_to_ansi(r, g, b, ascii_char))
                elif self._mode == MODE.GRAYSCALE:
                    row.append(gray_to_ansi(brightness, ascii_char))
                else:  # MODE.ASCII
                    row.append(ascii_char)

            ascii_art.append("".join(row))

        return "\n".join(ascii_art)

    def run(self, source: Union[str, int]) -> str:
        super().run(source)
        if not isinstance(source, str):
            raise TypeError("ImageProcessor solo acepta rutas de fichero")

        self._image = Image.open(source)

        width, height = self._image.size
        new_h = scale_height(self._target_width, width, height, self._scale_factor)
        self._image = self._image.resize((self._target_width, new_h))

        return self._execute_core()


class VideoProcessor(Processor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _execute_core(self, frame: Optional[np.ndarray] = None) -> str:
        if frame is None:
            raise ValueError("Frame requerido para VideoProcessor")

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
            scale_factor=self._scale_factor,
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

    def run(self, source: Union[str, int]) -> str:
        super().run(source)

        # cv2.VideoCapture puede recibir un índice de cámara o un archivo.
        cap = cv2.VideoCapture(source)  # puede ser "video.mp4" o 0
        if not cap.isOpened():
            raise ValueError(R + "No se pudo abrir la fuente de vídeo")

        # Variables para calcular FPS manualmente.
        last_time = time.time()  # Marca de tiempo del último segundo
        frames = 0  # Contador de frames procesados
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

                ascii_art = self._execute_core(frame)

                clear_console()
                print(ascii_art)

                if fps:
                    print(f"{Fore.CYAN}{Style.BRIGHT}FPS: {fps:.2f}")

                print(f"{Fore.YELLOW}{Style.BRIGHT}Presiona 'q' o 'Esc' para salir...")

                # Comprobar salida
                if keyboard.is_pressed("q") or keyboard.is_pressed("esc"):
                    break

        except KeyboardInterrupt:
            print(f"{Fore.RED}{Style.BRIGHT}Saliendo...")

        # Liberamos la cámara y cerramos ventanas de OpenCV.
        cap.release()
        cv2.destroyAllWindows()
        return ""
