from datetime import datetime, timezone
from decimal import Decimal

import pytest

from rewards.domain.errores import DatosMensajeInvalidos
from rewards.domain.modelos import EventoNotificacion, TransaccionCena
from rewards.infrastructure.messaging import serializacion


def _transaccion():
    return TransaccionCena(
        id_transaccion="t-1",
        monto=Decimal("120.50"),
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, 20, 0, tzinfo=timezone.utc),
    )


def test_transaccion_ida_y_vuelta():
    original = _transaccion()
    copia = serializacion.transaccion_desde_bytes(
        serializacion.transaccion_a_bytes(original)
    )
    assert copia == original


def test_transaccion_desde_bytes_invalido():
    with pytest.raises(DatosMensajeInvalidos):
        serializacion.transaccion_desde_bytes(b"{esto no es json}")


def test_transaccion_desde_bytes_falta_campo():
    with pytest.raises(DatosMensajeInvalidos):
        serializacion.transaccion_desde_bytes(b'{"id_transaccion": "x"}')


def test_evento_ida_y_vuelta():
    evento = EventoNotificacion(
        tarjeta_enmascarada="**** 1111", canal="email", mensaje="hola"
    )
    copia = serializacion.evento_desde_bytes(serializacion.evento_a_bytes(evento))
    assert copia == evento


def test_evento_desde_bytes_invalido():
    with pytest.raises(DatosMensajeInvalidos):
        serializacion.evento_desde_bytes(b"no-json")
