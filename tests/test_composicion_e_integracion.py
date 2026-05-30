"""Pruebas del composition root y del flujo extremo a extremo en memoria."""

from datetime import datetime, timezone

from rewards.apps.consumidor_recompensas import crear_manejador
from rewards.apps.factory_transaccion import construir_transaccion
from rewards.composicion import construir_caso_uso, crear_repositorio
from rewards.config import BROKER_MEMORIA, BROKER_RABBITMQ, Configuracion
from rewards.infrastructure.messaging.fabrica import (
    crear_consumidor_transacciones,
    crear_publicador_eventos,
    crear_publicador_transacciones,
)
from rewards.infrastructure.messaging.memoria import BrokerEnMemoria
from rewards.infrastructure.persistence.repositorio_memoria import (
    RepositorioRecompensasEnMemoria,
)
from rewards.infrastructure.persistence.repositorio_sqlite import (
    RepositorioRecompensasSqlite,
)


def test_crear_repositorio_memoria():
    config = Configuracion(tipo_broker=BROKER_MEMORIA)
    assert isinstance(crear_repositorio(config), RepositorioRecompensasEnMemoria)


def test_crear_repositorio_sqlite(tmp_path):
    config = Configuracion(
        tipo_broker=BROKER_RABBITMQ, ruta_base_datos=str(tmp_path / "r.db")
    )
    assert isinstance(crear_repositorio(config), RepositorioRecompensasSqlite)


def test_factory_transaccion_construye_valida():
    t = construir_transaccion("id-1", "100", "4111111111111111", "REST-001")
    assert t.id_transaccion == "id-1"
    assert t.fecha_hora is not None  # usa la hora actual por defecto
    t2 = construir_transaccion(
        id_transaccion="id-2",
        monto="50",
        numero_tarjeta="4111111111111111",
        codigo_restaurante="REST-001",
        fecha_hora=datetime(2026, 5, 16, tzinfo=timezone.utc),
    )
    assert t2.codigo_restaurante == "REST-001"


def test_flujo_extremo_a_extremo_en_memoria():
    """Restaurante publica -> microservicio consume -> recompensa y notifica."""
    config = Configuracion(tipo_broker=BROKER_MEMORIA)
    broker = BrokerEnMemoria()

    # Adaptadores compartiendo el mismo broker en memoria.
    pub_tx = crear_publicador_transacciones(config, broker)
    pub_evt = crear_publicador_eventos(config, broker)
    consumidor = crear_consumidor_transacciones(config, broker)

    repositorio = crear_repositorio(config)
    caso_uso = construir_caso_uso(repositorio, pub_evt)

    # El restaurante publica dos cenas de la misma tarjeta.
    pub_tx.publicar(construir_transaccion("t-1", "150.00", "4111111111111111", "R1"))
    pub_tx.publicar(construir_transaccion("t-2", "200.00", "4111111111111111", "R1"))

    # El microservicio consume y procesa.
    consumidor.consumir(crear_manejador(caso_uso))

    # Se generaron dos notificaciones y la cuenta acumulo ambos consumos.
    assert len(broker.notificaciones) == 2
    id_cuenta = construir_transaccion(
        "x", "1", "4111111111111111", "R1"
    ).id_cuenta
    cuenta = repositorio.obtener(id_cuenta)
    assert cuenta.puntos_totales == 350
