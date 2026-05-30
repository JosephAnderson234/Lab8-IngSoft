"""Repositorio de cuentas en memoria (util para pruebas y desarrollo)."""

import copy
from typing import Dict, Optional

from ...application.puertos import RepositorioRecompensas
from ...domain.modelos import CuentaRecompensas


class RepositorioRecompensasEnMemoria(RepositorioRecompensas):
    """Guarda las cuentas en un diccionario en memoria."""

    def __init__(self) -> None:
        self._cuentas: Dict[str, CuentaRecompensas] = {}

    def obtener(self, id_cuenta: str) -> Optional[CuentaRecompensas]:
        cuenta = self._cuentas.get(id_cuenta)
        # Se devuelve una copia para evitar mutaciones accidentales externas.
        return copy.deepcopy(cuenta) if cuenta is not None else None

    def guardar(self, cuenta: CuentaRecompensas) -> None:
        self._cuentas[cuenta.id_cuenta] = copy.deepcopy(cuenta)
