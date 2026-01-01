from PIL import Image
from typing import Optional

from src.utils import (
    get_index_ascii,
    calc_avg_brightness,
    rgb_to_ansi,
    gray_to_ansi,
    scale_height
)
from src.settings.config import MODE, GRADIENT
from src.cli.styles import R


class ImageProcessor():
    def __init__(
        self,
        target_width: int = 120,
        sequence: GRADIENT = GRADIENT.BASIC,
        mode: MODE = MODE.RGB,
        scale: float = 0.55
    ):
        self._target_width: int = int(target_width)
        self._gradient: str = str(sequence.value)
        self._mode: MODE = mode
        self._scale_factor: float = float(scale)
        self._image: Optional[Image.Image] = None

    # ---------------------------------------------------------
    #                   ASCII CONVERSION
    # ---------------------------------------------------------
    def Convert(self) -> str:
        if self._image is None:
            raise ValueError(R + "No image loaded. Call ProcessImage() first.")
        
        w, h = self._image.size
        pixels = self._image.load()  # MUCH faster than getpixel()
        
        ascii_art: list[str] = []

        for y in range(h):
            row = []
            for x in range(w):
                r, g, b = pixels[x, y][:3]

                brightness = calc_avg_brightness(r, g, b)
                ascii_char = get_index_ascii(brightness, self._gradient)

                if self._mode == MODE.RGB:
                    row.append(rgb_to_ansi(r, g, b, ascii_char))
                elif self._mode == MODE.GRAYSCALE:
                    row.append(gray_to_ansi(brightness, ascii_char))
                else:  # MODE.ASCII
                    row.append(ascii_char)

            ascii_art.append("".join(row))

        return "\n".join(ascii_art)

    # ---------------------------------------------------------
    #                   IMAGE PROCESSING
    # ---------------------------------------------------------

    def ProcessImage(self, path: str) -> str:
        if not path:
            print(R + "No se seleccionó ninguna imagen.")
            return ""

        try:
            self._image = Image.open(path)

            w, h = self._image.size
            new_h = scale_height(
                target_width=self._target_width,
                original_w=w,
                original_h=h,
                scale_factor=self._scale_factor
            )

            self._image = self._image.resize((self._target_width, new_h))

            return self.Convert()

        except FileNotFoundError:
            print(R + "Error al procesar la imagen. Volviendo.")
            return ""