# 🎥 ASCII Generator — Motor ASCII modular en Python

Este es uno de mis proyectos mas recientes, estuve aburrido (literal) y estuve investigando sobre el mundo del arte ascii y de alli surgio la inspiracion para este proyecto

## ✨ Características

- 🔡 **Conversión de imágenes y vídeo a ASCII**  
- 🎛️ **CLI interactiva** con menús, toggles y selección de archivos  
- 🎨 **Modos de color** y estilos configurables  
- 🧩 **Arquitectura modular**: separación clara entre lógica, datos y UI  
- 🖼️ **Soporte para OpenCV** para procesar frames de vídeo  
- 🧰 **Integración con Inquirer, Tkinter y PyFiglet** para una experiencia fluida  
- 🧪 **Tipado estricto** y documentación técnica para facilitar la extensión del proyecto  


## 📦 Tecnologías utilizadas

| Tecnología | Uso |
|-----------|-----|
| **Python 3.x** | Lenguaje principal |
| **OpenCV** | Procesamiento de imágenes y vídeo |
| **Tkinter** | Selección de archivos mediante diálogos |
| **InquirerPy** | Menús interactivos en terminal |
| **PyFiglet** | Banners ASCII |
| **Colorama** | Colores en terminal |


## 🚀 Instalación

Clona el repositorio:

```cmd
git clone https://github.com/DMsuDev/ASCII_Generator.git
cd ASCII_Generator
```

Instala las dependencias:

```cmd
pip install -r requirements.txt
```

## ▶️ Uso

Ejecuta el programa principal:

```cmd
python app.py
```

Desde ahí podrás:
- Seleccionar un archivo de vídeo o imagen
- Ajustar parámetros (ancho, densidad, color, velocidad…)
- Iniciar la conversión en tiempo real
- Navegar por menús dinámicos y configuraciones persistentes

## ✨ Ejemplos
![Descripción de la imagen](./assets/rgb_camera.png)
![Descripción de la imagen](./assets/var1_gray.png)
![Descripción de la imagen](./assets/var2_ascii.png)
![Descripción de la imagen](./assets/var2_rgb_ascii.png)

## 🛠️ Roadmap

- Arreglar los FPS (Actualmente solo muestran en pantalla)
- Implementar perfiles de configuración guardables
- Añadir soporte para exportar ASCII a archivo
- Mejorar rendimiento del renderizado en vídeo
- Deteccion de bordes
- Arreglar las Excepciones