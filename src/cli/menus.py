from src.cli.styles import Y

MENUS = {
    "main": {
        "type": "list",
        "name": "option",
        "message": "Bienvenido a ASCII GENERATOR by D*****",
        "choices": [
            (Y + "🛠️ Iniciar", "init"),
            (Y + "⚙️ Configuración", "settings"),
            (Y + "🚪 Salir", "exit")
        ]
    },

    "init": {
        "type": "list",
        "name": "option",
        "message": "Selecciona el modo de entrada",
        "choices": [
            (Y + "📷 Cámara", "camera"),
            (Y + "🖼️ Imagen", "image"),
            (Y + "🎬 Video", "video"),
            (Y + "◀️ Atrás", "back")
        ]
    },

    "settings": {
        "type": "form",
        "fields": [
            {
                "type": "text",
                "name": "fps",
                "message": "Define el límite de FPS del video",
                "default": "24"
            },
            {
                "type": "text",
                "name": "width",
                "message": "Define el ancho objetivo",
                "default": "120"
            },
            {
                "type": "text",
                "name": "scale_factor",
                "message": "Define el factor para escalar la altura del video/imagen",
                "default": "0.43"
            },
            {
                "type": "list",
                "name": "mode",
                "message": "Selecciona el modo de color",
                "choices": [
                    (Y + "RGB", "RGB"),
                    (Y + "Escala de grises", "GRAYSCALE"),
                    (Y + "ASCII", "ASCII")
                ],
                "default": "RGB"   # ← Corregido
            },
            {
                "type": "list",
                "name": "gradient",
                "message": "Selecciona el tipo de gradiente",
                "choices": [
                    (Y + "Gradiente corto (@%#*+=-:. )", "BASIC"),
                    (Y + "Gradiente largo ($@B%8&WM#*oahkbdpqwmZO0QLCJUYX...)", "DETAILED"),
                    (Y + "LIGHT (8@$e*+!:.  )", "LIGHT"),
                    (Y + "COLOR (◍sr*.)", "COLOR"),
                    (Y + "FILLED █▓▒", "FILLED"),
                ],
                "default": "DETAILED"
            }
        ]
    },

    "json": {
        "type": "text",
        "name": "option",
        "message": "Escriba el nombre del archivo.json",
        "default": "config.json"
    }
}
