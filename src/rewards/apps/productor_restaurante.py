"""App del restaurante: publica una transaccion de cena en el broker.

Uso:
    python -m rewards.apps.productor_restaurante <monto> <numero_tarjeta> <codigo>

La configuracion (broker, host, credenciales) se toma de variables de
entorno; ver ``.env.example``.
"""

import logging
import sys
import uuid

from ..config import Configuracion
from ..infrastructure.messaging.fabrica import crear_publicador_transacciones
from .factory_transaccion import construir_transaccion

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - entrada IO
    argv = argv if argv is not None else sys.argv[1:]
    monto = argv[0] if len(argv) > 0 else "150.00"
    numero_tarjeta = argv[1] if len(argv) > 1 else "4111111111111111"
    codigo_restaurante = argv[2] if len(argv) > 2 else "REST-001"

    config = Configuracion.desde_entorno()
    transaccion = construir_transaccion(
        id_transaccion=str(uuid.uuid4()),
        monto=monto,
        numero_tarjeta=numero_tarjeta,
        codigo_restaurante=codigo_restaurante,
    )

    publicador = crear_publicador_transacciones(config)
    publicador.publicar(transaccion)
    if hasattr(publicador, "cerrar"):
        publicador.cerrar()

    logging.info(
        "Transaccion %s publicada (tarjeta %s)",
        transaccion.id_transaccion,
        transaccion.tarjeta_enmascarada,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
