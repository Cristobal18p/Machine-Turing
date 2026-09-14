"""Punto de entrada principal para la aplicacion Maquina de Turing."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from interfaz.app import run_app

if __name__ == "__main__":
    run_app()