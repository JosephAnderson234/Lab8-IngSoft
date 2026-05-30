"""Repositorio de cuentas de recompensas sobre SQLite.

Implementa el puerto ``RepositorioRecompensas`` usando la libreria estandar
``sqlite3``. La estructura SQL queda encapsulada aqui; el resto del sistema
solo conoce el puerto, manteniendo el bajo acoplamiento.
"""

import sqlite3
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ...application.puertos import RepositorioRecompensas
from ...domain.modelos import CuentaRecompensas

_DDL = """
CREATE TABLE IF NOT EXISTS cuentas_recompensas (
    id_cuenta TEXT PRIMARY KEY,
    tarjeta_enmascarada TEXT NOT NULL,
    puntos_totales INTEGER NOT NULL DEFAULT 0,
    cashback_total TEXT NOT NULL DEFAULT '0.00',
    actualizada_en TEXT
)
"""


class RepositorioRecompensasSqlite(RepositorioRecompensas):
    """Persiste las cuentas en una base de datos SQLite."""

    def __init__(self, ruta: str = "recompensas.db") -> None:
        self._conexion = sqlite3.connect(ruta)
        self._conexion.row_factory = sqlite3.Row
        self._conexion.execute(_DDL)
        self._conexion.commit()

    def obtener(self, id_cuenta: str) -> Optional[CuentaRecompensas]:
        fila = self._conexion.execute(
            "SELECT * FROM cuentas_recompensas WHERE id_cuenta = ?",
            (id_cuenta,),
        ).fetchone()
        if fila is None:
            return None
        return self._a_modelo(fila)

    def guardar(self, cuenta: CuentaRecompensas) -> None:
        self._conexion.execute(
            """
            INSERT INTO cuentas_recompensas
                (id_cuenta, tarjeta_enmascarada, puntos_totales,
                 cashback_total, actualizada_en)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id_cuenta) DO UPDATE SET
                tarjeta_enmascarada = excluded.tarjeta_enmascarada,
                puntos_totales = excluded.puntos_totales,
                cashback_total = excluded.cashback_total,
                actualizada_en = excluded.actualizada_en
            """,
            (
                cuenta.id_cuenta,
                cuenta.tarjeta_enmascarada,
                cuenta.puntos_totales,
                str(cuenta.cashback_total),
                cuenta.actualizada_en.isoformat() if cuenta.actualizada_en else None,
            ),
        )
        self._conexion.commit()

    @staticmethod
    def _a_modelo(fila: sqlite3.Row) -> CuentaRecompensas:
        actualizada = fila["actualizada_en"]
        return CuentaRecompensas(
            id_cuenta=fila["id_cuenta"],
            tarjeta_enmascarada=fila["tarjeta_enmascarada"],
            puntos_totales=fila["puntos_totales"],
            cashback_total=Decimal(fila["cashback_total"]),
            actualizada_en=datetime.fromisoformat(actualizada) if actualizada else None,
        )

    def cerrar(self) -> None:
        self._conexion.close()
