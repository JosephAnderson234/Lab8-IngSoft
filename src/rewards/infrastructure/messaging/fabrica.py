"""Fabrica de adaptadores de mensajeria.

Centraliza la seleccion del broker (memoria, RabbitMQ o Kafka) segun la
configuracion. El resto de la aplicacion pide un puerto y recibe la
implementacion adecuada, sin acoplarse a una tecnologia concreta.
"""

from ...application.puertos import ConsumidorTransacciones, PublicadorEventos
from ...config import (
    BROKER_KAFKA,
    BROKER_MEMORIA,
    BROKER_RABBITMQ,
    Configuracion,
)
from .memoria import (
    BrokerEnMemoria,
    ConsumidorTransaccionesEnMemoria,
    PublicadorEventosEnMemoria,
    PublicadorTransaccionesEnMemoria,
)


def _broker_no_soportado(tipo: str):
    raise ValueError(f"Tipo de broker no soportado: {tipo!r}")


def crear_publicador_transacciones(
    config: Configuracion, broker: BrokerEnMemoria | None = None
):
    """Crea el publicador usado por el sistema del restaurante."""
    if config.tipo_broker == BROKER_MEMORIA:
        return PublicadorTransaccionesEnMemoria(broker or BrokerEnMemoria())
    if config.tipo_broker == BROKER_RABBITMQ:
        from .rabbitmq import PublicadorTransaccionesRabbitMQ

        return PublicadorTransaccionesRabbitMQ(config)
    if config.tipo_broker == BROKER_KAFKA:
        from .kafka import PublicadorTransaccionesKafka

        return PublicadorTransaccionesKafka(config)
    return _broker_no_soportado(config.tipo_broker)


def crear_publicador_eventos(
    config: Configuracion, broker: BrokerEnMemoria | None = None
) -> PublicadorEventos:
    """Crea el publicador de notificaciones usado por el caso de uso."""
    if config.tipo_broker == BROKER_MEMORIA:
        return PublicadorEventosEnMemoria(broker or BrokerEnMemoria())
    if config.tipo_broker == BROKER_RABBITMQ:
        from .rabbitmq import PublicadorEventosRabbitMQ

        return PublicadorEventosRabbitMQ(config)
    if config.tipo_broker == BROKER_KAFKA:
        from .kafka import PublicadorEventosKafka

        return PublicadorEventosKafka(config)
    return _broker_no_soportado(config.tipo_broker)


def crear_consumidor_transacciones(
    config: Configuracion, broker: BrokerEnMemoria | None = None
) -> ConsumidorTransacciones:
    """Crea el consumidor usado por el microservicio de recompensas."""
    if config.tipo_broker == BROKER_MEMORIA:
        return ConsumidorTransaccionesEnMemoria(broker or BrokerEnMemoria())
    if config.tipo_broker == BROKER_RABBITMQ:
        from .rabbitmq import ConsumidorTransaccionesRabbitMQ

        return ConsumidorTransaccionesRabbitMQ(config)
    if config.tipo_broker == BROKER_KAFKA:
        from .kafka import ConsumidorTransaccionesKafka

        return ConsumidorTransaccionesKafka(config)
    return _broker_no_soportado(config.tipo_broker)
