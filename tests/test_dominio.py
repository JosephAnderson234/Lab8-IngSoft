from datetime import datetime, timezone
from decimal import Decimal

import pytest

from rewards.domain.errores import TransaccionInvalida
from rewards.domain.modelos import (
    CalculoRecompensa,
    CuentaRecompensas,
    TransaccionCena,
)


def _transaccion(**cambios):
    base = dict(
        id_transaccion="t-1",
        monto=Decimal("120.50"),
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, 20, 0, tzinfo=timezone.utc),
    )
    base.update(cambios)
    return TransaccionCena(**base)


def test_transaccion_valida_normaliza_monto():
    t = _transaccion(monto="120.5")
    assert t.monto == Decimal("120.50")
    assert t.tarjeta_enmascarada.endswith("1111")
    assert len(t.id_cuenta) == 64


def test_transaccion_monto_no_positivo():
    with pytest.raises(TransaccionInvalida):
        _transaccion(monto="0")


def test_transaccion_monto_no_numerico():
    with pytest.raises(TransaccionInvalida):
        _transaccion(monto="abc")


def test_transaccion_sin_id():
    with pytest.raises(TransaccionInvalida):
        _transaccion(id_transaccion="")


def test_transaccion_tarjeta_invalida():
    with pytest.raises(TransaccionInvalida):
        _transaccion(numero_tarjeta="12")


def test_transaccion_sin_restaurante():
    with pytest.raises(TransaccionInvalida):
        _transaccion(codigo_restaurante="")


def test_transaccion_fecha_invalida():
    with pytest.raises(TransaccionInvalida):
        _transaccion(fecha_hora="2026-05-16")


def test_calculo_recompensa_negativa_invalida():
    with pytest.raises(TransaccionInvalida):
        CalculoRecompensa(puntos=-1, cashback=Decimal("1"), nivel="BRONCE")
    with pytest.raises(TransaccionInvalida):
        CalculoRecompensa(puntos=1, cashback=Decimal("-1"), nivel="BRONCE")


def test_cuenta_acredita_y_acumula():
    cuenta = CuentaRecompensas.nueva("id-1", "**** 1111")
    cuenta.acreditar(CalculoRecompensa(puntos=10, cashback=Decimal("2.00"), nivel="PLATA"))
    cuenta.acreditar(CalculoRecompensa(puntos=5, cashback=Decimal("1.50"), nivel="BRONCE"))
    assert cuenta.puntos_totales == 15
    assert cuenta.cashback_total == Decimal("3.50")
    assert cuenta.actualizada_en is not None


def test_cuenta_acreditar_con_momento_fijo():
    cuenta = CuentaRecompensas.nueva("id-1", "**** 1111")
    momento = datetime(2026, 5, 16, tzinfo=timezone.utc)
    cuenta.acreditar(
        CalculoRecompensa(puntos=1, cashback=Decimal("0.10"), nivel="BRONCE"),
        momento=momento,
    )
    assert cuenta.actualizada_en == momento
