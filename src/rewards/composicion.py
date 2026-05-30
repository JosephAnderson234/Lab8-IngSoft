"""Composition root: ensambla los componentes segun la configuracion.

Es el unico lugar que conoce simultaneamente las capas de aplicacion e
infraestructura. Mantener aqui el cableado deja el resto del codigo
desacoplado y facil de probar.
"""

from .application.caso_uso import ProcesarTransaccionCena
from .application.politica import PoliticaRecompensasEstandar
from .application.puertos import (
    PublicadorEventos,
    RepositorioRecompensas,
)
from .config import BROKER_MEMORIA, Configuracion
from .infrastructure.persistence.repositorio_memoria import (
    RepositorioRecompensasEnMemoria,
)
from .infrastructure.persistence.repositorio_sqlite import (
    RepositorioRecompensasSqlite,
)


def crear_repositorio(config: Configuracion) -> RepositorioRecompensas:
    """Selecciona el repositorio: en memoria para pruebas, SQLite por defecto."""
    if config.tipo_broker == BROKER_MEMORIA:
        return RepositorioRecompensasEnMemoria()
    return RepositorioRecompensasSqlite(config.ruta_base_datos)


def construir_caso_uso(
    repositorio: RepositorioRecompensas,
    publicador: PublicadorEventos | None = None,
) -> ProcesarTransaccionCena:
    """Construye el caso de uso con la politica estandar."""
    return ProcesarTransaccionCena(
        politica=PoliticaRecompensasEstandar(),
        repositorio=repositorio,
        publicador=publicador,
    )
