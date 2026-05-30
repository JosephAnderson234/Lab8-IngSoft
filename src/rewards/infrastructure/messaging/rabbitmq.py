"""Adaptador de mensajeria para RabbitMQ (libreria ``pika``).

La dependencia ``pika`` se importa de forma perezosa para que el resto del
sistema (y las pruebas) puedan ejecutarse sin tenerla instalada. Los
adaptadores implementan los mismos puertos que el resto, por lo que se
pueden intercambiar por Kafka o por el broker en memoria sin tocar la
logica de negocio.
"""

import logging

from ...application.puertos import (
    ConsumidorTransacciones,
    ManejadorTransaccion,
    PublicadorEventos,
)
from ...config import Configuracion
from ...domain.modelos import EventoNotificacion, TransaccionCena
from .serializacion import (
    evento_a_bytes,
    transaccion_a_bytes,
    transaccion_desde_bytes,
)

logger = logging.getLogger(__name__)


def _importar_pika():
    """Importa pika solo cuando realmente se necesita una conexion."""
    import pika  # noqa: WPS433 (import local intencional)

    return pika


def _parametros_conexion(config: Configuracion):
    pika = _importar_pika()
    credenciales = pika.PlainCredentials(config.usuario, config.password)
    return pika.ConnectionParameters(
        host=config.host,
        port=config.puerto,
        virtual_host=config.vhost,
        credentials=credenciales,
    )


class _CanalRabbitMQ:
    """Maneja la conexion/canal de RabbitMQ. Reutilizado por los adaptadores."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._conexion = None
        self._canal = None

    def canal(self, cola: str):
        if self._canal is None:
            pika = _importar_pika()
            self._conexion = pika.BlockingConnection(_parametros_conexion(self._config))
            self._canal = self._conexion.channel()
            self._canal.queue_declare(queue=cola, durable=True)
        return self._canal

    def publicar_bytes(self, cola: str, cuerpo: bytes) -> None:
        self.canal(cola).basic_publish(exchange="", routing_key=cola, body=cuerpo)

    def cerrar(self) -> None:
        if self._conexion is not None and self._conexion.is_open:
            self._conexion.close()
        self._conexion = None
        self._canal = None


class PublicadorTransaccionesRabbitMQ:
    """Publica transacciones de cena (lo realiza el sistema del restaurante)."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._canal = _CanalRabbitMQ(config)

    def publicar(self, transaccion: TransaccionCena) -> None:
        self._canal.publicar_bytes(
            self._config.cola_transacciones, transaccion_a_bytes(transaccion)
        )
        logger.info("Transaccion publicada en RabbitMQ (%s)", transaccion.id_transaccion)

    def cerrar(self) -> None:
        self._canal.cerrar()


class PublicadorEventosRabbitMQ(PublicadorEventos):
    """Publica eventos de notificacion en una cola durable de RabbitMQ."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._canal = _CanalRabbitMQ(config)

    def publicar(self, evento: EventoNotificacion) -> None:
        self._canal.publicar_bytes(
            self._config.cola_notificaciones, evento_a_bytes(evento)
        )
        logger.info("Notificacion publicada en RabbitMQ (%s)", evento.canal)

    def cerrar(self) -> None:
        self._canal.cerrar()


class ConsumidorTransaccionesRabbitMQ(ConsumidorTransacciones):
    """Consume transacciones de cena desde una cola durable de RabbitMQ."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._conexion = None
        self._canal = None

    def _construir_callback(self, manejador: ManejadorTransaccion):
        def callback(canal, metodo, _propiedades, cuerpo):
            transaccion = transaccion_desde_bytes(cuerpo)
            manejador(transaccion)
            canal.basic_ack(delivery_tag=metodo.delivery_tag)

        return callback

    def consumir(self, manejador: ManejadorTransaccion) -> None:
        pika = _importar_pika()
        self._conexion = pika.BlockingConnection(_parametros_conexion(self._config))
        self._canal = self._conexion.channel()
        self._canal.queue_declare(queue=self._config.cola_transacciones, durable=True)
        self._canal.basic_qos(prefetch_count=1)
        self._canal.basic_consume(
            queue=self._config.cola_transacciones,
            on_message_callback=self._construir_callback(manejador),
        )
        logger.info("Esperando transacciones en RabbitMQ...")
        self._canal.start_consuming()  # pragma: no cover - bucle bloqueante

    def cerrar(self) -> None:
        if self._conexion is not None and self._conexion.is_open:
            self._conexion.close()
        self._conexion = None
        self._canal = None
