"""Adaptador de mensajeria en memoria.

Implementa los puertos de mensajeria sin dependencias externas. Es ideal
para pruebas automatizadas y para ejecutar el flujo completo sin un broker
real, demostrando que la logica no depende de la tecnologia concreta.
"""

from collections import deque
from typing import Deque

from ...application.puertos import (
    ConsumidorTransacciones,
    ManejadorTransaccion,
    PublicadorEventos,
)
from ...domain.modelos import EventoNotificacion, TransaccionCena


class BrokerEnMemoria:
    """Broker minimo: guarda transacciones publicadas y notificaciones."""

    def __init__(self) -> None:
        self.transacciones: Deque[TransaccionCena] = deque()
        self.notificaciones: list[EventoNotificacion] = []

    def publicar_transaccion(self, transaccion: TransaccionCena) -> None:
        self.transacciones.append(transaccion)


class PublicadorTransaccionesEnMemoria:
    """Publica transacciones de cena directamente en el broker en memoria."""

    def __init__(self, broker: BrokerEnMemoria) -> None:
        self._broker = broker

    def publicar(self, transaccion: TransaccionCena) -> None:
        self._broker.publicar_transaccion(transaccion)


class PublicadorEventosEnMemoria(PublicadorEventos):
    """Acumula los eventos de notificacion publicados."""

    def __init__(self, broker: BrokerEnMemoria) -> None:
        self._broker = broker

    def publicar(self, evento: EventoNotificacion) -> None:
        self._broker.notificaciones.append(evento)


class ConsumidorTransaccionesEnMemoria(ConsumidorTransacciones):
    """Entrega al manejador todas las transacciones pendientes del broker."""

    def __init__(self, broker: BrokerEnMemoria) -> None:
        self._broker = broker

    def consumir(self, manejador: ManejadorTransaccion) -> None:
        while self._broker.transacciones:
            manejador(self._broker.transacciones.popleft())
