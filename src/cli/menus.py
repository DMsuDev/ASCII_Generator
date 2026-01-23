from cli.styles import Y

MENUS = {
    "main": {
        "type": "list",
        "name": "option",
        "message": "Welcome to ASCII GENERATOR by DMsuDev",
        "choices": [
            (Y + "🛠️ Start", "init"),
            (Y + "⚙️ Settings", "settings"),
            (Y + "🚪 Exit", "exit"),
        ],
    },
    "init": {
        "type": "list",
        "name": "option",
        "message": "Select the input mode",
        "choices": [
            (Y + "📷 Camera", "camera"),
            (Y + "🖼️ Image", "image"),
            (Y + "🎬 Video", "video"),
            (Y + "◀️ Back", "back"),
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
                    (Y + "RGB", "RGB"),
                    (Y + "Grayscale", "GRAYSCALE"),
                    (Y + "ASCII", "ASCII"),
                ],
                "default": "RGB",
            },
            {
                "type": "list",
                "name": "gradient",
                "message": "Select the gradient type",
                "choices": [
                    (Y + "Short gradient (@%#*+=-:. )", "BASIC"),
                    (Y + "Long gradient ($@B%8&WM#*oahkbdpqwmZO0QLCJUYX...)", "DETAILED",),
                    (Y + "Light gradient (8@$e*+!:.  )", "LIGHT"),
                    (Y + "Color gradients (◍sr*.)", "COLOR"),
                    (Y + "Filled blocks █▓▒", "FILLED"),
                ],
                "default": "DETAILED",
            },
        ],
    },
}
