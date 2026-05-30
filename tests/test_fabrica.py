import pytest

from rewards.config import (
    BROKER_KAFKA,
    BROKER_MEMORIA,
    BROKER_RABBITMQ,
    Configuracion,
)
from rewards.infrastructure.messaging import fabrica
from rewards.infrastructure.messaging.memoria import (
    BrokerEnMemoria,
    ConsumidorTransaccionesEnMemoria,
    PublicadorEventosEnMemoria,
    PublicadorTransaccionesEnMemoria,
)


def test_fabrica_memoria_usa_broker_compartido():
    broker = BrokerEnMemoria()
    config = Configuracion(tipo_broker=BROKER_MEMORIA)
    assert isinstance(
        fabrica.crear_publicador_transacciones(config, broker),
        PublicadorTransaccionesEnMemoria,
    )
    assert isinstance(
        fabrica.crear_publicador_eventos(config, broker), PublicadorEventosEnMemoria
    )
    assert isinstance(
        fabrica.crear_consumidor_transacciones(config, broker),
        ConsumidorTransaccionesEnMemoria,
    )


def test_fabrica_tipo_no_soportado():
    config = Configuracion(tipo_broker="activemq")
    with pytest.raises(ValueError):
        fabrica.crear_publicador_eventos(config)
    with pytest.raises(ValueError):
        fabrica.crear_publicador_transacciones(config)
    with pytest.raises(ValueError):
        fabrica.crear_consumidor_transacciones(config)


def test_fabrica_rabbitmq_y_kafka_construyen(monkeypatch):
    # No requieren conexion real: solo se instancian los adaptadores.
    config_r = Configuracion(tipo_broker=BROKER_RABBITMQ)
    config_k = Configuracion(tipo_broker=BROKER_KAFKA)
    assert fabrica.crear_publicador_eventos(config_r) is not None
    assert fabrica.crear_consumidor_transacciones(config_r) is not None
    assert fabrica.crear_publicador_transacciones(config_k) is not None
    assert fabrica.crear_consumidor_transacciones(config_k) is not None
