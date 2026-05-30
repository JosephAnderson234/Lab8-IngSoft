"""Pruebas del adaptador Kafka usando un modulo ``confluent_kafka`` falso."""

import sys
import types
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from rewards.config import Configuracion
from rewards.domain.errores import DatosMensajeInvalidos
from rewards.domain.modelos import EventoNotificacion, TransaccionCena
from rewards.infrastructure.messaging import serializacion


class _ProductorFalso:
    def __init__(self, _config):
        self.producidos = []
        self.flush_llamado = 0

    def produce(self, topico, value):
        self.producidos.append((topico, value))

    def flush(self):
        self.flush_llamado += 1


class _ConsumidorFalso:
    def __init__(self, _config):
        self.suscrito = None
        self.cerrado = False

    def subscribe(self, topicos):
        self.suscrito = topicos

    def close(self):
        self.cerrado = True


class _MensajeFalso:
    def __init__(self, value=None, error=None):
        self._value = value
        self._error = error

    def value(self):
        return self._value

    def error(self):
        return self._error


@pytest.fixture
def kafka_falso(monkeypatch):
    modulo = types.ModuleType("confluent_kafka")
    modulo.Producer = _ProductorFalso
    modulo.Consumer = _ConsumidorFalso
    monkeypatch.setitem(sys.modules, "confluent_kafka", modulo)
    return modulo


def _config():
    return Configuracion(tipo_broker="kafka", host="192.0.2.10", puerto=9092)


def _transaccion():
    return TransaccionCena(
        id_transaccion="t-1",
        monto=Decimal("100.00"),
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, tzinfo=timezone.utc),
    )


def test_publicador_eventos_produce_y_flush(kafka_falso):
    from rewards.infrastructure.messaging.kafka import PublicadorEventosKafka

    pub = PublicadorEventosKafka(_config())
    pub.publicar(EventoNotificacion("**** 1111", "email", "hola"))
    interno = pub._productor._productor
    assert interno.producidos[0][0] == _config().cola_notificaciones
    assert interno.flush_llamado == 1


def test_publicador_transacciones_produce(kafka_falso):
    from rewards.infrastructure.messaging.kafka import PublicadorTransaccionesKafka

    pub = PublicadorTransaccionesKafka(_config())
    pub.publicar(_transaccion())
    interno = pub._productor._productor
    topico, body = interno.producidos[0]
    assert topico == _config().cola_transacciones
    assert serializacion.transaccion_desde_bytes(body).id_transaccion == "t-1"


def test_consumidor_procesa_mensaje_valido(kafka_falso):
    from rewards.infrastructure.messaging.kafka import ConsumidorTransaccionesKafka

    consumidor = ConsumidorTransaccionesKafka(_config())
    recibidas = []
    mensaje = _MensajeFalso(value=serializacion.transaccion_a_bytes(_transaccion()))
    consumidor._procesar_mensaje(mensaje, recibidas.append)
    assert recibidas[0].id_transaccion == "t-1"


def test_consumidor_ignora_none_y_errores(kafka_falso):
    from rewards.infrastructure.messaging.kafka import ConsumidorTransaccionesKafka

    consumidor = ConsumidorTransaccionesKafka(_config())
    recibidas = []
    consumidor._procesar_mensaje(None, recibidas.append)
    consumidor._procesar_mensaje(_MensajeFalso(error="boom"), recibidas.append)
    assert recibidas == []


def test_consumidor_mensaje_corrupto_propaga(kafka_falso):
    from rewards.infrastructure.messaging.kafka import ConsumidorTransaccionesKafka

    consumidor = ConsumidorTransaccionesKafka(_config())
    with pytest.raises(DatosMensajeInvalidos):
        consumidor._procesar_mensaje(_MensajeFalso(value=b"no-json"), lambda _t: None)


def test_consumidor_suscribe_y_cierra(kafka_falso):
    from rewards.infrastructure.messaging.kafka import ConsumidorTransaccionesKafka

    consumidor = ConsumidorTransaccionesKafka(_config())
    interno = consumidor._asegurar_consumidor()
    assert interno.suscrito == [_config().cola_transacciones]
    consumidor.cerrar()
    assert interno.cerrado is True
