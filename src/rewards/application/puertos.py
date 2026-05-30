"""Puertos (interfaces) de la arquitectura hexagonal.

Definen los contratos que la capa de aplicacion necesita del exterior.
Los adaptadores concretos (RabbitMQ, Kafka, SQLite, memoria) los
implementan. Asi el dominio depende de abstracciones y no de detalles,
logrando bajo acoplamiento e intercambiabilidad de tecnologia.
"""

from abc import ABC, abstractmethod
from typing import Callable, Optional

from ..domain.modelos import (
    CalculoRecompensa,
    CuentaRecompensas,
    EventoNotificacion,
    TransaccionCena,
)


class PoliticaRecompensas(ABC):
    """Calcula los beneficios que genera una cena."""

    @abstractmethod
    def calcular(self, transaccion: TransaccionCena) -> CalculoRecompensa:
        ...


class RepositorioRecompensas(ABC):
    """Persistencia de las cuentas de recompensas."""

    @abstractmethod
    def obtener(self, id_cuenta: str) -> Optional[CuentaRecompensas]:
        ...

    @abstractmethod
    def guardar(self, cuenta: CuentaRecompensas) -> None:
        ...


class PublicadorEventos(ABC):
    """Puerto de salida para publicar eventos en el broker de mensajeria."""

    @abstractmethod
    def publicar(self, evento: EventoNotificacion) -> None:
        ...

    def cerrar(self) -> None:  # pragma: no cover - opcional para adaptadores
        """Libera recursos. Por defecto no hace nada."""


# Tipo del manejador que procesa cada transaccion entrante.
ManejadorTransaccion = Callable[[TransaccionCena], None]


class ConsumidorTransacciones(ABC):
    """Puerto de entrada para recibir transacciones desde el broker."""

    @abstractmethod
    def consumir(self, manejador: ManejadorTransaccion) -> None:
        ...

    def cerrar(self) -> None:  # pragma: no cover - opcional para adaptadores
        """Libera recursos. Por defecto no hace nada."""
