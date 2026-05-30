"""Pruebas del adaptador RabbitMQ usando un modulo ``pika`` falso.

No se conecta a un broker real: se inyecta un doble de prueba en
``sys.modules`` para verificar que el adaptador declara colas, publica los
bytes correctos y confirma (ack) los mensajes consumidos.
"""

import sys
import types
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from rewards.config import Configuracion
from rewards.domain.modelos import EventoNotificacion, TransaccionCena
from rewards.infrastructure.messaging import serializacion


class _CanalFalso:
    def __init__(self):
        self.colas_declaradas = []
        self.publicaciones = []
        self.acks = []
        self.qos = None
        self.consumo = None

    def queue_declare(self, queue, durable=False):
        self.colas_declaradas.append((queue, durable))

    def basic_publish(self, exchange, routing_key, body):
        self.publicaciones.append((exchange, routing_key, body))

    def basic_qos(self, prefetch_count):
        self.qos = prefetch_count

    def basic_consume(self, queue, on_message_callback):
        self.consumo = (queue, on_message_callback)

    def basic_ack(self, delivery_tag):
        self.acks.append(delivery_tag)


class _ConexionFalsa:
    def __init__(self, *_args, **_kwargs):
        self.is_open = True
        self._canal = _CanalFalso()

    def channel(self):
        return self._canal

    def close(self):
        self.is_open = False


@pytest.fixture
def pika_falso(monkeypatch):
    modulo = types.ModuleType("pika")
    modulo.PlainCredentials = lambda *a, **k: ("cred", a)
    modulo.ConnectionParameters = lambda **k: k
    modulo.BlockingConnection = _ConexionFalsa
    monkeypatch.setitem(sys.modules, "pika", modulo)
    return modulo


def _config():
    return Configuracion(tipo_broker="rabbitmq", usuario="test_user", password="x")


def _transaccion():
    return TransaccionCena(
        id_transaccion="t-1",
        monto=Decimal("100.00"),
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, tzinfo=timezone.utc),
    )


def test_publicador_eventos_declara_y_publica(pika_falso):
    from rewards.infrastructure.messaging.rabbitmq import PublicadorEventosRabbitMQ

    pub = PublicadorEventosRabbitMQ(_config())
    pub.publicar(EventoNotificacion("**** 1111", "email", "hola"))
    pub.publicar(EventoNotificacion("**** 2222", "sms", "hola2"))  # reusa el canal

    canal = pub._canal._canal
    assert canal.colas_declaradas[0][0] == _config().cola_notificaciones
    assert len(canal.publicaciones) == 2
    pub.cerrar()


def test_publicador_transacciones_publica_bytes(pika_falso):
    from rewards.infrastructure.messaging.rabbitmq import PublicadorTransaccionesRabbitMQ

    pub = PublicadorTransaccionesRabbitMQ(_config())
    pub.publicar(_transaccion())
    canal = pub._canal._canal
    _, cola, body = canal.publicaciones[0]
    assert cola == _config().cola_transacciones
    # El cuerpo se puede deserializar de vuelta a la transaccion.
    assert serializacion.transaccion_desde_bytes(body).id_transaccion == "t-1"
    pub.cerrar()


def test_consumidor_callback_procesa_y_confirma(pika_falso):
    from rewards.infrastructure.messaging.rabbitmq import ConsumidorTransaccionesRabbitMQ

    consumidor = ConsumidorTransaccionesRabbitMQ(_config())
    recibidas = []
    callback = consumidor._construir_callback(recibidas.append)

    canal = _CanalFalso()
    metodo = types.SimpleNamespace(delivery_tag=42)
    cuerpo = serializacion.transaccion_a_bytes(_transaccion())
    callback(canal, metodo, None, cuerpo)

    assert recibidas[0].id_transaccion == "t-1"
    assert canal.acks == [42]


def test_consumidor_cerrar_sin_conexion(pika_falso):
    from rewards.infrastructure.messaging.rabbitmq import ConsumidorTransaccionesRabbitMQ

    consumidor = ConsumidorTransaccionesRabbitMQ(_config())
    consumidor.cerrar()  # no debe fallar aunque no haya conexion
