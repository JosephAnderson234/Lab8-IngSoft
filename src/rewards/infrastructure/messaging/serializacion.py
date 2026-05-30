"""Serializacion JSON de los mensajes que viajan por el broker.

Centraliza la conversion entre objetos del dominio y bytes para evitar
duplicar la logica de (de)codificacion en cada adaptador de mensajeria.
"""

import json
from datetime import datetime
from decimal import Decimal

from ...domain.errores import DatosMensajeInvalidos
from ...domain.modelos import EventoNotificacion, TransaccionCena


def transaccion_a_bytes(transaccion: TransaccionCena) -> bytes:
    """Serializa una transaccion de cena a JSON (bytes UTF-8)."""
    datos = {
        "id_transaccion": transaccion.id_transaccion,
        "monto": str(transaccion.monto),
        "numero_tarjeta": transaccion.numero_tarjeta,
        "codigo_restaurante": transaccion.codigo_restaurante,
        "fecha_hora": transaccion.fecha_hora.isoformat(),
    }
    return json.dumps(datos).encode("utf-8")


def transaccion_desde_bytes(cuerpo: bytes) -> TransaccionCena:
    """Reconstruye una transaccion a partir del cuerpo recibido."""
    try:
        datos = json.loads(cuerpo.decode("utf-8"))
        return TransaccionCena(
            id_transaccion=datos["id_transaccion"],
            monto=Decimal(str(datos["monto"])),
            numero_tarjeta=datos["numero_tarjeta"],
            codigo_restaurante=datos["codigo_restaurante"],
            fecha_hora=datetime.fromisoformat(datos["fecha_hora"]),
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise DatosMensajeInvalidos(f"Mensaje de transaccion invalido: {exc}") from exc


def evento_a_bytes(evento: EventoNotificacion) -> bytes:
    """Serializa un evento de notificacion a JSON (bytes UTF-8)."""
    datos = {
        "tarjeta_enmascarada": evento.tarjeta_enmascarada,
        "canal": evento.canal,
        "mensaje": evento.mensaje,
    }
    return json.dumps(datos).encode("utf-8")


def evento_desde_bytes(cuerpo: bytes) -> EventoNotificacion:
    """Reconstruye un evento de notificacion desde su cuerpo."""
    try:
        datos = json.loads(cuerpo.decode("utf-8"))
        return EventoNotificacion(
            tarjeta_enmascarada=datos["tarjeta_enmascarada"],
            canal=datos["canal"],
            mensaje=datos["mensaje"],
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise DatosMensajeInvalidos(f"Mensaje de notificacion invalido: {exc}") from exc
