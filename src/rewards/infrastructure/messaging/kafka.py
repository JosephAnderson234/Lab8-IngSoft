"""Adaptador de mensajeria para Apache Kafka (libreria ``confluent_kafka``).

Igual que el adaptador de RabbitMQ, importa la dependencia de forma
perezosa e implementa los mismos puertos. Esto evidencia el principio de
inversion de dependencias: cambiar de broker no afecta a la aplicacion.
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


def _importar_kafka():
    """Importa confluent_kafka solo cuando se necesita."""
    from confluent_kafka import Consumer, Producer  # noqa: WPS433

    return Producer, Consumer


class _ProductorKafka:
    """Encapsula la creacion perezosa del productor de Kafka."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._productor = None

    def _asegurar(self):
        if self._productor is None:
            productor_cls, _ = _importar_kafka()
            self._productor = productor_cls(
                {"bootstrap.servers": f"{self._config.host}:{self._config.puerto}"}
            )
        return self._productor

    def publicar_bytes(self, topico: str, cuerpo: bytes) -> None:
        productor = self._asegurar()
        productor.produce(topico, value=cuerpo)
        productor.flush()


class PublicadorTransaccionesKafka:
    """Publica transacciones de cena en un topico de Kafka."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._productor = _ProductorKafka(config)

    def publicar(self, transaccion: TransaccionCena) -> None:
        self._productor.publicar_bytes(
            self._config.cola_transacciones, transaccion_a_bytes(transaccion)
        )
        logger.info("Transaccion publicada en Kafka (%s)", transaccion.id_transaccion)


class PublicadorEventosKafka(PublicadorEventos):
    """Publica eventos de notificacion en un topico de Kafka."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._productor = _ProductorKafka(config)

    def publicar(self, evento: EventoNotificacion) -> None:
        self._productor.publicar_bytes(
            self._config.cola_notificaciones, evento_a_bytes(evento)
        )
        logger.info("Notificacion publicada en Kafka (%s)", evento.canal)


class ConsumidorTransaccionesKafka(ConsumidorTransacciones):
    """Consume transacciones de cena desde un topico de Kafka."""

    def __init__(self, config: Configuracion) -> None:
        self._config = config
        self._consumidor = None
        self._activo = False

    def _asegurar_consumidor(self):
        if self._consumidor is None:
            _, consumidor_cls = _importar_kafka()
            self._consumidor = consumidor_cls(
                {
                    "bootstrap.servers": f"{self._config.host}:{self._config.puerto}",
                    "group.id": self._config.grupo_consumidor,
                    "auto.offset.reset": "earliest",
                }
            )
            self._consumidor.subscribe([self._config.cola_transacciones])
        return self._consumidor

    def _procesar_mensaje(self, mensaje, manejador: ManejadorTransaccion) -> None:
        """Procesa un unico mensaje de Kafka (separado para poder probarlo)."""
        if mensaje is None:
            return
        if mensaje.error():
            logger.error("Error de Kafka: %s", mensaje.error())
            return
        transaccion = transaccion_desde_bytes(mensaje.value())
        manejador(transaccion)

    def consumir(self, manejador: ManejadorTransaccion) -> None:  # pragma: no cover
        consumidor = self._asegurar_consumidor()
        self._activo = True
        logger.info("Esperando transacciones en Kafka...")
        while self._activo:  # bucle bloqueante de larga duracion
            mensaje = consumidor.poll(timeout=1.0)
            self._procesar_mensaje(mensaje, manejador)

    def cerrar(self) -> None:
        self._activo = False
        if self._consumidor is not None:
            self._consumidor.close()
        self._consumidor = None
