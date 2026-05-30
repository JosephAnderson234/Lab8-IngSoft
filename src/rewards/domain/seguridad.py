"""Utilidades de seguridad para datos sensibles del cliente.

El numero de tarjeta nunca se almacena ni se transmite completo dentro
del dominio: se enmascara para mostrarlo y se deriva un identificador
de cuenta a partir de un hash, evitando filtrar el dato real.
"""

import hashlib
import re

_SOLO_DIGITOS = re.compile(r"\D")


def normalizar_tarjeta(numero_tarjeta: str) -> str:
    """Devuelve solo los digitos de la tarjeta (sin espacios ni guiones)."""
    return _SOLO_DIGITOS.sub("", numero_tarjeta or "")


def enmascarar_tarjeta(numero_tarjeta: str) -> str:
    """Enmascara la tarjeta dejando visibles unicamente los ultimos 4 digitos."""
    digitos = normalizar_tarjeta(numero_tarjeta)
    if len(digitos) < 4:
        return "****"
    return "**** **** **** " + digitos[-4:]


def identificador_cuenta(numero_tarjeta: str) -> str:
    """Deriva un identificador estable y no reversible para la cuenta.

    Se usa un hash SHA-256 de los digitos de la tarjeta para no persistir
    el numero real, manteniendo a la vez una clave deterministica.
    """
    digitos = normalizar_tarjeta(numero_tarjeta)
    return hashlib.sha256(digitos.encode("utf-8")).hexdigest()
