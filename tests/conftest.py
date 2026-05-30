"""Configuracion compartida de pruebas: agrega ``src`` al path de import."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(RAIZ, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
