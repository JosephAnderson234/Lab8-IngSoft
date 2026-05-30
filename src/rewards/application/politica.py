"""Politica estandar de calculo de recompensas.

Regla de negocio aislada y altamente cohesiva: dado el monto de una cena
determina el nivel del cliente, los puntos y el cashback. Es facil de
probar y de sustituir por otra politica sin tocar el resto del sistema.
"""

from decimal import Decimal

from ..domain.modelos import CalculoRecompensa, TransaccionCena
from .puertos import PoliticaRecompensas

NIVEL_BRONCE = "BRONCE"
NIVEL_PLATA = "PLATA"
NIVEL_ORO = "ORO"


class PoliticaRecompensasEstandar(PoliticaRecompensas):
    """Asigna puntos y cashback segun umbrales de consumo configurables."""

    def __init__(
        self,
        puntos_por_unidad: int = 1,
        umbral_plata: Decimal = Decimal("100"),
        umbral_oro: Decimal = Decimal("300"),
        cashback_bronce: Decimal = Decimal("0.02"),
        cashback_plata: Decimal = Decimal("0.03"),
        cashback_oro: Decimal = Decimal("0.05"),
    ) -> None:
        self.puntos_por_unidad = puntos_por_unidad
        self.umbral_plata = Decimal(umbral_plata)
        self.umbral_oro = Decimal(umbral_oro)
        self._cashback_por_nivel = {
            NIVEL_BRONCE: Decimal(cashback_bronce),
            NIVEL_PLATA: Decimal(cashback_plata),
            NIVEL_ORO: Decimal(cashback_oro),
        }

    def _nivel(self, monto: Decimal) -> str:
        if monto >= self.umbral_oro:
            return NIVEL_ORO
        if monto >= self.umbral_plata:
            return NIVEL_PLATA
        return NIVEL_BRONCE

    def calcular(self, transaccion: TransaccionCena) -> CalculoRecompensa:
        monto = transaccion.monto
        nivel = self._nivel(monto)
        puntos = int(monto) * self.puntos_por_unidad
        cashback = monto * self._cashback_por_nivel[nivel]
        return CalculoRecompensa(puntos=puntos, cashback=cashback, nivel=nivel)
