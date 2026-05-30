from datetime import datetime, timezone
from decimal import Decimal

from rewards.domain.modelos import EventoNotificacion, TransaccionCena
from rewards.infrastructure.messaging.memoria import (
    BrokerEnMemoria,
    ConsumidorTransaccionesEnMemoria,
    PublicadorEventosEnMemoria,
    PublicadorTransaccionesEnMemoria,
)


def _transaccion(id_t="t-1"):
    return TransaccionCena(
        id_transaccion=id_t,
        monto=Decimal("100.00"),
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, tzinfo=timezone.utc),
    )


def test_publicar_y_consumir_transacciones():
    broker = BrokerEnMemoria()
    publicador = PublicadorTransaccionesEnMemoria(broker)
    publicador.publicar(_transaccion("a"))
    publicador.publicar(_transaccion("b"))

    recibidas = []
    consumidor = ConsumidorTransaccionesEnMemoria(broker)
    consumidor.consumir(recibidas.append)

    assert [t.id_transaccion for t in recibidas] == ["a", "b"]
    assert len(broker.transacciones) == 0  # se vaciaron


def test_publicador_eventos_acumula():
    broker = BrokerEnMemoria()
    publicador = PublicadorEventosEnMemoria(broker)
    publicador.publicar(
        EventoNotificacion(tarjeta_enmascarada="**** 1111", canal="email", mensaje="ok")
    )
    assert len(broker.notificaciones) == 1
