"""Microservicio de recompensas: consume transacciones y las procesa.

Recibe las transacciones de cena desde el broker, calcula los beneficios,
actualiza la cuenta del cliente y publica un evento de notificacion.

Uso:
    python -m rewards.apps.consumidor_recompensas
"""

import logging

from ..application.caso_uso import ProcesarTransaccionCena
from ..composicion import construir_caso_uso, crear_repositorio
from ..config import Configuracion
from ..domain.modelos import TransaccionCena
from ..infrastructure.messaging.fabrica import (
    crear_consumidor_transacciones,
    crear_publicador_eventos,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def crear_manejador(caso_uso: ProcesarTransaccionCena):
    """Crea el manejador que procesa cada transaccion recibida."""

    def manejar(transaccion: TransaccionCena) -> None:
        caso_uso.ejecutar(transaccion)

    return manejar


def main() -> int:  # pragma: no cover - entrada IO/bloqueante
    config = Configuracion.desde_entorno()
    repositorio = crear_repositorio(config)
    publicador = crear_publicador_eventos(config)
    caso_uso = construir_caso_uso(repositorio, publicador)

    consumidor = crear_consumidor_transacciones(config)
    logging.info("Microservicio de recompensas iniciado (broker=%s)", config.tipo_broker)
    consumidor.consumir(crear_manejador(caso_uso))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
