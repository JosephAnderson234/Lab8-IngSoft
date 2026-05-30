from datetime import datetime, timezone
from decimal import Decimal

import pytest

from rewards.application.politica import (
    NIVEL_BRONCE,
    NIVEL_ORO,
    NIVEL_PLATA,
    PoliticaRecompensasEstandar,
)
from rewards.domain.modelos import TransaccionCena


def _transaccion(monto):
    return TransaccionCena(
        id_transaccion="t-1",
        monto=Decimal(str(monto)),
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, tzinfo=timezone.utc),
    )


@pytest.mark.parametrize(
    "monto,nivel,cashback",
    [
        ("50.00", NIVEL_BRONCE, "1.00"),  # 2%
        ("150.00", NIVEL_PLATA, "4.50"),  # 3%
        ("300.00", NIVEL_ORO, "15.00"),  # 5%
    ],
)
def test_niveles_y_cashback(monto, nivel, cashback):
    politica = PoliticaRecompensasEstandar()
    calculo = politica.calcular(_transaccion(monto))
    assert calculo.nivel == nivel
    assert calculo.cashback == Decimal(cashback)


def test_puntos_son_parte_entera_del_monto():
    politica = PoliticaRecompensasEstandar()
    calculo = politica.calcular(_transaccion("99.99"))
    assert calculo.puntos == 99


def test_umbrales_configurables():
    politica = PoliticaRecompensasEstandar(
        umbral_plata=Decimal("10"), umbral_oro=Decimal("20")
    )
    assert politica.calcular(_transaccion("25")).nivel == NIVEL_ORO


def test_factor_puntos_configurable():
    politica = PoliticaRecompensasEstandar(puntos_por_unidad=3)
    assert politica.calcular(_transaccion("10")).puntos == 30
