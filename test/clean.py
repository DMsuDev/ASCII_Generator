#!/usr/bin/env python3
"""
Script para eliminar recursivamente todas las carpetas __pycache__
en el directorio actual o en la ruta especificada.

Uso:
    python clean_pycache.py
    python clean_pycache.py /ruta/a/tu/proyecto
"""

import sys
import shutil
from pathlib import Path
from typing import Optional


def remove_pycache_folders(start_path: Path) -> tuple[int, int]:
    """
    Busca y elimina todas las carpetas __pycache__ de forma recursiva.

    Returns:
        (deleted_count, errors_count)
    """
    deleted_count = 0
    errors_count = 0

    print(f"Buscando __pycache__ en: {start_path.resolve()}")
    print("-" * 60)

    for pycache_dir in start_path.rglob("__pycache__"):
        if not pycache_dir.is_dir():
            continue
        
        # Ignore folder .venv
        if ".venv" in pycache_dir.parts:
            continue

        try:
            shutil.rmtree(pycache_dir, ignore_errors=False)
            print(f"[ELIMINADO] {pycache_dir}")
            deleted_count += 1
        except PermissionError:
            print(f"[PERMISO DENEGADO] {pycache_dir}")
            errors_count += 1
        except OSError as e:
            print(f"[ERROR] {pycache_dir} → {e}")
            errors_count += 1
        except Exception as e:
            print(f"[ERROR INESPERADO] {pycache_dir} → {type(e).__name__}: {e}")
            errors_count += 1

    return deleted_count, errors_count


def main(target_dir: Optional[str] = None) -> None:
    """
    Punto de entrada principal del script.
    """
    # Si no se pasa argumento, usamos el directorio actual
    start_path = Path(target_dir).resolve() if target_dir else Path.cwd().resolve()

    if not start_path.exists():
        print(f"Error: La ruta {start_path} no existe.")
        sys.exit(1)

    if not start_path.is_dir():
        print(f"Error: {start_path} no es un directorio.")
        sys.exit(1)

    print("Iniciando limpieza de carpetas __pycache__ ...\n")

    deleted, errors = remove_pycache_folders(start_path)

    print("-" * 60)
    print("\nLimpieza finalizada:")
    print(f"  Carpetas __pycache__ eliminadas: {deleted}")
    print(f"  Errores encontrados: {errors}")

    if errors == 0:
        print("\n¡Todo limpio! ✓")
    else:
        print("\nAlgunos errores ocurrieron. Revisa los mensajes anteriores.")


if __name__ == "__main__":
    # Permitimos pasar una ruta como argumento
    if len(sys.argv) > 2:
        print("Uso:")
        print("  python clean_pycache.py              → limpia desde directorio actual")
        print("  python clean_pycache.py ./mi_proyecto → limpia en esa carpeta")
        sys.exit(1)

    target = sys.argv[1] if len(sys.argv) == 2 else None
    main(target)
