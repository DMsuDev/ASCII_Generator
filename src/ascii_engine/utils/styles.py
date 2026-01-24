from enum import Enum
from colorama import Fore, Style, init

def init_colors():
    """Initialize colorama for cross-platform colored output."""
    init(autoreset=True)

class COLORS(Enum):
    """ANSI color codes for terminal output."""
    BLACK   = Fore.BLACK + Style.BRIGHT
    RED     = Fore.RED + Style.BRIGHT
    GREEN   = Fore.GREEN + Style.BRIGHT
    YELLOW  = Fore.YELLOW + Style.BRIGHT
    BLUE    = Fore.BLUE + Style.BRIGHT
    MAGENTA = Fore.MAGENTA + Style.BRIGHT
    CYAN    = Fore.CYAN + Style.BRIGHT
    WHITE   = Fore.WHITE + Style.BRIGHT
    DIM     = Style.DIM
    RESET   = Style.RESET_ALL