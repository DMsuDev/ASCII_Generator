from ..utils import COLORS

MENUS: dict = {
    "main": {
        "type": "list",
        "name": "option",
        "message": "Welcome to ASCII GENERATOR by DMsuDev",
        "choices": [
            (COLORS.YELLOW.value + "🛠️ Start", "init"),
            (COLORS.YELLOW.value + "⚙️ Settings", "settings"),
            (COLORS.YELLOW.value + "🚪 Exit", "exit"),
        ],
    },
    "init": {
        "type": "list",
        "name": "option",
        "message": "Select the input mode",
        "choices": [
            (COLORS.YELLOW.value + "📷 Camera", "camera"),
            (COLORS.YELLOW.value + "🖼️ Image", "image"),
            (COLORS.YELLOW.value + "🎬 Video", "video"),
            (COLORS.YELLOW.value + "◀️ Back", "back"),
        ],
    },
    "settings": {
        "type": "form",
        "fields": [
            {
                "type": "text",
                "name": "fps",
                "message": "Set the FPS limit for the video",
                "default": "24",
            },
            {
                "type": "text",
                "name": "width",
                "message": "Set the target width (in characters)",
                "default": "120",
            },
            {
                "type": "text",
                "name": "scale_factor",
                "message": "Set the scale factor for the height of the video/image",
                "default": "0.50",
            },
            {
                "type": "list",
                "name": "mode",
                "message": "Select the color mode",
                "choices": [
                    (COLORS.YELLOW.value + "RGB", "RGB"),
                    (COLORS.YELLOW.value + "Grayscale", "GRAYSCALE"),
                    (COLORS.YELLOW.value + "ASCII", "ASCII"),
                ],
                "default": "RGB",
            },
            {
                "type": "list",
                "name": "gradient",
                "message": "Select the gradient type",
                "choices": [
                    (COLORS.YELLOW.value + "Short gradient (@%#*+=-:. )", "BASIC"),
                    (COLORS.YELLOW.value + "Long gradient ($@B%8&WM#*oahkbdpqwmZO0QLCJUYX...)", "DETAILED",),
                    (COLORS.YELLOW.value + "Light gradient (8@$e*+!:.  )", "LIGHT"),
                    (COLORS.YELLOW.value + "Color gradients (◍sr*.)", "COLOR"),
                    (COLORS.YELLOW.value + "Filled blocks █▓▒", "FILLED"),
                ],
                "default": "DETAILED",
            },
        ],
    },
}
