"""Configuracion de la aplicacion leida desde variables de entorno.

Las credenciales NUNCA se escriben en el codigo fuente: se obtienen del
entorno para evitar filtrar secretos y facilitar el despliegue. Existe un
archivo ``.env.example`` con los nombres de las variables esperadas.
"""

import os
from dataclasses import dataclass

BROKER_MEMORIA = "memoria"
BROKER_RABBITMQ = "rabbitmq"
BROKER_KAFKA = "kafka"


@dataclass(frozen=True)
class Configuracion:
    """Parametros de conexion y nombres logicos de colas/topicos."""

    tipo_broker: str = BROKER_MEMORIA
    host: str = "localhost"
    puerto: int = 5672
    usuario: str = "guest"
    password: str = ""
    vhost: str = "/"
    cola_transacciones: str = "transacciones_cena"
    cola_notificaciones: str = "notificaciones_recompensa"
    grupo_consumidor: str = "sistema_recompensas"
    ruta_base_datos: str = "recompensas.db"

    @classmethod
    def desde_entorno(cls, entorno: dict | None = None) -> "Configuracion":
        env = entorno if entorno is not None else os.environ
        return cls(
            tipo_broker=env.get("BROKER_TIPO", cls.tipo_broker),
            host=env.get("BROKER_HOST", cls.host),
            puerto=int(env.get("BROKER_PUERTO", cls.puerto)),
            usuario=env.get("BROKER_USUARIO", cls.usuario),
            password=env.get("BROKER_PASSWORD", cls.password),
            vhost=env.get("BROKER_VHOST", cls.vhost),
            cola_transacciones=env.get("COLA_TRANSACCIONES", cls.cola_transacciones),
            cola_notificaciones=env.get("COLA_NOTIFICACIONES", cls.cola_notificaciones),
            grupo_consumidor=env.get("GRUPO_CONSUMIDOR", cls.grupo_consumidor),
            ruta_base_datos=env.get("RUTA_BASE_DATOS", cls.ruta_base_datos),
        )
