"""
Estilos de color para la interfaz CLI usando Colorama.
"""

from colorama import Fore, Style, init

# Inicializa Colorama con autoreset para evitar códigos residuales
init(autoreset=True)

# Colores principales
Y = Fore.YELLOW + Style.BRIGHT
C = Fore.CYAN + Style.BRIGHT
G = Fore.GREEN + Style.BRIGHT
R = Fore.RED + Style.BRIGHT
W = Fore.WHITE + Style.BRIGHT

# Opcionales (útiles para logs o detalles)
DIM = Style.DIM
RESET = Style.RESET_ALL
